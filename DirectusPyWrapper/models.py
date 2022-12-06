from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    avatar: Optional[str]
    company: Optional[str]
    description: Optional[str]
    email: Optional[str]
    first_name: Optional[str]
    id: Optional[str]
    last_name: Optional[str]
    role: Optional[str]
    status: Optional[str]
    title: Optional[str]
    token: Optional[str]
