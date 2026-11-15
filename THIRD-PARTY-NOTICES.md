# Third-party notices

Reverse Fusion carries a repository-owned copy of the domain skill content from
the enhanced `reverse-skill` source pinned in `SOURCE-MANIFEST.json`. The copied
files are under `skills/` and retain the upstream MIT license in `skills/LICENSE`.
The local copy is the fresh-clone skill handoff; the old reverse-skill checkout
and its installer remain outside this repository's write scope.

The same pinned source supplies `CTF-Sandbox-Orchestrator/` (its separate
license remains in `CTF-Sandbox-Orchestrator/LICENSE`) and `burp-mcp-full/`
(covered by the source MIT license retained in `skills/LICENSE`). They are
supporting resources loaded or built on demand, not automatically registered
MCP services or additional PRIMARY routers. Exact file digests and the small
integration patch list are in `components/reverse-core/preservation.json`.

REA, Spec Kit, Craft, WABT and JADX retain their own upstream identities and
licenses. Their source URLs and pins are recorded in `SOURCE-MANIFEST.json` and
`components/official/manifest.json`.

RF-28 distributes a native adapter linked to Craft's pinned Rust engine under
its MIT OR Apache-2.0 terms. Its repository-owned driver and replayable Windows
patch are in `components/craft-native/`. Release archives include complete
dependency notice/license texts; the inventory is
`components/craft-native/dependency-notices.json`, with supplemental license
sources/digests in `components/craft-native/licenses/manifest.json`. MinGW/GCC
runtime terms and exception are included in the archive. The supplemental 0BSD
text is the SPDX standard text; yaxpeax-arm declares 0BSD in its package metadata
and ships no separate license text in that pinned package.
