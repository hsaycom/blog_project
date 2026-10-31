'''
schemas.py — это слой валидации, десериализации и сериализации на Pydantic.
Он описывает, в каком виде данные приходят в API и в каком виде уходят наружу.
'''
from pydantic import BaseModel, Field, field_validator


class PostCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1, max_length=5000)

    @field_validator("title", "content")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Поле не может быть пустым")
        return value


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None = Field(default=None, min_length=1, max_length=5000)

    @field_validator("title", "content")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            raise ValueError("Поле не может быть null")
        value = value.strip()
        if not value:
            raise ValueError("Поле не может быть пустым")
        return value


class PostResponse(BaseModel):
    id: int
    title: str
    content: str

    model_config = {"from_attributes": True}


class PostsResponse(BaseModel):
    result: list[PostResponse]


class UserCreate(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip()
        local, at, domain = value.partition("@")
        if (
            not at
            or not local
            or "." not in domain
            or " " in value
            or value.count("@") != 1
        ):
            raise ValueError("Некорректный email")
        return value


class UserResponse(BaseModel):
    email: str
    message: str
