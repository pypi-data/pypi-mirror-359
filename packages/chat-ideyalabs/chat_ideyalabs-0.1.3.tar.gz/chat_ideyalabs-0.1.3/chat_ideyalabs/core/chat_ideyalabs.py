"""
Main ChatIdeyalabs class - a langchain-like wrapper for Ideyalabs LLM API
"""

import json
import asyncio
from typing import Any, AsyncGenerator, Dict, List, Optional, Union
from ..utils.api_client import APIClient
from ..config import config
from .base import BaseMessage, messages_to_dict, AIMessage


class ChatIdeyalabs:
    """
    A langchain-like wrapper for Ideyalabs LLM API, similar to ChatOpenAI.
    
    This class provides both synchronous and asynchronous methods for 
    generating chat completions using the Ideyalabs LLM API.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "llama3.1",
        temperature: float = 0.0,
        max_tokens: int = 8190,
        base_url: Optional[str] = None,
        streaming: bool = False,
        user_id: Optional[str] = None,
        # OpenAI-compatible parameters
        response_format: Optional[Dict[str, Any]] = {"type": "json_object"},
        top_p: Optional[float] = None,
        n: Optional[int] = None,
        stop: Optional[Union[str, List[str]]] = None,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        logit_bias: Optional[Dict[str, float]] = None,
        user: Optional[str] = None,
        seed: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        **kwargs
    ):
        """
        Initialize ChatIdeyalabs.

        Args:
            api_key: User's API key for authentication (required for package usage)
            model: Model name to use (default: "llama3.1")
            temperature: Sampling temperature (default: 0.0)
            max_tokens: Maximum tokens to generate (default: 8190)
            base_url: Base URL for the API (default: ChatIdeyalabs endpoint)
            streaming: Whether to use streaming by default
            user_id: User ID for logging purposes
            response_format: Response format specification
            top_p: Nucleus sampling parameter
            n: Number of completions to generate
            stop: Stop sequences
            presence_penalty: Presence penalty
            frequency_penalty: Frequency penalty
            logit_bias: Token logit bias
            user: User identifier
            seed: Random seed for reproducibility
            tools: Available tools/functions
            tool_choice: Tool choice strategy
            **kwargs: Additional parameters
        """
        if api_key is None:
            raise ValueError(
                "API key is required. Get your API key from your ChatIdeyalabs admin.\n"
                "Usage: ChatIdeyalabs(api_key='your-api-key-here')"
            )
        
        self.user_api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.streaming = streaming
        self.user_id = user_id
        
        # Store OpenAI-compatible parameters
        self.response_format = response_format
        self.top_p = top_p
        self.n = n
        self.stop = stop
        self.presence_penalty = presence_penalty
        self.frequency_penalty = frequency_penalty
        self.logit_bias = logit_bias
        self.user = user
        self.seed = seed
        self.tools = tools
        self.tool_choice = tool_choice
        
        # Configure API client for external LLM endpoint
        self.llm_base_url = base_url or config.llm_base_url
        self.llm_api_key = config.llm_api_key
        
        # Validate configuration
        config.validate_config()
        
        self.api_client = APIClient(base_url=self.llm_base_url, api_key=self.llm_api_key, **kwargs)

    def invoke(
        self,
        messages: Union[List[BaseMessage], List[Dict[str, str]], str],
        **kwargs
    ) -> AIMessage:
        """
        Synchronous wrapper for generating chat completions.
        
        Args:
            messages: Input messages (can be BaseMessage objects, dicts, or string)
            **kwargs: Additional parameters to override defaults
            
        Returns:
            AIMessage with the response
        """
        import asyncio
        return asyncio.run(self.ainvoke(messages, **kwargs))

    async def ainvoke(
        self,
        messages: Union[List[BaseMessage], List[Dict[str, str]], str],
        **kwargs
    ) -> AIMessage:
        """
        Asynchronous method for generating chat completions.
        
        Args:
            messages: Input messages (can be BaseMessage objects, dicts, or string)
            **kwargs: Additional parameters to override defaults
            
        Returns:
            AIMessage with the response
        """
        # Validate user API key first
        await self._validate_user_api_key()
        
        # Process messages
        processed_messages = self._process_messages(messages)
        
        # Prepare payload
        payload = self._build_payload(processed_messages, **kwargs)
        
        # Make API call to external LLM
        response = await self.api_client.post("/v1/chat/completions", payload)
        
        # Extract content from response
        content = self._extract_content(response)
        
        return AIMessage(content=content)
    
    async def _validate_user_api_key(self):
        """
        Validate the user's API key against the validation endpoint.
        
        Raises:
            ValueError: If API key is invalid
        """
        import httpx
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{config.validation_endpoint}/v1/validate-key",
                    headers={
                        "Authorization": f"Bearer {self.user_api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    raise ValueError(
                        "Invalid or inactive API key. Please check your API key or contact your admin."
                    )
                
                user_info = response.json()
                
                # Store user info for potential logging (if enabled and user_id not set)
                if not self.user_id and user_info.get("user_id"):
                    self.user_id = user_info.get("user_id")
            
        except httpx.RequestError:
            raise ValueError("Unable to validate API key. Please check your connection.")
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"API key validation failed: {str(e)}")

    def stream(
        self,
        messages: Union[List[BaseMessage], List[Dict[str, str]], str],
        **kwargs
    ):
        """
        Synchronous wrapper for streaming chat completions.
        Note: For streaming, it's recommended to use astream() directly in async context.
        
        Args:
            messages: Input messages
            **kwargs: Additional parameters
            
        Raises:
            RuntimeError: Use astream() for streaming in async contexts
        """
        raise RuntimeError("For streaming completions, use astream() method in an async context")

    async def astream(
        self,
        messages: Union[List[BaseMessage], List[Dict[str, str]], str],
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Asynchronous method for streaming chat completions.
        
        Args:
            messages: Input messages
            **kwargs: Additional parameters
            
        Yields:
            Streaming response chunks
        """
        # Validate user API key first
        await self._validate_user_api_key()
        
        # Process messages
        processed_messages = self._process_messages(messages)
        
        # Prepare payload with streaming enabled
        payload = self._build_payload(processed_messages, stream=True, **kwargs)
        
        # Make streaming API call to external LLM
        async for line in self.api_client.stream_post("/v1/chat/completions", payload):
            if line.startswith("data: "):
                data_str = line[6:]  # Remove "data: " prefix
                if data_str.strip() == "[DONE]":
                    break
                try:
                    data = json.loads(data_str)
                    if "choices" in data and len(data["choices"]) > 0:
                        choice = data["choices"][0]
                        if "delta" in choice and "content" in choice["delta"]:
                            yield choice["delta"]["content"]
                except json.JSONDecodeError:
                    continue

    def _process_messages(
        self, messages: Union[List[BaseMessage], List[Dict[str, str]], str]
    ) -> List[Dict[str, str]]:
        """
        Process input messages into the format expected by the API.
        
        Args:
            messages: Input messages in various formats
            
        Returns:
            List of message dictionaries
        """
        if isinstance(messages, str):
            # If it's a string, treat it as a user message
            return [{"role": "user", "content": messages}]
        elif isinstance(messages, list) and len(messages) > 0:
            if isinstance(messages[0], BaseMessage):
                # Convert BaseMessage objects to dictionaries
                return messages_to_dict(messages)  # type: ignore
            elif isinstance(messages[0], dict):
                # Already in dictionary format
                return messages  # type: ignore
        
        raise ValueError("Messages must be a string, list of BaseMessage objects, or list of dictionaries")

    def _build_payload(
        self, 
        messages: List[Dict[str, str]], 
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Build the API payload.
        
        Args:
            messages: Processed messages
            stream: Whether to enable streaming
            **kwargs: Additional parameters to override defaults
            
        Returns:
            API payload dictionary
        """
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
        }
        
        if stream:
            payload["stream"] = True
        
        # Add OpenAI-compatible parameters from instance or kwargs
        params_map = {
            "response_format": kwargs.get("response_format", self.response_format),
            "top_p": kwargs.get("top_p", self.top_p),
            "n": kwargs.get("n", self.n),
            "stop": kwargs.get("stop", self.stop),
            "presence_penalty": kwargs.get("presence_penalty", self.presence_penalty),
            "frequency_penalty": kwargs.get("frequency_penalty", self.frequency_penalty),
            "logit_bias": kwargs.get("logit_bias", self.logit_bias),
            "user": kwargs.get("user", self.user),
            "seed": kwargs.get("seed", self.seed),
            "tools": kwargs.get("tools", self.tools),
            "tool_choice": kwargs.get("tool_choice", self.tool_choice),
        }
        
        # Add non-None parameters to payload
        for param_name, param_value in params_map.items():
            if param_value is not None:
                payload[param_name] = param_value
            
        return payload

    def _extract_content(self, response: Dict[str, Any]) -> str:
        """
        Extract content from API response.
        
        Args:
            response: API response dictionary
            
        Returns:
            Content string
        """
        if "choices" in response and len(response["choices"]) > 0:
            choice = response["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                return choice["message"]["content"]
        
        raise ValueError("Invalid response format from API")

    def __call__(self, messages: Union[List[BaseMessage], List[Dict[str, str]], str], **kwargs) -> AIMessage:
        """
        Make the instance callable, similar to langchain's interface.
        
        Args:
            messages: Input messages
            **kwargs: Additional parameters
            
        Returns:
            AIMessage with the response
        """
        return self.invoke(messages, **kwargs) 