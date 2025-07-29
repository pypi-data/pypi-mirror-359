from pydantic import BaseModel
from zodable_idschema import IdSchema
from zodable_sample_package_multiplatform import MultiplatformUser
from uuid import UUID
from typing import Optional
from zodable_sample_package.digital.guimauve.example.Address import Address
from zodable_kotlin_primitives import KotlinPair
from datetime import datetime
from zodable_sample_package.digital.guimauve.example.Message import Message

class User(BaseModel):
    id: UUID
    name: str
    email: Optional[str] = None
    followers: int
    addresses: list[Address]
    tags: list[str]
    settings: dict[str, bool]
    eventsByYear: dict[int, list[str]]
    contactGroups: dict[str, list[Address]]
    coordinates: KotlinPair[float, float]
    createdAt: datetime
    day: datetime
    daytime: datetime
    externalUser: MultiplatformUser
    birthDate: datetime
    otherId: IdSchema
    custom_name: str
    message: Message[str]
