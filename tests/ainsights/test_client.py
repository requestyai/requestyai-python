import json
from unittest.mock import Mock, patch

import pytest
from openai.types.chat import ChatCompletion, ParsedChatCompletionMessage, ParsedChoice
from openai.types.completion_usage import (
    CompletionTokensDetails,
    CompletionUsage,
    PromptTokensDetails,
)

from requestyai import AInsights
from requestyai.http.async_client import AsyncClient


@pytest.fixture
def mock_async_client():
    return Mock(spec=AsyncClient)


@pytest.fixture
def response():
    return ChatCompletion(
        id="chatcmpl-AUDTiRQf5GPu0FIr7JDLvOrlylztj",
        choices=[
            ParsedChoice(
                finish_reason="stop",
                index=0,
                logprobs=None,
                message=ParsedChatCompletionMessage(
                    content="How can I assist you today?",
                    refusal=None,
                    role="assistant",
                    audio=None,
                    function_call=None,
                    tool_calls=[],
                ),
            )
        ],
        created=1731765014,
        model="gpt-4o-mini-2024-07-18",
        object="chat.completion",
        service_tier=None,
        system_fingerprint="fp_0ba0d124f1",
        usage=CompletionUsage(
            completion_tokens=13,
            prompt_tokens=50,
            total_tokens=63,
            completion_tokens_details=CompletionTokensDetails(
                accepted_prediction_tokens=0,
                audio_tokens=0,
                reasoning_tokens=0,
                rejected_prediction_tokens=0,
            ),
            prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0),
        ),
    )


@pytest.fixture
def insights(mock_async_client):
    return AInsights(client=mock_async_client)


class TestAInsights:
    def test_init(self, mock_async_client):
        client = AInsights(client=mock_async_client)
        assert client._AInsights__client == mock_async_client

    def test_capture_response(self, insights, response):
        message = "test message"
        insights.capture(response=response, messages=message)
        insights._AInsights__client.put.assert_called_once()
        call_data = insights._AInsights__client.put.call_args[1]["data"]
        obj = json.loads(call_data)
        assert obj["response"] == response.model_dump()

    def test_capture_messages_string(self, insights, response):
        messages = "test message"
        insights.capture(response=response, messages=messages)
        insights._AInsights__client.put.assert_called_once()
        call_data = insights._AInsights__client.put.call_args[1]["data"]
        obj = json.loads(call_data)
        assert obj["messages"] == messages

    def test_capture_messages_list_of_strings(self, insights, response):
        messages = ["message1", "message2"]
        insights.capture(response=response, messages=messages)
        insights._AInsights__client.put.assert_called_once()
        call_data = insights._AInsights__client.put.call_args[1]["data"]
        obj = json.loads(call_data)
        assert obj["messages"] == messages

    def test_capture_messages_list_of_dicts(self, insights, response):
        messages = [{"role": "user", "content": "test"}]
        insights.capture(response=response, messages=messages)
        insights._AInsights__client.put.assert_called_once()
        call_data = insights._AInsights__client.put.call_args[1]["data"]
        obj = json.loads(call_data)
        assert obj["messages"] == messages

    def test_capture_args(self, insights, response):
        args = {"model": "gpt-4o-mini", "temperature": 0.7, "max_tokens": 150}
        messages = "test message"
        insights.capture(
            response=response,
            messages=messages,
            args=args,
        )
        insights._AInsights__client.put.assert_called_once()
        call_data = insights._AInsights__client.put.call_args[1]["data"]
        obj = json.loads(call_data)
        assert obj["args"] == args

    def test_capture_user_id(self, insights, response):
        user_id = "test_user"
        messages = [{"role": "user", "content": "test"}]
        insights.capture(
            response=response,
            messages=messages,
            user_id=user_id,
        )
        insights._AInsights__client.put.assert_called_once()
        call_data = insights._AInsights__client.put.call_args[1]["data"]
        obj = json.loads(call_data)
        assert obj["user_id"] == user_id

    def test_build(self):
        api_key = "test_key"
        custom_url = "https://custom.api.com"
        client = AInsights.new_client(api_key=api_key, base_url=custom_url)
        assert isinstance(client, AInsights)

    @patch("requestyai.ainsights.client.AsyncClient")
    def test_build_with_base_url(self, mock_async_client):
        api_key = "test_key"
        AInsights.new_client(api_key=api_key)

        mock_async_client.assert_called_once_with(
            base_url=AInsights.DEFAULT_BASE_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        )

    @patch("requestyai.ainsights.client.AsyncClient")
    def test_build_with_custom_url(self, mock_async_client):
        api_key = "test_key"
        base_url = "https://custom.api.com"
        AInsights.new_client(api_key=api_key, base_url=base_url)

        mock_async_client.assert_called_once_with(
            base_url=base_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        )
