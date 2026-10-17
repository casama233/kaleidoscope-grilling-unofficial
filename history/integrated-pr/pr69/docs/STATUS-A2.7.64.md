# A2.7.64 — Skewer Held Display Parity

本批完成 A2.7.62 Render Audit 最大的一组剩余问题：39 个 fixed-skewer attachable 的 held hierarchy 与 Java first/third-person display transform。

## 根因

旧正式链：

```
root (item-slot binding)
└─ bite geometry
```

A2.7.25 的通用 hold animation 又直接移动 bound root：

`position [0,7,2]`

这造成两个问题：

1. 39 个 attachable 的 first/third-person animation 都直接 transform 已綁手的 root；
2. Java fixed-skewer 已有完整 FP/TP rotation / translation / scale，但正式 Bedrock 只使用通用 offset。

## Java display

迁移前脚本核对 264 份 `item/fixed_skewers/` Java display report，四组 hand transform 一致。

共享 Java transform：

- FP right
  - rotation `[-95,-7,-163]`
  - translation `[-1,7.75,7.25]`
  - scale `[0.8,0.8,0.8]`
- FP left
  - rotation `[-94,0,-165]`
  - translation `[-1.5,7.25,7]`
  - scale `[0.8,0.8,0.8]`
- TP right/left
  - rotation `[-98.57,1.45,-174.51]`
  - translation `[0.75,6.25,5.5]`
  - scale `[0.8,0.8,0.8]`

## 修正

39 个 attachable 实际引用 150 个 bite-stage geometry。全部改为：

```
root (binding = q.item_slot_to_bone_name(context.item_slot))
└─ display
   └─ 原 bite geometry bones...
```

- bound root 不再被 hold animation 移动；
- 原有 bite geometry、UV、食物 stage、bite selector、pre_animation 不改；
- 新增共享 `a2764_skewer_java_display.animation.json`；
- 39 个 attachable 按 FP-right / FP-left / TP-right / TP-left 选择同一套 Java display animation；
- 旧 `a2725_skewer_hold.animation.json` 保留为历史文件，但已不再被正式 fixed-skewer attachable 引用。

一次性迁移日志实际确认：

- fixed-skewer attachables: **39**
- bite geometries: **150**
- geometry files changed: **150**
- Java display reports checked: **264**
- migration 后 Render Audit: **error 0 / high 0 / medium 0 / info 2**

info 2 仍只是 Big Vat 的 vanilla water/lava base-resource 引用。

## 防回归

Render Audit 现在把 fixed-skewer parity 升成 error-level contract：

- 必须有 39 个迁移后的 fixed-skewer attachable；
- 必须引用 150 个 bite geometry；
- 每个 geometry 的 root 必须保持 item-slot binding；
- 必须存在 unbound child `display`；
- shell bone 不得重新直接挂在 bound root 下；
- 四组共享 animation 必须逐值等于 pinned Java `beef_raw` display；
- attachable 不得重新引用 A2.7.25 bound-root hold animation；
- 四个 hand selector 必须同时存在。

## 验证边界

这批证明的是 canonical RP 结构与 pinned Java display 数值一致。实际 Minecraft FOV、玩家皮肤、左右手视觉、进食动画 blending 与 Android/GPU 最终像素仍需要实机验收。
