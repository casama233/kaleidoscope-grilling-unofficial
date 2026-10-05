# Main-sprite side attachment repair, private 6718

## Native failure and exact cause

Private6717 failed actual raw-beef helper appearance in the isolated client
1.26.52.3 Efe/upright/first-person/FOV60 main-hand test. At PTS4.800s textured
side strips jut beyond the beef; at4.900s an open rectangle extends into the
transparent background. The confirmed helper window is4.633–5.333s. Earlier
empty helper-hand views are the ordinary pre-helper phase. No reconstructed
whole-meal/helper return was observed in the dense5.500–6.833s completion window.
The saved4096-byte log ends mid-line:53split lines and zero error strings apply
only to that saved portion, not an error-free complete-session certification.

Clip SHA256:7e8c10ca41911ed35a890f4a10823792c71d06e50e595cc431dd084b8a8ec9db
Failed source:fb33b70bf9762c91224144e63d8a15b925761db5
Failed candidate receipt SHA256:
3b29387235b064fc028dac9131b3c44236c4b0ee77ed7bb7da2f6013fbb0b732

The source Java span detector is not the failure. Its side elements were fed
through the global Java element converter while the helper retained an already
authored Bedrock front/back UV mapping. The actual mapping makes image U run
along Bedrock X=u−8 and V along Y=40−v. The6717sides instead used X=8−u, and
vertical side V ran upward. Thus their positions/texel directions disagreed
with the main sprite. A source-generator-output comparison could not catch
this cross-convention mismatch.

The convention is independently established by official Blockbench5.2.1's
Bedrock parseCube (reflect JSON X; reverse up/down UV endpoints) followed by
CubeFace.UVToLocal. Pinned primary sources:

- https://raw.githubusercontent.com/JannisX11/blockbench/v5.2.1/js/formats/bedrock/bedrock.js
- https://raw.githubusercontent.com/JannisX11/blockbench/v5.2.1/js/outliner/types/cube.js

The installed official app's source map was also read without launching a GUI.
Bedrock codec source SHA256:
d77fa9edfaaa042cd5f72211aea34cce19ff88ec477364d9bbc237355374d347
Cube source SHA256:
9e2a2eaf9a85fef1e7ebd9976fa3e6d450b99b10471ec237e07bf215e4ef4a4a

## Bounded correction

Only the separate helper side-geometry file changes exported runtime. Direct
Bedrock side boundaries follow the established main-face UV map. Horizontal
side long-axis U and vertical long-axis V are positive. LEFT remains JSON east
(X-min after codec import), RIGHT remains west (X-max). Each short UV axis
samples precisely one original boundary texel, with no texture substitution.

The global Java cube converter, source alpha/span facts, all main faces,
16×16 XY footprint, Z±0.5 thickness, hand binding, raw-last selection, geometry
identifier/index arrays, one render pass, native curves/placement/scales,
BP/metadata/consumption and6716terminal scripts stay unchanged. No push, merge,
release, live change, GUI, installation or symlink replacement is performed.
The failed6717candidate stays immutable;6718is a new private identity.

## Stronger regression and proof boundary

An independent oracle imports serialized Bedrock cubes and evaluates the six
face texel-to-surface maps, rather than importing the food generator's output
formula as its expected answer. It reconstructs actual occupied front/back
texel boundaries from alpha. Every true alpha contour must have an attached
side; every opaque side sample must touch its owning main-sprite cell edge.
Cell endpoints and depth fractions0/0.1/0.5/0.9/1 are checked at both main planes.
Java's min/max span merging also creates interior samples, so exact equality
with the exposed-edge set would be an incorrect test.

The real installed beef alpha (hash-verified numeric facts, no color artwork)
reproduces frozen6717's detachment and passes the corrected mesh:all50true
contour edges,94opaque side samples and1410endpoint/depth points. Mutations
restoring X reflection or reversed horizontal/vertical UV are rejected.
Asymmetric, disjoint, hole, partial-alpha and64×64fixtures are covered. The
same oracle checks every213actual referenced PNG against serialized runtime
meshes; the immutable candidate receipt records the actual aggregate counts
and input/output hashes. All external PNGs remain outside Git/runtime.

This certifies static texel/mesh connectivity, not GPU filtering, material
lighting, native startup or Java/Bedrock pixel/FOV parity. Bounded6718native
observations are recorded below. Other foods/rigs, resource-alpha replacements,
dynamic item models and full-family loading retain separate acceptance bounds.


## Bounded native evidence, 2026-10-05 UTC

These are two separate runs of unchanged runtime source
4018ad37661ffd2e69871f75cd9a017da591fb97 and the same frozen private 2.8.6718.
The original candidate receipt remains
78a6711ffc84c3a595cef046d9c7d0b54a5920150581b2e448202207a0721b6c;
archive SHA256 remains
a2dfa373c3829af730194fe60854fa0e683f0066045070be128b2eb99b18d14e.

