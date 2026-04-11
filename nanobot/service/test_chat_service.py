"""Test chat service functionality."""
import asyncio
from .chat_service import ChatService


async def test_chat_service():
    """Test the chat service functionality."""
    # Create chat service instance
    chat_service = ChatService(config_path='nanobot/cli/workspace/config.json', workspace='nanobot/cli/workspace')
    
    try:
        # Test message
        test_message = "Hello, how are you?"
        session_id = "test_session"
        
        # Process message
        response = await chat_service.process_message(test_message, session_id)
        
        # Print response
        print("Test message:", test_message)
        print("Response:", response)
        
        # Verify response structure
        assert "content" in response, "Response should contain 'content' field"
        assert isinstance(response["content"], str), "Content should be a string"
        
        # Test with another message
        test_message_2 = "帮我整理一下近期中东的局势信息"
        response_2 = await chat_service.process_message(test_message_2, session_id)
        
        # Print response
        print("\nTest message 2:", test_message_2)
        print("Response 2:", response_2)
        
        # Verify response structure
        assert "content" in response_2, "Response should contain 'content' field"
        assert isinstance(response_2["content"], str), "Content should be a string"
        
        print("\nAll tests passed!")
        
    finally:
        # Close the chat service
        await chat_service.close()


if __name__ == "__main__":
    asyncio.run(test_chat_service())