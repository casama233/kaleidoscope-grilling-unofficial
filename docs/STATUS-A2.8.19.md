# A2.8.19 — oil machine transaction and persistence repair

Source target: Java Grilling1.1.1 NeoForge1.21.1 JAR SHA256 `cf31071e4ba790bcd5c1d3f6005439bc512acba084e70b8ab6a767e8c8f99dd6`, [official project](https://www.curseforge.com/minecraft/mc-mods/kaleidoscope-grilling). Bucket semantics checked against its pinned official NeoForge21.1.228 FluidUtil/ItemHandlerHelper source, SHA256 `35d93ba9eb7dd11244e2efecf34c20205cb6084efea4138d0ee109cb2095bce7`.

## Repairs

- A stack of empty buckets retains count-1 in the original main/off hand; one filled bucket goes to an exact inventory slot or overflow drop. A single bucket is replaced normally.
- Creative extraction drains one vat bucket but neither replaces the hand nor creates an extra filled bucket, matching FluidUtil.
- Rejected Cookery oil-pot conversion leaves the hand, metadata and all vat oil untouched.
- Bucket/pot exchanges and press-to-vat completion use synchronous rollback. Press residue spawning is part of that transaction, so a rejected residue spawn restores the original batch/oil.
- A failed rollback marks the affected machines for recovery, persistently when the property store is available, and blocks automatic retry. This is **not** an atomic crash-safe database transaction. Total storage failure cannot provide a persisted recovery marker; explicit warnings remain.
- Active press registration uses one coordinate record per dynamic property, with resumable legacy-array migration; the silent256-entry cap is removed. Unloaded chunks retain their pending entries. Idle machines are removed from the active scan rather than polled forever.
- Completion at progress16 can retry after a recoverable write failure; interacting with a historically stranded completed press also retries it. Entries already discarded by an old release cannot be magically reconstructed from that old registry.
- Native `kaleidoscope_grilling:press_stones` item tags are accepted, preserving anvil precedence.

`development/gameplay_core/test_oil_transactions.mjs` exercises the actual production functions with storage doubles: stack counts, main/off hand, Creative, full inventory, partial writes, rejected pot builder, failed rollback, residue failure, unload/reload,300 registered machines and interrupted registry migration. No Minecraft players or simulated players are used. The full2.8.18 regression/held-frame baseline remains included in `verify_a2819.py`.

## Still open

Native pickup delay/rendering, abrupt-process-crash transactions, explosion/support lifecycle, arbitrary Java advanced-rack tag adapters, finished seasoning stack metadata and rack rollback require further work. The known Cookery receipt/optional-mod/platform gaps in STATUS-A2.8.15 remain explicit. All geometry/UV/material/held-frame assets are unchanged from2.8.18.

No live installation or world migration is authorized by a passing unit/static result. Deploy only a published Release with exact family receipt, client acceptance and verified saved-world compatibility. Public2.8.18 should not be newly deployed while its known oil-loss paths remain.
