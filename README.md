# RequestyAI Python API library

[![tests](https://github.com/requestyai/requestyai-python/actions/workflows/tests.yml/badge.svg)](https://github.com/requestyai/requestyai-python/actions/workflows/tests.yml)

**Deliver AI products in days, not months, using requesty.ai**

Step up your AI game with a simple integration:

- Real-time insights into your AI flows: See how your clients use your LLMs
- Hassle free auditing and logging: Don't stress about storage and infra
- Powerful analytics: Discover trends using your [Requesty's](https://requesty.ai) insight-explorer

## Installation

```bash
pip install requestyai
```

## AInsights

A client library to effortlessly integrate powerful insights into your AI flows.

Create a client with minimal configuration and capture and request/response pair
for future analysis.

### Notes

#### Thread-safety

The insights client is thread-safe.
You can safely use a single client from multiple threads.

#### Asynchronous

The insights client is asynchronous.
`capture()`-ing requests/responses is a non-blocking operation,
and it will not interrupt the flow of your application.

### Usage pattern #1: Create client instance

If you prefer creating and using client instance,
just add an `AInsights` instance next to your `OpenAI` one,
and capture every interaction by adding a single call.

It doesn't matter if you're using simple free-text outputs, JSON outputs or tools,
the insights client will capture everything.

> Check out this [working sample](https://github.com/requestyai/requestyai-python/blob/main/samples/openai/client_instance.py)

```python
from openai import OpenAI
from requestyai import AInsights


class OpenAIWrapper:
    def __init__(self, openai_api_key, requesty_api_key):
        self.model = OpenAI(api_key=openai_api_key)
        self.args = {
            model="gpt-4o",
            temperature=0.7,
            max_tokens=150
        }

        self.insights = AInsights.new_client(api_key=requesty_api_key)

    def chat(self, user_id: str, user_input: str):
        messages = [
            { "role": "system", "content": "You are a helpful assistant." },
            { "role": "user", "content": user_input }
        ]

        class Response(BaseModel):
            answer: str

        response = self.model.beta.chat.completions.parse(messages=messages,
                                                          response_format=Response,
                                                          **self.args)

        self.insights.capture(messages=messages,
                              response=response,
                              args=self.args,
                              user_id=user_id)

        return Response.model_validate_json(response.choices[0].message.content)


if __name__ == "__main__":
    requesty_api_key = os.environ["REQUESTY_API_KEY"]
    openai_api_key = os.environ["OPENAI_API_KEY"]

    wrapper = OpenAIWrapper(openai_api_key, requesty_api_key)

    # Dummy loggin to capture the user's ID
    user_id = input("User ID: ")

    while True:
        user_input = input("Ask any question?")
        response = wrapper.chat(user_id, user_input)
        print(response.answer)
```

### Usage pattern #2: Use a global instance

You like it simple. You just want to call OpenAI from anywhere in your code,
and the insights should be no different.

Just create a simple file (`ainsights_instance.py` is a reasonable name) in your project,
and import it everywhere. The client is thread-safe.

> Check out this [working sample](https://github.com/requestyai/requestyai-python/blob/main/samples/openai/client_global.py)

```python
import os
from requestyai import AInsights


requesty_key = os.environ["REQUESTY_KEY"]
ainsights = AInsights.new_client(api_key=requesty_key)
```

Then, calling OpenAI and capturing is as easy as:

It doesn't matter if you're using simple free-text outputs, JSON outputs or tools,
the insights client will capture everything.

```python
from openai import OpenAI
from ainsights_instance import ainsights


if __name__ == '__main__':
    openai.api_key = os.environ["OPENAI_API_KEY"]

    messages = [{ "role": "user", "content": user_input }]
    args = {
        model="gpt-4o-mini",
        temperature=0.7,
        max_tokens=150
    }
    response = openai.chat.completions.create(messages=messages, **args)

    ainsights.capture(messages=messages, response=response, args=args)

    print(response.choices[0].message.content)
```

### User tracking

If you want your insights to be tied to a specific user,
you can specify the `user_id` argument when calling `capture(...)`.

See "Usage pattern #1" above for specific details.

### Sample applications

Check out the [samples](https://github.com/requestyai/requestyai-python/blob/main/samples/) directory for working examples you can try out in no time.
