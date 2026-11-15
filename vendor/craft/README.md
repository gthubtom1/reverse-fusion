# Craft runtime and source

The official portable CLI and the repository-owned native external-writer adapter
are separate artifacts. Their exact identities are in this manifest and
`components/craft-native/manifest.json`. Downloads, source checkout and build
outputs remain ignored. The adapter links the actual pinned Craft Rust engine;
it delegates workspace creation, candidate writes/edits and bounded commands to
that engine without starting a second Study workflow or selecting a model.

Run scripts/bootstrap-craft.ps1 for the pinned Windows x64 engine adapter;
-BuildFromSource verifies and replays the recorded patch. Engine lifecycle,
quoted commands, nonzero exit, timeout cleanup and writer exclusion were tested.
Target composition is tracked separately in the RF-28 checkpoint. A capability listing is
not evidence of a successful build or original/candidate equivalence.
