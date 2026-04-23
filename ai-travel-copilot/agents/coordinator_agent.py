import time
from typing import Dict, List

from agents.budget_agent import BudgetAgent
from agents.poi_agent import POIAgent
from agents.query_rewrite_agent import QueryRewriteAgent
from agents.ranking_fusion_agent import RankingFusionAgent
from agents.requirement_agent import RequirementAgent
from agents.schedule_agent import ScheduleAgent
from agents.web_research_agent import WebResearchAgent
from context.context_builder import context_builder
from memory.memory_service import memory_service
from observability.metrics import metrics_collector
from schemas.itinerary import ChatPlanResponse, ItineraryResponse
from schemas.request import ChatPlanRequest, NormalizedRequirement, PlanRequest
from utils.logger import get_logger


class CoordinatorAgent:
    """工作流协调器：requirement -> query_rewrite -> web_research -> ranking -> poi -> schedule -> budget。"""

    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self.requirement_agent = RequirementAgent()
        self.query_rewrite_agent = QueryRewriteAgent()
        self.web_research_agent = WebResearchAgent()
        self.ranking_fusion_agent = RankingFusionAgent()
        self.poi_agent = POIAgent()
        self.schedule_agent = ScheduleAgent()
        self.budget_agent = BudgetAgent()

    def _build_itinerary(self, request: PlanRequest, request_id: str, requirement: NormalizedRequirement, rewritten_queries: Dict[str, List[str]], source_summary: Dict[str, object], recommended_candidates: Dict[str, List[Dict[str, object]]], recommendation_reasons: List[str], candidate_pool_summary: Dict[str, object], research_memory_hit: bool, reused_candidates_count: int, refreshed_queries: Dict[str, List[str]], cache_strategy: str) -> ItineraryResponse:
        planner_context = context_builder.build_planner_context(session_id=request.session_id, user_id=request.user_id, candidate_pool=recommended_candidates)
        metrics_collector.record_workflow_step(request_id, "poi_agent")
        t1 = time.perf_counter()
        poi_selection = self.poi_agent.run(requirement, request_id=request_id, fused_candidates=recommended_candidates)
        metrics_collector.record_agent(request_id, "POIAgent", (time.perf_counter() - t1) * 1000)
        metrics_collector.record_workflow_step(request_id, "schedule_agent")
        t2 = time.perf_counter()
        daily_plan = self.schedule_agent.run(requirement, poi_selection, request_id=request_id)
        metrics_collector.record_agent(request_id, "ScheduleAgent", (time.perf_counter() - t2) * 1000)
        metrics_collector.record_workflow_step(request_id, "budget_agent")
        t3 = time.perf_counter()
        estimated_budget = self.budget_agent.run(requirement, request_id=request_id)
        metrics_collector.record_agent(request_id, "BudgetAgent", (time.perf_counter() - t3) * 1000)

        notes: List[str] = ["已融合规则解析、联网检索、多来源排序后的规划结果。"]
        notes.extend(self.schedule_agent.last_weather_notes)
        notes.extend(self.schedule_agent.last_route_notes)
        notes.extend(recommendation_reasons[:3])
        if requirement.locked_constraints:
            notes.append("本次规划已参考历史确认约束与已锁定信息。")
        if requirement.inherited_preferences:
            notes.append(f"已复用历史偏好：{requirement.inherited_preferences}。")
        if requirement.overridden_preferences:
            notes.append(f"本次已覆盖历史偏好：{requirement.overridden_preferences}。")
        if research_memory_hit:
            notes.append(f"Research Memory 命中：strategy={cache_strategy}，复用候选={reused_candidates_count}。")
        notes.append(f"Planner Context sections={planner_context.visible_sections}。")

        summary = f"已生成{request.origin}到{request.destination}的{request.days}天规划，节奏={request.constraints.pace}，预算¥{request.budget:.0f}。"
        day_completeness = len(daily_plan) / request.days if request.days else 0
        metrics_collector.record_constraints(request_id=request_id, budget_ok=estimated_budget.within_budget, itinerary_ok=(len(daily_plan) == request.days), day_completeness=day_completeness)

        itinerary = ItineraryResponse(summary=summary, daily_plan=daily_plan, estimated_budget=estimated_budget, notes=notes, hotel_recommendations=estimated_budget.hotel_recommendations, budget_breakdown=estimated_budget.budget_breakdown, over_budget_flag=estimated_budget.over_budget_flag, optimization_suggestions=estimated_budget.optimization_suggestions, normalized_requirements=requirement.model_dump(), query_rewrites=rewritten_queries, source_summary=source_summary, recommendation_reasons=recommendation_reasons, candidate_pool_summary=candidate_pool_summary, research_memory_hit=research_memory_hit, reused_candidates_count=reused_candidates_count, refreshed_queries=refreshed_queries, cache_strategy=cache_strategy, meta={"request_id": request_id, "session_id": request.session_id})

        memory_service.save_itinerary(session_id=request.session_id, user_id=request.user_id, itinerary=itinerary.model_dump())
        summary_payload = memory_service.build_plan_summary(itinerary=itinerary.model_dump(), requirement=requirement.model_dump(), confirmed_constraints={"pace": requirement.pace, "indoor_first": requirement.indoor_first, "budget_max": requirement.budget_max, "hotel_locked": bool(itinerary.hotel_recommendations)}, locked_days=[], rationale_summary=notes[:3])
        memory_service.save_summary(session_id=request.session_id, user_id=request.user_id, summary=summary_payload)
        return itinerary

    def _research_with_memory(self, request_id: str, requirement: NormalizedRequirement, rewritten_queries: Dict[str, List[str]], session_id: str, user_id: str | None, replan_reason: str | None = None) -> tuple[dict, dict]:
        decision = memory_service.evaluate_research_reuse(session_id=session_id, user_id=user_id, requirement=requirement.model_dump(), rewritten_queries=rewritten_queries, replan_reason=replan_reason)
        context_builder.build_research_context(session_id=session_id, user_id=user_id, rewritten_queries=rewritten_queries)
        research = self.web_research_agent.run_with_cache(request_id=request_id, queries=rewritten_queries, cache_decision=decision)
        return decision, research

    def run(self, request: PlanRequest, request_id: str) -> ItineraryResponse:
        requirement_context = context_builder.build_requirement_context(session_id=request.session_id, user_id=request.user_id, user_input=f"{request.origin}->{request.destination}")
        metrics_collector.record_workflow_step(request_id, "requirement_agent")
        t0 = time.perf_counter()
        requirement = self.requirement_agent.run(request, request_id=request_id, agent_context=requirement_context)
        metrics_collector.record_agent(request_id, "RequirementAgent", (time.perf_counter() - t0) * 1000)

        query_context = context_builder.build_query_rewrite_context(session_id=request.session_id, normalized_requirement=requirement)
        metrics_collector.record_workflow_step(request_id, "query_rewrite_agent")
        rewritten_queries = self.query_rewrite_agent.run(requirement, request_id=request_id, agent_context=query_context)

        metrics_collector.record_workflow_step(request_id, "web_research_agent")
        _, research = self._research_with_memory(request_id=request_id, requirement=requirement, rewritten_queries=rewritten_queries, session_id=request.session_id, user_id=request.user_id)

        metrics_collector.record_workflow_step(request_id, "ranking_fusion_agent")
        fusion = self.ranking_fusion_agent.run(request_id=request_id, requirement=requirement, candidate_pool=research["candidate_pool"])
        memory_service.save_research_results(session_id=request.session_id, user_id=request.user_id, research_result={"normalized_requirements_snapshot": requirement.model_dump(), "rewritten_queries": rewritten_queries, "search_results_summary": research["source_summary"], "candidate_pool": research["candidate_pool"], "ranked_candidates": fusion["recommended_candidates"], "freshness_tag": research.get("freshness_tag", "fresh")})
        return self._build_itinerary(request=request, request_id=request_id, requirement=requirement, rewritten_queries=rewritten_queries, source_summary=research["source_summary"], recommended_candidates=fusion["recommended_candidates"], recommendation_reasons=fusion["recommendation_reasons"], candidate_pool_summary=fusion["candidate_pool_summary"], research_memory_hit=bool(research.get("research_memory_hit", False)), reused_candidates_count=int(research.get("reused_candidates_count", 0)), refreshed_queries=research.get("refreshed_queries", {}), cache_strategy=str(research.get("cache_strategy", "full_refresh")))

    def run_chat(self, request: ChatPlanRequest, request_id: str) -> ChatPlanResponse:
        requirement_context = context_builder.build_requirement_context(session_id=request.session_id, user_id=request.user_id, user_input=request.user_input)
        metrics_collector.record_workflow_step(request_id, "requirement_agent_nl")
        requirement = self.requirement_agent.parse_natural_language(user_input=request.user_input, request_id=request_id, session_id=request.session_id, user_id=request.user_id, agent_context=requirement_context)

        query_context = context_builder.build_query_rewrite_context(session_id=request.session_id, normalized_requirement=requirement)
        metrics_collector.record_workflow_step(request_id, "query_rewrite_agent")
        rewritten_queries = self.query_rewrite_agent.run(requirement, request_id=request_id, agent_context=query_context)

        metrics_collector.record_workflow_step(request_id, "web_research_agent")
        _, research = self._research_with_memory(request_id=request_id, requirement=requirement, rewritten_queries=rewritten_queries, session_id=request.session_id, user_id=request.user_id)

        metrics_collector.record_workflow_step(request_id, "ranking_fusion_agent")
        fusion = self.ranking_fusion_agent.run(request_id=request_id, requirement=requirement, candidate_pool=research["candidate_pool"])
        memory_service.save_research_results(session_id=request.session_id, user_id=request.user_id, research_result={"normalized_requirements_snapshot": requirement.model_dump(), "rewritten_queries": rewritten_queries, "search_results_summary": research["source_summary"], "candidate_pool": research["candidate_pool"], "ranked_candidates": fusion["recommended_candidates"], "freshness_tag": research.get("freshness_tag", "fresh")})

        synthetic_request = PlanRequest(origin=requirement.origin, destination=requirement.destination, days=requirement.days, budget=requirement.budget, preferences=requirement.preferences, constraints={"pace": requirement.pace, "indoor_first": requirement.indoor_first}, session_id=requirement.session_id, user_id=requirement.user_id)
        itinerary = self._build_itinerary(request=synthetic_request, request_id=request_id, requirement=requirement, rewritten_queries=rewritten_queries, source_summary=research["source_summary"], recommended_candidates=fusion["recommended_candidates"], recommendation_reasons=fusion["recommendation_reasons"], candidate_pool_summary=fusion["candidate_pool_summary"], research_memory_hit=bool(research.get("research_memory_hit", False)), reused_candidates_count=int(research.get("reused_candidates_count", 0)), refreshed_queries=research.get("refreshed_queries", {}), cache_strategy=str(research.get("cache_strategy", "full_refresh")))
        return ChatPlanResponse(normalized_requirements=requirement.model_dump(), rewritten_queries=rewritten_queries, research_summary=research["source_summary"], recommended_candidates=fusion["recommended_candidates"], memory_applied=requirement.memory_applied, inherited_preferences=requirement.inherited_preferences, overridden_preferences=requirement.overridden_preferences, research_memory_hit=bool(research.get("research_memory_hit", False)), reused_candidates_count=int(research.get("reused_candidates_count", 0)), refreshed_queries=research.get("refreshed_queries", {}), cache_strategy=str(research.get("cache_strategy", "full_refresh")), final_plan=itinerary)
