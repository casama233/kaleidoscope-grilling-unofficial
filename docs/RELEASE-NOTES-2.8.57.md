# 2.8.57 — seasoning bottle motion and ingredient display

Sprinkling and shaking used whole-player camera-space arm offsets while the
attachable already supplied its own held transform. The bottle could leave the
first-person view. First-person motion now belongs to the bound bottle model;
the player gesture runs only in third person and sprinkling lasts the original
Java 10 ticks. Item identity and the actual use hand cancel stale presentation.

Empty and pending held bottles now render the actual ordered ingredient layers
instead of a fixed half-full special bottle. Both hands have separate synchronized
fill and packed color properties, within the native player property limit. Special
bottles retain their existing mixed variant and remaining-use models.

Placed and held ingredient layers share one palette. Redstone and gunpowder
previously fell through to the same brown fallback because native items have no
owned item JSON. Their Mojang sprites are now pinned by commit and SHA256;
all eight accepted ingredients have distinct center-half, two-color pairs.

The Java motion source is pinned to the existing 1.1.1 reference. Java XYZ
rotations are composed as matrices around the bottle center. View translation
is explicitly adapted to Bedrock's existing visible idle anchor; offhand is a
Bedrock accessibility extension. Static geometry/dispatch and native BDS load
checks do not certify client rendering. Human acceptance remains pending.

Candidate 2.8.56 was not deployed: final review caught a missing contents material
on empty bottles carrying partial ingredients. 2.8.57 declares it explicitly;
2.8.56 remains immutable in release history.
