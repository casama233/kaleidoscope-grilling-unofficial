# G90 current-main and held-plate candidate

Fresh 2.8.90 consolidates current main `fe99c0ca3d25ffe5140ed699e89a470ee6abbc63` (merged PR151 oil ownership, living/projectile damage attribution and Cloud feedback) with the exact [G89 placed repair](STATUS-A2.8.89.md). Existing Cookery palettes, food settlement, placement/insertion guards, helper cleanup and authored poses are retained. G89's [bounded graphics observations](NATIVE-PLATE-G89-BOUNDED-20261007.md) remain evidence for G89; this new source needs its own client checks.

## Held contents

A derived per-hand renderer projects saved plate rows without modifying the held ItemStack, metadata or plate storage. It reuses the eight existing bottle channels per hand, with disjoint owner markers and float32-safe packed values; the same 32 player properties remain, and only 16 integer ranges widen. There is no resource-pack player override or arm hiding. Existing bottle content plans remain unchanged and both hands are independently guarded.

The candidate includes source-derived raw/cooked meshes, three independently colored secret segments and the full ordinary mesh. Failed-family defaults remain bounded bare shafts; retained nondefault failure variants and missing historical source provenance remain unsupported. Dynamic GUI contents are still open.

Unchanged held snapshots reuse input plans. A semantic held-registry revision invalidates secret palette caches after meaningful registration/reset/restore. All shared input-read failures invalidate both projected owners, including an opposite-hand bottle read failure. Rejected owner writes try independent pair-word sentinels; complete setter refusal is reported and retries recover when writable. Output signatures are cleared before writes, so partial failures and reverting to the prior item cannot suppress recovery.

## Source identities and gates

Two independently published 2.8.83/84 lines have different bytes. Current-main entries remain canonical in `release-history.json`; [the explicit lineage ledger](../tools/fixtures/g90-source-lineages.json) preserves both exact histories and source hashes. Conflicting main verifier/delta/status files are retained as immutable snapshots, and historical plate comparisons use their exact source lineage. Current BP/RP bytes require full-tree conservation against both public inputs plus the reviewed held delta, with no blanket changed-path exclusions.

Required source/export CI, new native held views/counts/hand coexistence and recovery checks must be recorded for this exact candidate. The required BSM upstream-status evidence remains unavailable; family/BDS/saved-world/production gates are separate. Keep `client=false`, `production_ready=false`, `pending_client_acceptance`; no merge, release or live deployment is authorized for this review candidate.

Expanded G89 evidence is on the [owner-access personal Space Page](https://chatgpt.com/space/page_ed507605a220819186f21060f874f5ae). Public readers may not have access. Essential source identities/results are retained in Git; no new large screenshots or redundant full reports are added.
