# 2.8.61 — native materials and fixed palette UVs

The client's undefined custom material caused both placed and held seasoning
layer aliases to fail. Remove the custom material dependency entirely. Select
per-color geometry whose UV coordinates already address the correct palette
tile, using the existing native entity_alphatest_one_sided material. No shader
UV animation, custom material registration or additional texture handles are
required. Keep the same atlas pixels, geometry shape, palette indices, fill
selectors, packed hand properties and Java seasoning motion.

The source gate checks that every face in every held/placed palette geometry
stays inside its assigned tile and that all 32 controllers use the native
material without uv_anim. Advance runtime and guide 0.3.30 identities and
append the immutable history. 2.8.60 remains an intermediate Git revision;
the final family candidate uses 2.8.61. Client rendering remains pending.
