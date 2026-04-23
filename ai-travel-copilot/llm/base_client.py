from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseLLMClient(ABC):
    """LLM client abstract base class."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        raise NotImplementedError

    def generate_json(self, prompt: str) -> Dict[str, Any]:
        raise NotImplementedError
