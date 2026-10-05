# Bounded native completion verification, private 6716

The targeted main-hand no-return completion check passed in the actual client
for runtime source `259596af5d15ec79f114adecc1c6dc676d2e2738`, private 2.8.6716.

## Single-serving Survival completion

- Minecraft 1.26.52.3, Zuri skin, first person, FOV60, upright standing view
- Isolated Grilling + Cookery world, from the same unconsumed saved baseline
- One existing cooked Apple/Carrot/Beef Secret Skewer, main hand, 5,500 ms use
- Completed one serving, ended with empty hand, and effect icons appeared
- Two independent reviewers found no complete three-piece return at completion
- Dense review covered every source frame 300–413, PTS 5.000–6.883 seconds
- Original source frame 352 at PTS 5.867 seconds was empty; this exact frame
  position showed the one-frame return in the previous 6715 recording
- The session's flushed client log contained zero error lines after normal
  close at 2026-10-05 04:47:38 UTC

## Retained Creative visibility and reset

A separate longer run passed the bounded retained-item visual recovery check
using the same 6716 runtime in an isolated Grilling + Cookery world. The client
was in Creative, with the Kai skin, first-person main hand and natural rain.
The operator made two 12,000 ms held right-click inputs without changing the
selected slot. Continued holds may contain additional automatic restarts;
input-call count is not asserted to equal completed-serving count.

- Every source frame in PTS 5.750–6.500 s (frames 345–390) and
  17.500–18.500 s (frames 1049–1109) was reviewed at 60 fps
- No-food terminal views were followed by a restored complete three-piece
  model, fresh active use and new progressive ingredient removal
- Full retained food returned by frame 355 / 5.917 s and frame 1072 / 17.883 s;
  fresh active views appeared by frame 365 / 6.083 s and frame 1081 / 18.033 s
- Subsequent removal was visible at 19.000 s, with only the red piece remaining
  at 21.500 s and bare shaft again at 22.000 s
- Sampled 27.000–35.000 s views showed a stable, available full idle model;
  no item stranded in terminal-hidden state was observed
- Root's visual review agreed. The flushed client log had 53 lines and zero
  error lines after normal close at 2026-10-05 06:14:25 UTC

The earlier separate Creative recording with two 5,500 ms inputs remains
inconclusive: it did not establish completed terminal traversal followed by
fresh progressive use. The longer result does not retroactively change that
recording's conclusion. Query/latch values were not instrumented, so these are
bounded observed visibility/reset results rather than a universal protocol
proof or a direct before/after item-metadata comparison.

## Evidence identity

- Single-serving Survival clip SHA256:
  `5dfb26374982dcb85aca5eee02459e63c1aea60629b98a9f125fe0c1c0d71bb9`
- Earlier inconclusive Creative clip SHA256:
  `5cb34ad0ce107eb6247eb89fe6a7ad9ed6e83ea8275f66e7bb2ab3fb8b3d51d5`
- Longer bounded Creative clip SHA256:
  `8adadaf05785c43221557cfdefebca2910fb1c3c74f09f87f991d1b67990a210`
- Candidate archive SHA256:
  `8ac1cefe27a7c9afae8ec0cfafd9735fdf72fa2d5822c371cd0c33a320fd3165`
- Original candidate receipt SHA256:
  `2e9ade5522a15457a7d7500da126cc7dbeabc1810353ad5991dc4279e1780203`

Evidence media, world backups and machine logs remain outside this repository.
This documentation-only commit does not change exported runtime, the frozen
candidate, its original receipt or prior private candidates.

## Acceptance boundary

This verifies the targeted main-hand cooked THREE Survival completion return
and the separately observed retained-Creative visibility/reset under the listed
conditions. It does not certify exact serving/completion counts, Survival
retained-stack repeat or replacement, offhand/ALT, other skins/postures/FOVs
beyond these runs, helper scale/appearance, exact Java pixels or particle
fidelity, multiplayer/network variations, full-family loading, saved-world
migration, or production readiness. Those source regressions and broader client
checks remain separate evidence. No merge, release or live deployment is
established by this verification.
