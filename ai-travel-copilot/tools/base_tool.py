from abc import ABC


class BaseTool(ABC):
    """Shared base for all tools."""

    name: str
