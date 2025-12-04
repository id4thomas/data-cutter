from __future__ import annotations
import base64
import io
from typing import TYPE_CHECKING, Annotated, Literal, Union

import httpx
from PIL import Image

from pydantic import BaseModel, Field

from data_cutter.utils.image import ImageProcessor

class Base64ImageSourceParam(BaseModel):
    """Source parameter for base64 encoded image data"""

    data: str = Field(..., description="Base64 Data without URI prefix")

    async def load(self) -> Image.Image:
        """Load the image from base64 data"""
        data = self.data
        if data.startswith("data:"):
            # Format: data:image/png;base64,<base64_data>
            try:
                _, data = data.split(",", 1)
            except ValueError:
                raise ValueError("Invalid data URI format")

        image_bytes = base64.b64decode(data)
        return Image.open(io.BytesIO(image_bytes))


class URLImageSourceParam(BaseModel):
    """Source parameter for URL-based images"""

    url: str = Field(..., description="Image File URL")

    async def load(self) -> Image.Image:
        """Load the image from URL"""
        async with httpx.AsyncClient() as client:
            response = await client.get(self.url, follow_redirects=True)
            response.raise_for_status()
            return Image.open(io.BytesIO(response.content))

class FilePathImageSourceParam(BaseModel):
    """Source parameter for local file path images"""

    path: str = Field(..., description="Path to image file")

    async def load(self) -> Image.Image:
        if not self.path.exists():
            raise FileNotFoundError(f"Image file not found: {fpath}")
        return Image.open(self.path)

class BaseImageFile(BaseModel):
    media_type: Literal["image/jpeg", "image/jpg" ,"image/png"] = Field(
        "image/jpg", description="Image Type"
    )

    async def load(self) -> Image.Image:
        raise NotImplementedError()
    
    async def encode(self) -> "BaseImageFile":
        raise NotImplementedError()

class Base64ImageFile(BaseImageFile):
    type: Literal["base64"] = Field("base64")
    source: Base64ImageSourceParam = Field(..., description="Base64 Image Source")

    async def load(self, *args, **kwargs) -> Image.Image:
        return await self.source.load()
    
    async def encode(self, *args, **kwargs) -> "Base64ImageFile":
        return self

class URLImageFile(BaseImageFile):
    type: Literal["url"] = Field("url")
    source: URLImageSourceParam = Field(..., description="URL Image Source")

    async def load(self, *args, **kwargs) -> Image.Image:
        return await self.source.load()

    async def encode(self, *args, **kwargs) -> "Base64ImageFile":
        image = await self.load()

        # Encode the image to base64
        encoded_data = ImageProcessor.encode_image(image)

        # Create new ImageFile with base64 source
        return ImageFile(
            source=Base64ImageSourceParam(
                data=encoded_data
            ),
            media_type=self.media_type,
            type="base64"
        )
    
class FilePathImageFile(BaseImageFile):
    type: Literal["file"] = Field("file")
    source: FilePathImageSourceParam = Field(..., description="File Image Source")

    async def load(self) -> Image.Image:
        return await self.source.load()

    async def encode(self) -> "Base64ImageFile":
        image = await self.load()

        # Encode the image to base64
        encoded_data = ImageProcessor.encode_image(image)

        # Create new ImageFile with base64 source
        return ImageFile(
            source=Base64ImageSourceParam(
                data=encoded_data
            ),
            media_type=self.media_type,
            type="base64"
        )

ImageFile = Annotated[
    Union[URLImageFile, Base64ImageFile, FilePathImageFile],
    Field(discriminator="type")
]