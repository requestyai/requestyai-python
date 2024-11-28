import atexit
from concurrent.futures import Future
from typing import Optional, Union

from openai.types.chat import ChatCompletion

from ..http.async_client import AsyncClient
from .error import AInsightsValueError
from .types.event import AInsightsEvent


class AInsights:
    """The Insights client object that handles capturing and dispatching
    of events to the server
    """

    DEFAULT_BASE_URL = "https://ingestion.requesty.ai"

    __URL = "insight"

    def __init__(self, *, client: AsyncClient):
        self.__client = client
        atexit.register(self.close)

    def close(self):
        self.__client.close()

    def capture(
        self,
        *,
        response: ChatCompletion,
        messages: Union[None, str, list[str], list[dict]] = None,
        template: Union[None, str, list[str], list[dict]] = None,
        inputs: dict = {},
        args: dict = {},
        meta: dict = {},
        user_id: Optional[str] = None,
    ) -> Future:
        """Capture an AI interaction event and send it to the insights endpoint.

        This method dispatches the event asynchronously. The returned Future object
        can be ignored unless debugging is needed.

        You should pass to this method one of two argument combinations:

        Option #1 (Recommended): template and inputs
        Provide the prompt template with the formatting arguments, for example:
            "Read the following conversation: {conversation}
             Classify the user's sentiment.
             Choose only one of the following options: {options}"
        And the actual user inputs as a dictionary, for example"
            {
              "conversation": "Hi, I would like to return my watch ...",
              "options": "positive, neutral, negative"
            }

        Option #1: messages-only
        If you cannot provide the template and user inputs separately,
        just pass the `messages` argument that you use with the OpenAI client.

        Args:
            response: The ChatCompletion response from the OpenAI client.
            messages: The messages argument to the OpenAI client.
            template: The template used for the interaction.
            inputs: Dictionary of input parameters used in the interaction.
            args: Additional arguments used in the interaction.
            meta: Metadata associated with the interaction.
            user_id: Optional identifier for the user initiating the interaction.

        Returns:
            Future: An asynchronous result object representing the HTTP request.
        """

        if (messages is None) and (template is None or inputs is None):
            message = (
                "Please specify at least one of "
                "('messages') or ('template' and 'inputs')"
            )
            raise AInsightsValueError(message)

        event = AInsightsEvent(
            response=response,
            messages=messages,
            template=template,
            inputs=inputs,
            args=args,
            meta=meta,
            user_id=user_id,
        )

        return self.__client.put(url=self.__URL, data=event.model_dump_json())

    @staticmethod
    def new_client(*, api_key: str, base_url: Optional[str] = None) -> "AInsights":
        """Create a new AInsights client instance with the provided configuration.

        This is the recommended way to create new AInsights instances as it handles
        all the necessary dependency injection.

        Args:
            api_key: The API key for authentication with the insights service.
            base_url: [Optional] custom base URL for the insights service.
                      Defaults to DEFAULT_BASE_URL if not provided.

        Returns:
            AInsights: A configured AInsights client instance.
        """

        base_url = base_url if base_url is not None else AInsights.DEFAULT_BASE_URL

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        client = AsyncClient(base_url=base_url, headers=headers)
        return AInsights(client=client)
