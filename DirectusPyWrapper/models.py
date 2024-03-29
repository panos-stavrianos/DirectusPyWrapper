from __future__ import annotations

from typing import Optional, Union

from pydantic import BaseModel


class Role(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None

    class Config:
        collection = 'directus_roles'


class User(BaseModel):
    id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar: Optional[str] = None
    description: Optional[str] = None
    email: Optional[str] = None
    role: Union[str, Optional[Role], None] = None
    status: Optional[str] = None
    title: Optional[str] = None
    token: Optional[str] = None

    class Config:
        collection = 'directus_users'
