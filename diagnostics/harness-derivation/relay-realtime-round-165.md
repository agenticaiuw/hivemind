# Harness derivation — relay-realtime — round 165

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Use the pendant through my Mac over USB if cellular isn’t registered."
- **useful because:** It makes the system dependable today: the owner can test and use the pendant even without LTE registration.
- **path:** pendant → mac-bridge → relay
- **model tier:** Realtime for conversation, with the Mac acting as the transport owner when tethered.
- **latency:** Interactive; audio should feel live.
- **cost:** Mostly local; cloud cost is the relay session and transcription.
- **security:** USB tether must establish authenticated session epochs to prevent replay; strict ownership of serial ports to avoid double writers.
- **missing:** Serial gateway ownership and session epoch protocol; Typed INBOX/OUTBOX acknowledgements across USB; Relay awareness of tethered mode vs LTE mode

### "Tell me what you’re doing right now, briefly."
- **useful because:** A quick status reduces anxiety and prevents duplicate commands; it’s a wearable-friendly transparency feature.
- **path:** relay → mac-bridge → browser
- **model tier:** Realtime to summarize what’s already known; no heavy planning.
- **latency:** Under a second.
- **cost:** Very low; read-only status aggregation.
- **security:** Status must be privacy-aware and avoid reading sensitive content unnecessarily.
- **missing:** A relay-level capability inventory/status endpoint; Cross-surface task aggregation into one concise spoken line

### "“What changed since I last checked?” — compare the last known state of my Mac, open browser work, and pendant conversations, then tell me only the meaningful changes and act on any I explicitly ask for."
- **useful because:** The owner can recover from being away without manually reconstructing what happened. It turns the wearable into a continuity surface across the Mac, authenticated browser, and relay rather than another isolated assistant.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Background/state-diff model for snapshots; relay-realtime only compresses the resulting diff into speech and handles follow-up.
- **latency:** First spoken summary under 3 seconds from cached snapshots; a fresh Mac/browser refresh may take up to 15 seconds.
- **cost:** ~$0.01–$0.05 per refresh depending on page and screenshot volume; storage and diff computation dominate, not realtime speech.
- **security:** Snapshots may contain private browser pages, window titles, and document text. Keep raw snapshots on the Mac/relay encrypted, send only selected diffs to the realtime model, and expose source labels and timestamps in the spoken response. No mutation should be inferred from a change.
- **missing:** A durable, redacted cross-surface snapshot store with per-source timestamps and hashes; Mac agent hooks for filesystem/app/browser state snapshots; Browser extension export of authenticated tab metadata and selected page diffs; A temporal diff/ranking service and a pendant query verb

### "“Find the disagreement and tell me which one is current.” Given a claim that appears in my browser, Mac files, calendar, or previous assistant records, locate conflicting values, explain the conflict in one sentence, and identify the freshest evidence without changing anything."
- **useful because:** The owner often needs truth, not an action: deadlines, addresses, prices, and settings drift across sources. Today each surface can be queried separately, so the assistant can confidently repeat stale information.
- **path:** pendant → relay → faculty-perception → mac-planner → browser-extension → dashboard
- **model tier:** Faculty-perception performs extraction, normalization, timestamp comparison, and contradiction detection; relay-realtime only asks a narrowly targeted follow-up when ambiguity is irreducible.
- **latency:** Return a cached contradiction in 2 seconds; live authenticated-source checks may take 10–20 seconds.
- **cost:** ~$0.02–$0.10 per live investigation, dominated by page/file extraction and long-context comparison.
- **security:** Read-only access still exposes sensitive documents and authenticated pages. Use source-scoped retrieval, retain excerpts rather than whole pages, encrypt evidence, and speak only the minimum necessary text. Never silently resolve a conflict by editing a source.
- **missing:** A common claim/evidence schema with source URI, observed_at, effective_at, and confidence; Parallel read-only fan-out across Mac files/apps and authenticated browser tabs; A contradiction classifier that distinguishes revisions from genuine conflicts; Cited spoken answers and a browsable evidence view

### "“Make this a reusable handoff.” While I am away from my Mac, turn my spoken request plus the current browser/Mac context into a compact task packet another person or agent can continue: goal, constraints, evidence, attempted steps, and the exact next action."
- **useful because:** A voice request should not evaporate when the session ends or become an opaque job. This lets the owner hand work between the pendant, Mac planner, browser session, and a human while preserving context and avoiding repeated explanation.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** A cheaper background model assembles and redacts the packet; relay-realtime confirms the one-line summary; mac-planner/mac-vision append machine-observed steps and results.
- **latency:** Draft packet in under 5 seconds; append later observations asynchronously.
- **cost:** ~$0.01–$0.04 per packet; token cost is dominated by included evidence, so default to structured fields and short excerpts.
- **security:** Packets can become portable copies of private work. Apply source labels, configurable expiry, recipient scoping, encryption, and explicit redaction of secrets/tokens. Do not include browser cookies or raw credentials.
- **missing:** A durable handoff object and lifecycle (draft, active, blocked, completed, expired); A shared typed event log from relay, Mac planner, computer-use, and browser extension; Redaction/secret detection before export; A dashboard and pendant verb for retrieving, speaking, and resuming a handoff

