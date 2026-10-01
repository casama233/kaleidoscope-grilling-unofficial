# A2.8.18 — native Blockbench held-frame audit

Native Blockbench 5.2.1 exposed a real gap that JSON/anchor checks missed: copying
Java display Euler angles directly into Bedrock attachment animations does not
preserve the displayed pose. The old skewer pointed into the arm in the editor's
third-person reference; its first-person model was outside the viewport.

- Convert Java XYZ display rotation through the item reference frame into
  Bedrock ZYX bone channels. Keep skewer handle anchoring and every geometry,
  texture, bite stage and native eating component unchanged.
- Convert all four view/slot poses in the shared skewer, bottle and rack families
  (107 attachables). Bottle and rack translations account for their actual model
  origins. Rack first-person placement has an explicit Bedrock viewport offset;
  rack left-hand placement is a mirrored fallback, not a Java-authored slot.
- Replace obsolete A2.7.63/64 render-audit assumptions with current 107-item,
  150-skewer-stage and single-binding contracts. Direct animation of a bound
  bottle root is supported; it is informational, not automatically a defect.
- Add reproducible frame/viewport regressions and a read-only native Blockbench
  codec/Validator/preview tool. See [evidence and limits](render-audit/20261001/README.md).

This is an editor-validated repair, not completed Minecraft client acceptance.
Actual offhand, eating-to-mouth alignment, skin/FOV/mobile behavior, multipass
transparency and saved-world migration remain separate checks. No player.json
replacement, private packaging patch, live overwrite or installer attachment.
