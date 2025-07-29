"""
Pydantic models for the Chat Ideyalabs API
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class MessageModel(BaseModel):
    """Message model for API requests."""
    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")


class ChatCompletionRequest(BaseModel):
    """Request model for chat completions."""
    model: str = Field(default="llama3.1", description="Model to use")
    messages: Union[List[MessageModel], str] = Field(..., description="Messages or single string")
    temperature: Optional[float] = Field(default=0.0, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: Optional[int] = Field(default=8190, gt=0, description="Maximum tokens to generate")
    stream: bool = Field(default=False, description="Enable streaming response")
    user_id: Optional[str] = Field(None, description="User identifier for logging")
    # Additional OpenAI-compatible parameters
    response_format: Optional[Dict[str, Any]] = Field(None, description="Response format specification")
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0, description="Nucleus sampling parameter")
    n: Optional[int] = Field(None, ge=1, description="Number of completions to generate")
    stop: Optional[Union[str, List[str]]] = Field(None, description="Stop sequences")
    presence_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0, description="Presence penalty")
    frequency_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0, description="Frequency penalty")
    logit_bias: Optional[Dict[str, float]] = Field(None, description="Token logit bias")
    user: Optional[str] = Field(None, description="User identifier")
    seed: Optional[int] = Field(None, description="Random seed for reproducibility")
    tools: Optional[List[Dict[str, Any]]] = Field(None, description="Available tools/functions")
    tool_choice: Optional[Union[str, Dict[str, Any]]] = Field(None, description="Tool choice strategy")


class ChatCompletionResponse(BaseModel):
    """Response model for chat completions."""
    id: str = Field(..., description="Completion ID")
    object: str = Field(default="chat.completion", description="Object type")
    created: int = Field(..., description="Creation timestamp")
    model: str = Field(..., description="Model used")
    choices: List[Dict[str, Any]] = Field(..., description="Completion choices")
    usage: Optional[Dict[str, Any]] = Field(None, description="Token usage information")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: Dict[str, Any] = Field(..., description="Error details")


class UsageStatsResponse(BaseModel):
    """Usage statistics response model."""
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    avg_duration_ms: float


class LogEntry(BaseModel):
    """Log entry model."""
    user_id: Optional[str]
    api_key: Optional[str]
    request_timestamp: str
    response_timestamp: str
    duration_ms: int
    request_data: Dict[str, Any]
    response_data: Dict[str, Any]
    error: Optional[str]
    success: bool
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


class CreateAPIKeyRequest(BaseModel):
    """Request model for creating API keys."""
    name: str = Field(..., description="Name/description of the API key")
    user_id: str = Field(..., description="User ID for the new API key")
    description: Optional[str] = Field(None, description="Additional description")
    expires_at: Optional[str] = Field(None, description="Expiration date (ISO format)")


class APIKeyResponse(BaseModel):
    """Response model for API key creation."""
    api_key: str = Field(..., description="The generated API key")
    user_id: str = Field(..., description="User ID")
    name: str = Field(..., description="API key name")
    description: Optional[str] = Field(None, description="API key description")
    created_at: str = Field(..., description="Creation timestamp")
    expires_at: Optional[str] = Field(None, description="Expiration timestamp") 