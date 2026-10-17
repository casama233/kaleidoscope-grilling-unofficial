# 2.8.72 post-commit bottle visual cleanup candidate

This candidate follows G71 (`b59560e9a74e6d9bc950bc5061f51604a6b2e366`) and preserves its frozen release record, model, texture, icon and gameplay-data bytes.

After a successful bottle pickup transaction, reconcile the renderer's already-tracked coordinate immediately. Retire the old placed ingredient helper and update any surviving bottle stack through the shared visual sync logic. Never remove visuals before inventory/hand success; visual failure must not roll back an already committed item transfer. Normal dirty refresh remains the retry path.

This removes the known five-tick pump dependency for successful immediate reconciliation. It does not promise zero client-visible packet/render latency. Source/API-double tests, CI compilation, actual client acceptance and family deployment remain separate gates. No Release or live deployment is part of this draft checkpoint.

Focused source verification: 203 native-storage/native-hand/held API-double tests, including 15 post-commit visual cases; 17 placed-core cases; 9 parity cases; source-conservation checks; runtime syntax and both bottle visual generator checks. Geometry and texture files have no differences from the G71 source pin.

Bounded preceding G71 native and Blockbench evidence: `NATIVE-BOTTLE-G71-20261006.json`. It does not certify the G72 cleanup or expand the recorded native coverage. Original screenshots and world data are not published.

Subsequent bounded G72 native check: `NATIVE-BOTTLE-G72-20261006.json` records two pickups with no residue in the first returned screenshots, retained ingredients through re-placement, and successful shaking. It does not establish zero-frame latency, all-view/skin coverage or complete client acceptance. This evidence update changes no runtime bytes.
