# G86 current-main palette and plate integration candidate

G86 is a fresh source-coherent candidate based on current main `c85cb34f591079c0b06878b8e565e7f262833e49` (independently merged G82 palette PR144), preserving all G85 plate/food repairs from `07208cd8b8a047ed3e5be9a38596054b1818dcdc`. Frozen G83/G84/G85 identities and histories are not overwritten. The G85 PR became conflicted when main advanced; it remains an exact isolated native-test candidate, not a canonical CI pass.

## Exact runtime union

- All648 BP files are identical to G85, except the paired manifest identity advances to2.8.86. This preserves full plate meshes/display queue, source-yaw initialRotation, body component, native saturation refresh/bounds, diagnostics, metadata, quantities, ownership and all prior gameplay fixes
- All3499 RP files are identical to G85, except the manifest and the seven `food_100_0.png` through `food_100_6.png` atlases. Those seven files are exactly current main/G82's original Java Cookery suspicious-stir-fry palette correction
- Original Java palette/provenance fixtures, retained changed sprite, importer, attribution and G82 status survive byte-identical to main. G85's gameplay/plate scripts, meshes, aliases and exact reviewed main deltas survive without a new gameplay delta
- Both append-only release histories and verifier entries82–85 are retained. The G86 verifier runs the complete G85 chain once with expected_version86; existing palette generation checks cover all1491 atlases. A separate Git-source union/provenance gate protects the precise two-source relationship without weakening older byte guards
- Two immutable owned-repository commit pins are added to the existing audited source-ref inventory so shallow Linux/Windows CI can retrieve the exact comparison objects; no new workflow or private source pack is introduced

## Bounded native G85 evidence, not G86 acceptance

Actual Bedrock1.26.52.3 using exact G85 archive SHA256 `9041fc9e31d2763f6c1310c0ac4901590e53956ed822cec75f41e13fdcff78a6`: at04:37:56UTC, the same preserved occupied three-ingredient plate completed an ordinary1800ms main-hand air use. The selected slot became one bowl, hunger10→13, regeneration/absorption icons and two golden hearts were visible. Later the effects screen showed Absorption1:39 after regeneration had naturally expired. Inventory inspection confirmed bowl count1. No diagnostic tag was enabled.

A separate ordinary grilled-beef-skewer sample on one west-facing tray was immediately straight at04:40:46UTC and remained identical without input at04:41:07. This supports the initialRotation repair for that bounded ordinary/count1/facing case. It is not the consumed custom sample and does not certify all variants, counts, facings, Java comparison, audio or touch.

The source-coherence gate proves the associated BP behavior and the vanilla ingredient palettes are unchanged in G86. It does not make G85 screenshots a G86 native pass. G86 still needs its own exact-source/package identity, canonical/compiled CI and bounded native continuation; the seven corrected Cookery atlases have no new native color acceptance here.

## Gates

No merge, release or live deployment is authorized in this task. Canonical source/export checks and isolated native testing may run in parallel after exact Git/package/focused checks; both remain distinct. Required BSM freshness, full-family/saved-world/live admission and broader client acceptance remain open. Keep `client=false`, `production_ready=false`, `pending_client_acceptance`.

Private images, native logs, worlds, player records, machine paths and author Cookery archives are not published.

## G85 screenshot integrity
- `g85_plate_consumed.jpg`: `532036c28f4502cacfc1913f1713733762dbf04bfc0193fca97c4c443273205a`
- `g85_plate_effects.jpg`: `3d44a5bbbf77359563f5360e7f3ac3b935d17be48dc41655ec0254d31735094e`
- `g85_plate_inventory.jpg`: `bbb6627a2acc4638444ddbe96122c9aca5e0598e139f7e1f8a29a8f33cc8866f`
- `g85_plate_yaw_fresh.jpg`: `16413a3707449c871f9570d88938540c90157cf79550d398c1b49f9e4c72d10f`
- `g85_plate_yaw_settled.jpg`: `f6936fdb960f2ea681d93eeef37a13828559961a36cf591c1495122aefd9057c`
