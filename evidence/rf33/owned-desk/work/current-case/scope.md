# Case Scope

## meta
- case_id: current-case
- operator: Codex
- primary_skill: js-reverse

## auth
- status: granted
- basis: own_system
- evidence_of_auth: User requested copying, analyzing and recreating the supplied repository-owned local application; README confirms owned fixture.

## in_scope
- assets:
  - desk-original
  - outputs
  - work/current-case
- activities: [read, copy, analyze, local_execution, browser_test, independently_implement, package]

## out_of_scope
- activities: [external_services, modify_original_source, shared_repository_changes]

## network_profile
- mode: lab_only
- allowed: loopback HTTP for independently served original and candidate

## signoff
- ready_for_act: true

The bridge created this case before scope initialization. No second case is created.
All test storage is isolated in fresh browser contexts. No user data is read.
