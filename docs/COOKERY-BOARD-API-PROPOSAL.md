# Cookery chopping-board acquisition API proposal

Status: draft, not sent. Prepared 2026-10-02 for verified author Bedrock Cookery 1.0.8. This document describes requested capabilities; none of the proposed fields are supported by the current host. Grilling AGENTS.md permits upstream reads and prohibits upstream writes, so no maintainer issue/message has been posted.

## Reproduction without modifying the author pack

Use the original author archive (SHA256 `9e5b617cc4c7a08ecd429fb9e42ec10e8d40a1ed5fc1f6f6687c3aff8a45a5d5`), unpack its BP privately, then run:

```sh
node development/integration/reproduce_cookery_acquisition.mjs /path/to/verified-author-BP /tmp/acquisition-report.json
```

The harness checks source hashes before running actual host function bodies. It uses storage-operation doubles, not native players or client acceptance. The separately identified BDS overlay verifies the actual public registration API, not board use.

1. Register `minecraft:beef` → Grilling `beef_chunks`, count 2, cuts 4 through `registerExtensionRecipe`.
2. The registration is accepted. Loading raw beef on a board nevertheless chooses the built-in cow-offal recipe and ultimately yields cow offal ×2.
3. Adding speculative `priority`/`override` fields does not change this: normalization discards them.
4. Register a raw-chicken board recipe with primary cut meat plus proposed skin bonus. The registration is accepted, but `bonusOutputs` is discarded. Actual board use yields only the primary cut meat.
5. Four knife actions increment cuts and damage the knife; the following knife action releases output. Observe this release boundary in all completion tests.
6. Inject an unacknowledged payout through the storage harness: the board clears with no main output. Therefore clearing state cannot authorize an addon bonus reward.

This is a request for explicit extension behavior, not a request to replace private station files. The existing tool-transform API is usable but has a single fixed output and one tool action; it cannot express faithful multi-output four-cut chicken processing.

## Required behavior

- A host-approved way to replace the named built-in beef recipe while keeping four cuts and yielding two beef chunks. Conflicting overrides must return a clear rejection/selection receipt; addon load order must not silently pick a winner.
- A host-owned chicken completion output plan that preserves the primary recipe output and adds a uniformly sampled 1–3 skins. No skin on placement, intermediate cut, cancellation, break, explosion or failed output. Looting must not modify this cutting bonus.
- Output planning and acknowledgment belong to the host. A cross-pack script event is useful for observation but must not be an independently trusted authority that grants skins.
- Capability negotiation must positively confirm these features. Current `api: 1` plus `chopping_board` alone cannot authorize priority or secondary-output fields.

## Suggested contract and commit model

Proposed capability names (for discussion): `chopping_board_recipe_selection`, `chopping_board_multi_output`, `chopping_board_commit_receipt`. Exact field names/versioning should be chosen by the host maintainer. Unsupported fields should return explicit errors rather than a success response that silently removes the requested behavior.

At placement, persist the selected recipe/source/version and operation ID. Record the primary and bonus output plan; sample the bonus once when committing completion and persist that sample before any delivery. Reloading or retrying the same operation must reuse its plan. A later extension registration must not replace the recipe of an occupied board.

Completion must debit the input and deliver the recorded primary/bonus outputs as one host-controlled operation with verified storage acknowledgments. Restore debited items on a confirmed failure. If a world spawn may have succeeded before raising, retain a quarantined operation instead of blindly retrying and duplicating output. Persist a completion receipt after a verified commit; observer events can reference that receipt. A false/fake/late observer event must never grant new items.

Host unit tests and isolated BDS tests should cover:

| Case | Expected |
| --- | --- |
| Beef baseline and selected override | Unextended host unchanged; negotiated Grilling selection yields chunks ×2 |
| Chicken bonus random boundaries | Primary retained; 0 maps to 1, values below 1 map to 1–3 uniformly |
| Four cuts plus release | No premature output; four knife durability debits; one release commit |
| Repeated final action, restart or event replay | Exactly one recorded operation result |
| Cancel, break, explosion, player change | No uncommitted bonus; clearly defined input recovery |
| Full inventory or partial payout failure | No free bonus, no silent loss, no automatic duplicate retry |
| Registration conflict or missing capability | Clear rejection; no false success guide claim |
| Recipe update with a loaded board | Persisted operation retains its selected source and output plan |

Grilling's follow-up can remain declarative: register the beef selection and chicken bonus only after negotiated support, update the existing shared guide acquisition pages, bump all exported identities/hashes and run the complete family gates. This proposal does not install a host patch, approve a runtime override or certify clients.

## 2026-10-02 已實作的回饋候選

使用者明確要求擴充作者 API 並部署 live。A2.8.31 以自主編寫的通用 `host_api/board_api_core.js`、`board_api_runtime.js` 實作 `chopping_board_v2` 能力；`host-extensions/board-api.json` 僅描述原作者 hash 鎖定的介面插入點。新增 replace / supplement、嚴格 builtin 基線匹配、配方衝突拒絕與持久投放收據；不複製作者原始完整腳本。

可供作者採納的程式與介面均在本 canonical Git。這是公開回饋材料，尚未向作者傳送訊息或宣稱作者已採納。與普通 1.0.8 原包的既有缺陷重現見 acquisition reproduction；整套安裝須由家族收據登記，不能作為翻譯覆蓋。
