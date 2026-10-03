# A2.8.55 — Advanced Rack visible-content selection (draft)

Preserves 2.8.54 release grace and all previous runtime repairs. This change fixes which stored items become placed rack helpers; it does not claim a complete native equivalent of Java FIXED item rendering.

## Source-backed correction

Java 1.1.1 reference: [AdvancedRackRenderer at 9a1acdab27698457bec16c9362678e574895a28c](https://github.com/breezeth-CN/KaleidoscopeGrilling/blob/9a1acdab27698457bec16c9362678e574895a28c/neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/rack/AdvancedRackRenderer.java).

- Upper slots 0–4 do not spawn equipped-item helpers. Their decorative containers already belong to the rack block's spice-level 0–4 meshes.
- Scan logical lower tool slots 5–8 in order, skip empty slots, and render at most three non-empty stacks.
- Compress those stacks onto source hook X positions -0.284, 0, +0.278. Empty storage slots do not leave an empty visual hook before a later item.
- Keep all nine storage compartments, including the fourth logical tool slot. An undisplayed fourth tool remains stored and available; it is not deleted or truncated.
- Retire legacy upper/fourth helpers on the next display synchronization. Helpers never own stored items.

The existing native helper Y/Z offsets and equipped-item pose remain unchanged. Java uses FIXED display, .75 scale and X/Y/Z transform composition; Bedrock's current equipped-item route has item-specific native transforms and third-party attachables. Blindly copying Euler angles or scale would not establish equivalence. That remaining projection work is explicit rather than hidden behind a passing helper-count test.

Six tests execute the actual display callback and read-only selection core. They cover all 16 tool-occupancy masks, upper exclusion, slot8 visibility with fewer earlier tools, cleanup and preserved storage references. Five tests reproduced the old behavior before the dispatch repair.

## Actual client observation on preceding 2.8.54

Real Android Bedrock1.26.52.3 through minecraft-linux was used in a disposable local world. `advanced_rack` was obtained through the native command, held in first person and front-facing third person, and placed by actual right-click. Both held views used the generated sprite; placement produced the full rack block mesh. Screenshots remain private test artifacts.

This confirms the intended held-sprite/placed-model route. It does not certify exact Java hand pose, populated-rack helper appearance, other skewer item contexts or eating/shaking animations. The .55 selection repair still needs populated-rack native visual acceptance.
