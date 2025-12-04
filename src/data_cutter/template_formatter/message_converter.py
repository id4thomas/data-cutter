"""
Message format converters for different LLM API specifications
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from data_cutter.types.prompt.content import (
    ContentBlock,
    TextContentBlock,
    ImageContentBlock,
    ImageUrlObject,
)


class MessageFormatConverter(ABC):
    """Base class for message format converters"""

    @abstractmethod
    def convert(self, content_list: List[tuple[str, List[ContentBlock]]]) -> List[Dict[str, Any]]:
        """
        Convert content blocks to specific message format

        Args:
            content_list: List of tuples (role, content_blocks)

        Returns:
            List of messages in the specific format
        """
        pass


class OpenAIMessageConverter(MessageFormatConverter):
    """
    Converter for OpenAI message format

    Format:
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "..."},
            {"type": "image_url", "image_url": {"url": "..."}}
        ]
    }
    """

    def convert(self, content_list: List[tuple[str, List[ContentBlock]]]) -> List[Dict[str, Any]]:
        """Convert to OpenAI message format"""
        messages = []

        for role, content_blocks in content_list:
            # Convert ContentBlock objects to dict format
            content_dicts = []
            for block in content_blocks:
                content_dicts.append(block.model_dump())

            messages.append({"role": role, "content": content_dicts})

        return messages


class AnthropicMessageConverter(MessageFormatConverter):
    """
    Converter for Anthropic message format

    Format:
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "..."},
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": "..."
                }
            }
        ]
    }
    """

    def convert(self, content_list: List[tuple[str, List[ContentBlock]]]) -> List[Dict[str, Any]]:
        """Convert to Anthropic message format"""
        messages = []

        for role, content_blocks in content_list:
            content_items = []

            for block in content_blocks:
                if isinstance(block, TextContentBlock):
                    content_items.append({"type": "text", "text": block.text})

                elif isinstance(block, ImageContentBlock):
                    image_url = block.image_url
                    url = image_url.url if isinstance(image_url, ImageUrlObject) else image_url

                    # Parse data URL format: data:image/png;base64,<data>
                    if url.startswith("data:"):
                        parts = url.split(",", 1)
                        if len(parts) == 2:
                            header = parts[0]  # data:image/png;base64
                            data = parts[1]

                            # Extract media type
                            media_type = "image/png"  # default
                            if ":" in header and ";" in header:
                                media_part = header.split(":")[1].split(";")[0]
                                if media_part:
                                    media_type = media_part

                            content_items.append({
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": data,
                                },
                            })
                    else:
                        # URL format (not base64)
                        content_items.append({
                            "type": "image",
                            "source": {"type": "url", "url": url},
                        })

            messages.append({"role": role, "content": content_items})

        return messages


class MessageConverterFactory:
    """Factory for creating message format converters"""

    _converters = {
        "openai": OpenAIMessageConverter,
        "anthropic": AnthropicMessageConverter,
    }

    @classmethod
    def create(cls, format_type: str) -> MessageFormatConverter:
        """
        Create a message converter for the specified format

        Args:
            format_type: Type of format ("openai", "anthropic")

        Returns:
            MessageFormatConverter instance

        Raises:
            ValueError: If format_type is not supported
        """
        format_type = format_type.lower()
        converter_class = cls._converters.get(format_type)

        if converter_class is None:
            supported = ", ".join(cls._converters.keys())
            raise ValueError(
                f"Unsupported format type: {format_type}. Supported formats: {supported}"
            )

        return converter_class()

    @classmethod
    def register(cls, format_type: str, converter_class: type[MessageFormatConverter]):
        """
        Register a custom message converter

        Args:
            format_type: Name of the format
            converter_class: MessageFormatConverter subclass
        """
        cls._converters[format_type.lower()] = converter_class

    @classmethod
    def list_supported_formats(cls) -> List[str]:
        """Get list of supported format types"""
        return list(cls._converters.keys())
