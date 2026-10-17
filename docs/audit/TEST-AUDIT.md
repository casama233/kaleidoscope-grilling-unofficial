# Grilling Phase 0 test audit

Source: canonical `main` `6fc3ab711e90ae9f23739b18b1f28ef5f31bbf8a`, Grilling 2.8.114. Workspace was clean. This is a read-only static audit; no broad suite, BDS, client, mutation, runtime edit, test deletion or remote action was performed.

The current suite mixes useful production conservation/rollback regressions with source-text contracts, translated mathematics, API-operation doubles, asset self-comparisons and build integrity checks. These are different evidence levels. No current CI result in this audit certifies engine/client parity. The bounded original-Java bucket oracle was reproduced separately; Grilling runtime was not executed. Necessary source/release/pack/candidate/backup/deployment integrity gates remain required.

## Main findings

- `verify_current.py` selects `verify_a28114.py`; inheritance eventually reaches `verify_a2811.py`. Only selected older functions are called. For example, `verify_a283.assets/feedback` run as components; its historical `main` suite is not automatically current. Every active file/helper and each inactive current-tree test is inventoried in `TEST-INVENTORY.json`.
- Phase0 later reproduced the unchanged extracted original `FoodState.HEAT_BUCKET_TICKS`/`bucket` using `javac/java`; every fixture vector matched. This is a bounded runnable A oracle for nonnegative100-tick buckets. It did not execute the Grilling consumer/runtime or full Java JAR; repository-tracked generator and automatic CI oracle remain missing. See `java-oracle-check.json` and `java-oracle-output.txt` in this output directory.
- `tools/test_secret_food_palette.py` contains a real optional Java differential oracle using extracted pinned methods. `skipUnless` requires `KG_PINNED_SKEWER_PROVIDER` and Java; no active workflow sets the provider. Its default CI pass must not imply that Java oracle ran.
- Real BDS runners exist for fourth-flip restart, pepper natural generation/restart and profiling, plus native storage and host recipe probe scripts. They are manual isolated overlays, not current CI tests or a Phase 0 PASS. They do not simulate players. Profiling is measurement without a fixed regression budget.
- No actual D client acceptance was found in the test files. `native`/`java`/`render` names often mean mathematical or static source tests. They cannot certify first-person framing, animation feel, sound, particles or HUD appearance.
- Runtime conservation/rollback suites execute actual production functions/modules. Keep their independent B invariants, label API-double coverage as source-only, and split numerical/static/visual claims. Do not discard meaningful transaction protection merely because an adapter is synthetic.
- No general runtime mutation runner or brief-required A/B/C mutation annotations were found. Existing damaged-input/fixture cases and retained old subscribers demonstrate narrower detector sensitivity. Nothing was mutated in Phase 0.

## Inventory and decisions

Counts below describe inventory size only; they are not progress, parity or acceptance metrics.

| Inventory | Files |
|---|---:|
| current_ci_test_files_or_helpers | 128 |
| current_ci_pure_checks | 1 |
| current_ci_verifier_check_files | 75 |
| conditional_legacy_files | 11 |
| manual_bds_files | 8 |
| nonexecuted_current_tree_files | 246 |
| archived_history_test_files | 8 |

JSON contains classification, activation, reached functions, player-visible behavior, actual source/fixture/assertion excerpts, limitations and mutation status for every inventoried file. `current_ci` means statically reached by enabled CI commands, not observed execution in this audit; helper-only rows say so explicitly. Historical workflow roots and archived nonexecuted files are separated.

## Actionable consolidation/removal candidates

