# Feature: APK/DEX reconstruction case

## Source references

- Reverse route: `R1` (`components/reverse-core/routes/R1.md`)
- Original REA Evidence: `state/rea-apk-original.json` and
  `state/rea-apk-original-class.json`
- Candidate REA Evidence: `state/rea-apk-candidate.json` and
  `state/rea-apk-candidate-class.json`
- Provider: `jadx-headless-mcp@0.7.1`, pinned by
  `vendor/jadx-headless-mcp/0.7.1/manifest.json`

## Functional requirements

- FR-APK-001: Preserve the package, launcher manifest component and
  `com.reversefusion.Answer` class member inventory.
- FR-APK-002: Build a candidate APK with javac, D8 and AAPT in the repository
  workspace.
- FR-APK-003: Compare static package/class Evidence and keep Android runtime
  status `unknown` when no device or emulator is available.
