# G2.8.114 bottle RawMessage ownership and verified readback

Based on canonical G113 a33e4b94fd7d055454bfb25aec12d806abf70e7c. Retains
its Creative-consuming seasoning, quiet fifth bottle, original rejection keys,
translated warning outlet and all earlier pending completion/audio/count repairs.
Reintegrates the exact already-tested G109/PR172 pose assets and generator; no
new pose tuning. G111, G112 and G113 remain distinct frozen identities.

## Real-client failure and evidence limits

The disposable G112 clone's existing real eight-ingredient PENDING bottle kept
its old 3/8 count. Normal placement then empty-hand pickup raised `Bottle
ingredient lore write rejected`; the transaction did not finish. Cold forensic
comparison found the same complete item in native station storage, unchanged
except inventory slot, with no duplicate physical bottle. Saved lore consists
of JSON strings containing singleton rawtext-wrapped translation nodes, with
string-array arguments. Saved encoding is not proof of live getRawLore shape.
No native script console/probe existed; none was injected or assumed available.

Microsoft's RawText contract documents RawMessage serialization under rawtext.
RawMessage/getRawLore also permit string-to-text conversion and alternate plain
translation arguments. G112/G113 incorrectly compared raw JSON text and only
recognized top-level translate keys, making documented serialization both a
false write failure and a stale-owned-line duplication risk.

Sources:
- https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/rawtext?view=minecraft-bedrock-stable
- https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/itemstack?view=minecraft-bedrock-stable
- https://learn.microsoft.com/en-us/minecraft/creator/reference/content/rawmessagejson?view=minecraft-bedrock-stable

## Bounded repair

A bottle-specific pure helper recognizes only singleton sole-key rawtext wrappers
around text or translation nodes, known fields, and documented plain-string
translation argument representations. It ignores object key order, preserves
argument and line order, and keeps unknown/mixed messages structurally intact.
Only exact owned ingredient/ready/missing-base nodes are replaced. A mixed line
containing custom text and an owned translation is retained unchanged.

Readback remains mandatory: missing/changed lines, count/translation/argument
changes and unrelated custom loss reject the prepared clone. Exposed property
readback additionally detects loss of content-addressed metadata tokens. Native
storage/hand/projection transactions are unchanged. Diagnostic errors include
only mismatch index and owned/rawtext/type labels, never custom text, metadata
values or hidden tokens. No general metadata migration, polling, inventory sweep,
semantic kind changes or synthetic ingredient reconstruction is introduced.

Six production-helper tests using actual itemData plus SDK-shaped key ordering,
wrappers and argument objects all fail against the original G113 helper. The
new helper passes those and negative silent-reject/throw/wrong-count/custom-loss/
token-loss checks. Complete production hand/storage and helper suites total229
passing cases, including wrapped old count replacement without duplicates,
custom mixed preservation, transactional failure and replacement/reload. These
are API-double contract tests, not live getter or rendered-client evidence.

## Identity and acceptance

Fresh package/module/pair2.8.114 and guide0.3.44. Exact pose SHA256 values:
- a286_held.animation.json: 7efa0944bb50d874c2b294130487c68ea2f68e55a683dc8fb78961eeb518d644
- seasoning_held.animation.json: 2dd6a636e1c56709437557dd3fd2c5ab4c48b0048e279c7f23b0dbb24be20450

Draft only; no merge, Release, native installation or live deployment here.
Full canonical CI/Dash equality and source packaging remain independently gated.
First native gate on a separately approved failed-world clone: retained real
failure bottle pickup shows8/8 and exactly one ready line; replacement/pickup;
then shake; then normal save/restart and item/order/count verification. If still
rejected, collect only the structural diagnostic, stop, and cold-save evidence.
Full-family/Cookery-author-tracking/parity limitations remain open.
client=false; production_ready=false.
