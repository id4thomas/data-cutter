from pydantic import BaseModel, Field

class ModelParams(BaseModel):
    name: str = Field(
        ...,
        description="Name of the Parameter combination"
    )
    provider: str = Field(
        ...,
        description="The provider of the model. Supported providers are 'openai' and 'anthropic'.",
        examples=["openai", "anthropic", "hosted_vllm"],
    )
    model_name: str = Field(
        ...,
        description="The name of the model to use for the prompt content.",
        examples=["gpt-4o"],
    )
    parameters: dict = Field(
        default_factory=dict,
        description="The parameters of the model to use for the prompt content.",
        examples=[{"temperature": 1, "top_p": 1, "frequency_penalty": 0, "presence_penalty": 0}],
    )