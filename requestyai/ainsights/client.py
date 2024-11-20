import atexit
from concurrent.futures import Future
from typing import Optional, Union

from openai.types.chat import ChatCompletion

from ..http.async_client import AsyncClient
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
        response: ChatCompletion,
        messages: Union[str, list[str], list[dict]],
        args: dict = {},
        meta: dict = {},
        user_id: Optional[str] = None,
    ) -> Future:
        """Capture an event by sending it to the insights endpoint.
        This method dispatches the event asynchronously, and unless you are
        debugging any issues, you probably want to ignore the return value.
        """

        event = AInsightsEvent(
            response=response,
            messages=messages,
            args=args,
            meta=meta,
            user_id=user_id,
        )

        return self.__client.put(url=self.__URL, data=event.model_dump_json())

    @staticmethod
    def new_client(*, api_key: str, base_url: Optional[str] = None) -> "AInsights":
        """The standard way of creating new InsightsClient objects.
        As the InsightsClient uses dependency injections, this constructor
        handles the heavy lifting for you
        """

        base_url = base_url if base_url is not None else AInsights.DEFAULT_BASE_URL

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        client = AsyncClient(base_url=base_url, headers=headers)
        return AInsights(client=client)
