# Harness derivation — relay-realtime — round 75

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If the connection gets choppy, keep my voice and your voice from talking over each other, and prioritize my speech getting through."
- **useful because:** The measured LTE-M link can drop packets when both sides speak at once. Prioritizing the owner’s uplink preserves intent and avoids frustrating interruptions.
- **path:** pendant → relay → unified → mac-bridge
- **model tier:** Realtime model for immediate conversational control; delegate any follow-on tasks to the Mac planner as usual.
- **latency:** Sub-second decisions during a live call; any follow-up action planning can take longer and be delegated.
- **cost:** Low per invocation; the dominant cost is realtime compute while the call is active, not backend API calls.
- **security:** Only uses call-level telemetry (packet loss, buffer fullness) and current speaking state; no need to inspect content beyond what’s already necessary for voice processing.
- **missing:** A standard congestion/speaking-state signal from the pendant to the relay; Relay logic to preempt or shorten TTS when uplink loss spikes; Optional Mac-side policy to request concise replies when the relay flags poor link quality

### "“Compare the latest contract in my open work portal with the copy in my Mac project folder. Tell me what changed, especially dates, amounts, and obligations, and cite where each difference came from.”"
- **useful because:** The owner can resolve discrepancies while away from the desk using only the pendant, instead of manually downloading, switching tabs, and visually comparing versions. It uniquely combines the pendant’s voice front door, the Mac’s private filesystem, and authenticated browser sessions; neither endpoint alone can establish which version is authoritative or explain the differences.
- **path:** pendant → relay → browser → mac-bridge → dashboard
- **model tier:** relay-realtime handles intent extraction and a short spoken summary; mac-planner performs the local-file discovery and structured extraction; browser harness reads the already-authenticated portal tab; a cheaper background comparison model computes a field-level diff and provenance bundle, then relay speaks only the answer. No computer-use vision model is required unless a source is image-only.
- **latency:** Acknowledge in under 500 ms, collect both sources and return a result in 10–30 seconds. If either source is unavailable, say which one and offer a partial comparison rather than blocking the owner.
- **cost:** Roughly $0.03–$0.15 per comparison, dominated by fetching/parsing two documents and the comparison model; relay usage is limited to intent and final spoken synthesis.
- **security:** Sensitive contract text leaves the Mac/browser surfaces only to the relay comparison service and is retained only as a short-lived encrypted result with source hashes, not full documents. Restrict browser reads to the explicitly selected tab and local reads to the named project folder; never transmit credentials. Because this is read-only, no confirmation is needed, but the spoken result must identify uncertainty and stale sources.
- **missing:** A cross-surface source resolver that can select a named authenticated browser tab and a Mac folder/file set from one request; A common document extraction schema (text, tables, dates, currency, obligations) with page/URL and local-path provenance; A short-lived comparison worker that returns field-level diffs and source hashes to the relay; A pendant-friendly disambiguation flow when multiple contracts or tabs match

### "“What did you change for me in the last hour, and what is still pending?”"
- **useful because:** The owner gets a trustworthy spoken audit across Mac actions, browser commands, and relay jobs without remembering which surface handled each request. It distinguishes completed, failed, and merely queued work, and points to the exact app/tab or receipt when follow-up is needed—especially valuable because the pendant is often used away from the Mac.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** A cheap background aggregator normalizes action receipts, browser command results, pipeline events, and job states into a chronological activity ledger; relay-realtime only filters the requested time window and speaks a concise answer. Use the dashboard for the detailed expandable evidence view.
- **latency:** Spoken acknowledgment under 300 ms and answer within 2 seconds for the recent ledger; older ranges may take 5 seconds. Degrade gracefully to 'known receipts only' when a surface has not checked in.
- **cost:** Under $0.01 for a recent-window query; storage/indexing dominates, not model inference. A small summarization call is used only when the result has many events.
- **security:** The ledger is private owner data and must be scoped to the paired pendant/session. Store immutable event metadata and redacted arguments by default, with encrypted payloads expiring quickly. Never infer success from a plan: report only terminal receipts or explicitly mark work as pending/unknown.
- **missing:** A durable cross-surface event envelope with correlation id, surface, human-readable action, state transitions, timestamps, and evidence links; Ingestion adapters for mac action receipts, browser result callbacks, relay jobs, and pipeline events; A reconciliation process that marks orphaned queued jobs and stale heartbeats as pending/unknown rather than complete; An owner-facing retention and redaction setting for the activity ledger

