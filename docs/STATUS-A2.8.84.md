# G84 plate follow-up candidate

Preparation is based on G83 public source `69bfc1b97531679e10ed7d225992a1c5985e0a14`. This is a fresh diagnostics/body-alignment review candidate; the G83 candidate remains unchanged. No merge, release or live deployment is authorized in this task.

## Native G83 result and fresh-spawn yaw

Actual Bedrock 1.26.52.3 with exact G83 archive SHA256 `750bd04ec0a9209eb73b4adcf2a91c47782e35aa6c48bc49e3b7025bda4619d9`: the preserved mushroom-stew/golden-apple/carrot plate rendered its complete shaft and three distinct food colors immediately, without a refresh. Empty-hand retrieval cleared the world mesh and returned the matching full held skewer; reinsertion restored it. Save/reload retained the content and full food mesh. This is one plate/one facing, not all counts/facings, Java comparison, audio or full client acceptance.

A matched-camera fresh placement at 03:39:05 UTC showed a slightly diagonal shaft, then at 03:39:18, without intervening input or reload, the shaft aligned with the tray. This separates fresh helper body-yaw settling from loss of saved plate pose. Source count1 has zero slot yaw; actor facing is deterministic and the model root has no rotation. The appearance difference is not an authored diagonal slot or a shape-variant shaft rotation.

## Narrow body-rotation preparation

The plate-only helper now opts into [`minecraft:body_rotation_always_follows_head`](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitycomponents/minecraftcomponent_body_rotation_always_follows_head?view=minecraft-bedrock-stable). The official contract matches body rotation to head/facing and requires format1.21.90; this helper uses format1.26.0. The helper has no conflicting body-rotation blocker, cardinal quantization, AI behavior or native runtime override.

No global rotation component, repeated teleport loop, mesh change or arbitrary rotation correction is added. The existing source yaw is still applied to the actor; original 3–5-skewer diagonal slot yaws remain valid. Grill/rack helpers, plate storage, metadata, ownership and transactions are untouched by this body-only preparation. The canonical authoring tool generates the component; installation/package code does not patch it.

Focused binding/pose tests and the historical eating-animation conservation guard pass. They confirm the component and unchanged arbitrary facing/slot pose contract, not the native component's visible effect. Fresh placement and later settled screenshots on the exact future G84 package are required before claiming the transient yaw corrected.

## Other follow-up and limits

The G83 opt-in native trace separately established an occupied-plate reward-stage rollback after valid rows, session/identity, reconstruction and debit. The precise failed nutrition operation remains unknown. G84 adds bounded, opt-in reward-substage/error-category diagnosis only; no guessed nutrition or setter change is included. The [bounded native G83 report](NATIVE-PLATE-G83-BOUNDED-20261007.md) retains its exact source/archive identity, screenshot digests and acceptance limits.

Fresh2.8.84 identity and canonical runtime hashes are frozen with append-only history. Focused diagnosis/body/source-conservation checks pass; final exact-head aggregate/compiled CI, package identity and native tests are still pending. BSM freshness/family/live requirements remain open. Keep `client=false`, `production_ready=false`, `pending_client_acceptance`. Private images, native logs, worlds and machine paths are not published.

## Reward-substage trace

Only the existing nested plate reward opts into detailed tracing. The same dynamic food lookup, hunger/saturation component APIs, target calculations, write arguments and write order remain. The original thrown object is rethrown unchanged so the existing transaction restores food and nutrition. Untagged players do not run lazy diagnostic target/readback getters.

The existing bounded logger adds whitelisted reward substages, numeric facts/targets/readbacks, operation names and error-name categories. Nonfinite or huge numeric facts are marked, not changed; unknown error names become `OtherError`, and exception messages/stacks are never logged. The existing96/player,192/global per1,200ticks and16-key limits remain. These facts identify the failing native operation in a later opted-in clone trial; they are not a nutrition fix or an altered gameplay clamp.
