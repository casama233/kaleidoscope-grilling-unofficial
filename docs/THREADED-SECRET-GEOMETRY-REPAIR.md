# Threaded Secret Mix Skewer geometry repair

This is a private candidate repair, not a released or client-accepted parity claim.
Pinned Java reference: `breezeth-CN/KaleidoscopeGrilling` commit
`9a1acdab27698457bec16c9362678e574895a28c`.

## Implemented source contracts (6709 supersedes 6708 geometry mapping)

- The held food is no longer three 3.84 × 0 × 3.84 inventory-icon planes
- All 27 complete Java states provide the exact three-shape combinations
  - Neighboring shapes change cell-Z seam extents. Selecting only nine
    homogeneous meshes was insufficient for all-combination geometry parity
  - State 21, 42 and 63 still demonstrate the three homogeneous shape families
  - Shape 1 cells per slot: 12, 18, 18
  - Shape 2: 18, 18, 18
  - Shape 3: 12, 24, 26
- Every authored cuboid, exposed face, element rotation and face UV is retained
- Shaft dimensions remain 0.5 × 0.5 × 12.5; its texture and UVs now come from
  the actual secret-skewer shaft, not the raw-beef shaft
- The particle sprite's central region supplies the source 4 × 4 palette
- Alpha/dark filtering, transparent-cell fill, Lab quantization, isolated-cell
  cleanup, six face factors and cooking glaze follow `SkewerColorProvider`
- Tint is baked over the original white-concrete sprite. The full 16 × 16
  base texture and original face UVs remain unchanged; no texture downsampling
- Seven texture styles represent stages 0–5 and stage 4 with a cooked snapshot
- Completed held skewers and placed grill skewers share all 81 exact source
  state-slot volumes
- Unfinished skewers use all 12 exact one/two-ingredient source states, split
  into 21 slot meshes; the zero-ingredient state remains the bare shaft
  - Their existing packed stage fields carry actual partial count 0–2
  - Partial texture passes always select raw palette style 0
  - No eating aliases, progress clock or raw-last-item helper are attached
  - The grill has one transient skewer helper per occupied grill slot
  - Its original flip/root animation continues to affect shaft and food
  - The previous three native ingredient-item icon helpers are removed on grills
- The authored hand rig, main-item eating motion, bite order, owner occupancy
  and wildcard-off render masks are unchanged
- The separate late THREE helper remains the original raw last ingredient's
  generated-item sprite. It is not replaced by a food volume
- Threading stores Java-compatible random values 4–9 before debiting inputs
  - Values 4/7, 5/8 and 6/9 map to shapes 1, 2 and 3
  - Missing pre-repair Bedrock values use stable shape 1, without modifying an
    existing item or claiming the original random selection was recovered
- Existing six per-slot player integers carry food index in their low byte,
  shape and stage in upper bits. Partial attachables reuse the stage bits for
  actual ingredient count. Old plain indices retain shape 1/raw behavior
  - `food + 256 * ((shape - 1) + 3 * style)`; zero is hidden
  - Property count remains exactly 32; raw-helper properties remain unchanged
- Item snapshots, cooked ingredient data, creator data, nutrition/effects,
  transaction rollback and eating settlement remain on the existing paths

## Palette coverage and limits

The generic catalog has 213 entries. Apple, Carrot and raw/cooked Beef use
verified official Java 1.20.1 particle sprites, as do the other 36 vanilla entries.
57 Grilling entries use particle sprites resolved from the pinned Java source.
113 Cookery entries sample their previously reviewed, checksum-pinned public
Bedrock sprites. This does not certify Cookery Java particle-model parity.

The pinned default models for `raw_mushroom_skewer`, `raw_pork_belly_skewer`
and `skewer_plate` have unresolved particle references. Their provisional
neutral palette is the Java provider's exception fallback color. Native
missing-sprite behavior for these three entries is not claimed reproduced.

Arbitrary external resource overrides, item-state-dependent tint and dynamic
model overrides inside ingredient snapshots are not resolved at runtime.
Unsupported custom food visuals still require a registered catalog reference.

Plate composition and dropped/native inventory projection remain separate
open work. The unfinished-held gap observed in native 6708 is addressed by
6709 source/runtime selection, with native acceptance still pending. This repair does not replace
other family packs or claim those representations are fixed.

## Resource budget

The full-fidelity output has 1491 food/stage textures, each 256 × 96 RGBA,
plus one exact shaft texture. Food textures occupy 146,571,264 decoded bytes
(139.78 MiB), before mipmaps, and roughly 9.15 MiB compressed PNG bytes.
Held geometry has 107 definitions: shaft, three empty slot definitions, raw
helper, 81 exact complete-state slot meshes and 21 partial-state slot meshes.
Grill adds the same 81 complete-state slot meshes and three empty definitions
to its existing shaft/fixed models. Geometry is not multiplied by food or
texture stages; all 27 authored combinations are retained where seams differ.

Initial native validation should use an isolated Grilling + Cookery copy when
full-family client memory is tight. Full-family memory acceptance remains open.

## Validation boundary

Focused tests cover source-to-Bedrock geometry/rotation/UV round trips, held/
grill equivalence, exact tint × white-texture pixels, property packing,
metadata cloning, owner/hand dispatch, helper masks, and transaction snippets.
The palette differential oracle compares against methods extracted from the
pinned Java provider. These checks do not certify Minecraft rendering, rig
alignment, directional lighting, persistence in a real saved world, or native
performance. Blockbench previews are separately labeled source assemblies or
inverse-mapped actual exported geometry, with immutable hashes.
