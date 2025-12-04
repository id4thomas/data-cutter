"""Image processing utilities for VLM extraction"""

from __future__ import annotations

import base64
import io
from os import PathLike
from pathlib import Path
from typing import TYPE_CHECKING, List, Literal, Union

import httpx
from PIL import Image

from data_cutter.types.image.bbox import BBox


class ImageLoader:
    """Utility class for image file loading"""

    @classmethod
    async def load_from_url(cls, url: str) -> Image.Image:
        """
        Load image from URL

        Args:
            url: Image URL

        Returns:
            PIL Image object

        Raises:
            ValueError: If URL is empty or invalid
            httpx.HTTPError: If request fails
        """
        if not url:
            raise ValueError("URL cannot be empty")

        async with httpx.AsyncClient() as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            return Image.open(io.BytesIO(response.content))

    @classmethod
    def load_from_fpath(cls, fpath: Union[str, PathLike]) -> Image.Image:
        """
        Load image from file path

        Args:
            fpath: Path to image file

        Returns:
            PIL Image object

        Raises:
            ValueError: If path is empty or file doesn't exist
            FileNotFoundError: If file doesn't exist
        """
        if not fpath:
            raise ValueError("File path cannot be empty")

        path = Path(fpath)
        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {fpath}")

        return Image.open(path)

    @classmethod
    def load_from_base64(cls, data: str) -> Image.Image:
        """
        Load image from base64 encoded string

        Args:
            data: Base64 encoded image data (with or without data URI prefix)
        Returns:
            PIL Image object

        Raises:
            ValueError: If data is empty or invalid
        """
        if not data:
            raise ValueError("Base64 data cannot be empty")

        # Remove data URI prefix if present
        if data.startswith("data:"):
            # Format: data:image/png;base64,<base64_data>
            try:
                _, data = data.split(",", 1)
            except ValueError:
                raise ValueError("Invalid data URI format")

        image_bytes = base64.b64decode(data)
        return Image.open(io.BytesIO(image_bytes))

    @classmethod
    async def load_from_storage(cls, key: str, storage_client: StorageClient) -> Image.Image:
        """
        Load image from storage using StorageClient

        Args:
            key: Storage key/path to the image file
            storage_client: StorageClient instance to use for fetching

        Returns:
            PIL Image object

        Raises:
            ValueError: If key is empty
        """
        if not key:
            raise ValueError("Storage key cannot be empty")

        image_bytes = await storage_client.get_file(key)
        return Image.open(io.BytesIO(image_bytes)) 


class ImageProcessor:
    """Utility class for image processing and encoding"""
    @classmethod
    def encode_image_file(cls, fpath: str) -> str:
        """
        Encode image file to base64 string (without data URI prefix)

        Args:
            image_path: Path to image file

        Returns:
            Base64 encoded string
        """
        with open(fpath, "rb") as f:
            encoded_image = base64.b64encode(f.read()).decode("utf-8")
        return encoded_image

    @staticmethod
    def encode_image(image: Image.Image, format: str = "PNG") -> str:
        """
        Convert PIL Image to base64 data

        Args:
            pil_image: PIL Image object
            format: Image format (PNG, JPEG, etc.)

        Returns:
            str: base64 encoded image
        """
        buffered = io.BytesIO()

        # Handle RGBA to RGB conversion for formats like JPEG
        if format == "JPEG" and image.mode == "RGBA":
            image = image.convert("RGB")

        image.save(buffered, format=format)
        buffered.seek(0)
        img_bytes = buffered.getvalue()
        encoded_image = base64.b64encode(img_bytes).decode("utf-8")
        return encoded_image

    @classmethod
    def crop_image(cls, image: Image.Image, bbox: BBox) -> Image.Image:
        """
        Crop image using bounding box

        Args:
            image: PIL Image object
            bbox: BBox object with pixel coordinates

        Returns:
            Cropped PIL Image
        """
        # Ensure correct ordering
        bbox = bbox.validate_ordering()
        return image.crop(bbox.to_tuple())