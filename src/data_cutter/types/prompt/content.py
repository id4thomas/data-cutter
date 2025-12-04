from typing import Annotated, Iterable, Literal, Optional, Set, Union

from pydantic import BaseModel, Field

class TextContentBlock(BaseModel):
    type: Literal["text"] = "text"
    text: str = Field(..., description="")
    
class ImageUrlObject(BaseModel):
    url: str = Field(...)
    detail: Optional[str] = Field(None, )
    format: str = Field("")
    
class ImageContentBlock(BaseModel):
    type: Literal["image_url"] = "image_url"
    image_url: Union[str, ImageUrlObject] = Field(..., description="")
    

ContentBlock = Annotated[
    Union[
        TextContentBlock,
        ImageContentBlock
    ],
    Field(discriminator="type")
]

Content = Union[
    str,
    Iterable[ContentBlock],
]