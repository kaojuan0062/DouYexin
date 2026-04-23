from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any

from memory.preference_store import PreferenceMemoryStore
from memory.research_store import ResearchMemoryStore
from memory.session_store import SessionMemoryStore
from memory.summary_store import SummaryMemoryStore
from utils.logger import get_logger


class MemoryService:
    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self.session_store = SessionMemoryStore()
        self.preference_store = PreferenceMemoryStore()
        self.summary_store = SummaryMemoryStore()
        self.research_store = ResearchMemoryStore()
        self.research_freshness_window = timedelta(minutes=30)

    def _log_read(self, memory_type: str, session_id: str, hit: bool, user_id: str | None = None) -> None:
        self.logger.info(f"memory_read type={memory_type} session_id={session_id} user_id={user_id or '-'} hit={str(hit).lower()}")

    def _log_write(self, memory_type: str, session_id: str, keys: list[str], user_id: str | None = None) -> None:
        self.logger.info(f"memory_write type={memory_type} session_id={session_id} user_id={user_id or '-'} keys={','.join(keys)}")

    def load_context(self, session_id: str, user_id: str | None = None) -> dict[str, dict[str, Any]]:
        s = self.session_store.get(session_id=session_id, user_id=user_id)
        p = self.preference_store.get(session_id=session_id, user_id=user_id)
        m = self.summary_store.get(session_id=session_id, user_id=user_id)
        r = self.research_store.get(session_id=session_id, user_id=user_id)
        self._log_read("session", session_id, bool(s), user_id)
        self._log_read("preference", session_id, bool(p), user_id)
        self._log_read("summary", session_id, bool(m), user_id)
        self._log_read("research", session_id, bool(r), user_id)
        return {
            "session": deepcopy(s.payload if s else {}),
            "preference": deepcopy(p.payload if p else {}),
            "summary": deepcopy(m.payload if m else {}),
            "research": deepcopy(r.payload if r else {}),
        }

    def merge_preferences(self, existing: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
        merged = deepcopy(existing)
        merged["preferences"] = list(dict.fromkeys([*existing.get("preferences", []), *new.get("preferences", [])]))
        merged["hotel_preferences"] = list(dict.fromkeys([*existing.get("hotel_preferences", []), *new.get("hotel_preferences", [])]))
        merged["pace"] = new.get("pace") or existing.get("pace")
        if new.get("indoor_first") is not None:
            merged["indoor_first"] = bool(new["indoor_first"])
        elif existing.get("indoor_first") is not None:
            merged["indoor_first"] = bool(existing["indoor_first"])
        return merged

    def resolve_preference_conflicts(self, existing: dict[str, Any], current_request: dict[str, Any]) -> dict[str, Any]:
        overridden: list[dict[str, Any]] = []
        inherited: dict[str, Any] = {}
        old_prefs = existing.get("preferences", [])
        avoid = current_request.get("override_constraints", {}).get("avoid_preferences", [])
        current_prefs = current_request.get("explicit_preferences", [])
        kept = [x for x in old_prefs if x not in avoid]
        if kept:
            inherited["preferences"] = [x for x in kept if x not in current_prefs]
        for item in avoid:
            if item in old_prefs:
                overridden.append({"type": "preference", "value": item, "reason": "overridden_by_current_request"})
        if existing.get("pace") and current_request.get("explicit_pace") and existing.get("pace") != current_request.get("explicit_pace"):
            overridden.append({"type": "pace", "value": existing.get("pace"), "reason": f"current_request={current_request.get('explicit_pace')}"})
        elif existing.get("pace") and not current_request.get("explicit_pace"):
            inherited["pace"] = existing.get("pace")
        hotels = [x for x in existing.get("hotel_preferences", []) if x not in current_request.get("explicit_hotel_preferences", [])]
        if hotels:
            inherited["hotel_preferences"] = hotels
        if existing.get("indoor_first") is not None and current_request.get("explicit_indoor_first") is None:
            inherited["indoor_first"] = existing.get("indoor_first")
        elif existing.get("indoor_first") is not None and current_request.get("explicit_indoor_first") is not None and bool(existing.get("indoor_first")) != bool(current_request.get("explicit_indoor_first")):
            overridden.append({"type": "indoor_first", "value": existing.get("indoor_first"), "reason": f"current_request={current_request.get('explicit_indoor_first')}"})
        return {"inherited_preferences": inherited, "overridden_preferences": overridden}

    def save_requirement(self, session_id: str, parsed_requirement: dict[str, Any], user_id: str | None = None) -> None:
        payload = {"current_user_input": parsed_requirement.get("raw_user_input"), "parsed_requirement": deepcopy(parsed_requirement), "last_destination": parsed_requirement.get("destination"), "last_budget": parsed_requirement.get("budget"), "last_days": parsed_requirement.get("days")}
        self.session_store.upsert(session_id=session_id, user_id=user_id, payload=payload)
        self._log_write("session", session_id, list(payload.keys()), user_id)

    def save_itinerary(self, session_id: str, itinerary: dict[str, Any], user_id: str | None = None) -> None:
        payload = {"current_itinerary": deepcopy(itinerary), "last_itinerary_summary": itinerary.get("summary", ""), "locked_constraints": {"hotel_locked": bool(itinerary.get("hotel_recommendations")), "budget_locked": not bool(itinerary.get("over_budget_flag", False))}}
        self.session_store.upsert(session_id=session_id, user_id=user_id, payload=payload)
        self._log_write("session", session_id, list(payload.keys()), user_id)

    def _freshness_tag(self, generated_at: datetime) -> str:
        age = datetime.now(timezone.utc) - generated_at
        if age <= timedelta(minutes=10):
            return "fresh"
        if age <= self.research_freshness_window:
            return "warm"
        return "stale"

    def _parse_generated_at(self, value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None

    def save_research_results(self, session_id: str, research_result: dict[str, Any], user_id: str | None = None) -> None:
        now = datetime.now(timezone.utc)
        payload = {
            "normalized_requirements_snapshot": deepcopy(research_result.get("normalized_requirements_snapshot", {})),
            "rewritten_queries": deepcopy(research_result.get("rewritten_queries", {})),
            "search_results_summary": deepcopy(research_result.get("search_results_summary", {})),
            "candidate_pool": deepcopy(research_result.get("candidate_pool", {})),
            "ranked_candidates": deepcopy(research_result.get("ranked_candidates", {})),
            "generated_at": now.isoformat(),
            "freshness_tag": research_result.get("freshness_tag") or self._freshness_tag(now),
        }
        self.research_store.upsert(session_id=session_id, user_id=user_id, payload=payload)
        self._log_write("research", session_id, list(payload.keys()), user_id)

    def evaluate_research_reuse(self, session_id: str, requirement: dict[str, Any], rewritten_queries: dict[str, list[str]], user_id: str | None = None, replan_reason: str | None = None) -> dict[str, Any]:
        record = self.research_store.get(session_id=session_id, user_id=user_id)
        cached = deepcopy(record.payload if record else {})
        snapshot = cached.get("normalized_requirements_snapshot", {})
        generated_at = self._parse_generated_at(cached.get("generated_at"))
        freshness_tag = self._freshness_tag(generated_at) if generated_at else "stale"
        same_destination = bool(snapshot) and snapshot.get("destination") == requirement.get("destination")
        similar_days = bool(snapshot) and abs(int(snapshot.get("days", 0)) - int(requirement.get("days", 0))) <= 1
        a = set(str(x) for x in snapshot.get("preferences", []))
        b = set(str(x) for x in requirement.get("preferences", []))
        similarity = 1.0 if not a and not b else len(a & b) / max(len(a | b), 1)
        within_window = freshness_tag != "stale"
        hit = False
        strategy = "full_refresh"
        refreshed: dict[str, list[str]] = {}
        if same_destination and similar_days and similarity >= 0.5 and within_window:
            hit = True
            strategy = "full_reuse"
        elif same_destination and within_window and replan_reason == "rain":
            hit = True
            strategy = "partial_refresh"
            dest = requirement.get("destination", "")
            refreshed = {"poi_queries": [f"{dest} 雨天 室内 景点", f"{dest} 下雨 展览 博物馆"], "food_queries": [f"{dest} 雨天 室内 美食 商场"]}
        elif same_destination and similar_days and similarity >= 0.3 and within_window:
            hit = True
            strategy = "partial_refresh"
            refreshed = {k: rewritten_queries.get(k, [])[:1] for k in rewritten_queries}
        reused = sum(len(v) for v in cached.get("candidate_pool", {}).values()) if hit else 0
        self.logger.info(f"research_memory_evaluated session_id={session_id} user_id={user_id or '-'} hit={str(hit).lower()} strategy={strategy} same_destination={str(same_destination).lower()} similar_days={str(similar_days).lower()} preference_similarity={similarity:.2f} freshness_tag={freshness_tag} reused_candidates_count={reused} refreshed_queries={refreshed}")
        return {"hit": hit, "cache_strategy": strategy, "reused_candidates_count": reused, "refreshed_queries": refreshed, "freshness_tag": freshness_tag, "cached": cached}

    def update_preferences(self, session_id: str, extracted_preferences: dict[str, Any], user_id: str | None = None) -> dict[str, Any]:
        current = self.preference_store.get(session_id=session_id, user_id=user_id)
        existing = deepcopy(current.payload if current else {})
        merged = self.merge_preferences(existing=existing, new=extracted_preferences)
        merged["stable_preferences"] = list(dict.fromkeys([*merged.get("preferences", []), *merged.get("hotel_preferences", [])]))
        self.preference_store.upsert(session_id=session_id, user_id=user_id, payload=merged)
        self._log_write("preference", session_id, list(merged.keys()), user_id)
        self.logger.info(f"memory_preferences_extracted session_id={session_id} user_id={user_id or '-'} new_preferences={extracted_preferences}")
        return merged

    def build_plan_summary(self, itinerary: dict[str, Any], requirement: dict[str, Any], confirmed_constraints: dict[str, Any], locked_days: list[int], rationale_summary: list[str]) -> dict[str, Any]:
        hotels = itinerary.get("hotel_recommendations", [])
        area = str(hotels[0].get("area", "")) if hotels else ""
        clusters = [str(day.get("activities", [""])[0]) for day in itinerary.get("daily_plan", []) if day.get("activities")][:3]
        rejected = ["过远景点"]
        if itinerary.get("over_budget_flag"):
            rejected.insert(0, "高消费餐厅")
        adjustable = [int(day.get("day")) for day in itinerary.get("daily_plan", []) if int(day.get("day", 0)) not in locked_days]
        summary = {"last_plan_summary": itinerary.get("summary", ""), "confirmed_constraints": confirmed_constraints, "locked_days": locked_days, "selected_hotel_area": area, "preferred_poi_clusters": clusters, "rejected_options": rejected, "rationale_summary": rationale_summary, "adjustable_days": adjustable}
        self.logger.info(f"summary_generated locked_days={locked_days} confirmed_constraints={confirmed_constraints} adjustable_days={adjustable}")
        return summary

    def save_summary(self, session_id: str, summary: dict[str, Any], user_id: str | None = None) -> None:
        self.summary_store.upsert(session_id=session_id, user_id=user_id, payload=deepcopy(summary))
        self._log_write("summary", session_id, list(summary.keys()), user_id)

    def save_replan_request(self, session_id: str, replan_request: dict[str, Any], user_id: str | None = None) -> None:
        payload = {"last_replan_request": deepcopy(replan_request)}
        self.session_store.upsert(session_id=session_id, user_id=user_id, payload=payload)
        self._log_write("session", session_id, list(payload.keys()), user_id)

    def get_effective_constraints(self, session_id: str, user_id: str | None = None) -> dict[str, Any]:
        context = self.load_context(session_id=session_id, user_id=user_id)
        p = context["preference"]
        s = context["summary"]
        ss = context["session"]
        constraints = {"preferences": p.get("preferences", []), "hotel_preferences": p.get("hotel_preferences", []), "pace": p.get("pace") or s.get("confirmed_constraints", {}).get("pace"), "indoor_first": p.get("indoor_first"), "locked_constraints": s.get("confirmed_constraints") or s.get("locked_constraints") or ss.get("locked_constraints", {}), "confirmed_constraints": s.get("confirmed_constraints", {}), "current_itinerary": ss.get("current_itinerary", {}), "stable_preferences": p.get("stable_preferences", []), "locked_days": s.get("locked_days", []), "selected_hotel_area": s.get("selected_hotel_area", ""), "preferred_poi_clusters": s.get("preferred_poi_clusters", []), "rejected_options": s.get("rejected_options", []), "rationale_summary": s.get("rationale_summary", [])}
        self.logger.info(f"memory_effective_constraints session_id={session_id} user_id={user_id or '-'} has_preference={str(bool(p)).lower()} has_summary={str(bool(s)).lower()}")
        return constraints


memory_service = MemoryService()

