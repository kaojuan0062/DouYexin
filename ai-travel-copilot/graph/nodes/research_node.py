from agents.react_agent import ReactAgent
from config.settings import settings
from schemas.graph import TravelState
from schemas.request import NormalizedRequirement
from services.workflow_service import WorkflowService

workflow_service = WorkflowService()
_coordinator = workflow_service.coordinator
_react_agent = ReactAgent()


def research_node(state: TravelState) -> TravelState:
    requirement = NormalizedRequirement(**state["normalized_requirement"])
    use_react = bool(settings.REACT_AGENT_MODE)

    if use_react:
        try:
            research = _react_agent.run(
                request_id=str(state["request_id"]),
                queries=state.get("rewritten_queries", {}),
            )
            state["react_trace"] = research.get("react_trace", [])
        except Exception:
            _, research = _coordinator._research_with_memory(
                request_id=str(state["request_id"]),
                requirement=requirement,
                rewritten_queries=state.get("rewritten_queries", {}),
                session_id=str(state["session_id"]),
                user_id=state.get("user_id"),
                replan_reason=state.get("reason") if state.get("mode") == "replan" else None,
            )
            state["react_trace"] = []
    else:
        _, research = _coordinator._research_with_memory(
            request_id=str(state["request_id"]),
            requirement=requirement,
            rewritten_queries=state.get("rewritten_queries", {}),
            session_id=str(state["session_id"]),
            user_id=state.get("user_id"),
            replan_reason=state.get("reason") if state.get("mode") == "replan" else None,
        )
        state["react_trace"] = []
    state["research_results"] = research
    state["candidate_pool"] = research.get("candidate_pool", {})
    return state
