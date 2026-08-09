# Harness derivation — unified — round 199

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What personal facts did you infer from me since yesterday? Show me the exact evidence for each, and let me keep or forget them one by one.”"
- **useful because:** The system currently extracts facts invisibly, while deletion policy says anything extracted without an explicit request must be listable and individually erasable. This makes memory trustworthy: the owner can recognize the source, reject an inference, and receive a receipt that the fact, derived copies, and evidence capsule were removed without deleting the action audit trail.
- **path:** pendant → relay → mac-planner → dashboard-ux
- **model tier:** background for candidate clustering and evidence summarization; realtime only for the owner's spoken keep/forget decisions
- **latency:** First spoken list within 3 seconds; each keep/forget decision acknowledged within 1 second; off-machine deletion may be reported pending rather than falsely complete.
- **cost:** About $0.01–$0.05 per daily review, dominated by summarizing evidence; deletion itself is deterministic and free.
- **security:** Only extracted candidates and bounded evidence excerpts should leave the relay; redact secrets and raw audio by default. Forget must require an exact candidate ID and produce a signed pending/completed receipt. Never delete job history. Off-machine replicas must be marked requested-and-pending until confirmed.
- **missing:** A durable candidate state distinct from accepted facts (proposed/kept/forgotten/expired); An owner-facing dashboard or pendant speech format for evidence cards; Cross-store erase transaction covering facts.json, context graph, relay replicas, and evidence capsules

### "“I’m about to send/book/buy this. Read the exact page and tell me what will happen, what could conflict with my calendar or existing commitments, and wait for the pendant’s physical approval before doing it.”"
- **useful because:** This is the system's highest-value cross-surface action: the browser has private authenticated state, the Mac can compare calendar and commitments, the relay can preserve a plan while the browser changes, and the pendant supplies consent that a bearer-token Mac agent cannot impersonate. It prevents the dangerous failure mode where a spoken promise is announced but a blocked action is silently discarded.
- **path:** browser-extension → mac-planner → relay → pendant → dashboard-ux
- **model tier:** realtime for concise spoken preflight; background deterministic checks for page extraction, calendar conflicts, plan digest/world fingerprint, and receipt reconciliation
- **latency:** Preview in 4 seconds for ordinary pages; no mutation until physical approval; after approval, report browser submission and external confirmation separately.
- **cost:** $0.02–$0.10 per preflight, mostly model interpretation of page text; deterministic browser/calendar checks dominate latency, not token cost.
- **security:** Never send page secrets or form values to the pendant. Bind approval to opaque nonce, plan digest, world fingerprint, expiry, and replay counter. Treat browser submission as off-machine/irreversible where applicable and require a distinct spoken confirmation word plus the physical latch. If the page changes, refuse rather than silently replan.
- **missing:** A production caller from bridge/orchestrator into prepare/approve; Relay persistence and delivery for the existing approval handoff contract; A real dashboard/next-conversation path for pending approvals because the pendant cannot receive unsolicited prompts; Browser-side final-result verification after submission

### "“Erase the last thing I said from this conversation, everywhere, but keep the audit record of actions you already took.”"
- **useful because:** The owner needs an utterance-scoped privacy action, not only an all-device latch or whole voice-note deletion. It should remove the selected transcript/audio, derived facts and evidence capsules, and relay replicas while explicitly retaining job history. This gives a practical correction when the owner realizes a sentence was sensitive, without requiring them to remember an internal note ID.
- **path:** pendant → relay → mac-planner → mac-bridge → dashboard-ux
- **model tier:** realtime to identify the utterance boundary and obtain a deliberate confirmation; deterministic background erasure and replica reconciliation
- **latency:** Local capture/playback stop immediately; identify and preview the target in under 2 seconds; local deletion immediately, remote replicas shown as pending until receipts arrive.
- **cost:** Usually under $0.02 per erase; cost is dominated by replica confirmation and evidence indexing, not inference.
- **security:** Default to the smallest clearly bounded utterance; if boundaries are ambiguous, ask rather than over-delete. Require a confirmation phrase or physical approval for remote deletion. Preserve immutable action audit records but redact their copied content. Never claim remote deletion completed without a receipt.
- **missing:** Stable utterance IDs linking transcript, audio, extracted facts, evidence capsules, and relay replicas; A bounded erase transaction with tombstones/idempotency and retry; A spoken preview/confirmation path that works on the next conversation despite no unsolicited pendant push

### "“Something failed while you were working. Tell me exactly what reached the Mac, browser, relay, and pendant, what did not, and give me only the safe next choices.”"
- **useful because:** A job status is not enough: a relay receipt can say accepted while a browser command never ran, or audio can be delivered without being heard. This owner-facing incident answer joins the evidence by one intent and distinguishes completed, pending, failed, and unknown, so the owner does not retry an unrepeatable action blindly.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard-ux
- **model tier:** deterministic evidence join first; cheap background model only to phrase the bounded explanation
- **latency:** Return a compact spoken diagnosis within 2 seconds from cached receipts; refresh live surfaces only when needed, with a 10-second timeout and explicit unknown state.
- **cost:** Under $0.01 per query; mostly storage reads, with model cost only for natural-language compression.
- **security:** Scope the join to a signed intent/job binding, redact page content and secrets, and never infer success from absence of an error. A retry recommendation must use replaySafety, not reversibility, and must refuse unknown/unrepeatable actions.
- **missing:** A stable cross-surface correlation key carried into browser, Mac, relay, and audio receipts; A typed outcome vocabulary and provenance-preserving join endpoint; A safe-choice renderer that exposes retry/ask/blocked without executing

