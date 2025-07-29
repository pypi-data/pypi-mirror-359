from pydantic import BaseModel
from typing import Union
from typing import Literal

class EmptyPayload(BaseModel):
    type: Literal["EMPTY"]

class TextPayload(BaseModel):
    text: str
    type: Literal["TEXT"]

Payload = Union[EmptyPayload, TextPayload]
