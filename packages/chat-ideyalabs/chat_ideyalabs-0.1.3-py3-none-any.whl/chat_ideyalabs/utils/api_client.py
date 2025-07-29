"""
API client for making HTTP requests to Ideyalabs LLM API
"""

from typing import Any, AsyncGenerator, Dict, Optional, Union
import httpx


class APIClient:
    """
    Asynchronous HTTP client service for making API calls to Ideyalabs LLM API
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        max_connections: int = 200,
        max_keepalive_connections: int = 50,
        timeout: int = 600,
        verify: bool = False,
    ):
        """
        Initialize the API client with connection limits and timeouts.

        Args:
            base_url: Base URL for the API
            api_key: API key for authentication
            max_connections: Maximum number of connections
            max_keepalive_connections: Maximum number of idle connections to keep alive
            timeout: Request timeout in seconds
            verify: Whether to verify SSL certificates
        """
        # Import config here to avoid circular imports
        from ..config import config
        
        self.base_url = (base_url or config.llm_base_url).rstrip("/")
        self.api_key = api_key or config.llm_api_key
        self.limits = httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
        )
        self.timeout = timeout
        self.verify = verify

    def _get_headers(self) -> Dict[str, str]:
        """Get default headers with authorization."""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    async def post(
        self,
        endpoint: str,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Make a POST request to the API.

        Args:
            endpoint: API endpoint (e.g., "/v1/chat/completions")
            payload: JSON payload for the request
            headers: Additional headers

        Returns:
            JSON response from the API
        """
        url = f"{self.base_url}{endpoint}"
        request_headers = self._get_headers()
        if headers:
            request_headers.update(headers)

        async with httpx.AsyncClient(
            limits=self.limits, verify=self.verify, timeout=self.timeout
        ) as client:
            response = await client.post(url, json=payload, headers=request_headers)
            response.raise_for_status()
            return response.json()

    async def stream_post(
        self,
        endpoint: str,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Make a streaming POST request to the API.

        Args:
            endpoint: API endpoint
            payload: JSON payload for the request
            headers: Additional headers

        Yields:
            Lines from the streaming response
        """
        url = f"{self.base_url}{endpoint}"
        request_headers = self._get_headers()
        if headers:
            request_headers.update(headers)

        async with httpx.AsyncClient(
            limits=self.limits, verify=self.verify, timeout=self.timeout
        ) as client:
            async with client.stream(
                "POST", url, json=payload, headers=request_headers
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    yield line 