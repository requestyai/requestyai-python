import os

import openai

from .client_singleton import insights

openai.api_key = os.environ["OPENAI_KEY"]


def chat():
    user_input = input("Ask anything: ")

    messages = [{"role": "user", "content": user_input}]
    args = {"model": "gpt-4o-mini", "temperature": 0.7, "max_tokens": 150}
    response = openai.chat.completions.create(messages=messages, **args)

    insights.capture(messages=messages, args=args, response=response)

    print(response.choices[0].message.content)


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
