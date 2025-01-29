import random
from typing import Dict
import time
from collections import deque

class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests
        self.user_history: Dict[str, deque] = {}

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        """Remove timestamps outside the current window."""
        if user_id in self.user_history:
            while self.user_history[user_id] and self.user_history[user_id][0] <= current_time - self.window_size:
                self.user_history[user_id].popleft()
            if not self.user_history[user_id]:
                del self.user_history[user_id]

    def can_send_message(self, user_id: str) -> bool:
        """Check if the user can send a message."""
        current_time = time.time()
        self._cleanup_window(user_id, current_time)
        return len(self.user_history.get(user_id, [])) < self.max_requests

    def record_message(self, user_id: str) -> bool:
        """Record a new message and update the user's history."""
        current_time = time.time()
        if self.can_send_message(user_id):
            if user_id not in self.user_history:
                self.user_history[user_id] = deque()
            self.user_history[user_id].append(current_time)
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        """Calculate the time until the user can send the next message."""
        current_time = time.time()
        self._cleanup_window(user_id, current_time)
        if user_id not in self.user_history or len(self.user_history[user_id]) < self.max_requests:
            return 0.0
        return max(0.0, self.user_history[user_id][0] + self.window_size - current_time)


# Demonstration of the rate limiter
def test_rate_limiter():
    # Create a rate limiter with a 10-second window and 1 message max
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    # Simulate a stream of messages from users (user IDs from 1 to 5)
    print("\n=== Message Stream Simulation ===")
    for message_id in range(1, 11):
        user_id = message_id % 5 + 1  # User IDs cycle from 1 to 5
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Message {message_id:2d} | User {user_id} | "
              f"{'✓' if result else f'× (wait {wait_time:.1f}s)'}")
        time.sleep(random.uniform(0.1, 1.0))  # Simulate realistic delays

    # Wait for the window to clear
    print("\nWaiting for 4 seconds...")
    time.sleep(4)

    print("\n=== New Message Stream After Waiting ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1  # User IDs cycle from 1 to 5
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Message {message_id:2d} | User {user_id} | "
              f"{'✓' if result else f'× (wait {wait_time:.1f}s)'}")
        time.sleep(random.uniform(0.1, 1.0))  # Simulate realistic delays


if __name__ == "__main__":
    test_rate_limiter()
