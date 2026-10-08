# G2.8.111 ingredient-count transactions and calibrated bottle pose

Based on canonical G110, preserving its unconditional PENDING completion,
transactional hands, consumption ingredient lore, finish sound and particles.

## Reproduced count fault and repair

Accepted same-kind additions updated ingredients and fill identity but preserved
old lore. A PENDING bottle promoted at four ingredients therefore still displayed
4/8 after all eight were stored. A production-handler/API-double regression fails
before repair with actual 4 versus expected 8. The accepted-addition path now
refreshes only owned ingredient/ready/missing-base lines, retaining custom lore,
item metadata and readback validation. It changes no ingredient identities,
order, quantities, variants, native ownership or projection contracts. Existing
stale inventory items are not globally rewritten; later accepted additions create
correct lore, and subsequent pickup/replacement/runtime reload preserves it.

Tests cover totem-first plus three bases, all eight distinct default ingredients,
empty/partial/pending fill transitions, exact 4-to-8 advance, custom metadata,
independent lower bottles, pickup/replacement/reload and ninth-add rejection.
API-double reload is not a Minecraft save/restart certificate.

## Source-exact warning

Current Java SeasoningBottleBlock pickupOne and playerWillDestroy warn in chat
with message.kaleidoscope_grilling.missing_base_seasoning when ingredients are
nonempty and lack any of the three bases, irrespective of semantic bottle kind.
This candidate emits that existing translated key only after successful pickup
or committed player-break drops. Support loss, explosion/nonplayer destruction,
empty/complete lists and failed transactions stay silent. Drop contents and
transaction semantics remain unchanged. No actionbar, polling or invented text.

## Exact tested pose integration

Integrates the already native-tested PR172 calibration onto G110. Generator
camera offset changes from [-3*sign,5,-6] to [-1*sign,3,-3]. Only the two animation
files differ; their SHA256 values match the prior exact candidate:

- a286_held.animation.json: 7efa0944bb50d874c2b294130487c68ea2f68e55a683dc8fb78961eeb518d644
- seasoning_held.animation.json: 2dd6a636e1c56709437557dd3fd2c5ab4c48b0048e279c7f23b0dbb24be20450

Historical gates retain the reviewed inverse position delta. New exact-scope
checks retain every rotation, scale, timing and unrelated animation field.
This integration introduces no new pose tuning. Previous isolated pose evidence
keeps its original scope; it is not full G111 native acceptance.

## Identity and remaining acceptance

Fresh pack/module/pair version 2.8.111, guide/payload 0.3.41. No old release identity
or history is rewritten. Draft publication only; no merge, Release, deployment,
world mutation or installation by this task. No datapack-registry expansion or
fabricated metadata migration.

Required changed-candidate client checks: all-eight/totem-first/last/replaced
count after pickup/restart; both-hand start/hold/finish/cancel and exactly-once use;
authentic missing-base old PENDING completion; sixteen-use output and ingredient
order; consumption count after sprinkle/pickup/restart; heard finish sound and
visible particles; same-camera both-hand idle/shake/sprinkle/return; missing-base
pickup/player-break chat with complete/empty/failure controls. Saved-world and
full-family acceptance remain separate. client=false, production_ready=false.

## Upstream status read for this draft

The existing environment's read-only check at 2026-10-08 00:42 UTC found Grilling
Forge 1.20.1 / NeoForge 1.21.1 version 1.1.1 author files 8726006 / 8726014.
Reference, newest-author and newest-stable IDs agreed. Status was checked at
2026-10-07 22:23 UTC, within its six-hour interval, without explicit errors, but
predated the 00:17 family configuration edit. Its parity remains unverified;
all_reference_release_metadata_current and full_java_parity_verified are false.
Cookery has no tracked branch entry in those records, so its latest-author status
is not established. This supports source preparation only, not complete family
compatibility, current Cookery parity, release admission or native acceptance.
