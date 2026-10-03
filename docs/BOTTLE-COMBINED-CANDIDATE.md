# Bottle candidate for native acceptance

Source is the verified 2.8.61 handoff from `a9e6a4ae7262e18b7e8cc68d9cb9e2b926cd40b1`, applied over `4ee97f04e81dcdc2d00653e2bb907f6c1b1f0d6a`. The supplied manifest's 266 paths matched byte-for-byte before repair. Local snapshot parent `081761b871ddfcebe2f25c6dd1aff23121d9c257` preserves that candidate, including its unpublished eating fixes. The subsequent commit contains only this bottle repair.

EMPTY/PENDING now render shell and 16 Java half-cuboids from one geometry with one bound `grip` parent. Its child bones receive the same FP/TP pose. Each render pass selects only its child via `part_visibility`; opaque palette contents render before the blended shell. Palette colors and source cuboid bounds stay unchanged. The previous separately instanced geometry path could allow transform divergence; this is a source-level hypothesis awaiting native confirmation.

Both bottle FP positions move inward/upward/backward in the calibrated camera frame. Authored rotation and .72 scale remain unchanged. The old any-corner viewport test accepted models partly outside the screen; the new test checks every corner, all renderable children, near plane and both horizontal/vertical FOV conventions at aspect 1.49 and 16:9. This projection is not an engine emulation.

No gameplay runtime, item IDs, recipes, native ItemStack storage, player properties, or skewer settlement were changed by this repair. In particular `main.js`, `player.json` and `verify_a2861.py` retain their exact handoff bytes. Existing 177 uniform opaque palette PNGs and pinned Java ingredient RGB values pass verification.

Targeted validation:

```sh
node --test development/gameplay_core/test_bottle_held_visual.mjs development/gameplay_core/test_seasoning_native_storage.mjs development/gameplay_core/test_seasoning_native_hands.mjs
python -B -m unittest discover -s development/gameplay_core -p test_bottle_visual_assets.py -v
cd development/gameplay_core
python -B -m unittest test_native_bottle_fp test_native_bottle_full_frustum test_native_offhand_idle test_held_pose_frames -v
```

Results: 96 Node tests, 4 palette/asset tests, and 25 hierarchy/frustum/pose tests pass. All 264 geometry routes and 328 renderable bone routes fit the four tested projection scenarios. Native hand fixtures cover DP/clone metadata and place-pickup-replace in both hands with independent containers; they do not certify saved-world persistence.

Native acceptance remains required: EMPTY/PENDING with 0/1/2/3/4/8 ingredients, alternating different bottles in both hands, first/third person at 16:9, shell/content alignment, near-plane/full-bottle visibility, and saved-world place-pickup-replace. Also test full SPECIAL bottles and variants; they keep their existing fixed render routes while receiving the same FP position correction.

Separate shared-runtime finding: the event hand-intent signature does not distinguish stacks differing only in lockMode, keepOnDeath, canDestroy or canPlaceOn. This can choose the wrong hand when both stacks otherwise match. This bottle render commit leaves that shared `main.js` path untouched for coordination with the owner's ongoing runtime changes. Native client rendering and this edge case remain unaccepted.
