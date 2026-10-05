# Explicit terminal variable defaults, private 6715

6714 native startup reported an unknown retained offhand variable before use.
Its conditional initialization assumed that a retained field existed in the
variable store exposed by that expression. The prior numeric test proxy
silently supplied zero and could not detect this startup failure.

The fix explicitly coalesces every terminal-state read to zero with `?? 0`,
including initialization, inactive-hand preservation, snapshot comparisons,
selection of retained state, and the terminal visibility gate. The generator
removes both older and newer terminal suffixes/retention rows before rebuilding,
so generation remains idempotent. No timer, phase rule or namespace is changed.

The new regression executes initialization and pre-animation against separate
bare variable objects without implicit zero defaults, and checks every retained
read for its explicit fallback. Existing terminal/identity/hand/early-release
checks remain applicable. Native startup must be free of these errors before
rendered completion can be accepted. BP, item/consumption behavior, metadata,
poses and player property count remain unchanged from 6714.

The null-coalescing form is documented in the official Molang syntax guide:
https://learn.microsoft.com/en-us/minecraft/creator/documents/molang/syntax-guide

6714 and its receipt remain immutable. 6715 is a new private copied identity;
no public release, merge, deployment or live change is made.
