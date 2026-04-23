from schemas.models import DayPlan, PlanRequest, PlanResponse
from tools.mock_budget_tool import estimate_budget
from tools.mock_poi_tool import get_poi_candidates
from tools.mock_weather_tool import get_weather_forecast


class PlannerAgent:
    def plan(self, request: PlanRequest) -> PlanResponse:
        poi_data = get_poi_candidates(request.destination)
        weather_data = get_weather_forecast(request.destination, request.days)
        budget_data = estimate_budget(
            total_budget=request.budget,
            days=request.days,
            preferences=request.preferences,
        )

        daily_plan = []
        attractions = poi_data["attractions"]
        foods = poi_data["foods"]

        for i in range(request.days):
            attraction = attractions[i % len(attractions)]
            food = foods[i % len(foods)]
            weather = weather_data[i % len(weather_data)]
            pref_text = "、".join(request.preferences) if request.preferences else "轻松休闲"

            daily_plan.append(
                DayPlan(
                    day=i + 1,
                    weather=weather,
                    activities=[
                        f"上午：游览 {attraction}",
                        f"中午：品尝 {food}",
                        f"下午：围绕“{pref_text}”安排城市漫步或主题活动",
                        "晚上：自由活动与打卡夜景",
                    ],
                    transport_tip="市内优先地铁+步行，跨区建议打车",
                )
            )

        summary = (
            f"为你生成了从{request.origin}出发前往{request.destination}的"
            f"{request.days}天行程，预算约¥{request.budget:.0f}。"
        )

        notes = [
            "本计划为 mock 版本，景点与天气为示例数据。",
            "可在后续版本接入真实地图、天气与票务 API。",
        ]

        return PlanResponse(
            summary=summary,
            daily_plan=daily_plan,
            estimated_budget=budget_data,
            notes=notes,
        )
