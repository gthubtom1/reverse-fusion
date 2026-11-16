# Implementation Plan: 标签收纳盒完整复刻
**Branch**: `001-desk-recreation` | **Date**: 2026-11-16 | **Spec**: [spec.md](spec.md)
**Input**: specs/001-desk-recreation/spec.md

## Summary
Independently implement the full small local collection application. Preserve browser UI and persistence semantics; add only a local Windows launcher convenience. Native Craft writes candidate files after evidence review.

## Technical Context
**Language/Version**: Standard browser JavaScript ES modules; Python 3 standard library launcher.
**Primary Dependencies**: Browser DOM/storage only; Python already installed on this computer.
**Storage**: localStorage, original schema/key, distinct loopback port.
**Testing**: Node deterministic differential comparisons, Chrome Playwright operation trace, PNG byte comparison and layout metrics, launcher smoke test.
**Target Platform**: Current Windows computer and installed Chrome/Edge; application also works in modern browsers over local HTTP.
**Project Type**: Offline browser application with local-only launcher.
**Performance Goals**: Interactive actions complete within ordinary local browser event processing; no invented performance claim beyond the supplied target.
**Constraints**: No external network, no account, no original runtime imports, no shared-tool runtime dependency. Test contexts fresh and closed.
**Scale/Scope**: Entire supplied four-file application and simple launcher. No reduced subset.

## Constitution Check
Before research: pass; plain source available, native bundle retained, originals fixed, whole scope known.
After design: pass; eight requirements supported, launcher explicitly designed, no critical dependency unknown. Native static semantic unknowns remain partial and are not claimed closed.

## Project Structure
### Documentation (this feature)
spec.md, plan.md, research.md, data-model.md, contracts/ui.md, quickstart.md, tasks.md.
### Source Code (repository root)
work/current-case/craft/app/{index.html,core.mjs,page.mjs,launch.py,启动.cmd,使用说明.txt}
outputs/标签收纳盒/ receives the exact checked files, with a ZIP alongside it.
work/{compare.mjs,observe.cjs}: independent validation, outside delivered runtime.
**Structure Decision**: Candidate writes use a bounded native workspace; delivery copies verified exact files only after native cleanup.

## Phases
0. Research original static analysis and isolated runtime, freeze comparison rules.
1. Define state and UI contracts, including failure and restore semantics.
2. Execute official tasks/analyze, handoff review, native prepare, core/UI/launcher builds and checks.
3. Native cleanup, session finish, delivery launch smoke test, tasks completion and converge.

## Validation Design
Core differential tests compare returned JSON, exact thrown messages and input non-mutation over boundaries and seeded traces. Browser comparator checks all 21 snapshots, error-free runtime, storage, focus, controls, cancellation, desktop/mobile layout and PNG content. Same browser/locale/viewport and clean state. Mutant forces incorrect totals and MUST fail. Holdout is a separate fixed random seed with 500 operations. Local server is loopback-only, browser contexts closed; candidate runtime contains no original or tool references.

## Complexity Tracking
No constitution violations. No external packages needed by the delivered app.
