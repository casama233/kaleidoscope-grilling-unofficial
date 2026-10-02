The six `particles/feedback_*.json` files adapt particle definitions from
Mojang/bedrock-samples, tag `v1.26.50.4`. Their materials, UVs, billboard appearance,
lifetimes and motion profiles remain based on those samples. Emitters are changed
to one particle at an explicit point, with a supplied velocity. No vanilla
particle identifier or texture is replaced.

Source: https://github.com/Mojang/bedrock-samples/tree/v1.26.50.4/resource_pack/particles

(c) Mojang AB. All rights reserved. The sample files are subject to the Minecraft
End User License Agreement: https://www.minecraft.net/en-us/eula

Source notice: https://github.com/Mojang/bedrock-samples/blob/v1.26.50.4/LICENSE.md

The source snapshots and checksums are recorded in this port's
`development/gameplay_core/fixtures/feedback-mojang-1.26.50.4.json`. Java gameplay
event positions, burst counts and velocity parameters come from Kaleidoscope
Grilling 1.1.1, pinned source `9a1acdab27698457bec16c9362678e574895a28c`.
