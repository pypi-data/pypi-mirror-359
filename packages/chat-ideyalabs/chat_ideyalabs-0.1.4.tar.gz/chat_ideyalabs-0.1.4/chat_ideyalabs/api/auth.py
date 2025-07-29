"""
Authentication middleware and dependencies for Chat Ideyalabs API
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, Header, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..utils.api_key_manager import APIKeyManager

# Initialize API key manager with environment-based configuration
from ..config import config
api_key_manager = APIKeyManager(
    mongodb_url=config.mongodb_url,
    database_name=config.mongodb_database,
    collection_name=config.mongodb_collection
)

# Security scheme for Bearer token
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Validate API key and return user information.
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        User information
        
    Raises:
        HTTPException: If API key is invalid
    """
    try:
        user_info = await api_key_manager.validate_api_key(credentials.credentials)
        if not user_info:
            raise HTTPException(
                status_code=401,
                detail="Invalid API key",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Add the API key to user info for logging
        user_info["api_key"] = credentials.credentials
        return user_info
        
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    """
    Optional authentication - returns user info if API key is provided and valid.
    
    Args:
        authorization: Authorization header
        
    Returns:
        User information if valid API key provided, None otherwise
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    try:
        api_key = authorization.split(" ", 1)[1]
        user_info = await api_key_manager.validate_api_key(api_key)
        if user_info:
            user_info["api_key"] = api_key
        return user_info
    except Exception:
        return None


async def get_admin_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Validate that the current user is an admin.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User information if admin
        
    Raises:
        HTTPException: If user is not an admin
    """
    if not current_user.get("isAdmin", False):
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return current_user


def get_api_key_manager() -> APIKeyManager:
    """
    Dependency to get the API key manager instance.
    
    Returns:
        APIKeyManager instance
    """
    return api_key_manager 