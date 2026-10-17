# Original ProjectileDodge audio and category scope

Cookery 1.6 requests `SoundEvents.ENDERMAN_TELEPORT` twice after a successful
ProjectileDodge teleport: once at the original position with PLAYERS category,
volume1/pitch1, then through the living actor at its new position. Grilling
previously used one Bedrock destination event. This change imports only the
original two selected samples and provides an owned sound helper for those
two call sites.

Author sources: [Forge1.20.1](https://github.com/KaleidoscopeMods/KaleidoscopeCookery/blob/2f4e386ce23f49a385ddf003c67fc6415c55417a/src/main/java/com/github/ysbbbbbb/kaleidoscopecookery/event/effect/ProjectileDodgeEvent.java#L90-L94)
and [NeoForge1.21.1](https://github.com/KaleidoscopeMods/KaleidoscopeCookery/blob/4d39e36cfa749939ba5f9d6d3b715ef9a984cb9c/src/main/java/com/github/ysbbbbbb/kaleidoscopecookery/event/effect/ProjectileDodgeEvent.java#L90-L94).
The exact revisions, distinct Minecraft publisher asset indices, source event
entries and original sample records are committed in
`development/gameplay_core/fixtures/java-projectile-dodge-audio-160.json`.
Forge1.20.1's publisher metadata/index/sounds manifest were read independently
of the existing reviewed NeoForge1.21.1 reference. Both event entries and both
sample publisher identities/lengths match; this result was verified rather
than inferred from their similar event names.

Selected originals, by Mojang:

- [portal.ogg](https://resources.download.minecraft.net/7b/7b4b5323ef066caa1ae43cbe66fffd9dfce4ed32), publisher identity `7b4b5323ef066caa1ae43cbe66fffd9dfce4ed32`, 10010 bytes.
- [portal2.ogg](https://resources.download.minecraft.net/35/35461b6a4253db40973549e82d91f267c686be85), publisher identity `35461b6a4253db40973549e82d91f267c686be85`, 7442 bytes.

`tools/build_projectile_dodge_audio.py` is an offline selective producer. It
checks these two source assets at their import boundary and adds only their
owned aliases and the reviewed category adapter. It does not download or
export a game JAR, rebuild the six unchanged feedback events, replace author
resource packs or introduce a Tavern dependency. `--cache` accepts the selected
source asset cache; `--check` verifies the candidate's two assets, selected
definitions and generated category core.

`projectileDodgeTeleportFeedback(entity, origin)` only attempts sound commands;
the caller owns the already successful teleport and its immutable original
point. It attempts origin and destination independently. A failed origin cue
still allows the destination cue; a failed destination cue retains the origin
cue. No audio failure retries movement, spends effects or aborts the other cue.
It returns bounded delivery counts for native API checks, which are not human
audibility or rendering evidence.

The origin alias `kg_java21.teleport` is always category `player`. Destination
aliases reuse the same two samples and choose these **reviewed vanilla** actor
categories from the official Minecraft1.21.1 class hierarchy:

| Bedrock actor ID | Reviewed Java category | Source implementation |
| --- | --- | --- |
| `minecraft:player` | PLAYERS | `Player.getSoundSource()` |
| `minecraft:cow` | NEUTRAL | inherited `Entity.getSoundSource()` |
| `minecraft:zombie` | HOSTILE | inherited `Monster.getSoundSource()` |
| `minecraft:bat` | NEUTRAL | inherited `Entity.getSoundSource()` |

Bat is deliberately NEUTRAL: its name or `AmbientCreature` parent is not proof
that this original teleport call uses AMBIENT. The source class chain was read
directly. Unreviewed actor IDs use an explicit neutral adaptation, reported as
`destinationCategoryReviewed=false`; this is not a complete Java registry,
Forge subclass or arbitrary addon classification claim.

Java's destination `living.playSound` also checks `isSilent()` and uses the
actor's dynamic sound source. Stable Bedrock exposes no generic equivalent of
either query. The helper does not invent a silence property, query or tag.
Silent/custom actor behavior, exact mixing and attenuation therefore remain
listed platform/client differences. Identical OGGs and accepted server commands
cannot establish human playback acceptance.

The same source review found a flatulence category mismatch. Both Cookery
Java branches play that sound with PLAYERS category. The current original
Cookery1.6 Bedrock event uses `neutral`. Grilling's owned alias
`kg_cookery.flatulence` corrects only the category and references the existing
three source-proven Cookery sample paths, without copying those files or
editing the host RP. Both maintained `ModSounds.java` implementations register
the fart event with `createFixedRangeEvent(...,16.0F)`, so the owned alias also
sets `max_distance:16` rather than inheriting an unknown Bedrock default.
`FLATULENCE_SOUND_ID` is exported by the helper module for the caller; pitch
remains the source range 0.8–1.2 and volume1. This numeric source range does not
certify the native attenuation curve or human audibility.

`test_projectile_dodge_audio.mjs` checks both source records, selected sample
weights/gain, actual helper call sites and actor mappings, independent sound
failures, unknown-category scope and the host sample references. These are
API-operation/source checks. They do not use Minecraft players or certify
native collision order, actual sound mixing or human acceptance.

Relevant stable API: [Entity](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/entity?view=minecraft-bedrock-stable)
and [Dimension.playSound](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/dimension?view=minecraft-bedrock-stable).
Client and production-ready status remain false until actual acceptance.
