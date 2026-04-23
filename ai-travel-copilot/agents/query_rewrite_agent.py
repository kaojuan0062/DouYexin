import time
from typing import Dict, List

from config.settings import settings
from context.models import AgentContext
from llm.langchain_client import LangChainChatModel
from llm.openai_client import OpenAIClient
from schemas.request import NormalizedRequirement
from utils.logger import get_logger, log_event


class QueryRewriteAgent:
    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self.llm_client = OpenAIClient()
        self.langchain_llm = LangChainChatModel()

    def _use_langchain_llm(self) -> bool:
        return settings.LANGCHAIN_LLM_MODE in {"query_rewrite", "all"}

    def run(self, requirement: NormalizedRequirement, request_id: str, agent_context: AgentContext | None = None) -> Dict[str, List[str]]:
        start = time.perf_counter()
        research_hint = agent_context.optional_research_cache if agent_context else {}
        prompt = f"""
你是检索查询重写助手。基于结构化旅行需求生成查询词，返回 JSON。

需求：{requirement.model_dump_json()}
Research Memory 摘要：{research_hint}

输出字段：
- poi_queries: string[]
- food_queries: string[]
- hotel_queries: string[]
- fallback_queries: string[]

每类至少 2 条，适合联网搜索，简短精确。
""".strip()

        parsed = self.langchain_llm.invoke_json(prompt, system_prompt="你是一个检索查询重写助手。请严格输出 JSON。") if self._use_langchain_llm() else self.llm_client.generate_json(prompt)
        queries: Dict[str, List[str]] = {
            "poi_queries": [str(x) for x in parsed.get("poi_queries", [])],
            "food_queries": [str(x) for x in parsed.get("food_queries", [])],
            "hotel_queries": [str(x) for x in parsed.get("hotel_queries", [])],
            "fallback_queries": [str(x) for x in parsed.get("fallback_queries", [])],
        }

        log_event(logger=self.logger, request_id=request_id, agent_name="QueryRewriteAgent", action="rewrite_queries", duration_ms=(time.perf_counter() - start) * 1000, input_summary={"destination": requirement.destination, "days": requirement.days, "context_sections": agent_context.visible_sections if agent_context else [], "langchain_mode": self._use_langchain_llm()}, output_summary={"query_groups": {k: len(v) for k, v in queries.items()}})
        return queries
