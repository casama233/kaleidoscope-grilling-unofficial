# Pending seasoning placement, 2.8.105

An ordinary right-click toward a valid support previously queued placement of a
pending bottle and removed it from the held slot. Java's PendingSeasoningItem
only delegates placement while the player is sneaking; ordinary use keeps the
bottle in hand for its 80-tick shake.

Both native placement capture and the offhand supplement now require sneak for
pending bottles. The deferred write checks sneak again, so releasing it cannot
place a stale request. Empty and finished bottles keep ordinary placement. The
original base ingredients, held-use duration, completion, seasoning debit,
metadata, native storage, sound and visual assets remain authoritative.

The source-bound placement fixture reproduced six standing-hand/fill failures
and two release-before-write failures against G104. Its repaired 116 cases pass,
including exact bottle metadata, valid sneak placement, standing empty/finished
placement, both hands, duplicate events and existing rollback cases. These are
source/API adapters, not simulated players or rendered-client evidence.

This repairs a definite Java interaction difference. It does not establish the
cause of every failure reported in issue #168. Actual native use-start/completion
after a cancelled placement, finished-bottle application and the affected
inventory/held/placed display still require client reproduction. Historical
G65/G71 client clips do not certify this release. Dot contact remains pending;
client=false and production_ready=false. Generic inventory fill colors and
other unimplemented Java rendering requirements stay explicitly incomplete.
