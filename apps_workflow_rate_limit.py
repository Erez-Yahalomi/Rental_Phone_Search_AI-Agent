import time
from threading import Lock

class TokenBucket:
    """
    Simple local token bucket used by scheduler to throttle call starts.
    """
    def __init__(self, rate_per_sec: float, burst: int):
        self.rate = rate_per_sec
        self.capacity = burst
        self.tokens = burst
        self.last = time.time()
        self.lock = Lock()

    def acquire(self, tokens=1):
        with self.lock:
            now = time.time()
            elapsed = now - self.last
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last = now
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
