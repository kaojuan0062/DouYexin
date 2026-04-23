from schemas.request import NormalizedRequirement


def build_summary_prompt(req: NormalizedRequirement) -> str:
    return (
        f"请输出一段旅游规划摘要：目的地={req.destination}，天数={req.days}，"
        f"预算={req.budget}，偏好={','.join(req.preferences)}，节奏={req.pace}。"
    )
