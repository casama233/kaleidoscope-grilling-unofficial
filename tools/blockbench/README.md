# Native Blockbench audit

Use official Blockbench 5.2.1 or later. The local plugin is project-owned source,
not an official Blockbench plugin and not a network/MCP server. Review it before
loading it. It requests filesystem access to read the specification/models and
write a separate report directory; "Allow once" is sufficient. It never writes
canonical model files and contains no network calls.

1. Run `python tools/blockbench/prepare_audit.py --output /absolute/audit-directory --all-held`.
2. In Blockbench, File → Plugins → Load Plugin from File; choose `senra_model_audit.js`.
3. Tools → Audit Senra Models (Read-only); choose the generated input JSON.
4. Tools → Preview Senra Held Models (Read-only); select the same input JSON.
5. Inspect reports and actual PNGs in `native-blockbench/`. Never bulk-replace
   canonical geometry with the editor exports: visible bounds and display
   defaults may be recomputed despite otherwise equivalent geometry.

The full model pass loads and compiles every geometry definition with Blockbench's
native Bedrock codec, runs its Validator, checks finite native mesh positions and
records input source hashes. Held preview runs actual animation import and built-in
first-/third-person attachment reference modes. The built-in reference is right-
handed; offhand selector/math checks are not native offhand or client acceptance.

A bottle's contents are combined with its shell only in the temporary editor
preview. This cannot certify the game's separate alpha/material render passes.
Screenshots do not simulate eating, touch controls, resource-pack caching, other
skins, or the Minecraft GPU pipeline. No Blockbench warning is not a visual pass.
