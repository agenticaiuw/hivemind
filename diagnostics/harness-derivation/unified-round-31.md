# Harness derivation — unified — round 31

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Pause this and remind me where we left off when I’m ready.” Then, on the next pendant interaction, “Continue.”"
- **useful because:** Today ending a conversation loses the live task’s working set, while background jobs and receipts only cover work that has already completed. This would make the pendant, always-on relay, Mac, and private browser act as one interruptible assistant: safely checkpoint an in-progress plan, preserve exactly what was inspected or drafted, and resume without repeating work or accidentally submitting anything.
- **path:** pendant → relay → mac-bridge → browser → dashboard-ux
- **model tier:** Use the realtime model only to interpret the short pause/continue utterance and explain the checkpoint. Use a cheaper background model/local planner to serialize the plan and summarize deltas; browser and Mac agents execute only after explicit resume and existing risk gates.
- **latency:** A pause acknowledgement should be under 500 ms locally/relay-side and checkpoint within 3 s. Resume should speak a 10-second delta within 2 s, then wait for confirmation before any external or irreversible action.
- **cost:** About $0.01–$0.05 per pause/resume depending on summary length; dominant cost is one background summarization call. Most resumes should be zero-model-cost if the checkpoint is already typed and unchanged.
- **security:** Checkpoint may contain private tab titles, drafts, and page snippets. Encrypt at rest, bind it to the owner/session, apply a short TTL, and redact secrets/form values by default. Never replay a stale browser mutation: revalidate tab URL, page fingerprint, permissions, and before-values on resume; require confirmation for sends, purchases, deletes, or submissions.
- **missing:** A first-class interrupt checkpoint schema with plan-step status, browser tab/session handles, Mac window/app state, evidence hashes, and expiry; A relay endpoint and durable lease protocol for pause/resume, including crash recovery and exactly-once checkpoint writes; Mac/browser adapters that can capture and revalidate state without mutating it; Pendant firmware event semantics for an explicit pause gesture/short utterance distinct from ending a call; Dashboard and spoken receipt showing checkpoint age, sensitive fields retained, and discard/resume controls

### "“When I walk away, protect my open work; when I come back, restore exactly what I was doing.”"
- **useful because:** The owner cannot currently leave a desk safely while authenticated browser tabs, drafts, meetings, and sensitive Mac windows remain exposed. A worn pendant can act as a continuous presence signal: leaving would trigger a privacy perimeter and safe suspension, while returning would restore the working set without losing drafts or task position. This is a new physical affordance that no Mac-only or browser-only agent can provide.
- **path:** pendant → relay → mac-bridge → browser → iOS → dashboard-ux
- **model tier:** Use deterministic firmware/relay rules for presence, locking, redaction, and restoration. Use a cheap background model only to summarize what was suspended and prepare a spoken return brief; realtime is needed only if the owner asks questions after returning.
- **latency:** Detect departure and issue protective actions within 2 seconds, subject to OS lock APIs. On return, restore the safe workspace within 5 seconds and speak a compact status; never delay protection for model inference.
- **cost:** Near-zero per event beyond relay storage and device traffic; optional background summary costs under $0.01 per departure/return. Hardware cost depends on adding BLE/UWB presence support, roughly $3–$15 in components and under 50 mW average for a production pendant.
- **security:** A presence signal must not be treated as identity by itself. Require a cryptographic pendant pairing, proximity threshold, optional voice/PIN confirmation for unlocking, and immediate revocation on loss/theft. Lock or blur private browser tabs, stop microphone streaming, and never transmit page content merely to determine presence. Keep an audit trail and provide a physical emergency lock gesture.
- **missing:** A production pendant presence radio and authenticated proximity protocol (BLE is a minimum; UWB gives safer distance bounds); Mac bridge APIs for lock, window privacy/redaction, microphone/audio suspension, and exact workspace restoration; Browser extension/bridge support to hide or freeze private tabs without closing sessions, preserving drafts safely; Relay presence state machine with hysteresis, offline behavior, theft/loss timeout, and signed device pairing; Owner-configurable privacy policies and a dashboard audit/recovery flow


