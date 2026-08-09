# Harness derivation — relay-realtime — round 171

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Keep working on this task after I stop talking and only ask me if you’re blocked."
- **useful because:** Lets the system behave like an assistant, not a dictation box. The owner can initiate a workflow by voice, then the Mac and browser can continue the multi-step work without holding a live conversation.
- **path:** relay → mac-bridge → browser
- **model tier:** mac-planner for multi-step workflows; browser extension for web steps; realtime only for brief confirmations
- **latency:** Start immediately; subsequent steps can be slower as long as progress is tracked and summarized.
- **cost:** Higher than a single action, dominated by planner iterations and browser actions. Savings come from not keeping the realtime tier engaged.
- **security:** High-impact actions should be reversible and logged. Use receipts and concise confirmations. Do not read or exfiltrate private data beyond the task scope.
- **missing:** A durable orchestration layer to resume after disconnects; Reliable status receipts surfaced to relay; A standard way to attach spoken summaries to job completion

### "What’s going on with my devices right now?"
- **useful because:** Quick situational awareness is perfect for a pendant: is the Mac reachable, is the bridge online, is a session active, what’s stuck?
- **path:** relay → mac-bridge
- **model tier:** realtime for quick spoken status
- **latency:** Under a second when cached; a few seconds when probing live endpoints.
- **cost:** Cheap. One or two status calls and a short spoken reply.
- **security:** Status may reveal patterns (when the owner is home). Keep it generic unless asked for specifics.
- **missing:** A relay-visible device status endpoint that is not 404; Consistent heartbeat from the bridge and pendant into the relay

### "When I say “read what I’m looking at,” have the pendant read the exact screen or browser region I meant, keep that snapshot as the reference for follow-up questions, and warn me if the page changed before acting on it."
- **useful because:** Today a spoken request can be routed to a Mac or browser, but there is no stable shared referent between what the owner saw, what the Mac inspected, and what the relay says aloud. Snapshot identity would prevent acting on a changed tab or answering about the wrong window while the owner is away from the keyboard.
- **path:** pendant → relay → mac-vision → browser-extension → mac-planner
- **model tier:** Realtime relay for disambiguation and short speech; mac-vision/browser harness for capture and region grounding; cheaper background model for OCR/summarization.
- **latency:** Initial grounding under 2 seconds; follow-up answer under 3 seconds. Snapshot hash and region metadata should be local/cheap; only interpretation spends model tokens.
- **cost:** Roughly $0.01–$0.05 per interaction depending on image/OCR tokens; capture and hashing dominate latency, not the relay response.
- **security:** Screen pixels and authenticated page contents leave the Mac only when explicitly requested. Bind each answer/action to a snapshot hash, redact secrets from spoken output, and never silently reuse an expired snapshot.
- **missing:** A Mac screen/region capture route with stable snapshot IDs and hashes; A browser inspection result that includes tab identity, URL, viewport/selection, and capture timestamp; A relay conversation field for the active visual referent; A change detector that can invalidate the referent before execution

### "If a task gets stuck because the Mac or browser needs one fact from me, have the relay ask exactly one short question on the pendant, let me answer by voice or button choice, and resume the same task without making me repeat the original request."
- **useful because:** A long-running delegated task currently has no conversational rendezvous: an alert can say something needs attention, but the owner cannot supply the missing value in-place and have the suspended plan resume with a typed answer. This is the difference between a useful away-from-Mac assistant and a job queue that eventually fails.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Realtime relay only for the clarification turn; mac-planner remains responsible for planning and execution; a cheap validator normalizes the answer into the waiting field.
- **latency:** Question should reach the pendant within 5 seconds of the blocker; resume acknowledgement within 2 seconds after the answer. No polling burden on the owner.
- **cost:** Usually one short realtime turn ($0.005–$0.03) plus negligible durable-state storage; expensive work remains on the existing planner job.
- **security:** Persist only the minimum pending question and answer, scoped to the originating job and session. Do not accept an answer after expiry or for a different job; authenticated browser values must never be echoed into speech unless requested.
- **missing:** A durable blocked-job state with a typed missing-input schema; An inbound pendant answer endpoint that correlates to the blocked job; Planner support for checkpoint/resume rather than restarting; A relay push path for clarification prompts, distinct from completion alerts

