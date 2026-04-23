from schemas.graph import TravelState
from schemas.request import PlanRequest, ReplanRequest
from services.workflow_service import WorkflowService

workflow_service = WorkflowService()
_replanner = workflow_service.replanner


def replanner_node(state: TravelState) -> TravelState:
    request = ReplanRequest(
        original_request=PlanRequest(**dict(state.get("original_request") or {})),
        current_plan=dict(state.get("current_plan") or {}),
        affected_days=list(state.get("affected_days") or []),
        locked_days=list(state.get("locked_days") or []),
        reason=str(state.get("reason", "rain")),
        keep_budget=bool(state.get("keep_budget", True)),
        keep_hotel=bool(state.get("keep_hotel", True)),
        keep_confirmed_segments=bool(state.get("keep_confirmed_segments", True)),
        new_budget=state.get("new_budget"),
        closed_poi=state.get("closed_poi"),
        food_focus=bool(state.get("food_focus", False)),
        session_id=str(state["session_id"]),
        user_id=state.get("user_id"),
    )
    result = _replanner.run(request=request, request_id=str(state["request_id"]))
    state["itinerary"] = result.model_dump()
    return state
