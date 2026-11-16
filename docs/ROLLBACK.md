# Rollback

Rollback acts on this repository only. Inspect `git status`, save wanted local
work and identify the exact commits before reverting. The pre-RF-25 baseline
is `2bcb7d4bdc02b1edcde5855c40445590822d415c`; the RF-25 checkpoint records
the audited replacement commit. Use `git log --oneline` and revert the relevant
RF-25 changes in reverse order, or inspect the old revision in a separate
checkout. Do not reset unrelated user changes.

The historical RF-24 changes are enumerated by
`git log --reverse --oneline 481e936..2bcb7d4`. This is a source-history boundary,
not an instruction to revert all later work automatically. Old Evidence from
that baseline includes the invalid path-normalized archive; restoring it also
restores that limitation and must not be called an authenticated archive.

## Installation and providers

- CLI `uninstall --apply` removes this checkout's `state/install.json` and, when the
  receipt records it, the managed Codex user-level adapter. Existing unrelated
  content in the user's global `AGENTS.md` is preserved.
- `scripts/uninstall.ps1 -Apply` or `scripts/uninstall.sh` removes the repository
  venv and receipt after canonical containment checks. Vendor assets remain.
- For an upstream/provider regression, restore the previous manifest and adapter
  commit together. Recreate only the affected repository-local vendor asset
  with its pinned bootstrap and rerun its focused check. Do not replace an
  existing global tool installation or rewrite host credentials/configuration.
- Case records, original Evidence, Spec features and candidates are not generic
  uninstall garbage. Preserve them unless the user explicitly wants that case
  removed. Generated build/cache artifacts may be removed within the verified
  repository or named case path.

RF-31 atomically replaces owned files and rolls back the managed skill, AGENTS
and install receipt when install/uninstall reports an I/O failure. Fault-injection
checks cover both entry updates and receipt failures. This is not a durable
cross-process transaction journal or a machine-power-loss recovery guarantee.
If a child call times out or
descendant cleanup is uncertain, record cleanup as unknown/blocked and resolve
that writer before starting a replacement. Do not promote a configuration
snapshot or a returned root process into proof that all descendants ended.
