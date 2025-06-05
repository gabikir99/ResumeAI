import time
from datetime import datetime, timedelta
import sys
import os

# Add the parent directory to sys.path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rate_limit import InMemoryRateLimiter

def test_rate_limit_terminal():
    """
    Test the rate limit functionality in the terminal.
    This script will:
    1. Create a rate limiter with 5 messages per hour
    2. Create a test session
    3. Send messages until rate limit is reached
    4. Display rate limit information
    5. Wait a short time and try again to show it's still limited
    """
    print("=== Terminal Rate Limit Test ===")
    print("Testing with 5 messages per hour limit")
    
    # Create rate limiter with 5 messages per hour
    rate_limiter = InMemoryRateLimiter(message_limit=5, reset_period_hours=1)
    
    # Create a test session
    session_id = "test-session-" + datetime.now().strftime("%Y%m%d%H%M%S")
    print(f"\n1. Created test session: {session_id}")
    
    # Check initial status
    status = rate_limiter.get_session_stats(session_id)
    print(f"Initial status: {status['remaining']}/{status['limit']} messages remaining")
    
    # Send messages until rate limit is reached
    print("\n2. Sending messages until rate limit is reached...")
    
    for i in range(1, 8):  # Try to send 7 messages (2 over the limit)
        print(f"\nAttempting to send message {i}...")
        
        # Check if allowed before sending
        check_result = rate_limiter.check_limit(session_id)
        
        if check_result['allowed']:
            # Simulate sending a message
            rate_limiter.increment_count(session_id)
            print(f"✅ Message {i} sent successfully")
            
            # Get updated status
            status = rate_limiter.get_session_stats(session_id)
            print(f"Status: {status['remaining']}/{status['limit']} messages remaining")
        else:
            # Rate limit reached
            print(f"❌ Rate limit reached after {i-1} messages!")
            print(f"Status: {status['current_count']}/{status['limit']} messages used")
            
            if status['reset_time']:
                print(f"Reset time: {status['reset_time'].strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"Time until reset: {status['time_until_reset']}")
            
            break
    
    # Wait a short time and try again
    print("\n3. Waiting 5 seconds and trying again...")
    time.sleep(10)
    
    check_result = rate_limiter.check_limit(session_id)
    if not check_result['allowed']:
        print("✅ Still rate limited as expected!")
        print(f"Status: {check_result['current_count']}/{check_result['limit']} messages used")
        print(f"Reset time: {check_result['reset_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        # Calculate time until reset
        time_until_reset = check_result['reset_time'] - datetime.now()
        print(f"Time until reset: {str(time_until_reset).split('.')[0]}")
    else:
        print("❌ Test failed: Rate limit should still be in effect!")
    
    # Test reset functionality
    print("\n4. Testing manual reset functionality...")
    rate_limiter.reset_session(session_id)
    
    # Check if reset worked
    status = rate_limiter.get_session_stats(session_id)
    print(f"After reset: {status['remaining']}/{status['limit']} messages remaining")
    
    if status['remaining'] == status['limit']:
        print("✅ Manual reset successful!")
    else:
        print("❌ Manual reset failed!")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_rate_limit_terminal()
