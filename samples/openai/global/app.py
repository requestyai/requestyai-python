import os

import openai

from .ainsights import ainsights

openai.api_key = os.environ["OPENAI_API_KEY"]


def chat():
    user_input = input("Ask anything: ")

    messages = [{"role": "user", "content": user_input}]
    args = {"model": "gpt-4o-mini", "temperature": 0.7, "max_tokens": 150}
    response = openai.chat.completions.create(messages=messages, **args)

    ainsights.capture(messages=messages, args=args, response=response)

    print(response.choices[0].message.content)

    print(
        (
            "** See your insights on the Requesty platform: "
            "https://app.requesty.ai/chatlogs **"
        )
    )


def main():
    try:
        while True:
            chat()
    except KeyboardInterrupt:
        print("Terminated...")
    except Exception as ex:
        print("Error", ex)


if __name__ == "__main__":
    main()
