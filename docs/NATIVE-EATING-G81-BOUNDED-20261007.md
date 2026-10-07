# G81 native client: bounded eating, stop and relog observations

Observed: 2026-10-07, approximately 02:30–02:34 UTC. This is a documentation-only record for the exact published candidate below. It does not change runtime, assets, version locks, release contents or deployment state.

## Result and acceptance boundary

- Main-hand ordinary early release left the two-item stack and empty hunger unchanged
- A later main-hand release settled one item, added five hunger points and displayed a Strength icon; normal Save & Quit/reload retained the one-item stack and hunger without an extra debit or resumed eating
- A full main-hand use of the stack previously held offhand also settled one item and five hunger points, with a Strength icon and a settled held pose
- Normal right-click in air did not activate the offhand skewer in the tested shovel-mainhand or empty-mainhand arrangements. This is an observed offhand activation gap, not evidence of a new G81 settlement regression
- First- and third-person settled-pose stills exist. Continuous animation, matched Java visual parity and audio acceptance remain unverified

These observations add bounded native-client evidence. Keep `client=false`, `production_ready=false` and `pending_client_acceptance`; they are not full client acceptance, complete D02 logout equivalence or a release-readiness claim.

## Exact candidate and isolated setup

| Item | Identity |
| --- | --- |
| Repository | `casama233/kaleidoscope-grilling-unofficial`, numeric ID `1377218440` |
| Source commit | [`21b995bb1b1fdffd1e8300dc17a2b968272384a4`](https://github.com/casama233/kaleidoscope-grilling-unofficial/commit/21b995bb1b1fdffd1e8300dc17a2b968272384a4) |
| Published prerelease | [A2.8.81-test.311.1](https://github.com/casama233/kaleidoscope-grilling-unofficial/releases/tag/A2.8.81-test.311.1) |
| Installed Grilling archive | `Kaleidoscope_Grilling_A2.8.81_Review.mcaddon`, 14,012,370 bytes |
| Archive SHA256 | `22de5761877bb628f0c162acedf994f3082c82bcd259e03d859ca5df89b31fbe` |
| Exported-file comparison | All 4,141 archive entries matched the exact public source tree: 644 BP + 3,497 RP files |
| Required host | Unmodified author Cookery 1.6.0, archive SHA256 `da12fe6d39d7514aff1de3c963d69899324d771be5ca0fc3da1ccb759c7ad458` |
| Installation receipt SHA256 | `358757610a97ffcd21f793db47d9662530cba0676962c15af4630cf39b842980` |
| Native client | Bedrock `1.26.52.3` |

The stopped-world installer created an isolated clone and preserved the source world and original packs. It reused the exact author Cookery host, installed only the exact published Grilling candidate, and did not rewrite script module declarations. The candidate declares stable `@minecraft/server` 2.9.0; native startup reported promotion to 2.10. Tavern, World Liquor and external diagnostic packs were inactive. No saved-world migration acceptance or live-deployment acceptance is claimed.

The saved G80 rack fixture was preserved. G80 rack observations remain separate evidence and receive no new acceptance claim from this eating session.

The starting eating setup was Survival, hunger HUD empty, two cold/unseasoned `kaleidoscope_grilling:grilled_beef_skewer` items in the selected main-hand slot, with `enableEatingAnimations=true` confirmed. Hunger numbers below are read from the HUD: five points is 2.5 drumsticks, ten points is five drumsticks. No native event/tick trace was captured.

## Native input and visible outcomes

The hold intervals are requested wall-time mouse-input durations, not measurements of native ticks or event order. Screenshots are after release/settlement, not frame-by-frame use recordings.

| Sequence | Input and visible outcome | Evidence |
| --- | --- | --- |
| Baseline | Main hand: two beef skewers; hunger 0/20; no Strength icon | `g81_baseline.jpg` |
| Early release | Normal right-click in air held for 750 ms, then released. Stack remained two; hunger remained 0/20; no Strength icon | `g81_earlystop.jpg` |
| Later release | Normal right-click in air held for 1,750 ms, then released, before the item's declared 4.5-second full-use duration. Stack became one; hunger HUD 5/20; Strength icon visible; held pose settled | `g81_eligiblestop.jpg` |
| Normal relog | Save & Quit at 02:30:49 UTC; reload observed at 02:31:46 UTC. Stack remained one; hunger HUD remained 5/20; no extra debit or resumed eating observed | `g81_relog.jpg` |
| Offhand with shovel | Two beef skewers offhand, iron shovel mainhand. Normal right-click in air for 750 ms and then 1,750 ms did not visibly begin eating. Hunger remained 5/20; inventory still showed two offhand items | `g81_offhandearly.jpg`, `g81_offhandeligible.jpg`, `g81_offhandinventory.jpg` |
| Main-hand control | The same two-item offhand stack was moved into main hand through the inventory UI. A 4,700 ms full use, observed at 02:32:53 UTC, left one item; hunger HUD became 10/20; Strength icon visible; no extra debit; held pose settled | `g81_complete.jpg` |
| Empty-mainhand offhand | One skewer offhand, main hand empty. Normal right-click in air held for 1,750 ms, observed at 02:34:22 UTC, did not visibly begin eating; hunger remained 10/20 | `g81_empty_main_offhand.jpg` |
| Settled render stills | First-person held pose plus third-person rear/front stills recorded. The front still shows the settled held skewer | `g81_complete.jpg`, `g81_thirdperson.jpg`, `g81_thirdfront.jpg` |

The single later-release/relog sequence and full-use control showed one debit and one five-point hunger increment each. They do not establish every stack, food profile, effect, repeated-input ordering, disconnect route or multiplayer path.

## Offhand finding and source interpretation

Inventory placement in the offhand slot worked. The official [`minecraft:allow_off_hand` contract](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/itemreference/examples/itemcomponents/minecraft_allow_off_hand?view=minecraft-bedrock-stable) describes offhand inventory placement; it does not promise that normal right-click starts offhand food use.

The exact-source [beef-skewer item definition](https://github.com/casama233/kaleidoscope-grilling-unofficial/blob/21b995bb1b1fdffd1e8300dc17a2b968272384a4/projects/grilling/gameplay_core/behavior_pack/items/grilled_beef_skewer.json) enables offhand placement and a 4.5-second eating use. The [native start-use handler](https://github.com/casama233/kaleidoscope-grilling-unofficial/blob/21b995bb1b1fdffd1e8300dc17a2b968272384a4/projects/grilling/gameplay_core/behavior_pack/scripts/main.js#L912-L957) can track either captured hand when the engine supplies an item-use event. The [before-use handler](https://github.com/casama233/kaleidoscope-grilling-unofficial/blob/21b995bb1b1fdffd1e8300dc17a2b968272384a4/projects/grilling/gameplay_core/behavior_pack/scripts/main.js#L1035-L1059) rejects sneaking for edible skewers; sneaking is not an established offhand eating fallback.

Source inspection supports an activation-path investigation: no custom offhand eating input trigger is established by these handlers. The native tests themselves establish only that the two tested ordinary air-use arrangements did not visibly activate or debit the offhand item. Without a native event trace or a pre-G81 matched test, they cannot identify the missing event, prove its engine cause, or label this as a newly introduced G81 settlement bug. Offhand stop/relog and completion acceptance therefore remain open.

## What remains unverified

- The sub-50-ms stop/leave/deferred-callback race, exact 23/24/25-tick boundaries and actual native remaining-use counters
- Direct leave while charging, dimension changes, missing/zero counters, terminal complete/stop ordering, server shutdown/crash and full D02 logout equivalence
- Offhand eating activation and subsequent offhand stop/relog/completion behavior
- Continuous first/third-person movement, bite-stage transitions, animation interruption and comparison against matched source-pinned Java frames
- Sound: the client environment reported unavailable SDL3 audio output, so no sound quality, timing or parity acceptance is claimed
- Other food profiles, hot/seasoned metadata/effects, Creative, repeated or reentrant native input, multiplayer and full saved-world migration
- Rack targeting/placement and the rest of the G81 client acceptance matrix; earlier G80 rack observations retain their own bounded scope

The previously documented [G81 source repair and remaining D02 boundary](STATUS-A2.8.81.md) remains authoritative. Script doubles, static checks, exported-file identity and this native session are distinct evidence classes.

## Screenshot integrity index

All eleven original screenshot files were inspected. Their digests identify the retained evidence; the screenshots, private installation receipt, worlds, player logs, author scripts and machine paths are not included in this public documentation change.

| Evidence filename | SHA256 |
| --- | --- |
| `g81_baseline.jpg` | `5efb4fc574ac851a837e317c1b0bed401b79c5030e281097d10cb5af00b2e16a` |
| `g81_earlystop.jpg` | `22d44e7fba13d68d6689541627f3093ab3953836222883a16be488bcce108996` |
| `g81_eligiblestop.jpg` | `0203c11c9e7fcc7e3f03093c0f7e02e5506d4f5659a59591a41328c9dfff355e` |
| `g81_relog.jpg` | `e20cb851e7721f860bf65fda748bbc7f38eb6ce0e760509c5ae741b1a6804ad3` |
| `g81_offhandearly.jpg` | `6f3336832c00821a2fac87d7c158053689eff5f0a1fcd0685ecdb3e8b969800f` |
| `g81_offhandeligible.jpg` | `79208486bc91df10aced34d82839a1125f1fc4c544a3196bfc021f7bd4c60f6c` |
| `g81_offhandinventory.jpg` | `b0bf084215c076749f55e9bb45264ad9a61c3cb66c084f893a4d322e9ab226c5` |
| `g81_complete.jpg` | `c274a271c0e25acd1a99694249d6339264c12d8942ea9d39ce40be4cccd8b207` |
| `g81_empty_main_offhand.jpg` | `268462fe621f7b3d93ddaee4a2130669bf2818db11d2781e8d72a51b6ab7aebd` |
| `g81_thirdperson.jpg` | `e469181365d7b49411210f11f9b5ee5233dd8e762884200498f2c0179ba01324` |
| `g81_thirdfront.jpg` | `ebe33f3829339428afffb91d3eeda692a9b9ebf4bd73d3eddeed2bb552eb1505` |

No runtime repair is asserted by this report. No exported file changes, pack-version bump, merge, new release or live restart accompany its publication.
