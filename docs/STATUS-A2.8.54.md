# A2.8.54 — Java release-checkpoint grace (draft)

Preserves 2.8.53 use gates, nutrition and sound corrections. This candidate changes only early-release eligibility for the existing skewer eating sessions.

## Source and repair

Pinned Java Grilling 1.1.1: commit `9a1acdab27698457bec16c9362678e574895a28c`, `MultiBiteSkewerItem.java`, Git blob `612574290c1e02493e96083678c63d8c3a6905cd`, SHA256 `e350c1d628fe3067ad80b41a46928b2fb83727c9b37a1247a340fb58053e94a7`.

[Java source](https://github.com/breezeth-CN/KaleidoscopeGrilling/blob/9a1acdab27698457bec16c9362678e574895a28c/neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/skewer/MultiBiteSkewerItem.java): lines 30–31 define minimum 25 and release grace 1; lines 199–208 mark readiness at 25 without granting nutrition; lines 256–274 settle once if ready or within the release grace.

- A fresh release at 23 ticks does not settle; 24 and 25 ticks can settle if the same eligible serving remains held.
- Elapsed time is captured at the stop event. Deferred cleanup cannot turn a 23-tick stop into an eligible one.
- Native completion duration and event identity checks remain unchanged. Completion wins either completion/stop event order; a deferred old stop cannot remove a new session.
- The graphical readiness checkpoint remains 25 ticks. No nutrition is awarded merely by reaching a checkpoint.

Eight deterministic tests execute the production complete/stop callbacks, covering boundary eligibility, delayed cleanup, both event orders, duplicate stops, early completion, replacement sessions, item identity and absent items. The pre-fix run reproduces refusal at 24 ticks. This is callback verification, not a claim about native event-clock timing.

## Real-client development workflow verified separately

A disposable diagnostic BP in `development_behavior_packs` was loaded by an actual Android Bedrock 1.26.52.3 client through minecraft-linux. While remaining in the same test world, its script marker was changed from A to B and native `/reload` executed. The content log recorded A at 14:09:09 and B at 14:10:16 (UTC+08, 2026-10-03), and B appeared in game chat. The temporary pack was removed from the world after normal save/quit; canonical addon bytes were not altered by that experiment.

This establishes script reload in the current client. It does not establish texture, model or animation hot reload, native 24-tick timing, or full Java visual parity. The client observations before this repair used the preceding 2.8.53 candidate.

## Remaining work

Actual short-release timing, full eating/shaker sequences, cooked-secret snapshot timing, failed-skewer original model preservation and logout settlement remain separate acceptance or implementation work. No live deployment or release publication is part of this document.

The corresponding screenshot is retained in the private test environment; it is not part of this public source report.
