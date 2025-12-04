"""
Template formatting classes for converting PromptTemplate to Content objects
"""

from typing import Any, Dict, List, Optional
from data_cutter.types.prompt.template import (
    PromptTemplate,
    ContentTemplate,
    TextTemplate,
    ImageTemplate,
    StaticContentTemplateGroup,
    IterableContentTemplateGroup,
)
from data_cutter.types.prompt.content import (
    ContentBlock,
    TextContentBlock,
    ImageContentBlock,
    ImageUrlObject,
)
from data_cutter.template_formatter.message_converter import (
    MessageFormatConverter,
    MessageConverterFactory,
)


class ContentTemplateFormatter:
    """Formats individual content templates (text or image)"""

    def format(self, content_template: ContentTemplate, variables: Dict[str, Any]) -> List[ContentBlock]:
        """
        Format a single content template with variables

        Args:
            content_template: TextTemplate or ImageTemplate
            variables: Dictionary of variable values

        Returns:
            List of ContentBlock objects
        """
        if isinstance(content_template, TextTemplate):
            return self._format_text(content_template, variables)
        elif isinstance(content_template, ImageTemplate):
            return self._format_image(content_template, variables)
        return []

    def _format_text(self, template: TextTemplate, variables: Dict[str, Any]) -> List[ContentBlock]:
        """Format a text template"""
        formatted_text = template.content.format(**variables)
        return [TextContentBlock(text=formatted_text)]

    def _format_image(self, template: ImageTemplate, variables: Dict[str, Any]) -> List[ContentBlock]:
        """Format an image template"""
        image_data = variables.get(template.input_name)
        if image_data:
            return [ImageContentBlock(image_url=ImageUrlObject(url=image_data, format=""))]
        return []


