# Reproducible JADX headless provider

REA's Android/DEX tools require the caller to provide the official
`jadx-headless-mcp` bridge. The repository commits only the pinned release
manifest; the JAR is downloaded into this ignored directory by
`scripts/bootstrap-jadx.ps1` and is accepted only after SHA-256 verification.

The bootstrap writes inside this repository and does not modify Android,
JADX, REA, Java, or host-global configuration. Set `REA_JADX_MCP_JAR` to the
returned absolute path for REA Android commands.
