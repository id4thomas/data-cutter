import json
import os
from typing import Any, Dict, Optional
import yaml

from data_cutter.types.generation_config import GenerationConfig
from data_cutter.types.prompt_template import PromptTemplate
from data_cutter.types.output_schema import (
    OutputSchema,
    PlainOutputSchema,
    StructuredOutputSchema
)
from data_cutter.types.task import Task

# Task consists of following files
# CONFIG_FILE="config.json" # TODO
PROMPT_TEMPLATE_FILE="prompt_template.yaml"
GENERATION_CONFIG_FILE="generation_config.json"
OUTPUT_SCHEMA_FILE="output_schema.json"

INPUT_EXAMPLE_FILE="input_example.json"


class TaskLoader:
    @classmethod
    def load_generation_config(
        cls,
        file_path: str,
        encoding: str = 'utf-8'
    ) -> GenerationConfig:
        if not os.path.exists(file_path):
            raise ValueError(
                f"Generation Config ({GENERATION_CONFIG_FILE}) file not found"
            )
        with open(file_path, "r", encoding=encoding) as f:
            data = json.load(f)
        return GenerationConfig.model_validate(data)
    
    @classmethod
    def load_input_example(
        cls,
        file_path: str,
        encoding: str = 'utf-8'
    ) -> Optional[Dict[str, Any]]:
        if not os.path.exists(file_path):
            return None
        with open(file_path, "r", encoding=encoding) as f:
            data = json.load(f)
        return data
    
    @classmethod
    def load_output_schema(
        cls,
        file_path: str,
        encoding: str = 'utf-8'
    ) -> OutputSchema:
        if not os.path.exists(file_path):
            raise ValueError(
                f"Output Schema ({OUTPUT_SCHEMA_FILE}) file not found"
            )
        with open(file_path, "r", encoding=encoding) as f:
            data = json.load(f)
        if data["type"]=="plain":
            return PlainOutputSchema.model_validate(data)
        elif data["type"]=="structured":
            return StructuredOutputSchema.model_validate(data)
        else:
            raise ValueError(f"OutputSchema type {data["type"]} not recognized")
    
    @classmethod
    def load_prompt_template(
        cls,
        file_path: str,
        encoding: str = 'utf-8'
    ) -> PromptTemplate:
        if not os.path.exists(file_path):
            raise ValueError(
                f"Prompt Template ({PROMPT_TEMPLATE_FILE}) file not found"
            )
        with open(file_path, "r", encoding=encoding) as f:
            data = yaml.safe_load(f)
        return PromptTemplate.model_validate(data)
            
    
    @classmethod
    def load(
        cls,
        path: str,
    )-> Task:
        if not os.path.isdir(path):
            raise ValueError(f"Path {path} isn't valid")
        
        # PromptTemplate
        prompt_template = cls.load_prompt_template(
            os.path.join(path, PROMPT_TEMPLATE_FILE)
        )
        
        # OutputSchema
        output_schema = cls.load_output_schema(
            os.path.join(path, OUTPUT_SCHEMA_FILE)
        )
        
        # GenerationConfig
        generation_config = cls.load_generation_config(
            os.path.join(path, GENERATION_CONFIG_FILE)
        )
        
        # Input Example
        input_example = cls.load_input_example(
            os.path.join(path, INPUT_EXAMPLE_FILE)
        )
        
        task = Task(
            prompt_template = prompt_template,
            generation_config = generation_config,
            output_schema = output_schema,
            input_example = input_example
        )
        return task
