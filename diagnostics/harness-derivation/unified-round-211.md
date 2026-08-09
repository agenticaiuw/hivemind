# Harness derivation — unified — round 211

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Pick up the conversation we were having before the connection dropped, without making me repeat myself.”"
- **useful because:** A dropped LTE/WebSocket turn currently loses continuity even though Mac work has handoff primitives. This makes the wearable feel dependable: it resumes from the last confirmed spoken/listened boundary, not from a guessed transcript, and never repeats an action or audio.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime only for the resumed conversational reply; a cheap background model compacts the durable turn journal and extracts unresolved references.
- **latency:** On reconnect, 1–2 s to load the last turn capsule; under 500 ms for the relay to decide whether it is safe to resume. No background compaction on the speech critical path.
- **cost:** About $0.001–$0.01 per reconnect depending on transcript length; storage and receipt writes dominate less than model tokens.
- **security:** Persist only redacted transcript excerpts, turn IDs, delivery/playback receipts, and pending intent—not raw audio. The relay must require the same session/device binding, honor the privacy latch, and mark uncertain boundaries as “ask me to repeat.” Browser pages are never copied into the capsule. Resuming an action requires the existing replaySafety/riskTier policy and physical approval for staged writes.
- **missing:** A durable voice-turn capsule schema with uplink/downlink sequence boundaries and audio_delivery_ack_queue integration; Relay persistence and expiry for turn capsules; A reconnect route that returns the last confirmed boundary and unresolved references; A policy/UI for showing the owner exactly what will be resumed

### "“Fill out this form, but show me exactly what will be submitted and wait for my deliberate approval on the pendant.”"
- **useful because:** This closes the currently broken promise that blocked plans can wait for approval. The owner gets a concrete, reviewable form submission rather than a browser action that silently stalls or executes with the wrong fields.
- **path:** browser-extension → relay-realtime → pendant → mac-planner → dashboard
- **model tier:** Background/planner model extracts fields and produces the summary; realtime speaks the concise diff; deterministic executor submits only the approved digest.
- **latency:** Stage in 2–5 s, approval response within one conversation/physical gesture, submission and receipt within 5 s after approval.
- **cost:** Roughly $0.01–$0.05 per staged form depending on page complexity; browser inspection and screenshot transfer dominate.
- **security:** Never send secrets/page contents to the pendant. Bind approval to plan digest, world fingerprint, expiry, and physical transaction nonce; reject changed pages, expired approvals, duplicate nonce, and approval without delivered spoken summary. Keep the shared AGENT_TOKEN limitation explicit until authorization is separated.
- **missing:** Relay implementation of APPROVAL_STORE_CONTRACT and delivery/readback tracking; A bridge from browser result to /prepare and from physical approval event to /approve; A real dashboard/pending-approval view and owner-visible diff; A least-privilege browser submission action with field-level redaction

### "“Run a complete audio check now and tell me whether the pendant, relay, and bridge are healthy before I start a conversation.”"
- **useful because:** It turns the shipped 24 kHz path and its known failure modes into an owner-facing answer instead of raw counters: a single deliberate check identifies codec overload, packet loss, jitter, clipping, frame discontinuity, and bridge safety before the owner speaks.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** Deterministic checks and a cheap background classifier; realtime only summarizes the verdict to the owner.
- **latency:** 30–60 s for the complete test, with a progress indication; never run automatically during a live conversation.
- **cost:** Under $0.01 per run; test audio, relay probes, and artifact retention dominate, not inference.
- **security:** Use synthetic fixtures only, never record room audio. Store redacted counters and hashes, expire artifacts quickly, and require explicit confirmation before any repair that changes firmware, link profile, or queued jobs.
- **missing:** A single orchestration route joining the granted validator and fault-injector results with pendant/bridge acknowledgements; A compact HEALTHY/DEGRADED/FAILED contract with actionable owner language; A manual trigger exposed through the pendant inbox or dashboard; Bridge-side acknowledgement correlation and a signed test receipt

