"""
API Key management system for Chat Ideyalabs
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorClient


class APIKeyManager:
    """Manages API keys for Chat Ideyalabs authentication."""
    
    def __init__(self, mongodb_url: str, database_name: str = "iMAP", collection_name: str = "apiKeys"):
        """
        Initialize API Key Manager.
        
        Args:
            mongodb_url: MongoDB connection URL
            database_name: Database name
            collection_name: Collection name for API keys
        """
        self.mongodb_url = mongodb_url
        self.database_name = database_name
        self.collection_name = collection_name
        self.client: Optional[AsyncIOMotorClient] = None
        self.database = None
        self.collection = None
    
    async def connect(self):
        """Establish connection to MongoDB."""
        if self.client is None:
            self.client = AsyncIOMotorClient(self.mongodb_url)
            self.database = self.client[self.database_name]
            self.collection = self.database[self.collection_name]
    
    async def disconnect(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            self.client = None
            self.database = None
            self.collection = None
    
    def generate_api_key(self) -> str:
        """Generate a new API key."""
        # Generate a secure random key
        key = secrets.token_urlsafe(32)
        return f"sk-idlb-{key}"
    
    def hash_api_key(self, api_key: str) -> str:
        """Hash an API key for secure storage."""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    async def create_api_key(
        self,
        user_id: str,
        name: str,
        description: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Create a new API key.
        
        Args:
            user_id: User identifier
            name: Name/description of the API key
            description: Additional description
            expires_at: Expiration date (None for no expiration)
            
        Returns:
            Dictionary containing the API key and metadata
        """
        await self.connect()
        
        api_key = self.generate_api_key()
        api_key_hash = self.hash_api_key(api_key)
        
        key_data = {
            "api_key_hash": api_key_hash,
            "user_id": user_id,
            "name": name,
            "description": description,
            "created_at": datetime.utcnow(),
            "expires_at": expires_at,
            "is_active": True,
            "last_used_at": None,
            "usage_count": 0
        }
        
        await self.collection.insert_one(key_data)
        
        return {
            "api_key": api_key,
            "user_id": user_id,
            "name": name,
            "description": description,
            "created_at": key_data["created_at"].isoformat(),
            "expires_at": expires_at.isoformat() if expires_at else None
        }
    
    async def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Validate an API key and return user information.
        
        Args:
            api_key: The API key to validate
            
        Returns:
            User information if valid, None if invalid
        """
        await self.connect()
        
        api_key_hash = self.hash_api_key(api_key)
        
        key_data = await self.collection.find_one({
            "api_key_hash": api_key_hash,
            "is_active": True
        })
        
        if not key_data:
            return None
        
        # Check if key has expired
        if key_data.get("expires_at") and key_data["expires_at"] < datetime.utcnow():
            return None
        
        # Update last used timestamp and usage count
        await self.collection.update_one(
            {"_id": key_data["_id"]},
            {
                "$set": {"last_used_at": datetime.utcnow()},
                "$inc": {"usage_count": 1}
            }
        )
        
        return {
            "user_id": key_data["user_id"],
            "name": key_data["name"],
            "created_at": key_data["created_at"].isoformat(),
            "usage_count": key_data["usage_count"] + 1,
            "isAdmin": key_data.get("isAdmin", False)
        }
    
    async def deactivate_api_key(self, api_key: str) -> bool:
        """
        Deactivate an API key.
        
        Args:
            api_key: The API key to deactivate
            
        Returns:
            True if successful, False if key not found
        """
        await self.connect()
        
        api_key_hash = self.hash_api_key(api_key)
        
        result = await self.collection.update_one(
            {"api_key_hash": api_key_hash},
            {"$set": {"is_active": False, "deactivated_at": datetime.utcnow()}}
        )
        
        return result.modified_count > 0
    
    async def list_user_keys(self, user_id: str) -> List[Dict[str, Any]]:
        """
        List all API keys for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of API key metadata (without the actual keys)
        """
        await self.connect()
        
        cursor = self.collection.find(
            {"user_id": user_id},
            {"api_key_hash": 0}  # Exclude the hash from results
        ).sort("created_at", -1)
        
        keys = await cursor.to_list(length=100)
        
        # Convert datetime objects to ISO format strings for JSON serialization
        for key in keys:
            if key.get("created_at"):
                key["created_at"] = key["created_at"].isoformat()
            if key.get("expires_at"):
                key["expires_at"] = key["expires_at"].isoformat()
            if key.get("last_used_at"):
                key["last_used_at"] = key["last_used_at"].isoformat()
            if key.get("deactivated_at"):
                key["deactivated_at"] = key["deactivated_at"].isoformat()
        
        return keys
    
    async def get_key_usage_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get usage statistics for API keys.
        
        Args:
            user_id: User identifier (None for all users)
            
        Returns:
            Usage statistics
        """
        await self.connect()
        
        match_stage = {}
        if user_id:
            match_stage["user_id"] = user_id
        
        pipeline = []
        if match_stage:
            pipeline.append({"$match": match_stage})
        
        pipeline.extend([
            {
                "$group": {
                    "_id": None,
                    "total_keys": {"$sum": 1},
                    "active_keys": {"$sum": {"$cond": ["$is_active", 1, 0]}},
                    "total_usage": {"$sum": "$usage_count"},
                    "avg_usage": {"$avg": "$usage_count"}
                }
            }
        ])
        
        result = await self.collection.aggregate(pipeline).to_list(length=1)
        if result:
            stats = result[0]
            del stats["_id"]
            return stats
        
        return {
            "total_keys": 0,
            "active_keys": 0,
            "total_usage": 0,
            "avg_usage": 0
        } 