# G85 native plate nutrition and spawn-yaw candidate

Based on exact G84 public source `7eef713cbc2cf1089c7bac6f99c29674e10525b4`, archive SHA256 `22eb8c73d044a96fdec7a825e84e631a0584f4ae727437097366331c1885b7cc`. G83/G84 stay frozen. No merge, release or live deployment is authorized in this task.

## Proven native nutrition failure

Actual Bedrock1.26.52.3 G84 trace accepted occupied plate rows, session identity and reconstruction. Debit succeeded. Hunger10/max20 updated to13 successfully. The saturation component snapshot reported current10/effectiveMax10; the attempted target12.353846153846154 threw `ArgumentOutOfBoundsError` at `saturation_write`. The existing transaction restored the occupied plate and hunger. This identifies the concrete failing operation; it is not a hypothesis about float equality, recipe decoding or failed native activation.

The canonical nutrition function now reacquires the current saturation component after the hunger write. It keeps the existing gain calculation and sets no higher than the updated hunger, the current component's authoritative effectiveMax, or current saturation plus gain. It does not set/guess an attribute maximum, invent20 as a universal cap, round away fractional gain, change component APIs or skip transaction rollback. An unavailable/throwing refreshed component still fails the existing transaction rather than granting only part of a serving.

A native-like effectiveMax10 regression now completes legally at10; a fresh max13 view retains the expected fractional gain. Tests also cover canonical and both actual native secret aliases, refresh/read/set failures, ownership/nutrition rollback and the exact G84 counterfactual. These API doubles verify the repair/transaction contract, not actual native G85 consumption or complete Java saturation parity. The exact G85 native target/readback and consumed plate still need confirmation.

## Plate helper spawn yaw

G84's body-follows-head candidate stopped the13-second settling but showed a stable diagonal shaft in one matched-camera/count1 case. A read-only native `rym/ry` selector confirmed actor yaw−90 while the rendered shaft remained diagonal. G84 body orientation is therefore not accepted as Java parity.

The plate-only helper now supplies [`SpawnEntityOptions.initialRotation`](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/spawnentityoptions?view=minecraft-bedrock-stable) at creation, using the same already computed facing plus authored slot yaw that is passed to teleport. This supported member was released in server2.3; the pack uses server2.9. There is no guessed angular correction, axis quantization, model alteration, global helper change or polling loop. Original3–5-skewer diagonal slots are preserved. Existing body-follows-head stays; native fresh/settled comparison must confirm the combined helper setup before claiming the yaw issue repaired.

The plain/alternate secret-food normalization, full original source meshes/palettes, count layouts, display cleanup and post-commit placement queue remain. Grill/rack source and plate storage metadata/ownership are unchanged. G83's [bounded visibility/retrieval/reinsert/reload evidence](NATIVE-PLATE-G83-BOUNDED-20261007.md) remains its own result and is not borrowed as G85 acceptance.

## Gates and privacy

Focused source/diagnostic/rollback/spawn-yaw tests, exact original witness deltas, syntax and generator checks pass. Fresh2.8.85 identity/hash freeze, public source/package identity, final exact-head canonical/compiled CI and native G85 tests are checked separately. The isolated native clone may be tested in parallel with canonical CI after source/package/focused checks; this does not authorize merge/release/live or waive CI.

Required BSM freshness/family/live gates remain open. Keep `client=false`, `production_ready=false`, `pending_client_acceptance`. Opt-in diagnostic limits and lazy sanitized categories remain; remove the QA tag after the bounded trial. Native logs, screenshots, worlds, player records, private machine paths and author Cookery archives are not published.

## Bounded G84 screenshot integrity

- `g84_plate_yaw_fresh.jpg`: `e21495cf26ed06987acc8a2883d03e311239062ab31658a124ff2a326ffec00b`
- `g84_plate_yaw_settled.jpg`: `fdb8d65e1f5afef9063ab79fec08f3cf3d830f2c64a9af958ab08bd55b6f1cb8`
- `g84_actor_yaw_probe.jpg`: `17b96cfa79c6d62ece8bc4443f0d847196382d6484a4e018963a193f1db6aa19`

The G84 native client was closed normally at04:26:54UTC with the occupied plate and rollback sample preserved. The QA opt-in tag was checked absent at04:20:38UTC. These bounded source/receipt observations remain separate from the new G85 native result.
- `g84_plate_reward_trace.jpg`: `3b765755589dc77352cdd84e482850655d7720c608911ca25f3b816678c66536`
- `g84_qa_disabled.jpg`: `f9e08febfec013d152469495a58186a0ce54572d2c1a7029933d09f1b3b5eff4`
