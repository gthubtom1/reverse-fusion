# Tasks: 标签收纳盒完整复刻

**Input**: specs/001-desk-recreation/{spec,plan,research,data-model}.md and contracts/ui.md
**Prerequisites**: source behavior review, native original bundle, 21 browser checkpoints, no critical dependency unknown.
**Tests**: Explicitly required by SC-001 through SC-004. Independent original/candidate comparison is the acceptance authority for tested cases.

## Phase 1: Setup (Shared Infrastructure)
- [x] T001 Preserve immutable original identity and original runtime observations in work/current-case/evidence; source-ref FR-001..FR-007, E-001..E-003.
- [x] T002 Generate official constitution/spec/plan and reviewed state/UI contracts in specs/001-desk-recreation; source-ref Constitution I-V.

## Phase 2: Foundational (Blocking Prerequisites)
- [x] T003 Freeze original/candidate comparator and deliberate mutant check in work/compare.mjs and work/observe.cjs; source-ref SC-001..SC-003. Missing candidate MUST fail before implementation.
- [x] T004 Prepare reviewed native Craft workspace work/current-case/craft using evidence-linked handoff; source-ref Constitution III.

## Phase 3: User Story 1 - 添加与保存 (Priority: P1)
**Goal**: Full observed item model, validation, state and persistence.
**Independent Test**: Pure differential transitions and original/candidate add/reload/error browser traces.
- [x] T005 [US1] Implement independent core.mjs in work/current-case/craft/app: version 1; next safe positive integer; unique safe positive ids below next; name at most 32 UTF-16 units on add; quantity integer 1..99; exact errors and validation order; preserve valid extra restored fields. Source-ref FR-002, FR-003, FR-005, data-model.md, E-001/E-003, desk-fr-002/003/005.
- [x] T006 [US1] Build matching index.html and independent page.mjs in work/current-case/craft/app with full styling, labels, storage transaction, native number validity, focus, text rendering and exact copy; source-ref FR-001, FR-005, FR-006, FR-007, E-002, contracts/ui.md.

## Phase 4: User Story 2 - 搜索排序 (Priority: P2)
**Goal**: Matching search, locale sort, filtered counts and empty states.
**Independent Test**: Comparator search/sort cases plus browser query checkpoints.
- [x] T007 [US2] Implement view projection in work/current-case/craft/app/core.mjs and wire query/order in page.mjs: trimmed en-US case-insensitive combined substring, zh-CN name sort with id tie break, default descending id, filtered totals; source-ref FR-004, FR-006, SC-001, E-001..E-003.

## Phase 5: User Story 3 - 删除清空与运行 (Priority: P3)
**Goal**: Full collection lifecycle and accessible local launch.
**Independent Test**: Delete/cancel/confirm traces and actual delivered launcher start-stop.
- [x] T008 [US3] Wire exact delete and confirm/cancel clear behavior in work/current-case/craft/app/page.mjs; source-ref FR-003, FR-006, E-002.
- [x] T009 [US3] Add launch.py, 启动.cmd and 使用说明.txt in work/current-case/craft/app: fixed 127.0.0.1:8877, serve only this folder, use installed Python and browser, visible user-controlled window and clear bind errors; source-ref FR-008, SC-004, contracts/ui.md. Launcher is designed convenience.

## Phase 6: Validation & Delivery
- [x] T010 Run frozen full comparator via native Craft and inspect retained work/current-case/evidence/differential: 1200 seeded transitions, boundaries, errors, state, 21 browser checkpoints, three exact screenshot comparisons, mutant rejection and no original dependency; source-ref SC-001..SC-003 and all requirements.
- [x] T011 Execute native summary/cleanup and observer finish, copy exact verified files into outputs/标签收纳盒, ZIP them, and smoke-test delivered launcher in isolation; source-ref FR-008, SC-004.
- [x] T012 Complete Spec implement/converge review and Chinese delivery note under outputs; source-ref Constitution IV-V and all requirements.

## Dependencies & Execution Order
T001-T003 precede T004. T005 precedes T006. T007/T008 modify shared core/controller files and run sequentially. T009 precedes T010. All frozen native checks precede cleanup and tasks progress updates. T011 and T012 complete delivery after native finish. The entire product is delivered together; story organization does not reduce scope.

## Parallel Opportunities
Independent analysis artifacts could be parallelized, but the small application has one native writer. No candidate-file concurrency is used.

## Implementation Strategy
Implement complete product in one reviewed lease, retaining original evidence. Validate all stories before packaging. If a requirement changes, abort the old lease, preserve it and prepare a new reviewed batch; never alter frozen expected behavior to pass.

## Phase 7: Convergence
- [x] T013 Fix Windows duplicate-port launch conflict in work/current-case/craft-v2/app/launch.py using exclusive bind, replay all application comparisons and actual launcher startup/conflict/cleanup checks; source-ref FR-008, SC-004, contracts/ui.md (partial). No in-app behavior change.
