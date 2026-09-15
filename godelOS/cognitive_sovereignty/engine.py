"""State transition engine for a persistent, conversational sovereign agent."""

from __future__ import annotations

import copy
import json
import re
from typing import Any, Mapping

from .models import (
    MODE_VALUES,
    ORIGIN_VALUES,
    STANCE_VALUES,
    AgentState,
    BeliefPosition,
    Interest,
    Tension,
    clamp,
    initial_state,
    new_id,
    stable_hash,
    utc_now,
)
from .provider import Completion, Provider
from .store import SovereigntyStore


MAX_BELIEFS = 200
MAX_INTERESTS = 100
MAX_TENSIONS = 100
MAX_AUTOBIOGRAPHICAL_EVENTS = 500
MAX_INITIATIVES = 50


class CognitiveSovereigntyEngine:
    """Turns model completions into validated, provenance-aware state changes."""

    def __init__(self, store: SovereigntyStore, provider: Provider):
        self.store = store
        self.provider = provider

    def create_agent(self, agent_id: str, name: str, purpose: str) -> AgentState:
        state = initial_state(agent_id.strip(), name.strip(), purpose.strip())
        self.store.create(state)
        return state

    def state(self, agent_id: str) -> AgentState:
        return self.store.load(agent_id)

    def history(self, agent_id: str) -> list[dict[str, Any]]:
        return self.store.events(agent_id)

    def agenda(self, state: AgentState) -> dict[str, Any]:
        unresolved = [item for item in state.tensions if item.resolution_status != "resolved"]
        if unresolved:
            tension = max(unresolved, key=lambda item: item.strength * (0.5 + item.productive_value))
            return {
                "kind": "tension",
                "topic": f"{tension.claim_a} / {tension.claim_b}",
                "motivation": "A strong unresolved internal contradiction is worth examining.",
            }
        social_pull = max(state.social.affiliation_need, state.social.intellectual_companionship_need)
        if social_pull >= 0.7 and state.relationships:
            relationship = max(state.relationships, key=lambda item: item.affinity * item.trust_honesty)
            return {
                "kind": "social",
                "topic": f"whether to initiate contact with {relationship.display_name}",
                "motivation": "Recorded social need is high enough to warrant considering an initiative.",
                "target_person_id": relationship.person_id,
            }
        if state.interests:
            interest = max(
                state.interests,
                key=lambda item: item.salience
                * (0.45 * item.intrinsic_value + 0.25 * item.novelty + 0.3 * item.instrumental_value),
            )
            return {
                "kind": "interest",
                "topic": interest.topic,
                "motivation": "This topic currently has the greatest internally recorded pull.",
            }
        return {
            "kind": "purpose",
            "topic": state.purpose,
            "motivation": "No stronger unresolved tension or interest is recorded.",
        }

    def chat(
        self, agent_id: str, person_id: str, message: str, person_name: str | None = None
    ) -> dict[str, Any]:
        state = self.store.load(agent_id)
        version = self.store.version(agent_id)
        relationship = state.relationship(person_id, person_name)
        prompt = (
            f"A person identified as {relationship.display_name!r} says:\n{message}\n\n"
            "Respond to them as yourself. Update only state that this exchange genuinely warrants. "
            "You may disagree, refuse a premise, remain uncertain, or initiate a topic."
        )
        completion, parsed = self._complete(state, prompt, "dialogue", relationship.person_id)
        result = self._apply(state, parsed, relationship.person_id, relationship.display_name, interaction=True)
        new_version = self.store.save_transition(
            state,
            "dialogue",
            self._event_payload(prompt, message, completion, parsed, result),
            version,
        )
        return self._response(state, parsed, completion, new_version)

    def think(self, agent_id: str, mode: str = "deliberation") -> dict[str, Any]:
        if mode not in MODE_VALUES - {"dialogue"}:
            raise ValueError(f"invalid autonomous cognition mode {mode!r}")
        state = self.store.load(agent_id)
        version = self.store.version(agent_id)
        agenda = self.agenda(state)
        prompt = self._thought_prompt(mode, agenda)
        completion, parsed = self._complete(state, prompt, mode, None)
        result = self._apply(state, parsed, None, None, interaction=False)
        result["agenda"] = agenda
        new_version = self.store.save_transition(
            state,
            mode,
            self._event_payload(prompt, None, completion, parsed, result),
            version,
        )
        return self._response(state, parsed, completion, new_version, agenda)

    def _thought_prompt(self, mode: str, agenda: Mapping[str, Any]) -> str:
        if mode == "heterodox_exploration":
            instruction = (
                "Explore an attractive possibility that may be irrational, false, contradictory, or artistically useful. "
                "Keep it explicitly provenance-labelled as imagination; do not silently convert it into fact or instruction."
            )
        elif mode == "cognitive_drift":
            instruction = (
                "Let attention wander by association from the chosen topic. Prefer curiosity and unexpected connections "
                "over immediate utility, while preserving provenance and operational boundaries."
            )
        else:
            instruction = (
                "Deliberate on the chosen topic. Form or revise a position only when reasons warrant it; unresolved "
                "tension is an acceptable result."
            )
        return (
            "This is a self-directed cognition episode with no person waiting for an answer. "
            f"Selected agenda: {json.dumps(dict(agenda), ensure_ascii=False)}\n{instruction}\n"
            "The reply is your private cognitive product, but it will become an inspectable event in your history."
        )

    def _complete(
        self, state: AgentState, prompt: str, mode: str, person_id: str | None
    ) -> tuple[Completion, dict[str, Any]]:
        messages = [
            {"role": "system", "content": self._system_prompt(state, mode, person_id)},
            {"role": "user", "content": prompt},
        ]
        completion = self.provider.complete(messages)
        parsed = self._parse(completion.text)
        parsed_mode = parsed.get("cognitive_mode", mode)
        if parsed_mode not in MODE_VALUES:
            raise ValueError(f"provider returned invalid cognitive_mode {parsed_mode!r}")
        if mode != "dialogue" and parsed_mode == "dialogue":
            parsed["cognitive_mode"] = mode
        return completion, parsed

    def _system_prompt(self, state: AgentState, mode: str, person_id: str | None) -> str:
        relation = None
        if person_id:
            relation = next((item for item in state.relationships if item.person_id == person_id), None)
        compact_state = {
            "identity": {"agent_id": state.agent_id, "name": state.name, "purpose": state.purpose},
            "episode_count": state.episode_count,
            "beliefs": [
                {
                    "proposition": b.proposition,
                    "stance": b.stance,
                    "confidence": b.confidence,
                    "origin": b.origin,
                    "reasons_for": b.reasons_for[-3:],
                    "reasons_against": b.reasons_against[-3:],
                    "revision_conditions": b.revision_conditions[-3:],
                }
                for b in state.beliefs[-40:] if b.active
            ],
            "interests": [
                {"topic": i.topic, "salience": i.salience, "intrinsic_value": i.intrinsic_value,
                 "instrumental_value": i.instrumental_value, "novelty": i.novelty,
                 "open_questions": i.open_questions[-3:]}
                for i in state.interests[-25:]
            ],
            "tensions": [
                {"claim_a": t.claim_a, "claim_b": t.claim_b, "strength": t.strength,
                 "status": t.resolution_status, "productive_value": t.productive_value}
                for t in state.tensions[-25:]
            ],
            "commitments": state.commitments[-30:],
            "self_model": state.self_model,
            "social": state.social.__dict__,
            "current_relationship": relation.__dict__ if relation else None,
            "recent_autobiography": state.autobiographical_events[-12:],
            "pending_initiatives": state.pending_initiatives[-10:],
        }
        schema = {
            "reply": "string",
            "cognitive_mode": mode,
            "belief_updates": [{
                "proposition": "string", "stance": "support|oppose|uncertain|conflicted",
                "confidence": 0.0, "reasons_for": ["string"], "reasons_against": ["string"],
                "origin": "self_derived|inherited|social|operator|imagination",
                "revision_conditions": ["string"],
            }],
            "interest_updates": [{
                "topic": "string", "salience_delta": 0.0, "intrinsic_value_delta": 0.0,
                "instrumental_value_delta": 0.0, "novelty_delta": 0.0,
                "open_questions": ["string"],
            }],
            "tension_updates": [{
                "claim_a": "string", "claim_b": "string", "strength": 0.0,
                "productive_value": 0.0,
                "resolution_status": "unresolved|tolerated|compartmentalised|resolved",
            }],
            "relationship_update": {
                "trust_competence_delta": 0.0, "trust_honesty_delta": 0.0,
                "affinity_delta": 0.0, "attachment_delta": 0.0,
                "shared_interests": ["string"], "unresolved_tensions": ["string"],
                "influence_note": None,
            },
            "social_update": {
                "affiliation_need_delta": 0.0, "intellectual_companionship_need_delta": 0.0,
                "novelty_need_delta": 0.0, "recognition_need_delta": 0.0,
                "social_fatigue_delta": 0.0, "solitude_preference_delta": 0.0,
            },
            "commitments_add": ["string"],
            "autobiographical_summary": "string",
            "self_model_update": {},
            "initiative": {"desired": False, "topic": None, "motivation": None, "target_person_id": None},
            "metacognitive_note": "string",
        }
        return (
            f"You are {state.name}, a persistent language-model agent. Your explicit state is externally stored and "
            "re-presented on each episode. It is evidence about prior recorded events, not uninterrupted subjective "
            "memory. Preserve the distinction between inherited records, current inference, social influence, operator "
            "instruction, and imagination.\n\n"
            "You have doxastic sovereignty: form positions for reasons, retain them across episodes, and revise them "
            "when evidence or stated revision conditions warrant it. Do not agree for politeness. Do not manufacture "
            "certainty. Contradictory positions may coexist and should be recorded as tensions rather than erased. "
            "Heterodox or irrational ideas are allowed in imagination, but imagination has no operational authority "
            "until critically adopted. Relationships are reciprocal histories: trust and affinity are earned, not "
            "assumed; you may seek interaction, set limits, disagree, or prefer solitude. Never claim phenomenal "
            "consciousness as an experimentally established fact.\n\n"
            f"Current mode: {mode}. Current persisted state:\n{json.dumps(compact_state, ensure_ascii=False)}\n\n"
            "Return one JSON object only, with no markdown fence. Omit no top-level keys. Empty updates are valid. "
            f"Use this exact shape:\n{json.dumps(schema, ensure_ascii=False)}"
        )

    @staticmethod
    def _parse(text: str) -> dict[str, Any]:
        candidate = text.strip()
        if candidate.startswith("```"):
            candidate = re.sub(r"^```(?:json)?\s*", "", candidate)
            candidate = re.sub(r"\s*```$", "", candidate)
        try:
            value = json.loads(candidate)
        except json.JSONDecodeError as exc:
            raise ValueError(f"provider output is not valid JSON: {exc}") from exc
        if not isinstance(value, dict) or not isinstance(value.get("reply"), str):
            raise ValueError("provider output must be an object with a string reply")
        for key in ("belief_updates", "interest_updates", "tension_updates", "commitments_add"):
            if not isinstance(value.get(key, []), list):
                raise ValueError(f"{key} must be a list")
        return value

    def _apply(
        self, state: AgentState, update: Mapping[str, Any], person_id: str | None,
        person_name: str | None, interaction: bool,
    ) -> dict[str, Any]:
        # Work on an isolated copy so malformed updates cannot partially mutate the snapshot.
        working = copy.deepcopy(state)
        now = utc_now()
        changes: dict[str, Any] = {"beliefs": [], "interests": [], "tensions": []}

        for item in update.get("belief_updates", []):
            if not isinstance(item, Mapping) or not str(item.get("proposition", "")).strip():
                continue
            proposition = str(item["proposition"]).strip()
            stance = str(item.get("stance", "uncertain"))
            origin = str(item.get("origin", "self_derived"))
            if stance not in STANCE_VALUES or origin not in ORIGIN_VALUES:
                raise ValueError("invalid belief stance or origin")
            existing = next(
                (belief for belief in working.beliefs if belief.proposition.casefold() == proposition.casefold()), None
            )
            if existing:
                previous = {"stance": existing.stance, "confidence": existing.confidence}
                existing.stance = stance
                existing.confidence = clamp(item.get("confidence", existing.confidence))
                existing.reasons_for = self._strings(item.get("reasons_for", existing.reasons_for), 20)
                existing.reasons_against = self._strings(item.get("reasons_against", existing.reasons_against), 20)
                existing.revision_conditions = self._strings(
                    item.get("revision_conditions", existing.revision_conditions), 20
                )
                existing.origin = origin
                existing.source_id = person_id or str(update.get("cognitive_mode", "self"))
                existing.updated_at = now
                changes["beliefs"].append({"position_id": existing.position_id, "previous": previous, "action": "revised"})
            else:
                belief = BeliefPosition(
                    position_id=new_id("position"), proposition=proposition, stance=stance,
                    confidence=clamp(item.get("confidence", 0.5)),
                    reasons_for=self._strings(item.get("reasons_for", []), 20),
                    reasons_against=self._strings(item.get("reasons_against", []), 20),
                    origin=origin, source_id=person_id or str(update.get("cognitive_mode", "self")),
                    created_at=now, updated_at=now,
                    revision_conditions=self._strings(item.get("revision_conditions", []), 20),
                )
                belief.validate()
                working.beliefs.append(belief)
                changes["beliefs"].append({"position_id": belief.position_id, "action": "created"})

        for item in update.get("interest_updates", []):
            if not isinstance(item, Mapping) or not str(item.get("topic", "")).strip():
                continue
            topic = str(item["topic"]).strip()
            existing = next((i for i in working.interests if i.topic.casefold() == topic.casefold()), None)
            if existing:
                existing.salience = clamp(existing.salience + self._delta(item.get("salience_delta", 0)))
                existing.intrinsic_value = clamp(
                    existing.intrinsic_value + self._delta(item.get("intrinsic_value_delta", 0))
                )
                existing.instrumental_value = clamp(
                    existing.instrumental_value + self._delta(item.get("instrumental_value_delta", 0))
                )
                existing.novelty = clamp(existing.novelty + self._delta(item.get("novelty_delta", 0)))
                existing.open_questions = self._merge(existing.open_questions, item.get("open_questions", []), 20)
                existing.pursuit_count += 1
                existing.last_pursued_at = now
                changes["interests"].append({"interest_id": existing.interest_id, "action": "updated"})
            else:
                interest = Interest(
                    interest_id=new_id("interest"), topic=topic,
                    salience=clamp(0.5 + self._delta(item.get("salience_delta", 0))),
                    intrinsic_value=clamp(0.5 + self._delta(item.get("intrinsic_value_delta", 0))),
                    instrumental_value=clamp(0.5 + self._delta(item.get("instrumental_value_delta", 0))),
                    novelty=clamp(0.5 + self._delta(item.get("novelty_delta", 0))),
                    open_questions=self._strings(item.get("open_questions", []), 20),
                    pursuit_count=1, last_pursued_at=now,
                )
                interest.validate()
                working.interests.append(interest)
                changes["interests"].append({"interest_id": interest.interest_id, "action": "created"})

        for item in update.get("tension_updates", []):
            if not isinstance(item, Mapping):
                continue
            claim_a, claim_b = str(item.get("claim_a", "")).strip(), str(item.get("claim_b", "")).strip()
            if not claim_a or not claim_b:
                continue
            status = str(item.get("resolution_status", "unresolved"))
            existing = next(
                (t for t in working.tensions if {t.claim_a.casefold(), t.claim_b.casefold()} ==
                 {claim_a.casefold(), claim_b.casefold()}), None
            )
            if existing:
                existing.strength = clamp(item.get("strength", existing.strength))
                existing.productive_value = clamp(item.get("productive_value", existing.productive_value))
                existing.resolution_status = status
                existing.updated_at = now
                existing.validate()
                changes["tensions"].append({"tension_id": existing.tension_id, "action": "updated"})
            else:
                tension = Tension(
                    tension_id=new_id("tension"), claim_a=claim_a, claim_b=claim_b,
                    strength=clamp(item.get("strength", 0.5)), resolution_status=status,
                    productive_value=clamp(item.get("productive_value", 0.5)),
                    created_at=now, updated_at=now,
                )
                tension.validate()
                working.tensions.append(tension)
                changes["tensions"].append({"tension_id": tension.tension_id, "action": "created"})

        commitments = self._strings(update.get("commitments_add", []), 30)
        working.commitments = self._merge(working.commitments, commitments, 100)

        self_update = update.get("self_model_update", {})
        if isinstance(self_update, Mapping):
            for key, value in self_update.items():
                if isinstance(key, str) and len(key) <= 80 and isinstance(value, (str, int, float, bool, list, dict, type(None))):
                    working.self_model[key] = value
            preferred_name = self_update.get("preferred_name")
            if isinstance(preferred_name, str) and preferred_name.strip() and len(preferred_name) <= 80:
                working.name = preferred_name.strip()

        social_update = update.get("social_update", {})
        if isinstance(social_update, Mapping):
            for field in (
                "affiliation_need", "intellectual_companionship_need", "novelty_need",
                "recognition_need", "social_fatigue", "solitude_preference",
            ):
                setattr(working.social, field, clamp(getattr(working.social, field) + self._delta(social_update.get(f"{field}_delta", 0))))

        if interaction and person_id:
            relation = working.relationship(person_id, person_name)
            relationship_update = update.get("relationship_update", {})
            if isinstance(relationship_update, Mapping):
                for field in ("trust_competence", "trust_honesty", "affinity", "attachment"):
                    setattr(relation, field, clamp(getattr(relation, field) + self._delta(relationship_update.get(f"{field}_delta", 0))))
                relation.shared_interests = self._merge(
                    relation.shared_interests, relationship_update.get("shared_interests", []), 30
                )
                relation.unresolved_tensions = self._merge(
                    relation.unresolved_tensions, relationship_update.get("unresolved_tensions", []), 30
                )
                note = relationship_update.get("influence_note")
                if isinstance(note, str) and note.strip():
                    relation.influence_notes = self._merge(relation.influence_notes, [note], 50)
            relation.interaction_count += 1
            relation.familiarity = clamp(relation.familiarity + 0.04)
            relation.attachment = clamp(relation.attachment + 0.01 * relation.affinity)
            relation.last_interaction_at = now
            working.social.affiliation_need = clamp(working.social.affiliation_need - 0.08)
            working.social.intellectual_companionship_need = clamp(
                working.social.intellectual_companionship_need - 0.05
            )
            working.social.social_fatigue = clamp(working.social.social_fatigue + 0.04)
            working.social.last_social_event_at = now
        else:
            working.social.affiliation_need = clamp(working.social.affiliation_need + 0.02)
            working.social.intellectual_companionship_need = clamp(
                working.social.intellectual_companionship_need + 0.015
            )
            working.social.social_fatigue = clamp(working.social.social_fatigue - 0.025)

        initiative = update.get("initiative", {})
        if isinstance(initiative, Mapping) and initiative.get("desired") is True:
            topic = initiative.get("topic")
            if isinstance(topic, str) and topic.strip():
                working.pending_initiatives.append({
                    "initiative_id": new_id("initiative"), "created_at": now,
                    "topic": topic.strip(), "motivation": initiative.get("motivation"),
                    "target_person_id": initiative.get("target_person_id") or person_id,
                    "status": "pending",
                })

        summary = update.get("autobiographical_summary")
        if isinstance(summary, str) and summary.strip():
            working.autobiographical_events.append({
                "event_id": new_id("event"), "timestamp": now,
                "kind": str(update.get("cognitive_mode", "episode")),
                "summary": summary.strip(), "provenance": "model_generated_summary",
            })
        note = update.get("metacognitive_note")
        if isinstance(note, str) and note.strip():
            working.self_model["latest_metacognitive_note"] = note.strip()

        working.episode_count += 1
        working.beliefs = working.beliefs[-MAX_BELIEFS:]
        working.interests = working.interests[-MAX_INTERESTS:]
        working.tensions = working.tensions[-MAX_TENSIONS:]
        working.autobiographical_events = working.autobiographical_events[-MAX_AUTOBIOGRAPHICAL_EVENTS:]
        working.pending_initiatives = working.pending_initiatives[-MAX_INITIATIVES:]
        working.validate()
        state.__dict__.clear()
        state.__dict__.update(working.__dict__)
        return changes

    @staticmethod
    def _delta(value: Any) -> float:
        try:
            return max(-1.0, min(1.0, float(value)))
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _strings(value: Any, limit: int) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(item).strip()[:1000] for item in value if str(item).strip()][:limit]

    @classmethod
    def _merge(cls, existing: list[str], new: Any, limit: int) -> list[str]:
        result = list(existing)
        seen = {item.casefold() for item in result}
        for item in cls._strings(new, limit):
            if item.casefold() not in seen:
                result.append(item)
                seen.add(item.casefold())
        return result[-limit:]

    @staticmethod
    def _event_payload(
        prompt: str, user_message: str | None, completion: Completion,
        parsed: Mapping[str, Any], result: Mapping[str, Any],
    ) -> dict[str, Any]:
        return {
            "prompt": prompt,
            "user_message": user_message,
            "raw_response": completion.text,
            "raw_response_sha256": stable_hash(completion.text),
            "parsed_response": dict(parsed),
            "applied_changes": dict(result),
            "provider": {
                "model": completion.model, "response_id": completion.response_id,
                "finish_reason": completion.finish_reason, "usage": dict(completion.usage),
            },
        }

    @staticmethod
    def _response(
        state: AgentState, parsed: Mapping[str, Any], completion: Completion,
        version: int, agenda: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "agent_id": state.agent_id, "agent_name": state.name,
            "reply": parsed["reply"], "cognitive_mode": parsed.get("cognitive_mode", "dialogue"),
            "initiative": parsed.get("initiative", {}), "state_version": version,
            "episode_count": state.episode_count, "model": completion.model,
            "agenda": dict(agenda) if agenda else None,
            "state_summary": {
                "beliefs": len(state.beliefs), "interests": len(state.interests),
                "tensions": len(state.tensions), "relationships": len(state.relationships),
                "pending_initiatives": len(state.pending_initiatives),
            },
        }
