# Grilling 2.8.61: held seasoning contents and eating projection

Unfrozen local review work. No merge, release, live deployment or complete Java parity claim.

## Confirmed defects and canonical changes

- Partial seasoning bottles retain the empty-bottle item identity and their native ingredient data. Previously their held attachable displayed only the shell, while the placed renderer displayed contents. The candidate projects up to eight actual ingredient entries per hand into client-synchronized properties without replacing ItemStacks, changing identity or rewriting their metadata.
- Pending bottles previously used a fixed half-full held model. Empty/partial/pending held routes now select the actual source-derived sixteen half-layer cuboids and ingredient colors. The finished-bottle route remains separate.
- Placed pending contents retain the Java cuboid bounds. Direct opaque palette textures replace UV-animated atlas sampling. This is a candidate fix for the reported striped interior; a clean native visual comparison is required before assigning the exact rendering cause or declaring it resolved.
- All forty skewer attachables previously applied Java first-person child displacement in third-person too. That motion is now first-person-only, leaving the native third-person arm path intact.
- A server-session elapsed-tick property supplies remote bite-stage progress. The user's observer recording demonstrates bad movement; remote native countdown behavior itself remains unmeasured. This clock is a defensive presentation fix, not a claim that a second defect was independently reproduced.
- First-person projected arms require the matching item, profile and hand. Food debit/reward settlement remains event-owned.

## Validation boundaries

Focused tests cover source palette/geometry, held-content synchronization and metadata non-mutation, native-storage transactions, observer phase boundaries, exact item/profile/hand gates, generator round trips and historical pose preservation. The combined player property count is 27 of 32.

Full canonical validation is being reconciled against the changed, explicit rendering contract. Actual native client, BDS, complete-family admission, saved-world migration and exact-head CI are separate gates. Instrumented native probes are test-only and must never be imported into a release.

Still open: complete camera/skin/posture/observer coverage; native offhand eating activation; random THREE versus THREE_ALT duration consistency; ONE/THREE detached-piece/helper-arm rendering; all other previously documented Java feature gaps. Native inventory icons remain static; this candidate addresses held and placed ingredient visuals.
