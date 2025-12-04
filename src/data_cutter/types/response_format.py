from typing import Any, Literal, Optional, Union

from pydantic import BaseModel, Field


class JsonSchemaResponseFormat(BaseModel):
    name: str = Field("Output", description="Name of the Response Format")
    description: Optional[str] = None
    # schema is the field in openai but that causes conflicts with pydantic so
    # instead use json_schema with an alias
    json_schema: Optional[dict[str, Any]] = Field(None, alias='schema')
    strict: Optional[bool] = Field(True)


class ResponseFormat(BaseModel):
    type: Literal["text", "json_object", "json_schema"]
    json_schema: Optional[JsonSchemaResponseFormat] = None

AnyResponseFormat = Union[ResponseFormat]