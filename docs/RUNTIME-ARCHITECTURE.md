# Gameplay Core Runtime Architecture

## Canonical runtime

The current release source is exactly:

- `projects/grilling/gameplay_core/behavior_pack/`
- `projects/grilling/gameplay_core/resource_pack/`
- `projects/grilling/gameplay_core/config.json`

The behavior-pack manifest has one Script API module entry: `scripts/main.js`. Runtime modules may be imported by that entry, but they are not independent pack entrypoints.

`development/gameplay_core/augment_a*.py`, version-specific verifiers, archived CI workflows and historical reports remain useful for provenance and replaying old checkpoints. They are **not** the default path for editing or packaging the current release. A current fix must be visible in the canonical BP/RP before it is considered deliverable.

## Current source → artifact path

1. Edit canonical BP/RP.
2. Run `python tools/check_grilling_release.py`.
3. Compile `projects/grilling/gameplay_core` with the checksum-pinned bridge. Dash release used by CI.
4. Run `python tools/check_grilling_release.py --compiled` so every canonical source file is present in the compiled pack and JSON is semantically identical.
5. Run `python tools/build_grilling_release.py` to make a sorted, fixed-timestamp candidate `.mcaddon`.
6. Verify the produced ZIP, packaged manifests, Script API entry and SHA-256.
7. Treat Minecraft client/BDS/Android visual acceptance as a separate evidence layer.

This means old augmenters cannot silently overwrite a newer canonical runtime during the normal release path.

## Runtime ownership rules

The project is not yet fully converted to one central event router. Until that migration is complete, every runtime module must follow these rules:

- A gesture is owned by one module after its target predicate matches.
- Repeated `playerInteractWithBlock` callbacks must honor `isFirstEvent` where the action is edge-triggered.
- Java rules live in core/contract modules; Bedrock event routing and inventory mutation live in runtime/adapters; HUD, animation, sound and particles remain presentation responsibilities.
- Do not fix display bugs by changing recipe, consumption or persistence semantics.
- Do not add a second pack-level script entry to solve a routing problem.

Known current owners include the grill/seasoning path in `main.js`, plate/recipe placement in `a25_plate_recipe_runtime.js`, oil press/big vat in `a26_oil_machine_runtime.js`, typed Cookery oil-pot state in `a2736_typed_oil_pot_block_runtime.js`, Advanced Rack in `a2746_advanced_rack_runtime.js`, and Cookery host cuisine metadata in `a2750_cookery_cuisine_runtime.js`.

A later cleanup can move these handlers behind one dispatcher, but only after preserving each module's exact Java/host priority and cancellation rules. Mechanical consolidation is not itself a correctness improvement.

## Hot-path policy

### Grill registry

The grill registry is still polled every tick because cooking timers and Java-like support/leg state need live updates.

A2.7.61 changes persistence only:

- when `tickState` actually changes grill state, persist it;
- when the state is unchanged, do not rewrite the world dynamic property;
- always keep `syncGrillPermutation` running so support changes can still update `legged`.

Cooking timers therefore remain crash-persistent at the same tick granularity. Idle grills stop generating redundant persistent-state writes.

### Oil press registry

A registered press already came from the registry being iterated. The timer path therefore calls `writePress(..., false)` and does not reread/re-register the same press. The registry list is rewritten only when invalid entries were actually removed.

The press completion delay remains tick-accurate; this is a write/read reduction, not a timing change.

## Validation boundary

Static JSON/JS checks, UUID/dependency checks, Dash compilation and source-vs-compiled comparison prove structure and packaging consistency. They do not prove first/third-person transforms, Android rendering, transparent materials, animation timing, HUD coexistence, multiplayer behavior or real BDS interaction.

Those claims require the corresponding real client/server evidence and must be reported separately.
