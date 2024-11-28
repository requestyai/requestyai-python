import os
import uuid

from openai import OpenAI
from pydantic import BaseModel

from requestyai import AInsights


class Model:
    def __init__(
        self, openai_api_key, openai_args, requesty_api_key, requesty_base_url
    ):
        self.__model = OpenAI(api_key=openai_api_key)
        self.__args = openai_args
        self.__insights = AInsights.new_client(
            api_key=requesty_api_key, base_url=requesty_base_url
        )

    def chat(self, user_id: str, user_input: str):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_input},
        ]

        class Response(BaseModel):
            answer: str

        response = self.__model.beta.chat.completions.parse(
            messages=messages, response_format=Response, **self.__args
        )

        self.__insights.capture(
            messages=messages, response=response, args=self.__args, user_id=user_id
        )

        content = response.choices[0].message.content
        if not content:
            return None

        return Response.model_validate_json(content)


def run(*, openai_key, requesty_key, requesty_base_url):
    openai_args = {"model": "gpt-4o-mini", "temperature": 0.7, "max_tokens": 150}
    model = Model(openai_key, openai_args, requesty_key, requesty_base_url)

    # Dummy "user ID"
    user_id = f"user_{uuid.uuid4()}"

    try:
        while True:
            user_input = input("Ask anything: ")
            reply = model.chat(user_id, user_input)
            print(reply)
            print(
                (
                    "** See your insights on the Requesty platform: "
                    "https://app.requesty.ai/chatlogs **"
                )
            )
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
