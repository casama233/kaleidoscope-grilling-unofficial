# G92 bounded held-plate client diagnostic

This isolated diagnostic candidate is based on frozen public G91 `b29737b250544fea2e3ab712bad30c2c04498809` / tree `254f367835779c07963efc8ad139c13a41f048bb`. G91's bounded native observation found an empty secret-alt plate despite matching server projected/live words, with beef contents visible. Cloud loaded without the earlier syntax error and first-person trays fit the viewport. Those observations do not accept G92 or resolve player-arm behavior.

## Default-off probe

The existing `kg_plate_qa` tag enables the probe only for the exact one-row fixture `[8285209,0,0,0,0,57,0,133]`. Its derived, unused row4 word becomes `1`; removing the tag restores `0`. Cached production plans and all stored ItemStack data remain untouched. Other plates, counts, bottles and malformed inputs cannot enable this writer flag. No property schema/type/packing, inventory, lore, player model or arm changes are introduced.

The client uses this small flag, count1 and raw held-plate occupancy independently of production large-word validation. Four body-textured posts have heights1/2/3/4:

- A: probe flag/count/occupancy reached the client
- B: raw client word0 equals8285209
- C: raw client words5/7 equal57/133
- D: decoded descriptor57, shape18, style0 and foods199/195/180 match

A separate constant pass selects existing state53 geometry `Geometry.secret_0_18_1` and `Texture.food_195_s0`, bypassing dynamic arrays. It does not replace any production controller. All526 production geometries,31 production controllers, animations, palette textures and BP player bytes are conserved.

The supported [query.log](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/molangreference/examples/molangconcepts/queryfunctions/query_log?view=minecraft-bedrock-stable) route emits at most three numeric-only groups per attachable lifetime, about one second apart. Opt-out/re-entry cannot reset that lifetime cap. The thirteen-value legend is: canary914000, hand1(main)/2(off), raw0, floor0, raw5, raw7, count, descriptor0, shape0, style0, food0, food1, food2. Expected main group: `[914000,1,8285209,8285209,57,133,1,57,18,0,199,195,180]`. No player identity, position, lore or creator fields are logged. Enable Content Log File and inspect the actual client log; an absent canary leaves the logging route unverified.

## Evidence and admission limits

The exact reviewed held patch SHA256 is `47725fb4d7fc39233c6fb1919f23efcca4be2b522e3e10f050f0bb76c2d3ca2e`. Focused generator, read-only writer, expression/frame and exact frozen-G91/current-G92 conservation checks are source evidence only. Native logging, marker pixels and the constant food pass remain to be observed. Secret-alt rendering, player-arm behavior, dynamic GUI, non-default failed variants, complete Java parity and family/BSM/live admission remain open.

Latest main `93056ea40dd598761a200fa22e91de02c8eadb0a` contains PR154's colliding G85 history. This candidate does not rebase or consolidate that lineage. Keep the draft conflict/history/CI gate explicit; focused local checks are not canonical merge CI readiness. Full historical verification is retained in wrapper92 but is not a prerequisite to this bounded diagnostic handoff. The required current BSM upstream-status input remains unavailable; existing Java author pins are inherited, with no new author release adoption or latest/full-parity claim. Keep `client=false`, `production_ready=false`, `pending_client_acceptance`; no merge, Release or live deployment.
