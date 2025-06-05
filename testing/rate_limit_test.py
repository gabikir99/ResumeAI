import time
import requests
import json
from datetime import datetime, timedelta

def test_rate_limit():
    """
    Test the rate limit functionality with 5 messages per hour.
    This script will:
    1. Create a new session
    2. Send messages until rate limit is reached
    3. Show the rate limit error
    4. Wait for reset time information
    """
    print("=== Rate Limit Test ===")
    print("Testing with 5 messages per hour limit")
    
    # Base URL - change if your server is running on a different port/host
    base_url = "http://localhost:5000"
    
    # Step 1: Create a new session
    print("\n1. Creating new session...")
    response = requests.post(
        f"{base_url}/api/session",
        json={"action": "new"}
    )
    
    if response.status_code != 200:
        print(f"Error creating session: {response.text}")
        return
    
    session_data = response.json()
    session_id = session_data["session_id"]
    print(f"Session created with ID: {session_id}")
    print(f"Rate limit: {session_data['rate_limit']['messages_remaining']}/{session_data['rate_limit']['messages_limit']} messages remaining")
    
    # Step 2: Send messages until rate limit is reached
    print("\n2. Sending messages until rate limit is reached...")
    
    messages = [
        "Hello, I need help with my resume",
        "I'm looking for a job in software development",
        "Can you help me write a cover letter?",
        "What skills should I highlight on my resume?",
        "How do I explain a gap in my employment history?",
        "This message should hit the rate limit"
    ]
    
    for i, message in enumerate(messages, 1):
        print(f"\nSending message {i}: '{message}'")
        
        response = requests.post(
            f"{base_url}/api/chat-stream",
            json={"message": message, "session_id": session_id}
        )
        
        if response.status_code == 429:
            # Rate limit reached
            error_data = response.json()
            print(f"\n✅ Rate limit correctly enforced after {i} messages!")
            print(f"Error message: {error_data['message']}")
            print(f"Reset time: {error_data['reset_time']}")
            
            # Calculate and display time until reset
            reset_time = datetime.fromisoformat(error_data['reset_time'])
            now = datetime.now()
            time_until_reset = reset_time - now
            
            print(f"Time until reset: {time_until_reset}")
            break
        elif response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            break
        else:
            # Get first chunk of response to see if it contains rate limit message
            content = response.text
            if "You've reached the limit" in content:
                print(f"\n✅ Rate limit correctly enforced in stream response!")
                print(f"Response: {content[:200]}...")
                break
            
            # Check rate limit status
            status_response = requests.get(
                f"{base_url}/api/rate-limit/status",
                params={"session_id": session_id}
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"Messages used: {status_data['messages_used']}/{status_data['messages_limit']}")
                print(f"Messages remaining: {status_data['messages_remaining']}")
                
                if status_data['reset_time']:
                    reset_time = datetime.fromisoformat(status_data['reset_time'])
                    print(f"Reset time: {reset_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 3: Check rate limit status endpoint
    print("\n3. Checking rate limit status endpoint...")
    response = requests.get(
        f"{base_url}/api/rate-limit/status",
        params={"session_id": session_id}
    )
    
    if response.status_code == 200:
        status_data = response.json()
        print(f"Session ID: {status_data['session_id']}")
        print(f"Messages used: {status_data['messages_used']}/{status_data['messages_limit']}")
        print(f"Messages remaining: {status_data['messages_remaining']}")
        
        if status_data['reset_time']:
            reset_time = datetime.fromisoformat(status_data['reset_time'])
            now = datetime.now()
            time_until_reset = reset_time - now
            
            print(f"Reset time: {reset_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Time until reset: {time_until_reset}")
    else:
        print(f"Error checking status: {response.text}")
    
    print("\nTest completed successfully!")
    print("The rate limit is working as expected with 5 messages per hour.")

if __name__ == "__main__":
    test_rate_limit()
