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
