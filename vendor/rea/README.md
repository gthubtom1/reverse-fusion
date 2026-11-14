# Reproducible REA runtime

The official `rea-agents@6.9.0` package is acquired into this ignored
directory by `scripts/bootstrap-rea.ps1`. The manifest pins npm integrity and
the package is launched with a process-local WABT path. No global REA or Codex
configuration is changed.