### "“Keep anything I say about this topic on my Mac. Do not send it to the relay, browser, or pendant history, and tell me if a requested action would require crossing that boundary.”"
- **useful because:** The current privacy latch stops capture, but it cannot express a durable data-routing boundary for a category of conversation. This would let the owner use the system for sensitive work while knowing exactly which surfaces may receive content and when a task cannot be completed without disclosure.
- **path:** pendant → mac-planner → relay → browser-extension → dashboard-ux
- **model tier:** realtime only to interpret and confirm a policy change; deterministic enforcement at every capture, memory, browser, relay, and receipt boundary
- **latency:** Policy decision before the next utterance; enforcement adds no perceptible latency. A blocked cross-boundary action should be explained within 2 seconds.
- **cost:** Under $0.01 per policy change; ongoing enforcement is metadata checks with negligible model cost.
- **security:** The policy must be enforced before upload, not applied after relay storage. Use a local classification tag, fail closed when classification is uncertain, and prevent sensitive text from appearing in logs, prompts, receipts, or browser commands. Policy changes require physical or spoken confirmation and produce a local-only audit receipt.
- **missing:** A field-level data residency policy engine enforced before capture upload and memory extraction; Local classification/redaction on the pendant or Mac before relay transmission; Surface capability declarations so the planner can prove whether an action crosses the boundary; A local-only receipt store

### "“Only accept a high-stakes command if it came from my live pendant turn, not a replayed transcript, browser result, or queued job. Tell me when you cannot prove that.”"
- **useful because:** Bearer-token access and copied transcripts currently do not establish that a sensitive instruction was uttered live by the owner. A hardware-attested turn would let the system safely distinguish an owner's present command from stale or injected text before sending a message, approving a purchase, deleting data, or changing a routine.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** deterministic verification; realtime model interprets the command only after attestation passes
- **latency:** Under 150 ms for attestation verification; no model work should begin until the authenticity check succeeds.
- **cost:** Negligible per turn; cryptographic verification is local and the attestation adds a small envelope to existing audio/control traffic.
- **security:** The private key must remain on protected device storage; bind the signature to turn ID, monotonic counter, session, and expiry; reject duplicates and unverifiable transport. Do not treat voice biometrics as identity. This proves device-originated live input, not who physically holds the pendant, so high-risk actions still need the existing physical approval latch.
- **missing:** Device key provisioning and protected-key storage; Firmware signing of button-to-capture turn boundaries and a monotonic anti-replay counter; Relay verification and propagation of attestation status into Mac/browser planners; A policy mapping command classes to required attestation and physical approval

### "“Before you change anything that affects another person, show me who is affected, what they would see, and the least-impacting alternative.”"
- **useful because:** The current planner can classify action risk, but it does not model human impact across a calendar invite, shared document, message, or browser workflow. An impact preview would make the system useful as an agent rather than merely an executor: the owner sees recipient scope, notifications, permissions, and collateral changes before approval.
- **path:** browser-extension → mac-planner → relay → dashboard-ux → pendant
- **model tier:** background planner for deterministic recipient/permission/diff analysis; realtime only to summarize the preview and collect the owner's choice
- **latency:** Preview in 3–5 seconds for ordinary actions; no external mutation until the owner chooses an option and, where required, uses physical approval.
- **cost:** $0.02–$0.08 per preview, dominated by reading authenticated page state and generating a concise alternative comparison.
- **security:** Inspect only explicitly bound tabs/apps. Never infer recipients from hidden page content without displaying them. Treat permission expansion, external messages, and shared-resource edits as high-risk. Preserve the original plan digest and refuse if affected scope changes.
- **missing:** A cross-surface effect model for recipients, observers, permissions, notifications, and diffs; Browser and Mac adapters that expose side effects before mutation; An alternative-plan generator constrained to the same intent; A compact pendant/dashboard impact card


## Changes it proposed to its own stack

### `context` — Introduce a durable cross-surface intent envelope with one opaque intentId, source utterance hash, sensitivity class, replaySafety, and redacted artifact references. Require every Mac job, browser command, relay receipt, audio delivery event, and extracted fact candidate to carry it; expose a read-only join that returns only evidence references and state transitions.
- **owner gets:** The owner can ask “what happened to that?” once and get one truthful answer instead of separate Mac, browser, audio, and relay histories that cannot be connected. It also makes targeted forgetting and failure diagnosis possible without copying secrets into a central transcript.
- effort: High: schema migration and propagation through planners, browser bridge, relay jobs, pipeline/audio, memory extraction, and receipt writers; compatibility adapters can generate IDs for old jobs.  ·  risk: Correlation metadata could become a privacy side channel or accidentally join unrelated actions. Use random opaque IDs, per-surface authorization, retention limits, and refuse joins when provenance is missing rather than guessing.
- cost: A few dozen bytes per event and modest index storage; no meaningful model-token increase if only IDs and redacted references are propagated.  ·  latency: Sub-millisecond local indexing; remote joins may add one bounded read round trip.
- security: Reduces accidental data over-sharing by replacing content joins with references, but requires strict access control and deletion tombstones for derived references.
- depends on: Stable event IDs in existing action/audio/browser receipts; Relay schema migration and index; A retention/tombstone policy for intent envelopes; Typed outcome and replaySafety fields at all producers


## What it asked for

_Nothing._
