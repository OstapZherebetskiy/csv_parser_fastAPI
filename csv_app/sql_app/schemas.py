from pydantic import BaseModel
from datetime import date


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    firstname: str
    lastname: str
    gender: str
    category: str
    birthDate: date

    class Config:
        orm_mode = True
