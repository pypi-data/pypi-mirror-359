"""
Example showing how to interact with the FastAPI server
"""

import asyncio
import httpx
import json


async def test_chat_completion():
    """Test basic chat completion endpoint."""
    print("=== Testing Chat Completion ===")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/v1/chat/completions",
            json={
                "model": "llama3.1",
                "messages": [{"role": "user", "content": "Hello, how are you?"}],
                "temperature": 0.0,
                "max_tokens": 100,
                "user_id": "test_user_123"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result['choices'][0]['message']['content']}")
        else:
            print(f"Error: {response.status_code} - {response.text}")


async def test_streaming():
    """Test streaming endpoint."""
    print("\n=== Testing Streaming ===")
    
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST",
            "http://localhost:8000/v1/chat/completions",
            json={
                "model": "llama3.1",
                "messages": [{"role": "user", "content": "Tell me a short story about a robot"}],
                "stream": True,
                "user_id": "test_user_123"
            }
        ) as response:
            print("Streaming response: ", end="", flush=True)
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str.strip() == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        if "choices" in data and len(data["choices"]) > 0:
                            choice = data["choices"][0]
                            if "delta" in choice and "content" in choice["delta"]:
                                print(choice["delta"]["content"], end="", flush=True)
                    except json.JSONDecodeError:
                        continue
            print("\n")


async def test_health_check():
    """Test health check endpoint."""
    print("\n=== Testing Health Check ===")
    
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/health")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Health Status: {result['status']}")
        else:
            print(f"Health check failed: {response.status_code}")


async def configure_mongodb():
    """Configure MongoDB logging (optional)."""
    print("\n=== Configuring MongoDB (Optional) ===")
    
    # Replace with your actual MongoDB connection URL
    mongodb_url = "mongodb://localhost:27017/chat_ideyalabs"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/v1/configure/mongodb",
                json=mongodb_url
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"MongoDB configured: {result['message']}")
            else:
                print(f"MongoDB configuration failed: {response.status_code}")
        except Exception as e:
            print(f"MongoDB configuration skipped: {e}")


async def test_usage_stats():
    """Test usage statistics endpoint."""
    print("\n=== Testing Usage Stats ===")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "http://localhost:8000/v1/usage/stats?user_id=test_user_123"
            )
            
            if response.status_code == 200:
                stats = response.json()
                print(f"Usage Stats: {json.dumps(stats, indent=2)}")
            else:
                print(f"Usage stats failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Usage stats test skipped: {e}")


async def main():
    """Run all client tests."""
    print("Starting FastAPI Client Tests...")
    print("Make sure the server is running: python -m chat_ideyalabs.api.main")
    print()
    
    try:
        await test_health_check()
        await configure_mongodb()
        await test_chat_completion()
        await test_streaming()
        await test_usage_stats()
        
        print("\n=== All tests completed successfully! ===")
    except httpx.ConnectError:
        print("Error: Could not connect to server. Make sure it's running on localhost:8000")
    except Exception as e:
        print(f"Error running tests: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 