### Recorded run: beef helper visually bounded-pass, completion unestablished

The GrillAlign6718QA recording used an operator-reported original/unconsumed
baseline clone, client 1.26.52.3, Efe skin, first person, upright, FOV 60, Survival, main-hand cooked
Apple/Carrot/RawBeef. The operator reported 6,500/12,000/30,000 ms holds; press/release
PTS were not instrumented and phases are not assigned to individual inputs.

- Actual helper frames at 67.500 s, 68.500 s and 69.500 s show the raw-beef stepped alpha
  silhouette with adjoining side faces. The prior 6717 detached strips and open
  rectangle are absent in inspected views. Root also viewed 67.500 s directly
- This is a bounded raw-beef helper visual pass for those views. It does not
  measure exact one-unit depth, certify all 213 native foods or Java pixels
- Helper remains at 69.567 s; full three-piece idle returns at 69.583 s and persists
  through the dense 70.583 s endpoint. Later inspected samples remain full idle
- No successful completed serving, empty-hand completion or effect icons are
  established by this recorded run. It remains an unsuccessful/inconclusive
  completion test; the later separate endpoint does not retroactively pass it
- The saved 36,864-byte log has 519 split lines, zero error strings, 233 Watchdog
  lines including a final partial line, and 232 fully parsed slowdown averages
  ranging 14–204 ms. Saved diagnostics do not establish a full clean session or
  explain the irregular progression. Normal close was reported 08:11:21 UTC

Recorded clip SHA256:
88196155315e5f306b78917fb7404168678d8a9da4db11d938c90e9931f2f0fc
Selected helper at 67.500 s PNG SHA256:
c7b06e60ebc4481b50d4047edcf48b82f2283e51dbb2fa4c8072133509f7e9f7
Recorded-run review JSON SHA256:
26e420e0c63e78ff0fbf2fcded5bac09f624ee0932373c552730f86ba5bbbe84
Recorded-run review text SHA256:
c3a35ec5ebcefc92222395178887e9759348d8b7ef01c7dc9e576a7414486938
Installed-copy record SHA256:
3e4446004432af89c5395e2333e9bf15d74ae3178d891f0c6fa94bcd4c8681cd
Recorded-run saved log SHA256:
622cd5ad84397a981331fc5d2f73bdb7ddfbdd8e57846433fda2973e3d48f263

### Separate fresh no-new-recording run: observed completion endpoint pass

GrillQuiet6718QA was reported as a fresh clone of the original unconsumed
probe baseline, with unchanged 6718, Efe/FOV 60/Survival/main-hand slot 6 and the same serving.
The fresh client session did not start a new SSR recording. After one 6,500 ms
held-use input, root's live CUA screenshots at 08:18:56 UTC and 08:19:18 UTC showed
an empty hand and empty slot 6 with two effect icons. The same endpoint was present
at both observations. This is a bounded observed completion endpoint
pass for that fresh run.

No screenshot file was saved: the attempted save failed with an argument-list
length error. Those live tool observations have no archived image/hash here.
There is no new video evidence or framewise completion-flash review for this run. In particular, an
empty endpoint cannot certify that no transient full-meal/helper flash occurred
between frames, exact intermediate timing, all retained-stack/Creative reset
flows, other hands or general consumption/metadata correctness.

The client was normally closed at 08:20:20 UTC and the stopped-world copy
world-g6718-quiet-after-0820 contains 12 files. Its LevelDB state was not interpreted.
The saved ContentLog2026-10-05_16-16-18_1.txt is 4,096 bytes with 53 split lines,
zero error/Watchdog strings, no trailing newline and a mid-line ending. These
counts apply only to the saved portion; they do not certify an error-free or
Watchdog-free complete session or diagnostics through the observed endpoints.

Fresh-run saved log SHA256:
abdf5fa16703da0f4e548e825aced6da784f7af2e0f7fa1b74dac72a374d8e62
Fresh stopped-world 12-file inventory tree SHA256:
be555c8701b354e779caf681d9cdd7fb706a040260b094256d5a907616de8f40
Inventory hash algorithm: SHA256 of sorted UTF-8 relative path, NUL, file SHA256, LF.
Combined root native-summary snapshot SHA256:
0a0c222d19011bc8efcf81a3cf95d396be58167896950c2dbd6742e6315932e2

### Remaining boundary

Both a fresh session and recording conditions changed together. The exact
slowdown cause remains unresolved; this is not a causal attribution to SSR,
geometry, server logic, CPU load or input delivery. The failed 6717 helper result
and 6718 recorded-run failure to establish completion remain preserved.

These observations add bounded beef-helper appearance and a separate fresh-run
completion endpoint. They do not grant all 213 food native acceptance, exact
Java parity, a new framewise no-flash completion pass, global/all-state client
acceptance, full-family/world persistence or production readiness. This update
is documentation-only: frozen candidate/receipt, runtime source identity,
public locks, installed packs, worlds and live deployment are not changed.
