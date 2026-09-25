# A2.7.67 — Server schema correction test build

PR #71 is merged into the existing development line (commit `96fd50ceefe07fed20f689520a9737fd19e83b31`). The larger PR #70 remains under review; this is not a merge of that entire project into main.

## Changes

Eight workbench recipes now have ingredient-based unlock data, without changes to their ingredients, shape, counts or output. All six declared big-vat material maps now use blend for both shell and fluid, removing the confirmed alpha_test/blend mismatch while retaining liquid transparency and existing assets.

UUIDs, public Cookery 1.0.6 dependencies, gameplay scripts, model/texture data and saved-state formats are preserved. The new verifier checks 23 blocks, 133 effective material maps, 72 block_placer references and the eight crafting recipes. Reversing only the approved recipe/material changes reproduces the normalized hash of all 1,239 non-manifest runtime files from A2.7.66.

## Evidence

Canonical PR CI `36109405098` passed source checks, checksum-pinned Dash compilation, actual source/dist comparison and deterministic packaging. The downloaded compiled package independently passed the schema/baseline verifier. Its SHA256 was `4c0406f8281718a429491399dad5bac4ba2e9d435587b8d772f8dd3be0ffc86a` (1,730,388 bytes). This release marker rebuilds the same runtime through the existing publication pipeline.

## Limits

Minecraft tested: **NO**. BDS tested: **NO**. Client visuals tested: **NO**. No simulated-player interaction tests were run for this data-only correction. Material validation is not proof of on-device alpha sorting or elimination of all reported warnings.

The identifier-free `Block  couldn't be found in the registry` message remains unattributed. Existing private-server Cookery UUID rewiring and server-edition adapters remain necessary for deployments using them; this public package does not silently replace those adapters. A Magic Way HUD coexistence is being corrected separately in the Tavern repository.

See [the server-status follow-up](STATUS-A2.7.67-SERVER.md) for the historical checklist, changed files and outstanding validation.
