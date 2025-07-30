"""Async Python client for the Radiant Stears API.

This module wraps every public endpoint exposed by the Rust service shown
in the documentation:

*   `GET  /health`                                          – service liveness (no auth)
*   `GET  /v1/services`                                     – list available services
*   `POST /v1/service/{service_name}/extract-transactions`  – send URLs **or** free‑form text for extraction
*   `GET  /v1/task/{task_id}/status`                        – track a background task
*   `GET  /v1/resources/{resource_type}`                    – list resources of a given type
*   `POST /v1/resource/{resource_type}/{resource_name}/delete` – delete a resource

Usage example (see bottom of file):

```python
import asyncio

async def main():
    client = AsyncClient()
    print(await client.health_check())
    print(await client.get_services())
    await client.close()

asyncio.run(main())
```
"""

from dataclasses import dataclass
import os
from typing import List, Optional, Union, Any, Dict

import requests
import aiohttp
from dotenv import load_dotenv

__all__ = [
    "Client",
    "AsyncClient",
    "ResourceType",
    "ClientError",
]


class ClientError(RuntimeError):
    """Base class for all client‑side errors."""


@dataclass(frozen=True)
class ResourceType:
    """Enumerates resource types accepted by the API.

    You may also pass a plain string if you prefer; the value will be
    lower‑cased and validated minimally.
    """

    AGENT: str = "agent"
    NAMESPACE: str = "namespace"
    PROFILE: str = "profile"
    TASK: str = "task"
    CRON_TASK: str = "cron_task"
    SERVICE: str = "service"
    COMPONENT: str = "component"
    CONTEXT_MANAGER: str = "context_manager"
    PROVIDER: str = "provider"
    MODEL: str = "model"
    SERVER: str = "server"
    RESOURCE: str = "resource"

    _ALL = {
        AGENT,
        NAMESPACE,
        PROFILE,
        TASK,
        CRON_TASK,
        SERVICE,
        COMPONENT,
        CONTEXT_MANAGER,
        PROVIDER,
        MODEL,
        SERVER,
        RESOURCE,
    }

    @classmethod
    def normalise(cls, value: Union["ResourceType", str]) -> str:
        if isinstance(value, ResourceType):  # pragma: no cover – isinstance always False for dataclass
            return value  # type: ignore[return-value]
        value_lc = value.lower()
        if value_lc not in cls._ALL:
            raise ValueError(
                f"Invalid resource type '{value}'. Valid options: {sorted(cls._ALL)}"
            )
        return value_lc


