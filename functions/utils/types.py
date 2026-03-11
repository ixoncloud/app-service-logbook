from datetime import datetime
import time
from typing import Annotated, Generic, TypeVar

from bson.objectid import ObjectId
from pydantic import BaseModel, ConfigDict, Field, PlainSerializer, WithJsonSchema

T = TypeVar("T")

JSONObjectId = Annotated[
    ObjectId,
    PlainSerializer(lambda x: str(x), return_type=str, when_used="json"),
    WithJsonSchema({"type": "string"}),
]

DateTimeISO = Annotated[
    datetime,
    PlainSerializer(lambda x: x.isoformat(), return_type=str, when_used="json"),
    WithJsonSchema({"type": "string"}),
]


class Note(BaseModel):
    id: JSONObjectId = Field(default_factory=ObjectId, alias="_id", serialization_alias="_id")
    user: str | None = Field(default=None, deprecated=True)
    text: str
    created_on: int = Field(default_factory=lambda: round(time.time() * 1000))

    author_id: str | None = Field(default=None)
    author_name: str | None = Field(default=None)

    editor_id: str | None = Field(default=None)
    editor_name: str | None = Field(default=None)
    updated_on: int | None = Field(default=None)

    subject: str | None = Field(default=None)
    category: int | None = Field(default=None)

    model_config = ConfigDict(arbitrary_types_allowed=True)


class NoteBasic(BaseModel):
    id: JSONObjectId = Field(default_factory=ObjectId, alias="_id", serialization_alias="_id")
    text: str
    created_on: DateTimeISO

    author_name: str | None = Field(default=None)

    editor_name: str | None = Field(default=None)
    updated_on: DateTimeISO | None = Field(default=None)

    subject: str | None = Field(default=None)
    category: int | None = Field(default=None)

    model_config = ConfigDict(arbitrary_types_allowed=True)


class Response(BaseModel, Generic[T]):
    data: T | None = Field(default=None)
    message: str | None = Field(default=None)
    success: bool = Field(default=True)


class SuccessResponse(Response[T]):
    success: bool = Field(default=True)


class ErrorResponse(Response[T]):
    message: str = Field(default="An unexpected error occurred")
    success: bool = Field(default=False)


class NoteEdit(BaseModel):
    note_id: str
    text: str

    subject: str | None = Field(default=None)
    category: int | None = Field(default=None)


class NoteAdd(BaseModel):
    text: str

    subject: str | None = Field(default=None)
    category: int | None = Field(default=None)


class NoteRemove(BaseModel):
    note_id: str
