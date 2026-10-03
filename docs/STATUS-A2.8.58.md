# A2.8.58 — scoped eating and offhand review candidate

This candidate is not complete Java parity, a merged release, or a live deployment.
Native observations below are bounded to Android x86_64 Bedrock 1.26.52.3 in an
isolated Creative world. Server checks, editor checks and native rendering are
separate gates.

## Changes

- TWO, THREE_ALT and FOUR fixed-skewer geometry use source-derived active
  arm/item transforms from pinned Java 1.1.1. Active item rendering uses Java's
  NONE item context instead of stacking motion onto the idle display transform
- Absolute player bone channels replace subtraction of `this`;
  override_previous_animation affects only the listed active arm/item sockets
- A captured start-event duration plus the native active countdown and frame
  interpolation determines elapsed seconds. Raw item-use duration queries are
  not assumed to be seconds on the tested client. Invalid durations cannot
  activate the scoped projection
- The client-synced projection property no longer prematurely stops a newly
  requested animation. Blend masking still checks it; release/item changes stop
  the animation. Owned state is cleared on new use, completion, release and spawn
- Slim child translation is resolved on the player item socket, without an
  attachable owning_entity geometry assumption
- Idle skewer_fp_left and bottle_fp_left now use the actual native left socket,
  not a fictitious mirrored right-arm empty-hand pose. Equip lowering, bob and
  the slim shoulder offset remain inherited. Right FP, all TP and rack tracks
  are unchanged by this idle correction
- bridge's stale 2.8.51 compiler output label is aligned to 2.8.58 and checked
  against baseline.json

ONE/THREE helper arms, detached food pieces, non-standing postures and other
views retain their previous paths. No RP player entity file is replaced. The
native first-person render controller is preserved outside the owned condition.

## Verified local evidence

- Full canonical gameplay-core verifier passes, including 418 relative imports
- Matrix/source, lifecycle, native-clock and true-left-socket regressions pass
- Held dispatch tests exercise profiles 2/3/4/5, projection=false, excluded
  sneaking/swimming/gliding/riding states and inactive hands
- Independent 240 Hz source comparison bounds sampled-channel approximation at
  0.09546 model pixels and 0.33173 degrees; it is not exact continuous playback
- True native-frame projection checks pass 300 skewer and 266 bottle cases;
  regression fixtures expose 150 old left skewer stages and 133 old left bottle
  cases that the previous mirrored test incorrectly considered visible
- Fresh canonical-only FOUR/raw-beef recordings on Efe/slim and Zuri/wide show
  food remaining visible and disappearing in bite stages, repeated use and
  return to idle after release
- Canonical TWO/raw-bun recording on Efe/slim shows motion and bite stages;
  early positions remain near the lower viewport edge, pending Java frame QA
- Zuri/wide 700 ms TWO cancellation followed by switching to a Tavern shaker
  does not leave the eating arm active
- Fresh canonical Zuri/wide idle checks show offhand raw beef and empty seasoning
  bottle with either an empty main hand or another held item
- A scoped third-person diagnostic recording shows arm-to-face motion and
  return to idle; it is not full third-person Java animation acceptance
- bridge 2.7.54 GUI imports 2,204 source/config files byte-identically, recognizes
  both 2.8.58 manifests, and reports successful export. Its dev build contains
  530 BP and 1,673 RP files with no missing/extra files or byte drift
- Local Blockbench MCP 1.10.0 actually imports the canonical raw-beef stage-0
  geometry (5 cubes, 3 groups); this alone does not validate its active animation

Temporary diagnostic BP/RP packs were removed after normal Save & Quit. The
original eight BP and eight RP entries were preserved exactly. Probe scripts,
worlds, client binaries, screenshots and videos are not exported in this repo.

## Explicit remaining gaps

- Full frame-by-frame Java camera/hand parity, all skins/postures/items and all
  animation profiles are not accepted. THREE_ALT has source coverage; the
  random-profile native clip does not establish complete branch acceptance
- ONE/THREE helper-arm and detached-food behavior remain incomplete
- Native offhand food activation remains unavailable in the tested input path:
  a 3-second offhand attempt emitted no itemStartUse event, while a 1-second
  main-hand control emitted start(duration=90) and stop(remaining=69). Visible
  offhand placement is not equivalent to native offhand eating
- A palette probe found offhand-height context unavailable with two held items
  but present with an empty main hand. Canonical idle poses deliberately do not
  depend on that context or on owning_entity
- Direct Java-frame comparison, random-profile duration differences, broader
  inventory settlement and saved-world migration remain separate work
- Optional Creator Tools validation is not completed. No clean result is claimed
- Family BDS, final package identity, remote CI and publication status must be
  established from their own receipts; editor/native observations above do not
  imply those steps are complete

## Frozen candidate receipts

The canonical 2.8.58 identity is frozen. The deterministic review package and
16-pack isolated BDS run passed their own checks; no logged BDS errors occurred.
Guide transfer remains sent_unconfirmed without an acknowledgement. Full client,
saved-world migration and production readiness remain false. See
[scoped acceptance receipt](ACCEPTANCE-A2.8.58.json). Remote publication and CI
are not established merely by these local results.
