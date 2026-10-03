# Native bottle pass diagnostics

The owner reports native FP and TP failure for `fb2addc`: partial2's four colored halves separate from the shell, and the default finished8's single fill separates from its shell. The source projection checks passing do not establish native alignment. That candidate is not accepted. No private client images or logs are included here.

`development/gameplay_core/bottle_render_pass_probe.py` produces a private RP overlay, never modifies canonical resource/behavior packs, and records input/output SHA256. The four historical overlay cases require an archived copy of the exact multipass RP that failed natively; they are not production single-pass transforms. Run them against that archived RP:

```sh
python development/gameplay_core/bottle_render_pass_probe.py --source-rp projects/grilling/gameplay_core/resource_pack --case shell-first --output /private/bottle-probe-shell-first
python development/gameplay_core/bottle_render_pass_probe.py --source-rp projects/grilling/gameplay_core/resource_pack --case shell-only --output /private/bottle-probe-shell-only
python development/gameplay_core/bottle_render_pass_probe.py --source-rp projects/grilling/gameplay_core/resource_pack --case rebuild-true --output /private/bottle-probe-rebuild
python development/gameplay_core/bottle_render_pass_probe.py --source-rp projects/grilling/gameplay_core/resource_pack --case single-rc-two-layer --output /private/bottle-probe-single
```

Use a fresh output directory. Each case must start from the same unmodified failed private RP, not another case's overlay. Copy only `outputs_sha256` paths from its receipt into that private RP. Retain the private RP manifest identity and all BP/gameplay files. Reload through the owner's client procedure, then compare the existing QA partial2 and finished8 at the same camera, skin, hand and FOV. This source generator does not perform deployment or control a client.

| Case | Changed variable | Interpretation |
| --- | --- | --- |
| shell-first | Move the shell RC from last to first for all 67 bottle attachables; no pose, geometry, property, material or texture changes | If positions follow pass order, supports a pass-dependent matrix/cache/binding problem. It does not prove animation is replayed per RC. |
| shell-only | Keep only the original shell RC for all 67 bottle attachables | Compare that exact shell to its original multipass position. No contents are expected. |
| rebuild-true | Set `rebuild_animation_matrices=true` in the three files defining every bottle-used RC | Boolean is documented, but its attachable/cache behavior must be measured. No assumed fix. |
| single-rc-two-layer | One geometry, one RC, original shell plus the first two dynamic layers; also one RC for default finished8 | Isolates the single-pass alternative. Colors remain data-driven via static UV bones. Other fixed variants retain their original routes. |

The single-pass partial geometry has a bound grip, one shell child, and four half-cuboids with nine color candidates each. `part_visibility` activates exactly the candidate matching the existing numeric layer property. Zero hides all candidates. It deliberately renders only two ingredient layers; pending3/pending8 are not valid completeness checks for this limited probe. It introduces no runtime properties, item ID changes, shaders or UV animations. Each attachable retains its exact source identifier, scripts/pre-animation/dispatch and authored animation references.

The atlas is 128x128 with the original 32x32 bottle texture copied verbatim into its original pixel coordinates. All shell UV numbers stay unchanged and the geometry's texture dimensions match the larger image. The palette tiles are copied from existing 16x16 opaque source-color PNGs; the generator verifies their uniform RGBA, original shell byte equality and every palette tile's pixel equality. Static cube UVs sample an inset 8x8 uniform region with a four-pixel gutter. This is a diagnostic fixed-UV atlas, not the old animated UV offset approach. Default finished8's original shell and fill UVs both sample the unchanged bottle pixels.

Source generation for all four historical cases succeeded. The owner subsequently observed pass-order-dependent position/direction changes with shell-first, and aligned partial2/default finished8 with single-rc-two-layer. These limited native results motivated the full production expansion described in `BOTTLE-COMBINED-CANDIDATE.md`; they do not accept its eight-layer/all-variant behavior.

The retained generator also audits the current production RP without writing any overlay assets:

```sh
python development/gameplay_core/bottle_render_pass_probe.py --case one-rc-audit --output /private/bottle-one-rc-audit
```

This case checks 67 single-RC/default-geometry/default-texture routes, material bindings, the two production controller identities, static UV use and complete geometry inventory. Its receipt records source hashes and zero output files. `shell-first` and `shell-only` reject current single-RC inputs explicitly; use the archived multipass source to reproduce the original diagnostics. No case controls or reloads a native client.

Official evidence: [RC schema](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/visualreference/render_controller.v1.8.0?view=minecraft-bedrock-stable) lists `rebuild_animation_matrices`; [RC documentation](https://learn.microsoft.com/en-us/minecraft/creator/documents/animations/animationrendercontroller?view=minecraft-bedrock-stable) demonstrates bone visibility and material mapping. [Animation schema](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/schemasreference/schemas/minecraftschema_actor_animation_1.8.0?view=minecraft-bedrock-stable) defines resetting animated bones via `override_previous_animation`. These sources do not establish that every RC repeats an attachable pose transform.
