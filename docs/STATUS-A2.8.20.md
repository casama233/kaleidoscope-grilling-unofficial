# A2.8.20 — advanced-rack transfer and public-tag repair

Parent-authored canonical changes; Java released 1.1.1 is the behavior reference. This release is not full Java parity or a live deployment receipt.

## Fixed

- Normal deposit, partial withdrawal, hotbar swap and bulk return now snapshot and plan all touched native slots before mutation. Exact ItemStack clones preserve name, lore and supported native metadata without serialization.
- Filter persistence belongs to the same synchronous rollback transaction. A failed write restores the exact previous raw property, including its absence.
- Hotbar return retains Java ordering: remembered nearby rack, a matching filtered local slot, then inventory excluding the selected slot. Insufficient room makes no changes. Cross-rack rollback covers both racks.
- Withdrawal no longer calls inventory.addItem, whose partial writes cannot be rolled back without recording each affected slot.
- Automation borrow/return reports success only after commits succeed. Ambiguous rollback quarantines the affected racks and throws a recovery-required error instead of handing back a speculative full remainder.
- Persistent transaction-fault property plus in-memory gate prevents automatic reuse after incomplete rollback. If all persistent-property writes fail, only the in-memory guard can be guaranteed until restart.
- Public advanced_rack_seasonings and advanced_rack_tools tags are checked independently per slot. Dual-tag items work in both groups while existing Cookery knife/shovel tags and built-in categories remain supported.
- Malformed stored filter data fails before item transfer rather than being treated as an empty filter.

## Validation

24 focused tests load actual production function bodies with storage doubles. They cover post-write exceptions, earlier merges followed by rejection, exact filter rollback, partial/full inventories, cross-rack returns, automation failures, metadata clones, dual tags and quarantine. No simulated players or native client acceptance is implied. The complete 2.8.19/2.8.18 baseline remains required by verify_current.py; current native/BDS and release CI results are separate evidence.

## Still open

- Generic remembered filters retain item ID/category, not Java's complete component-sensitive filter stack. This repair does not claim that renamed generic items exactly match Java after a slot empties.
- Native inventory operations are synchronous best-effort transactions, not crash-safe database commits. Quarantined items require explicit diagnosis and reconciliation; do not clear the fault marker blindly.
- Finished seasoning placement/pickup metadata, generic destruction/support-loss lifecycle, other host integration gaps and exact native client hand/eating appearance remain separate work.
- All held-frame geometry, textures, UVs and eating assets are unchanged from the reviewed 2.8.18/2.8.19 baseline.

### Maintainer constraints and additional parity limits

Each transaction may contain at most one independently prepared insertion plan per rack. Current swap paths meet this condition and bulk deposits commit sequentially. Future batched callers must coalesce the rack filter snapshot instead of concatenating independent plans that each create a filter.

Native isStackableWith is used for safe item merging; identical nonstackable tools can take the swap/fallback route where Java's same-item/components check treats them alike. Partial withdrawal preserves item counts but currently scans inventory slots 0–35 instead of Java's reverse menu destination order. These are disclosed remaining interaction differences.
