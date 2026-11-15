"""Install the small Codex adapter that points to this checkout.

The repository owns the router and domain material.  The user-level adapter is
only a pointer and a trigger rule, so unrelated project files remain in the
workspace where the user opened them.
"""

from __future__ import annotations

from pathlib import Path
import os


MARKER_START = "<!-- reverse-fusion:begin -->"
MARKER_END = "<!-- reverse-fusion:end -->"
LEGACY_HEADER = "# Global Codex guidance"
SKILL_MARKER = "# Reverse Fusion cross-project adapter"


def adapter_paths(home: Path | None = None) -> dict[str, Path]:
    root = (home or Path.home()).expanduser()
    codex_root = (Path(os.environ['CODEX_HOME']).expanduser()
                  if home is None and os.environ.get('CODEX_HOME') else root / '.codex')
    return {
        "skill": root / ".agents" / "skills" / "reverse-fusion" / "SKILL.md",
        "agents": codex_root / "AGENTS.md",
    }


def _repo_display(repo_root: Path) -> str:
    return repo_root.resolve().as_posix()


def skill_text(repo_root: Path) -> str:
    repo = _repo_display(repo_root)
    return f"""---
name: reverse-fusion
description: Use Reverse Fusion for requests such as 分析这个软件然后复刻, 看懂APK, 照着网站做一样的, reverse engineering, protected/obfuscated binaries, protocol or behavior reconstruction, specialist security analysis/forensics, or explicit Reverse Fusion requests. Route through the shared repository and preserve the user goal across analysis and implementation.
---

# Reverse Fusion cross-project adapter

Use this skill for plain requests to analyze/recreate a supplied target, specialist security analysis/forensics, or when the current task involves reverse engineering, protected or obfuscated software, APK/DEX, PE/.NET, JavaScript/WASM, protocol reconstruction, behavior equivalence, or when the user explicitly asks to use Reverse Fusion.

The canonical checkout is `{repo}`. Keep the user's current project as the working project. Do not copy Reverse Fusion's entire `skills/` tree into the current project and do not write project output into the Reverse Fusion checkout unless the task is specifically about maintaining Reverse Fusion.

First read [the agent workflow]({repo}/docs/AGENT-WORKFLOW.md). Plain user language is sufficient: preserve the original delivery objective, start an unidentified recreation request with analysis, refine methods from actual evidence, and ask concrete product/operation questions only when needed. The user does not choose route IDs or component commands. Do not replace a whole-product goal with an unrequested demo or slice; keep unresolved dependencies and remaining work attached to that goal.

Before choosing a specialist workflow, verify the checkout and invoke its local router with the repository venv:

```text
Windows PowerShell: & "{repo}/.venv/Scripts/python.exe" -m reverse_fusion bridge --project-root "<current project absolute path>" --source local --hint "<the user's task>" --format json
POSIX: "{repo}/.venv/bin/python" -m reverse_fusion bridge --project-root "<current project absolute path>" --source local --hint "<the user's task>" --format json
```

Read `workflow.objective` and `workflow.user_request` separately from the current `workflow.stage`. A generic request to recreate a target starts with analysis; route selection is not implementation readiness. For a continuation, resume the existing case and carry forward the original objective rather than treating a short message as a new task. Read the returned `workflow`, `skill`, `required_reads`, `related_routes`, `next_stage`, `hard_target`, and `missing_support`. Read the returned local `SKILL.md` and required references before acting. If the task is ordinary software development without reverse or reconstruction intent, keep the normal host-native workflow and do not activate Reverse Fusion just because this skill exists.

For analysis or reconstruction, read [the cross-project handoff guide]({repo}/docs/CROSS-PROJECT-WORKFLOW.md) before starting implementation. `required_read_paths` are absolute skill-checkout paths; cases, task files, candidate outputs and session receipts belong to `project_root`. Do not change cwd to the tool checkout to make a task command work. After identifying the real technology, refine the same case's domain route rather than staying on an initial generic route.

Reconstruction requires evidence-linked spec/tasks and review of critical dependencies, then run the installed official Spec Kit generated project workflow and `native-craft prepare --case-root "work/<case>" --handoff-manifest "<project-relative handoff>" --review-file "<project-relative semantic review>"` before candidate edits. Read `docs/NATIVE-COMPONENTS.md` in the shared checkout for the lease, native build/check/refine/summary/cleanup and additional session observer. Continue independent behavior validation. Pass the same `--project-root` on every task command and record the bridge with `--case-root "work/<case>" --record` after identifying the target. The handoff checker blocks declared critical unknowns; it cannot detect omitted licensing/state dependencies or prove semantic readiness. Do not silently remove an observed licensing dependency or redefine the delivery as a standalone local subset. Missing REA permits raw-tool analysis, but not fabricated native proof. Real REA, official Spec Kit and native Craft are required installed components. Current host reasoning supplies content to actual Craft engine tools; direct edits or the session observer do not substitute for Craft. Missing components mean incomplete deployment; maintain the repository-owned adapter/source patch when upstream has a demonstrated gap. A route pass is not execution of REA, Spec, Craft or Builder: report which parts actually ran.

Use `--mode analysis` while investigating; the bridge retains the reconstruction objective. After the readiness review, explicitly transition the same case with `--mode reconstruction` for the implementation/equivalence stage. Preserve `pass`, `fail`, `unknown`, `blocked`, and `unsupported` honestly. Do not select or download models, change host runtime configuration, start every provider, or claim target acceptance from route selection alone.

If the canonical checkout or its venv is missing, report that the shared adapter is unavailable and ask the user to restore or redeploy the checkout; do not silently clone or install a second copy in the user's project.
"""


