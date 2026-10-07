# Bounded G83 native plate result

Exact public source `69bfc1b97531679e10ed7d225992a1c5985e0a14`; archive SHA256 `750bd04ec0a9209eb73b4adcf2a91c47782e35aa6c48bc49e3b7025bda4619d9`; actual Bedrock `1.26.52.3`.

## Observed pass scope

- One preserved three-ingredient plate shows full shaft and brown/yellow/orange-green ingredients immediately after placement
- Empty-hand retrieval clears display and returns held skewer
- Reinsert restores display
- Save/quit/reload retains visible food and data

## Open boundaries

- Fresh placement shaft initially diagonal then settles straight at identical camera after13seconds; not a saved-data pose-loss finding
- Consumption repeatedly reaches debit_ok then reward_begin and commit_failed; inventory/hunger rolled back; precise reward throw remains unknown
- No all-count/all-facing, full Java, touch or audio acceptance

The transient yaw observation was repeated at the same camera with no input or reload between fresh placement and the settled view. This is not proof of lost saved block facing. The G84 body component is a source-backed candidate response; its native result is still pending.

The opt-in consumption trace establishes valid event/current rows, accepted identity, completed reconstruction and successful debit before reward failure. Ownership and hunger were restored. It does not identify the failing numeric getter/setter or justify a guessed nutrition repair. The next diagnostic must identify that substage with sanitized error categories.

The native client exited normally on 2026-10-07 at03:47:51UTC. The occupied plate remained1/5, with empty offhand and unchanged hunger10/20. Diagnostic opt-in absence was checked at03:40:35UTC. These are bounded observations; no full-family migration, complete Java, all counts/facings, touch, audio or general client acceptance is claimed.

## Screenshot integrity

- `g83_plate_diag_disabled.jpg`: `68515efbebc9714c252d229c4fee32842b903ee28d00ad042ce2847fabaa981a`
- `g83_plate_diag_history.jpg`: `53e59acdb895f85d8c66bb2ad1e57612cc0d92b8cb24c4ef23dee53addd4eb83`
- `g83_plate_diag_use.jpg`: `5d1165701eea67de17d39acc9e71a1190596400420e678ddcdb61403e3acd025`
- `g83_plate_first.jpg`: `89cb6d229e4f5e9724dde06d4b10c540449094a81484230c515d93054bd9287b`
- `g83_plate_reinsert.jpg`: `e9d9f4d80732f760bf279613953ef52c7f3688fce931fdffd1443c7200b63806`
- `g83_plate_reload_fixed.jpg`: `1c24cbf906deed2daeccba63569d4096e9bcea75e7179e53414a808ee851d8b9`
- `g83_plate_retrieve.jpg`: `a7e405e642c35bcd8a60f7c5e90ac6574782d8bd19f962c476c63ed0aaf4a7e9`
- `g83_plate_yaw_fresh.jpg`: `3bd03a686fde3cd760a8063d5f8490d3754a9ce4af2d743f3ddde90337372523`
- `g83_plate_yaw_settled.jpg`: `5c6620a7c8cf8a7d3b43c6fbc6d9807f046a6dda0c1180d96222e2e2ddee243f`

Images, native logs, player records, worlds, private receipt paths and author Cookery archives are not published. Keep `client=false`, `production_ready=false`, `pending_client_acceptance`.