class ContentTemplateGroupFormatter:
    """Formats content template groups (static or iterable)"""

    def __init__(self):
        self.content_formatter = ContentTemplateFormatter()

    def format(
        self,
        group: StaticContentTemplateGroup | IterableContentTemplateGroup,
        variables: Dict[str, Any],
    ) -> List[ContentBlock]:
        """
        Format a content template group

        Args:
            group: StaticContentTemplateGroup or IterableContentTemplateGroup
            variables: Dictionary of variable values

        Returns:
            List of ContentBlock objects
        """
        if isinstance(group, StaticContentTemplateGroup):
            return self._format_static(group, variables)
        elif isinstance(group, IterableContentTemplateGroup):
            return self._format_iterable(group, variables)
        return []

    def _format_static(
        self, group: StaticContentTemplateGroup, variables: Dict[str, Any]
    ) -> List[ContentBlock]:
        """Format a static group - each item is formatted once"""
        results = []
        for item in group.items:
            results.extend(self.content_formatter.format(item, variables))
        return results

    def _format_iterable(
        self, group: IterableContentTemplateGroup, variables: Dict[str, Any]
    ) -> List[ContentBlock]:
        """Format an iterable group - items are formatted N times"""
        # Find the iteration source (list or list variable)
        iteration_source = self._find_iteration_source(group, variables)

        if not iteration_source:
            return []

        # Iterate and format
        results = []
        for item_vars in iteration_source:
            # Merge with parent variables
            merged_vars = {**variables, **item_vars}

            for item in group.items:
                # Handle nested iterable groups
                if isinstance(item, IterableContentTemplateGroup):
                    results.extend(self.format(item, merged_vars))
                else:
                    results.extend(self.content_formatter.format(item, merged_vars))

        return results

    def _find_iteration_source(
        self, group: IterableContentTemplateGroup, variables: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Find the iteration source for the group.

        Returns a list of dictionaries where each dict contains variables for one iteration.
        Supports both parallel lists and list of dicts.
        """
        # Strategy 0: If input_key is specified, use it directly
        if group.input_key:
            if group.input_key in variables and isinstance(variables[group.input_key], list):
                iteration_list = variables[group.input_key]
                if iteration_list and isinstance(iteration_list[0], dict):
                    # List of dicts - return directly
                    return iteration_list
                else:
                    # Scalar list - wrap each item in a dict with the key
                    return [{group.input_key: item} for item in iteration_list]
            return []

        # Collect all input variables from the group
        all_vars = set()
        for item in group.items:
            if isinstance(item, TextTemplate):
                all_vars.update(item.input_variables)
            elif isinstance(item, ImageTemplate):
                all_vars.add(item.input_name)

        if not all_vars:
            return []

        # Strategy 1: Find list variables that match the template variables
        list_vars = {}
        for var_name in all_vars:
            if var_name in variables and isinstance(variables[var_name], list):
                list_vars[var_name] = variables[var_name]

        # Strategy 2: If no matching list vars found, look for ANY list in variables
        # This handles cases where data is nested (e.g., "pages" contains page_no and page_image)
        if not list_vars:
            for _key, value in variables.items():
                if isinstance(value, list) and len(value) > 0:
                    # Check if list items are dicts that contain our variables
                    if isinstance(value[0], dict):
                        # Check if at least one of our variables exists in the dict
                        if any(var in value[0] for var in all_vars):
                            return value
            return []

        # Get length from first list
        list_length = len(next(iter(list_vars.values())))

        # Check if we're iterating over a list of dictionaries
        first_list_name = next(iter(list_vars.keys()))
        first_list = list_vars[first_list_name]

        if first_list and isinstance(first_list[0], dict):
            # List of dicts - each dict contains all the variables for that iteration
            return first_list
        else:
            # Parallel lists - create dicts by zipping the lists together
            result = []
            for i in range(list_length):
                iter_vars = {}
                for var_name in all_vars:
                    if var_name in variables:
                        if isinstance(variables[var_name], list):
                            iter_vars[var_name] = variables[var_name][i]
                        else:
                            iter_vars[var_name] = variables[var_name]
                result.append(iter_vars)
            return result


class PromptTemplateFormatter:
    """Formats complete PromptTemplate into Content objects and messages"""

    def __init__(self, message_format: str = "openai"):
        """
        Initialize the formatter

        Args:
            message_format: Format specification for messages ("openai", "anthropic", etc.)
        """
        self.group_formatter = ContentTemplateGroupFormatter()
        self.content_formatter = ContentTemplateFormatter()
        self.message_format = message_format
        self._converter: Optional[MessageFormatConverter] = None

    @property
    def converter(self) -> MessageFormatConverter:
        """Lazy load the message converter"""
        if self._converter is None:
            self._converter = MessageConverterFactory.create(self.message_format)
        return self._converter

    def format(
        self, template: PromptTemplate, input_data: Dict[str, Any]
    ) -> List[tuple[str, List[ContentBlock]]]:
        """
        Convert a PromptTemplate to Content objects

        Args:
            template: The PromptTemplate to format
            input_data: Dictionary containing all input data

        Returns:
            List of tuples (role, content_blocks)
        """
        result = []

        for message_template in template.templates:
            role = message_template.role

            if message_template.type == "single":
                # Single content message
                content_blocks = self.content_formatter.format(
                    message_template.content, input_data
                )
                result.append((role, content_blocks))

            elif message_template.type == "iterable":
                # Iterable content message
                all_content_blocks = []

                # Determine what to iterate over
                if message_template.input_key:
                    # If input_key is specified, iterate over that variable
                    if message_template.input_key in input_data:
                        iteration_data = input_data[message_template.input_key]
                        if not isinstance(iteration_data, list):
                            iteration_data = [iteration_data]
                    else:
                        iteration_data = []
                else:
                    # No input_key specified - cannot iterate
                    iteration_data = []

                for document_data in iteration_data:
                    # Process each content group
                    for content_group in message_template.contents:
                        content_blocks = self.group_formatter.format(content_group, document_data)
                        all_content_blocks.extend(content_blocks)

                result.append((role, all_content_blocks))

        return result

    def format_to_messages(
        self,
        template: PromptTemplate,
        input_data: Dict[str, Any],
        message_format: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Convert a PromptTemplate directly to LLM message format

        Args:
            template: The PromptTemplate to format
            input_data: Dictionary containing all input data
            message_format: Override the default message format for this call

        Returns:
            List of messages in the specified format
        """
        content_list = self.format(template, input_data)
        return self.content_to_messages(content_list, message_format=message_format)

    def content_to_messages(
        self,
        content_list: List[tuple[str, List[ContentBlock]]],
        message_format: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Convert Content objects to LLM message format

        Args:
            content_list: List of tuples (role, content_blocks)
            message_format: Override the default message format for this call

        Returns:
            List of messages in the specified format
        """
        if message_format:
            converter = MessageConverterFactory.create(message_format)
        else:
            converter = self.converter

        return converter.convert(content_list)
