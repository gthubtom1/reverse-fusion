# Decisions

## RF-001 Single repository

This project is published as one GitHub repository. Official components are described by manifests and fetched through their official distribution; owned enhancements live in this repository.

## RF-002 Official by default

REA and Spec Kit remain official until a documented capability gap justifies a
local fork. Craft is currently a repository-owned bounded interface with an
upstream reference, not an upstream-plus-patch distribution. The four historical
patch names are provenance only; no patch is distributed or replayed here.

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
or downloaded by Reverse Fusion. The default Builder is that agent in the
current conversation, not another CLI invocation. Frozen-input and allowed-write
observations are separate from independent business acceptance. Child CLI
transport is optional and has its own live login/quota/cleanup status.

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

## RF-011 Nested subcases

Normal development is a host-native baseline, not a separate universe. A main
project may create an isolated analysis or reconstruction subcase at any point:
the subcase owns its target path, route, Evidence, tasks and candidate; only
reviewed Evidence-backed conclusions flow back into the main project. This
allows a website, desktop application, APK or another project to be researched
mid-development without forcing every main project into reconstruction mode.

## RF-012 Local domain skill ownership

The new repository carries a pinned copy of the enhanced reverse-skill domain
skill bodies under `skills/`. Route metadata alone is insufficient for a fresh
clone; the local route reports `unavailable` when its descriptor or referenced
skill body is missing. The old reverse-skill checkout remains read-only and
optional compatibility input.

## RF-013 Evidence and host-boundary records

Representative records live under the stable `evidence/rf22/` path. RF-25 found
that path normalization had changed hash-covered fields without changing IDs;
it replaces those invalid records with raw authenticated runs. Historical
absolute paths are observations, not deployment configuration. Contracts check
file hashes; official REA additionally checks identity, bundle links and a real
tamper counterexample. Optional host calls compare known configuration hashes;
changed/unobservable snapshots and uncertain descendant cleanup are never
declared verified merely because the root invocation returned.

## RF-014 Preserve content and executable handoff separately

RF-24 audits enhanced reverse-skill at its recorded pin. Skill text equality is
not sufficient when a domain references resources outside skills or a route
does not carry downstream context. Restore those supporting resources, publish
current portable rules, expose required reads, and report missing resources.
Keep hard-target methods adaptive and provider neutral. The 603-file inventory
records exact current upstream/local digests and adaptation reasons; it is
content preservation, not target runtime acceptance. All local route entries use the product JSON; the
original skills JSON remains the original compatibility baseline.

## RF-015 Repository-stored deployment and honest scope

`docs/AGENT-BOOTSTRAP.md` is the only deployment action contract. The user gives
the repository link; the selected current host discovers paths and installs a
local venv/receipt. Analysis does not require reconstruction tasks. Uninstall scripts remove the
local venv/receipt, retain vendor/case assets and implement no transaction journal.

## RF-017 Codex cross-project adapter

When Codex is the selected host, install writes a user-level `reverse-fusion` skill
and a marked global `AGENTS.md` block that point to this checkout's router. The
adapter is deliberately thin: it preserves the current project as the work area,
does not copy domain skills, choose models, or start providers, and can be skipped
with `--no-global-adapter`. Uninstall removes only the managed block and skill.

## RF-016 Bounded integration proof authority

Repository-owned bounded verifiers may use the pinned official REA serializer
under the explicit integration exception in `skills/reconstruction/SKILL.md`.
They must recheck artifact hashes, perform the declared finite observations and
retain links. They do not impersonate REA native process verification. Web's
bounded answer ledger is separate from its complete graph's open obligations;
APK manifest/member equality does not prove method-body or device equivalence.
