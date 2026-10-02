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
