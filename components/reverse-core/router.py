"""Repository-owned, portable Reverse router.

The upstream reverse-skill routing semantics are kept as a versioned data file
next to this module.  The router is intentionally small: it scores declarative
``must``/``mustAll``/``exclude`` rules, resolves ties with the declared
priority list, and returns a local route descriptor.  It has no provider,
credential, model, or receipt dependency.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
ROUTING_FILE = ROOT / "routing.json"
LOCAL_ROUTE_DIR = ROOT / "routes"


@dataclass(frozen=True)
class LocalRoute:
    status: str
    source: str
    hint: str
    primary_id: str
    primary: str
    label: str
    confidence: str
    matches: tuple[str, ...]
    notes: tuple[str, ...]
    routing_sha256: str
    skill: str
    skill_available: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "source": self.source,
            "hint": self.hint,
            "primary_id": self.primary_id,
            "primary": self.primary,
            "label": self.label,
            "confidence": self.confidence,
            "matches": list(self.matches),
            "notes": list(self.notes),
            "routing_sha256": self.routing_sha256,
            "skill": self.skill,
            "skill_available": self.skill_available,
        }


def _load() -> tuple[dict[str, Any], str]:
    payload = ROUTING_FILE.read_bytes()
    data = json.loads(payload.decode("utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("routes"), dict):
        raise ValueError("local routing manifest is malformed")
    priority = data.get("priority")
    if not isinstance(priority, list) or not priority:
        raise ValueError("local routing priority is missing")
    route_ids = set(data["routes"])
    if set(priority) != route_ids:
        raise ValueError("local routing routes and priority diverge")
    fallback = data.get("meta", {}).get("fallbackId")
    if fallback not in route_ids:
        raise ValueError("local routing fallback is missing")
    return data, hashlib.sha256(payload).hexdigest()


def _hit(text: str, rule: dict[str, Any]) -> bool:
    pattern = rule.get("must")
    if not isinstance(pattern, str) or not re.search(pattern, text, flags=re.IGNORECASE):
        return False
    must_all = rule.get("mustAll", [])
    if any(not re.search(item, text, flags=re.IGNORECASE) for item in must_all):
        return False
    exclude = rule.get("exclude")
    if isinstance(exclude, str) and re.search(exclude, text, flags=re.IGNORECASE):
        return False
    return True


def _descriptor(route_id: str, route: dict[str, Any]) -> str:
    descriptor = LOCAL_ROUTE_DIR / f"{route_id}.md"
    if descriptor.is_file():
        return str(descriptor.relative_to(ROOT.parent.parent)).replace("\\", "/")
    # A descriptor is part of the repository contract.  Returning the stable
    # path still lets callers report a missing local capability explicitly.
    return str(descriptor.relative_to(ROOT.parent.parent)).replace("\\", "/")


def _local_skill(route: dict[str, Any]) -> tuple[str, bool]:
    skill = route.get("skill")
    if not isinstance(skill, str) or not skill:
        return "", False
    path = ROOT.parent.parent / "skills" / skill
    return f"skills/{skill}", path.is_file()


def route(hint: str, *, primary: str | None = None) -> LocalRoute:
    """Resolve a hint without reading any external installation state."""
    data, digest = _load()
    text = (hint or "").lower()
    scores: dict[str, int] = {}
    notes: list[str] = []
    for route_id, route_data in data["routes"].items():
        for rule in route_data.get("keywords", []):
            if _hit(text, rule):
                scores[route_id] = scores.get(route_id, 0) + 1

    route_ids = set(data["routes"])
    if primary:
        if primary not in route_ids:
            raise ValueError(f"explicit primary id '{primary}' is not in local routing")
        selected = primary
        confidence = "explicit"
        notes.append("Explicit primary override; automatic keyword scoring was not used for PRIMARY.")
    else:
        selected = None
        max_score = -1
        for item in data["priority"]:
            if item in scores and scores[item] > max_score:
                selected = item
                max_score = scores[item]
        if selected is None:
            selected = data["meta"]["fallbackId"]
            confidence = "low"
            notes.append("No strong keyword hit; the generic reverse route remains the owner.")
        else:
            confidence = "high" if len(scores) == 1 else "medium"

    selected_data = data["routes"][selected]
    descriptor = _descriptor(selected, selected_data)
    skill, skill_available = _local_skill(selected_data)
    if not (LOCAL_ROUTE_DIR / f"{selected}.md").is_file():
        notes.append("Local route descriptor is missing.")
    if not skill_available:
        notes.append("Local domain skill is missing.")
    status = "local-route-pass" if (LOCAL_ROUTE_DIR / f"{selected}.md").is_file() and skill_available else "unavailable"
    if not text:
        notes.append("Empty hint; provide task text before acting on the route.")
    return LocalRoute(
        status=status,
        source="local",
        hint=hint,
        primary_id=selected,
        primary=descriptor,
        label=selected_data["label"],
        confidence=confidence,
        matches=tuple(item for item in data["priority"] if item in scores),
        notes=tuple(notes),
        routing_sha256=digest,
        skill=skill,
        skill_available=skill_available,
    )

