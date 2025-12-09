from typing import Annotated, Dict, List, Literal, Optional, Set, Union

from pydantic import BaseModel, Field

# ContentItemTemplate
class TextTemplate(BaseModel):
    """Template for text item"""
    type: Literal["text"] = "text"
    value: str = Field(
        ...,
        description="string template",
    )
    input_variables: List[str] = Field(
        default_factory=list,
        description="List of input variables used in the message",
    )
    
class ImageTemplate(BaseModel):
    """Template for image item"""
    type: Literal["image"] = "image"
    input_name: str = Field(..., description="Name of image to use")

class IterableTemplate(BaseModel):
    type: Literal["iterable"] = "iterable"
    input_variable: str = Field(
        ...,
        description="The variable name containing the list to iterate over"
    )
    items: List[Union[TextTemplate, ImageTemplate, "IterableTemplate"]] = Field(
        ...,
        description=""
    )

IterableTemplate.model_rebuild()

TemplateItem = Annotated[
    Union[
        TextTemplate,
        ImageTemplate,
        IterableTemplate
    ],
    Field(discriminator="type")
]


class MessageTemplate(BaseModel):
    role: str = Field("user", description="Message role value")
    contents: List[TemplateItem] = Field(..., description="content template to use")

class PromptTemplate(BaseModel):
    name: str = Field(
        ...,
        description="Name of the Prompt Template"
    )
    template_format: Literal["jinja2", "f-string"] = Field(
        "f-string",
        description="String format of the prompt template"
    )
    messages: List[MessageTemplate] = Field(
        ...,
        description="List of message templates",
        min_length=1
    )