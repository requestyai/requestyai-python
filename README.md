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

Create a client with minimal configuration and capture and request/response pair for future analysis.

### Notes

#### Thread-safety

The insights client is thread-safe.
You can safely use a single client from multiple threads.

#### Asynchronous

The insights client is asynchronous.
`capture()`-ing requests/responses is a non-blocking operation,
and it will not interrupt the flow of your application.

### Usage pattern #1: Use a global instance

Just create a simple file (`ainsights.py` is a reasonable name) in your project,
and import it everywhere. The client is thread-safe.

> Check out this [working sample app](https://github.com/requestyai/requestyai-python/blob/main/samples/openai/global/app.py)

Notes:
- Make sure to set the environment variable `OPENAI_API_KEY` to your OpenAI API key.
- Make sure to set the environment variable `REQUESTY_API_KEY` to your Requesty API key.

```python
import os
from requestyai import AInsights


ainsights = AInsights.new_client(api_key=os.environ["REQUESTY_API_KEY"])
```

Then, calling OpenAI and capturing is as easy as:

It doesn't matter if you're using simple free-text outputs, JSON outputs or tools,
the insights client will capture everything.

```python
import os
from openai import OpenAI
from .ainsights import ainsights

openai.api_key = os.environ["OPENAI_API_KEY"]


if __name__ == '__main__':
    user_input = input("Ask anything: ")

    messages = [{"role": "user", "content": user_input}]
    args = {"model": "gpt-4o-mini", "temperature": 0.7, "max_tokens": 150}
    response = openai.chat.completions.create(messages=messages, **args)

    ainsights.capture(messages=messages, response=response, args=args)

    print(response.choices[0].message.content)
```

### Usage pattern #2: Create a client instance

If you prefer creating and using client instance,
just add an `AInsights` instance next to your `OpenAI` one,
and capture every interaction by adding a single call.

It doesn't matter if you're using simple free-text outputs, JSON outputs or tools,
the insights client will capture everything.

> Check out this [working sample app](https://github.com/requestyai/requestyai-python/blob/main/samples/openai/basic/app.py)

Notes:
- Make sure to set the environment variable `OPENAI_API_KEY` to your OpenAI API key.
- Make sure to set the environment variable `REQUESTY_API_KEY` to your Requesty API key.

```python
from openai import OpenAI
from pydantic import BaseModel
from requestyai import AInsights


class Model:
    def __init__(self, openai_api_key, openai_args, requesty_api_key):
        self.__model = OpenAI(api_key=openai_api_key)
        self.__args = openai_args
        self.__insights = AInsights.new_client(api_key=requesty_api_key)

    def chat(self, user_id: str, user_input: str):
        messages = [
            {"role": "system", "content": "You are a helpful search assistant."},
            {"role": "user", "content": user_input}
        ]

        meta = {"class": "Search assistant"}

        class Response(BaseModel):
            answer: str

        response = self.__model.beta.chat.completions.parse(
            messages=messages, response_format=Response, **self.args
        )

        self.__insights.capture(messages=messages,
                                response=response,
                                args=self.args,
                                meta=meta,
                                user_id=user_id)

        content = response.choices[0].message.content
        if not content:
            return None

        return Response.model_validate_json(content)
```

### Meta tagging

If you want to add additional, custom, tags to your model interactions,
the `capture()` method allows you to specify an extra argument, called `meta`.

You can then use those tags to group and inspect relevant traffic on the UI.

See "Usage pattern #2" above for specific details.

### User tracking

If you want your insights to be tied to a specific user,
you can specify the `user_id` argument when calling `capture(...)`.

The `user_id` is not part of the `meta` dictionary,
because the platform can leverage this specific piece of information
to track usage patterns and provide additional insights.

See "Usage pattern #2" above for specific details.

### Sample applications

Check out the [samples](https://github.com/requestyai/requestyai-python/blob/main/samples/) directory for working examples you can try out in no time.

Set up the required virtual Python environment easily using poetry:
```
poetry install
poetry shell
```

From inside the virtual environment shell, run the samples using:
```
REQUESTY_KEY="<YOUR_REQUESTY_KEY>" OPENAI_KEY="<YOUR_OPENAI_KEY>" \
python -m samples.openai.basic.app
```
