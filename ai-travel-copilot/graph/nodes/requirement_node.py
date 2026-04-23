from typing import Any

from context.context_builder import context_builder
from memory.memory_service import memory_service
from schemas.graph import TravelState
from schemas.request import NormalizedRequirement, PlanRequest
from services.workflow_service import WorkflowService

workflow_service = WorkflowService()
_requirement_agent = workflow_service.coordinator.requirement_agent


def _to_plan_request(state: TravelState, requirement: NormalizedRequirement) -> PlanRequest:
    original = dict(state.get("original_request") or {})
    constraints = original.get(
        "constraints",
        {"pace": requirement.pace, "indoor_first": requirement.indoor_first},
    )
    return PlanRequest(
        origin=str(original.get("origin", requirement.origin)),
        destination=str(original.get("destination", requirement.destination)),
        days=int(original.get("days", requirement.days)),
        budget=float(original.get("budget", requirement.budget)),
        preferences=list(original.get("preferences", requirement.preferences)),
        constraints=constraints,
        session_id=str(state["session_id"]),
        user_id=state.get("user_id"),
    )


def requirement_node(state: TravelState) -> TravelState:
    session_id = str(state["session_id"])
    user_id = state.get("user_id")
    state["memory_context"] = memory_service.load_context(session_id=session_id, user_id=user_id)

    if state.get("mode") == "replan":
        original_request = dict(state.get("original_request") or {})
        plan_request = PlanRequest(**original_request)
        requirement = _requirement_agent.run(
            request=plan_request,
            request_id=str(state["request_id"]),
            agent_context=context_builder.build_requirement_context(
                session_id=session_id,
                user_id=user_id,
                user_input=state.get("user_input", "graph-replan"),
            ),
        )
    else:
        requirement = _requirement_agent.parse_natural_language(
            user_input=state.get("user_input", ""),
            request_id=str(state["request_id"]),
            session_id=session_id,
            user_id=user_id,
            agent_context=context_builder.build_requirement_context(
                session_id=session_id,
                user_input=state.get("user_input", ""),
                user_id=user_id,
            ),
        )
        state["original_request"] = _to_plan_request(state, requirement).model_dump()

    state["normalized_requirement"] = requirement.model_dump()
    return state
