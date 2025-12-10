from typing import Any, Dict, List, Union

from data_cutter.types.prompt.template import (
    TextTemplate,
    ImageTemplate,
    IterableTemplate,
    PromptTemplate
)
from .base import BasePromptFormatter, format_string

class OpenAIPromptFormatter(BasePromptFormatter):
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
        return [{"type": "text", "text": formatted_text}]
    
    @classmethod
    def _process_image_template(
        cls, 
        item: ImageTemplate, 
        variables: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Process ImageTemplate and return image content"""
        image_url = variables.get(item.input_name, "")
        return [{"type": "image_url", "image_url": {"url": image_url}}]