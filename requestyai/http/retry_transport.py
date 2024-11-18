import time

import httpx

from .retry_policy import RetryPolicy


class RetryTransport(httpx.HTTPTransport):
    def __init__(self, retry_policy: RetryPolicy, **kwargs):
        super().__init__(**kwargs)
        self.__retry_policy = retry_policy

    def handle_request(self, request):
        retries = 0

        while True:
            try:
                response = super().handle_request(request)

                if not self.__retry_policy.is_retry(response, request.method):
                    return response

                if retries >= self.__retry_policy.max_retries:
                    return response

            except httpx.NetworkError:
                if retries >= self.__retry_policy.max_retries:
                    raise

            retries += 1
            backoff = self.__retry_policy.get_backoff_time(retries)
            time.sleep(backoff)
