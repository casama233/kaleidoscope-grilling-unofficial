# Single-pass bottle candidate for native acceptance

The verified unpublished 2.8.61 handoff is preserved by snapshot parent `081761b871ddfcebe2f25c6dd1aff23121d9c257`. This expansion follows probe commit `4d9cee9c0d8f256954b2e6b5148acf40f1ee09e1`; it changes bottle resource assets and source guards, preserving the owner's gameplay/eating work.

Native feedback rejected the earlier combined-geometry/multiple-RC candidate: shell and contents still separated. Reordering only RCs changed positions and directions, supporting a pass-order-dependent transform/binding problem without proving animation replay. The owner's limited single-RC probe aligned partial2 and default finished8 in FP and TP. The full bottle was visible in that FP test (Alex, FOV60, 1180x664). Those observations certify the probe cases only.

All 67 production attachables now use one RC, one default geometry and one static atlas. EMPTY/PENDING have one bound grip, one shell child and 144 static color candidates: 16 Java half-cuboids times nine nonempty palette values. Eight existing numeric layer variables select one color per half; zero hides it. Both-hand pre-animation reads hand/owner context; the RC reads numeric `v.*` only. SPECIAL uses 64 combined fixed geometries preserving every original geometry fallback and texture choice; default SPECIAL shares r8/v0.

The 128x128 atlas copies all four original 32x32 textures pixel-for-pixel across its first row. Fixed cube UVs shift horizontally to the corresponding original image; other cube data stays unchanged. Dynamic UVs sample opaque uniform tiles with an inset gutter. Pinned Java RGB, palette/tie order, the 177 placed palette PNGs and original fixed geometry/texture sources remain unchanged. Contents use opaque `entity`; shell uses `entity_alphablend` in the same RC. Historical source geometry/controller definitions remain for reproducibility; no bottle attachable invokes a multipass route.

The calibrated FP pose is retained. Source projection checks cover every renderable child, both hands, near plane and horizontal/vertical FOV interpretations at 1.49 and 16:9. This is mathematical validation, not an engine emulation.

This render expansion leaves item IDs, recipes, ItemStack/DP storage, player properties, manifests and gameplay scripts unchanged. The before-event metadata API regression is a separate runtime fix requiring independent integration and testing.

Validation:

```sh
python development/gameplay_core/a2861_bottle_held_visual_assets.py --check
python development/gameplay_core/bottle_render_pass_probe.py --case one-rc-audit --output /private/bottle-one-rc-audit
cd development/gameplay_core
python -B -m unittest test_bottle_single_pass test_bottle_visual_assets test_native_bottle_fp test_native_bottle_full_frustum test_native_offhand_idle test_held_pose_frames -v
```

Results: 37 Python tests pass (11 independent asset/reproducibility tests and 26 pose/frustum tests); `verify_a287.binding_assets` and `verify_a286.bottle_chain` pass. The independent audit checks all 67 routes, 65 geometries, 144 dynamic candidates, every fixed cube against frozen original routes and original RGBA samples. Both-hand projection checks cover 134 geometry routes and 840 potentially renderable bone routes. These results do not certify native rendering or saved-world persistence.

Full production native acceptance remains required: EMPTY/PENDING 0/1/2/3/4/8 ingredients, unknown-value fallback, all SPECIAL variants, alternating different bottles in both hands, FP/TP, full-frustum visibility, shell/contents alignment, colors and saved-world place-pickup-replace with metadata. The owner performs client testing; no deployment or client control is part of this change.
