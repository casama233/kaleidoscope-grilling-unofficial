# 2.8.71 bottle repair candidate

This candidate is rebuilt from public G69 (`8ac0dd7625ff304b79c33fa42f41e785f39ae4d2`). The earlier local G70 object was not available from the public repository, so this release does not claim to recover its bytes or reuse its identity.

## Repairs

- Finished bottles select 64 distinct inventory sprites from the pinned Java remaining/variant models, rather than displaying the full variant-0 sprite for every state.
- Pending ingredient halves use the Java-to-Bedrock X reflection (`8 - end.x`). Ingredient 0a at Java X 5.5–8 becomes Bedrock X 0–2.5. Ordered tint halves, shell cuboids, UVs and finished meshes are preserved.
- Hidden empty/pending fill proxies preserve the canonical mechanic kind and display fill-level inventory sprites. Ingredient colors in the held and placed renderer remain driven by the ordered ingredient payload; fill-only inventory sprites cannot encode arbitrary ingredient combinations.

## Acceptance limits

Source tests and deterministic generator checks do not certify Minecraft rendering. Bottle body, ordered layers, held poses and inventory icons require native client review. Full-family BDS loading, saved-world migration and deployment are separate gates. This candidate must not be treated as client accepted, production ready or authorized for live deployment merely because source checks or Git upload succeed.

No main merge, tag or Release is part of this checkpoint.
