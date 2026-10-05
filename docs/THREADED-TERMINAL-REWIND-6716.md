# Authoritative fresh-session boundary, private 6716

6715's flushed native log had zero errors, but original source frame 352 at
5.867 seconds still showed the complete three-piece meal. Adjacent source
frames 351 and 353 were empty. The former longer idle flash was suppressed;
this one-frame return still fails the strict completion target.

A stale local auto-repeat is a hypothesis, not directly measured query data.
The demonstrated source hole is precise: 6715 clears terminal ownership on
any local using=true/rewound bite-stage frame, even while the authoritative
server session is still terminal.

This client-only change retains terminal ownership through that local rewind
when the exact owner/hand/profile and visual snapshot still match and the
existing server elapsed property has not reset. Its retained elapsed value is
separate for identity/hand and every read keeps an explicit zero fallback.
Visibility is held only for local stop or a stage rewind during that old
terminal session. A decrease in authoritative elapsed acknowledges a fresh
server session and releases an identical new serving; existing phase, owner,
snapshot, early-interruption and rejoin boundaries remain intact.
Terminal acquisition additionally requires the unchanged source third-bite
checkpoint in authoritative ticks: 71 for THREE, 70 for THREE_ALT. This prevents
a fresh server phase from reacquiring an old local end clock before its counter
restarts. It does not move any source bite/curve or consumption checkpoint.

Source basis: `main.js` publishes `eat_elapsed_ticks` from the captured active
start on each presentation tick, and clears it on native completion/cleanup;
`player_presentation_core.js` computes clamped elapsed ticks from that start.
No new player property, server patch, delay, curve, consumed metadata write or
consumption change is introduced. The ordinary THREE JSON duration is 5.0
seconds; THREE_ALT is 4.5 seconds. Native timing must use the actual session.

Cold native testing still decides whether this hypothesis closes the last
frame. Startup log cleanliness, every hand/form, exact Java parity and
full-family acceptance are not inferred from source tests. 6715 remains
immutable; 6716 is a fresh private identity, with no public or live change.
