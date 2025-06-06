import time
from datetime import datetime
import sys
import os

# Add the parent directory to sys.path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from rate_limit import InMemoryRateLimiter

def test_rate_limit_terminal():
    """
    Terminal test for InMemoryRateLimiter:
    1. Creates a limiter with 5 messages/hour
    2. Sends messages to trigger rate limiting
    3. Verifies blocking behavior
    4. Tests manual reset
    """
    print("=== Terminal Rate Limit Test ===")
    rate_limiter = InMemoryRateLimiter(message_limit=5, reset_period_hours=1)
    session_id = f"test-session-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    print(f"\n[1] Created session: {session_id}")

    def print_status():
        status = rate_limiter.get_session_stats(session_id)
        print(f"→ Used: {status['current_count']} / {status['limit']} | Remaining: {status['remaining']}")
        if status['reset_time']:
            print(f"→ Resets at: {status['reset_time'].strftime('%Y-%m-%d %H:%M:%S')}, In: {status['time_until_reset']}")

    print_status()

    print("\n[2] Sending messages...")
    for i in range(1, 8):  # Try to send 7 messages
        print(f"\nAttempt {i}:")
        allowed = rate_limiter.check_limit(session_id)
        if allowed['allowed']:
            rate_limiter.increment_count(session_id)
            print(f"✅ Sent message {i}")
        else:
            print(f"❌ Blocked (rate limit reached)")
            print_status()
            break
        print_status()

    print("\n[3] Waiting 5 seconds and retrying...")
    time.sleep(5)
    retry = rate_limiter.check_limit(session_id)
    if retry['allowed']:
        print("❌ Should still be blocked, but got allowed")
    else:
        print("✅ Still blocked as expected")
        print_status()

    print("\n[4] Resetting rate limit...")
    rate_limiter.reset_session(session_id)
    status = rate_limiter.get_session_stats(session_id)
    if status['remaining'] == status['limit']:
        print("✅ Manual reset successful")
    else:
        print("❌ Manual reset failed")
    print_status()

    print("\n🎉 Test Completed")

if __name__ == "__main__":
    test_rate_limit_terminal()
