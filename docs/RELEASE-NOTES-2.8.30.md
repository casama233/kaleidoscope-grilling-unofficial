# Grilling 2.8.30 — fixed recipe tags and held-model regression guards

Fixed Skewer Recipe Books now accept the same public ingredient tags as manual threading and Java selectors. Nine fixed recipes gain tag substitutes; all 20 canonical recipes retain their explicit item alternatives. Live inventory tags reach the planner. Duplicate counts, selected-slot exclusion and transactional rollback are preserved. Secret recorded recipes intentionally remain exact-ID matching; malformed tag selectors in custom records are refused.

The held-render audit now rejects missing/duplicate/wrong view dispatch, swapped animation aliases, missing animation targets and broken rack/skewer pivot hierarchies. It also traverses native block-item geometry/material/texture chains for grill, oil press and big vat. These are stronger checks; no current rack geometry or hand transform was changed merely because previous validation was incomplete.

Official Blockbench 5.2.1 desktop opened the canonical advanced-rack geometry and texture. Its imported rack_fp_right and rack_tp_right were inspected with the built-in first-/third-person item reference and centered first-person camera. The textured rack remains visible and attached at the reference hand in these editor views. This is not Minecraft rendering, eating-animation, alternate-skin, touch, or live-world acceptance. Existing 922 geometry source hashes are unchanged from the previous editor audit.

Dynamic per-ingredient secret-skewer appearance, public Cookery beef/chicken-skin acquisition cooperation, native client input/animation acceptance and full saved-world migration remain open. No live deployment is included.

This release preserves concurrent upstream 2.8.28 audio/localized-lore/shared-guide work and 2.8.29 native grill-content display. Third-person skewers now use the complete authored Java translation instead of the former zero-position palm-centre exception. Both hands and all 150 bite-stage geometries pass source-frame corner equivalence; native eating-to-mouth trajectory remains unverified.
