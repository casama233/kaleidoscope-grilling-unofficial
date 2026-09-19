# Migration checkpoint — 2026-09-19

## Confirmed destination

- Repository: `casama233/kaleidoscope-grilling-unofficial`
- Numeric repository ID: `1377218440`
- Branch: `main`

The repository was empty before this initialization. Repository identity is recorded in `.repo-target.json`; `AGENTS.md` requires checking the actual remote name and numeric ID before future writes.

## Actually imported in this checkpoint

The following three files were taken from the delivered `Grilling_A1.13_Recovery_Development.zip`, under `project/continuation_a113/notebook/`, without source changes:

| Repository path | Bytes | Expected Git blob SHA-1 |
|---|---:|---|
| `notebook/core.js` | 5660 | `ab30323d2eb73f02f3016313b16f36ea01b16f4b` |
| `notebook/test.mjs` | 3517 | `a8d9a7ef84de89e4d1f886fdc795e54da9a8741a` |
| `notebook/package.json` | 33 | `f9ec9b62f616f5c61144ef14c6cbbb1f8454f745` |

`node notebook/test.mjs` was rerun locally during migration: exit code 0, 27 checks passed. These use mock per-player adapters. They do not prove Minecraft persistence across world reloads, real guide callbacks, BDS compatibility, or a completed addon.

## Archive baselines still outside this repository

These SHA-256 values were calculated from the actual conversation files. The archive filenames below are inventory records, NOT public download links and NOT a claim that the archive bytes have been committed here.

| Existing archive | SHA-256 |
|---|---|
| `KaleidoscopeGrilling_Bedrock_A1.12.0.zip` | `5913ef9efd6c434e5a6e77cb24e2fcc4a770a6883f09d3d468d077a069fb5922` |
| `Grilling_A1.13_Recovery_Development.zip` | `8f8ad72ba683a824ffacde459ff0e13dbafe583bf680e13117098eec6508d699` |

Pending full import: cumulative models, textures, source snapshots, conversion/review tools, guide test BP/RP, documentation and generated review material. The A1.12 archive remains the verified cumulative asset baseline; do not infer that unfinished later work exists because a preview image or status claim mentions it.

No Cookery installation archive, third-party private script collection, world, credential or local environment dump is included. No automated importer is enabled in this checkpoint.

## Development boundaries retained

One Grilling entry in the existing Cookery guide; no extra guidebook item. Notebook storage code is not yet bound to interactive in-game guide pages. Static model verification is separate from Minecraft lighting, materials, poses and animation acceptance. No new gameplay completion is claimed by this migration.
