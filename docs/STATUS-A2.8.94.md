# G94 single binary client diagnostic

This isolated candidate follows frozen public G93 `44c5fd8a786addf6cf1881ba5f7d665f0f492b0c` / tree `b555875c13464c377ac8d81adc4d01ca7b0b5a00`. One default-off eight-row board exposes the selected raw word0 and existing decoded tail in one screenshot. It is a diagnostic, not a production arithmetic or rendering repair.

The existing `kg_plate_qa` writer and raw word4=1/marker133 guard remain unchanged. The board uses explicit geometric0/1 digits, opaque light tiles, row labels, printed7-to0 column headers and fixed controls. Read MSB screen-left in either hand; use the labels/corner mark instead of reversing the offhand grid. Only new QA geometry, one additional QA render controller and attachable references are introduced. BP, schema/packing, stored data, production decoder/order, all33 prior controllers, meshes, animations, poses and arms are conserved. Reviewed six-file patch SHA256: `052a29fc9deff0617a15425600f5267c854212cc26b59570fd083e7f8fee553b`.

## Eight-row legend, top to bottom

- H: raw word0 bits23..16; expected `01111110`
- M: raw bits15..8; expected `01101100`
- L: raw bits7..0; expected `00011001`
- C: count bits2/1/0, fractional-raw flag, exact half-step flag, fixed0, fixed1, enabled reference1; expected `00100011`
- D: negative-raw flag, descriptor bits6..0; expected `00111001`
- 0: food0 bits7..0; expected `11000111` (199)
- 1: food1 bits7..0; expected `11000011` (195)
- 2: food2 bits7..0; expected `10110100` (180)

Raw integer bits use only power-of-two floor/subtraction, without nonbinary divisors or large equality predicates. Negative and fractional flags distinguish those raw-query cases. The production `/123` decoder is untouched; its float32 reciprocal-boundary possibility remains unproven until actual client values are observed. Old bounded numeric logging/posts/constant-food controls remain conserved, but this round does not depend on logs.

Focused probe/frame, opacity/contrast/shaft-clearance, unchanged-frame viewport projections and exact frozen-G93/current-G94 conservation are source evidence only. No intermediate candidate or native acceptance is claimed. Root owns the single native observation and its private evidence; no screenshots or private evidence URLs are published here.

Main `3134539ae4b846b55db29a80aa42dd5f8563aeb2` has an independent colliding G86 lineage, and earlier main930 has colliding G85 history. No rebase/consolidation occurs here. Keep the draft source/history/CI and missing-current-BSM gates open, with `client=false`, `production_ready=false`, `pending_client_acceptance`. Full historical verification remains in wrapper94 but is not run before this bounded diagnostic handoff. No merge, Release or live deployment.
