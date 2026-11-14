# Reverse core

This directory owns the portable route and case boundary for Reverse Fusion.
`routing.json` is a versioned data snapshot of the upstream route semantics;
`router.py` executes it without a receipt, provider, credential, or model. The
generated `routes/R*.md` files are local route descriptors and the stable
handoff surface for a fresh clone.

The installed enhanced `reverse-skill` remains a read-only compatibility source
when explicitly requested with `reverse-fusion bridge --source external`. Its
result is reported as `external-route-pass` and never replaces the local route
owner. A missing or unusable external installation is reported as
`unavailable`; it cannot make local routing fail.

Route selection is triage, not business acceptance. A selected descriptor must
still hand off to the target-specific analysis, REA Evidence, Spec tasks,
host-owned Builder, and independent comparison contracts.
