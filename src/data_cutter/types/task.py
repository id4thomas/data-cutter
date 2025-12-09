from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from data_cutter.types.generation_config import GenerationConfig
from data_cutter.types.prompt import PromptTemplate
from data_cutter.types.output_schema import OutputSchema, PlainOutputSchema

class Task(BaseModel):
    prompt_template: PromptTemplate = Field(
        ...,
        description="Prompt Template"
    )
    generation_config: GenerationConfig = Field(
        ...,
        description="LLM Generation config"
    )
    output_schema: OutputSchema = Field(
        default_factory=PlainOutputSchema,
        description="Generation Output Schema definition"
    )
    input_example: Optional[Dict[str, Any]] = Field(
        None,
        description="Dictionary of input_variables and example values"
    )