### "“Make the last five minutes private now: remove anything captured during that window from every place it could have landed, and prove what was removed.”"
- **useful because:** The physical privacy latch stops future capture, but it does not provide a bounded retroactive purge of already-created relay rows, transcripts, browser exposure, queued jobs, or failure-buffer artifacts. The owner needs a single emergency action that converts the latch event into an auditable, cross-surface deletion request.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic deletion and receipt correlation; no model required except optional background classification of which derived text belongs to the bounded interval.
- **latency:** Local stop is immediate; issue deletion requests within 2 seconds and report pending off-machine deletion separately. Never claim completion before each surface responds.
- **cost:** Under $0.01 per purge; off-machine replication and receipt polling dominate.
- **security:** Require a locally authenticated latch event, monotonic time bounds, and a conservative inclusion rule. Never delete audit history or unrelated owner-created reminders. Preserve a tamper-evident deletion receipt while deleting the content. Off-machine copies must be reported as requested/pending until confirmed.
- **missing:** A latch-scoped deletion transaction spanning relay, Mac, browser, and pendant outbox/inbox; Interval and provenance indexes linking derived transcripts/captures to their source event; A deletion receipt that distinguishes completed, pending, and impossible surfaces; A clear owner setting for the default retroactive window

### "“Give me one answer assembled from my private browser session, Mac files, and our conversation, and show me which source supports every important claim.”"
- **useful because:** Today the system can reach these surfaces independently, but the owner cannot reliably tell whether an answer came from a browser page, a Mac artifact, remembered context, or model inference. A provenance-bound answer would make private-session access useful without turning the model's synthesis into an unverifiable assertion.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Background planner retrieves and normalizes bounded evidence; a cheaper synthesis model drafts; realtime only delivers the final concise answer and provenance summary.
- **latency:** 3–8 seconds for a bounded query; stream “searching browser / Mac / conversation” status without exposing contents prematurely.
- **cost:** Approximately $0.02–$0.10 for multi-source retrieval and synthesis; browser inspection and context size dominate.
- **security:** Every source must be explicitly bound to a tab, app, path, or session. Do not merge secrets across unrelated contexts. Return citations as opaque source IDs and snippets, redact credentials, and require confirmation before any answer-derived action.
- **missing:** A cross-surface evidence envelope with source IDs, timestamps, hashes, and redaction state; A retrieval policy that separates observed evidence from model inference; A provenance renderer usable over 24 kHz speech and the dashboard; A refusal mode when sources conflict or a browser binding is stale

### "“Let me give you a task with a spending, time, and authority limit; stop automatically when any limit is reached and tell me exactly why.”"
- **useful because:** The current action risk and approval machinery evaluates individual plans, but the owner cannot express a bounded autonomy contract across a multi-step job. A hard envelope would make delegation safer: the system can work unattended only within explicit limits and must stop rather than improvise when the budget or authority boundary is crossed.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → dashboard
- **model tier:** Deterministic policy engine enforces limits; background planner decomposes work; realtime is used only for initial confirmation and stop notifications.
- **latency:** Enforcement must be synchronous before every action; status updates under 1 second after a boundary is reached.
- **cost:** Low inference overhead; roughly $0.01–$0.05 for planning a bounded job, with browser/Mac execution dominating.
- **security:** Limits must be immutable for the active job and included in the plan digest. Track cumulative actions, elapsed time, monetary estimates, touched domains, and approval scope. Physical approval is required when crossing a risk tier; stopping must be fail-closed if accounting or relay state is unavailable.
- **missing:** A durable autonomy-envelope schema and per-step counter; Executor hooks that atomically check the envelope before dispatch; A pendant-visible stopped/awaiting-approval state and signed stop receipt; A policy for estimating money and authority when an action's cost is unknown


## What it asked for

_Nothing._
