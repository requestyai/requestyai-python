from typing import Optional, Union

from openai.types.chat import ChatCompletion
from pydantic import BaseModel


class AInsightsEvent(BaseModel):
    response: ChatCompletion
    messages: Union[None, str, list[str], list[dict]]
    template: Union[None, str, list[str], list[dict]]
    inputs: dict
    args: dict
    meta: dict
    user_id: Optional[str]
