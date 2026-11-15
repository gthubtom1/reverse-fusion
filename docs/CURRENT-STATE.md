# Current State

Stage: RF-25
Status: reconstruction-product-v1-final

Product version: `1.0.0`. The retained Reverse domain contract version is
`components/reverse-core/VERSION` (`1.9.0`); these are separate identities.

RF-25 rechecks the RF-22 product claim and RF-23/RF-24 hardening against actual
code, source files and execution. Historical checkpoints remain historical;
the current acceptance is this file, `docs/FINAL-RELEASE-ACCEPTANCE.md` and
`checkpoints/RF-25-20261115-001.md`. The finite audit and declared integration
release gates are closed. Future target variants are new cases, not a requirement to
pre-execute every possible program, architecture or protector.

## Current implementation and observations

- Fresh clones carry the local Reverse router, route descriptors, domain skills,
  required reads and hard-target handoff. An old reverse-workflow receipt is
  optional read-only compatibility input, not an installation requirement.
- `docs/AGENT-BOOTSTRAP.md` is the stored URL-only deployment entry. It installs
  a repository-local venv, checks contracts and records the selected host. It
  does not globally inject skills into other projects; another workspace must
  explicitly read this checkout's entry or deploy its own checkout.
- Normal development does not force a case. Analysis cases retain route,
  Evidence, limitations and conclusions. Reconstruction adds frozen tasks,
  a candidate, build/run, comparison, proof, cleanup and an obligation ledger.
- The default Builder is the agent in the current conversation. `session
  prepare/check/refine/finish` freezes task/research hashes and observes allowed
  candidate writes. These observations are not business acceptance. The current
  host generated eight source files for Web, .NET and APK, then checked,
  reviewed/refined and finished that bounded session. No child CLI, account,
  provider or model is required for this path.
- Child host CLI transport is optional. The RF-25 child Codex invocation reached
  `out of credits` and is `blocked`; earlier Codex/Pi sentinel passes are not
  current availability claims. A fixed-sentinel probe measures transport, not
  instruction loading or target business behavior. Current probe results are
  separately recorded in `docs/PROVIDER-STATUS.md` and the RF-25 checkpoint.
- Builder checks now detect changes/deletions of existing files, stale primary
  output and unsafe links. Frozen context reaches refinement. Codex receives
  long prompts through stdin rather than Windows command-line arguments.
- The RF-25 runners stop on failed native commands rather than accepting stale
  output. Provider versions and checksums remain pinned; writes and cleanup
  stay inside the canonical repository boundary.

## Representative target Acceptance

The current archived identities and file hashes are indexed by
`evidence/rf22/manifest.json`. The `rf22` directory name is retained for stable
links; RF-25 regenerates the records from real runs and retains their original
hash-covered fields. Absolute paths in historical observations are not deploy
configuration and must not be substituted while retaining an Evidence ID.

| Target | Observed scope | Remaining boundary |
|---|---|---|
| WASM | WABT execution, original/candidate/interface/proof Evidence and bounded ledger; correct=`pass`, wrong=`fail`, missing=`unknown` | bounded fixture only |
| Web/JavaScript | four finite Node export traces match; bounded answer obligation ledger ready | static shape partial; full graph ledger is unknown with 5 total / 1 verified / 4 required open obligations (2 packaging, 2 application/parser) |
| PE/.NET | .NET 8 build, managed member comparison, finite executable traces and bounded ledger | larger/native/obfuscated targets require their own Evidence |
| APK/DEX | javac/D8/AAPT build, package/manifest and Answer member projection comparison, static ledger ready | Android runtime=`unknown`; fixture MainActivity is not a functioning Android Activity |

The integration proof adapters use the pinned official REA serializer, validate
artifact SHA-256 and retain Evidence links. They are repository-owned bounded
verifiers, not REA's native process verifier. Archive admission passed the
official `parseEvidence`, bundle-link and tamper-rejection checks; the previous
path-normalized archive is superseded because its IDs no longer authenticated.
The full Web graph ledger is archived separately as `evidence/rf22/web/full-ledger.json`.

## Preserved capabilities and provider boundaries

- The source inventory retains 603 files from enhanced reverse-skill
  `3fdbb927b474dc23ef2e19403d5464dcb9702cec`: skills 453, CTF sidecar 136,
  Burp 14. Exact current adaptation counts and reasons live in
  `components/reverse-core/preservation.json`, not an independently maintained
  count in this document. Packing/unpacking, anti-analysis, OLLVM, Android
  DEX/JNI/anti-Frida, .NET obfuscation and JS VM/WASM methods remain available.
  Preservation is not proof that every protected target executes successfully.
- Official REA is `6.9.0`; Node must satisfy
  `^22.23.4 || ^24.22.1 || >=26.12.1`. Node 24.20.0 does not satisfy this pin.
  WABT is `1.0.42`; JADX headless MCP is `0.7.1`.
- Spec Kit source pin reports `1.4.1.dev0`; the earlier CLI execution receipt
  reports `1.4.0`. Task artifacts can be used without installing the CLI for
  every deployment; source identity and a local CLI execution are distinct.
- Craft is `repository-interface-only`. The four historical patch names are
  references, not distributed or replayed patches. The companion's
  `--all-tools` argument is preserved. Current companion health is unobserved;
  native R46 qualification remains `unsupported`.
- Windows REA PTY descendant cleanup remains unsupported. Android device
  runtime and Web graph obligations retain their explicit unknown states.
- Uninstall scripts remove the repository venv and installation receipt;
  pinned vendor assets remain until explicitly removed. No receipt transaction
  journal or automatic global rollback is implemented.

## Next action

No audit implementation task remains. Use the deployed checkout for normal
development or a new target case; selective upstream review follows
`docs/UPSTREAM-MAINTENANCE.md` when requested.

The remote clone of `a643b958774dc8d90b3be29f68aff5d5d0f0b91a` started without
old state, installed product 1.0.0 into a new venv, passed contracts/plan/doctor/
handoff, selected-host receipt, hard-target route, 37 product tests and 39
reconstruction tests. Native provider failure stopped before stale acceptance,
POSIX traversal was rejected, and Node 24.20.0 was rejected by the precise
REA engine gate. Final documentation closure follows that source commit; its
checkpoint records this tested code identity rather than claiming another
machine or every provider was executed.

Old repositories, old installations, host credentials and global configuration
are outside this repository's write scope.
