from tools.base_tool import BaseTool


class TransportTool(BaseTool):
    name = "transport_tool"

    def run(self, pace: str) -> str:
        if pace == "紧凑":
            return "跨区建议网约车+地铁组合以节省时间"
        return "市内优先地铁+步行，跨区可选择网约车"
