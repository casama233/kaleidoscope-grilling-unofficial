# G2.8.112 existing-bottle pickup lore compatibility

Retains the entire G111 count, exact Java chat-warning and calibrated-pose
candidate, including all G110 completion/consumption/audio repairs. G111 remains
an immutable, distinct release identity and is not installed by this task.

G111 refreshed derived lore only after accepted ingredient addition. An existing
full PENDING eight-ingredient item with stale 4/8 lore could not accept more
materials, so its tooltip remained stale after pickup. G112 shares that narrow
owned-lore helper with normal partial/PENDING pickup. It reads actual ingredient
data from the cloned native item, verifies lore readback, then uses the existing
transaction. Only owned ingredient/ready/missing-base lines change. Custom lore,
name, flags, restrictions, ingredient order, quantities, variants and native
ownership remain unchanged; failed commits restore the original item. Finished
bottles are not refreshed; truly blank empty bottles do not gain count/status.
There is no semantic migration, world scan or automatic inventory rewrite.

The stale-full-eight partial and PENDING pickup controls fail before the pickup
call (two success-path failures; two rollback controls pass). All 202 combined
native-hand/storage API-double cases pass with it, including pickup/replacement/
independent runtime reload, opaque same-type native fields and failed-hand rollback.
These are source tests, not Minecraft save/restart or rendered-client evidence.

Fresh package/module/pair 2.8.112 and guide/payload 0.3.42; previous release history
and pose bytes remain unchanged. Exact G109-to-final comparison and archive
provenance are recorded at handoff. Required G111 native checks still apply, plus
existing full-eight stale-tooltip pickup before any shake, followed by placement,
restart and second pickup. Preserve all G109 samples in their original world;
use a separately approved clone for changed-candidate testing.

Draft only: no merge, Release, installation or deployment. Full canonical CI,
compiled equality, BDS/native/saved-world/full-family gates stay separately
reported. The upstream metadata and missing Cookery/full-parity limitations in
STATUS-A2.8.111 remain applicable. client=false, production_ready=false.
