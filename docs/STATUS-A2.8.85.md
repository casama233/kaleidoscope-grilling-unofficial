# G85 finite projectile-dodge claims and original feedback

G84 queued a200-tick charge after cancelling each hit. Two same-tick projectile
hits could therefore both see the unspent effect and obtain two dodges from one
charge. G85 reserves each charge in memory before cancellation and acknowledges
its stored debit once in the mutable callback. Remaining1 or200 ticks admits one
hit;401 admits three. Failed native reads/writes close that observed generation
instead of refunding already cancelled hits. Explicit acknowledged refresh/clear,
lifecycle and observable effect replacement invalidate old claims. Owned expiry
and cost removal retain claims already admitted at the original time.

The named effect uses the real absolute clock and a monotonic observed watermark;
time rollback cannot enlarge its budget. Unrelated effects retain their existing
clock behavior. No offline player write or new saved-state schema is introduced.
The source cases execute the actual production subscriber and effect adapter;
API-operation adapters are source evidence, never client acceptance.

Combined ProjectileDodge/Invincible follows the reviewed source phase order:
admitted projectile dodge spends its charge and teleports before an invincible
damage hook can run. A depleted dodge or a non-projectile hit still reaches
Invincible. External addons may cancel before this subscriber; the adapter does
not claim Java event-priority equivalence across arbitrary addon ordering.

Successful movement uses the original16 uniform attempts, vanilla logical-height
clamps and single-rider dismount. The original two portal samples and separately
attempted old-site PLAYERS/destination category cues are restored. Player, cow,
zombie and bat categories have reviewed source; other actors use an explicit
neutral fallback. Flatulence gets an owned PLAYERS alias with the source fixed
range16, referencing the existing Cookery samples without replacing its RP.

Retained limitations include stable before-hurt/deferred mutation instead of Java
projectile-impact SKIP_ENTITY, Java ground/no-liquid/navigation/TELEPORT-event
semantics, custom logical dimensions, infinite effect durations, generic silent
actors and unreviewed categories. A hit already cancelled cannot be undone if
milk, logout or replacement invalidates its later callback. Arbitrary third-party
same-byte remove/reinsert cannot be observed. These are explicit boundaries;
the candidate does not claim complete collision, lifecycle or client parity.

Actual native cows/arrows confirmed the1/200/401 finite capacities, acknowledged
fees, health and combined-effect order. Two sound API commands were accepted.
A separate actual-helper rider case confirmed immediate target-only exit and
next-tick mount-list acknowledgement; the earlier failed immediate-list
measurement is preserved. This is neither heard audio nor player acceptance.
Canonical PR/CI/merge and complete family admission are recorded separately. Keep client=false, production_ready=false and
pending_client_acceptance until real client review. Existing G84 oil/Hinder and
earlier eating, ownership, guide and rack repairs remain preserved.

See [audio and movement sources](PROJECTILE-DODGE-AUDIO-20261007.md),
[movement bounds and dismount](PROJECTILE-DODGE-MOVEMENT-20261007.md),
[combined-effect order](PROJECTILE-DODGE-INVINCIBLE-ORDER-20261007.md),
[the previous release](STATUS-A2.8.84.md) and
[the complete goal and client work](JAVA-FIDELITY-GOAL-20261007.md).
