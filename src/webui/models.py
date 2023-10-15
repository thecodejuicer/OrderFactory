from typing import Annotated, Union, Any

from bson import ObjectId
from pydantic import BaseModel, Field, AfterValidator, PlainSerializer, WithJsonSchema, ConfigDict


def validate_object_id(v: Any) -> ObjectId:
    if isinstance(v, ObjectId):
        return v
    if ObjectId.is_valid(v):
        return ObjectId(v)
    raise ValueError("Invalid ObjectId")


PyObjectId = Annotated[
    Union[str, ObjectId],
    AfterValidator(validate_object_id),
    PlainSerializer(lambda x: str(x), return_type=str),
    WithJsonSchema({"type": "string"}, mode="serialization"),
]


class Customer(BaseModel):
    mongo_id: PyObjectId = Field(alias="_id")
    id: str
    name: str
    email: str
    zip_code: str

    model_config = ConfigDict(arbitrary_types_allowed=True)
