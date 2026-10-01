# A2.8.16 — bridge. canonical normalization

- Add a complete repository-root bridge. project pointing at canonical BP/RP; preserve the existing gameplay-core entry and document legacy assets-only entry.
- Use a pass-through compiler profile and prevent automatic format-version correction. Document turning off automatic manifest version/metadata edits.
- Remove six Java-only top-level loot-table `type` fields. Every reward pool remains exactly the same; hashes recorded in `BRIDGE-LOOT-NORMALIZATION-20261001.json`.
- Add exact bridge. export/source comparisons and project regression tests, plus checksum-pinned real Dash CI.
- Repair the root check/build compatibility entry points so their sibling verifier modules import correctly.

No models, textures, animations, item IDs, UUIDs, recipes or gameplay scripts changed. Original Java parity gaps, client rendering acceptance and live saved-world migration remain open. See `BRIDGE-WORKFLOW.md` for schema-data limitations.
