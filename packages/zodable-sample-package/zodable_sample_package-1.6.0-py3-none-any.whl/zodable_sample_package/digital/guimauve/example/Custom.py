from pydantic import BaseModel

from typing import List

class Custom(BaseModel):
    name: str
    age: int
    is_active: bool
    tags: List[str]
