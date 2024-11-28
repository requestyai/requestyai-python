import os
import uuid
from typing import Optional

from openai import OpenAI, pydantic_function_tool
from pydantic import BaseModel

from requestyai import AInsights


class SearchInternet(BaseModel):
    query: str


def chat(
    openai_client: OpenAI,
    openai_args: dict,
    ainsights_client: AInsights,
    user_input: str,
    user_id: Optional[str] = None,
):
    messages = [
        {"role": "system", "content": "You help users search the internet."},
        {"role": "user", "content": user_input},
    ]

    tools = [pydantic_function_tool(SearchInternet)]

    response = openai_client.beta.chat.completions.parse(
        messages=messages, tools=tools, **openai_args
    )

    ainsights_client.capture(
        messages=messages, args=openai_args, response=response, user_id=user_id
    )

    message = response.choices[0].message
    if message.content:
        print(message.content)

    if message.tool_calls:
        for call in message.tool_calls:
            print(
                f"Call {call.function.name} with arguments: {call.function.arguments}"
            )

    print(
        (
            "** See your insights on the Requesty platform: "
            "https://app.requesty.ai/chatlogs **"
        )
    )


def run(*, openai_key, requesty_key, requesty_base_url):
    ainsights_client = AInsights.new_client(
        api_key=requesty_key, base_url=requesty_base_url
    )

    openai_client = OpenAI(api_key=openai_key)
    openai_args = {"model": "gpt-4o-mini", "temperature": 0.7, "max_tokens": 150}

    user_id = f"user_{uuid.uuid4()}"

    try:
        while True:
            user_input = input("What information do you want to find online? ")
            chat(openai_client, openai_args, ainsights_client, user_input, user_id)
    except KeyboardInterrupt:
        print("Terminated...")
    except Exception as ex:
        print("Error", ex)


def main():
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key is None:
        print("Missing environment variable 'OPENAI_API_KEY'")
        exit(1)

    requesty_key = os.environ.get("REQUESTY_API_KEY")
    if requesty_key is None:
        print("Missing environment variable 'REQUESTY_API_KEY'")
        exit(1)

    requesty_base_url = os.environ.get("REQUESTY_BASE_URL")

    run(
        openai_key=openai_key,
        requesty_key=requesty_key,
        requesty_base_url=requesty_base_url,
    )


if __name__ == "__main__":
    main()
