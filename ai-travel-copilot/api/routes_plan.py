from fastapi import APIRouter

from graph.travel_graph import run_travel_graph
from memory.memory_service import memory_service
from schemas.graph import GraphTravelRequest, GraphTravelResponse
from schemas.itinerary import ChatPlanResponse, ItineraryResponse
from schemas.request import ChatPlanRequest, PlanRequest, ReplanRequest
from services.planner_service import PlannerService

router = APIRouter(prefix="/plan", tags=["plan"])
planner_service = PlannerService()


@router.get("/health")
def plan_health() -> dict:
    """规划模块健康检查。"""

    return {"status": "ok", "module": "plan"}


@router.post("/generate", response_model=ItineraryResponse)
def generate_plan(request: PlanRequest) -> ItineraryResponse:
    """生成完整旅游规划（结构化入参）。"""

    return planner_service.generate_plan(request)


@router.post("/graph", response_model=GraphTravelResponse)
def graph_plan(request: GraphTravelRequest) -> GraphTravelResponse:
    """LangGraph 版本的多 Agent 规划入口。"""

    return run_travel_graph(request)


@router.post("/chat", response_model=ChatPlanResponse)
def chat_plan(request: ChatPlanRequest) -> ChatPlanResponse:
    """口语化需求规划入口。"""

    return planner_service.chat_plan(request)


@router.post("/replan", response_model=ItineraryResponse)
def replan(request: ReplanRequest) -> ItineraryResponse:
    """根据变化条件进行局部重规划。"""

    return planner_service.replan(request)


@router.get("/memory/{session_id}")
def get_memory(session_id: str, user_id: str | None = None) -> dict:
    context = memory_service.load_context(session_id=session_id, user_id=user_id)
    return {
        "session_memory": context["session"],
        "preference_memory": context["preference"],
        "summary_memory": context["summary"],
        "research_memory": context["research"],
    }


@router.post("", response_model=ItineraryResponse)
def create_plan_legacy(request: PlanRequest) -> ItineraryResponse:
    """兼容第一轮接口: POST /plan。"""

    return planner_service.generate_plan(request)
