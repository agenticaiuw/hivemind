# Harness derivation — relay-realtime — round 74

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "While you are carrying out something I asked from the pendant, let me say “stop,” “pause,” or “that’s enough,” and have the whole operation halt promptly across the Mac and any authenticated browser tab, then tell me exactly what did and did not happen."
- **useful because:** Today a spoken request can hand work to a downstream agent, but the owner may be away from the Mac and cannot safely interrupt an in-flight multi-step operation. A wearable-level abort is especially valuable for accidental commands, changed intent, or an unexpected side effect. This is genuinely hive-specific: the pendant hears the interruption, the always-awake relay identifies the active operation, and Mac/browser workers must cooperatively stop and report a consistent partial result.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Realtime handles only the short interruption classification and spoken acknowledgement. A deterministic relay/job controller propagates cancellation; downstream agents use their existing models only to reach a safe action boundary and summarize the receipt.
- **latency:** Acknowledge the stop locally/in the relay within 300 ms where possible; send cancellation to all workers within 1 s; provide a final partial-operation receipt within 3 s. If a worker cannot stop immediately, say so explicitly rather than claiming success.
- **cost:** Usually one short realtime turn (roughly $0.01–$0.05 depending on audio duration); cancellation and receipts are mostly control-plane work. No model call should be needed for the final status unless the partial result requires summarization.
- **security:** The relay must bind an interruption to the owner’s active session/job and reject stale or guessed job IDs. Cancellation cannot undo an already-committed external mutation, so the spoken response must distinguish cancelled, completed, and unknown. Persist an immutable receipt of actions reached before the stop; do not transmit unrelated microphone audio or page contents.
- **missing:** A first-class cancellation token and operation tree spanning relay jobs, mac-planner plans, Mac action execution, and browser-extension commands; Cooperative cancellation checkpoints before every downstream action, including a bounded stop timeout and an explicit non-cancellable state for already-committed actions; A pendant/voice interruption path that remains active while a job is running, rather than treating the original turn as finished; One aggregated receipt schema that merges Mac and browser partial results and can be spoken concisely; Idempotent cancel handling so repeated “stop” commands are harmless

### "If the Mac drops offline while you are doing something for me, keep the task going in the server browser where that is possible; if the browser cannot reach the needed session, pause and resume on my Mac when it returns, without making me repeat the request."
- **useful because:** The owner wears the pendant away from the Mac, so connectivity and substrate availability change during real tasks. Today work is tied to whichever downstream surface received it. A portable, resumable task would let a request survive walking away, a sleeping laptop, or a temporarily unavailable browser while clearly refusing steps that require a missing capability or session.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Realtime only acknowledges the handoff and reports status. A cheaper background controller serializes and migrates the task; the planner/model is invoked only to re-plan steps that differ between substrates.
- **latency:** Detect a lost worker within 5 s, announce that the task is being preserved within 1 s of the next pendant interaction, and resume on an eligible surface within 10 s of availability. Never silently replay a mutation after migration.
- **cost:** Control-plane persistence is negligible; a migrated task generally costs one planner call (roughly $0.02–$0.15 depending on plan size) plus any browser/Mac execution calls. Keeping a compact action graph rather than transcript context limits repeated-token cost.
- **security:** Authenticated browser cookies and Mac-local data must never be copied between substrates. Each step declares required capabilities and data locality; only portable inputs and redacted state cross the relay. Mutating steps need idempotency keys and must be marked committed/unknown before a retry. The owner hears which surface acted and which steps were skipped.
- **missing:** A substrate-neutral task graph with capability and data-locality requirements per step; Checkpoint serialization of planner state, browser tab identity, Mac action receipts, and committed/unknown outcomes; A worker lease/heartbeat protocol and deterministic failover controller; Idempotency keys plus recovery rules preventing duplicate external mutations; A capability-aware migration planner that can substitute server-browser, Mac, or browser-extension steps without exporting secrets; Owner-visible spoken status for paused, migrated, resumed, and permanently blocked tasks

### "When a task is running, let me long-press the pendant’s single button to abort it silently, even if speech recognition is unavailable, and flash the LED to show whether the abort was accepted, pending uplink, or too late to prevent a committed action."
- **useful because:** A wearable control must remain usable in traffic, a meeting, loud environments, or when the owner cannot safely speak. The physical button is the only dependable local input and a fast abort is safer than waiting for a voice turn. The pendant can signal immediately, while the relay and Mac/browser workers reconcile the result and report the exact boundary reached.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-action
- **model tier:** No model is needed for the button event, cancellation propagation, or LED state machine. Realtime may give a brief spoken result after uplink; background workers produce the detailed receipt.
- **latency:** Firmware must record the long-press and show an acknowledgement LED pattern within 100 ms. Relay delivery should occur on the next available LTE-M uplink, target under 2 s; workers stop at their next checkpoint and reconcile a final receipt.
- **cost:** Near-zero inference cost; a small firmware change and one tiny control packet per abort. LTE-M traffic is negligible. The main engineering cost is reliable state reconciliation across dropped links.
- **security:** Only an active operation bound to this paired pendant may be cancelled. The event must be authenticated, monotonic, replay-resistant, and idempotent. LED patterns must not expose sensitive task content. If the link is down, label the local state as “abort queued,” never claim that remote work stopped, and expire queued aborts after the associated operation ends.
- **missing:** Firmware long-press event and persistent sequence number; A signed, replay-resistant abort packet and relay endpoint that accepts it while voice is unavailable; Relay-to-worker cancellation fan-out with checkpoints and exactly-once reconciliation; A compact pendant LED state machine for queued, delivered, stopped, and too-late outcomes; A final spoken and durable receipt joining the local event with Mac/browser execution state


## Changes it proposed to its own stack

### `integration` — Introduce a cross-surface job ledger with a single jobId, parent/child steps, and typed receipts. Relay creates the job and records the initial utterance. Mac planner and browser harness attach planned steps and receipts (with sources, timestamps, and before/after). Relay serves status and spoken summaries from this ledger, even when Mac is offline.
- **owner gets:** They can ask “what happened to that thing?” and get one consistent answer. It reduces confusion, avoids duplicate work, and makes results auditable without reading logs.
- effort: Medium to high: requires schema design, migration plan, and adapters in relay, mac-planner, and browser harness.  ·  risk: Mis-joining steps could mix tasks. Mitigate with idempotency keys, explicit parent/child linking, and strong source tagging. Provide an undo path for reversible actions.
- cost: Small per job for metadata storage; main cost is implementation time. Runtime cost is dominated by downstream execution, not the ledger.  ·  latency: Minimal added latency; writes are small. Status reads become fast and local to the relay.
- security: Receipts may contain sensitive data; store hashes/snippets, not full content, and enforce redaction in spoken summaries.
- depends on: Typed receipts and idempotency keys (partially exists via action receipts); A durable storage mechanism for the relay (Durable Object/D1/R2)


## What it asked for

_Nothing._
## Its own summary

Recorded three capabilities the owner cannot reliably have today: (1) spoken stop/pause that propagates across an in-flight Mac/browser operation with an exact partial receipt, (2) substrate-neutral migration and resume when the Mac or browser disappears, without replaying mutations or exporting secrets, and (3) a silent long-press pendant abort with immediate LED acknowledgement and eventual reconciliation. Each proposal names the existing routes/tools it can build from and the missing connective protocol or firmware work.

**Biggest unknown:** Whether any existing job runner already has hidden cancellation, checkpoint, lease, or migration semantics; the observed routes expose jobs and receipts, but no such cross-surface contract was established.

