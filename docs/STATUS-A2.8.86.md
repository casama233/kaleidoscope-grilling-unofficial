# G86 projectile-dodge liquid admission and Hinder living classes

Previously native block collision alone could accept a sampled dodge whose body
overlapped liquid. The movement helper now checks every cell in the translated
native AABB after targeted dismount and before teleport: water, lava, waterlogged
blocks and the reviewed water-carrying vanilla plants/bubble columns reject the
attempt. Unreadable flags/blocks, unknown registry identities and oversized
volumes fail closed. Sixteen sampled attempts, fee settlement and original
teleport feedback remain unchanged. A later successful dry attempt clears the
earlier rejection reason. Dimension changes after dismount and re-mounting during
the precheck stop movement rather than applying permission from stale context.

Hinder now maps Java LivingEntity membership using health plus native mob family,
player or armor-stand identity. Health-bearing boats and minecarts are excluded
as both attacker and victim; the victim receives the original100-tick amplifier1
slowness. Reported living attacker priority and recognized arrow-owner fallback
remain intact. No positive-health or positive-damage restriction is added.

The fluid-cell predicate is independently reviewed in the original maintained
Forge and NeoForge delegates. Java performs downward support search before its
collision/liquid checks. This release only improves admission at the sampled
native candidate: exact Java ground adjustment, native versus Java body/pose
geometry, collision shapes and engine phases remain unfinished. Generic custom
entity inheritance and unreviewed block IDs remain explicit mapping limits.
This is not complete movement parity or an exemption for known portable bugs.

Source-operation adapters and isolated native observations establish only their
recorded cases. Canonical Git checks, complete-family loading and saved-world
admission precede live development deployment. Actual player rendering, heard
audio and physical gameplay acceptance remain pending with client=false and
production_ready=false. Previous source/evidence/failure history is preserved.

See [liquid source and API boundaries](PROJECTILE-DODGE-LIQUID-20261007.md),
[Hinder source classes](HINDER-LIVING-DAMAGE-CLASS-20261007.md),
[retained G85 changes](STATUS-A2.8.85.md) and
[the complete Java fidelity goal](JAVA-FIDELITY-GOAL-20261007.md).

Selected native1.26.51.1 observations passed with normal stops: repeated wet16 rejection, wet→dry second-attempt success and paired dry/waterlogged top-slab admission; cow/armor-stand class reads, actual cow-attributed SlowII and vehicle-attributed cow hurt without SlowII. Ordinary selected vehicles have no health component, so health-bearing vehicle fixes remain source/API compatibility evidence. Vehicle-victim hurt callbacks were not observed. Failed concurrent startup attempts remain separate failed evidence.
