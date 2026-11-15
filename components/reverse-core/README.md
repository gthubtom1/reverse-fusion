# Reverse core

This directory owns the portable route and case boundary for Reverse Fusion.
`routing.json` is a versioned data snapshot of the upstream route semantics;
`router.py` executes it without a receipt, provider, credential, or model. The
generated `routes/R*.md` files are local route descriptors and the root `skills/`
copy contains the actual domain instructions used by a fresh-clone handoff.
The route is reported unavailable if either its descriptor or its local skill is
missing.

The installed enhanced `reverse-skill` remains a read-only compatibility source
when explicitly requested with `reverse-fusion bridge --source external`. Its
result is reported as `external-route-pass` and never replaces the local route
owner. A missing or unusable external installation is reported as
`unavailable`; it cannot make local routing fail.

Route selection is triage, not business acceptance. A selected descriptor must
still hand off to the target-specific analysis, REA Evidence, Spec tasks,
host-owned Builder, and independent comparison contracts.

RF-24 adds `runtime.json`: routes return the concrete `required_reads` and
`missing_support`, including relevant hard-target overlays when the hint
describes protection or anti-analysis. `RULES.md` applies the same transition
when difficulty is discovered later. `bridge --record` carries these refs into
the case. Missing required support makes that route unavailable.

`preservation.json` records the pinned enhanced content and reviewed integration
patches. The existing `contracts`/`doctor` check verifies these files rather
than introducing another validator. The inherited PowerShell/Bash route entries
read this directory's effective `routing.json` when present; the inherited
`skills/config/routing.json` stays as the upstream compatibility baseline.
