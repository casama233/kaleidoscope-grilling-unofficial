# 2.8.60 — register the seasoning material in entity.material

The owner supplied a client content log: the custom seasoning material was
undefined, followed by missing Material.layers and Material.contents aliases.
2.8.59 shipped the definition in materials/seasoning_atlas.material. Move the
unchanged UV-enabled definition to the standard materials/entity.material
resource, alongside the same loading convention used by the existing family
and external packs. Preserve all atlas pixels, selectors and animation data.

Update the canonical asset generator and existing version-aware material
verification. Advance manifests, guide 0.3.29, payload and immutable history
together. Native BDS checks do not certify client material loading; human
client acceptance remains pending. Private client logs are not published.
