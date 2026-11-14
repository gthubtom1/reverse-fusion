# Current State

Stage: RF-22
Status: reconstruction-product-v1

RF-17 through RF-22 are closed against `docs/PRODUCT-GOAL.md`. This is a
bounded, evidence-driven reconstruction product: it does not claim that every
future target, packer, obfuscator or runtime provider has already been tested.

Completed product gates:

- Fresh clones own the portable Reverse route from
  `components/reverse-core/routing.json`; an old reverse-workflow receipt is
  optional read-only compatibility input.
- Codex and Pi fixed-sentinel host handshakes pass. Claude CLI starts but is
  blocked by the missing host login/API credential; the record is explicit and
  does not count as a false pass.
- The host-owned Codex Builder generated the APK candidate and completed
  `prepare`, `build`, `check`, `refine`, `return_summary` and `cleanup`; the
  invocation contains no `--model` and records `config_mutation=false`.
- Spec tasks and append-only converge records exist for Web/JavaScript,
  PE/.NET and APK/DEX under `specs/reconstruction-*`.
- WASM ledger: `rol_09e99625528899bcc2b492bdc7b2811b44fb573c13418ff80af0404548039928`,
  `required_open=0`.
- Web/JavaScript: original `ev_d42bef240bdf9e48b3444a5bb947adcc5bb30257a8e492115e421e9cac1e3955`,
  candidate `ev_ff3486e9a5d5cb34105392e5bdfbb2388d416d8c2028ab75ad8ecad4eaa55ed1`,
  comparison `ev_216f5663a396f32a8c09777922294d6149abcee640129d9911fb62e150b47a75`,
  runtime proof `ev_15fee3b64989528f65eacac69ae67f6085bb053619730330dfa448fd0162f8b9`,
  ledger `rol_39c38b659a45e5b080c5dc55870f154eb17b9e484fb998aacba88d07cd579c48`,
  `required_open=0`. Static shape remains `partial`; package/parser scope is
  recorded as unknown in the acceptance record.
- PE/.NET: original `ev_062f2f49691e51cf4fe728d0dca75761220b14432f4ee53a4715429c4f600a16`,
  candidate `ev_4ed5fcd1923341556d97a39443a426d1c9809e71755f71191af465fb372651ab`,
  comparison `ev_8204b1f0b84f883aec5b4480f78865ffbf2faff7ad35c0919e156e96326e5832`,
  runtime proof `ev_c4d41f92991a0bb95aa29499ea1f272cdc3a5b0270a008a48016fcc4d13f1e83`,
  ledger `rol_53dd8e6683c0351977afc491a5c50863e56a390e5925d0c6d63fde1372bebba9`,
  `required_open=0`.
- APK/DEX: original package `ev_cba76f8064e8c1933ee7b4899591dab58aeb658cfe308e6486fa427534ac6284`,
  original class `ev_d9349e30a3eeafaa557a55ee4afd6a18bed7b7d617ffc060b6b1b873112de962`,
  candidate package `ev_a49fc8732219412e40bf3fd1b9440fca4c48ce83636a2ff2df5ac36324055c17`,
  candidate class `ev_323d65a56a365581d436b61b8b0ded6a573edc91446fbee8bdcc18b44dd08c79`,
  comparison `ev_4a0123224c2a1a5daa8124e3dcfb36f5d5f522697c303a4ed3c6285488c8f350`,
  proof `ev_af2166ec8020eafb0b3c0914ba5fd5a51936571407b0bed11749097865d4affa`,
  ledger `rol_b9833a0dd114ad263d96217960a2990d87c9e3629048488d3f4f2379f93762b`,
  `required_open=0`. APK build and static comparison pass; Android runtime is
  `unknown` because this host has no adb device or emulator.
- Global three-state gate: WASM correct candidate `pass`, intentionally wrong
  candidate `fail`, missing Evidence `unknown`.
- Fresh clone `029f4fe093b0d93ff92ca0a1de5565d3f655ecf7` passed contracts,
  plan, doctor, handoff, install/update/uninstall dry-runs, local bridge and
  14 Python tests. Generated Evidence, candidates and
  build outputs remain ignored under `state/` and fixture build directories.

Provider boundaries:

- Craft companion 0.6.1 remains installed with its required `--all-tools`
  argument. Native R46 qualification is still unsupported, while the real
  host Builder path is verified independently.
- Windows REA PTY process capture remains unsupported because descendant cleanup
  is not qualified on this host.
- Full REA JavaScript analysis retains conservative semantic unknowns; the Web
  case closes only its reviewed export obligation and records excluded
  package/parser behavior as unknown.
- APK/DEX Android device behavior requires a future adb/emulator provider.

No old repository, old installer, REA/Craft/Spec Kit installation, host
credential or global client configuration was modified. The next maintenance
action is an upstream review using `docs/UPSTREAM-MAINTENANCE.md`, not an
automatic merge.