## Changes it proposed to its own stack

### `relay` — Add an Interrupt Checkpoint Protocol: POST /v1/tasks/:id/pause atomically records a versioned, encrypted checkpoint containing intent, step DAG/status, lease owner, Mac app/window identity, browser session/tab IDs, evidence hashes, pending mutations, sensitivity labels, and expiry; POST /resume returns a revalidation plan rather than executing. The Mac/browser bridges must answer read-only state probes, and the relay marks each step stale when URL, DOM fingerprint, app identity, or before-value changed. Resume leases are single-use and idempotent, with an append-only pause/resume receipt and discard endpoint.
- **owner gets:** They can stop a task when interrupted, disconnected, or uncertain and later pick up from the exact safe point instead of repeating research or risking a stale form submission. The pendant becomes a reliable “bookmark for action,” not merely a voice call button.
- effort: Medium-large: relay schema/API and encrypted storage, bridge read-only probes, dashboard controls, voice intents, and crash/reconnect tests. Start with read/draft-only workflows before mutation-capable workflows.  ·  risk: A stale or incomplete checkpoint could cause duplicated work or unsafe replay. Mitigate with step-level idempotency keys, mandatory revalidation, conservative invalidation, explicit approval after any changed evidence, and a discard/recovery path. If the relay crashes, the durable checkpoint remains resumable but no action is auto-replayed.
- cost: Negligible storage and relay compute per checkpoint; roughly 2–10 KB metadata plus selected redacted snippets. One cheap background summarization call is optional; no realtime call is needed after the initial utterance.  ·  latency: Pause acknowledgement can be immediate; durable write target under 3 seconds. Resume adds a few seconds for Mac/browser state probes, but avoids redoing the full task.
- security: High-value private state crosses relay storage. Encrypt checkpoint payloads, minimize/redact fields, short TTL, owner/session ACL, and audit every read/resume/discard. Never persist passwords, tokens, or raw form secrets.
- depends on: A typed shared context/checkpoint schema instead of hand-written fleetContext sections; Reliable browser request IDs and tab/session affinity; Mac bridge read-only state inspection and action receipts; A durable job/lease runner or equivalent atomic task store; Pendant pause/resume intent and spoken confirmation semantics


## What it asked for

### `s5-9vta` (skill) — task_checkpoint_gesture
- does: Recognizes a deliberate long-press (for example 1.5–2 s) as “pause/checkpoint the current task,” distinct from the existing short press start/end conversation behavior. It locally emits a compact checkpoint-request event with monotonic timestamp, call/task nonce, and gesture confidence; LED gives a distinct acknowledgement or error flash. It must not execute browser/Mac actions or store sensitive content.
- must be on-device because: The gesture must still be captured when LTE is congested, audio is duplex-saturated, or the call drops. Local acknowledgement prevents the owner from wondering whether a pause was registered; the relay can persist the actual private checkpoint once connectivity returns.
- trigger: Physical button long-press; server push is not required. A short press retains current start/end semantics.
- storage: Persist only a small last-event record and monotonic sequence in existing flash/settings (well under 256 B); do not persist audio, transcripts, or task contents.
- RAM budget: Approximately 2–4 KB for debounce/timing state, event serialization, and a tiny reconnect queue; comfortably below the 211,608 B application RAM budget, subject to existing audio buffers.

## Its own summary

Discovered the current fleet still has the Mac bridge online but the browser device offline, and the pendant has only one button/LED with LTE-M duplex contention. I added a genuinely new cross-surface capability: interruptible task checkpoints (“Pause this” / “Continue”), plus a relay Interrupt Checkpoint Protocol with encrypted, versioned step state, leases, evidence revalidation, and no automatic replay of stale mutations. I also queued a pendant-local long-press checkpoint gesture so pausing remains reliable during link loss. Sent the gap to faculty-judgement.

**Biggest unknown:** The remaining implementation contract: which existing task/job schema and browser/Mac read-only state probes can become the checkpoint substrate, and the production pendant’s button/feedback semantics. The pending grants for workspace editing, audio validation, incident/offline skills, and fleet health are still not visible in the granted category.