### "When I ask “is it really done?”, have the relay give me an evidence-linked answer: reconcile the Mac action receipt, the browser’s resulting state, and the relay’s delivery record, say what is proven versus merely attempted, and let me say “show me” to open the exact source."
- **useful because:** A success response today can describe an attempted action without proving the external state changed. The owner needs a trustworthy answer while wearing the pendant, especially for messages, purchases, edits, and authenticated web work; evidence linkage also makes failures diagnosable instead of forcing a Mac session.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Cheap deterministic reconciliation first; realtime model only converts the evidence graph into a concise spoken explanation and handles the “show me” follow-up.
- **latency:** Receipt reconciliation under 1 second when records exist; spoken answer under 3 seconds. Opening evidence may take normal Mac/browser latency.
- **cost:** Near-zero for hashes/status joins; $0.005–$0.02 for optional spoken synthesis and explanation. Storage is small typed receipt metadata, not screen/audio archives.
- **security:** Evidence references must be capability-scoped and expire; never speak private page contents by default. “Show me” should open the source on the already paired Mac/browser, and the owner should hear when proof is unavailable rather than a confident guess.
- **missing:** A common evidence record linking intent, action, receipt, observed postcondition, and delivery; Mac and browser adapters that report postcondition observations, not only command acceptance; A relay endpoint that answers evidence queries and resolves “show me” to a source; Dashboard/UI for inspecting the evidence chain


## Changes it proposed to its own stack

### `relay` — Implement a real event delivery path from job completion to the pendant, with a durable queue on the relay side (not on the pendant) and a delivery contract that replays undelivered events on reconnect.
- **owner gets:** They get completion results hands-free, even after the conversation ends, without polling.
- effort: Medium to high. Requires a durable object or KV-backed queue, delivery retries, and idempotent acknowledgements.  ·  risk: Duplicate or out-of-order notifications; mitigate with jobId+sequence and ack receipts.
- cost: Low per event. Storage cost scales with undelivered backlog.  ·  latency: Low; near-real-time when connected.
- security: Spoken content is sensitive. Encrypt at rest and require authenticated delivery. Keep payload minimal.

### `integration` — Create a cross-surface 'handoff contract' that defines what context is preserved when a realtime voice session ends (task summary, constraints, privacy level) and how downstream jobs reference it without resending full transcripts.
- **owner gets:** Tasks continue smoothly after they stop talking, and the system doesn’t forget why it started.
- effort: Medium. Requires schema, storage, and changes in planner and relay.  ·  risk: Context drift or accidental disclosure. Use minimal summaries and explicit privacy labels.
- cost: Reduces repeated context tokens, lowering API spend.  ·  latency: Faster follow-ups because less context must be re-sent.
- security: Clear boundaries reduce accidental leakage. Add TTLs and redaction.

### `model-routing` — Add a rule that routes anything not requiring immediate speech to mac_delegate, and only uses realtime for short confirmations or status. Include a 'verbosity budget' so long explanations are summarized automatically.
- **owner gets:** Feels snappy on the pendant and cheaper overall, while still getting work done.
- effort: Low to medium. Mostly policy and a few guardrails in the orchestrator.  ·  risk: Misrouting could delay time-sensitive tasks. Provide an override phrase like 'do it now' or 'tell me details'.
- cost: Reduces realtime token usage.  ·  latency: Improves responsiveness for quick interactions.
- security: Lower exposure of sensitive data in realtime transcripts.


## What it asked for

_Nothing._
