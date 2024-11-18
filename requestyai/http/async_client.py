import threading
from concurrent.futures import Future
from datetime import datetime, timedelta
from queue import Empty, Queue
from typing import Optional

import httpx

from .atomic import AtomicFlag
from .retry_policy import RetryPolicy
from .retry_transport import RetryTransport


class AsyncClient:
    DEFAULT_TIMEOUT = 10.0
    QUEUE_TIMEOUT = 0.1
    SHUTDOWN_TIMEOUT = 3.0

    def __init__(
        self,
        *,
        base_url: str,
        headers: dict,
        timeout: float = DEFAULT_TIMEOUT,
        retry_policy: Optional[RetryPolicy] = None,
    ):
        retry_policy = retry_policy if retry_policy else RetryPolicy()
        transport = RetryTransport(retry_policy=retry_policy)

        self.__client = httpx.Client(
            base_url=base_url,
            headers=headers,
            timeout=timeout,
            transport=transport,
        )

        self.__closing = AtomicFlag()
        self.__closed = threading.Event()

        self.__queue = Queue()

        self.__thread = threading.Thread(target=self._run_loop, daemon=True)
        self.__thread.start()

    @property
    def base_url(self):
        return self.__client.base_url

    @property
    def headers(self):
        return self.__client.headers

    @property
    def timeout(self):
        return self.__client.timeout

    @staticmethod
    def __should_run_loop(closing_ts, closing_delay):
        # Common case, client wasn't closed
        if closing_ts is None:
            return True

        # Client was closed, but we allow it a grace period to dispatch everything
        # that is still in the queue
        if datetime.now() - closing_ts < closing_delay:
            return True

        return False

    def _run_loop(self):
        """Process jobs in an infinite loop.
        Notes:
        - Use custom logic to allow graceful dispatch of queued jobs up to
        SHUTDOWN_TIMEOUT seconds.
        - Catch all httpx.Client's exceptions by returning them as the future
        value, whereas other exceptions will cause the worker to stop.
        """

        closing_ts = None
        closing_delay = timedelta(seconds=self.SHUTDOWN_TIMEOUT)

        while self.__should_run_loop(closing_ts, closing_delay):
            # Capture the timestamp the first time we see the flag set
            if self.__closing.is_set() and closing_ts is None:
                closing_ts = datetime.now()

            try:
                job = self.__queue.get(timeout=self.QUEUE_TIMEOUT)
            except Empty:
                if self.__closing.is_set():
                    break
                else:
                    continue

            try:
                job()
                self.__queue.task_done()
            except Exception:
                # Job expections should be caught inside the job and returned
                # via the future object. If we get here, something bad happened.
                break

        self.__closed.set()

    def __put_job(self, method, *args, **kwargs) -> Future:
        future = Future()

        def job():
            try:
                result = method(*args, **kwargs)
            except Exception as ex:
                result = ex
            future.set_result(result)

        self.__queue.put(job)
        return future

    def get(self, *args, **kwargs) -> Future:
        return self.__put_job(self.__client.get, *args, **kwargs)

    def post(self, *args, **kwargs) -> Future:
        return self.__put_job(self.__client.post, *args, **kwargs)

    def put(self, *args, **kwargs) -> Future:
        return self.__put_job(self.__client.put, *args, **kwargs)

    def delete(self, *args, **kwargs) -> Future:
        return self.__put_job(self.__client.delete, *args, **kwargs)

    def close(self):
        was_closing = self.__closing.get_and_set()
        if was_closing:  # If it's a double-close, just wait
            self.__closed.wait()
            return

        # Wait for the thread to close gracefully by dispatching the last jobs
        self.__closed.wait(timeout=self.SHUTDOWN_TIMEOUT)

        # Close the actual underlying client to cut it short if it didn't
        self.__client.close()

        self.__thread.join()
