from __future__ import annotations

import time
from dataclasses import dataclass, field
from threading import Lock
from typing import Any, Dict, List


@dataclass
class AgentMetric:
    agent_name: str
    duration_ms: float


@dataclass
class ToolMetric:
    tool_name: str
    calls: int = 0
    duration_ms: float = 0.0


@dataclass
class RunMetric:
    request_id: str
    route: str
    started_at: float
    ended_at: float = 0.0
    duration_ms: float = 0.0

    workflow_steps: List[str] = field(default_factory=list)
    agents: List[AgentMetric] = field(default_factory=list)
    tools: Dict[str, ToolMetric] = field(default_factory=dict)

    budget_constraints_ok: bool = True
    itinerary_constraints_ok: bool = True
    itinerary_days_completeness: float = 0.0
    replan_duration_ms: float = 0.0

    daily_commute_minutes: Dict[int, int] = field(default_factory=dict)
    transport_fallback_triggered: bool = False
    weather_fallback_triggered: bool = False
    hotel_fallback_triggered: bool = False
    search_fallback_triggered: bool = False


class MetricsCollector:
    def __init__(self) -> None:
        self._runs: Dict[str, RunMetric] = {}
        self._lock = Lock()

    def start_run(self, request_id: str, route: str) -> None:
        with self._lock:
            self._runs[request_id] = RunMetric(
                request_id=request_id,
                route=route,
                started_at=time.perf_counter(),
            )

    def end_run(self, request_id: str) -> Dict[str, Any]:
        with self._lock:
            run = self._runs[request_id]
            run.ended_at = time.perf_counter()
            run.duration_ms = (run.ended_at - run.started_at) * 1000
            return self._to_dict(run)

    def record_workflow_step(self, request_id: str, step: str) -> None:
        with self._lock:
            run = self._runs.get(request_id)
            if not run:
                return
            run.workflow_steps.append(step)

    def record_agent(self, request_id: str, agent_name: str, duration_ms: float) -> None:
        with self._lock:
            run = self._runs.get(request_id)
            if not run:
                return
            run.agents.append(AgentMetric(agent_name=agent_name, duration_ms=round(duration_ms, 2)))

    def record_tool(self, request_id: str, tool_name: str, duration_ms: float) -> None:
        with self._lock:
            run = self._runs.get(request_id)
            if not run:
                return
            metric = run.tools.get(tool_name)
            if not metric:
                metric = ToolMetric(tool_name=tool_name)
                run.tools[tool_name] = metric
            metric.calls += 1
            metric.duration_ms = round(metric.duration_ms + duration_ms, 2)

    def record_constraints(
        self,
        request_id: str,
        budget_ok: bool,
        itinerary_ok: bool,
        day_completeness: float,
    ) -> None:
        with self._lock:
            run = self._runs.get(request_id)
            if not run:
                return
            run.budget_constraints_ok = budget_ok
            run.itinerary_constraints_ok = itinerary_ok
            run.itinerary_days_completeness = round(day_completeness, 2)

    def record_replan_duration(self, request_id: str, duration_ms: float) -> None:
        with self._lock:
            run = self._runs.get(request_id)
            if not run:
                return
            run.replan_duration_ms = round(duration_ms, 2)

    def record_daily_commute(self, request_id: str, day: int, minutes: int) -> None:
        with self._lock:
            run = self._runs.get(request_id)
            if not run:
                return
            run.daily_commute_minutes[int(day)] = int(minutes)

    def record_transport_fallback(self, request_id: str, triggered: bool) -> None:
        with self._lock:
            run = self._runs.get(request_id)
            if not run:
                return
            run.transport_fallback_triggered = run.transport_fallback_triggered or bool(triggered)

    def record_weather_fallback(self, request_id: str, triggered: bool) -> None:
        with self._lock:
            run = self._runs.get(request_id)
            if not run:
                return
            run.weather_fallback_triggered = run.weather_fallback_triggered or bool(triggered)

    def record_hotel_fallback(self, request_id: str, triggered: bool) -> None:
        with self._lock:
            run = self._runs.get(request_id)
            if not run:
                return
            run.hotel_fallback_triggered = run.hotel_fallback_triggered or bool(triggered)

    def record_search_fallback(self, request_id: str, triggered: bool) -> None:
        with self._lock:
            run = self._runs.get(request_id)
            if not run:
                return
            run.search_fallback_triggered = run.search_fallback_triggered or bool(triggered)

    def _to_dict(self, run: RunMetric) -> Dict[str, Any]:
        fallback_used = {
            "weather": run.weather_fallback_triggered,
            "transport": run.transport_fallback_triggered,
            "hotel": run.hotel_fallback_triggered,
            "search": run.search_fallback_triggered,
        }

        return {
            "request_id": run.request_id,
            "route": run.route,
            "duration_ms": round(run.duration_ms, 2),
            "workflow_steps": run.workflow_steps,
            "agents": [
                {"agent_name": x.agent_name, "duration_ms": x.duration_ms} for x in run.agents
            ],
            "tools": {
                name: {"calls": metric.calls, "duration_ms": metric.duration_ms}
                for name, metric in run.tools.items()
            },
            "tool_calls": sum(metric.calls for metric in run.tools.values()),
            "fallback_used": fallback_used,
            "budget_constraints_ok": run.budget_constraints_ok,
            "itinerary_constraints_ok": run.itinerary_constraints_ok,
            "itinerary_days_completeness": run.itinerary_days_completeness,
            "constraint_satisfaction": {
                "budget_ok": run.budget_constraints_ok,
                "itinerary_ok": run.itinerary_constraints_ok,
                "day_completeness": run.itinerary_days_completeness,
            },
            "replan_duration_ms": run.replan_duration_ms,
            "daily_commute_minutes": run.daily_commute_minutes,
            "transport_fallback_triggered": run.transport_fallback_triggered,
        }


metrics_collector = MetricsCollector()
