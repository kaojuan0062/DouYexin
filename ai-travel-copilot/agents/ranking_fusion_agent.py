import time
from typing import Dict, List

from llm.openai_client import OpenAIClient
from schemas.request import NormalizedRequirement
from utils.logger import get_logger, log_event


class RankingFusionAgent:
    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self.llm_client = OpenAIClient()

    def _fallback_fusion(self, candidate_pool: Dict[str, List[Dict[str, str]]]) -> Dict[str, object]:
        recommended: Dict[str, List[Dict[str, object]]] = {}
        category_counts: Dict[str, int] = {}

        for category in ["poi", "food", "hotel", "fallback"]:
            seen: set[str] = set()
            fused_items: List[Dict[str, object]] = []
            for item in candidate_pool.get(category, []):
                name = str(item.get("name") or item.get("title") or "").strip()
                url = str(item.get("url", "")).strip()
                key = f"{name}::{url}"
                if not name or key in seen:
                    continue
                seen.add(key)
                fused_items.append(
                    {
                        "name": name,
                        "title": str(item.get("title") or name),
                        "snippet": str(item.get("snippet", "")),
                        "source": str(item.get("source", "unknown")),
                        "url": url,
                        "category": category,
                        "source_count": 1,
                        "score": max(1.0, 10.0 - len(fused_items)),
                    }
                )
                if len(fused_items) >= 5:
                    break
            recommended[category] = fused_items
            category_counts[category] = len(fused_items)

        reasons = [
            "已使用候选池结果完成基础去重与排序。",
            "当前排序结果基于本地兜底逻辑生成。",
        ]
        summary = {
            "deduped": True,
            "fallback_used": True,
            "category_counts": category_counts,
            "total_candidates": sum(category_counts.values()),
        }
        return {
            "recommended_candidates": recommended,
            "recommendation_reasons": reasons,
            "candidate_pool_summary": summary,
        }

    def run(self, request_id: str, requirement: NormalizedRequirement, candidate_pool: Dict[str, List[Dict[str, str]]]) -> Dict[str, object]:
        start = time.perf_counter()
        prompt = f"""
你是旅游推荐融合排序助手。请基于候选池和用户需求完成多来源融合排序，输出 JSON。

需求：{requirement.model_dump_json()}
候选池：{candidate_pool}

打分考虑：
- source_count_weight
- preference_match_weight
- budget_fit_weight
- weather_fit_weight
- transport_fit_weight

输出字段：
- recommended_candidates: {{"poi":[], "food":[], "hotel":[], "fallback":[]}}
  每个候选包含 name,title,snippet,source,url,category,source_count,score
- recommendation_reasons: string[]
- candidate_pool_summary: object

要求：
1) 对同名候选做去重并统计 source_count
2) 若多来源重复提到，在 recommendation_reasons 中明确“多来源推荐”
""".strip()

        try:
            parsed = self.llm_client.generate_json(prompt)
            recommended = {
                k: [dict(x) for x in v]
                for k, v in dict(parsed.get("recommended_candidates", {})).items()
            }
            reasons = [str(x) for x in parsed.get("recommendation_reasons", [])]
            summary = dict(parsed.get("candidate_pool_summary", {}))
        except ValueError as exc:
            self.logger.warning(f"ranking_fusion_llm_parse_failed fallback_to_candidate_pool reason={exc}")
            fallback = self._fallback_fusion(candidate_pool)
            recommended = fallback["recommended_candidates"]
            reasons = fallback["recommendation_reasons"]
            summary = fallback["candidate_pool_summary"]

        log_event(
            logger=self.logger,
            request_id=request_id,
            agent_name="RankingFusionAgent",
            action="fuse_and_rank",
            duration_ms=(time.perf_counter() - start) * 1000,
            input_summary={"pool_categories": list(candidate_pool.keys())},
            output_summary={
                "category_counts": {k: len(v) for k, v in recommended.items()},
                "reasons": len(reasons),
            },
        )

        return {
            "recommended_candidates": recommended,
            "recommendation_reasons": reasons,
            "candidate_pool_summary": summary,
        }
