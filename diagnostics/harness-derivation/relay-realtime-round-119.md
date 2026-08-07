# Harness derivation — relay-realtime — round 119

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If that’s still running, what’s the status of the thing I asked you to do?"
- **useful because:** The owner gets a simple, trustworthy answer while on the go, even when the Mac is asleep. It prevents duplicate requests and reduces anxiety about whether anything is actually happening.
- **path:** pendant → relay → mac-bridge
- **model tier:** realtime for the spoken prompt; cheaper background reads for job record retrieval
- **latency:** Under a second for common cases; status should be stored and readable at the relay without waiting for the Mac.
- **cost:** Very low per invocation. Mostly a single read from a relay-side job record store.
- **security:** Job descriptions can contain sensitive text. Store minimal metadata, redact details in the spoken response, and enforce retention limits.
- **missing:** Relay-side durable job record store with retention policy; Implemented relay_job_status tool bound to that store; Receipts from downstream actions consistently written back to the relay

### "When I interrupt the pendant while it is speaking—'stop', a correction, or a new request—it should stop at once, preserve the unfinished sentence and task state, then continue or answer the correction without replaying itself or losing the Mac/browser work already underway."
- **useful because:** Today a spoken answer competing with the owner's next thought forces them to wait, repeat themselves, or accidentally launch a second task. This gives a worn, one-button device natural barge-in while keeping downstream work coherent across an unattended Mac and authenticated browser.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime relay model for turn-taking, interruption classification, and a compact resumable speech checkpoint; use the cheaper planner/background tiers for the already-running Mac/browser work. Do not spend realtime tokens regenerating unchanged task context.
- **latency:** Mute playback and acknowledge the interruption locally in under 150 ms; classify the new utterance and speak a response in under 900 ms when possible. Resumption should be explicit and never replay more than the last incomplete semantic clause.
- **cost:** Small incremental realtime cost per barge-in (classification plus a short checkpoint, roughly a fraction of a normal turn); durable checkpoint storage and event plumbing dominate engineering cost, not inference.
- **security:** The checkpoint may contain private speech and authenticated-tab task references, so retain it only for the active session, encrypt it in transit and at rest, and expose an owner-visible clear action. Never treat an interruption as cancellation of an external mutation unless the downstream job receives an explicit cancel intent.
- **missing:** Pendant-side playback-ducking/barging-in signal with sentence-boundary marker (not merely a button event); Relay duplex session state that stores an audio cursor plus task/job correlation and accepts a new utterance while a response is streaming; A downstream correlation contract so Mac/browser jobs continue once while relay conversation can pause, revise, or resume them; TTS streaming metadata identifying safe semantic pause points and a resume endpoint; Dashboard inspection of interrupted/resumed turns and a manual discard-checkpoint control

### "Let me refer back to anything the pendant just said by voice—'repeat the second option', 'what source supported that?', 'use the link you mentioned'—and have it retrieve the exact spoken segment and its Mac/browser receipt instead of making me repeat the whole request."
- **useful because:** A wearable has no screen or transcript to point at. Exact verbal references are essential when the owner is walking or driving, and they prevent duplicate searches/actions caused by vague follow-up questions. It also makes the hive explainable: an answer can be tied to the browser page, Mac action, or receipt that produced it.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime model resolves the short reference against a compact rolling segment index; use no new model call when the reference is unambiguous, and use a cheaper background model only to build citations for long results.
- **latency:** Resolve a recent segment in under 500 ms and begin playback within 1 s. Keep only a rolling spoken index so normal turns do not gain context-token cost.
- **cost:** Negligible inference for indexed exact references; occasional small citation-extraction call for a long Mac/browser result. Storage and event correlation are the main cost.
- **security:** Segment indexes and citations can reveal private tab titles, files, or speech. Encrypt them, scope them to the paired session, expire them promptly, and redact secrets from spoken citations. Do not expose an authenticated URL aloud unless the owner explicitly asks.
- **missing:** A relay-side turn ledger assigning stable segment IDs to streamed speech, transcript, and downstream job IDs; Typed provenance links from Mac/browser results and receipts back to the segment that announced them; A low-bandwidth pendant command for replay/reroute without resending the complete conversation; Dashboard view for inspecting and deleting the rolling spoken index

### "After the pendant loses LTE and reconnects, tell me exactly what was heard, what was merely planned, what the Mac/browser actually changed, and what remains unknown—then let me say 'continue' or 'discard' without accidentally running a duplicated action."
- **useful because:** A worn LTE device will inevitably cross dead zones. Today silence leaves the owner guessing whether a request happened, which is especially dangerous for actions spanning a Mac and an authenticated browser. A compact reconciliation makes recovery safe and comprehensible without requiring the owner to inspect a dashboard.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use deterministic event/receipt reconciliation first; realtime model only verbalizes the resulting state and resolves 'continue/discard'. Use a cheaper background model for compressing older history.
- **latency:** On reconnect, local acknowledgement under 200 ms and a spoken three-state summary within 2 s. No replay of full transcripts or action payloads.
- **cost:** Low per reconnect: mostly durable event reads and a short spoken summary; engineering cost is an idempotent reconciliation protocol and pendant reconnect handling.
- **security:** Do not replay secrets, authenticated URLs, or raw command arguments over audio. Bind reconciliation to the paired device/session, encrypt pending summaries, expire them after acknowledgement, and distinguish 'unknown' from 'failed' rather than guessing.
- **missing:** A durable per-request event ledger shared by relay, Mac planner, Mac vision, and browser command queue with monotonic sequence numbers; Idempotency keys propagated from the spoken request through /plan, /execute, Mac actions, and browser actions; A reconnect handshake that reports the last pendant sequence received and requests only the missing state delta; A compact typed outcome vocabulary (heard/planned/started/completed/failed/unknown/cancelled) exposed to the pendant; Owner controls to continue or discard an unresolved request without creating a fresh duplicate

