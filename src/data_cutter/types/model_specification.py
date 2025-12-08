from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

Number = Union[int, float]


class DtypeSpecification(BaseModel):
    # your existing stuff
    dim: int = 0
    dtype: str = "string"  # "string" | "number" | "integer" | "boolean" | "bbox" | custom name
    allowed_values: Optional[List[Any]] = None
    optional: bool = False

    # extra metadata (optional)
    description: Optional[str] = None

    # string constraints
    pattern: Optional[str] = None   # regex
    format: Optional[str] = None    # "email", "date-time", ...

    # number / integer constraints
    multipleOf: Optional[Number] = None
    minimum: Optional[Number] = None
    maximum: Optional[Number] = None
    exclusiveMinimum: Optional[Number] = None
    exclusiveMaximum: Optional[Number] = None

    # array constraints (only meaningful when dim == 1)
    minItems: Optional[int] = None
    maxItems: Optional[int] = None

class FieldSpec(BaseModel):
    name: str
    specification: DtypeSpecification

class CustomDTypeSpecification(BaseModel):
    name: str
    fields: List[FieldSpec]

class ModelSpecification(BaseModel):
    name: str = Field(..., description="Name of schema model")
    fields: List[FieldSpec] = Field(..., description="attributes in the schema")
    custom_dtypes: List[CustomDTypeSpecification] = Field(default_factory=list)