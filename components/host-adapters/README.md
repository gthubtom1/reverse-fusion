# Host adapters

The repository exposes one host-neutral CLI and shared Reverse/REA/Spec/Craft
core. The selected host supplies reasoning with its existing account and model.

Codex `install --apply --client codex` writes a managed user-level skill and
marked global instruction block pointing to the shared checkout. Pi/Claude use
`connect --client <host> --project-root <outcome-project> --apply` for a thin
project skill, instruction file and connection receipt. Installing the shared
core alone does not connect every outcome project. Connection/removal preserves
unrelated user instructions and does not change credentials, providers or model
settings. See [host project connection](../../docs/HOST-PROJECT-CONNECTION.md).

Adapter completion requires checking the host's actual entry, skill discovery,
tool invocation, project paths and official Spec layout. Shared-core full use
is qualified by representative Codex/Pi runs; a logged-in full-model run is not
required for every adapter. Optional handshake and actual model-use observations
remain separately reported at their observed scope. An unperformed model run
does not imply an incomplete adapter or a successful runtime invocation.
