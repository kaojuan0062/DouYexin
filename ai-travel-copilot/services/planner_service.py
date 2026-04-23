from schemas.itinerary import ChatPlanResponse, ItineraryResponse
from schemas.request import ChatPlanRequest, PlanRequest, ReplanRequest
from services.workflow_service import WorkflowService
from utils.logger import get_logger


class PlannerService:
    """兼容层：旧服务名称保留，内部转发到工作流服务。"""

    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self.workflow = WorkflowService()

    def generate_plan(self, request: PlanRequest) -> ItineraryResponse:
        self.logger.info("PlannerService -> WorkflowService.generate")
        return self.workflow.generate(request)

    def chat_plan(self, request: ChatPlanRequest) -> ChatPlanResponse:
        self.logger.info("PlannerService -> WorkflowService.chat_plan")
        return self.workflow.chat_plan(request)

    def replan(self, request: ReplanRequest) -> ItineraryResponse:
        self.logger.info("PlannerService -> WorkflowService.replan")
        return self.workflow.replan(request)
