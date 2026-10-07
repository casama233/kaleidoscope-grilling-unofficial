# G89 placed facing and full ordinary-skewer candidate

The exact G89 candidate now has a [bounded native placed-rendering result](NATIVE-PLATE-G89-BOUNDED-20261007.md): the restored ordinary mesh is visible with a fresh empty content log, and the observed five-beef samples face the placer correctly in all four directions. Canonical source/Dash/export CI passed for the same runtime. This does not certify every variant or held-plate input, audio, Java pixel/animation or family/live parity.

G89 is a fresh 2.8.89 candidate based on frozen G88 documentation head `39e6dd145a84abdf921382aef9c90833061aa955`. It retains the original Cookery palette correction and all prior plate visibility, nutrition, native-use cancellation, yaw-change rebuild and removal-fault guards. The [G88 bounded native report](NATIVE-PLATE-G88-BOUNDED-20261007.md) and its successful [documentation-head canonical CI](https://github.com/casama233/kaleidoscope-grilling-unofficial/actions/runs/37577098848) remain evidence for those exact bytes, not G89 acceptance.

## Two additional native observations

Four-facing smoke on the same five-beef-skewer plate showed handles toward the placing player in east/west but away in north/south. The actual north block state was confirmed as `minecraft:cardinal_direction=north`, ruling out placement for that sample. No south block-state probe was performed. The original Java placement stores the player's direction and the renderer puts the bare low-Z end toward that player in all four directions.

A canonical `ordinary_skewer` placed in a plate rendered blank, with a native missing `query.property` Molang error. Its plan was absent, so it used the old equipment helper and a held attachable whose eating properties were not present on that helper. This is distinct from lost plate ownership or contents.

## Narrow changes

### Native mesh/world facing

Actor anchors and all original 1–5 layouts remain unchanged. A source-to-mesh X reflection plus the sample-calibrated native mesh Z basis gives `N(yaw) · C = Ry(180 − yaw)`. Java requires `Ry(slotYaw − facing)`. The candidate therefore uses normalized native yaw `180 + facing − slotYaw`. This also preserves the signed −22.5° and −45° upper-slot angles; a lone 180° offset would reverse the previously correct east/west cases.

An independent oracle applies the calibrated native matrix to actual exported shaft corners and compares them with the original Java renderer/FIXED transform, including scale, translation and post-scale root offsets. It covers 480 corners per mesh across every authored slot and four facings for beef, ordinary and secret shafts. The candidate agrees within floating-point tolerance; the old yaw and the wrong slot-angle sign fail. This is a calibrated mathematical candidate, not a native all-facing or asymmetric-model pass.

### Full ordinary-skewer mesh

Canonical, native-plain and alternate ordinary variants now select plate-only model 115. It reuses the existing original-source full 19-cube ordinary geometry and stage-0 atlas. Cube dimensions, UVs and rotations are preserved; held binding/display are removed and Y is normalized exactly like the established world-mesh generator. A new plate-only base render controller extends its arrays to model 115. Existing grill arrays/range, held assets, eating animation and player properties are unchanged. No dummy eating properties or equipment/attachables are added to the helper.

## Conservation and separate gaps

Runtime changes are restricted to `plate_visual_core.js`, the plate helper's model range/client bindings, and two new plate-only ordinary geometry/controller files, apart from fresh paired manifests. All other BP/RP bytes, metadata, transfers, food rewards, `main.js`, observer/budget/cleanup, original palette inputs and other stations remain byte-identical to G88. Full runtime tests admit only those five exact reviewed paths; historical G86/G87/G88 source and release history assertions remain intact.

Mysterious/dark failures are unchanged. Java has shape-specific and original-failed-source variants; existing Bedrock failures do not preserve the Java `FailedSkewerSource` marker. Missing provenance must not be reconstructed by guessing. Missing model variants also must not be treated as recovered shape 1: Java's absent-variant state is the bare-shaft state. A later focused producer/renderer repair is needed. This candidate does not claim full failure-family display parity.

Occupied-plate handheld contents are being handled separately. Dynamic GUI icons remain unproven. This candidate changes no held/player channel, arm visibility or player render-controller override.

## Gates and evidence integrity

Focused source, matrix, asset conservation, production display, ownership/rollback and nutrition checks are distinct from engine acceptance. G89 has verified exact public Git/package identity, full canonical/compiled CI and the linked bounded native direction/ordinary checks. No all-facing, full-Java, audio, family/live, BSM freshness or production acceptance is claimed. Keep `client=false`, `production_ready=false`, `pending_client_acceptance`. No merge, release or live deployment is authorized here.

Private worlds, player records, machine paths and logs are not published. Native observation screenshot SHA256:

- South five: `bbf135974e5136dd009225071ca05ac490a1dc48bf1851ce619aaf363030e197`
- East five: `248680e4a07a2dd40db1eadf43e48e604ec836aeb75e6f3926f3054aefe0fed1`
- North five: `78abc471399d61eb9f5246294df44f7f148dbeae8c8a106949f61f97813a3d42`
- North state: `7ea59d5bd01e1ec53220e4f955ac3f29b3c83044e82d28271da890ccb77bb62b`
- Ordinary blank plate: `8272e8e9094dcc870a1ef983e382f28270d4b85d5884276bd92ca360ccdbb243`
- Ordinary missing-property log: `8ce069419902c41fbd44c0576c00e8bca8e962098f380c30f33f280befce48a7`
