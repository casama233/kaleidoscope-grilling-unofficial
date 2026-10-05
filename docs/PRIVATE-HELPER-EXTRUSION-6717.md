# Generated raw-food helper extrusion, private 6717

## Subsequent native failure

Private6717 failed the actual raw-beef helper visual check: its added side
strips detached from the unchanged main sprite. The historical source checks
below did not test Bedrock texel-to-surface alignment. The reflected-X element
conversion described below was incompatible with the existing main-face UVs,
and vertical side V was reversed. See PRIVATE-HELPER-SILHOUETTE-6718.md for the
bounded repair and an independent regression that rejects frozen6717. The
frozen6717 artifact and original receipt are retained unchanged.

This canonical source repair restores the generated-item detail confirmed by
comparison with official Java 1.20.1: the raw-last food helper keeps its complete
16×16 NONE footprint and centering, with front/back at Z −0.5/+0.5 model units
and sides derived from the referenced sprite's actual transparent outline.
It does not change helper scale, depth, placement, raw/cooked selection, hand
binding, authored THREE curves, item data or consumption. Bedrock screen parity
is still a separate client check.

## Actual texture inputs

All 213 catalog entries resolve; no substitute silhouette was chosen.

- 40 vanilla entries: 39 unique PNGs read from the installed Bedrock 1.26.52.3
  vanilla brarchives. Base pack plus vanilla_1.14 honey bottle and vanilla_1.17.0
  glow berries were used; every installed duplicate alpha mask agrees
- 113 Cookery entries: existing Cookery 1.0.8 referenced PNGs, each matching the
  catalog's recorded texture SHA256
- 60 Grilling entries: existing canonical runtime PNGs, unchanged

Only compact derived span facts and source hashes are committed. Vanilla and
Cookery artwork remains outside this repository/runtime copy; existing texture
references are unchanged. The source-fact fixture records image dimensions,
actual alpha hash and values, source PNG/archive hashes and generated spans.
One referenced Cookery icon is 64×64; its UV/pixel edge steps are normalized to
the same 16×16 model footprint. Cookery partial-alpha pixels remain occupied
because the official Java SpriteContents transparency test is alpha==0.

Installed-alpha review receipt SHA256:
48e2ac910fdf60e0c9e927bcb77e6726d337f603774cdbdf3204b9a9ff2e09cd

Installed-alpha mask catalog SHA256:
20db43788aa2c41bee0a6f726fe8c918e64f3c27f8149eb7b0b1ab144e034574

## Geometry and selection contract

The Java ItemModelGenerator span algorithm scans occupied pixels, admits an
edge only when its neighbor is transparent/outside, and merges min/max per
edge direction and pixel anchor. Its exact reflected-X held conversion, Y
boundary, east/west side names and boundary-strip UVs are retained. The full
north/south UV mapping stays unchanged. The front/back cube has only those two
faces, so its transparent rectangle background gets no enclosing solid walls.
Side planes carry only their exposed directional face and actual boundary-strip
UV; holes and disjoint gaps retain texture alpha.

The 213 entries deduplicate to 166 outline variants in one compact generated
geometry file (537,142 bytes), plus the existing hidden index-zero front/back
fallback. The existing single helper render pass selects exactly one geometry
and texture with the same raw-last index. A selected helper has at most 81
cube records: two main faces plus up to 80 single-face side planes. There are no added render passes or
player properties. Existing meal-state geometry remains in its readable file;
all non-helper meshes and unfinished items are unchanged. Native eligibility
requires both exact generated mesh documents, unchanged owned geometry refs
and the existing controller list; altered outlines fail closed.

## Preservation and verification boundary

All behavior-pack source files, all textures, both shared eating animation
files, helper selection/runtime, every terminal script and owner guard remain
byte-identical to the 6716 source. Only the two complete attachables' geometry
references, helper model data and the helper controller's selected geometry
array change exported runtime; one compact helper geometry file is added.
The 6716 terminal ownership/restart repair is not replaced or retimed.

Focused source/renderer/index/terminal tests and exact generator checks apply
to the final committed candidate. The immutable candidate receipt records the
actual counts, logs, source/copy tree inventories and archive hashes. These
checks do not establish native pixels, native startup, Java/Bedrock FOV or
lighting parity, all-hands/postures, dynamic ingredient model/tint overrides,
resource-pack replacement alpha, full-family BDS/world loading or production
readiness. Static referenced-sprite outlines require regeneration if source
resource alpha changes. Previous bounded 6716 client completion observations
remain evidence for that exact older candidate, not new 6717 native acceptance.

The private 2.8.6717 copy changes copied manifest identity fields only. No
6716 overwrite, symlink replacement, GUI operation, publication, merge,
release, installation or live deployment is performed by this source repair.
