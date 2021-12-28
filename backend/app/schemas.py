from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
    id: int
    username: str
    is_rw: bool

    class Config:
        orm_mode = True


class CreateUser(BaseModel):
    username: str
    password: str
    is_rw: bool


class UpdateUser(BaseModel):
    username: str
    password: Optional[str]
    is_rw: bool

class AuthCredentials(BaseModel):
    username: str
    password: str
