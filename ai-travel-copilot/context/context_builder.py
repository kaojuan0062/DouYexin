from __future__ import annotations

from typing import Any, Dict

from context.models import AgentContext
from memory.memory_service import memory_service
from schemas.request import NormalizedRequirement, ReplanRequest
from utils.logger import get_logger


class ContextBuilder:
    def __init__(self) -> None:
        self.logger = get_logger(__name__)

    def _base(self, session_id: str, user_id: str | None = None) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
        context = memory_service.load_context(session_id=session_id, user_id=user_id)
        effective = memory_service.get_effective_constraints(session_id=session_id, user_id=user_id)
        return context, effective

    def _log_context(self, session_id: str, user_id: str | None, agent_name: str, ctx: AgentContext) -> None:
        summary = ctx.summary()
        self.logger.info(
            f"context_built agent={agent_name} session_id={session_id} user_id={user_id or '-'} "
            f"visible_sections={summary['visible_sections']} memory_keys={summary['memory_keys']} "
            f"recent_summary_keys={summary['recent_summary_keys']} research_cache_keys={summary['research_cache_keys']}"
        )

    def build_requirement_context(self, session_id: str, user_input: str, user_id: str | None = None) -> AgentContext:
        context, effective = self._base(session_id=session_id, user_id=user_id)
        ctx = AgentContext(
            scope="requirement",
            current_input={"user_input": user_input},
            memory_context={
                "preference": context["preference"],
                "summary": context["summary"],
                "session": {"parsed_requirement": context["session"].get("parsed_requirement", {})},
            },
            effective_constraints=effective,
            recent_summary=context["summary"],
            optional_research_cache={},
            visible_sections=["current_input", "preference_memory", "summary_memory", "effective_constraints"],
        )
        self._log_context(session_id, user_id, "RequirementAgent", ctx)
        return ctx

    def build_query_rewrite_context(self, session_id: str, normalized_requirement: NormalizedRequirement) -> AgentContext:
        context, effective = self._base(session_id=session_id, user_id=normalized_requirement.user_id)
        ctx = AgentContext(
            scope="query_rewrite",
            current_input={"normalized_requirement": normalized_requirement.model_dump()},
            memory_context={
                "preference": context["preference"],
                "summary": context["summary"],
            },
            effective_constraints=effective,
            recent_summary=context["summary"],
            optional_research_cache={
                "rewritten_queries": context["research"].get("rewritten_queries", {}),
                "freshness_tag": context["research"].get("freshness_tag"),
                "search_results_summary": context["research"].get("search_results_summary", {}),
            },
            visible_sections=["current_input", "summary_memory", "research_memory_summary", "effective_constraints"],
        )
        self._log_context(session_id, normalized_requirement.user_id, "QueryRewriteAgent", ctx)
        return ctx

    def build_research_context(self, session_id: str, rewritten_queries: Dict[str, list[str]], user_id: str | None = None) -> AgentContext:
        context, effective = self._base(session_id=session_id, user_id=user_id)
        ctx = AgentContext(
            scope="research",
            current_input={"rewritten_queries": rewritten_queries},
            memory_context={
                "summary": context["summary"],
                "session": {"parsed_requirement": context["session"].get("parsed_requirement", {})},
            },
            effective_constraints=effective,
            recent_summary=context["summary"],
            optional_research_cache=context["research"],
            visible_sections=["current_input", "recent_summary", "research_cache", "effective_constraints"],
        )
        self._log_context(session_id, user_id, "WebResearchAgent", ctx)
        return ctx

    def build_planner_context(self, session_id: str, candidate_pool: Dict[str, list[dict[str, Any]]], user_id: str | None = None) -> AgentContext:
        context, effective = self._base(session_id=session_id, user_id=user_id)
        ctx = AgentContext(
            scope="planner",
            current_input={"candidate_pool": candidate_pool},
            memory_context={
                "summary": context["summary"],
                "session": {"current_itinerary": context["session"].get("current_itinerary", {})},
            },
            effective_constraints=effective,
            recent_summary=context["summary"],
            optional_research_cache={
                "ranked_candidates": context["research"].get("ranked_candidates", {}),
                "search_results_summary": context["research"].get("search_results_summary", {}),
            },
            visible_sections=["candidate_pool", "budget_and_constraints", "recent_summary", "research_cache"],
        )
        self._log_context(session_id, user_id, "PlannerFlow", ctx)
        return ctx

    def build_replanner_context(self, session_id: str, replan_request: ReplanRequest) -> AgentContext:
        context, effective = self._base(session_id=session_id, user_id=replan_request.user_id)
        ctx = AgentContext(
            scope="replanner",
            current_input={"replan_request": replan_request.model_dump()},
            memory_context={
                "session": {"current_itinerary": context["session"].get("current_itinerary", {})},
                "summary": context["summary"],
            },
            effective_constraints=effective,
            recent_summary=context["summary"],
            optional_research_cache={
                "rewritten_queries": context["research"].get("rewritten_queries", {}),
                "candidate_pool": context["research"].get("candidate_pool", {}),
                "freshness_tag": context["research"].get("freshness_tag"),
            },
            visible_sections=["current_itinerary", "locked_days", "recent_summary", "research_cache"],
        )
        self._log_context(session_id, replan_request.user_id, "ReplannerAgent", ctx)
        return ctx


context_builder = ContextBuilder()
