"""Deterministic trigger policy for autonomous cognition cycles."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable

from .engine import CognitiveSovereigntyEngine
from .models import AgentState


@dataclass(frozen=True)
class CycleDecision:
    mode: str
    reason: str


class CognitiveScheduler:
    """Chooses when/how to think; the model chooses the cognitive content."""

    def choose(self, state: AgentState) -> CycleDecision:
        unresolved = [t for t in state.tensions if t.resolution_status != "resolved"]
        if unresolved and max(t.strength for t in unresolved) >= 0.65:
            return CycleDecision("deliberation", "strong unresolved tension")
        if state.social.novelty_need >= 0.65:
            return CycleDecision("cognitive_drift", "high novelty drive")
        if state.episode_count > 0 and state.episode_count % 4 == 0:
            return CycleDecision("heterodox_exploration", "periodic protected divergent search")
        return CycleDecision("deliberation", "highest current interest")

    def run_cycle(self, engine: CognitiveSovereigntyEngine, agent_id: str) -> dict:
        decision = self.choose(engine.state(agent_id))
        result = engine.think(agent_id, decision.mode)
        result["scheduler_reason"] = decision.reason
        return result

    def run(
        self, engine: CognitiveSovereigntyEngine, agent_id: str, cycles: int,
        interval_seconds: float, on_result: Callable[[dict], None] | None = None,
    ) -> None:
        for index in range(cycles):
            result = self.run_cycle(engine, agent_id)
            if on_result:
                on_result(result)
            if index + 1 < cycles:
                time.sleep(max(0.0, interval_seconds))
