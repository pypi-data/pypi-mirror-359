"""
FastAPI application for Chat Ideyalabs wrapper API
"""

import json
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from ..core.chat_ideyalabs import ChatIdeyalabs
from ..core.base import HumanMessage, SystemMessage
from .models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ErrorResponse,
    UsageStatsResponse,
    LogEntry,
    MessageModel,
    CreateAPIKeyRequest,
    APIKeyResponse
)
from .auth import get_current_user, get_optional_user, get_admin_user, get_api_key_manager

# Import MongoDB logger, config, and log sanitizer
from ..utils.mongodb_logger import MongoDBLogger
from ..utils.log_sanitizer import sanitize_log_data
from ..config import config


app = FastAPI(
    title="Chat Ideyalabs API",
    description="A langchain-like wrapper for Ideyalabs LLM API",
    version="0.1.1"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MongoDB logger only if logging is enabled
mongo_logger = MongoDBLogger() if config.enable_request_logging else None


def get_mongo_logger():
    """Get MongoDB logger instance."""
    return mongo_logger


@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(
    request: ChatCompletionRequest,
    user_info: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a chat completion using the Ideyalabs LLM API.
    
    This endpoint accepts the same format as OpenAI's chat completions API
    but routes requests to the Ideyalabs LLM service.
    """
    request_timestamp = datetime.utcnow()
    completion_id = f"chatcmpl-{uuid.uuid4().hex[:29]}"
    
    try:
        # Create ChatIdeyalabs instance with user's API key
        chat_client = ChatIdeyalabs(
            api_key=user_info.get("api_key"),  # User's API key for authentication
            user_id=user_info.get("user_id")   # User ID for logging
        )
        
        # Process messages
        if isinstance(request.messages, str):
            messages = [HumanMessage(content=request.messages)]
        else:
            messages = []
            for msg in request.messages:
                if msg.role == "user":
                    messages.append(HumanMessage(content=msg.content))
                elif msg.role == "system":
                    messages.append(SystemMessage(content=msg.content))
                # Add more role types as needed
        
        # Handle streaming
        if request.stream:
            async def generate():
                try:
                    # Prepare kwargs for streaming
                    stream_kwargs = {
                        "model": request.model,
                        "temperature": request.temperature,
                        "max_tokens": request.max_tokens,
                    }
                    
                    # Add all optional OpenAI parameters if provided
                    if request.response_format is not None:
                        stream_kwargs["response_format"] = request.response_format
                    if request.top_p is not None:
                        stream_kwargs["top_p"] = request.top_p
                    if request.n is not None:
                        stream_kwargs["n"] = request.n
                    if request.stop is not None:
                        stream_kwargs["stop"] = request.stop
                    if request.presence_penalty is not None:
                        stream_kwargs["presence_penalty"] = request.presence_penalty
                    if request.frequency_penalty is not None:
                        stream_kwargs["frequency_penalty"] = request.frequency_penalty
                    if request.logit_bias is not None:
                        stream_kwargs["logit_bias"] = request.logit_bias
                    if request.user is not None:
                        stream_kwargs["user"] = request.user
                    if request.seed is not None:
                        stream_kwargs["seed"] = request.seed
                    if request.tools is not None:
                        stream_kwargs["tools"] = request.tools
                    if request.tool_choice is not None:
                        stream_kwargs["tool_choice"] = request.tool_choice
                    
                    async for chunk in chat_client.astream(messages, **stream_kwargs):
                        chunk_data = {
                            "id": completion_id,
                            "object": "chat.completion.chunk",
                            "created": int(time.time()),
                            "model": request.model,
                            "choices": [{
                                "index": 0,
                                "delta": {"content": chunk},
                                "finish_reason": None
                            }]
                        }
                        yield f"data: {json.dumps(chunk_data)}\n\n"
                    
                    # Final chunk
                    final_chunk = {
                        "id": completion_id,
                        "object": "chat.completion.chunk",
                        "created": int(time.time()),
                        "model": request.model,
                        "choices": [{
                            "index": 0,
                            "delta": {},
                            "finish_reason": "stop"
                        }]
                    }
                    yield f"data: {json.dumps(final_chunk)}\n\n"
                    yield "data: [DONE]\n\n"
                    
                except Exception as e:
                    error_chunk = {
                        "error": {
                            "message": str(e),
                            "type": "api_error"
                        }
                    }
                    yield f"data: {json.dumps(error_chunk)}\n\n"
            
            return StreamingResponse(
                generate(),
                media_type="text/plain",
                headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
            )
        
        # Non-streaming completion - forward all parameters
        kwargs = {
            "model": request.model,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }
        
        # Add all optional OpenAI parameters if provided
        if request.response_format is not None:
            kwargs["response_format"] = request.response_format
        if request.top_p is not None:
            kwargs["top_p"] = request.top_p
        if request.n is not None:
            kwargs["n"] = request.n
        if request.stop is not None:
            kwargs["stop"] = request.stop
        if request.presence_penalty is not None:
            kwargs["presence_penalty"] = request.presence_penalty
        if request.frequency_penalty is not None:
            kwargs["frequency_penalty"] = request.frequency_penalty
        if request.logit_bias is not None:
            kwargs["logit_bias"] = request.logit_bias
        if request.user is not None:
            kwargs["user"] = request.user
        if request.seed is not None:
            kwargs["seed"] = request.seed
        if request.tools is not None:
            kwargs["tools"] = request.tools
        if request.tool_choice is not None:
            kwargs["tool_choice"] = request.tool_choice
        
        response = await chat_client.ainvoke(messages, **kwargs)
        
        response_timestamp = datetime.utcnow()
        
        # Build response
        api_response = {
            "id": completion_id,
            "object": "chat.completion",
            "created": int(time.time()),
            "model": request.model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response.content
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 0,  # These would need to be calculated
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }
        
        # Log to MongoDB (only if logging is enabled)
        if config.enable_request_logging and mongo_logger:
            try:
                # Create safe log data (hide sensitive information)
                                 safe_request_data = request.dict()
                 if not config.log_sensitive_data:
                     # Remove sensitive data from logs
                     safe_request_data.pop("user_id", None)
                     safe_request_data = sanitize_log_data(safe_request_data)
                
                                 safe_response_data = api_response.copy()
                 if not config.log_sensitive_data:
                     safe_response_data = sanitize_log_data(safe_response_data)
                
                await mongo_logger.log_request(
                    user_id=user_info.get("user_id") if config.log_sensitive_data else "***",
                    api_key="***" if not config.log_sensitive_data else user_info.get("api_key"),
                    request_data=safe_request_data,
                    response_data=safe_response_data,
                    request_timestamp=request_timestamp,
                    response_timestamp=response_timestamp
                )
            except Exception as e:
                print(f"Failed to log to MongoDB: {e}")
        
        return api_response
        
    except Exception as e:
        response_timestamp = datetime.utcnow()
        
        # Log error to MongoDB (only if logging is enabled)
        if config.enable_request_logging and mongo_logger:
            try:
                                 safe_request_data = request.dict()
                 if not config.log_sensitive_data:
                     safe_request_data.pop("user_id", None)
                     safe_request_data = sanitize_log_data(safe_request_data)
                
                await mongo_logger.log_request(
                    user_id=user_info.get("user_id") if config.log_sensitive_data else "***",
                    api_key="***" if not config.log_sensitive_data else user_info.get("api_key"),
                    request_data=safe_request_data,
                    response_data={},
                    request_timestamp=request_timestamp,
                    response_timestamp=response_timestamp,
                    error="API Error" if not config.log_sensitive_data else str(e)
                )
            except Exception as log_error:
                print(f"Failed to log error to MongoDB: {log_error}")
        
        raise HTTPException(status_code=500, detail={"error": {"message": str(e), "type": "api_error"}})


@app.get("/v1/usage/stats", response_model=UsageStatsResponse)
async def get_usage_stats(
    user_id: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get usage statistics from MongoDB logs."""
    logger = get_mongo_logger()
    
    try:
        # If no user_id specified, use the authenticated user's ID
        target_user_id = user_id or current_user["user_id"]
        stats = await logger.get_usage_stats(user_id=target_user_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get usage stats: {str(e)}")


@app.get("/v1/usage/logs", response_model=List[LogEntry])
async def get_user_logs(
    user_id: Optional[str] = None,
    limit: int = 100,
    skip: int = 0,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get logs for a specific user."""
    logger = get_mongo_logger()
    
    try:
        # If no user_id specified, use the authenticated user's ID
        target_user_id = user_id or current_user["user_id"]
        logs = await logger.get_user_logs(user_id=target_user_id, limit=limit, skip=skip)
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user logs: {str(e)}")


@app.post("/v1/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    request: CreateAPIKeyRequest,
    admin_user: Dict[str, Any] = Depends(get_admin_user)
):
    """Create a new API key for the specified user. Admin access required."""
    api_key_mgr = get_api_key_manager()
    
    try:
        # Parse expires_at string to datetime if provided
        expires_at = None
        if request.expires_at:
            from datetime import datetime
            expires_at = datetime.fromisoformat(request.expires_at.replace('Z', '+00:00'))
        
        key_data = await api_key_mgr.create_api_key(
            user_id=request.user_id,
            name=request.name,
            description=request.description,
            expires_at=expires_at
        )
        return key_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create API key: {str(e)}")


@app.get("/v1/api-keys")
async def list_api_keys(current_user: Dict[str, Any] = Depends(get_current_user)):
    """List all API keys for the authenticated user."""
    api_key_mgr = get_api_key_manager()
    
    try:
        keys = await api_key_mgr.list_user_keys(current_user["user_id"])
        return {"api_keys": keys}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list API keys: {str(e)}")


@app.delete("/v1/api-keys/{api_key}")
async def deactivate_api_key(
    api_key: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Deactivate an API key."""
    api_key_mgr = get_api_key_manager()
    
    try:
        success = await api_key_mgr.deactivate_api_key(api_key)
        if not success:
            raise HTTPException(status_code=404, detail="API key not found")
        return {"message": "API key deactivated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to deactivate API key: {str(e)}")


@app.post("/v1/validate-key")
async def validate_api_key(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Validate API key for external package usage."""
    return {
        "valid": True,
        "user_id": current_user["user_id"],
        "name": current_user.get("name", ""),
        "active": True
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 