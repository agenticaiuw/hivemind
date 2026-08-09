# Harness derivation — unified — round 208

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I lost connection in the middle of that conversation—continue from the exact next turn, without repeating audio or making me repeat myself.”"
- **useful because:** A dropped LTE/WebSocket session currently makes a spoken interaction feel abandoned or risks replay. This would make the wearable conversation durable across relay, Mac bridge, and reconnects: preserve semantic turn boundaries and a playback cursor, then resume only the unacknowledged portion.
- **path:** pendant → relay → mac-bridge
- **model tier:** Realtime for turn-boundary detection and low-latency continuation; background tier for compact transcript/audio checkpoint compaction.
- **latency:** Checkpoint at each utterance boundary in under 150 ms; reconnect recovery under 2 s. Never resume in the middle of a word or duplicate a completed turn.
- **cost:** About $0.001–$0.01 per interrupted conversation for compact transcript/checkpoint work; storage and relay bandwidth dominate, not inference.
- **security:** Encrypt checkpoints; retain only the current conversation TTL; bind every cursor to session and device nonce; require the pendant's next deliberate press to resume if the interruption occurred during an action or sensitive response. Raw audio should be discarded after acknowledged playback.
- **missing:** A durable conversation-turn checkpoint schema and cursor acknowledgement spanning relay and pendant; A reconnect handshake that proves the last heard turn and rejects duplicate TTS; A relay-side TTL/GC policy for interrupted conversation state

### "“Do that in my logged-in browser, then prove to me what actually changed—not just that the click succeeded.”"
- **useful because:** Browser command acceptance is not the same as the requested outcome. This would join the staged intent, browser command receipt, postcondition evidence, and (when relevant) a Mac-side confirmation into one owner-facing result, catching silent no-ops, wrong tabs, and partial submissions.
- **path:** browser-extension → mac-bridge → relay
- **model tier:** Background/planner tier for postcondition reasoning; deterministic checks first, with an expensive model only when evidence is ambiguous.
- **latency:** Return an initial action receipt immediately, then verify within 3 s or label the outcome pending; never claim success without bound evidence.
- **cost:** Usually <$0.003 per verification; model cost only for ambiguous pages. Browser inspection and evidence retention dominate latency.
- **security:** Bind evidence to an explicit tab/session target and pre-action digest; redact secrets and page contents from relay; never infer success from a generic URL or button click; require confirmation for irreversible or off-machine outcomes.
- **missing:** A typed postcondition contract attached to each browser intent; A read-only browser snapshot/diff endpoint with stable element or form-field provenance; A joiner that correlates browser result, relay receipt, and optional Mac evidence without copying credentials

### "“I can’t find my pendant—freeze anything queued for it and lock down the browser and Mac until I recover it.”"
- **useful because:** A lost wearable is a cross-surface security incident, not merely an offline device. One owner command should quarantine pending action approvals, stop browser commands and queued audio exposure, mark the device suspect, and provide a reversible recovery ceremony when the pendant returns.
- **path:** pendant → relay → mac-bridge → browser-extension → dashboard
- **model tier:** Deterministic policy and state machine; no expensive model needed except optional owner-facing explanation.
- **latency:** Relay quarantine under 1 s; Mac/browser polling observes it within 5 s; recovery requires explicit physical approval and a fresh device challenge.
- **cost:** Negligible inference cost; a few durable relay state writes and heartbeat checks per incident.
- **security:** Fail closed for pending off-machine, irreversible, and browser actions; do not erase audit history; keep the privacy latch independent; use device identity, monotonic counter, expiry, and a one-time recovery challenge to prevent replay or an attacker reviving an old pendant.
- **missing:** A device trust/revocation state in the relay; A fan-out quarantine signal consumed by Mac bridge and browser bridge; A recovery ceremony that extends physical_transaction_approval_latch with device identity and anti-replay counters; A durable heartbeat and stale-device policy

### "“Show me every place this system learned or copied that fact, and let me inspect the exact evidence before I keep it.”"
- **useful because:** The owner’s extracted facts are currently invisible as a connected lineage. This would expose a human-readable chain from spoken evidence to relay record, memory projection, context-graph entity, and any derived copy, with confidence and timestamps, without exposing unrelated secrets.
- **path:** pendant → relay → mac-bridge → browser-extension → dashboard
- **model tier:** Background tier for grouping and plain-language explanations; deterministic provenance joins first and no model call for simple lineage.
- **latency:** Open the lineage view within 2 seconds; stream deeper evidence lazily. A delete request must show the complete affected-copy set before execution.
- **cost:** Usually <$0.002 per query; storage/indexing and redaction dominate.
- **security:** Evidence capsules may contain private speech and browser context. Default to redacted excerpts, bind access to the owner session, never send credentials to the relay, and preserve action audit history even when a fact is erased.
- **missing:** A provenance graph that links extracted facts to evidence capsules and all derived copies; Owner-facing redacted evidence rendering and an impact preview for deletion; A transactional erase operation spanning local and off-machine replicas with requested-and-pending status