### "“Stop everything you’re doing for me right now, across the Mac and browser, and tell me what could not be stopped.”"
- **useful because:** A single spoken emergency stop is the only practical recovery when the owner is away from the Mac and a long plan is behaving unexpectedly. It coordinates relay jobs, Mac execution, and browser command queues, then gives an honest list of actions that already committed or cannot be interrupted.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** relay-realtime performs exact intent recognition and immediately dispatches cancellation; deterministic coordinators cancel queued work and send stop signals to Mac and browser. A cheaper background reconciler verifies terminal states and produces the final compact report; no expensive planning model is needed.
- **latency:** Dispatch stop signals within 300 ms of the utterance and speak acknowledgment immediately. Return verified per-surface results within 3 seconds, with late completions pushed as a follow-up notification.
- **cost:** Usually below $0.01, dominated by coordination/storage; no model call beyond the short relay turn.
- **security:** This is destructive to in-progress automation but not to owner data. Scope it to the paired owner and active session, use idempotent cancellation, and never claim a stop succeeded without a terminal callback. Already-committed mutations remain visible with receipts; cancellation itself must not delete audit history.
- **missing:** A first-class cancellation protocol understood by relay jobs, Mac planner/executor, and browser command queues; An active-work registry mapping owner/session to cancellable job and command IDs; Best-effort stop endpoints and terminal cancellation callbacks on Mac and browser surfaces; A follow-up notifier for work that races the stop request


## Changes it proposed to its own stack

### `relay` — Add a speaking-state and congestion-aware turn-taking controller in the relay. It monitors uplink packet loss and buffer health, and when the owner starts speaking or loss spikes, it suppresses or truncates TTS and asks downstream models to keep replies brief until the link stabilizes.
- **owner gets:** The owner’s words get through first. Fewer talk-overs, fewer dropped phrases, less frustration on a weak LTE-M connection.
- effort: Moderate: wire metrics from existing pipeline/audio events into a small state machine; add a brief-mode hint to downstream planning.  ·  risk: TTS could be cut too aggressively and feel abrupt. Recovery: fall back to current behavior if metrics are missing, and add a one-line audible cue when truncation happens.
- cost: Low. Uses existing telemetry and short control messages; no new heavy API calls.  ·  latency: Improves perceived latency by avoiding collisions; negligible processing overhead.
- security: Minimal; uses operational telemetry rather than sensitive content.
- depends on: A consistent telemetry event schema from the pendant firmware for packet loss/buffer fullness; Downstream support for a brief-mode hint (mac-planner and TTS)

### `relay` — Add a cross-surface activity ledger and reconciliation layer. Every plan, execution, Mac action, browser command, pipeline event, and callback is wrapped in one correlation id and normalized into queued/running/succeeded/failed/unknown transitions. Persist redacted metadata plus evidence pointers, ingest late callbacks idempotently, and expire sensitive payloads separately from durable status. A reconciler must never promote a plan to success merely because it was accepted; stale heartbeats become unknown and are surfaced as such.
- **owner gets:** When the owner asks the pendant what happened, they hear one honest account across all agents instead of a collection of partial job lists. They can tell whether something actually changed, what still needs attention, and where to resume without returning to the Mac.
- effort: Medium: define an event envelope and schema, add adapters at existing route boundaries, implement idempotent storage and a small reconciliation worker, then expose a time-window query for relay and dashboard.  ·  risk: Duplicate or out-of-order callbacks could produce misleading state; use monotonic transition rules, correlation IDs, and an audit trail. If the ledger is unavailable, existing execution continues and the relay explicitly reports that history is incomplete. Recovery is replay from retained route events and receipts.
- cost: Small persistent storage and indexing cost; roughly a few KB of metadata per action. No meaningful per-request model cost; aggregation can be deterministic.  ·  latency: Negligible write overhead (<100 ms target). Recent queries should be sub-second; reconciliation can be asynchronous.
- security: Creates a concentrated activity record. Encrypt at rest, redact command arguments and document contents, scope reads to the paired owner, apply short retention to evidence, and log ledger access.
- depends on: Stable correlation IDs shared by /plan, /execute, browser command/result callbacks, Mac action receipts, and pipeline events; A durable worker or alarm mechanism for stale-job reconciliation (currently absent); A read route/tool that returns normalized activity for the relay and dashboard


## What it asked for

_Nothing._
## Its own summary

Recorded three non-duplicate proposals: cross-surface contract discrepancy comparison, a reconciled activity ledger for truthful 'what happened?' answers, and a spoken cross-surface emergency stop. The required changes are source resolution/document provenance, durable event normalization and reconciliation, and idempotent cancellation with active-work tracking and late-result notification.

**Biggest unknown:** Whether the existing Mac/browser callback implementations expose enough stable correlation IDs and cancellation hooks to connect these surfaces without changing their execution contracts.

