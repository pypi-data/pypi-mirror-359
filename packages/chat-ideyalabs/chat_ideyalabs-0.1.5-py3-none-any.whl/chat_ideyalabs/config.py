"""
Secure configuration management for ChatIdeyalabs
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ChatIdeyalabsConfig:
    """Configuration class to manage sensitive settings."""
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        self._load_config()
    
    def _load_config(self):
        """Load configuration from environment variables with fallbacks."""
        
        # MongoDB Configuration
        self.mongodb_url = os.getenv(
            'CHATIDEYALABS_MONGODB_URL',
            'mongodb://localhost:27017'  # Safe fallback
        )
        self.mongodb_database = os.getenv('CHATIDEYALABS_MONGODB_DATABASE', 'DBName')
        self.mongodb_collection = os.getenv('CHATIDEYALABS_MONGODB_COLLECTION', 'CollectionName')
        
        # LLM API Configuration - YOUR private LLM server
        self.llm_base_url = os.getenv(
            'CHATIDEYALABS_LLM_BASE_URL',
            'http://localhost:8000'  # Your actual LLM server
        )
        self.llm_api_key = os.getenv(
            'CHATIDEYALABS_LLM_API_KEY', 
            'Your API key'  # Your actual LLM API key
        )
        
        # Logging Configuration
        self.enable_request_logging = os.getenv('CHATIDEYALABS_ENABLE_LOGGING', 'false').lower() == 'true'
        self.log_sensitive_data = os.getenv('CHATIDEYALABS_LOG_SENSITIVE', 'false').lower() == 'true'
        
        # Note: API key validation is done directly via MongoDB
        # No external validation endpoint needed
    
    def validate_config(self) -> bool:
        """Validate that required configuration is present."""
        required_fields = [
            ('LLM API Key', self.llm_api_key),
            ('MongoDB URL', self.mongodb_url),
        ]
        
        missing_fields = [name for name, value in required_fields if not value]
        
        if missing_fields:
            raise ValueError(
                f"Missing required configuration: {', '.join(missing_fields)}. "
                f"Please set the appropriate environment variables."
            )
        
        return True
    
    def get_safe_config_info(self) -> dict:
        """Return non-sensitive configuration information for logging."""
        return {
            "mongodb_database": self.mongodb_database,
            "mongodb_collection": self.mongodb_collection,
            "llm_base_url": self._mask_url(self.llm_base_url),
            "validation_method": "MongoDB Direct",
            "logging_enabled": self.enable_request_logging
        }
    
    def _mask_url(self, url: str) -> str:
        """Mask sensitive parts of URLs for logging."""
        if not url:
            return "Not configured"
        
        # Show only the domain part
        if url.startswith('http'):
            try:
                from urllib.parse import urlparse
                parsed = urlparse(url)
                return f"{parsed.scheme}://{parsed.netloc}/***"
            except:
                return "***configured***"
        
        return "***configured***"


# Global configuration instance
config = ChatIdeyalabsConfig() 