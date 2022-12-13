from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class Role(BaseModel):
    id: Optional[UUID]
    name: Optional[str]


class User(BaseModel):
    id: Optional[UUID]
    first_name: Optional[str]
    last_name: Optional[str]
    avatar: Optional[UUID]
    description: Optional[str]
    email: Optional[str]
    role: Optional[UUID] | Optional[Role]
    status: Optional[str]
    title: Optional[str]
    token: Optional[str]
