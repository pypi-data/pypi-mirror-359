"""
Example demonstrating secure ChatIdeyalabs setup for PyPI distribution.

This shows how users would use the package after it's published to PyPI,
with all sensitive information properly hidden via environment variables.
"""

import os
import asyncio
from chat_ideyalabs import ChatIdeyalabs

# Set environment variables (users would do this in their deployment)
os.environ['CHATIDEYALABS_LLM_BASE_URL'] = 'https://your-llm-endpoint.com'
os.environ['CHATIDEYALABS_LLM_API_KEY'] = 'your-llm-api-key-here'
os.environ['CHATIDEYALABS_MONGODB_URL'] = 'mongodb+srv://username:password@cluster.mongodb.net/database'
os.environ['CHATIDEYALABS_ENABLE_LOGGING'] = 'false'  # Disable logging by default
os.environ['CHATIDEYALABS_LOG_SENSITIVE'] = 'false'   # Never log sensitive data


async def main():
    """
    Example usage after PyPI installation.
    
    Users would install with: pip install chat-ideyalabs
    """
    
    try:
        # Initialize with user's API key (provided by admin)
        chat = ChatIdeyalabs(
            api_key="user-api-key-from-admin",  # User gets this from admin
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        print("🚀 ChatIdeyalabs initialized successfully!")
        print("📝 Configuration loaded from environment variables")
        print("🔒 API key validation via direct MongoDB connection")
        print("🛡️ No external HTTP dependencies for validation")
        
        # Example basic usage
        response = await chat.ainvoke("What is artificial intelligence?")
        print(f"\n💬 AI Response: {response.content}")
        
        # Example streaming usage  
        print(f"\n🔄 Streaming response:")
        async for chunk in chat.astream("Write a short poem about technology"):
            print(chunk, end="", flush=True)
        
        print(f"\n\n✅ Secure setup working correctly!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check that environment variables are set")
        print("2. Verify your API key is valid") 
        print("3. Ensure MongoDB connection is accessible")


if __name__ == "__main__":
    asyncio.run(main()) 