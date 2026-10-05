# Targeted threaded idle calibration, private 6711

This source repair builds on private 6709 source
`f64bcbd0a1f9e350c17aa7db1b05aa5d5430c236` and the exact 6710 diagnostic
component `fc83dee2b6918a78beccb13bd342244e3db42fe0`.

The native 1.26.52.3 A/B showed all three pieces of an existing cooked Secret
Mix Skewer in main-hand and off-hand idle first person at FOV 60. The previous
6708 main-hand view cropped the lower piece. Reference captures are
`G6710-cooked-secret-first-person.png` and
`G6710-cooked-secret-offhand-FOV60.png`.

This is a bounded empirical idle-placement calibration. Neither the diagnostic
nor the native A/B proves a universal intrinsic engine eye Y of 27.41, or pixel
parity at other FOVs, aspects, client versions, character rigs or postures.

## Implementation

- Two owned first-person idle clips are cloned from the unchanged shared pose
- Only position changes. Rotations, authored 0.8 scale and geometry stay intact
- The tested world-Y +3.41 offset is inverse-mapped through the right socket
  `Rz(115) Ry(45) Rx(-95)`, with Bedrock's position-X sign convention
- The left socket is translational, so its local Y moves by +3.41
- The calculated positions exactly reproduce the 6710 component
  - Right: [-8.44353417, 0.51001839, -8.65064748]
  - Left: [-11.88255811, 10.91077069, 10.76686643]
- Only Secret Mix Skewer, its THREE-ALT form and Unfinished Skewer opt in
- Clear `fp_idle_calibrated_right/left` aliases run only while that owning hand
  is idle. Existing `fp_right/left` aliases remain the original shared clips
  during active use, preserving legacy eating-base composition
- Active `fp_eat_*`, legacy `eat_*`, TP and raw-helper routes are unchanged
- Existing owner occupancy, render masks, metadata, property counts, palettes,
  0/1/2 partial state selection and 27 complete-state mapping are unchanged

`tools/secret_idle_calibration.py` is used by the canonical held and eating
motion generators. It verifies the immutable shared animation hash and emits
an independent owned animation file. Packaging only changes copied manifest
identity; it does not patch generated animation files.

## Remaining native acceptance

6711 still needs 0/1/2/3 ingredient views and the idle-to-active mouth/eating
transition checked in the real client. Eating animation, mouth alignment,
other view contexts and universal engine framing are not claimed fixed.
6708, 6709 and 6710 remain immutable; their original receipts are preserved.
No public release/lock, live deployment, user world or UI is changed here.
