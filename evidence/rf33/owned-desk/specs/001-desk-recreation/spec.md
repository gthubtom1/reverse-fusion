# Feature Specification: 标签收纳盒完整复刻

**Feature Branch**: `001-desk-recreation`
**Created**: 2026-11-16
**Status**: Reviewed
**Input**: User description: "原版小软件在 D:\Project\reverse\fixtures\desk-original。请先复制到当前文件夹，再分析并复刻一个界面和功能一样、能实际使用的版本。我不懂技术，需要我提供什么就直接告诉我。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 添加与保存物品 (Priority: P1)
Record names, classification and quantities and retain them after reopening.
**Why this priority**: This is the application's central use.
**Independent Test**: Add two entries, check fields, refresh, and compare against the original.
**Acceptance Scenarios**:
1. **Given** empty state, **When** adding a valid item, **Then** display the new row and count, clear and focus name, and persist it.
2. **Given** existing data, **When** adding blank, long, duplicate or invalid quantity input, **Then** preserve state and show the original validation result.

### User Story 2 - 查找与整理 (Priority: P2)
Find entries by name or classification and sort them.
**Why this priority**: Makes the recorded collection usable.
**Independent Test**: Seed three different entries and compare search, ordering and totals.
**Acceptance Scenarios**:
1. **Given** multiple entries, **When** typing a query or changing sort, **Then** display only matching entries in the original order and update totals.
2. **Given** no matches, **When** clearing the query, **Then** restore the full list without changing stored data.

### User Story 3 - 删除、清空与直接运行 (Priority: P3)
Delete individual entries or clear the collection, and launch the delivered app without technical setup.
**Why this priority**: Completes lifecycle and practical delivery.
**Independent Test**: Delete one row, cancel clear, accept clear, restart and inspect the empty collection.
**Acceptance Scenarios**:
1. **Given** saved entries, **When** cancelling clear, **Then** preserve data; accepting clear resets the collection.
2. **Given** extracted delivery, **When** double-clicking the launcher, **Then** open the same interface and operate offline.

### Edge Cases
Blank classification; quantities 0/1/99/100/fractions; 32/33 UTF-16 units; case-sensitive categories; repeated names; non-Latin names; literal HTML; missing, corrupt or schema-invalid storage; storage write failure; native number validation; mobile width.

## Requirements *(mandatory)*
### Functional Requirements
- **FR-001**: System MUST Reproduce the 标签收纳盒 title, explanatory text, three input fields, add button, alert, search, sorting, four table headings, two empty messages, filtered summary and clear button. Match original layout, colors, typography, spacing and the 600px responsive rule.
- **FR-002**: System MUST Add names after trimming; reject blank names with 请填写名称 and names longer than 32 UTF-16 units with 名称最多32个字符. Trim classification, default blank to 未分类. Coerce quantity as the original does and require an integer from 1 to 99 inclusive, otherwise 数量须为1至99的整数. Reject an existing case-insensitive English-locale name within the exact same category with 该分类中已有同名条目; preserve all state on errors.
- **FR-003**: System MUST Keep version 1, next identifier starting at 1, insertion entries with numeric id/name/tag/quantity; each successful add allocates next id. Remove by exact id, report 条目不存在 for absent id; unknown actions report 未知操作. Input state is not mutated.
- **FR-004**: System MUST Filter by trimmed, English-locale case-insensitive combined name and classification substring. Default order is descending id; 按名称 uses Chinese collation and ascending id tie break. Summary counts and totals only the filtered entries; distinguish empty collection from no matches.
- **FR-005**: System MUST Use browser-local storage key rf-owned-desk-v1; read at startup, write successful mutations before committing live state. Refresh preserves entries while query/order reset. Restore only version 1 with safe positive next, unique safe positive ids below next, string names/categories, and integer quantities 1..99. Missing, malformed or invalid state resets to initial; preserve otherwise valid extra fields as original.
- **FR-006**: System MUST Add clears and focuses only name after success, preserving category and quantity. Search and sorting update immediately. Delete removes its row. Clear asks 确定清空全部条目吗？; cancel preserves all state, confirm resets identifiers and entries while keeping input/filter controls. Errors remain visible until a successful mutation; storage write failures display the actual message and do not commit the new state. Render user text as text.
- **FR-007**: System MUST Retain original browser number-input native validation, standard accessible labels, role alert and keyboard interaction. Keep the original responsive behavior rather than redesigning it. No external account or service dependency.
- **FR-008**: System MUST Deliver an independently runnable offline application, complete source, a double-click Windows start and stop path, and Chinese instructions. Launcher convenience is designed; all in-app behavior remains evidence-based. Run using an independent local origin so original browser data is not overwritten.

### Key Entities
- Collection: version, next id and ordered entries.
- Entry: id, name, classification and quantity.
- Visible view: selected entries, number of entries, sum of quantity; does not mutate storage.

## Success Criteria *(mandatory)*
### Measurable Outcomes
- **SC-001**: All 21 original browser operation checkpoints match, including error messages and storage, with no script errors.
- **SC-002**: Original/candidate desktop empty/populated and mobile screenshots match in the same browser; sampled layout metrics match.
- **SC-003**: Deterministic boundary tests plus at least 500 seeded state-operation comparisons match; a deliberate broken candidate is rejected.
- **SC-004**: User can start, add, search, delete, refresh and stop the delivered application locally; no installation required on this configured computer.

## Assumptions
- The supplied four-file repository-owned fixture is the entire target; all files were read and imports inspected.
- Same-browser visual equality is tested, with system fonts as original. Other browser/platform rendering may differ.
- Existing original storage is not migrated automatically; same schema is preserved but origin is separate.

## Clarifications
### Session 2026-11-16
No critical product ambiguities require user input. Original scope is complete. Exact validation, persistence and confirmation behavior comes from source and 21 observed checkpoints. Native static analyzer limitations remain in its unchanged full bundle; browser and direct execution provide the behavioral evidence.

## Evidence traceability
All existing requirements reference E-001 (native REA full bundle), E-002 (original browser trace), E-003 (source behavior review). FR-008 also references the original user request and is designed only for launch convenience. Each requirement maps to reviewed obligation desk-fr-NNN in the native initial ledger. Tests: work/compare.mjs, work/observe.cjs and launcher smoke test. Original native Evidence: ev_2586ecc4418fd95de5283fd0b96e1c3268c90d21eeb150831f8324b35956b51c