class Client:
    """Lightweight wrapper around the Radiant Stears project HTTP API.

    Parameters
    ----------
    api_key:
        The *Polaris* / *Radiant* API key. If ``None`` (default) the client
        looks for **API_KEY** in the environment (populate it via an
        ``.env`` file).
    base_url:
        The root of the Stears project server. *Do not* include a trailing
        slash.
    timeout:
        Seconds before aborting any single HTTP request.
    session:
        Optionally supply a pre‑configured ``requests.Session`` (useful for
        retries, custom adapters, etc.). If omitted the client creates its
        own ephemeral session on each call.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: Optional[str] = None,
        timeout: int | float = 30,
        session: Optional[requests.Session] = None,
    ) -> None:
        load_dotenv(override=False)
        self.api_key: str | None = api_key or os.getenv("API_KEY")
        self.base_url = base_url or os.getenv("BASE_URL")
        self.timeout = timeout
        self._session = session  # can be None → we fall back to requests

        if not self.api_key:
            raise ClientError(
                "API key not supplied and API_KEY not found in environment."
            )
            
        if not self.base_url:
            raise ClientError(
                "Base URL not supplied and BASE_URL not found in environment."
            )

    # ------------------------------------------------------------------ #
    # Public methods – one per endpoint ↓                                 #
    # ------------------------------------------------------------------ #
    def health_check(self) -> Dict[str, Any]:
        """Ping the service (no authentication required)."""
        return self._request("GET", "/health", auth=False).json()

    def get_services(self) -> Dict[str, Any]:
        """Retrieve a list of available service names."""
        return self._request("GET", "/v1/services").json()

    def extract_transactions(
        self,
        service_name: str,
        *,
        urls: Optional[List[str]] = None,
        text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Trigger transaction extraction on the given *service*.

        Supply **either** ``urls`` *or* ``text`` – never both.
        """
        self._validate_urls_or_text(urls, text)
        payload: Dict[str, Any]
        if urls is not None:
            payload = {"urls": urls}
        else:
            payload = {"message": text}

        path = f"/v1/service/{service_name}/extract-transactions"
        return self._request("POST", path, json=payload).json()

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Return the current status of a long‑running task."""
        path = f"/v1/task/{task_id}/status"
        return self._request("GET", path).json()

    def get_resources(self, resource_type: Union[ResourceType, str]) -> Dict[str, Any]:
        """List all resources of a given *type*."""
        res_type = ResourceType.normalise(resource_type)
        path = f"/v1/resources/{res_type}"
        return self._request("GET", path).json()

    def delete_resource(
        self,
        resource_type: Union[ResourceType, str],
        resource_name: str,
    ) -> Dict[str, Any]:
        """Delete the specified resource."""
        res_type = ResourceType.normalise(resource_type)
        path = f"/v1/resource/{res_type}/{resource_name}/delete"
        return self._request("POST", path).json()

    # ------------------------------------------------------------------ #
    # Internal helpers ↓                                                 #
    # ------------------------------------------------------------------ #
    def _request(
        self,
        method: str,
        path: str,
        *,
        auth: bool = True,
        **kwargs: Any,
    ) -> requests.Response:
        url = f"{self.base_url}{path}"
        headers: Dict[str, str] = kwargs.pop("headers", {})

        # Inject headers if the endpoint requires authentication.
        if auth:
            headers.setdefault("X-API-Key", self.api_key)
        headers.setdefault("Content-Type", "application/json")
        headers.setdefault("Accept", "application/json")

        req_func = self._session.request if self._session else requests.request
        response = req_func(method, url, headers=headers, timeout=self.timeout, **kwargs)

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            message = (
                f"{method} {url} returned {response.status_code}: "
                f"{response.text.strip()}"
            )
            raise ClientError(message) from exc
        return response

    @staticmethod
    def _validate_urls_or_text(
        urls: Optional[List[str]], text: Optional[str]
    ) -> None:
        if (urls and text) or (not urls and not text):
            raise ValueError("Provide *either* 'urls' or 'text', not both, and not neither.")
        if urls is not None:
            if not isinstance(urls, list):
                raise TypeError("'urls' must be a list of strings.")
            if not urls:
                raise ValueError("'urls' list is empty.")
            if any(not (isinstance(u, str) and u.strip()) for u in urls):
                raise ValueError("'urls' contains empty or non‑string entries.")
        if text is not None and not text.strip():
            raise ValueError("'text' may not be empty or whitespace only.")


class AsyncClient:
    """Async lightweight wrapper around the Radiant Stears project HTTP API.

    Parameters
    ----------
    api_key:
        The *Polaris* / *Radiant* API key. If ``None`` (default) the client
        looks for **API_KEY** in the environment (populate it via an
        ``.env`` file).
    base_url:
        The root of the Stears project server. *Do not* include a trailing
        slash.
    timeout:
        Seconds before aborting any single HTTP request.
    session:
        Optionally supply a pre‑configured ``aiohttp.ClientSession`` (useful for
        retries, custom connectors, etc.). If omitted the client creates its
        own session that should be closed with ``close()`` or used as an
        async context manager.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: Optional[str] = None,
        timeout: Union[int, float] = 30,
        session: Optional[aiohttp.ClientSession] = None,
    ) -> None:
        load_dotenv(override=False)
        self.api_key: str | None = api_key or os.getenv("API_KEY")
        self.base_url: str | None = base_url or os.getenv("BASE_URL")
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session = session
        self._own_session = session is None  # Track if we created the session

        if not self.api_key:
            raise ClientError(
                "API key not supplied and API_KEY not found in environment."
            )
        
        if not self.base_url:
            raise ClientError(
                "Base URL not supplied and BASE_URL not found in environment."
            )

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the underlying aiohttp session if we created it."""
        if self._own_session and self._session:
            await self._session.close()
            self._session = None

    def _get_session(self) -> aiohttp.ClientSession:
        """Get or create the aiohttp session."""
        if self._session is None:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session

    # ------------------------------------------------------------------ #
    # Public methods – one per endpoint ↓                                 #
    # ------------------------------------------------------------------ #
    async def health_check(self) -> Dict[str, Any]:
        """Ping the service (no authentication required)."""
        return await self._request("GET", "/health", auth=False)

    async def get_services(self) -> Dict[str, Any]:
        """Retrieve a list of available service names."""
        return await self._request("GET", "/v1/services")

    async def extract_transactions(
        self,
        service_name: str,
        *,
        urls: Optional[List[str]] = None,
        text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Trigger transaction extraction on the given *service*.

        Supply **either** ``urls`` *or* ``text`` – never both.
        """
        self._validate_urls_or_text(urls, text)
        payload: Dict[str, Any]
        if urls is not None:
            payload = {"urls": urls}
        else:
            payload = {"message": text}

        path = f"/v1/service/{service_name}/extract-transactions"
        return await self._request("POST", path, json=payload)

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Return the current status of a long‑running task."""
        path = f"/v1/task/{task_id}/status"
        return await self._request("GET", path)

    async def get_resources(self, resource_type: Union[ResourceType, str]) -> Dict[str, Any]:
        """List all resources of a given *type*."""
        res_type = ResourceType.normalise(resource_type)
        path = f"/v1/resources/{res_type}"
        return await self._request("GET", path)

    async def delete_resource(
        self,
        resource_type: Union[ResourceType, str],
        resource_name: str,
    ) -> Dict[str, Any]:
        """Delete the specified resource."""
        res_type = ResourceType.normalise(resource_type)
        path = f"/v1/resource/{res_type}/{resource_name}/delete"
        return await self._request("POST", path)

    # ------------------------------------------------------------------ #
    # Internal helpers ↓                                                 #
    # ------------------------------------------------------------------ #
    async def _request(
        self,
        method: str,
        path: str,
        *,
        auth: bool = True,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        headers: Dict[str, str] = kwargs.pop("headers", {})

        # Inject headers if the endpoint requires authentication.
        if auth:
            headers.setdefault("X-API-Key", self.api_key)
        headers.setdefault("Content-Type", "application/json")
        headers.setdefault("Accept", "application/json")

        session = self._get_session()
        
        try:
            async with session.request(method, url, headers=headers, **kwargs) as response:
                # Check for HTTP errors
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as exc:
            # Handle aiohttp-specific errors
            message = f"{method} {url} failed: {exc}"
            raise ClientError(message) from exc
        except Exception as exc:
            # Handle other errors (like HTTP status errors)
            if hasattr(exc, 'status'):
                try:
                    error_text = await response.text()
                except:
                    error_text = str(exc)
                message = (
                    f"{method} {url} returned {exc.status}: "
                    f"{error_text.strip()}"
                )
            else:
                message = f"{method} {url} failed: {exc}"
            raise ClientError(message) from exc

    @staticmethod
    def _validate_urls_or_text(
        urls: Optional[List[str]], text: Optional[str]
    ) -> None:
        if (urls and text) or (not urls and not text):
            raise ValueError("Provide *either* 'urls' or 'text', not both, and not neither.")
        if urls is not None:
            if not isinstance(urls, list):
                raise TypeError("'urls' must be a list of strings.")
            if not urls:
                raise ValueError("'urls' list is empty.")
            if any(not (isinstance(u, str) and u.strip()) for u in urls):
                raise ValueError("'urls' contains empty or non‑string entries.")
        if text is not None and not text.strip():
            raise ValueError("'text' may not be empty or whitespace only.")


# ---------------------------------------------------------------------- #
# Simple demonstration (will execute when `python client.py` is run)
# ---------------------------------------------------------------------- #
if __name__ == "__main__":
    import asyncio
    import json
    import sys

    async def main():
        urls = [
            # Put your URLs here to test extraction
            # "https://example.com/statement1",
            # "https://example.com/statement2",
        ]
        
        try:
            # Using as context manager (recommended)
            async with AsyncClient(base_url="http://localhost:3000", api_key="test") as client:
                print("→ Health check:")
                health = await client.health_check()
                print(json.dumps(health, indent=2))

                print("\n→ Services:")
                services = await client.get_services()
                print(json.dumps(services, indent=2))

                if services.get("services"):
                    default_service = services["services"][0]
                    try:
                        if urls:
                            print(f"\n→ Extracting transactions with service '{default_service}' (dummy URL):")
                            extraction = await client.extract_transactions(
                                default_service,
                                urls=urls,
                            )
                            print(json.dumps(extraction, indent=2))
                        else:
                            print(f"\n→ Extracting transactions with service '{default_service}' (dummy text):")
                            extraction = await client.extract_transactions(
                                default_service,
                                text="This is a dummy text for testing. Ignore this message.",
                            )
                            print(json.dumps(extraction, indent=2))
                    except ClientError as err:
                        print(f"Extraction failed: {err}")

                # The remaining endpoints cannot be meaningfully demoed without concrete
                # IDs / resource names supplied by the live system.
                print("\nDemo complete – the remaining endpoints require real IDs to showcase.")

        except ClientError as err:
            sys.exit(f"Cannot run demo – {err}")

    # Alternative usage pattern without context manager
    async def alternative_usage():
        client = AsyncClient(base_url="http://localhost:3000", api_key="test")
        try:
            health = await client.health_check()
            print(json.dumps(health, indent=2))
        finally:
            await client.close()  # Important: close the session

    asyncio.run(main())
