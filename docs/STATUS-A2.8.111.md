# G2.8.111 seasoning consumption and missing-base feedback

Current maintained Grilling 1.1.1 Forge 1.20.1 (CF8726006) and NeoForge
1.21.1 (CF8726014) call the four-argument GrillAutomationApi.season overload
from GrillBlock. That overload consumes seasoning in Creative as well as
Survival. G110 incorrectly returned an unchanged Creative bottle. G111 removes
that exemption: each occupied grill slot consumes one of sixteen doses, with
an exhausted bottle replaced by a fresh empty bottle. The existing verified
hand/state transaction, ingredient preservation and insufficient-dose refusal
remain. The production planner's 38 cases passed 36/failed 2 before and pass
38 after the repair; the two failures were the Creative hand cases.

SeasoningBottleBlock also specifies quiet rejection of a fifth bottle, and
selects bottle_full versus invalid_seasoning from the top bottle's ingredient
count even for a finished bottle or an unrelated held item. G111 restores these
rules. After a committed pickup or player break, a nonempty ingredient list
missing any of the three base ingredients emits the original translated
missing_base_seasoning message to chat (Java false overlay). Empty lists and
complete bases stay quiet. Failed transactions emit no success-side warning;
support loss and explosions do not acquire player-break feedback. This closes
the missing diagnostic, not proof of the reported native held-use failure.

The production storage/hand fixture now passes 78 cases, including thirteen
new rejection/chat/rollback cases; the existing hand fixture passes 116.
These use API doubles and actual canonical bodies, not simulated Minecraft
players, native input events or client acceptance. Current source excerpts were
reviewed separately for both maintained Java branches; automation planning's
base validation is not imposed on manual PENDING completion.

Package/modules/pair 2.8.111 and guide/payload 0.3.41 are synchronized. Required
canonical Git checks, complete-family native loading/restart and fresh stopped
saved-world rehearsal precede live development deployment. Physical use start,
four-second mixing, finished sprinkling, heard/rendered feedback and per-stack
inventory composition remain open in issues 168 and 166. No full Java parity
or client acceptance is claimed; client=false and production_ready=false.
