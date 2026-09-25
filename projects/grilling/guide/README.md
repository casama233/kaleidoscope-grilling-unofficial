# Grilling Guide content

## Canonical source

Guide A2.0 之后，当前玩家指南唯一内容源是：

- `projects/grilling/guide/content.a2.json`

它描述：

- 5 个玩家章节；
- 52 个主题；
- zh_CN / zh_TW / en_US 三套标题与正文；
- Cookery Guidebook Extension API v1 所需图标、分类与条目顺序。

生成正式 Cookery 集成内容：

```sh
python tools/build_grilling_guide.py
```

检查仓库中的 `payload.js` 与三套 `.lang` 是否仍由当前内容源生成：

```sh
python tools/build_grilling_guide.py --check
python tools/check_grilling_guide.py
```

## Delivery path

当前实际交付工程仍是：

- `projects/grilling/integration/cookery106/behavior_pack/`
- `projects/grilling/integration/cookery106/resource_pack/`

烟火只注册为 Cookery 原指南中的一个 `kg_a1:grilling` 入口，不新增第二本指南书。

Cookery 1.0.6 原始 Guidebook Extension API v1 的 `mechanicsByLocale` locale validator 有已验证兼容问题；canonical CI 会继续生成现有的窄范围 locale-compat host 候选，只修改该 validator，不修改 Cookery gameplay、UUID 或指南 UI 流程。

## Historical files

- `projects/grilling/guide/content.json` 是 A1.x 时代的历史内容快照，不再是当前发布来源。
- `development/guide/augment_a*.py`、`verify_a*.py` 保存旧版迁移和取证逻辑，不应在 A2.0 canonical guide 上重新执行。
- 旧 A1.x workflow 保留作历史证据；常规指南修改由 `.github/workflows/guide-canonical.yml` 验证。

## Validation boundary

Guide checker / Dash / compiled-output comparison 可以证明内容结构、引用、生成结果以及与当前 Gameplay Core 关键常数的静态一致性。

它们不能证明 Minecraft 客户端中的触控排版、控制器导航、字体换行、实际 Cookery UI 观感或多人环境行为；这些仍需真实客户端验收。
