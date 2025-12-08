from typing import Annotated, Dict, List, Literal, Optional, Set, Union

from pydantic import BaseModel, Field


class TextTemplate(BaseModel):
    """Template for text content"""
    type: Literal["text"] = "text"
    content: str = Field(
        ...,
        description="string template",
    )
    input_variables: List[str] = Field(
        default_factory=list,
        description="List of input variables used in the message",
    )
    

class ImageTemplate(BaseModel):
    """Template for image content"""
    type: Literal["image"] = "image"
    input_name: str = Field(..., description="Name of image to use")

ContentTemplate = Annotated[
    Union[
        TextTemplate,
        ImageTemplate
    ],
    Field(discriminator="type")
]


class StaticContentTemplateGroup(BaseModel):
    """Group of static content templates (no iteration)"""
    type: Literal["static"] = "static"
    items: List[ContentTemplate] = Field(
        ...,
        description="List of ContentTemplates in this group",
        min_length=1
    )

class IterableContentTemplateGroup(BaseModel):
    """Group of content templates that will be iterated over"""
    type: Literal["iterable"] = "iterable"
    items: List[Union[ContentTemplate, "IterableContentTemplateGroup"]] = Field(
        ...,
        description="List of ContentTemplates or nested iterable groups to iterate over",
        min_length=1
    )
    input_key: Optional[str] = Field(
        None,
        description="The variable name containing the list to iterate over. If not specified, will auto-detect from available list variables."
    )

# Enable forward references for nested iteration
IterableContentTemplateGroup.model_rebuild()

ContentTemplateGroup = Annotated[
    Union[
        StaticContentTemplateGroup,
        IterableContentTemplateGroup
    ],
    Field(discriminator="type")
]

class BaseMessageTemplate(BaseModel):
    role: str = Field("user", description="Message role value")

class SingleContentMessageTemplate(BaseMessageTemplate):
    type: Literal["single"] = "single"
    content: ContentTemplate = Field(..., description="content template to use")

class IterableContentMessageTemplate(BaseMessageTemplate):
    type: Literal["iterable"] = "iterable"
    contents: List[ContentTemplateGroup] = Field(..., description="groups of templates (can be static or iterable)")
    input_key: Optional[str] = Field(
        None,
        description="The variable name containing the list to iterate over. If not specified, will iterate over the input_data list directly."
    )
    
MessageTemplate = Annotated[
    Union[
        SingleContentMessageTemplate,
        IterableContentMessageTemplate
    ],
    Field(discriminator="type")
]

class PromptTemplate(BaseModel):
    name: str = Field(
        ...,
        description="Name of the Prompt Template"
    )
    template_format: Literal["jinja2", "f-string"] = Field(
        "f-string",
        description="String format of the prompt template"
    )
    templates: List[MessageTemplate] = Field(
        ...,
        description="List of message templates",
        min_length=1
    )