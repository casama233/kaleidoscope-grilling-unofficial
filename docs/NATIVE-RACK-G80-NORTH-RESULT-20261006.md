# G80 native rack checkpoint: north-facing bounded pass

Observed in Bedrock 1.26.52.3 x86_64 with Cookery 1.6.0, 2026-10-06 20:21:43–20:27:21 UTC. This records actual client observations, not a simulated renderer or source-test inference.

- Tested runtime source: `9c1ac4a54c3c6b92be75f8bcd9a00d6569f6c2ac` ([draft PR142](https://github.com/casama233/kaleidoscope-grilling-unofficial/pull/142))
- Version: `2.8.80`
- Archive SHA256: `315790e7b3882b36bac1b7e757d60a3e5d1bb29d223cf016bb2c3caf28ac98bd`

## Passed within the north-facing rack

1. Outer saved slot4 accepted insertion on the left and displayed on the left. Pickup removed that same jar
2. Outer saved slot0 accepted insertion on the right and displayed on the right; the center remained unchanged
3. Ordinary insertions made all five upper positions visible at the same time
4. Removing inner slot1 left a stable gap; the other four jar positions did not move. Reinsertion restored the gap
5. Save/quit and world reload retained all five upper jars and the four lower tools

## Screenshot identities

All four local screenshots were inspected and their byte counts/SHA256 verified before recording this checkpoint. Screenshot names identify the retained evidence; the images themselves, private world files and machine-specific paths are not published here.

- `g80_jar_left_correct.jpg` — 106596 bytes; SHA256 `6c6c0f0d0c394deb94bab57d56b866f9ce02e090d67ae5174c1a5bdd4baf0b7b`
- `g80_jar_right_correct.jpg` — 106834 bytes; SHA256 `daae9971782559261ee8e834e7759d0c95dd9a36fce53ed4ffd91dbe9f31a2d1`
- `g80_jar_gap_correct.jpg` — 116903 bytes; SHA256 `3f74bfb48ac13b6e44e724a706837c95e7b8ef047cf9cc1c32e0fafdfe3c228b`
- `g80_five_jars_reload.jpg` — 114364 bytes; SHA256 `4531dd33aa3a110005b9e8e695a303984931919a6760bd8a77925769081626a1`

## Limits and unchanged gates

East, south and west client-facing behavior and touch controls were not tested in this checkpoint. Full Java visual parity and individual contained-ingredient rendering are not accepted; jars currently share an appearance. This bounded north-facing pass does not set global client acceptance or production readiness.

This evidence-only change leaves runtime bytes, version, baseline/release history and the exact tested archive unchanged. BSM verification remains required before merge, Release publication or live deployment. No such action is included.

## Cardinal addendum: outer left/right cells

Additional actual client session: 2026-10-06 20:29:03–20:38:26 UTC, using the same G80 runtime source, archive and Cookery 1.6.0 listed above.

East, west and south racks were physically placed on corresponding stone faces. On each facing, ordinary empty-bottle insertion into the outer left and outer right slot displayed the jar on the clicked side. Empty-hand pickup removed that same visible jar and returned the bottle. No form UI appeared. All six tested outer slots were recovered empty afterward; the client and launcher were closed at the end.

Together with the earlier north session, outer left/right insertion, display and pickup have bounded actual-client coverage in all four cardinal facings. The north-only five-jar simultaneous occupancy, inner slot1 gap/reinsertion and save/reload observations are not extended to east/west/south. Inner slots on those three facings were not separately tested. Touch, full Java visual parity and individual contained-ingredient appearance remain unaccepted. Private world paths, absolute positions, player identity and unrelated observations are omitted.

Six additional screenshots were inspected and their bytes/SHA256 verified:

- `g80_east_left.jpg` — 105304 bytes; SHA256 `7fce3381432a48d752f12b1ef85284474fb260755e4bd9557d0458443a1b50f3`
- `g80_east_right.jpg` — 105559 bytes; SHA256 `9e1a72ee15f0f0407896990c153a5ea60213cb8f86a1e46b86f78d1b16ef9dba`
- `g80_west_left.jpg` — 102546 bytes; SHA256 `076d46f0e7513d296efd50f15b5a7d06f03c2e81bde51822c1e19f28656f046d`
- `g80_west_right.jpg` — 103395 bytes; SHA256 `25ae7237790d7ada0446e8ceb40ebeb804c5fb2d206c3efbe9e47af2c0e0415c`
- `g80_south_left.jpg` — 107204 bytes; SHA256 `7c9f91d4e7339916603e9d1f5786611abe1abc5c5bb09bbf133c487a22d07ea2`
- `g80_south_right.jpg` — 107716 bytes; SHA256 `457df80a71794159a41692c5f01512ebc6a1f765a72bf5a7706378e5c3234f48`

This addendum is documentation only: runtime identity, all exported bytes, version and tested archive remain unchanged. BSM/merge/Release/live gates remain pending; no such action is included.
