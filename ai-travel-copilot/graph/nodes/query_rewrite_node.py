from context.context_builder import context_builder
from schemas.graph import TravelState
from schemas.request import NormalizedRequirement
from services.workflow_service import WorkflowService

workflow_service = WorkflowService()
_query_rewrite_agent = workflow_service.coordinator.query_rewrite_agent


def query_rewrite_node(state: TravelState) -> TravelState:
    requirement = NormalizedRequirement(**state["normalized_requirement"])
    queries = _query_rewrite_agent.run(
        requirement=requirement,
        request_id=str(state["request_id"]),
        agent_context=context_builder.build_query_rewrite_context(
            session_id=str(state["session_id"]),
            normalized_requirement=requirement,
        ),
    )
    state["rewritten_queries"] = queries
    return state
