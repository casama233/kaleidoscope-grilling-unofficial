# A2.8.30 — authored Java grip and tag-aware recipe books

Preserves all merged 2.8.28 audio/localized lore/shared-guide and 2.8.29 native grill-slot/stage work. Fixes remain in canonical source.

- Restore authored Java skewer third-person translation, replacing the prior forced palm-centre override. Geometry, UVs, bite-stage cubes and binding hierarchy are unchanged. Right and left hand frames are checked against the whole Java transform for every cube corner of all 150 bite-stage models.
- Fixed recipe books accept the same public ingredient tags as manual threading; secret custom recipes retain exact item IDs and recorded metadata. No inventory transaction semantics are relaxed.
- Held checks reject missing/duplicate/wrong view dispatch, swapped aliases, missing target bones and altered pivots/parents. Native block-item visual geometry/material/texture chains are audited too.

Blockbench editor source-frame checks and native BDS loading/storage are separate from actual Minecraft client acceptance. Native Bedrock eating remains in use: exact Java eating trajectory, mouth contact, touch, FOV, skins and resource-stack blending are not accepted by these tests. Personalized secret-skewer rendering and host-owned beef/chicken-skin acquisition remain open. No live deployment.
