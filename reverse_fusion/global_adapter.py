"""Install the small Codex adapter that points to this checkout.

The repository owns the router and domain material.  The user-level adapter is
only a pointer and a trigger rule, so unrelated project files remain in the
workspace where the user opened them.
"""

from __future__ import annotations

from pathlib import Path


MARKER_START = "<!-- reverse-fusion:begin -->"
MARKER_END = "<!-- reverse-fusion:end -->"
LEGACY_HEADER = "# Global Codex guidance"
SKILL_MARKER = "# Reverse Fusion cross-project adapter"


def adapter_paths(home: Path | None = None) -> dict[str, Path]:
    root = (home or Path.home()).expanduser()
    return {
        "skill": root / ".agents" / "skills" / "reverse-fusion" / "SKILL.md",
        "agents": root / ".codex" / "AGENTS.md",
    }


def _repo_display(repo_root: Path) -> str:
    return repo_root.resolve().as_posix()


def skill_text(repo_root: Path) -> str:
    repo = _repo_display(repo_root)
    return f"""---
name: reverse-fusion
description: Use the Reverse Fusion repository for reverse engineering, protected binary and APK analysis, JavaScript/WASM reverse work, protocol reconstruction, behavior reconstruction, or explicit Reverse Fusion requests. Route the task through the repository-local bridge before selecting domain materials or verification steps.
---

# Reverse Fusion cross-project adapter

Use this skill when the current task involves reverse engineering, protected or obfuscated software, APK/DEX, PE/.NET, JavaScript/WASM, protocol reconstruction, behavior equivalence, or when the user explicitly asks to use Reverse Fusion.

The canonical checkout is `{repo}`. Keep the user's current project as the working project. Do not copy Reverse Fusion's entire `skills/` tree into the current project and do not write project output into the Reverse Fusion checkout unless the task is specifically about maintaining Reverse Fusion.

Before choosing a specialist workflow, verify the checkout and invoke its local router with the repository venv:

```text
Windows: {repo}/.venv/Scripts/python.exe -m reverse_fusion bridge --source local --hint "<the user's task>" --format json
POSIX:   {repo}/.venv/bin/python -m reverse_fusion bridge --source local --hint "<the user's task>" --format json
```

Read the returned `workflow`, `skill`, `required_reads`, `related_routes`, `next_stage`, `hard_target`, and `missing_support`. Read the returned local `SKILL.md` and required references before acting. If the task is ordinary software development without reverse or reconstruction intent, keep the normal host-native workflow and do not activate Reverse Fusion just because this skill exists.

Use `--mode analysis` for evidence-backed analysis and `--mode reconstruction` for an explicit reimplementation/equivalence task. Preserve `pass`, `fail`, `unknown`, `blocked`, and `unsupported` honestly. Do not select or download models, change host runtime configuration, start every provider, or claim target acceptance from route selection alone.

If the canonical checkout or its venv is missing, report that the shared adapter is unavailable and ask the user to restore or redeploy the checkout; do not silently clone or install a second copy in the user's project.
"""


def agents_block(repo_root: Path) -> str:
    repo = _repo_display(repo_root)
    return f"""{MARKER_START}
- When a task involves reverse engineering, protected or obfuscated software, APK/DEX, PE/.NET, JavaScript/WASM reverse work, protocol reconstruction, behavior equivalence, or an explicit request to use Reverse Fusion, use the user-level `reverse-fusion` skill before acting.
- Keep the current project directory as the work area. The Reverse Fusion checkout is a shared reference and router at `{repo}`; do not write unrelated project output there.
{MARKER_END}"""


def _replace_agents_block(text: str, block: str) -> str:
    start = text.find(MARKER_START)
    end = text.find(MARKER_END)
    if start >= 0 and end >= start:
        end += len(MARKER_END)
        updated = text[:start].rstrip() + "\n\n" + block + text[end:]
        return updated.rstrip() + "\n"

    # Convert the adapter written by the first manual deployment into the
    # managed block without touching any unrelated user instructions.
    legacy = (
        f"{LEGACY_HEADER}\n\n"
        "- When a task involves reverse engineering, protected or obfuscated software, APK/DEX, PE/.NET, JavaScript/WASM reverse work, protocol reconstruction, behavior equivalence, or an explicit request to use Reverse Fusion, use the user-level `reverse-fusion` skill before acting.\n"
        "- Keep the current project directory as the work area. The Reverse Fusion checkout is a shared reference and router at `D:\\Project\\reverse`; do not write unrelated project output there.\n"
    )
    if legacy in text:
        text = text.replace(legacy, "")
    return (text.rstrip() + "\n\n" + block + "\n") if text.strip() else block + "\n"


def install_global_adapter(repo_root: Path, home: Path | None = None) -> dict[str, object]:
    repo = repo_root.resolve()
    paths = adapter_paths(home)
    if paths["skill"].is_file():
        existing_skill = paths["skill"].read_text(encoding="utf-8")
        if SKILL_MARKER not in existing_skill:
            raise ValueError(f"Existing user skill is not managed by Reverse Fusion: {paths['skill']}")
    paths["skill"].parent.mkdir(parents=True, exist_ok=True)
    paths["agents"].parent.mkdir(parents=True, exist_ok=True)
    paths["skill"].write_text(skill_text(repo), encoding="utf-8")
    existing = paths["agents"].read_text(encoding="utf-8") if paths["agents"].is_file() else ""
    paths["agents"].write_text(_replace_agents_block(existing, agents_block(repo)), encoding="utf-8")
    return {
        "enabled": True,
        "skill": str(paths["skill"]),
        "agents": str(paths["agents"]),
        "repository": str(repo),
    }


def remove_global_adapter(home: Path | None = None) -> dict[str, object]:
    paths = adapter_paths(home)
    removed: list[str] = []
    if paths["skill"].is_file():
        text = paths["skill"].read_text(encoding="utf-8")
        if SKILL_MARKER in text:
            paths["skill"].unlink()
            removed.append(str(paths["skill"]))
            try:
                paths["skill"].parent.rmdir()
            except OSError:
                pass
    if paths["agents"].is_file():
        text = paths["agents"].read_text(encoding="utf-8")
        start = text.find(MARKER_START)
        end = text.find(MARKER_END)
        if start >= 0 and end >= start:
            end += len(MARKER_END)
            updated = (text[:start].rstrip() + text[end:].lstrip()).rstrip()
            if updated:
                paths["agents"].write_text(updated + "\n", encoding="utf-8")
            else:
                paths["agents"].unlink()
            removed.append(str(paths["agents"]))
    return {"enabled": False, "removed": removed}
