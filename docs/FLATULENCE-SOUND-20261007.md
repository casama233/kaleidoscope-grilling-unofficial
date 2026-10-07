# Original flatulence sound origin and float pitch

Cookery 1.6.0 plays its fart cue from the center of the player's block position.
Grilling's prior producer used the continuous feet position and double-precision
pitch arithmetic. The new `flatulence_sound_runtime.js` provides the original
sound coordinates and scalar pitch for the caller to use after Cloud emission.
These helpers do not emit particles, move actors, read effects or play sound.

The maintained [Forge source](https://github.com/KaleidoscopeMods/KaleidoscopeCookery/blob/2f4e386ce23f49a385ddf003c67fc6415c55417a/src/main/java/com/github/ysbbbbbb/kaleidoscopecookery/network/message/SimpleC2SModMessage.java#L48-L58)
and [NeoForge source](https://github.com/KaleidoscopeMods/KaleidoscopeCookery/blob/4d39e36cfa749939ba5f9d6d3b715ef9a984cb9c/src/main/java/com/github/ysbbbbbb/kaleidoscopecookery/network/message/SimpleC2SModMessage.java#L48-L57)
both send the Cloud packet first, then request PLAYERS sound at
`player.blockPosition()`, volume1, with `0.8F + (float)Math.random() * 0.4F`.
The original compiled handler was also inspected independently in each author's
[Forge release](https://modrinth.com/mod/kaleidoscope-cookery/version/Ghp0qCKY)
and [NeoForge release](https://modrinth.com/mod/kaleidoscope-cookery/version/g8w0b2ly).
Both contain the same pitch operations: float0.8, one `Math.random()D`, `d2f`,
float0.4, `fmul`, `fadd`. Only the selected handler class and ZIP metadata were
acquired; no complete author archive or class is distributed by this change.

The independently reviewed official Minecraft1.20.1 and1.21.1 `Entity` bodies
floor X/Y/Z into the cached block position. Each `Level.playSound` BlockPos
overload then adds0.5 to all three axes. The fixture
`development/gameplay_core/fixtures/java-flatulence-sound-160.json` records
the separate source revisions, publisher release identities, mapped bodies
and pitch opcode positions. These facts were read separately for both versions.

`flatulenceSoundOrigin(entity)` reads the actual `entity.location` once and
returns a new `{x,y,z}` at each floored coordinate plus0.5. For feet
`(1.2,80.1,-0.2)` it returns `(1.5,80.5,-0.5)`. Cloud must still originate
at continuous `(1.2,80.35,-0.2)`. Negative fractions use floor, rather than
truncation. Unavailable, nonfinite or out-of-signed-int BlockPos coordinates
return `undefined`; the caller must retain bounded sound-failure handling.

`flatulenceSoundPitch(random = Math.random)` takes exactly one double draw in
`[0,1)` and rounds at the original float cast, multiply and add boundaries,
including the two float literal constants. With draw0.1, Java yields
0.8400000333786011; rounding only the final double result yields
0.8399999737739563. A valid double draw close to1 can cast to float1 and produce
1.2000000476837158. The helper preserves that original result without clamping
the rounded draw or sampling again. An unavailable or invalid generator returns
`undefined`. A small Java scalar oracle supplies the fixture's expected values;
it is not a Minecraft execution or client test.

The module re-exports the existing `FLATULENCE_SOUND_ID`,
`kg_cookery.flatulence`. Its PLAYERS category, fixed range16 and existing three
Cookery samples remain supplied by the previously reviewed owned alias. No
asset, alias, host resource pack or dependency changes are made here.

`test_flatulence_sound.mjs` exercises only the new origin and pitch contract,
including negative/fractional/integer coordinates, one location snapshot,
unavailable reads, the independently calculated float difference and one-draw
failure boundaries. Those source/API-operation checks do not certify native
sound commands, mixing or audibility. Original Java and Bedrock random sequences
are not synchronized. Cloud attraction, its client-side random stages and
physical input/network timing remain separate gaps. Client and production-ready
status remain false until actual acceptance.
