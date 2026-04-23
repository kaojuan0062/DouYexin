import time
import uuid

from agents.coordinator_agent import CoordinatorAgent
from agents.replanner_agent import ReplannerAgent
from observability.metrics import metrics_collector
from schemas.itinerary import ChatPlanResponse, ItineraryResponse
from schemas.request import ChatPlanRequest, PlanRequest, ReplanRequest
from utils.logger import get_logger


class WorkflowService:
    """负责多 Agent 工作流编排。"""

    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self.coordinator = CoordinatorAgent()
        self.replanner = ReplannerAgent()

    def generate(self, request: PlanRequest) -> ItineraryResponse:
        request_id = str(uuid.uuid4())
        if not request.session_id:
            request.session_id = str(uuid.uuid4())
        metrics_collector.start_run(request_id=request_id, route="/plan/generate")
        metrics_collector.record_workflow_step(request_id, "workflow_generate_start")

        start = time.perf_counter()
        result = self.coordinator.run(request, request_id=request_id)
        run_metrics = metrics_collector.end_run(request_id)

        self.logger.info(
            f"workflow_generate_done request_id={request_id} session_id={request.session_id} duration_ms={(time.perf_counter() - start)*1000:.2f}"
        )

        result.planning_trace_summary = {
            "request_id": run_metrics["request_id"],
            "workflow_steps": run_metrics.get("workflow_steps", []),
            "duration_ms": run_metrics.get("duration_ms", 0),
            "constraint_satisfaction": run_metrics.get("constraint_satisfaction", {}),
        }
        result.tool_usage_summary = {
            "tool_calls": run_metrics.get("tool_calls", 0),
            "tools": run_metrics.get("tools", {}),
            "fallback_used": run_metrics.get("fallback_used", {}),
        }
        result.meta = {**result.meta, "metrics": run_metrics}
        return result

    def chat_plan(self, request: ChatPlanRequest) -> ChatPlanResponse:
        request_id = str(uuid.uuid4())
        if not request.session_id:
            request.session_id = str(uuid.uuid4())
        metrics_collector.start_run(request_id=request_id, route="/plan/chat")
        metrics_collector.record_workflow_step(request_id, "workflow_chat_start")

        result = self.coordinator.run_chat(request, request_id=request_id)
        run_metrics = metrics_collector.end_run(request_id)

        self.logger.info(f"workflow_chat_done request_id={request_id} session_id={request.session_id}")
        result.final_plan.planning_trace_summary = {
            "request_id": run_metrics["request_id"],
            "workflow_steps": run_metrics.get("workflow_steps", []),
            "duration_ms": run_metrics.get("duration_ms", 0),
            "constraint_satisfaction": run_metrics.get("constraint_satisfaction", {}),
        }
        result.final_plan.tool_usage_summary = {
            "tool_calls": run_metrics.get("tool_calls", 0),
            "tools": run_metrics.get("tools", {}),
            "fallback_used": run_metrics.get("fallback_used", {}),
        }
        result.final_plan.meta = {**result.final_plan.meta, "metrics": run_metrics}
        return result

    def replan(self, request: ReplanRequest) -> ItineraryResponse:
        request_id = str(uuid.uuid4())
        if not request.session_id:
            request.session_id = str(uuid.uuid4())
        metrics_collector.start_run(request_id=request_id, route="/plan/replan")
        metrics_collector.record_workflow_step(request_id, "workflow_replan_start")
        metrics_collector.record_workflow_step(request_id, "replanner_agent")

        result = self.replanner.run(request, request_id=request_id)
        run_metrics = metrics_collector.end_run(request_id)

        self.logger.info(f"workflow_replan_done request_id={request_id} session_id={request.session_id}")

        result.planning_trace_summary = {
            "request_id": run_metrics["request_id"],
            "workflow_steps": run_metrics.get("workflow_steps", []),
            "duration_ms": run_metrics.get("duration_ms", 0),
            "constraint_satisfaction": run_metrics.get("constraint_satisfaction", {}),
        }
        result.tool_usage_summary = {
            "tool_calls": run_metrics.get("tool_calls", 0),
            "tools": run_metrics.get("tools", {}),
            "fallback_used": run_metrics.get("fallback_used", {}),
        }
        result.meta = {**result.meta, "metrics": run_metrics}
        return result