### "Let me say 'off the record' before or during a pendant conversation, so that request is handled across the relay, Mac, and authenticated browser but leaves no transcript, memory, briefing item, browser inspection, or dashboard history after it finishes."
- **useful because:** The owner may need help with sensitive work while wearing the device, but a permanently logged voice assistant is not appropriate for every thought. Today there is no single privacy control spanning the relay, downstream jobs, browser session evidence, and receipts; deleting pieces afterward is unreliable.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime model handles the short mode transition and confirmation; all downstream work remains on the normal appropriate tier. No model should summarize or retain the private turn.
- **latency:** Enter private mode on the next utterance and acknowledge in under 300 ms. Suppression/deletion must complete before the relay reports the mode ended; otherwise it must say what could not be erased.
- **cost:** Negligible inference cost; implementation cost is propagation of a retention label, deletion guarantees, and audit tests across every persistence sink.
- **security:** This is a privacy promise, so failure must be explicit rather than silently claiming deletion. Encrypt transient buffers, prevent sensitive text from provider logs where configurable, mark downstream jobs non-retainable, scrub browser screenshots/receipts, and provide a local LED pattern indicating private mode. External mutations still happen; privacy mode must not imply cancellation or safety.
- **missing:** A session-scoped retention/consent label propagated from pendant audio through relay, planner, Mac actions, browser commands, receipts, and logs; A deletion coordinator with per-sink acknowledgements and a truthful incomplete-deletion report; Provider and Worker logging controls that can omit raw audio/transcript for marked turns; Pendant firmware state and LED indication for private mode, including behavior after LTE reconnect; A dashboard privacy ledger showing only deletion status and no sensitive content


## Changes it proposed to its own stack

### `relay` — Implement the granted relay_route_intent and relay_job_status schemas as real, minimal endpoints in the relay Worker. relay_route_intent should accept an intent label, the utterance, and a target surface, then forward to the correct downstream tool (mac_run_actions, browser_run_actions, mac_delegate, or a future server-side browser runner) without bespoke ad hoc routing logic. relay_job_status should read a durable job record store owned by the relay (Durable Object or KV) and return a concise spoken status plus machine fields.
- **owner gets:** The owner can say what they want, and the relay can route it reliably and tell them what happened later, even if the Mac is asleep. It reduces confusion, repeated requests, and accidental duplicate work.
- effort: Medium. Needs a small routing layer, a durable job store, and integration tests for intent mapping and status reads.  ·  risk: Routing mistakes could send an action to the wrong surface. Mitigate with typed intent mapping, idempotency keys, and receipts. Status could expose sensitive task details; restrict stored fields and encrypt at rest if needed.
- cost: Low per request. Main cost is storage reads/writes for job records and occasional downstream tool calls. Implementation cost is moderate engineering time.  ·  latency: Improves perceived latency by avoiding unnecessary Mac round trips for status. Routing adds a small constant overhead.
- security: Job records contain potentially sensitive text. Store minimal data, apply retention limits, and avoid logging full utterances by default.
- depends on: A durable store for job records (Durable Object or KV); An intent-to-tool mapping table with typed parameters; Receipt storage for downstream work

### `interaction` — Add a spoken interruption protocol: when the owner interrupts mid-task, the relay should capture a short 'interruption intent' (e.g., stop, pause, ask status, change plan) and route it to the right place. The Mac side should be able to mark the job as paused/cancelled or adjust the plan, and the relay should confirm with a brief spoken acknowledgement.
- **owner gets:** Pendant interactions are conversational and messy. A clear interruption model prevents accidental continuation, makes stopping safer, and gives the owner confidence they’re in control.
- effort: Medium. Requires small protocol changes, UI/voice phrasing, and job-state support for pause/cancel on the Mac agent.  ·  risk: If pause/cancel is misrouted, work may continue unexpectedly. Mitigate with explicit job IDs in confirmations and idempotent cancel operations.
- cost: Low. Mostly state updates and a small amount of extra logic.  ·  latency: Very small overhead; improves perceived responsiveness by handling interruptions immediately at the relay.
- security: Minimal, but job control messages should be authenticated and auditable.
- depends on: relay_route_intent implementation; Job state machine supporting pause/cancel; Reliable receipts for state transitions


## What it asked for

_Nothing._
## Its own summary

Recorded four owner-facing capabilities: interruption-safe duplex speech with resumable task state; voice refer-back to exact spoken segments and Mac/browser provenance; LTE reconnect reconciliation that distinguishes heard/planned/completed/unknown and prevents duplicate actions; and an explicit off-the-record mode spanning pendant, relay, Mac, browser, receipts, logs, and memory. Each proposal names the missing cross-node contracts rather than assuming current routes are sufficient.

**Biggest unknown:** Whether the relay's existing production persistence and provider logging can actually suppress or delete raw audio/transcripts per request; that must be verified before promising the off-the-record mode.

