# Reverse Fusion operating rules

These are the operating rules for the local enhanced Reverse Skills copy.
`AGENTS.md`, the current user's instructions, and the current host's instruction
hierarchy apply. Ordinary development remains `normal-dev`; this file does not
activate every analysis tool or require a reverse case for ordinary development.

## Routing and context

1. Use `python -m reverse_fusion bridge --source local --hint "<task>"` for a
   specialist task. `components/reverse-core/routing.json` is the effective
   route source. The inherited PowerShell/Bash routers read it when present;
   `skills/config/routing.json` retains the pinned upstream baseline.
2. Read the selected `skill` and `required_reads` returned by the route. The
   descriptor is a pointer, not the domain instructions. The current host's
   main agent owns route, case, scope, work items and promotion of observations.
   In inherited documents, “Pi lead” means this current host's lead; another
   host or model is not a prerequisite.
   For cross-project use, pass the active outcome project's `--project-root` to
   task commands. Skill references belong to the shared checkout; case/task/
   candidate files belong to the outcome project. Read
   `docs/CROSS-PROJECT-WORKFLOW.md` before handing analysis into implementation.
3. Keep the original target read-only and put derived artifacts in the active
   repository-local case. `bridge --record` saves a recovery pointer, not
   permission, a completed scope, work items, Evidence or business acceptance.
   Use the inherited `case-init`/scope, timeline/workitem and evidence helpers
   when the target task needs them, within the user's existing authorization.
4. Reuse the active case and settled user decisions when changing tools. A
   technical pivot is not a new project or a reason to restart consent for an
   already authorized action. Record a decision delta and carry forward refs.

## Packed, obfuscated and anti-analysis targets

When the task text or new observations show packing, obfuscation, anti-debug,
anti-VM, anti-hook, dynamic loading, early exit, self-checks or virtualized code,
load the hard-target resources listed in `components/reverse-core/runtime.json`.
They supplement the selected domain instead of replacing it with a fixed flow.

- Preserve the question, input identity, hypothesis, failed path, next probe,
  unknowns and cleanup. Methods and their order follow the actual evidence.
- Sparse imports, unreadable decompilation, a dump or a failed tool are partial
  observations. They do not prove absent behavior or completed reconstruction.
- For tool-triggered early exits, compare unobserved, minimally observed and
  current runs where the environment permits; record observer side effects.
- PE OEP, dump, IAT repair, a runnable copy and recovered semantics are separate
  results. Stop repeated static repairs when self-check or layout failures point
  to a runtime observation instead.
- APK analysis can move across DEX, class loaders, JNI and native code; JS can
  cross browser, worker, WASM and native boundaries. Retain their provenance.
- ADF is a decision overlay for stalled analysis, not another PRIMARY router.
  After repeated attempts produce no new evidence, replan or end as unknown.

## Tools, provider ownership and cleanup

Use actual installed paths from a current tool index. Generate it with
`skills/scripts/refresh-tool-index.ps1` or `.sh` as needed; its outputs are local
and ignored. Tool presence or an MCP registration does not prove runtime health.
The inherited catalogs are detection hints, not a promise that a tool is present.

REA is the official Evidence backend where capable. A failed or missing REA
provider does not disable the inherited raw CLI, debugger, hook or emulator
methods. Select an available method within the active scope and record its
different coverage. Use `skills/ops/rea-delegation-contract.md` for bounded work
items and `skills/ops/process-lifecycle.md` for owned processes and cleanup.
Windows `process-lease.ps1` explicitly lacks complete descendant containment;
its observed cleanup is not equivalent to verified full cleanup. Retain blocked
cleanup where the provider contract requires it.

The current host owns its model and account. Keep old repositories, existing
installations, credentials, global configuration and Craft `--all-tools` intact.
Inherited bootstrap, IDA watchdog/autostart and GUI launchers are optional tools
with their original effects; they are not part of a normal installation. Prefer
the repository-local bootstrap entries in `scripts/`. Prepare another needed
tool only within the authorized environment and write scope, without silently
invoking legacy global installers or persistent services.

## Analysis to reconstruction

Reverse owns the case and analysis narrative; REA owns its native Evidence and
proof records. The lead references those records instead of forging a second
REA ledger. The installed official Spec Kit generated workflow produces reviewed
tasks; current host reasoning supplies content to the actual Craft native engine,
which writes only the bounded candidate and runs frozen checks. Session observation
and offline copying do not replace those components. See docs/NATIVE-COMPONENTS.md.
Analysis-only cases can stop at their requested
report. Reconstruction adds build/run, comparison, proof and obligations.
Preserve `pass`, `fail`, `unknown`, `blocked` and `unsupported` at the actual
scope of each observation. Integrate reviewed results into the main project
only within the requested task.

Reports, diagrams and field-journal updates are conditional on useful results.
No empty reports or new evidence ledgers are needed merely to finish a checklist.

## Inherited supporting resources

- `CTF-Sandbox-Orchestrator/` is the R41 downstream sidecar, loaded on demand;
  its child skills do not add global PRIMARY routes.
- `burp-mcp-full/` restores the inherited source and bridge referenced by tool
  discovery; building or starting Burp is a separate provider operation.
- Linux, macOS and Kali use the shipped `skills/scripts/*.sh` entries. The
  previous repository's separate Kali/global installation tree is not required.
- Historical content and intentional integration patches are recorded in
  `components/reverse-core/preservation.json` and
  `docs/REVERSE-CAPABILITY-AUDIT.md`.
