# A2.8.53 — Java skewer use gates and nested nutrition (draft)

Preserves the complete 2.8.52 bottle-frame candidate and published 2.8.51 integration contracts. Reference is Java Grilling 1.1.1 at `9a1acdab27698457bec16c9362678e574895a28c`.

## Repairs

- Ordinary fixed/secret skewer and plate eating is cancelled while sneaking, matching SkewerItem.use and SkewerPlateItem.use.
- The fullHungerEating setting now includes plates. Valid standing threading, crouch disassembly and hot-food consolidation are resolved before the eating gate.
- SkeweringHandler's crouch branch never threads: a stick or empty unfinished skewer in the offhand no longer accidentally begins threading while crouched.
- Nested/plated hot nutrition uses the existing configured saturationMultiplier once and remains capped by hunger, matching HotFoodHandler.finishNested's configured rule. Existing Bedrock setting range is retained.
- Successful threading plays action_success volume 0.7/pitch 1; successful grill insertion plays action_success 0.65/1. Brush/flip sounds are unchanged.

Nine deterministic production-function/callback regressions cover these boundaries. The canonical verifier includes them after every existing verifier through 2.8.52. These fixtures are not simulated players and do not certify rendered client behavior.

## Source references

- [SkewerItem](https://github.com/breezeth-CN/KaleidoscopeGrilling/blob/9a1acdab27698457bec16c9362678e574895a28c/neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/skewer/SkewerItem.java)
- [SkewerPlateItem](https://github.com/breezeth-CN/KaleidoscopeGrilling/blob/9a1acdab27698457bec16c9362678e574895a28c/neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/skewer/SkewerPlateItem.java)
- [SkeweringHandler](https://github.com/breezeth-CN/KaleidoscopeGrilling/blob/9a1acdab27698457bec16c9362678e574895a28c/neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/skewer/SkeweringHandler.java)
- [HotFoodHandler](https://github.com/breezeth-CN/KaleidoscopeGrilling/blob/9a1acdab27698457bec16c9362678e574895a28c/neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/food/HotFoodHandler.java)
- [GrillBlock](https://github.com/breezeth-CN/KaleidoscopeGrilling/blob/9a1acdab27698457bec16c9362678e574895a28c/neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/grill/GrillBlock.java)

Still open: one-tick release grace, cooked-secret snapshot timing, failed-skewer original model preservation, logout settlement and actual animation/client validation. This batch does not mark those complete.
