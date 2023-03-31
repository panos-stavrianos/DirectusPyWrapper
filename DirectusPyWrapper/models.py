from typing import Optional


from pydantic import BaseModel


class Role(BaseModel):
    id: Optional[str]
    name: Optional[str]

    class Config:
        collection = 'directus_roles'


class User(BaseModel):
    id: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    avatar: Optional[str]
    description: Optional[str]
    email: Optional[str]
    role: Optional[str] | Optional[Role]
    status: Optional[str]
    title: Optional[str]
    token: Optional[str]

    class Config:
        collection = 'directus_users'
