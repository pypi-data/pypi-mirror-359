"""
Basic usage examples for Chat Ideyalabs
"""

import asyncio
from chat_ideyalabs import ChatIdeyalabs, HumanMessage, SystemMessage


def basic_example():
    """Basic synchronous usage example."""
    print("=== Basic Usage Example ===")
    
    # Initialize the client with API key (required)
    chat = ChatIdeyalabs(
        api_key="your-api-key-here",  # Replace with your actual API key
        model="llama3.1",
        temperature=0.0,
        max_tokens=100
    )
    
    # Simple string input
    response = chat.invoke("What is the capital of France?")
    print(f"Response: {response.content}")


def message_objects_example():
    """Example using message objects."""
    print("\n=== Message Objects Example ===")
    
    chat = ChatIdeyalabs(api_key="your-api-key-here")  # API key required
    
    # Using message objects
    messages = [
        SystemMessage(content="You are a helpful assistant that answers in exactly one sentence."),
        HumanMessage(content="Explain quantum computing in simple terms")
    ]
    
    response = chat.invoke(messages)
    print(f"Response: {response.content}")


def response_format_example():
    """Example using response_format and other OpenAI parameters."""
    print("\n=== Response Format Example ===")
    
    chat = ChatIdeyalabs(
        api_key="your-api-key-here",
        response_format={"type": "json_object"},
        temperature=0.7,
        top_p=0.9,
        max_tokens=200
    )
    
    response = chat.invoke("List 3 programming languages as JSON with their use cases")
    print(f"JSON Response: {response.content}")


async def async_example():
    """Asynchronous usage example."""
    print("\n=== Async Usage Example ===")
    
    chat = ChatIdeyalabs(
        api_key="your-api-key-here",
        max_tokens=150,
        presence_penalty=0.1
    )
    
    # Async completion
    response = await chat.ainvoke("What are the benefits of renewable energy?")
    print(f"Async Response: {response.content}")


async def streaming_example():
    """Streaming usage example."""
    print("\n=== Streaming Example ===")
    
    chat = ChatIdeyalabs(
        api_key="your-api-key-here",
        temperature=0.8
    )
    
    print("Streaming response: ", end="", flush=True)
    async for chunk in chat.astream("Write a haiku about artificial intelligence"):
        print(chunk, end="", flush=True)
    print("\n")


async def main():
    """Run all examples."""
    print("Note: Replace 'your-api-key-here' with your actual ChatIdeyalabs API key")
    print("=" * 60)
    
    try:
        # Run sync examples
        basic_example()
        message_objects_example()
        response_format_example()
        
        # Run async examples
        await async_example()
        await streaming_example()
        
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 To get an API key:")
        print("1. Contact your ChatIdeyalabs administrator")
        print("2. Admin users can create API keys using the /v1/api-keys endpoint")
        print("3. Replace 'your-api-key-here' with your actual API key")


if __name__ == "__main__":
    asyncio.run(main())