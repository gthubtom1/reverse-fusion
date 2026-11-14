# Reproducible WABT assets

WABT binaries are downloaded into this ignored directory by
`scripts/bootstrap-wabt.ps1`. The repository commits only the pinned manifest;
the archive is never trusted until its SHA-256 matches the manifest.