- **split-gates**: Keep canonical boundary integrity gates; remove their output from A–D gameplay/visual acceptance summaries. Separate verifier orchestration, BUILD_INTEGRITY, B source invariants and explicit A/C/D evidence in one current test manifest.
- **golden-oracles**: Check in a reviewable generator for the declared executed heat bucket vectors and make optional palette Java differential mandatory only for relevant logic changes after reviewing the maintained author branch. Store input→output vectors with source method identity, not hash-as-truth.
- **transactions**: Retain actual production rollback/conservation/idempotence cases, extract them from large mixed VM suites, add bounded generated operation sequences, and record one targeted broken-implementation check per new A/B/C case. API doubles remain source B diagnostics, never C.
- **visual-math**: Remove computed frustum/matrix/UV/asset-rebuild equality from visual functional acceptance. Preserve independent geometry invariants/provenance as build diagnostics; replace visual acceptance with fixed real Java/Bedrock client capture matrix.
- **self-comparison**: Within mixed tests, delete/replace formula-mirroring and output-vs-same-generator expected assertions after an independent oracle exists; specifically GUI front-slot pixel expectations reuse gui.mask_tone/ingredient_color, palette atlas expectations reuse palette.color_at, and HUD width loop reuses a translated formula. Keep corresponding source provenance once at the input boundary.
- **historical-chain**: Consolidate current inherited calls into a feature/test manifest without running all old verifier mains. Preserve historical code and evidence; obsolete revision count/report assertions are removal candidates from functional acceptance, not a mandate to rewrite old receipts.
- **C-scene-gap**: Reuse exact-candidate successful real BDS evidence when present; bind manual native probes to reviewed candidate and add actual chunk unload/reload/restart/concurrent-owner scenarios only where behavior lacks evidence. Performance profiler currently measures; it needs an agreed regression budget before it becomes a pass/fail performance test. No simulated players.
- **D-missing**: Require real human client capture/recording for visible models, both hands, animation, audio, particles and HUD; test filenames containing native/java/render cannot substitute for D.

No files were deleted. Removal means removal from functional acceptance reporting unless a later reviewed change explicitly retires an obsolete assertion. Keep integrity at meaningful state boundaries and preserve historical evidence.

## Concrete current-chain examples

- `test_hot_food_manual_merge.mjs`: `verify_a2812.main → verify_a287.parity_batch2_gate` (`verify_a287.py:246`) launches it, then `verify_a2828.py:36` launches it again in the same current inherited chain.
- `test_seasoning_native_storage.mjs`: `verify_a285.survival_gate` (`verify_a285.py:27`) launches it before `verify_a2861.py:13` repeats it. Keep the valuable B invariants; consolidate the invocation.
- `test_native_bottle_fp.py`: `verify_a2852.py:7` and `verify_a2861.py:14` run the same frustum unittest through different launchers. Neither invocation is D.
- `tools/build_eating_motion.py --check`: repeated at `verify_a2862.py:20` and `verify_a2867.py:16`. Consolidate unchanged generator checks; keep real source/export boundaries.
- `test_a283_feedback.mjs` is not duplicated merely because an old verifier lists it: current `verify_a2811` reaches `verify_a283.assets/feedback`, not `verify_a283.main`; the actual current explicit call is `verify_a2839.py:8`.

High-value B examples are reverse-order transactional rollback at `review/pure_checks.mjs:20`, full rack ownership restoration at `test_rack_transactions.mjs:66`, plate hand/property/block rollback at `test_plate_transactions.mjs:63`, and oil/bucket conservation at `test_oil_transactions.mjs:42`. These execute production code against independent state-preservation expectations. Storage/API-double boundaries still require C evidence for native semantics.

Unclear independent input/expectation sources are marked **待人工複核** in JSON. No assertion/file name alone authorizes deletion. Source-preservation, byte/regex/reference and generator checks are explicitly PRECONDITION/BUILD_INTEGRITY.


## 逐檔記錄與可信度

[TEST-INVENTORY.json](TEST-INVENTORY.json) 保留每個檔案的類別、觸發入口、所保護行為、bug種類、期望來源、限制和待複核標記。歷史未執行檔案分開列出。這是分類／重整清單，不是每個檔案已通過執行或人工逐行審完的聲明。沒有刪除測試，沒有用清單數量認證完成度。

本輪另確認既有未改動 Java `FoodState.bucket` oracle 可編譯、執行且與 heat fixture一致，詳見 [ORACLE-CHECK.json](ORACLE-CHECK.json)。範圍只有非負時間的100-tick桶；repo缺可重跑generator／普通CI不執行Java oracle的缺口仍在。
