import re
import time
from typing import Any, Dict

from config.settings import settings
from context.models import AgentContext
from llm.langchain_client import LangChainChatModel
from llm.openai_client import OpenAIClient
from memory.memory_service import memory_service
from schemas.request import NormalizedRequirement, PlanRequest
from utils.logger import get_logger, log_event


class RequirementAgent:
    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self.llm_client = OpenAIClient()
        self.langchain_llm = LangChainChatModel()

    def _build_parse_prompt(self, user_input: str) -> str:
        return f"""
你是旅行需求解析器。请把用户口语化需求解析为 JSON，禁止输出多余文本。
输出字段：
- origin,destination,days,budget,budget_min,budget_max,companions,preferences,pace,indoor_first
- hotel_preferences,travel_dates,clarification_needed,clarification_questions
- stable_preferences: 可包含 preferences,hotel_preferences,pace,indoor_first
- temporary_constraints: 可包含 days,budget,budget_min,budget_max,travel_dates
- override_constraints: 可包含 avoid_preferences,avoid_pois,avoid_categories,pace_override
规则：
- “两千多”=> budget=2500, budget_min=2000, budget_max=3000
- “别太赶”=> pace=轻松
- “拍照好看”=> preferences 包含 拍照
- “这次不想去博物馆”=> override_constraints.avoid_preferences 包含 博物馆
用户输入：{user_input}
""".strip()

    def _use_langchain_llm(self) -> bool:
        return settings.LANGCHAIN_LLM_MODE in {"requirement", "all"}

    def _generate_parse_json(self, prompt: str) -> Dict[str, Any]:
        if self._use_langchain_llm():
            return self.langchain_llm.invoke_json(prompt, system_prompt="你是一个旅行需求解析器。请严格输出 JSON。")
        return self.llm_client.generate_json(prompt)

    def _build_structured_extraction(self, request: PlanRequest) -> Dict[str, Any]:
        explicit_preferences = [str(x) for x in request.preferences]
        return {
            "stable_preferences": {"preferences": explicit_preferences, "hotel_preferences": [], "pace": request.constraints.pace, "indoor_first": request.constraints.indoor_first},
            "temporary_constraints": {"days": request.days, "budget": request.budget, "budget_min": round(request.budget * 0.9, 2), "budget_max": round(request.budget * 1.1, 2)},
            "override_constraints": {"avoid_preferences": [], "avoid_pois": [], "avoid_categories": []},
            "explicit_preferences": explicit_preferences,
            "explicit_hotel_preferences": [],
            "explicit_pace": request.constraints.pace,
            "explicit_indoor_first": request.constraints.indoor_first,
        }

    def _apply_memory(self, memory_ctx: Dict[str, Any], effective: Dict[str, Any], current: Dict[str, Any]) -> Dict[str, Any]:
        preference_memory = memory_ctx.get("preference", {})
        conflict = memory_service.resolve_preference_conflicts(existing=preference_memory, current_request=current)
        inherited = conflict["inherited_preferences"]
        overridden = conflict["overridden_preferences"]
        preferences = list(dict.fromkeys([*current.get("explicit_preferences", []), *inherited.get("preferences", [])]))
        preferences = [x for x in preferences if x not in current.get("override_constraints", {}).get("avoid_preferences", [])]
        hotel_preferences = list(dict.fromkeys([*current.get("explicit_hotel_preferences", []), *inherited.get("hotel_preferences", [])]))
        pace = current.get("explicit_pace") or inherited.get("pace") or effective.get("pace") or "轻松"
        indoor_first = current.get("explicit_indoor_first")
        if indoor_first is None:
            indoor_first = inherited.get("indoor_first")
        if indoor_first is None:
            indoor_first = effective.get("indoor_first") if effective.get("indoor_first") is not None else False
        return {"inherited": inherited, "overridden": overridden, "preferences": preferences, "hotel_preferences": hotel_preferences, "pace": pace, "indoor_first": bool(indoor_first)}

    def _as_int(self, value: Any, default: int) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _as_float(self, value: Any, default: float) -> float:
        if value in [None, "", "无限制", "不限", "未知", "待定"]:
            return default
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def _cn_num(self, text: str) -> int | None:
        m = {"一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}
        if not text:
            return None
        if text.isdigit():
            return int(text)
        if text in m:
            return m[text]
        if len(text) == 2 and text[0] == "十" and text[1] in m:
            return 10 + m[text[1]]
        if len(text) == 2 and text[1] == "十" and text[0] in m:
            return m[text[0]] * 10
        if len(text) == 3 and text[1] == "十" and text[0] in m and text[2] in m:
            return m[text[0]] * 10 + m[text[2]]
        return None

    def _extract_budget(self, text: str) -> tuple[float | None, float | None, float | None]:
        match = re.search(r"(\d+(?:\.\d+)?)\s*(千|k|K|万|w|W)?\s*(多|左右|以内|以下)?", text)
        if not match:
            return None, None, None
        value = float(match.group(1))
        unit = match.group(2) or ""
        suffix = match.group(3) or ""
        if unit in {"千", "k", "K"}:
            value *= 1000
        elif unit in {"万", "w", "W"}:
            value *= 10000
        if suffix == "多":
            return value + 500, value, value + 1000
        if suffix in {"以内", "以下"}:
            return value, max(value * 0.7, 0), value
        return value, value * 0.8, value * 1.2

    def _normalize_pace(self, value: Any, default: str = "轻松") -> str:
        text = str(value or "").strip()
        if text == "紧凑":
            return "紧凑"
        if text == "轻松":
            return "轻松"
        if any(word in text for word in ["紧凑", "赶", "高密度", "特种兵", "安排满"]):
            return "紧凑"
        if any(word in text for word in ["轻松", "悠闲", "松弛", "慢", "别太赶"]):
            return "轻松"
        return default

    def _heuristic_parse(self, user_input: str) -> Dict[str, Any]:
        parsed: Dict[str, Any] = {
            "preferences": [],
            "hotel_preferences": [],
            "stable_preferences": {},
            "temporary_constraints": {},
            "override_constraints": {"avoid_preferences": [], "avoid_pois": [], "avoid_categories": []},
            "clarification_questions": [],
        }
        city = re.search(r"(?:去|到|玩|逛|飞|想去|计划去)([\u4e00-\u9fa5]{2,8})(?:玩|旅游|旅行|过周末|几天|[，。,\s]|$)", user_input)
        if city:
            parsed["destination"] = city.group(1)
        days = re.search(r"([一二两三四五六七八九十\d]+)\s*(天|日)", user_input)
        if days:
            val = self._cn_num(days.group(1))
            if val:
                parsed["days"] = val
                parsed["temporary_constraints"]["days"] = val
        nights = re.search(r"([一二两三四五六七八九十\d]+)晚", user_input)
        if nights and "days" not in parsed:
            val = self._cn_num(nights.group(1))
            if val:
                parsed["days"] = val + 1
                parsed["temporary_constraints"]["days"] = val + 1
        budget, budget_min, budget_max = self._extract_budget(user_input)
        if budget is not None:
            parsed.update({"budget": budget, "budget_min": budget_min, "budget_max": budget_max})
            parsed["temporary_constraints"].update({"budget": budget, "budget_min": budget_min, "budget_max": budget_max})
        pref_map = {
            "美食": ["美食", "好吃", "小吃", "探店", "吃货", "本地特色", "特色餐厅"],
            "拍照": ["拍照", "出片", "打卡", "好看", "摄影", "拍写真"],
            "夜景": ["夜景", "夜游", "夜生活", "晚上逛"],
            "自然": ["自然", "山", "湖", "公园", "徒步", "风景", "海边"],
            "文化": ["博物馆", "展览", "古镇", "寺", "历史", "人文", "文化"],
            "亲子": ["亲子", "带娃", "小朋友", "儿童"],
            "购物": ["购物", "逛街", "商场", "买买买"],
            "休闲": ["放松", "松弛", "休闲", "度假", "躺平"],
        }
        for tag, words in pref_map.items():
            if any(word in user_input for word in words):
                parsed["preferences"].append(tag)
        hotel_map = {
            "地铁方便": ["地铁", "交通方便", "出行方便", "靠近地铁"],
            "市中心": ["市中心", "核心区", "繁华", "中心城区"],
            "安静": ["安静", "清静", "不吵"],
            "高性价比": ["性价比", "便宜点", "实惠", "划算"],
            "景观房": ["江景", "湖景", "景观房", "海景"],
        }
        for tag, words in hotel_map.items():
            if any(word in user_input for word in words):
                parsed["hotel_preferences"].append(tag)
        if any(word in user_input for word in ["别太赶", "轻松", "悠闲", "慢一点", "不要太赶", "松弛"]):
            parsed["pace"] = "轻松"
        elif any(word in user_input for word in ["紧凑", "多玩点", "安排满", "赶一点", "特种兵"]):
            parsed["pace"] = "紧凑"
        if any(word in user_input for word in ["室内", "下雨", "避雨", "不晒", "商场里"]):
            parsed["indoor_first"] = True
        if any(word in user_input for word in ["女朋友", "男朋友", "情侣", "对象"]):
            parsed["companions"] = ["情侣"]
        elif any(word in user_input for word in ["家人", "父母", "爸妈"]):
            parsed["companions"] = ["家人"]
        elif any(word in user_input for word in ["朋友", "闺蜜", "兄弟"]):
            parsed["companions"] = ["朋友"]
        elif any(word in user_input for word in ["孩子", "宝宝", "带娃"]):
            parsed["companions"] = ["亲子"]
        parsed["override_constraints"]["avoid_preferences"] = list(dict.fromkeys(re.findall(r"不想去([\u4e00-\u9fa5]{2,10})", user_input)))
        parsed["preferences"] = list(dict.fromkeys(parsed["preferences"]))
        parsed["hotel_preferences"] = list(dict.fromkeys(parsed["hotel_preferences"]))
        parsed["stable_preferences"] = {
            "preferences": parsed["preferences"],
            "hotel_preferences": parsed["hotel_preferences"],
            "pace": parsed.get("pace"),
            "indoor_first": parsed.get("indoor_first"),
        }
        return parsed

    def _merge_parsed(self, parsed: Dict[str, Any], heuristic: Dict[str, Any]) -> Dict[str, Any]:
        merged = dict(parsed)
        for field in ["destination", "days", "budget", "budget_min", "budget_max", "pace", "indoor_first", "companions", "travel_dates"]:
            if merged.get(field) in [None, "", [], {}] and heuristic.get(field) not in [None, "", [], {}]:
                merged[field] = heuristic[field]
        merged["preferences"] = list(dict.fromkeys([*[str(x) for x in merged.get("preferences", [])], *heuristic.get("preferences", [])]))
        merged["hotel_preferences"] = list(dict.fromkeys([*[str(x) for x in merged.get("hotel_preferences", [])], *heuristic.get("hotel_preferences", [])]))
        temp = dict(heuristic.get("temporary_constraints", {}))
        temp.update(dict(merged.get("temporary_constraints", {})))
        for k, v in heuristic.get("temporary_constraints", {}).items():
            if temp.get(k) in [None, "", [], {}]:
                temp[k] = v
        merged["temporary_constraints"] = temp
        stable = dict(heuristic.get("stable_preferences", {}))
        stable.update(dict(merged.get("stable_preferences", {})))
        stable["preferences"] = list(dict.fromkeys([*heuristic.get("stable_preferences", {}).get("preferences", []), *stable.get("preferences", [])]))
        stable["hotel_preferences"] = list(dict.fromkeys([*heuristic.get("stable_preferences", {}).get("hotel_preferences", []), *stable.get("hotel_preferences", [])]))
        if stable.get("pace") in [None, ""]:
            stable["pace"] = heuristic.get("stable_preferences", {}).get("pace")
        if stable.get("indoor_first") is None:
            stable["indoor_first"] = heuristic.get("stable_preferences", {}).get("indoor_first")
        merged["stable_preferences"] = stable
        override = {"avoid_preferences": [], "avoid_pois": [], "avoid_categories": []}
        override.update(dict(heuristic.get("override_constraints", {})))
        override.update(dict(merged.get("override_constraints", {})))
        for k in ["avoid_preferences", "avoid_pois", "avoid_categories"]:
            override[k] = list(dict.fromkeys([*heuristic.get("override_constraints", {}).get(k, []), *override.get(k, [])]))
        merged["override_constraints"] = override
        return merged

    def parse_natural_language(self, user_input: str, request_id: str, session_id: str, user_id: str | None = None, agent_context: AgentContext | None = None) -> NormalizedRequirement:
        start = time.perf_counter()
        ctx = agent_context.model_dump() if agent_context else {"memory_context": {}, "effective_constraints": {}, "recent_summary": {}}
        parsed: Dict[str, Any] = self._generate_parse_json(self._build_parse_prompt(user_input))
        parsed = self._merge_parsed(parsed, self._heuristic_parse(user_input))
        extracted_preferences = {"preferences": [str(x) for x in parsed.get("preferences", [])], "hotel_preferences": [str(x) for x in parsed.get("hotel_preferences", [])], "pace": parsed.get("pace"), "indoor_first": parsed.get("indoor_first")}
        stable_preferences = dict(parsed.get("stable_preferences", {}))
        stable_preferences.setdefault("preferences", extracted_preferences["preferences"])
        stable_preferences.setdefault("hotel_preferences", extracted_preferences["hotel_preferences"])
        if extracted_preferences.get("pace"):
            stable_preferences.setdefault("pace", extracted_preferences["pace"])
        if extracted_preferences.get("indoor_first") is not None:
            stable_preferences.setdefault("indoor_first", extracted_preferences["indoor_first"])
        temporary_constraints = dict(parsed.get("temporary_constraints", {}))
        override_constraints = dict(parsed.get("override_constraints", {}))
        override_constraints.setdefault("avoid_preferences", [])
        override_constraints.setdefault("avoid_pois", [])
        override_constraints.setdefault("avoid_categories", [])
        applied = self._apply_memory(ctx.get("memory_context", {}), ctx.get("effective_constraints", {}), {"explicit_preferences": extracted_preferences["preferences"], "explicit_hotel_preferences": extracted_preferences["hotel_preferences"], "explicit_pace": parsed.get("pace"), "explicit_indoor_first": parsed.get("indoor_first"), "override_constraints": override_constraints})
        parsed_requirement = ctx.get("memory_context", {}).get("session", {}).get("parsed_requirement", {})
        normalized_pace = self._normalize_pace(applied["pace"])

        default_days = self._as_int(temporary_constraints.get("days", parsed_requirement.get("days", 2)), 2)
        default_budget = self._as_float(temporary_constraints.get("budget", parsed_requirement.get("budget", 2500)), 2500.0)
        default_budget_min = self._as_float(temporary_constraints.get("budget_min", 2000), 2000.0)
        default_budget_max = self._as_float(temporary_constraints.get("budget_max", 10000), 10000.0)

        normalized = NormalizedRequirement(
            origin=str(parsed.get("origin", parsed_requirement.get("origin", "当前城市"))),
            destination=str(parsed.get("destination", parsed_requirement.get("destination", "杭州"))),
            days=self._as_int(parsed.get("days"), default_days),
            budget=self._as_float(parsed.get("budget"), default_budget),
            preferences=applied["preferences"],
            pace=normalized_pace,
            indoor_first=applied["indoor_first"],
            session_id=session_id,
            user_id=user_id,
            budget_min=self._as_float(parsed.get("budget_min"), default_budget_min),
            budget_max=self._as_float(parsed.get("budget_max"), default_budget_max),
            companions=[str(x) for x in parsed.get("companions", ["朋友"])],
            hotel_preferences=applied["hotel_preferences"],
            travel_dates=parsed.get("travel_dates"),
            raw_user_input=user_input,
            clarification_needed=bool(parsed.get("clarification_needed", False)),
            clarification_questions=[str(x) for x in parsed.get("clarification_questions", [])],
            locked_constraints=ctx.get("effective_constraints", {}).get("locked_constraints", {}),
            memory_summary={"has_preference_memory": bool(ctx.get("memory_context", {}).get("preference")), "has_summary_memory": bool(ctx.get("recent_summary", {}))},
            extracted_preferences=extracted_preferences,
            temporary_constraints=temporary_constraints,
            stable_preferences=stable_preferences,
            override_constraints=override_constraints,
            memory_applied={"preference_memory_hit": bool(ctx.get("memory_context", {}).get("preference")), "summary_memory_hit": bool(ctx.get("recent_summary", {})), "applied_fields": [k for k in ["preferences", "hotel_preferences", "pace", "indoor_first"] if applied["inherited"].get(k) not in [None, [], {}]]},
            inherited_preferences=applied["inherited"],
            overridden_preferences=applied["overridden"],
        )
        memory_service.save_requirement(session_id=session_id, user_id=user_id, parsed_requirement=normalized.model_dump())
        merged_memory = memory_service.update_preferences(session_id=session_id, user_id=user_id, extracted_preferences=stable_preferences)
        self.logger.info(f"preference_resolution session_id={session_id} inherited={applied['inherited']} overridden={applied['overridden']} merged={merged_memory}")
        log_event(logger=self.logger, request_id=request_id, agent_name="RequirementAgent", action="parse_natural_language", duration_ms=(time.perf_counter() - start) * 1000, input_summary={"session_id": session_id, "user_id": user_id, "context_sections": agent_context.visible_sections if agent_context else [], "langchain_mode": self._use_langchain_llm()}, output_summary={"destination": normalized.destination, "days": normalized.days, "budget": normalized.budget, "clarification_needed": normalized.clarification_needed})
        return normalized

    def run(self, request: PlanRequest, request_id: str, agent_context: AgentContext | None = None) -> NormalizedRequirement:
        start = time.perf_counter()
        ctx = agent_context.model_dump() if agent_context else {"memory_context": {}, "effective_constraints": {}}
        extraction = self._build_structured_extraction(request)
        applied = self._apply_memory(ctx.get("memory_context", {}), ctx.get("effective_constraints", {}), extraction)
        normalized = NormalizedRequirement(origin=request.origin, destination=request.destination, days=request.days, budget=request.budget, preferences=applied["preferences"], pace=applied["pace"], indoor_first=applied["indoor_first"], session_id=request.session_id, user_id=request.user_id, budget_min=request.budget * 0.9, budget_max=request.budget * 1.1, companions=["朋友"], hotel_preferences=applied["hotel_preferences"], locked_constraints=ctx.get("effective_constraints", {}).get("locked_constraints", {}), memory_summary={"has_preference_memory": bool(ctx.get("memory_context", {}).get("preference")), "has_summary_memory": bool(ctx.get("recent_summary", {}))}, extracted_preferences={"preferences": extraction["explicit_preferences"], "hotel_preferences": extraction["explicit_hotel_preferences"], "pace": extraction["explicit_pace"], "indoor_first": extraction["explicit_indoor_first"]}, temporary_constraints=extraction["temporary_constraints"], stable_preferences=extraction["stable_preferences"], override_constraints=extraction["override_constraints"], memory_applied={"preference_memory_hit": bool(ctx.get("memory_context", {}).get("preference")), "summary_memory_hit": bool(ctx.get("recent_summary", {})), "applied_fields": [k for k in ["preferences", "hotel_preferences", "pace", "indoor_first"] if applied["inherited"].get(k) not in [None, [], {}]]}, inherited_preferences=applied["inherited"], overridden_preferences=applied["overridden"])
        memory_service.save_requirement(session_id=request.session_id, user_id=request.user_id, parsed_requirement=normalized.model_dump())
        memory_service.update_preferences(session_id=request.session_id, user_id=request.user_id, extracted_preferences=extraction["stable_preferences"])
        self.logger.info(f"preference_resolution session_id={request.session_id} inherited={applied['inherited']} overridden={applied['overridden']}")
        log_event(logger=self.logger, request_id=request_id, agent_name="RequirementAgent", action="normalize_request", duration_ms=(time.perf_counter() - start) * 1000, input_summary={"session_id": request.session_id, "user_id": request.user_id, "destination": request.destination, "context_sections": agent_context.visible_sections if agent_context else []}, output_summary={"days": normalized.days, "budget": normalized.budget, "preferences_count": len(normalized.preferences)})
        return normalized
