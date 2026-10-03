# Native stop cancellation P0

This isolated source repair follows `6ce5f020b1b64231efdd5a4b031c8dbd0431fc30`. No pack identity, release, deployment, item definition, animation, metadata serializer or offhand write changes.

The owner recorded ONE fish start tick 390947 / duration 90 / amount 1, stop 390982 / remaining 55, then an empty main slot at 390984 without completion. Independently THREE pearl start 393804 / duration 100 / amount 2, stop 393840 / remaining 64, then amount 1 at 393842 without completion. Production-subscriber API doubles reproduce both losses before this repair (two failing regressions).

The cause is the stop subscriber's `used + 1 >= 25` test, which calls `hungerSettle` after release. Its existing inventory transaction clears amount 1 or decrements amount 2. The helper renderer creates no ItemStack and is not this debit path.

Stop now captures the event tick and native remaining duration before deferred cleanup. Its manual fallback requires `nativeEatingCompleted(start, stopTick, nativeDuration, remaining)`: remaining must be numeric zero and the original inclusive boundary must hold (90 ticks at delta 89; 100 at delta 99). Cleanup, exact item/metadata/current-hand identity, native completion precedence, old-session protection and duplicate-stop protection remain. Positive remaining, short zero-remaining events, missing/invalid remaining and a late cleanup cannot settle a serving. Native completion itself and the helper animation are unchanged.

This deliberately changes Bedrock cancellation policy at the owner's explicit request. Pinned Java `MultiBiteSkewerItem` allows partial release settlement after its 25-tick readiness checkpoint. Cancellation preservation therefore is not a claim of identical Java gameplay semantics. The authored visual checkpoint remains unchanged.

Validation: 84 production-body/API-double tests pass, including both recorded cancel cases, terminal fallback for 90/100 ticks, both hands, Creative, metadata/opposite-equipment preservation, completion/stop event ordering, duplicate events, replacement sessions and delayed cleanup. Full `verify_current.py` results are recorded separately in the delivery evidence. None of these tests uses simulated players or certifies native client behavior.

Integrate the isolated commit rather than replacing the root's current `main.js`: retain the root's restricted-event getter/after-safe changes and PR124 final metadata/type-ID normalization repairs. Native/BDS/client acceptance remains the owner's gate. A fresh real-client cancel at about 1.8 seconds must retain both quantity and metadata without completion rewards; complete use must still consume exactly once.

Separately, ONE's pinned helper arm and piece transform are constant after 2.75 seconds. A fresh source-only camera-space calculation places all cooked-fish corners in front of the camera (late depth 0.521081 to 0.678292 blocks) and yields no near-plane crossing between 1.167 and 4.5 seconds. Thus a new giant upper-right frame at 3.8-4.4 seconds cannot be explained by a change in those authored helper curves. This conditional calculation does not certify the Bedrock rig, camera or multi-render-controller binding. The helper visual defect and true second-observer acceptance remain unresolved; activation is still limited to the two representatives.
