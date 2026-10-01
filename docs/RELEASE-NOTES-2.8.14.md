# A2.8.14 candidate: skewer hand anchor

The user's third-person screenshots show raw and cooked skewers detached from the hand, including during native eating. The previous attachment used Java display translation directly on the Bedrock bound bone. Every skewer shared that pose; the handle was not anchored at the binding pivot.

This candidate separates the bound hand anchor, authored display rotation/scale, and model origin. In third person the exposed bamboo handle centre `(0,25,-6)` is translated onto the binding pivot `(0,24,0)` **before** display rotation/scale. The display translation is zero. Consequently the grip remains on the native item bone under any inherited arm transform, including native eating. No player entity override or scripted arm teleport is added.

All 150 bite-stage geometries retain identical cubes, local cube rotations, UVs and textures. First-person transforms remain equivalent to A2.8.13. Both equipment slots retain their existing explicit dispatch. Guide previews from A2.8.13 and all integrated PR behavior are retained.

Verification separates mathematical/structural regression checks, BDS loading and actual client rendering. The anchor invariant does not prove final orientation, skin-specific compatibility, first-person mouth alignment or third-party animation compatibility in Minecraft. Client acceptance remains open. The final two screenshots match the advanced rack inventory icon and held geometry. Its wood-board centre is now anchored before third-person display rotation/scale; first-person transforms and all geometry remain unchanged.

The public Cookery 1.0.8 dependency does not authorize automatic migration of the live server's private Cookery UUID or saved dynamic properties. Production deployment remains gated on an explicit migration rehearsal and a recoverable fresh backup.