def agents_block(repo_root: Path) -> str:
    repo = _repo_display(repo_root)
    return f"""{MARKER_START}
- When a task involves reverse engineering, protected or obfuscated software, APK/DEX, PE/.NET, JavaScript/WASM reverse work, protocol reconstruction, behavior equivalence, specialist security analysis or forensics, a plain request to analyze/recreate a supplied target, or an explicit request to use Reverse Fusion, use the user-level `reverse-fusion` skill before acting.
- Keep the current project directory as the work area. The Reverse Fusion checkout is a shared reference and router at `{repo}`; do not write unrelated project output there.
{MARKER_END}"""


def _check_markers(text: str) -> None:
    if (text.count(MARKER_START), text.count(MARKER_END)) not in {(0, 0), (1, 1)}:
        raise ValueError("Global AGENTS.md has incomplete or duplicate Reverse Fusion markers")
    if text.find(MARKER_END) >= 0 and text.find(MARKER_END) < text.find(MARKER_START):
        raise ValueError("Global AGENTS.md has reversed Reverse Fusion markers")


def _replace_agents_block(text: str, block: str) -> str:
    _check_markers(text)
    start = text.find(MARKER_START)
    end = text.find(MARKER_END)
    if start >= 0 and end >= start:
        end += len(MARKER_END)
        return text[:start] + block + text[end:]

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
    existing = paths["agents"].read_text(encoding="utf-8") if paths["agents"].is_file() else ""
    updated = _replace_agents_block(existing, agents_block(repo))
    paths["skill"].parent.mkdir(parents=True, exist_ok=True)
    paths["agents"].parent.mkdir(parents=True, exist_ok=True)
    paths["skill"].write_text(skill_text(repo), encoding="utf-8")
    paths["agents"].write_text(updated, encoding="utf-8")
    return {
        "enabled": True,
        "skill": str(paths["skill"]),
        "agents": str(paths["agents"]),
        "repository": str(repo),
    }


def remove_global_adapter(home: Path | None = None, *, repo_root: Path | None = None) -> dict[str, object]:
    paths = adapter_paths(home)
    agents_text = paths['agents'].read_text(encoding='utf-8') if paths['agents'].is_file() else ''
    _check_markers(agents_text)
    removed: list[str] = []
    if paths["skill"].is_file():
        text = paths["skill"].read_text(encoding="utf-8")
        owned = repo_root is None or f'The canonical checkout is `{_repo_display(repo_root)}`.' in text
        if SKILL_MARKER in text and owned:
            paths["skill"].unlink()
            removed.append(str(paths["skill"]))
            try:
                paths["skill"].parent.rmdir()
            except OSError:
                pass
    if paths["agents"].is_file():
        text = agents_text
        start = text.find(MARKER_START)
        end = text.find(MARKER_END)
        if start >= 0 and end >= start:
            end += len(MARKER_END)
            if repo_root is not None and text[start:end] != agents_block(repo_root):
                return {"enabled": False, "removed": removed, "retained": "another checkout owns the global pointer"}
            updated = text[:start] + text[end:]
            if updated.strip():
                paths["agents"].write_text(updated, encoding="utf-8")
            else:
                paths["agents"].unlink()
            removed.append(str(paths["agents"]))
    return {"enabled": False, "removed": removed}
