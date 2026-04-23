from abc import abstractmethod
from typing import Any, Dict

from tools.base_tool import BaseTool


class BaseTransportTool(BaseTool):
    name = "transport_tool"

    @abstractmethod
    def estimate_route(
        self,
        origin: str,
        destination: str,
        mode: str = "taxi",
    ) -> Dict[str, Any]:
        """估算 origin -> destination 的距离与时间。"""
        raise NotImplementedError
