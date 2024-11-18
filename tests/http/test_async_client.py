from unittest.mock import Mock, call, patch

import httpx
import pytest

from requestyai.http.async_client import AsyncClient
from requestyai.http.retry_jitter_type import RetryJitterType
from requestyai.http.retry_policy import RetryPolicy
from requestyai.http.retry_transport import RetryTransport


def build_mock_request(method):
    request = Mock(spec=httpx.Request)
    request.method = method
    return request


def build_mock_response(status_code):
    response = Mock(spec=httpx.Response)
    response.status_code = status_code
    return response


class TestRetryPolicy:
    def test_default_initialization(self):
        policy = RetryPolicy()
        assert policy.max_retries == RetryPolicy.DEFAULT_MAX_RETRIES
        assert policy.backoff_factor == RetryPolicy.DEFAULT_BACKOFF_FACTOR
        assert policy.status_forcelist == set(
            RetryPolicy.DEFAULT_STATUS_FORCELIST.keys()
        )
        assert policy.allowed_methods == RetryPolicy.DEFAULT_ALLOWED_METHODS
        assert policy.jitter_type == RetryPolicy.DEFAULT_JITTER_TYPE

    def test_custom_initialization(self):
        policy = RetryPolicy(
            max_retries=5,
            backoff_factor=0.5,
            status_forcelist=[500, 502],
            allowed_methods=["GET"],
            jitter_type=RetryJitterType.NONE,
        )
        assert policy.max_retries == 5
        assert policy.backoff_factor == 0.5
        assert policy.status_forcelist == {500, 502}
        assert policy.allowed_methods == {"GET"}
        assert policy.jitter_type == RetryJitterType.NONE

    @pytest.mark.parametrize(
        "factor,retry,expected",
        [
            (0.5, 1, 0.5),
            (0.5, 2, 1),
            (0.5, 3, 2),
        ],
    )
    def test_backoff_calculation_jitter_none(self, factor, retry, expected):
        policy = RetryPolicy(backoff_factor=factor, jitter_type=RetryJitterType.NONE)
        assert policy.get_backoff_time(retry) == expected

    @pytest.mark.parametrize(
        "status_code,method,expected",
        [
            (500, "GET", True),
            (200, "GET", False),
            (500, "POST", False),
            (429, "GET", True),
        ],
    )
    def test_retry_decision(self, status_code, method, expected):
        policy = RetryPolicy()
        response = build_mock_response(status_code)
        assert policy.is_retry(response, method) == expected


class TestRetryTransport:
    async def test_successful_request(self):
        retry_policy = RetryPolicy()
        transport = RetryTransport(retry_policy=retry_policy)

        mock_response = build_mock_response(200)
        mock_request = build_mock_request("GET")

        with patch.object(
            httpx.HTTPTransport, "handle_request", return_value=mock_response
        ):
            response = transport.handle_request(mock_request)
            assert response == mock_response

    async def test_retry_on_error(self):
        retry_policy = RetryPolicy()
        transport = RetryTransport(retry_policy=retry_policy)

        mock_response = build_mock_response(200)
        mock_request = build_mock_request("GET")

        with patch.object(
            httpx.HTTPTransport,
            "handle_request",
            side_effect=[httpx.NetworkError("Timed-out"), mock_response],
        ):
            response = transport.handle_request(mock_request)
            assert response == mock_response


class TestAsyncClient:
    @pytest.fixture
    def client(self):
        return AsyncClient(
            base_url="http://test.com",
            headers={"User-Agent": "Test"},
        )

    def test_initialization(self, client):
        assert isinstance(client._AsyncClient__client, httpx.Client)

    async def test_get_request(self, client):
        with patch.object(httpx.Client, "get") as mock_get:
            mock_get.return_value = build_mock_response(200)

            future = client.get("/test")
            future.result()

        assert mock_get.called

    async def test_client_close(self, client):
        with patch.object(httpx.Client, "close") as mock_close:
            client.close()

        assert mock_close.called

    @pytest.mark.timeout(AsyncClient.SHUTDOWN_TIMEOUT + 1)
    def test_client_dispatches_queued_messages_on_close(self, client):
        args1 = {"data": "test1"}
        args2 = {"data": "test2"}

        with patch.object(httpx.Client, "put") as mock_dispatch:
            mock_dispatch.return_value = build_mock_response(200)

            client.put(**args1)
            client.put(**args2)

            client.close()

        assert mock_dispatch.call_count == 2
        mock_dispatch.assert_has_calls([call(**args1), call(**args2)])


@pytest.mark.integration_test
class TestIntegration:
    @pytest.mark.asyncio
    async def test_retry_with_real_request(self):
        client = AsyncClient(base_url="http://httpbin.org", headers={})

        response = client.get("/status/500")
        result = response.result()
        assert result.status_code == 500

        client.close()
