# A2.8.57 — bounded graphical eating HUD lifetime

## Native defect and repair

In the real Bedrock 1.26.52.3 cloud client, the A2.8.56 eating bar remained visible more than eight minutes after a raw beef skewer was consumed and the selected hand became empty. The runtime stopped sending valid eating packets, but the UI used an alpha animation whose start and end were both 1.

The canonical generator and generated UI now use an explicit zero-duration alpha start, a 75 ms constant-opacity wait, and a 1 ms fade to zero. The private packet/control names, original Java textures, 102-pixel bar, readiness checkpoint, shared-family message filters and script lifecycle are preserved. No actionbar clear packet or shared native completion event is introduced.

The chain follows Mojang's item-name alpha/wait/fade pattern: https://github.com/Mojang/bedrock-samples/blob/v1.26.50.4/resource_pack/ui/hud_screen.json#L1905-L1925

## Actual client observations on 2026-10-03

- A single-variable alpha endpoint 1→0 trial hid the bar after packet silence, but visibly faded during updates; it is not the final design.
- A wait-only animation attached through panel `anims` failed the native idle check and was rejected.
- The final alpha-bound chain showed no residual bar after five seconds without packets, preserved a normal actionbar message, displayed a restarted packet and hid again after the final stop.
- In survival, a single raw beef skewer remained after a 500 ms use/release; the eating bar did not remain.
- Holding use for 6000 ms then consumed the single skewer; the selected hand/slot became empty and no eating bar remained.
- These checks used the full paired local family, plus a temporary diagnostic BP for deterministic UI packets. The probe is not shipped. Gameplay eating checks occurred after its packet sequence ended.

## Verification limits

The native result certifies bounded visible lifetime for these exercised flows, not disposal of internal UI objects, frame-by-frame absence of every possible flicker, all skewer profiles, Java camera/animation parity, server migration or live deployment. Screenshot captures during held-key commands serialize behind that command, so they do not certify the full intermediate animation sequence. No release or live deployment is claimed.

Four focused HUD regressions and the full canonical functional chain passed during development; release hashes/build/family checks are tracked separately. Test images remain private; this report contains no world files or account data.
