import json
from pathlib import Path
from typing import Optional, Type, Union

import yaml
from pydantic import BaseModel

from data_cutter.types.schema import SchemaConfig
from data_cutter.schema_maker import SchemaModelMaker


class SchemaLoader:
    @classmethod
    def _make_model(cls, config: SchemaConfig) -> Type[BaseModel]:
        """Create a Pydantic model from SchemaConfig."""
        maker = SchemaModelMaker()
        return maker.make(config)

    @classmethod
    def from_dict(cls, schema_dict: dict) -> Type[BaseModel]:
        """
        Create a Pydantic model from a dictionary.

        Args:
            schema_dict: Dictionary containing schema configuration

        Returns:
            Pydantic BaseModel type created from the schema
        """
        config = SchemaConfig.model_validate(schema_dict)
        return cls._make_model(config)

    @classmethod
    def from_json(
        cls,
        fpath: Union[str, Path],
        encoding: Optional[str] = "utf-8"
    ) -> Type[BaseModel]:
        """
        Create a Pydantic model from a JSON file.

        Args:
            fpath: Path to JSON file containing schema configuration
            encoding: File encoding (default: utf-8)

        Returns:
            Pydantic BaseModel type created from the schema
        """
        with open(fpath, 'r', encoding=encoding) as f:
            schema_dict = json.load(f)
        return cls.from_dict(schema_dict)

    @classmethod
    def from_yaml(
        cls,
        fpath: Union[str, Path],
        encoding: Optional[str] = "utf-8"
    ) -> Type[BaseModel]:
        """
        Create a Pydantic model from a YAML file.

        Args:
            fpath: Path to YAML file containing schema configuration
            encoding: File encoding (default: utf-8)

        Returns:
            Pydantic BaseModel type created from the schema
        """
        with open(fpath, 'r', encoding=encoding) as f:
            schema_dict = yaml.safe_load(f)
        return cls.from_dict(schema_dict)