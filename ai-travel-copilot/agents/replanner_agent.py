import time
from copy import deepcopy
from datetime import date, timedelta
from typing import Dict, List

from context.context_builder import context_builder
from memory.memory_service import memory_service
from observability.metrics import metrics_collector
from schemas.itinerary import ItineraryResponse
from schemas.request import ReplanRequest
from tools.tool_factory import get_weather_tool
from utils.logger import get_logger, log_event


class ReplannerAgent:
    """局部重规划：仅修改受影响天，保留其他天不变。"""

    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self.weather_tool = get_weather_tool()

    def _target_days(self, request: ReplanRequest, total_days: int, summary_locked_days: List[int]) -> List[int]:
        requested = request.affected_days or ([request.day] if 1 <= request.day <= total_days else [])
        locked = set(summary_locked_days + request.locked_days)
        return sorted({d for d in requested if 1 <= d <= total_days and d not in locked})

    def run(self, request: ReplanRequest, request_id: str) -> ItineraryResponse:
        start = time.perf_counter()
        agent_context = context_builder.build_replanner_context(session_id=request.session_id, replan_request=request)
        summary_memory = agent_context.recent_summary
        research_memory = agent_context.optional_research_cache
        self.logger.info(f"replan_context_ready session_id={request.session_id} visible_sections={agent_context.visible_sections}")
        memory_service.save_replan_request(session_id=request.session_id, user_id=request.user_id, replan_request=request.model_dump())

        source_plan = request.current_plan or agent_context.memory_context.get("session", {}).get("current_itinerary", {})
        plan_dict = deepcopy(source_plan)
        before_daily = deepcopy(plan_dict.get("daily_plan", []))
        daily_plan = [dict(day_item) for day_item in plan_dict.get("daily_plan", [])]

        summary_locked_days = [int(x) for x in summary_memory.get("locked_days", [])]
        target_days = self._target_days(request, len(daily_plan), summary_locked_days)
        preserved_constraints = {"locked_days": sorted(set(summary_locked_days + request.locked_days)), "keep_hotel": bool(request.keep_hotel), "keep_budget": bool(request.keep_budget), "keep_confirmed_segments": bool(request.keep_confirmed_segments), "confirmed_constraints": summary_memory.get("confirmed_constraints", {})}

        research_decision = memory_service.evaluate_research_reuse(session_id=request.session_id, user_id=request.user_id, requirement=request.original_request.model_dump(), rewritten_queries=research_memory.get("rewritten_queries", {}), replan_reason=request.reason)

        changed_segments: List[Dict] = []
        unchanged_segments: List[Dict] = []
        for day_idx in range(1, len(daily_plan) + 1):
            target = daily_plan[day_idx - 1]
            if day_idx not in target_days:
                unchanged_segments.append({"day": day_idx, "status": "kept", "reason": "locked_or_not_affected"})
                continue
            if request.reason.lower() == "rain":
                target_date = (date.today() + timedelta(days=day_idx - 1)).isoformat()
                w_start = time.perf_counter()
                weather_info = self.weather_tool.get_weather(city=request.original_request.destination, date=f"{target_date}-rain")
                metrics_collector.record_tool(request_id=request_id, tool_name=self.weather_tool.name, duration_ms=(time.perf_counter() - w_start) * 1000)
                metrics_collector.record_weather_fallback(request_id=request_id, triggered=bool(weather_info.get("fallback", False)))
                target["weather"] = f"{weather_info.get('condition', 'unknown')} {weather_info.get('temperature_min', '-') }~{weather_info.get('temperature_max', '-') }℃"
                target["activities"] = ["上午：室内博物馆/展览", "中午：商场或室内美食街用餐", "下午：室内体验活动（手作/展馆）", "晚上：根据天气灵活安排"]
            if request.reason.lower() == "poi_closed" and request.closed_poi:
                target["activities"] = [x.replace(request.closed_poi, "城市替代景点") for x in target["activities"]]
            if request.reason.lower() == "reduce_budget" and request.new_budget and not request.keep_budget:
                target["activities"][-1] = "晚上：免费城市步行路线与夜景打卡"
                plan_dict["estimated_budget"]["total"] = float(request.new_budget)
                plan_dict["estimated_budget"]["daily_average"] = round(float(request.new_budget) / request.original_request.days, 2)
            if request.food_focus:
                target["activities"][1] = "中午：老字号 + 夜市双段美食路线"
            daily_plan[day_idx - 1] = target
            changed_segments.append({"day": day_idx, "reason": request.reason, "reused_summary": bool(summary_memory), "research_memory_hit": research_decision["hit"]})

        plan_dict["daily_plan"] = daily_plan
        notes = plan_dict.get("notes", [])
        notes.append(f"局部重规划：affected_days={target_days}，原因={request.reason}。")
        notes.append(f"Replanner Context sections={agent_context.visible_sections}。")
        if request.keep_budget or summary_memory.get("confirmed_constraints", {}).get("budget_locked"):
            notes.append("已保留预算约束并优先局部调整。")
        if request.keep_hotel or summary_memory.get("confirmed_constraints", {}).get("hotel_locked"):
            notes.append("已保留原酒店方案，不改动住宿推荐。")
        if request.keep_confirmed_segments:
            notes.append("已复用 summary memory 中的已确认片段与锁定日期。")
        if research_decision["hit"]:
            notes.append(f"Research Memory 复用成功：strategy={research_decision['cache_strategy']}，候选复用={research_decision['reused_candidates_count']}。")
        plan_dict["notes"] = notes

        replanning_diff = {"affected_days": target_days, "changed_segments": changed_segments, "unchanged_segments": unchanged_segments, "before": [x for x in before_daily if x.get("day") in target_days], "after": [x for x in daily_plan if x.get("day") in target_days]}
        duration_ms = (time.perf_counter() - start) * 1000
        metrics_collector.record_agent(request_id, "ReplannerAgent", duration_ms)
        metrics_collector.record_replan_duration(request_id, duration_ms)
        log_event(logger=self.logger, request_id=request_id, agent_name="ReplannerAgent", action="partial_replan", duration_ms=duration_ms, input_summary={"affected_days": target_days, "reason": request.reason, "context_sections": agent_context.visible_sections}, output_summary={"changed_count": len(changed_segments), "unchanged_count": len(unchanged_segments), "research_memory_hit": research_decision["hit"], "cache_strategy": research_decision["cache_strategy"]})

        result = ItineraryResponse(**plan_dict)
        result.replanning_diff = replanning_diff
        result.reused_memory_summary = summary_memory
        result.preserved_constraints = preserved_constraints
        result.research_memory_hit = bool(research_decision["hit"])
        result.reused_candidates_count = int(research_decision["reused_candidates_count"])
        result.refreshed_queries = research_decision["refreshed_queries"]
        result.cache_strategy = str(research_decision["cache_strategy"])
        result.meta = {**result.meta, "request_id": request_id, "session_id": request.session_id}

        memory_service.save_itinerary(session_id=request.session_id, user_id=request.user_id, itinerary=result.model_dump())
        summary_payload = memory_service.build_plan_summary(itinerary=result.model_dump(), requirement=request.original_request.model_dump(), confirmed_constraints={**summary_memory.get("confirmed_constraints", {}), "keep_budget": request.keep_budget, "keep_hotel": request.keep_hotel, "keep_confirmed_segments": request.keep_confirmed_segments}, locked_days=preserved_constraints["locked_days"], rationale_summary=notes[:4])
        memory_service.save_summary(session_id=request.session_id, user_id=request.user_id, summary=summary_payload)
        return result
