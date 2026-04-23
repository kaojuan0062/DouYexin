import uuid
from typing import Any

from langgraph.graph import END, START, StateGraph

from graph.nodes.planner_node import planner_node
from graph.nodes.query_rewrite_node import query_rewrite_node
from graph.nodes.ranking_node import ranking_node
from graph.nodes.replanner_node import replanner_node
from graph.nodes.requirement_node import requirement_node
from graph.nodes.research_node import research_node
from schemas.graph import GraphTravelRequest, GraphTravelResponse, TravelState


def _route_mode(state: TravelState) -> str:
    return "replanner" if state.get("mode") == "replan" else "requirement"


def build_travel_graph() -> Any:
    graph = StateGraph(TravelState)
    graph.add_node("requirement", requirement_node)
    graph.add_node("query_rewrite", query_rewrite_node)
    graph.add_node("research", research_node)
    graph.add_node("ranking", ranking_node)
    graph.add_node("planner", planner_node)
    graph.add_node("replanner", replanner_node)

    graph.add_conditional_edges(
        START,
        _route_mode,
        {
            "requirement": "requirement",
            "replanner": "replanner",
        },
    )
    graph.add_edge("requirement", "query_rewrite")
    graph.add_edge("query_rewrite", "research")
    graph.add_edge("research", "ranking")
    graph.add_edge("ranking", "planner")
    graph.add_edge("planner", END)
    graph.add_edge("replanner", END)
    return graph.compile()


def run_travel_graph(request: GraphTravelRequest) -> GraphTravelResponse:
    app = build_travel_graph()
    initial_state: TravelState = {
        "mode": request.mode,
        "request_id": str(uuid.uuid4()),
        "session_id": request.session_id,
        "user_id": request.user_id,
        "user_input": request.user_input,
        "original_request": dict(request.original_request or {}),
        "current_plan": dict(request.current_plan or {}),
        "reason": request.reason,
        "affected_days": list(request.affected_days or []),
        "locked_days": list(request.locked_days or []),
        "keep_budget": request.keep_budget,
        "keep_hotel": request.keep_hotel,
        "keep_confirmed_segments": request.keep_confirmed_segments,
        "new_budget": request.new_budget,
        "closed_poi": request.closed_poi,
        "food_focus": request.food_focus,
        "memory_context": {},
        "normalized_requirement": {},
        "rewritten_queries": {},
        "research_results": {},
        "candidate_pool": {},
        "recommendation_reasons": [],
        "candidate_pool_summary": {},
        "itinerary": {},
        "react_trace": [],
    }
    final_state = app.invoke(initial_state)
    return GraphTravelResponse(
        mode=request.mode,
        state=dict(final_state),
        itinerary=dict(final_state.get("itinerary", {})),
    )
