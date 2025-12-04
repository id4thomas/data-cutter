"""
Loader for PromptTemplate from YAML files
"""

import yaml
from pathlib import Path
from typing import Union
from data_cutter.types.prompt.template import PromptTemplate


class PromptTemplateLoader:
    """Loads PromptTemplate from YAML files"""

    @staticmethod
    def load(file_path: Union[str, Path]) -> PromptTemplate:
        """
        Load a PromptTemplate from a YAML file

        Args:
            file_path: Path to the YAML file

        Returns:
            PromptTemplate object

        Raises:
            FileNotFoundError: If the file doesn't exist
            yaml.YAMLError: If the YAML is invalid
            pydantic.ValidationError: If the YAML doesn't match PromptTemplate schema
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Template file not found: {file_path}")

        with open(file_path, "r") as f:
            data = yaml.safe_load(f)

        return PromptTemplate.model_validate(data)

    @staticmethod
    def load_from_string(yaml_content: str) -> PromptTemplate:
        """
        Load a PromptTemplate from a YAML string

        Args:
            yaml_content: YAML content as string

        Returns:
            PromptTemplate object

        Raises:
            yaml.YAMLError: If the YAML is invalid
            pydantic.ValidationError: If the YAML doesn't match PromptTemplate schema
        """
        data = yaml.safe_load(yaml_content)
        return PromptTemplate.model_validate(data)
