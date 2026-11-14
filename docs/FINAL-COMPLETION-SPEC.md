# Final v1 completion specification

The project is final only when every gate below is either verified or has an
explicit supported boundary recorded in the capability matrix. Intermediate
milestones are progress records, not final acceptance.

Current release status: **accepted within the declared capability boundaries**.
The gate-by-gate evidence and retained provider limits are recorded in
`docs/FINAL-RELEASE-ACCEPTANCE.md`.

1. A fresh clone can run the repository-local install/plan/doctor path on each
   supported host family without modifying global client configuration.
2. Reverse remains the only route and case owner; official REA, Spec Kit and
   Craft identities are pinned by manifests.
3. REA Evidence, unknown, comparison and obligation pointers have typed adapters
   and at least one real Evidence-driven vertical slice.
4. Spec Kit project-local artifacts preserve source references, tasks and
   append-only converge records.
5. Craft has a qualified bounded backend or a repository-owned bounded fallback
   with the same six-tool, single-writer and cleanup contract. The current
   fallback is `local-bounded-worker`; a mere MCP tool listing is not acceptance.
6. Codex, Pi and Claude host plans are portable; actual host loading is reported
   separately from discovery.
7. The target capability matrix covers the declared families and records
   unsupported provider surfaces without pretending universal compatibility.
8. The vertical slice passes for a correct candidate, fails for an intentionally
   wrong candidate and returns unknown when Evidence is absent.
9. Source drift, rollback, upstream update, cleanup failure and context handoff
   are persisted and mechanically checked.
10. Tests, contracts, docs, checkpoints and GitHub remote are clean and agree.

The final product claim is “the framework is complete within its declared
capability boundaries.” It is not a claim that every future target has already
been analyzed.