### "“If the pendant cannot play your answer, give me a private text fallback on my Mac and continue exactly once—never both silently.”"
- **useful because:** A relay receipt or websocket acknowledgement does not mean the owner heard the response. This capability would detect failed or unconfirmed playback, expose the answer in a chosen Mac surface, and reconcile the playback cursor so reconnecting audio cannot duplicate it.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Deterministic delivery state machine; background tier only to compress a long response for text fallback.
- **latency:** Offer fallback within 3 seconds of a playback timeout or explicit pendant failure; suppress fallback when playback is confirmed.
- **cost:** Near-zero model cost for short replies; <$0.005 when summarization is needed. Delivery telemetry is the main overhead.
- **security:** Text fallback may be visible to bystanders. Require an owner-selected private surface, redact sensitive replies unless explicitly allowed, encrypt pending content, and expire unplayed fallbacks.
- **missing:** A cross-surface playback arbitration state machine with exactly-once semantic response IDs; A private-surface preference and visibility check on the Mac; A relay policy for expiration and deletion of unplayed fallback text

### "“Take this multi-step task as far as you safely can while I’m away, then leave me a compact proof packet—not a vague ‘done’.”"
- **useful because:** Long tasks currently have fragmented jobs and receipts, but no owner-facing deliverable that separates completed, blocked, and unverified steps across Mac and browser. This would produce a resumable proof packet with artifacts, decisions needed, and explicit uncertainty rather than silently continuing or claiming success.
- **path:** relay → mac-bridge → browser-extension → dashboard → pendant
- **model tier:** Background/planner tier for decomposition and proof summarization; deterministic execution and receipt validation for each step.
- **latency:** Start immediately, checkpoint after every step, and surface a compact status at the next owner interaction; never wait on the expensive model for safety decisions.
- **cost:** $0.01–$0.10 for a substantial task depending on planning and summarization; browser/Mac execution and evidence capture dominate.
- **security:** Every step needs replay-safety and risk classification; irreversible/off-machine steps pause for physical approval; secrets remain in the browser/Mac boundary; proof packets must cite evidence rather than include raw sensitive contents.
- **missing:** A durable task envelope joining relay job, Mac job, browser commands, and proof artifacts; A policy that separates auto-runnable idempotent steps from approval-gated steps; A compact owner-facing proof format with explicit blocked/unverified states and resumable handoff


## Changes it proposed to its own stack

### `relay` — Add a device-revocation and quarantine state machine keyed by a hardware-backed pendant identity and monotonic counter. A lost-device command atomically marks the pendant suspect, cancels or freezes all pending browser/Mac commands and staged approvals, and fan-outs a signed quarantine epoch. Reconnects must prove a newer device counter and pass a fresh physical approval before normal traffic resumes; all transitions remain in the audit ledger.
- **owner gets:** If the pendant is lost, one action stops it from authorizing or exposing anything while preserving the history of what was frozen. Recovery is deliberate rather than silently trusting whichever device reconnects first.
- effort: Medium-high: relay schema/state machine, Mac/browser bridge hooks, reconnect protocol, and firmware identity/counter plumbing; test with dropped links and replayed frames.  ·  risk: A false quarantine can interrupt a conversation or leave work paused. Make quarantine reversible, show exactly what was frozen, and provide a time-limited recovery path; never delete audit records.
- cost: Negligible model/API cost; a few small durable relay records and heartbeat writes. Hardware cost $0 if the nRF9160 identity/counter facilities are sufficient; otherwise a secure element is an optional future addition.  ·  latency: Quarantine fan-out under 1 second at relay; bridge observation within its polling interval. Normal reconnect adds one challenge round-trip.
- security: Strongly improves fail-closed behavior and replay resistance; requires careful key provisioning and protection of the device identity. Does not weaken the local privacy latch.
- depends on: physical_transaction_approval_latch must expose a device-bound nonce/counter; relay_jobs needs an expiry/requeue lease so quarantined work cannot remain ambiguously processing; Mac and browser bridges need to honor a signed quarantine epoch


## What it asked for

_Nothing._
## Its own summary

Recorded three new cross-surface capabilities and one relay change: resumable conversation turns after a link drop; postcondition-proven browser actions; lost-pendant quarantine/recovery; and a device-revocation epoch that freezes Mac/browser work. The live Mac agent is healthy (GET /health 200, v0.5.0), and the pendant remains physically testable over USB but USB is not a product transport.

**Biggest unknown:** The implementation-critical unknowns are the durable conversation checkpoint/cursor contract, whether the existing browser and workbench routes expose enough provenance for postcondition verification, and how the nRF9160 should provide a device-bound identity/monotonic counter. I still need those inspected or specified; I am not re-requesting the already-pending browser identity attestation or denied macOS TCC permissions.

