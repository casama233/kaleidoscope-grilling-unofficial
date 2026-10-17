# G76: legal rack occupancy states

G75 public `aada09a9ee8ae601122cf2f88eac3f78cf4f43ec` passed source/compiled checks but failed actual Bedrock1.26.52.3 rack registration. The native content log rejected `seasoning_occupancy` for having 32 values where a block state permits at most 16, then reported the rack block absent from the registry. Its item remained visible but could not place. This is a confirmed G75 defect, not an API-version hypothesis.

G76 splits the five occupancy bits into a low 0–15 state and a high 0–1 state. Logical five-slot occupancy, fixed shelf/tool layout, inventory/filter/payload keys and source model/texture bytes remain unchanged. Geometry visibility and runtime projection use both legal states. Old G75 identity/history and its failure evidence remain preserved; this is a fresh runtime identity.

Both G72 and G75 already required server2.9.0/server-ui2.2.0 and minimum engine1.26.50. The actual G75 log promoted server2.9 to2.10 successfully. No dependency downgrade is part of this repair. Cookery1.6.0 remains the exact host.

Focused checks passed: 48 rack tests, legal state domains, all 32 occupancy masks, production low/high projection/no-op/failure behavior, generator check mode and exact G76 structural expectations. All 1,251 tracked geometry files, 381 editor models and 2,990 texture-path files are byte-identical to G75. Generic source admission passed with 483 imports. Git-first draft publication and compiled CI remain separate from the root's native placement/interaction retest. No G76 native pass is claimed. BSM remains mandatory before merge/release/deployment; no release or live action is requested.

[Sanitized native failure receipt](NATIVE-RACK-G75-FAILURE-20261006.json) retains exact G75 source/archive and evidence hashes, without publishing private world paths or logs.
