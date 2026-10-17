# G2.8.109 pending seasoning completion

Both current Grilling1.1.1 branches (Forge1.20.1 CF8726006 and NeoForge1.21.1
CF8726014) finish every PENDING identity without testing base ingredient
membership. Their legacy loader creates PENDING for any nonempty old ingredient
list. G108 instead rejected missing-base pending items at completion, leaving
legitimate old or externally supplied pending bottles unable to become finished.
G109 removes that extra gate. EMPTY-to-PENDING promotion still requires the three
base ingredients. Captured hand/slot/identity, stale-event rejection, verified
metadata, fresh result semantics, one-time completion and write rollback remain.

Completion feedback now emits the original12 Happy Villager particle commands
before sound, retaining the captured dimension and reading fresh BlockPos-center
coordinates afterward. Its distinct sound alias uses PLAYERS classification,
16-block range, original ACTION_SUCCESS sample gain0.85 and caller volume0.8 /
pitch1. Generic block sounds and the other callers are unchanged. Source particle
command generation and native delivery are separate from rendered/ heard parity.

Focused current-source completion and audio oracles:18 cases,8 passed/10 failed
before the repair and18 passed afterward. These run actual runtime bodies with
API doubles; they are not native use events, player or rendered-client results.
Required CI retains the existing verifier chain. Package/module/pair2.8.109 and
guide/payload0.3.39 are synchronized by the canonical release producer.

An independent Native source-fragment observer passed four real ItemStack /
container cases (one base ingredient, foreign old ingredient, empty pending and
all three bases). Source result construction, zero uses, fresh name and exact
materials survived actual four-slot bottle inventory writes/readback. No API
getter was replaced. The observer called only the unmodified construction
fragment, not the complete handler, native use callbacks or player hand writes.
The first attempted Zombie hand observer failed because its equipment component
was unavailable before any case; that failure remains separate and is not
counted as successful completion evidence.

The fresh-bottle client regression in issue168 and ingredient-specific inventory
icons in issue166 remain open. Dot contact has not been established. Native sound
instance interruption, original local shake/tracking/network, full GUI composition,
projectile/collision/remaining terrain and complete Java parity remain unverified
or incomplete. Keep client=false and production_ready=false. Canonical PR/checks/
merge and complete family/static/Native/fresh stopped-world/admission precede the
standing live-development update.
