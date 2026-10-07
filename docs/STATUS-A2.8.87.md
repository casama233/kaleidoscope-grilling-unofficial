# G87 original flatulence sound origin and pitch

The previous sneak-press producer played the Cookery cue at continuous feet
coordinates and calculated pitch with double arithmetic. Both maintained
Cookery1.6.0 branches instead use the center of the player's floored BlockPos
and float rounding at the random cast, multiply and add. G87 restores those
two sound operations in the actual producer, after its existing ten-Cloud
emission. For feet(1.2,80.1,-0.2), sound is(1.5,80.5,-0.5), while Cloud remains
at(1.2,80.35,-0.2). Draw0.1 yields the original0.8400000333786011.

One current location snapshot supplies the sound origin, followed by one pitch
draw. A failed sound-origin read skips sound without consuming randomness or
repeating the cue while sneak remains held; release and a new press can emit
a fresh cue. Particle delivery, impulse, effect checks, range16, PLAYERS alias,
original three host samples and the previous G86 movement/Hinder repairs are
retained. The new read-only helper performs no movement or sound command.

Five new helper cases and five affected actual-producer operation cases passed
in their source adapters. An isolated native1.26.51.1 observation using the
unchanged helper bytes passed actual cow location centering, Java scalar float
arithmetic and the existing alias's sound API acceptance, with a normal stop
and no real or simulated players. That observer used the previous reviewed
family plus the helper: it did not exercise this new main consumer, physical
sneak input, network delivery, audible sound or rendered client behavior.
Canonical candidate checks and full-family loading/saved-world admission are
separate required deployment gates.

Java random streams remain unsynchronized. Client Cloud attraction/Gaussian
stages, source input/network timing, downward ground search, collision shapes
and engine phases remain incomplete. Ground-table work is excluded from this
sound release. Owner-accepted platform differences remain explicit; portable
logic gaps have not been waived. client=false and production_ready=false until
actual human acceptance; live development deployment is not100% Java parity.

See [source and exact arithmetic](FLATULENCE-SOUND-20261007.md),
[retained G86 scope](STATUS-A2.8.86.md) and
[the complete fidelity goal](JAVA-FIDELITY-GOAL-20261007.md).
