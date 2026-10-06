# G79: correct rack physical-hit coordinates

Base is pinned merged G78 `2c62525235ff95c2baa05623774d22acbe58ecf6`. Its seasoning/output preservation, semantic heat cleanup, legal rack states and six-tool source-derived display are retained. Earlier G75/G77 proposals stay in their original history; no previous identity is overwritten.

Actual G77 crosshair interaction at an upper shelf returned native `faceLocation.y = .3255882263` and resolved lower tool slot7. The category guard correctly rejected the seasoning bottle. Tavern's existing MCPE-223452 adapter documents negative-axis native hit mirroring; the corresponding true local Y is `.6744117737`, in the upper row. [Exact G77 native receipt](NATIVE-RACK-G77-DIAGNOSIS-20261006.json) records improved front tool silhouettes and the failed upper interaction. File logging did not retain the warning; screenshot hashes are the evidence authority.

G79 captures the player's head/view ray in the same before-event and intersects only the actual clicked rack's reviewed selection box. Existing slot mapping, event target, range, hand, sneak, facing, category and transactional ownership checks remain authoritative. Invalid or missed rays reject without using another block or guessed Y offsets.

Known direct touch (`InputInfo.lastInputModeUsed == Touch` and `touchOnlyAffectsHotbar == false`) uses the corrected native tapped-face point, preserving off-crosshair tapping. Touch-crosshair, mouse/gamepad and unknown modes use the ray. No platform-name inference is used. Direct-touch correction restores each negative world-axis fraction and the actual box face; it is separately validated against the reviewed bounds.

The opt-in `kg_rack_qa` log now includes relative head origin, view direction, raw event hit, derived ray point and selected point/source. It still omits identities, absolute world coordinates and stack data. Before ending the next isolated test, explicitly remove/read back the QA tag: the prior removal command was sent but not independently verified.

Focused helper/transaction/visual checks passed 76 tests, including negative coordinates, all facings, known direct-touch versus crosshair and unchanged lower ownership. These are source tests, not native acceptance. G79 upper insertion, all five occupancy cells, touch interaction and saved-world behavior still require actual acceptance. Cookery1.6.0 is unchanged. BSM remains mandatory before merge/release/deployment; no release/live action is requested.
