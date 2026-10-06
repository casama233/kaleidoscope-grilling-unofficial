# Historical family-profile material

`cookery-host.json`, `knife-metadata.json`, `batch1-candidate.json`, `candidate.json` and the storage overlay describe the older family compatibility batches. In particular, `candidate.json` is the fixed **2.8.9** candidate, and `cookery-host.json` records its Cookery **1.0.8** provenance. These records are retained unchanged; they are not the current canonical host lock and must not select dependencies for current packaging or installation.

For current releases, use:

- `baseline.json` and the paired canonical pack manifests for required host UUIDs/versions
- `projects/grilling/gameplay_core/behavior_pack/host-extensions/board-api.json` for the reviewed current author hooks
- `tools/fixtures/cookery-160-reference.json` and `tools/check_cookery160_host.py` for the Cookery 1.6.0 source review
- Canonical baseline, station-storage, family-knife and guide checks used by current CI

The old `tools/family_candidate.py` and `tools/apply_family_profile.py` belong to those historical candidates. They are not current build/install entry points. Do not run an old overlay over the canonical runtime. A later host UUID/data migration still needs its own saved-world and native acceptance.
