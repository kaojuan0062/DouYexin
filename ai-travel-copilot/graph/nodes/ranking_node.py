from memory.memory_service import memory_service
from schemas.graph import TravelState
from schemas.request import NormalizedRequirement
from services.workflow_service import WorkflowService

workflow_service = WorkflowService()
_ranking_agent = workflow_service.coordinator.ranking_fusion_agent


def ranking_node(state: TravelState) -> TravelState:
    requirement = NormalizedRequirement(**state["normalized_requirement"])
    research = state.get("research_results", {})
    fusion = _ranking_agent.run(
        request_id=str(state["request_id"]),
        requirement=requirement,
        candidate_pool=research.get("candidate_pool", {}),
    )
    state["candidate_pool"] = fusion.get("recommended_candidates", {})
    state["recommendation_reasons"] = fusion.get("recommendation_reasons", [])
    state["candidate_pool_summary"] = fusion.get("candidate_pool_summary", {})
    memory_service.save_research_results(
        session_id=str(state["session_id"]),
        user_id=state.get("user_id"),
        research_result={
            "normalized_requirements_snapshot": requirement.model_dump(),
            "rewritten_queries": state.get("rewritten_queries", {}),
            "search_results_summary": research.get("source_summary", {}),
            "candidate_pool": research.get("candidate_pool", {}),
            "ranked_candidates": fusion.get("recommended_candidates", {}),
            "freshness_tag": research.get("freshness_tag", "fresh"),
        },
    )
    return state
