# A2.8.25: core skewer safety

Rebuilt from verified public 2.8.21 after the temporary cloud workspace containing unpublished QA candidates 2.8.22–24 became unavailable. No candidate is claimed to have been published. This version is independently retested.

- Craft one stick into an empty unfinished skewer, equip offhand, use ingredients on a block. Empty starters can be sneak-disassembled to a stick. No vanilla item override or metadata-blind reverse crafting recipe.
- Advancing one skewer retains remaining native offhand items. A full inventory rejects threading/disassembly and restores inputs instead of gambling on an unacknowledged drop.
- Exact-slot extraction, charcoal conversion and destruction use rollback plans. Unknown drop/rollback outcomes quarantine station storage; no automatic unsafe retry.
- Native complete-use owns full eating. Animation timers never debit food. Deferred partial-stop handling matches item identity, pins the session, and protects newly started identical sessions. Natural heat expiry is accepted without permitting changed ingredient/seasoning metadata; hot benefits expire at commit.

Verification distinguishes actual-runtime function tests with storage/event doubles, isolated BDS loading/native persistence, and real client interaction. No simulated Minecraft players. Synchronous rollback is not crash atomicity. Client input/event ordering, protection integration and live saved-world migration remain unverified.

Beef chunks and chicken skin still lack exact Java public-host acquisition. The other 18 fixed ingredient chains have source-backed acquisition; that is not a claim of a complete survival playthrough. Secret-skewer models/full arbitrary ingredient metadata and optional integrations are outside this repair. No live deployment.

Reconstructed focused suite: 33 actual-function storage/event tests passed. Full source gate and BDS results are recorded separately; earlier lost-workspace evidence is not substituted for this version.

Final isolated BDS 1.26.52.3 / BSM 3.10.6 verification passed in four-pack Grilling+Cookery scope: two exact-load cycles without script errors, and a separate test-only native probe saved three full ItemStacks and a two-flip state, restarted the actual process, completed four flips, produced cooked outputs with metadata/heat/seasonings, and committed charcoal output/reset. No experimental creator features or simulated players. See BDS-CORE-SKEWER-20261002.json. This is not a full-family or client acceptance result.
