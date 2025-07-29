"""
MongoDB logger for tracking API usage and responses
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import json


class MongoDBLogger:
    """MongoDB logger for tracking chat completions and API usage."""

    def __init__(self, connection_url: str = None, database_name: str = None, collection_name: str = None):
        """
        Initialize MongoDB logger.

        Args:
            connection_url: MongoDB connection URL
            database_name: Database name (default: "chat_ideyalabs")
            collection_name: Collection name (default: "api_logs")
        """
        from ..config import config
        self.connection_url = connection_url or config.mongodb_url
        self.database_name = database_name or config.mongodb_database
        self.collection_name = collection_name or f"{config.mongodb_collection}Logs"
        self.client: Optional[AsyncIOMotorClient] = None
        self.database = None
        self.collection = None

    async def connect(self):
        """Establish connection to MongoDB."""
        if self.client is None:
            self.client = AsyncIOMotorClient(self.connection_url)
            self.database = self.client[self.database_name]
            self.collection = self.database[self.collection_name]

    async def disconnect(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            self.client = None
            self.database = None
            self.collection = None

    async def log_request(
        self,
        user_id: Optional[str],
        api_key: Optional[str],
        request_data: Dict[str, Any],
        response_data: Dict[str, Any],
        request_timestamp: datetime,
        response_timestamp: datetime,
        error: Optional[str] = None,
        **metadata
    ) -> str:
        """
        Log a chat completion request and response.

        Args:
            user_id: User identifier
            api_key: API key used for the request
            request_data: Request payload
            response_data: Response data
            request_timestamp: When the request was made
            response_timestamp: When the response was received
            error: Error message if any
            **metadata: Additional metadata

        Returns:
            Document ID of the logged entry
        """
        await self.connect()

        log_entry = {
            "user_id": user_id,
            "api_key": api_key,
            "request_timestamp": request_timestamp,
            "response_timestamp": response_timestamp,
            "duration_ms": int((response_timestamp - request_timestamp).total_seconds() * 1000),
            "request_data": request_data,
            "response_data": response_data,
            "error": error,
            "success": error is None,
            **metadata
        }

        # Calculate token counts if available
        if "usage" in response_data:
            usage = response_data["usage"]
            log_entry.update({
                "input_tokens": usage.get("prompt_tokens"),
                "output_tokens": usage.get("completion_tokens"),
                "total_tokens": usage.get("total_tokens")
            })

        result = await self.collection.insert_one(log_entry)
        return str(result.inserted_id)

    async def get_user_logs(
        self,
        user_id: str,
        limit: int = 100,
        skip: int = 0,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get logs for a specific user.

        Args:
            user_id: User identifier
            limit: Maximum number of logs to return
            skip: Number of logs to skip
            start_date: Filter logs after this date
            end_date: Filter logs before this date

        Returns:
            List of log entries
        """
        await self.connect()

        query = {"user_id": user_id}
        
        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter["$gte"] = start_date
            if end_date:
                date_filter["$lte"] = end_date
            query["request_timestamp"] = date_filter

        cursor = self.collection.find(query).sort("request_timestamp", -1).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    async def get_usage_stats(
        self,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get usage statistics.

        Args:
            user_id: User identifier (None for all users)
            start_date: Filter logs after this date
            end_date: Filter logs before this date

        Returns:
            Usage statistics
        """
        await self.connect()

        match_stage = {}
        if user_id:
            match_stage["user_id"] = user_id
        
        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter["$gte"] = start_date
            if end_date:
                date_filter["$lte"] = end_date
            match_stage["request_timestamp"] = date_filter

        pipeline = []
        if match_stage:
            pipeline.append({"$match": match_stage})

        pipeline.extend([
            {
                "$group": {
                    "_id": None,
                    "total_requests": {"$sum": 1},
                    "successful_requests": {"$sum": {"$cond": ["$success", 1, 0]}},
                    "failed_requests": {"$sum": {"$cond": ["$success", 0, 1]}},
                    "total_input_tokens": {"$sum": "$input_tokens"},
                    "total_output_tokens": {"$sum": "$output_tokens"},
                    "total_tokens": {"$sum": "$total_tokens"},
                    "avg_duration_ms": {"$avg": "$duration_ms"}
                }
            }
        ])

        result = await self.collection.aggregate(pipeline).to_list(length=1)
        if result:
            stats = result[0]
            del stats["_id"]
            return stats
        
        return {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_tokens": 0,
            "avg_duration_ms": 0
        } 