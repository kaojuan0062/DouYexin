from __future__ import annotations

from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field

ContextScope = Literal[
    "requirement",
    "query_rewrite",
    "research",
    "planner",
    "replanner",
]


class AgentContext(BaseModel):
    scope: ContextScope
    current_input: Dict[str, Any] = Field(default_factory=dict)
    memory_context: Dict[str, Any] = Field(default_factory=dict)
    effective_constraints: Dict[str, Any] = Field(default_factory=dict)
    recent_summary: Dict[str, Any] = Field(default_factory=dict)
    optional_research_cache: Dict[str, Any] = Field(default_factory=dict)
    visible_sections: List[str] = Field(default_factory=list)

    def summary(self) -> Dict[str, Any]:
        return {
            "scope": self.scope,
            "visible_sections": self.visible_sections,
            "memory_keys": sorted(self.memory_context.keys()),
            "effective_constraint_keys": sorted(self.effective_constraints.keys()),
            "recent_summary_keys": sorted(self.recent_summary.keys()),
            "research_cache_keys": sorted(self.optional_research_cache.keys()),
        }
