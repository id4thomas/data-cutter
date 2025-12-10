from typing import Any, Dict, List, Union

from data_cutter.types.prompt.template import (
    TextTemplate,
    ImageTemplate,
    IterableTemplate,
    PromptTemplate
)
from .base import BasePromptFormatter, format_string

class AnthropicPromptFormatter(BasePromptFormatter):
    @classmethod
    def _process_text_template(
        cls,
        item: TextTemplate,
        variables: Dict[str, Any],
        template_format: str = "f-string"
    ) -> List[Dict[str, Any]]:
        """Process TextTemplate and return formatted text content"""
        # Filter variables to only include those defined in input_variables
        if item.input_variables:
            filtered_vars = {k: variables[k] for k in item.input_variables if k in variables}
        else:
            filtered_vars = {}

        formatted_text = format_string(item.value, filtered_vars, template_format)
        return [
            {
                "type": "text",
                "text": formatted_text
            }
        ]
    
    @classmethod
    def _process_image_template(
        cls,
        item: ImageTemplate,
        variables: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Process ImageTemplate and return image content"""
        image_url = variables.get(item.input_name, "")

        # Check if it's a base64 data URL
        if image_url.startswith("data:"):
            # Parse data URL format: data:image/png;base64,<base64_data>
            try:
                # Extract media type and base64 data
                header, base64_data = image_url.split(",", 1)
                media_type_part = header.split(":")[1].split(";")[0]

                # Validate media type
                valid_media_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
                if media_type_part not in valid_media_types:
                    raise ValueError(f"Unsupported media type: {media_type_part}")

                return [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type_part,
                            "data": base64_data
                        }
                    }
                ]
            except (ValueError, IndexError) as e:
                raise ValueError(f"Invalid base64 data URL format: {e}")
        else:
            # Regular URL
            return [
                {
                    "type": "image",
                    "source": {
                        "type": "url",
                        "url": image_url
                    }
                }
            ]