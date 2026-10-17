# Scene visual repair scope — 2026-10-09

This is a source-backed repair note, not Minecraft client acceptance. The
reviewed input is Bedrock `de445c13985cdcdab0f2353ef259aaa13e523e08` (G124),
with original Grilling Java source
`breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c`.
Forge 1.20.1 and NeoForge 1.21.1 were checked separately; the light, oil tint,
custom GUI mask composition and premium vat lighting rules below agree.
Release identity and client acceptance are recorded by the integration release.

## Corrections in canonical BP/RP

### Grill light

Both effective lit permutations in `behavior_pack/blocks/grill.json` now emit
7 instead of 13. The unlit value remains 0, and the later direction-only
permutations do not override it. Original `registry/ModBlocks.java` sets
`LIT ? 7 : 0` in both loaders. `verify_a23.py` remains the historical A2.3
validator with its original value 13; it is not the current verification entry.

### Animated world oil and vat fluid surfaces

Original NeoForge `client/ClientSetup.java` registers water still/flow sprites
with canola tint `0xFFC08A24`, water still/flow with secret chili tint
`0xFFE04B2A`, and lava still/flow with premium tint `0xFF9E1B16`. Forge
`oil/OilFluidType.java` declares the same three routes.

The port previously registered single-frame, five-color handmade oil textures.
It now uses tinted, animated **Bedrock native** fluid strips from the official
[Mojang 1.26.50.4 sample revision](https://github.com/Mojang/bedrock-samples/tree/46ba6ea985fb5a92d79a9419198f10dda14c199d/resource_pack/textures):

| Oil | Source sprite | Still animation | Flow animation | RGB tint |
| --- | --- | --- | --- | --- |
| Canola | Native grayscale water | 32 frames, 2 ticks/frame | 32 frames, source default frame time, replicate 2 | `C0 8A 24` |
| Secret chili | Native grayscale water | 32 frames, 2 ticks/frame | 32 frames, source default frame time, replicate 2 | `E0 4B 2A` |
| Premium chili | Native lava | 32 frames, 16 ticks/frame | 16 frames, 10 ticks/frame, replicate 2 | `9E 1B 16` |

`development/gameplay_core/fixtures/bedrock-fluids-1.26.50.4/source-manifest.json`
pins the source commit, blobs and bytes, with Mojang's license retained.
`tools/build_scene_visuals.py` multiplies each native RGB channel by the Java
tint (`floor(source * tint / 255)`), retains the source alpha, writes new
strips and first-frame fallbacks, and copies each selected native animation's
frame timing/replication metadata. Existing handmade texture files are retained.
Terrain entries now point at the new fallbacks and matching flipbook atlas keys.
Top/bottom faces use still textures; side faces have a distinct flow material.
The same still atlas entries are already used by the big vat's oil materials.

This is a **native sprite adaptation**, not a Java vanilla texture import.
Bedrock's underlying water/lava art, alpha and animation sequence have not been
verified byte-identical to Java and can change under resource packs. RGB multiplication is quantized to
8-bit PNG channels, while Java multiplies vertex color in the renderer.
The port retains its eight step-height world-oil geometries and scripted fluid
mechanics; native slope tessellation, occlusion and Java fluid rendering are
not supplied by flipbook registration. No claim of pixel-identical oil is made.

Original `oil/BigVatRenderer.java` uses a 12 × 12 pixel surface, UV inset
1/16..15/16, four fill heights `(2 + level * 3)/16 + .001`, and full light
`0xF000F0` for **premium chili only**. It does not brighten the vat's bricks
or adjacent blocks. The current block material schema has no classic
per-material fullbright field, so a bounded transient renderer supplies that
one premium surface using `entity_emissive_alpha` and `ignore_lighting: true`.
It reads only the block's existing fluid/level state; it stores no fluid or item.

The existing block fluid planes now use the same UV inset and nominal height;
the premium overlay is .001 block above that fallback, at the Java offset.
The block fallback remains visible if the helper cannot be created. The shared
station display quota, 48-block audience range, unknown-spawn reservations,
cleanup, reload discovery and per-tick target budget also apply to this helper.
The 32-frame premium sheet is selected every 16 game ticks through the same
bounded display queue. Under load, intermediate frames can be skipped; a
terrain atlas animation and an entity helper need not share the same client
frame phase. Native shader behavior, distant filtering, lighting and unload
transitions still require the integrated client's acceptance.

### Secret skewer icons on wall recipes

Original `skewer/SkewerGuiIconCache.recipeIcon16` normally selects the custom
16-pixel GUI composition. The previous port always flattened the held 3D mesh
for secret results. It now creates one `custom_recipe_icon_visual` helper at
the existing Java page position and size and renders the authored GUI layers.

The renderer uses the original stick and six ingredient masks from the pinned
`java-custom-skewer-gui-9a1acdab` fixture. `CustomSkewerGuiTexture` supplies the
five tone markers and front-slot overwrite order. It samples center cells
5/6/9/10 through the existing source-derived palette sampler. The color table
uses the same 213 food slots and cooked snapshot styles as current held/plate
visuals. Each helper receives three exact 24-bit base colors, an ingredient
count and three saved GUI variant bits. No ItemStack identity or metadata is
written, swapped or manufactured for display.

There are 85 tiny **authored-mask variants**, independent of food combinations:
15 stick masks for the four possible counts and shape bits, plus 70 white
tone masks for the three ordered ingredient slots. Covered pixels are removed
in advance, so all rendered masks are disjoint. Their compositing order does
not depend on coplanar depth tests. Sixteen render controllers draw at most
one stick plus fifteen tone layers on a single helper; no helper is created
per color or ingredient. `guiVariantBits` preserves stored 4..9 values and
translates Java's signed-int hash fallback for legacy/missing variants.

This repairs the wall-recipe route. The existing color catalog still cannot
sample an arbitrary third-party client's item model/particle sprite or a
resource-pack override at runtime; unsupported ingredients use the explicit
fallback palette. The real client must still confirm shading, pixel filtering,
four-facing projection, culling, transparent edges and update timing. A source
recomposition check does not prove that an engine renders these layers exactly.

## Investigated surfaces that remain incomplete

| Surface | Current concrete boundary |
| --- | --- |
| Secret/unfinished native inventory icon | Stable `minecraft:icon` exposes `textures.default` as an item-atlas key; the stable `ItemStack` API exposes no icon texture setter or per-stack renderer callback. A scene helper cannot affect an inventory slot. Current static fallbacks remain. |
| Plate native inventory contents | The held/placed plate renderer has its own contents channel. The inventory item still uses a fixed atlas image and has no stable API route for rendering each saved stack's contents. |
| Fixed slime/mysterious native inventory animation | The official flipbook schema/tutorial is a **block** texture route. The current icon component has no documented frame/Molang selector. Adding an item atlas key to the terrain flipbook list would not establish a supported inventory animation route. Existing wall/HUD frame routes are preserved. |
| Hot-food inventory badge | Item metadata/lore can represent heat; this does not expose a per-stack icon-overlay callback. Current lore is not counted as the original badge. |
| Secret eating HUD icon | JSON UI supports image tint and bindings, so this is not classified as universally impossible. The current private eating packet contains a finite icon ID, duration, progress and readiness. It has no per-slot color/variant channel or verified binding that constructs an RGB color from the encoded text. The new scene masks/color planner are reusable inputs, but no unverified JSON UI expression, guessed binding or huge precomposed food table is shipped here. The current original progress/25-tick checkpoint behavior is retained. |

This repair does not use transient item-ID aliases, durability/data hacks,
native dye components, per-tick inventory replacement, or food-combination
texture generation to disguise these missing routes. Such replacements would
need to prove preservation of stacking, state, host integration and saved
identity before they could be considered equivalent.

## Primary platform references checked

- [Microsoft item icon schema](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/itemreference/examples/itemcomponents/minecraft_icon?view=minecraft-bedrock-stable): `textures.default` is a string atlas key; the legacy `texture` field is deprecated.
- [Microsoft stable ItemStack API](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/itemstack?view=minecraft-bedrock-stable): available per-stack methods and components; no dynamic icon renderer.
- [Microsoft animated block texture tutorial](https://learn.microsoft.com/en-us/minecraft/creator/documents/createanimatedblocktexture?view=minecraft-bedrock-stable) and [Mojang flipbook schema](https://github.com/Mojang/bedrock-schemas/blob/main/schemas/rp/textures/flipbook_textures.schema.json): block atlas animation route.
- [Microsoft render controller schema](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/visualreference/render_controller.v1.8.0?view=minecraft-bedrock-stable): Molang color channels, texture/geometry arrays, UV scale/offset and `ignore_lighting`.
- [Microsoft block materials](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/blockreference/examples/blockcomponents/minecraftblock_material_instances?view=minecraft-bedrock-stable): explicit geometry material slots and classic render methods; named biome tint methods, with no classic fullbright parameter.
- [Microsoft JSON UI element schema](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/jsonuireference/examples/jsonuicomponents/ui_element?view=minecraft-bedrock-stable): image color is an RGB number array; bindings connect existing game/control properties. It does not expose a universal ItemStack texture renderer.

## Targeted verification

- Existing `test_plate_recipe_visual.mjs`: **17 passing**, including saved
  recipe colors/variant changes without metadata mutation, premium vat state
  transitions, native-data separation and the existing failure/quota cleanup.
- Existing `tools/test_java_custom_skewer_gui.py`: **8 passing**, including
  independent recomposition against the pre-existing Java source translator
  with no overlapping coplanar masks for representative raw/cooked recipes.
- `tools/build_scene_visuals.py --check`: **106 generated display assets current**;
  checks the new pinned source boundary and only its declared asset outputs.
- Existing `verify_visual_refs.py`: **PASS**; no missing current atlas, geometry,
  attachable or render-controller references found by that gate.
- Syntax checks for the three modified runtime modules: **PASS**.

No full redundant historical suite, Minecraft client, BDS or live deployment
was run for this isolated visual branch. The integration release must preserve
historical guards, include the new generator check and retain client acceptance
as pending until the owner compares the actual candidate.
