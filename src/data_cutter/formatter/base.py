from typing import Any, Dict, List, Union

from data_cutter.types.prompt.template import (
    TextTemplate,
    ImageTemplate,
    IterableTemplate,
    PromptTemplate
)

def format_string(value: str, variables: Dict[str, Any], template_format: str = "f-string") -> str:
    """Format string based on template_format (f-string or jinja2)"""
    if template_format == "f-string":
        # Only format with available variables to avoid KeyError
        return value.format(**variables)
    elif template_format == "jinja2":
        from jinja2 import Template
        jinja_template = Template(value)
        return jinja_template.render(**variables)
    return value

class BasePromptFormatter:
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
    
    @classmethod
    def _process_iterable_template(
        cls,
        item: IterableTemplate,
        variables: Dict[str, Any],
        template_format: str = "f-string"
    ) -> List[Dict[str, Any]]:
        """Process IterableTemplate by iterating over the specified variable"""
        results = []
        iterable_data = variables.get(item.input_variable, [])

        if not isinstance(iterable_data, (list, tuple)):
            raise ValueError(
                f"Variable '{item.input_variable}' must be a list, "
                f"got {type(iterable_data).__name__}"
            )

        for item_data in iterable_data:
            # Merge parent variables with current iteration item variables
            if isinstance(item_data, dict):
                merged_vars = {**variables, **item_data}
            else:
                merged_vars = {**variables, item.input_variable: item_data}

            # Process each sub-item in the iterable
            for sub_item in item.items:
                results.extend(cls._process_template_item(sub_item, merged_vars, template_format))

        return results
    
    @classmethod
    def _process_template_item(
        cls,
        item: Union[TextTemplate, ImageTemplate, IterableTemplate],
        variables: Dict[str, Any],
        template_format: str = "f-string"
    ) -> List[Dict[str, Any]]:
        """Route to appropriate processor based on item type"""
        if isinstance(item, TextTemplate):
            return cls._process_text_template(item, variables, template_format)
        elif isinstance(item, ImageTemplate):
            return cls._process_image_template(item, variables)
        elif isinstance(item, IterableTemplate):
            return cls._process_iterable_template(item, variables, template_format)
        else:
            raise ValueError(f"Unknown template item type: {type(item)}")
    
    @classmethod
    def format(
        cls,
        template: PromptTemplate,
        variables: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Format the prompt template with provided variables.

        Args:
            template: The prompt template to format
            variables: Dictionary containing all variables needed for formatting

        Returns:
            List of formatted messages ready for API consumption
        """
        messages = []

        for message_template in template.messages:
            content = []

            for item in message_template.contents:
                content.extend(cls._process_template_item(item, variables, template.template_format))

            messages.append({
                "role": message_template.role,
                "content": content
            })

        return messages