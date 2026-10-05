# Threaded completion render ownership, private 6713

Native 6712 passed the bounded main-hand origin correction but briefly drew
the full three-piece idle mesh at video 5.80–5.90 seconds before empty hand
by about 5.95 seconds. This is not the prescribed late raw-ingredient helper.

The repair changes only visual synchronization. Confirmed native completion
of a non-Creative single serving clears its exact owning hand/slot/identity's
visual indices before presentation reset, even if the server's held snapshot
still exposes the consumed item during that callback. The short-lived ownership
record clears on authoritative inventory change, changed identity or slot,
fresh use, hotbar switch or leave. Retained counts and Creative are never
suppressed. Early interruption does not create a completion record.

Only the two complete Secret attachables require a nonempty visual snapshot
as well as exact owning-item identity. This prevents all-zero completion data
from drawing an idle shaft or resetting all three foods to stage zero.
Unfinished Skewer, active/idle poses, particles, helper curves, player properties
and all item/timing/consumption/reward/effect/settlement logic are unchanged.

Focused ownership, interruption and replacement/rejoin tests establish source
scope. Root-owned native completion testing remains pending. Private 6712
stays immutable; 6713 uses a fresh private manifest identity. No public release,
merge, deploy or live change is made here.
