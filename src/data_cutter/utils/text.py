from abc import ABC, abstractmethod
from typing import Any, Dict, Type

from jinja2 import Environment, StrictUndefined


class TemplateRenderer(ABC):
    """Formatting strategy interface."""

    @classmethod
    @abstractmethod
    def render(cls, text: str, variables: Dict[str, Any]) -> str:
        ...


class FStringTemplateRenderer(TemplateRenderer):
    """Implements f-string templates"""
    
    @classmethod
    def render(cls, text: str, variables: Dict[str, Any]) -> str:
        try:
            return text.format(**variables)
        except KeyError as e:
            missing = e.args[0]
            raise ValueError(f"Missing variable '{missing}' for f-string item") from e
        except Exception as e:
            raise ValueError(f"Error formatting f-string item: {e}") from e


class JinjaTemplateRenderer(TemplateRenderer):
    """Implements Jinja2 templates"""

    @classmethod
    def render(cls, text: str, variables: Dict[str, Any]) -> str:
        try:
            with Environment(undefined=StrictUndefined, autoescape=False) as env:
                template = env.from_string(text)
            return template.render(variables)
        except Exception as e:
            raise ValueError(f"Error rendering Jinja2 item: {e}") from e


Renderers: dict[str, Type[TemplateRenderer]] = {
    "f-string": FStringTemplateRenderer,
    "jinja2": JinjaTemplateRenderer,
}