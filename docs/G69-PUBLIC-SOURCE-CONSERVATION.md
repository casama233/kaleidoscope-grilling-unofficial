# G69 public repaired-source conservation

## Current acceptance boundary

The current guards use the immutable, already-repaired public PR134 source:

- Repository: https://github.com/casama233/kaleidoscope-grilling-unofficial
- Commit: `a2656e08d97a6b4c31ef3667b2c957e18c80c8fd`
- Tree: `7d2c9c91d9d3be7713d893c76d64aa458b2cb1db`
- Exact witness file hashes: `tools/fixtures/g69-public-source-witness.json`

The six source-conservation tests pin current repaired runtime bytes. Independent
pose matrices, generator idempotence, exact item/profile/owner/use/terminal
behavior and mutation rejection remain active. Removing and reapplying an
explicit calibration suffix is a counterfactual check of its bounded expression,
not evidence that an unavailable earlier commit contained the uncalibrated data.
Release identity metadata is evaluated separately by the release gates.

These tests do not claim the former private-before comparison, newly establish
native-client rendering acceptance, or prove an exact historical repair delta.
No missing Git object was fabricated or remapped to another object's SHA.

## Earlier comparison history

The former before/after source objects are unavailable after the execution
workspace reset and are not current acceptance witnesses. Their original
references remain preserved in the already-public immutable source consumers:

- [Active calibration](https://github.com/casama233/kaleidoscope-grilling-unofficial/blob/a2656e08d97a6b4c31ef3667b2c957e18c80c8fd/development/gameplay_core/test_secret_active_calibration.py)
- [Idle calibration](https://github.com/casama233/kaleidoscope-grilling-unofficial/blob/a2656e08d97a6b4c31ef3667b2c957e18c80c8fd/development/gameplay_core/test_secret_idle_calibration.py)
- [Held owner context](https://github.com/casama233/kaleidoscope-grilling-unofficial/blob/a2656e08d97a6b4c31ef3667b2c957e18c80c8fd/development/gameplay_core/test_secret_held_owner_context.py)
- [Completion scope](https://github.com/casama233/kaleidoscope-grilling-unofficial/blob/a2656e08d97a6b4c31ef3667b2c957e18c80c8fd/development/gameplay_core/test_secret_completion_scope.py)
- [Terminal visibility](https://github.com/casama233/kaleidoscope-grilling-unofficial/blob/a2656e08d97a6b4c31ef3667b2c957e18c80c8fd/development/gameplay_core/test_secret_terminal_visibility.py)
- [Java eating projection admission](https://github.com/casama233/kaleidoscope-grilling-unofficial/blob/a2656e08d97a6b4c31ef3667b2c957e18c80c8fd/development/gameplay_core/test_java_eating_projection_admission.py)
- [Threaded idle QA builder](https://github.com/casama233/kaleidoscope-grilling-unofficial/blob/a2656e08d97a6b4c31ef3667b2c957e18c80c8fd/tools/build_threaded_idle_private.py)
- [Threaded secret QA builder](https://github.com/casama233/kaleidoscope-grilling-unofficial/blob/a2656e08d97a6b4c31ef3667b2c957e18c80c8fd/tools/build_threaded_secret_private.py)

The original checksum-pinned selected source pack remains unchanged, with two
original commits and 93 exact original objects. It continues to support the
other source comparisons. The audited active inventory additionally lists the
public PR134 commit so a shallow CI checkout fetches its exact source witness.
No historical G68 release identity or acceptance record is rewritten here.

## Archived builders

The obsolete one-shot private QA builders retain their complete original bytes
under `docs/archive/private-builders/` as non-executable historical text. They
are excluded from active Python pin discovery and are not current acceptance or
release builders. They still depend on the unavailable private source lineage
and old private candidate receipts.

- `build_threaded_idle_private.py.txt`: 9088 bytes; SHA256 `e317d33b2aad3f6619dda4cf34c96d843797ae489243a9385460f381485ab618`
- `build_threaded_secret_private.py.txt`: 9282 bytes; SHA256 `3115914dca63a84317c3729b4c302bdb1e782d65bfb90cf3089644c1ce32bc22`
