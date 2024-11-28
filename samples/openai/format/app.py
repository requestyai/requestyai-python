import os
import uuid

from openai import OpenAI

from requestyai import AInsights


def run(*, openai_key, requesty_key, requesty_base_url):
    ainsights_client = AInsights.new_client(
        api_key=requesty_key, base_url=requesty_base_url
    )

    openai_client = OpenAI(api_key=openai_key)
    openai_args = {"model": "gpt-4o-mini", "temperature": 0.7, "max_tokens": 150}

    template = [
        {"role": "system", "content": "You help users search the internet."},
        {
            "role": "user",
            "content": "What is the best query to learn more about {subject}",
        },
    ]

    user_id = f"user_{uuid.uuid4()}"

    try:
        while True:
            subject = input("What information do you want to find online? ")
            inputs = {"subject": subject}

            messages = [
                {
                    "role": message["role"],
                    "content": message["content"].format(**inputs),
                }
                for message in template
            ]

            response = openai_client.beta.chat.completions.parse(
                messages=messages, **openai_args
            )

            ainsights_client.capture(
                template=template,
                inputs=inputs,
                args=openai_args,
                response=response,
                user_id=user_id,
            )

            print(response.choices[0].message.content)
            print(
                (
                    "** See your insights on the Requesty platform: "
                    "https://app.requesty.ai/chatlogs **"
                )
            )
    except KeyboardInterrupt:
        print("Terminated...")
    except Exception as ex:
        import traceback

        traceback.print_exc()
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
