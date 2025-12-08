from typing import Annotated, Literal, Union
from pydantic import BaseModel, Field

from data_cutter.types.model_specification import ModelSpecification

class PlainOutputSchema(BaseModel):
    type: Literal["plain"] = "plain"
    
class StructuredOutputSchema(BaseModel):
    type: Literal["structured"] = "structured"
    definition: ModelSpecification = Field(..., description="Schema Specification")
    
    
OutputSchema = Annotated[
    Union[
        PlainOutputSchema,
        StructuredOutputSchema
    ],
    Field(discriminator="type")
]