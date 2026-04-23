from __future__ import annotations

import json
import time
from typing import Any, Dict, List

from llm.langchain_client import LangChainChatModel
from tools.langchain_tools import search_tool
from utils.logger import get_logger, log_event


class ReactAgent:
    """Minimal ReAct-style agent for research-stage tool calling."""

    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self.llm = LangChainChatModel()

    def _thought(self, query: str, category: str) -> str:
        prompt = (
            "你是一个 ReAct 风格旅行研究助手。"
            "请基于给定检索任务，输出一句简短 Thought，说明下一步要查什么。"
            f"\ncategory={category}\nquery={query}"
        )
        return self.llm.invoke_text(prompt, system_prompt="你是一个遵循 Thought -> Action -> Observation 的研究助手。")

    def _normalize_results(self, observation: str, category: str) -> List[Dict[str, str]]:
        parsed = json.loads(observation)
        items: List[Dict[str, str]] = []
        for item in parsed[:5]:
            title = str(item.get("title", "")).strip()
            if not title:
                continue
            items.append(
                {
                    "name": title,
                    "title": title,
                    "snippet": str(item.get("snippet", "")),
                    "source": str(item.get("source", "unknown")),
                    "url": str(item.get("url", "")),
                    "category": category,
                }
            )
        return items

    def run(self, request_id: str, queries: Dict[str, List[str]]) -> Dict[str, Any]:
        start = time.perf_counter()
        candidate_pool: Dict[str, List[Dict[str, str]]] = {"poi": [], "food": [], "hotel": [], "fallback": []}
        trace: List[Dict[str, str]] = []

        for qtype, qlist in queries.items():
            category = "poi" if qtype.startswith("poi") else "food" if qtype.startswith("food") else "hotel" if qtype.startswith("hotel") else "fallback"
            for query in qlist[:2]:
                thought = self._thought(query=query, category=category)
                self.logger.info(f"[ReAct][Thought] {thought}")

                action = f"search_tool({query})"
                self.logger.info(f"[ReAct][Action] {action}")

                observation = search_tool.invoke(query)
                self.logger.info(f"[ReAct][Observation] {observation}")

                trace.append({"thought": thought, "action": action, "observation": observation})
                candidate_pool[category].extend(self._normalize_results(observation=observation, category=category))

        summary = {
            "total_results": sum(len(v) for v in candidate_pool.values()),
            "by_category": {k: len(v) for k, v in candidate_pool.items()},
            "react_trace_steps": len(trace),
            "mode": "react",
        }
        log_event(
            logger=self.logger,
            request_id=request_id,
            agent_name="ReactAgent",
            action="react_research",
            duration_ms=(time.perf_counter() - start) * 1000,
            input_summary={"query_count": sum(len(v) for v in queries.values())},
            output_summary=summary,
        )
        return {
            "candidate_pool": candidate_pool,
            "source_summary": summary,
            "react_trace": trace,
            "research_memory_hit": False,
            "reused_candidates_count": 0,
            "refreshed_queries": queries,
            "cache_strategy": "full_refresh",
            "freshness_tag": "fresh",
        }
