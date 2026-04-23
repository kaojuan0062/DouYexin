import time
from collections import defaultdict
from copy import deepcopy
from typing import Dict, List

from llm.openai_client import OpenAIClient
from observability.metrics import metrics_collector
from tools.tool_factory import get_search_tool
from utils.logger import get_logger, log_event


class WebResearchAgent:
    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self.search_tool = get_search_tool()
        self.llm_client = OpenAIClient(timeout=300)

    def _extract_with_fallback(self, raw_by_type: Dict[str, List[Dict[str, str]]]) -> Dict[str, List[Dict[str, str]]]:
        extracted: Dict[str, List[Dict[str, str]]] = {}
        for category in ["poi", "food", "hotel", "fallback"]:
            seen: set[str] = set()
            items: List[Dict[str, str]] = []
            for item in raw_by_type.get(category, []):
                title = str(item.get("title", "")).strip()
                url = str(item.get("url", "")).strip()
                key = f"{title}::{url}"
                if not title or key in seen:
                    continue
                seen.add(key)
                items.append(
                    {
                        "name": title,
                        "title": title,
                        "snippet": str(item.get("snippet", "")),
                        "source": str(item.get("source", "unknown")),
                        "url": url,
                        "category": category,
                    }
                )
                if len(items) >= 5:
                    break
            extracted[category] = items
        return extracted

    def _extract_all_with_llm(self, raw_by_type: Dict[str, List[Dict[str, str]]]) -> Dict[str, List[Dict[str, str]]]:
        compact_input: Dict[str, List[Dict[str, str]]] = {}
        for category, items in raw_by_type.items():
            compact_input[category] = [
                {
                    "title": str(item.get("title", ""))[:80],
                    "snippet": str(item.get("snippet", ""))[:120],
                    "source": str(item.get("source", "unknown"))[:40],
                    "url": str(item.get("url", ""))[:200],
                }
                for item in items[:4]
            ]

        prompt = f"""
你是旅游检索信息抽取助手。根据检索结果抽取候选，并按类别返回 JSON。

输入结果：{compact_input}

输出格式：
{{
  "poi": [{{"name":"","title":"","snippet":"","source":"","url":"","category":"poi"}}],
  "food": [{{"name":"","title":"","snippet":"","source":"","url":"","category":"food"}}],
  "hotel": [{{"name":"","title":"","snippet":"","source":"","url":"","category":"hotel"}}],
  "fallback": [{{"name":"","title":"","snippet":"","source":"","url":"","category":"fallback"}}]
}}

要求：
1) 去重（同名或同 URL 视为重复）
2) 每类最多 5 条
3) 仅输出 JSON
""".strip()

        try:
            parsed = self.llm_client.generate_json(prompt)
        except ValueError as exc:
            self.logger.warning(f"research_llm_parse_failed fallback_to_raw_extraction reason={exc}")
            return self._extract_with_fallback(raw_by_type)
        extracted: Dict[str, List[Dict[str, str]]] = {}
        for category in ["poi", "food", "hotel", "fallback"]:
            arr = parsed.get(category, [])
            extracted[category] = [
                {
                    "name": str(x.get("name", "")) or str(x.get("title", "")),
                    "title": str(x.get("title", "")) or str(x.get("name", "")),
                    "snippet": str(x.get("snippet", "")),
                    "source": str(x.get("source", "unknown")),
                    "url": str(x.get("url", "")),
                    "category": category,
                }
                for x in arr
                if (str(x.get("name", "")).strip() or str(x.get("title", "")).strip())
            ]
        return extracted

    def _merge_candidate_pool(self, cached_pool: Dict[str, List[Dict[str, str]]], refreshed_pool: Dict[str, List[Dict[str, str]]]) -> Dict[str, List[Dict[str, str]]]:
        merged: Dict[str, List[Dict[str, str]]] = {}
        for category in ["poi", "food", "hotel", "fallback"]:
            seen: set[str] = set()
            merged_items: List[Dict[str, str]] = []
            for item in [*cached_pool.get(category, []), *refreshed_pool.get(category, [])]:
                key = f"{item.get('name', '')}::{item.get('url', '')}"
                if key in seen:
                    continue
                seen.add(key)
                merged_items.append(item)
            merged[category] = merged_items
        return merged

    def run(self, request_id: str, queries: Dict[str, List[str]], top_k: int = 5) -> Dict[str, object]:
        start = time.perf_counter()
        raw_by_type: Dict[str, List[Dict[str, str]]] = defaultdict(list)
        fallback_used = False

        for qtype, qlist in queries.items():
            for query in qlist:
                s = time.perf_counter()
                results = self.search_tool.search(query, top_k=top_k)
                metrics_collector.record_tool(request_id=request_id, tool_name=self.search_tool.name, duration_ms=(time.perf_counter() - s) * 1000)
                mapped_category = "poi" if qtype.startswith("poi") else "food" if qtype.startswith("food") else "hotel" if qtype.startswith("hotel") else "fallback"
                for item in results:
                    item_fallback = str(item.get("fallback", "")).lower() == "true"
                    fallback_used = fallback_used or item_fallback
                    metrics_collector.record_search_fallback(request_id=request_id, triggered=item_fallback)
                    raw_by_type[mapped_category].append({"title": str(item.get("title", "")), "snippet": str(item.get("snippet", "")), "source": str(item.get("source", "unknown")), "url": str(item.get("url", ""))})

        by_type = self._extract_all_with_llm(raw_by_type)
        total = sum(len(v) for v in by_type.values())
        summary = {"total_results": total, "by_category": {k: len(v) for k, v in by_type.items()}, "fallback_used": fallback_used, "search_provider": "real_or_mock"}

        log_event(logger=self.logger, request_id=request_id, agent_name="WebResearchAgent", action="search_and_extract", duration_ms=(time.perf_counter() - start) * 1000, input_summary={"query_count": sum(len(v) for v in queries.values())}, output_summary=summary)
        return {"candidate_pool": by_type, "source_summary": summary}

    def run_with_cache(self, request_id: str, queries: Dict[str, List[str]], cache_decision: Dict[str, object], top_k: int = 5) -> Dict[str, object]:
        cached = deepcopy(cache_decision.get("cached", {}))
        strategy = str(cache_decision.get("cache_strategy", "full_refresh"))
        refreshed_queries = dict(cache_decision.get("refreshed_queries", {}))
        if strategy == "full_reuse":
            self.logger.info(f"research_memory_hit request_id={request_id} strategy=full_reuse reused_candidates={cache_decision.get('reused_candidates_count', 0)} refreshed_queries=[]")
            return {
                "candidate_pool": cached.get("candidate_pool", {}),
                "source_summary": cached.get("search_results_summary", {}),
                "research_memory_hit": True,
                "reused_candidates_count": int(cache_decision.get("reused_candidates_count", 0)),
                "refreshed_queries": refreshed_queries,
                "cache_strategy": strategy,
                "freshness_tag": cache_decision.get("freshness_tag", "stale"),
            }
        if strategy == "partial_refresh":
            refreshed = self.run(request_id=request_id, queries=refreshed_queries, top_k=top_k)
            merged_pool = self._merge_candidate_pool(cached.get("candidate_pool", {}), refreshed.get("candidate_pool", {}))
            merged_summary = deepcopy(cached.get("search_results_summary", {}))
            merged_summary["partial_refresh"] = True
            merged_summary["refreshed_queries"] = refreshed_queries
            merged_summary["reused_candidates_count"] = int(cache_decision.get("reused_candidates_count", 0))
            merged_summary["by_category"] = {k: len(v) for k, v in merged_pool.items()}
            merged_summary["total_results"] = sum(len(v) for v in merged_pool.values())
            self.logger.info(f"research_memory_hit request_id={request_id} strategy=partial_refresh reused_candidates={cache_decision.get('reused_candidates_count', 0)} refreshed_queries={refreshed_queries}")
            return {
                "candidate_pool": merged_pool,
                "source_summary": merged_summary,
                "research_memory_hit": True,
                "reused_candidates_count": int(cache_decision.get("reused_candidates_count", 0)),
                "refreshed_queries": refreshed_queries,
                "cache_strategy": strategy,
                "freshness_tag": cache_decision.get("freshness_tag", "stale"),
            }
        refreshed = self.run(request_id=request_id, queries=queries, top_k=top_k)
        self.logger.info(f"research_memory_hit request_id={request_id} strategy=full_refresh reused_candidates=0 refreshed_queries={queries}")
        return {
            **refreshed,
            "research_memory_hit": False,
            "reused_candidates_count": 0,
            "refreshed_queries": queries,
            "cache_strategy": "full_refresh",
            "freshness_tag": "fresh",
        }
