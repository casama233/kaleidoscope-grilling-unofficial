# A2.8.73 — Cookery 1.6 reconciliation with bottle repairs

Locally frozen 2.8.73 integration candidate; native acceptance and BSM gates remain open. This reconciliation starts at published main `3e83eb492ad99a725296d5cd4027643eba84c845` and integrates the bottle work from draft PR135 `0c33806e570219a60c5d063a7d4fef536f49c5fc`.

## Preserved branches and collision

Published main's 2.8.72 adapts G69 to author Cookery 1.6.0. Its existing release-history entry and release are unchanged. PR135 independently used 2.8.72 for bottle fixes with Cookery 1.0.8. These are different contents with colliding identities; the draft is not substituted for the published release.

The old bottle status is preserved as `PR135-G72-BOTTLE-CANDIDATE.md`. Its native evidence remains pinned to its original source/archive in `NATIVE-BOTTLE-G71-20261006.json` and `NATIVE-BOTTLE-G72-20261006.json`. Those observations do not transfer to this Cookery 1.6 reconciliation.

## Combined source

- Preserve current-main Cookery 1.6 manifests, board API adapter, catalog host reference, host checker and reference fixture, bridge guard and historical host guards
- Retain all 64 finished bottle icons,16 fill proxies, ordered reflected ingredient geometry and metadata-safe EMPTY/PENDING mechanics
- Retain synchronous post-success pickup refresh, rollback isolation and retry behavior
- Keep all bottle model/texture bytes equal to PR135
- Derive future release installation text from reviewed canonical host dependencies; do not rewrite an existing release
- Fix plated secret-skewer aliases dispatching ingredient finish effects/remainders through the canonical ID, preserving the original stack and transaction ordering
- Replace advanced-rack forms with exact fixed 5+4 cell interactions, shared hit/display geometry, and direct filtered bulk return; this is the owner-requested interaction extension
- Update the existing Cookery guide in three languages for those controls (guide 0.3.32)
- Add source-derived Java custom-skewer GUI reference tooling; native arbitrary-ingredient inventory rendering remains unresolved, with scoped G72 reproduction evidence
- Keep current published 2.8.72 history intact, and use 2.8.73 only after fresh collision checks and an explicit new freeze

## Current verification and blockers

The integrated canonical source gate passed locally on 2026-10-06 (482 relative imports), including the plate alias, direct-rack, bottle, guide, conservation and all eight Cookery 1.6 host-target checks. The exact later rack block/guide deltas are explicitly declared in historical label conservation checks; old release assertions remain intact. New publication-text tests validate both reviewed host pairs and reject mismatches. Compiled CI, native G73 and migration acceptance are separate and still pending. Main remained 3e83eb49 and no 2.8.73 remote tag/branch was found immediately before the first local freeze.

The required current BSM upstream status is unavailable. The owner explicitly authorized local repairs and Git draft submission on 2026-10-06 at 12:33 UTC while keeping BSM verification mandatory before merge, release or deployment. No BSM status freshness or success is inferred. A separate public check found the author CurseForge file pages still label Forge 1.20.1 file 8726006 and NeoForge 1.21.1 file 8726014 as latest 1.1.1 releases (2026-08-24). Full file-list retrieval was unavailable and the displayed page crawls were 2–3 days old. The author's GitHub release list was empty; README says 1.1.1a while branch properties and latest source commit `9a1acdab27698457bec16c9362678e574895a28c` say 1.1.1. This is recorded uncertainty, not a newer binary release or complete Java adaptation.

Official sources:
- https://www.curseforge.com/minecraft/mc-mods/kaleidoscope-grilling/files/8726006
- https://www.curseforge.com/minecraft/mc-mods/kaleidoscope-grilling/files/8726014
- https://github.com/breezeth-CN/KaleidoscopeGrilling

G73 + Cookery 1.6 native behavior, saved-world migration, full-family compatibility and client acceptance remain untested. No release, merge or live deployment is authorized by this draft.

Current core coverage and open work: [Java parity checklist](JAVA-PARITY-CHECKLIST-20261006.md), [rack controls](RACK-DIRECT-INTERACTION.md), [inventory rendering limits](CUSTOM-SKEWER-INVENTORY-RENDER-LIMITS.md).
