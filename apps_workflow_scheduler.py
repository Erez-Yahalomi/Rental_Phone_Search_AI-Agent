import threading
import queue
from typing import List
from .jobs import CallJob
from .rate_limit import TokenBucket

class Scheduler:
    """
    Concurrent scheduler with bounded concurrency and local rate limiting.
    """

    def __init__(self, executor, concurrency: int, rate_limit: TokenBucket):
        self.executor = executor
        self.concurrency = concurrency
        self.rate_limit = rate_limit
        self.q = queue.Queue()
        self.workers = []

    def submit(self, jobs: List[CallJob]):
        for job in jobs:
            self.q.put(job)

    def start(self):
        for _ in range(self.concurrency):
            t = threading.Thread(target=self._worker, daemon=True)
            t.start()
            self.workers.append(t)

    def _worker(self):
        while True:
            job = self.q.get()
            try:
                if self.rate_limit.acquire():
                    self.executor.execute(job)
                else:
                    # Backoff and requeue when limited
                    threading.Event().wait(0.5)
                    self.q.put(job)
            finally:
                self.q.task_done()

    def wait(self):
        self.q.join()
