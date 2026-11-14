# Decisions

## RF-001 Single repository

This project is published as one GitHub repository. Official components are described by manifests and fetched through their official distribution; owned enhancements live in this repository.

## RF-002 Official by default

REA and Spec Kit remain official until a documented capability gap justifies a local fork. Craft starts as an upstream-plus-patch bundle.

## RF-003 Old projects are read-only

The old reverse-skill, old installer, existing REA/Craft/Spec Kit installations and current host configuration are outside this repository's write scope.

## RF-004 One CLI

The repository exposes one `reverse-fusion` CLI with plan/install/doctor/accept/update/uninstall/handoff/contracts subcommands. Small checks are modules, not separate command scripts.

## RF-005 Persistent handoff

The repository stores project context, current state, source manifest, decisions, upstream policy and checkpoints so a new agent can resume after context compression.

## RF-006 Portable local Reverse owner

RF-17 makes `components/reverse-core/router.py` and its versioned
`routing.json` the default route owner. The previous enhanced `reverse-skill`
remains a read-only, explicitly selected compatibility source. This closes the
fresh-clone receipt dependency without introducing a second runtime route owner.

## RF-007 Host-owned Builder and model boundary

The repository owns task scope, output paths, checks and cleanup. The current
Codex/Pi/Claude host owns its account, provider and model; no model is selected
or downloaded by Reverse Fusion. A real host Builder is accepted only when its
candidate writes, six-tool trace and cleanup are directly observable.

## RF-008 Bounded target ledgers

Each representative target has its own Spec tasks, original/candidate Evidence,
comparison, proof and obligation ledger. A ledger may close a reviewed bounded
obligation while retaining REA-generated unknowns for package, parser, device or
dynamic behavior outside that case; those unknowns are recorded explicitly.

## RF-009 APK provider bootstrap

The official `jadx-headless-mcp@0.7.1` bridge is caller-supplied through a
repository-local checksum manifest and bootstrap script. The JAR is ignored
from Git history and is never installed into global JADX, REA, Java or host
configuration.

## RF-010 RF-22 completion label

`reconstruction-product-v1-final` is written only after the four representative
chains, host Builder, three-state acceptance, fresh-clone lifecycle, provider
boundaries and documentation consistency have direct Evidence. Future targets
start new cases or small capability updates; they do not reopen the completed
product architecture merely because every variant was not pre-executed.
