# A2.7 — Content + Recipe Reconciliation

Java baseline: **Kaleidoscope Grilling 1.1.1** `breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c`.

As of 2026-09-21 the upstream `main` ref is identical to that release commit, so A2.7 is closing Bedrock parity gaps rather than chasing a newer Java revision.

## What A2.7 adds

### 27 previously missing base/processed items and dishes

Base / processed content:

- `beef_chunks`
- `canola_seeds`
- `carrot_dice`
- `chicken_skin`
- `chicken_wing`
- `houttuynia`
- `minced_houttuynia`
- `onion`
- `potato_slice`
- `raw_mantou_slice`
- `raw_sweet_potato_sheet`
- `red_chili_powder`
- `squid_tentacle`
- `sweet_potato`
- `sweet_potato_powder`

Dishes:

- `cold_houttuynia`
- `pepper_honey`
- `roasted_chicken_wing`
- `roasted_sweet_potato`
- `sugared_tomato`
- `wedding_candy`
- `houttuynia_stir_fried_pork`
- `green_pepper_squid_tentacles`
- `braised_chicken_wings`
- `potato_beef_stew`
- `red_sweet_potato_porridge`
- `sour_spicy_noodles`

All 27 icons are fetched from the pinned Java commit and verified by Git blob SHA-1 before generation.

### Java food values and effects

A2.7 ports the Java nutrition / saturation / stack-size values for all 15 edible entries.

Special effects kept at the Java durations:

| Item | Java effect |
|---|---|
| Roasted Sweet Potato | Cookery Warmth, 600 ticks |
| Cold Houttuynia | Fire Resistance, 1200 ticks |
| Pepper Honey | Grilling Numb, 1200 ticks |
| Wedding Candy | Invincible, 300 ticks |
| Red Sweet Potato Porridge | Flatulence + Warmth, 900 ticks each |
| Sour Spicy Noodles | Warmth, 900 ticks |

`sweet_potato_powder` also keeps the Java **30 tick knead** behavior: completing use converts the held stack 1:1 into `raw_sweet_potato_sheet`.

The custom effect entries reuse A2.1's persisted effect contract (`kaleidoscope_grilling:a21_fx`) instead of creating a second incompatible status system.

## Recipe reconciliation

A2.7 reads recipe inputs/results from the pinned Java 1.1.1 files and records the mapping in `reports/a27-recipe-catalog.json`.

Current mapped total: **25 recipes**.

- **8 native/direct Bedrock recipes**
  - Pepper Honey
  - Sugared Tomato
  - furnace / smoker / campfire variants for Roasted Chicken Wing
  - furnace / smoker / campfire variants for Roasted Sweet Potato
- **17 deterministic survival fallbacks**
  - 5 chopping-board recipes
  - 7 Create milling recipes
  - 3 Cookery pot recipes
  - 2 Cookery stockpot recipes

### Why 17 are called fallbacks

Java registers Cookery chopping-board / pot / stockpot and Create milling as custom Java `RecipeType` families. Retail Bedrock 26.51 cannot register those Java serializers.

A2.7 therefore preserves the pinned Java ingredient counts and outputs but exposes them through crafting-table recipes so the survival acquisition graph is playable. This is intentionally reported as a **platform substitution, not 1:1 workstation parity**.

For stockpot fallbacks, one bowl is added because Java serves the completed stockpot meal through the workstation rather than consuming a bowl in the recipe JSON.

`c:crops/tomato` is narrowed to the guaranteed Cookery tomato for the Bedrock fallback.

## Deliberately not faked

### Cold Houttuynia dynamic recipe

Java requires exactly:

- three Houttuynia items;
- one Cookery filled oil pot whose oil type is `premium_chili`;
- at least 2 oil points;
- only **2 points** are consumed and the oil pot is returned.

A normal Bedrock JSON recipe cannot inspect and mutate those stack dynamic properties. A2.7 does **not** replace this with a recipe that destroys a whole oil bucket.

### Sour Spicy Noodles

The Java recipe is conditional on optional `kaleidoscope_tavern` and references Tavern vinegar. Retail Bedrock recipe JSON has no safe equivalent of NeoForge's mod-loaded condition for an unknown optional item identifier. The item/effect exists in A2.7, while its optional Tavern recipe remains deferred to an explicit compatibility layer.

### Create-specific compatibility

The Java `crushing`, `millstone`, `filling`, and `mixing` recipe families remain compatibility work. A2.7's milling fallback provides the core powders without claiming Create machine automation.

## Remaining Java differences after A2.7

### A2.8 — crops and world generation

- `canola_crop`
- `onion_crop`
- `sweet_potato_crop`
- `houttuynia_crop`
- seed placement / growth / harvest / drops
- `pepper_log`
- `pepper_leaves`
- `pepper_sapling`
- pepper-tree generation and biome/world placement

The A1 plant geometry/textures already exist; the missing part is gameplay/world behavior.

### A2.9 — remaining blocks and meta systems

- `advanced_rack` block/entity behavior
- Java advancement set -> Bedrock equivalent
- single Grilling entry inside the existing Cookery guide with live/dynamic content
- final plate BlockEntity-style per-skewer dynamic 3D renderer
- exact Cold Houttuynia stateful crafting path
- optional Tavern recipe compatibility
- remaining Create integration hooks
- Oil Residue bonemeal behavior for non-numeric growth targets

### A3.0 — real runtime acceptance

- Minecraft 26.51 client validation
- BDS validation
- multiplayer ownership/state races
- reload / restart persistence
- old-world migration
- performance profiling
- final asset/lighting/animation pass
- final Java diff report

## Known engine substitutions that still remain

These are not missing Java source code; they are cross-platform engine differences:

- Forge arbitrary `IFluidHandler` / third-party fluids vs the scripted stable-Bedrock oil/vat layer.
- Create funnels/tanks/machines require a Bedrock Create compatibility target before true automation can be claimed.
- Numb's Java GUI-mixin crosshair motion still has no safe per-player stable Bedrock HUD-offset API.
- A2.6 Oil Residue's double-bonemeal approximation currently covers numeric growth-state crops, not every Java bonemeal target.

## Verification

A2.7 has a dedicated workflow, `.github/workflows/gameplay-core-a27.yml`, which rebuilds A2.0 -> A2.7 in order, checks JS syntax and A2.7 parity assertions, runs the official checksum-pinned bridge. Dash v1.2.0 compiler, compares the compiled packs against sources, and only publishes generated A2.7 artifacts on `main`.

Until that workflow and real Minecraft/BDS testing have run, this document does **not** claim runtime acceptance.
