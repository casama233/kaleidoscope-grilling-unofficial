# A2.8.67 — Java parity repair candidate

This release integrates the reviewed G66 source lineage into canonical main history and repairs additional findings from [the 2026-10-05 audit](JAVA-PARITY-AUDIT-20261005.md). The audit remains an immutable record of the previous baseline. This page records the resulting scope; it does not inherit G66's client acceptance or native receipts.

`client=false`, `production_ready=false`, `pending_client_acceptance`. Source, isolated native probes, full-family admission, saved-world rehearsal and live deployment are separate evidence. Human acceptance follows the authorized development deployment.

| Finding | Implemented change / remaining boundary |
|---|---|
| G01 | This release has a new identity and separates source changes, historical candidate observations and current acceptance. |
| G02 | Integrates the native generation seed and shared Java tree plan, complete canopy preparation, unload deferral and rollback. A transient write failure now retains the seed after rollback so generation can retry. Natural generation and persistence are checked separately from synthetic placement. |
| G03 | Integrates owning-player context for secret-skewer ingredient rendering. Both hands, all profiles, third-person observers and final visual cropping remain human acceptance items. |
| G04 | Uses the configured hot-food saturation multiplier for secret and plated nutrition, with 1.0/1.25/2.0 source regressions. |
| G05 | **Still unsupported in this stable runtime:** there is no authoritative vanilla fortress/new-chunk callback. The existing explicit fresh-fortress producer API remains available. No player-near scan or heuristic replacement of crops is installed. |
| G06 | Integrates corrected native durations, completion identity, release ordering and interaction precedence. Adds the actual 25-tick native completion path when custom eating animations are disabled; manual early-release debit is disabled for that mode. Continuous real input and disconnect behavior still need human acceptance. |
| G07 | Integrates native main/offhand bottle placement, recoverable metadata, layer/selection and animation changes from G66. Source transaction tests do not establish rendered parity. |
| G08 | Reserves deferred Heavy Metal rescue synchronously, respects already-cancelled damage, validates effect identity and life state before settlement, and prevents duplicate rewards. **Java fatal-damage equivalence remains unresolved:** armor, absorption and other addons can change the meaning of before-hurt damage. This release does not claim a native death callback. |
| G09 | Persistent switches control actual native eating duration, Cookery table interception, and Cookery food heat/seasoning. Host handshakes carry the cuisine setting, preserve saved configuration and delivery idempotency, and suppress new heat/seasoning while disabled. Existing food data is retained. |
| G10 | Restores all oil ownership/scheduling indexes on rollback; avoids unchanged native writes; adds source-backed premium-oil particles with bounded, nearby-player emission. Per-cycle native block reads are reused without caching across cycles. Oil remains a bounded script simulation, not a native custom fluid. |
| G11 | Existing quick-sneak interaction remains the Bedrock input adaptation. Arbitrary dynamic inventory icons, Java CapsLock input and per-player numb crosshair movement remain platform gaps; no global HUD replacement is introduced. |
| G12 | Integrates fourth-flip cooked ingredient snapshots and preserves transaction rollback. A native normal-stop/restart probe tests saved snapshots; player slot/hand/disconnect acceptance remains separate. |
| G13 | Adds reproducible native minimal/full-family workload and profiler tools, reuses synchronous cooking/audio state, counts occupied slots without cloning ItemStacks, avoids off-cadence display lookups, reduces duplicate oil/block queries, and records profiler overhead separately. Zero-player server tests cannot certify multiplayer load or client FPS. |
| G14 | Existing public output, stack projection, cuisine and producer contracts remain available. Arbitrary Java callbacks, Create and Maid have no corresponding installed Bedrock modules; they are not represented as completed integrations. |

## Configuration

- `enableEatingAnimations` defaults to `true`. `false` selects hidden native item aliases with a 1.25-second food use duration and ordinary item presentation. Conversion preserves the captured hand, item metadata and failure rollback; changing the setting does not debit food.
- `interceptCookeryTableWhenPlacingPlate` defaults to `true`. `false` lets the host table handle the skewer interaction. Existing plate items retain their own behavior.
- `enableCookeryFoodHeatAndSeasoning` defaults to `true`. The owned host extension persists and publishes this setting through the versioned cuisine configuration handshake. Disabling it prevents new shared heat/seasoning effects and seasoning consumption without erasing already-saved food metadata.

The single Cookery guide contains the corresponding localized notes. The owned board/cuisine host extension is version 0.2.4; it retains the same eight registered host patch targets and eight additive copies.

## Verification and limitations

`verify_current.py` selects the A2.8.67 source gate. Historical G66 receipts remain historical: changed files must pass current source checks and new family admission. The new oil read-reuse test changes a cell between cycles to verify that the optimization does not hide world edits. Tree tests inject write failures and verify retained provenance and successful retry.

`native_performance_check.py` assembles identical 64-grill/192-slot and 32-oil-source workloads in the dependency closure and the complete family. The two runs use identical host extension bytes. Script overlays create only test blocks and containers in a separate world, reset cooking stages to sustain load, and report their own hashes and experimental lab status. They create no simulated players. Long profiler recordings are not used as evidence of ordinary runtime memory growth: the same workload must also run without recording.

The stable `@minecraft/server` 2.9.0 API used here does not expose the experimental `getGeneratedStructures` method. Microsoft's [experimental method reference](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/dimension?view=minecraft-bedrock-experimental#getgeneratedstructures) identifies it as pre-release. A generic world-generation replacement cannot distinguish all fortress crops from other structures while preserving the Java structure boundary. Enabling a new live experiment is outside this repair; G05 remains explicit.

## Bounded native results

The [source and native evidence](evidence/parity-repairs-2.8.67-native.json) binds the exact runtime files and test reports. In the 180-second unprofiled workload, the minimal closure improved from 16.36 to 19.71 TPS and the full 41-pack family from 15.70 to 18.77 TPS. Both final runs had zero errors or watchdog warnings. These are single measurements on a shared host; the full stress workload remains below 20 TPS and is not a multiplayer capacity or client FPS acceptance claim.

The new-world forest probe found a naturally generated tree with four log blocks, eighteen leaves and five initially fruiting leaves. Its geometry and existing fruit survived a normal restart. The exact tree implementation still matches this release; this bounded probe does not certify unrelated later runtime changes. The final fourth-flip probe is bound to all current owned runtime bytes and checks three slots across a normal stop/restart, including registry changes after snapshot creation.

Full-family static/BDS/saved-world admission, reviewed receipts and installation are produced by the canonical family update workflow after the reviewed Git merge. They are not asserted by the isolated probe report.
