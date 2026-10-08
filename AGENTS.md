# Repository scope

This workspace is the unofficial **Kaleidoscope Grilling** Bedrock port.

Before any remote mutation, read `.repo-target.json` and verify BOTH the authenticated repository full name and numeric repository ID. The only allowed write target for this project is `casama233/kaleidoscope-grilling-unofficial` (ID `1377218440`). A similarly named repository is not an alternative. Do not change another repository without a new explicit user instruction.

Preserve existing assets and UUIDs during imports. Read upstream sources as needed, but do not write to upstream repositories. Do not publish the user's original Cookery mcaddon, third-party private scripts, worlds, credentials, browser profiles or machine-specific logs.

Keep migration status honest: files in a local artifact are not automatically in GitHub. Do not count planned or recovered-but-unverified work as delivered. Before reporting success, read the remote HEAD/files back and compare expected content hashes.

The guide must remain one Grilling entry in the existing Cookery guide, not a new physical guidebook. Notebook tests with mock player adapters do not certify Minecraft persistence or guide UI integration. Asset previews do not certify engine rendering.

Guide changes must also follow `docs/GUIDE-STANDARD.md`: shared host navigation, localized item pages, honest acquisition status and no host file replacement. Its six cooking categories are distinct from Tavern's seven brewing categories.

# Canonical baseline

- HUD behaviour must follow the pinned original Java release: source-backed interaction messages keep their original triggers/keys/arguments; original graphical eating progress uses the original textures, dimensions and 25-tick checkpoint. Do not add polling text, numeric machine summaries, ASCII eating bars or arbitrary reminders. Java machine panels are disabled by default (HudControl.enabled); do not enable them as a substitute for client parity. Legacy interactionFeedback/eatingProgress stay silent; Java messages use javaInteractionFeedback and exceptional storage faults use interactionFailure for operator diagnostics only. Do not clear the shared actionbar on eating completion. Script/BDS checks cannot certify rendered client parity.

- Follow `docs/BASELINE-MAINTENANCE.md`. Own fixes belong to canonical runtime; do not introduce gameplay transforms in a private builder or BSM hook.
- A changed exported file requires a new release identity, lock/history update and functional verification. Never reuse the same version for different content.
- The owner’s 2026-10-03 instruction is standing authorization to update luosen live after every completed functional repair/development candidate, including the current candidate. Finish canonical PR/checks/merge, full-family static/BDS checks and saved-world rehearsal, then back up, normally stop/restart and deploy the exact candidate for the owner to test. Do not wait for pre-deployment human client acceptance or request the same deployment permission again. Documentation-only changes that do not change exported runtime need no pack bump or live restart.
- Use canonical family_bundle/family_guard and a consistent stopped-world backup with a rollback version. Register this standing instruction, its time and each candidate’s exact receipt SHA256 in deferred_client_acceptance; never reuse a different receipt hash or bypass admission. Keep client=false, production_ready=false and pending_client_acceptance until actual human acceptance. See the family maintenance procedure; deployment is not rendered-client verification.

# Owner 2026-10-06: remote source, current Java and adaptation

- All repairs and compatibility adapters must be committed, reviewed and merged in their canonical Git remote before deployment. A local artifact or local-only Git commit is not remote delivery. Public owned code belongs to the three canonical repositories; private integration remains in the verified private remote, never in a public repository. Do not place worlds, credentials or complete private author scripts in the public repositories.
- Track the newest available Java author release for each maintained Minecraft/loader branch, including Tavern, World Liquor and Grilling. Read the current `family/java-upstream.json` and BSM `addon_quality/senluo-java-upstream-status.json` before repair/release. Refresh stale or failed checks. Keep Forge/NeoForge/version branches distinct; explicitly record source revisions, new releases, adaptation gaps and which current bytes were reviewed. Do not keep an obsolete fixture as the permanent gameplay authority or label a version-pin-only update as complete adaptation.
- Aim for Java parity of mechanics, recipes, quantities, timing, interactions, persistence, models, animation, sound and effects. Fix reproducible implementation gaps in canonical source. Separate implemented parity, explicit platform adaptations and unimplemented/unverified behavior. Original quiet immersion and the user's explicit extensions remain authoritative. Static/SDK/BDS checks are not rendered-client or complete gameplay acceptance.
- Keep adapters current with the author version being installed: dependency UUID/version, host API, producer/consumer contracts, guide data and saved ownership must be reviewed together. Do not drop existing working repairs while updating an author package. Rehearse UUID/data migrations before adopting live data.
- Avoid meaningless duplicate hashing or repeated suites. Reuse successful CI/BDS evidence for the exact unchanged candidate; invalidate on relevant input changes. Verify source/release identity, author archive provenance, candidate content, stopped-backup/migration integrity and deployment/readback at the actual state boundaries. Do not add a second source of checksum truth or treat hash equality as Java functional parity.

# Owner 2026-10-08: reorganization with minimal tests

- Start from the current work index and relevant canonical modules, not a fresh traversal of every historical report. `README.md` is the current authoring entry; `docs/PARITY-MATRIX.md` is the current parity index. Audit snapshots and version status files retain their original evidence scope.
- Prefer existing checks. Add a test only for a concrete, material failure that existing checks cannot detect; do not copy an implementation formula, enumerate cosmetic combinations or test documentation merely to increase counts. Use targeted local diagnosis, then let the PR's required CI run the full suite. Do not repeat successful unchanged evidence locally.
- Keep conserved items, single settlement, rollback and saved ownership guards. Build/reference/byte checks are prerequisites, not gameplay or client acceptance. Preserve necessary integrity checks at actual source/release/deployment boundaries.
- Current packaging reads canonical BP/RP directly. Do not run historical `build.py` or `augment_a*.py` to rebuild the maintained runtime. Legacy reconstruction must use a new explicit isolated output outside Git worktrees; history cannot be installed as a replacement for current source.
- Tooling/documentation changes without exported runtime changes do not consume a pack version, create a game candidate or restart LIVE. Runtime fixes retain the existing PR/full-family/deployment requirements. Preserve other active worktrees and unique unmerged fixes.
