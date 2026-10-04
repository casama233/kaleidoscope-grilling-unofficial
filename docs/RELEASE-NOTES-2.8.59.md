# 2.8.59 — enable atlas UV selection in seasoning materials

The owner supplied a live client screenshot of multicolor stripes inside the
placed ingredient bottle. Render controllers provided `uv_anim`, but their
materials did not enable `USE_UV_ANIM`; the renderer sampled the complete atlas.

Add one owned material derived from `entity_alphatest_one_sided`, enabling
`USE_UV_ANIM`. All placed and held ingredient layers resolve to this material.
Keep ordinary special-bottle and oil materials unchanged. Both canonical
generators preserve the new contract. Guide 0.3.28 and release identities advance
together. The client failure evidence is local/private; no screenshot is published.

Reference: https://learn.microsoft.com/en-us/minecraft/creator/documents/practices/improvingperformanceandresourceusage

Static and native checks do not certify human rendering acceptance.
