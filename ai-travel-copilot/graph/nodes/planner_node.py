from schemas.graph import TravelState
from schemas.request import NormalizedRequirement, PlanRequest
from services.workflow_service import WorkflowService

workflow_service = WorkflowService()
_coordinator = workflow_service.coordinator


def planner_node(state: TravelState) -> TravelState:
    requirement = NormalizedRequirement(**state["normalized_requirement"])
    request = PlanRequest(**dict(state.get("original_request") or {}))
    research = state.get("research_results", {})
    itinerary = _coordinator._build_itinerary(
        request=request,
        request_id=str(state["request_id"]),
        requirement=requirement,
        rewritten_queries=state.get("rewritten_queries", {}),
        source_summary=research.get("source_summary", {}),
        recommended_candidates=state.get("candidate_pool", {}),
        recommendation_reasons=state.get("recommendation_reasons", []),
        candidate_pool_summary=state.get("candidate_pool_summary", {}),
        research_memory_hit=bool(research.get("research_memory_hit", False)),
        reused_candidates_count=int(research.get("reused_candidates_count", 0)),
        refreshed_queries=research.get("refreshed_queries", {}),
        cache_strategy=str(research.get("cache_strategy", "full_refresh")),
    )
    state["itinerary"] = itinerary.model_dump()
    return state
