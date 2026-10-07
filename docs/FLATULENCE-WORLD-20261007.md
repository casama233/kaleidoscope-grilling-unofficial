# Original flatulence world capture

Both maintained Cookery1.6.0 handlers capture a ServerLevel local before
sendParticles and retain that same local for playSound. Forge source line51
and compiled offsets26/29/64/97, and NeoForge source line50 and offsets30/33/
68/101, separately establish level-read/store/Cloud/sound order. References
and the exact owned canonical G94 before-producer are in the compact fixture
java-flatulence-world-160.json; original classes and private dumps are omitted.

The NEXT producer captures the current native dimension after its existing
impulse and before Cloud delivery, then reuses it for sound. It still reads the
sound location after Cloud and keeps G94 block-centering/float pitch, original
alias/range/samples, continuous ten-Cloud coordinates and held-sneak bookkeeping.
The sound-origin fault behavior and other effects/movement remain unchanged.

Two new actual-producer source-operation cases compare canonical G94's exact
line against NEXT. An injected particle-delivery callback changes dimension
and location: G94 sends sound to the new dimension, while NEXT keeps the original
world and uses fresh centered coordinates. A second callback makes a later
dimension getter fail: G94 skips sound, while NEXT uses the retained world.
These controlled source/API adapters are not real native dimension-changing
callbacks or players. No such native failure has been observed; ordinary stable
synchronous particle behavior is not thereby certified as a mutation phase.
Original client/server input and network phases, Cloud attraction/Gaussian
stages, audible sound and rendered/player acceptance remain separate gaps.
This unfrozen NEXT work is not a live release or complete Java parity.
