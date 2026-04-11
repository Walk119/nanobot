"""Test the /api/skills/agent/chat API endpoint."""
import requests
import json


def test_agent_chat_api():
    """Test the agent chat API endpoint."""
    # API endpoint URL
    url = "http://127.0.0.1:8000/api/skills/agent/chat"
    
    # Test case 1: Basic message
    print("Test 1: Basic message")
    data = {
        "message": "Hello, how are you?"
    }
    
    response = requests.post(url, json=data)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    assert "content" in response.json(), "Response should contain 'content' field"
    print("✓ Test 1 passed\n")
    
    # Test case 2: Message with custom session ID
    print("Test 2: Message with custom session ID")
    data = {
        "message": "What can you do?",
        "session_id": "test_session_123"
    }
    
    response = requests.post(url, json=data)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    assert "content" in response.json(), "Response should contain 'content' field"
    print("✓ Test 2 passed\n")
    
    # Test case 3: Complex message
    print("Test 3: Complex message")
    data = {
        "message": "帮我整理一下近期中东的局势信息"
    }
    
    response = requests.post(url, json=data)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    assert "content" in response.json(), "Response should contain 'content' field"
    print("✓ Test 3 passed\n")
    
    print("All tests passed!")


if __name__ == "__main__":
    test_agent_chat_api()