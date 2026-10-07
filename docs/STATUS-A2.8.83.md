# G83 plate display review candidate

G83 is based on published G81 commit `21b995bb1b1fdffd1e8300dc17a2b968272384a4`. It does not include the independently open G82 Cookery palette proposal. No merge, public release or live deployment is authorized in this task.

## Reproduction

Actual Bedrock 1.26.52.3 with G81 A2.8.81-test.311.1: a normally manufactured secret skewer containing mushroom stew, golden apple and carrot, with all three saved ingredient rows, was retargeted to `secret_skewer_native_plain` by the normal animations-disabled configuration. Sneak-use on a grass top created a plate. Breaking it returned a packed plate with 1/5 contents. Re-placement and a subsequent ordinary shovel tap queued the visual refresh, but the tray remained almost empty after 32 seconds, with tiny colored flecks at its edge. A read-only native equipment query confirmed that one transient equipment helper held mushroom stew. This proves stored contents and an equipped renderer existed; it does not establish the engine's exact equipped-item transform.

## Repair

- Known fixed raw/cooked skewers and the canonical secret skewer, including real native eating aliases, use a dedicated transient `plate_food_visual` with the existing Java-derived full-skewer world meshes and original food palette references
- The secret renderer preserves all three packed ingredient indices, source shape variants and cooked-snapshot visual state through the existing read-only `secretVisualState`; it does not equip three unrelated vanilla item icons
- Original Java count-based 1–5 layouts, heights and per-slot yaw are preserved. The plate uses its actual south/west/north/east facing basis. The composed plate/FIXED model transforms cancel their X/Z rotations, give scale 1.2, and require post-scale Y/Z translation. Existing fixed world meshes already subtract one authored Y pixel; their offset compensates for that exact conversion
- Original, mysterious/dark and tagged extension rows without a reviewed world mesh preserve the existing native fallback. Their client rendering is not certified by this repair
- Successful plate placement calls a registered visual invalidation once after every placement/storage/hand step commits. Failure and rollback do not notify, and a display notification failure cannot undo committed ownership
- The existing visual queue, audience range, helper cap and startup transient cleanup remain authoritative. Full meshes use one helper per known skewer. Plate data, nutrition, selection, quantities, metadata, ownership and transactions are unchanged
- Grill and rack assets/runtime are unchanged; the new client binding refers to the existing grill geometry/palette/controller data without adding a cooking flip, hop, native runtime identifier, inventory or attachable

## Opt-in native consumption diagnosis

G81 also reproduced a separate packed-plate consumption no-op in three main-hand air-use trials. Its cause is not established and this candidate does not claim to repair it. An opt-in `kg_plate_qa` tag enables bounded, sanitized `[Grilling plate QA]` console records at existing before/start/complete/stop/settlement gates. The trace records only item identifiers, event/main/off row counts, cancellation/session/identity booleans and whitelisted stages. It does not emit names, IDs, coordinates, lore, ingredient payloads, errors or arbitrary supplied fields. Untagged players incur no hand/metadata snapshot reads. Limits are 96 records/player and 192 globally per 1,200 ticks, at most 16 internal rate-limit keys. Diagnostic failures are caught and cannot change the original interaction. Remove the tag after an isolated native trial. Existing gameplay semantics, source-conservation witnesses and VM adapters are preserved.

## Source and limits

Original Grilling main was rechecked on 2026-10-07 and remains `9a1acdab27698457bec16c9362678e574895a28c`, 1.1.1. The [public family source tracker](https://github.com/casama233/kaleidoscope-tavern-unofficial/blob/main/family/java-upstream.json) still separates Forge 1.20.1 file 8726006 and NeoForge 1.21.1 file 8726014. Original [NeoForge plate renderer](https://github.com/breezeth-CN/KaleidoscopeGrilling/blob/9a1acdab27698457bec16c9362678e574895a28c/neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/skewer/SkewerPlateRenderer.java), source SHA256 `81afc858b3eb2d347af3ba9c228178519931d1091c17eb2b884df721be426f93`, supplies the layout and transform. Existing canonical grill meshes/palettes retain their published source witnesses. This is source-backed adaptation, not complete Java/client parity.

The mandatory BSM Java freshness report is still unavailable. The existing exception permits canonical Git draft publication and isolated local repair/testing only. Merge, release, family/live admission remain blocked. Keep `client=false`, `production_ready=false`, `pending_client_acceptance`.

Focused source tests cover 19 raw/cooked families, generated native aliases, secret three-food state, all five count layouts/four facings, helper reuse/removal/budget/failure, read-only metadata and placement commit/rollback notification. Generator checks ensure exact reuse of all canonical world bindings. Static/SDK/source tests do not certify actual pixels, save/reload, audio, plate consumption or complete family behavior. The exact G83 candidate still needs native client placement/refresh/reload/pickup checks before claiming this display reproduction repaired.

A bounded native Blockbench GUI/MCP inspection on 2026-10-07 opened the actual `geometry.kg_station.grill.state_21_0`, imported original `food_199_0.png`, and inspected 12 cubes, two groups and the 256x96 palette texture. A read-only native editor export retained the original bones to six decimal places. The editor serialized format1.12 while canonical source remains format1.16; no editor export replaced canonical files. This certifies one representative ingredient part only, not the full plate, all variants or Minecraft pixels.

Read-only asset review confirms all 104 reused geometries have one unbound, untransformed root. The 19 fixed shafts and secret shaft have identical transformed bounds relative to their Java slot: X[-0.3,0.3], Y[-0.9,-0.3], Z[-7.8,7.2] pixels. Slight lower-food intersections with the authored 2-pixel tray top and shaft overhang are preserved, not raised arbitrarily. These calculations are not native pixel acceptance.

Only source code, generated public bindings, tests, release identities and this report are published. Screenshots, native worlds, player logs, private receipts, author Cookery archives and machine-specific paths are omitted.
