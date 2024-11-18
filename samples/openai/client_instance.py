import argparse
import uuid
from pathlib import Path
from typing import Optional

from openai import OpenAI
from pydantic import BaseModel

from requestyai import AInsights


def read_file(filename):
    with open(filename) as fin:
        return fin.read().strip()


def chat(
    openai_client: OpenAI,
    openai_args: dict,
    ainsights_client: AInsights,
    user_input: str,
    user_id: Optional[str] = None,
):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": user_input},
    ]

    class Response(BaseModel):
        answer: str

    response = openai_client.beta.chat.completions.parse(
        messages=messages, response_format=Response, **openai_args
    )

    ainsights_client.capture(
        messages=messages, args=openai_args, response=response, user_id=user_id
    )

    content = response.choices[0].message.content
    if not content:
        return None

    response_obj = Response.model_validate_json(content)
    return response_obj.answer


def run(*, requesty_key_file, openai_key_file, base_url):
    requesty_key = read_file(requesty_key_file)
    openai_key = read_file(openai_key_file)

    ainsights_client = AInsights.new_client(requesty_key, base_url)

    openai_client = OpenAI(api_key=openai_key)
    openai_args = {"model": "gpt-4o-mini", "temperature": 0.7, "max_tokens": 150}

    user_input = "What is the most famous quote by Albert Einstein?"

    user_id = f"user_{uuid.uuid4()}"

    try:
        while True:
            user_input = input("Ask anything: ")
            reply = chat(
                openai_client, openai_args, ainsights_client, user_input, user_id
            )
            print(reply)
    except KeyboardInterrupt:
        print("Terminated...")
    except Exception as ex:
        print("Error", ex)


def main():
    default_base_url = "https://api.requesty.ai"

    default_keys_dir = Path.home() / ".keys"
    default_requesty_key_file = default_keys_dir / "requesty"
    default_openai_key_file = default_keys_dir / "openai"

    parser = argparse.ArgumentParser(
        description="AI insights client sample application"
    )

    parser.add_argument(
        "--requesty_key_file",
        type=str,
        default=default_requesty_key_file,
        help="File that contains Requesty's API key (DEFAULT: %(default)s)",
    )

    parser.add_argument(
        "--openai_key_file",
        type=str,
        default=default_openai_key_file,
        help="File that contains OpenAI's API key (DEFAULT: %(default)s)",
    )

    parser.add_argument(
        "--base_url",
        type=str,
        default=default_base_url,
        help="The base url (DEFAULT: %(default)s)",
    )

    args = parser.parse_args()

    run(
        requesty_key_file=args.requesty_key_file,
        openai_key_file=args.openai_key_file,
        base_url=args.base_url,
    )


if __name__ == "__main__":
    main()
