import json

from services.workflow_service import WorkflowService
from schemas.request import PlanConstraints, PlanRequest


def main() -> None:
    workflow = WorkflowService()
    request = PlanRequest(
        origin="上海",
        destination="杭州",
        days=3,
        budget=3000,
        preferences=["美食", "夜景", "历史"],
        constraints=PlanConstraints(pace="轻松", indoor_first=False),
        session_id="demo-session",
    )
    result = workflow.generate(request)
    print(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
