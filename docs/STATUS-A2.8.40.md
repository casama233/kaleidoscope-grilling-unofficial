# A2.8.40: owner-scoped oil debit recovery

## Confirmed failure and correction

A2.8.37 could apply a hand debit, fail its restoration, and return only ok:false.
A repeat then debited again without an acknowledgement or recovery marker. Another
case restored a legacy pot without kc_oil_count, accepted its identical visible
presentation, and subsequently treated it as a full256 pot. Both were reproduced
with production functions and fault-injected storage adapters, not native players.

Before any non-creative debit, the API now saves and reads back a prepared receipt
under the opaque player's persistent ID. Both station and stationless wrappers
share this scope, so changing station or held slot does not remove the guard.
Unscoped API callers conservatively share an unscoped receipt key. The receipt
contains before/after native item metadata and optional station context; dynamic
property enumeration/read errors prevent mutation. Private legacy count and
unrelated properties are compared during acknowledgement and restoration; public
portable oil remains authoritative over stale legacy count on successful reads.

The station path keeps the prepared receipt until both the hand debit and station
save/sync are acknowledged. Failure attempts both compensations independently.
Only exact successful compensation permits marking the receipt rolled_back and retrying. Successful operations retain a committed terminal receipt.
One latest receipt per owner is retained; a subsequent acknowledged operation may replace a terminal receipt. Unresolved receipts persist across module/server restart; there is no automatic
expiry, refund, logout/slot-change cleanup or world migration. An administrator
must inspect the saved before/after states and affected stores before recovery.

This is fail-closed recovery, not cross-store crash atomicity. It does not prevent
a player manually transferring an uncertain item to another owner; do not move
items from an unresolved operation before investigation. No uncertainty is treated
as successful restoration. Independent unaffected owners continue normally.

## Scope

Family host extension patch0.2.2 retains the original Cookery archive/UUIDs, eight
reviewed source hooks/modules and two offhand capabilities. Only the owned oil
adapter and receipt handling change. No player.json override, client animation
change, secret credentials, or live deployment. The guide remains0.3.14 because
its content is unchanged. Existing .36 icons/cancellation and .37 APIs are retained.

Focused regression cases include partial writes, throwing/silent failed restores,
legacy-count loss, complete successful rollback, failed prepared persistence,
module reload, changed stations/slots, owner isolation, creative guard preservation,
and dynamic-property read failures. Native verification is recorded separately.

Receipt settlement does not delete the durable marker. If final journal acknowledgement
fails after the hand/station mutation is already acknowledged, the operation remains
ok:true with recoveryPending:true; it is not compensated or reported as uncredited.
A prepared receipt remains blocked across restart. A confirmed committed/rolled_back
receipt permits a new operation; this is not retrying an unresolved operation.

## Concurrent source preservation

Preserves public A2.8.38 author legacy-filled defaults and A2.8.39 source-backed
Java HUD/messages, including diagnostic-only failure feedback. Their .38/.39
release identities and histories remain authoritative. The final gate chains
through .39 and retains the added legacy snapshot test alongside oil recovery
regressions. A prior private .38 recovery worktree was never frozen or published.

## Final validation

All registered source regressions pass, including 21 focused oil/food cases and
363 resolved relative imports. Exact packaging matches the frozen .40 baseline.
The latest published Tavern .85 and Liquor .49 archives were independently checked
against their frozen runtime hashes, then assembled with .40 and pinned upstream
packs into the exact 16-pack test family.

Two unmodified BDS1.26.52.3 load/restart cycles passed. A separate append-only
probe in the extended Cookery pack exercised real ContainerSlots/ItemStacks and
world-property receipts: typed debit, accessible unrelated metadata, injected
partial write and failed rollback, blocked replacement slot, exact compensation
and safe retry, plus unresolved/terminal receipt persistence across restart.
Both native cycles passed with zero players and no content/script errors.

Test-only probe import/file hashes are recorded separately from exported sources
in BDS-OIL-RECOVERY-2.8.40.json. Metadata verification is within the same script
context, not proof of reading another BP's private namespace. No client or live
acceptance is claimed. Earlier .84/.48 lab runs also passed; final evidence uses
the updated .85/.49 pair rather than extrapolating their results.
