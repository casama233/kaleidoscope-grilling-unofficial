# Client terminal visibility boundary, private 6714

Native 6713 still drew the complete meal after the local use query became false
and before authoritative completion visuals arrived. Its 60-fps review showed
large idle food at about 18.350–18.417 s, then smaller active food through about
18.483 s. The server visual-clear-before-phase-reset remains necessary.

This repair adds attachable-local state only to Secret and its THREE_ALT form.
The terminal bite stage is retained while the exact owning item/hand's
synchronized eating phase is still active but local use has stopped. During
that gap the owned mesh passes, including the shaft, stay hidden. Authoritative
empty data/phase reset, changed snapshot/owner/hand, a fresh use or a fresh
attachable instance releases the boundary. A retained/Creative or identical new
serving is visible after authoritative phase clear. Early interruption never
establishes terminal ownership. Third-person behavior is unchanged.
Retained fields have separate main/offhand and regular/ALT names, and only the
current hand initializes or updates them, even under a shared variable store.

No timer fudge, curve, camera, player property, item metadata or consumption
change is introduced. Existing 6713 server synchronization is preserved; no
additional server patch is layered on. The two canonical generators emit the
same idempotent owned state. Native property/phase coherence and the final
client behavior still require root's cold repeated-cancel/full-use test.

The authoritative zero-before-reset order is explicit in the server source,
but this candidate does not claim that the client receives every property
atomically. If the phase reset becomes visible while stale nonzero visual
data remains, the cold native test must reject this boundary; blindly retaining
that state would instead risk hiding a Creative, retained or fresh same-ID meal.

Private 6713 and its review remain immutable. 6714 uses a fresh private copied
manifest identity. No public release, merge, deployment or live change occurs.