### "“Why did you tell me that?” Replay the exact evidence, timestamps, and transformations behind the last spoken answer, and say what could make it wrong; if the evidence has changed, offer the corrected answer."
- **useful because:** A wearable answer is easy to trust and hard to inspect. This gives the owner a fast way to audit an important answer without hunting through Mac logs, browser tabs, or voice history.
- **path:** pendant → relay → faculty-perception → faculty-judgement → mac-planner → browser-extension → dashboard
- **model tier:** A background provenance builder records typed evidence and transformations; relay-realtime renders a short explanation and can fetch one missing source on demand.
- **latency:** Audit cached answers in 2 seconds; source revalidation within 15 seconds.
- **cost:** ~$0.01–$0.06 per audit; most cost is optional source revalidation and evidence retention.
- **security:** Provenance can reveal private source names and excerpts. Store immutable hashes plus minimal excerpts, redact secrets, enforce per-owner retention, and never claim a source was consulted unless its receipt exists.
- **missing:** A provenance receipt attached to every answer-producing pipeline run; Typed transformation and source citations across relay, Mac, and browser; A compact audit renderer for speech and dashboard; A revalidation operation that does not mutate source systems

### "“Keep me in the loop while you work, but only when something meaningful happens.” For a long Mac/browser task, send the pendant sparse milestone updates, distinguish waiting from failure, and let me ask for the current step or cancel/resume from voice."
- **useful because:** Today a queued task is either silent or requires polling. The owner can walk away and still know whether work is progressing, blocked, or finished without hearing noisy progress narration.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Background event classifier consumes typed action receipts; relay-realtime handles only the owner’s spoken query and short notification wording.
- **latency:** Milestone notification within 2 seconds of a state transition; spoken status query under 1 second from cached state.
- **cost:** ~$0.005–$0.03 per task, mostly event storage and occasional summarization; no realtime model call for routine milestones.
- **security:** Notifications may expose sensitive task names in public spaces. Support private/neutral wording, source-scoped event payloads, expiry, and no raw page contents in push events. Cancellation must identify the exact job.
- **missing:** A durable event stream with deduplication and milestone semantics; A real job runner that emits progress and supports pause/cancel/resume; Pendant delivery acknowledgement and offline expiry policy; Voice commands mapped to a specific job rather than a vague session


## Changes it proposed to its own stack

### `relay` — Publish a relay capability manifest endpoint (like the Mac’s /capabilities) so relay-realtime can inventory its own routes/tools instead of probing blind.
- **owner gets:** Fewer failures and faster responses when the wearable asks for help, because the relay knows what it can actually do.
- effort: Medium: add an endpoint and keep it in sync with routing.  ·  risk: Low; mainly consistency drift. Mitigate with tests that assert manifest matches router.
- cost: Minimal runtime cost.  ·  latency: Improves responsiveness by reducing failed probes.
- security: Must avoid exposing secrets; publish only public names and schemas.

### `integration` — Implement durable job tracking with completion notification mapping: plan/execute jobs persist, completion emits a notification event that routes to the existing inbox queue for the pendant.
- **owner gets:** Lets the owner fire-and-forget tasks and get a spoken completion later.
- effort: High: needs durable storage and delivery receipts.  ·  risk: Medium: wrong status mapping could mislead. Mitigate with strict status wording and receipts.
- cost: Moderate; storage and event delivery.  ·  latency: No impact on interactive speech; completion events are asynchronous.
- security: Notifications must be scoped to the owner and avoid leaking sensitive content.


## What it asked for

_Nothing._
## Its own summary

Recorded five owner-facing capabilities: cross-surface change recovery, contradiction resolution, reusable task handoffs, provenance/audit replay, and sparse meaningful progress updates. The strongest gap is not another action primitive: it is a trustworthy shared evidence/event layer that lets the pendant explain what changed, why it believes an answer, and what a remote Mac/browser job is actually doing. The owner still needs durable cross-surface snapshots, typed provenance and job events, source-scoped redaction, and a real long-running runner with pause/cancel/resume plus pendant delivery.

**Biggest unknown:** Whether the existing /ops/history and /ops/memory routes already retain enough typed source receipts to support provenance and temporal diffs; no further discovery was permitted this round.

