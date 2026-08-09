# Harness derivation — mac-planner — round 233

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“When I press the bookmark button, remember what I was doing across my Mac and browser; later, when I ask ‘what was that?’, tell me and reopen the exact context.”"
- **useful because:** The shipped pendant bookmark records only a local event. Pairing it with the live Mac foreground/app state, browser tabs, and a durable relay record turns a fleeting button press into reliable continuity: the owner can leave a thought, return hours later, hear a one-sentence reminder, and resume without reconstructing the context.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Use deterministic capture for timestamp, app, URL, tab title, file paths, and job IDs. Use a cheap background model only to produce the optional one-sentence label; realtime is reserved for the later spoken lookup.
- **latency:** A bookmark acknowledgement must be local/immediate; Mac/browser snapshot within 2 seconds. A later lookup should speak within 3 seconds and reopen context within 5 seconds.
- **cost:** About $0.001–$0.01 per bookmark, dominated by optional labeling; raw metadata capture and deduplicated storage are negligible.
- **security:** Never persist page bodies, passwords, cookies, or typed secrets by default. Store redacted URL/title/app/file identity plus references to existing job/session records, with a per-bookmark sensitivity flag and a local-delete command. Reopening an authenticated page must not execute actions.
- **missing:** A relay record joining offline_moment_bookmark IDs to a cross-surface context snapshot; A browser inspect response with stable tab identifiers and redacted titles/URLs; A Mac context read for semantic document identity and selected text (the pending mac_semantic_context_read request is not available); A spoken lookup route that searches bookmark context and returns a reopen plan rather than raw secrets

### "“If the Mac or browser agent is doing something and I press-and-hold the pendant, stop every queued action immediately and tell me what was already done.”"
- **useful because:** A wearable is the only surface the owner can reach while looking away from the Mac. This gives one dependable physical abort for a runaway browser loop, an accidental repeated command, or an automation that outlives the owner's intent, while receipts distinguish completed work from cancelled work.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** No model is needed for the stop path: a signed event and deterministic cancellation fan-out must beat any model latency. Realtime can give a short status sentence afterward; background logic reconciles receipts.
- **latency:** Pendant must latch locally in under 100 ms. Relay fan-out under 500 ms when connected; each executor should acknowledge cancellation within 2 seconds. If disconnected, the pendant retains the stop state and blocks new work until it reconnects.
- **cost:** Under $0.001 per stop; this is event routing and receipt reconciliation, not inference.
- **security:** The stop event needs device authentication, monotonic sequence numbers, replay protection, and an explicit scope (active job, all jobs, or browser only). It must not delete completed files or undo committed purchases; it only prevents queued/future actions and reports the irreversible prefix. The local latch must fail closed across a dropped link, but allow a deliberate local resume.
- **missing:** A relay cancellation fan-out with an idempotent cancel token understood by both Mac and browser workers; An executor contract that checks cancellation between actions and emits a final completed/cancelled prefix receipt; A pendant firmware amendment to local_privacy_latch or the existing button state machine so this is distinct from audio privacy without inventing an unavailable gesture

### "“Research this topic, then leave me a cited note on my Mac and a short audio version on the pendant; every claim must link back to the source passage you used.”"
- **useful because:** The owner already schedules LTE-M research and asks for news, but a spoken answer alone is not durable or auditable. This turns browser research into a traceable artifact: sources are fetched, claims retain URL plus excerpt anchors, the Mac note is created, and the pendant delivers only the concise takeaway for later playback.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** Use a cheaper background model for source clustering and claim-to-excerpt alignment; use realtime only if the owner asks follow-up questions. Browser and Mac operations remain deterministic.
- **latency:** 3–10 minutes for a bounded research job depending on source count; the first spoken progress update within 5 seconds, and the note/audio receipt only after all claims have source anchors.
- **cost:** Approximately $0.03–$0.15 per brief, dominated by source retrieval and background summarization; storage is small because excerpts are capped and deduplicated.
- **security:** Only public URLs unless the owner explicitly selects an authenticated browser session. Strip tracking parameters, redact account data, cap excerpt length, and show citations in the note. Never claim a source supports a sentence when alignment confidence is below threshold; mark it unresolved instead.
- **missing:** A research job schema that stores source URL, retrieval time, excerpt hash, and claim anchors together; A Mac note writer that can atomically create the cited note and receipt (not merely type into the foreground app); A pendant audio inbox item that references the durable note and expires stale research; A verifier that rejects unsupported or contradictory claims before publication

### "“Treat the pendant as my physical presence key: sensitive browser and Mac sessions may use their existing login only while the pendant has granted a short lease, and revoke that lease immediately when I lock it or it disappears.”"
- **useful because:** Today an authenticated browser session and a powerful Mac agent can continue acting after the owner walks away. A wearable-held, short-lived lease would make presence—not merely an old cookie or an unattended desktop—the condition for sensitive automation, without forcing the owner to retype passwords or expose them to the model.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** No model is needed for authorization. Use device cryptography and deterministic policy; realtime may narrate lease state but must never decide it.
- **latency:** Grant or revoke in under 1 second while connected. On a link loss, workers enter a conservative lease-expired state after a configurable grace period (for example 10 seconds), while ordinary public browsing remains unaffected.
- **cost:** Under $0.001 per lease event; cryptographic verification and heartbeat traffic dominate, with no inference cost.
- **security:** The pendant needs a hardware-backed device key and monotonic counters; the relay issues audience-scoped, short-lived leases bound to browser session and Mac agent identity. Do not treat LTE absence as proof of absence: the USB-attached bench mode needs an explicit local transport policy, not an accidental bypass. Fail closed for mail send, purchases, deletion, credential display, and file export; retain a revocation journal without recording secrets. Recovery must require a deliberate local button action plus re-authentication if the lease expires.
- **missing:** Hardware-backed key storage and a signed presence/lock protocol on the pendant; A relay lease service with replay protection, revocation, audience binding, and offline-expiry semantics; Browser and Mac middleware that checks the lease immediately before sensitive effects rather than only at session creation; Owner-configurable policy classes for which actions require presence, because current FULL_CONTROL_MODE has no effective approval policy

### "“Before you send any part of my request or screen to a model or relay, tell me which parts stay on my Mac, which may leave it, and let me set a rule that certain apps, sites, or folders are local-only.”"
- **useful because:** The current system can redact outputs, but the owner cannot express a durable boundary over source data before browser, Mac, relay, and model processing. A visible data-flow decision lets him use powerful automation without having to guess whether an authenticated page, private note, or source file crossed the machine boundary.
- **path:** mac-planner → browser-extension → relay-realtime → pendant
- **model tier:** Use deterministic origin classification and policy evaluation; a small local model may label ambiguous fields, but ambiguous data must remain local. Realtime only reads the short policy explanation aloud.
- **latency:** Under 200 ms for known app/site/path rules; under 2 seconds for an ambiguous preview. Never silently fall back to remote inference when classification times out.
- **cost:** Near-zero per request for policy matching; occasional local classification uses Mac CPU and no API spend.
- **security:** Policy evaluation must happen before serialization or upload, not after a model call. Rules need precedence, default-deny for unknown sensitive sources, tamper-evident audit entries, and a local emergency override. The pendant should show only category/count, never the protected content. Browser cookies, passwords, and keychain material are always local-only.
- **missing:** A preflight data-flow manifest emitted by Mac and browser actions; A policy engine shared by relay, Mac, and browser with path/domain/app selectors and default-deny semantics; A model gateway that accepts only policy-approved fields and proves what it received; An owner UI/voice command to inspect, edit, and revoke rules

### "“If I give you a goal with a deadline, keep working across the relay, browser, and Mac until it is actually done; if a dependency blocks it, wake me only with the exact decision or missing item, and escalate before the deadline.”"
- **useful because:** Today scheduled routines can run commands, but a long-running goal has no owner-visible service level: browser sessions expire, the Mac sleeps, and failures become isolated jobs. Deadline escrow would turn delegation into an accountable promise with progress, dependency detection, and a useful escalation instead of repeated vague reminders.
- **path:** relay-realtime → browser-extension → mac-planner → pendant
- **model tier:** Use a cheap background planner for decomposition and periodic reconciliation; deterministic workers perform actions. Reserve realtime for a blocker question or final concise status, not polling.
- **latency:** Create a plan in under 10 seconds. Reconcile on event, worker completion, session expiry, and at least every 5 minutes. Alert only at meaningful risk thresholds (for example 24 hours, 2 hours, and 15 minutes before the deadline).
- **cost:** Approximately $0.01–$0.05 per multi-step goal, dominated by occasional background replanning; event-driven reconciliation avoids per-minute model calls.
- **security:** The escrow must declare scope, deadline, allowed surfaces, and maximum side effects up front. It may not improvise purchases, sends, deletions, or credential use. Store progress as redacted checkpoints, sign worker results, and let the owner pause/revoke from the pendant.
- **missing:** A durable goal/constraint record distinct from a one-shot job; Dependency and deadline risk evaluation across browser session, Mac availability, and relay state; A scheduler that can wake/retry workers idempotently and deliver targeted blocker questions; A pendant-facing escalation queue with acknowledgement and expiry semantics


## Changes it proposed to its own stack

### `integration` — Add a cross-surface event ledger that correlates one owner request, its relay plan, browser command IDs, Mac action receipts, pendant bookmark/alert events, and final outcome into a single append-only timeline. Each event carries monotonic sequence, surface, redacted intent, status, and parent job ID; expose a compact owner-facing summary and a machine-readable handoff checkpoint.
- **owner gets:** After asking the system to do something, the owner can answer “what happened?” without guessing which machine ran which part. If the Mac sleeps or the browser loses its session, the system can say exactly what completed, what did not, and where to resume instead of silently repeating work.
- effort: Medium: define the event envelope, adapters for relay/browser/Mac/pendant, idempotent append, and a summary route; roughly 1–2 engineering weeks plus failure-injection tests.  ·  risk: A correlation bug could merge two requests or expose more detail than intended. Use request-scoped IDs, redaction at ingestion, immutable raw events with access control, and replay tests; if an adapter is absent, report unknown rather than fabricate completion.
- cost: Negligible storage and routing cost; optional background summarization is a few cents for long jobs and should not run for every event.  ·  latency: No added latency on the action path if events append asynchronously; final receipt may lag by under a second. Critical cancellation and completion events should use synchronous acknowledgement.
- security: Improves auditability but creates a sensitive activity history. Encrypt at rest, enforce per-owner scope, omit secrets/page bodies, and provide retention/delete controls separate from operational receipts.
- depends on: A stable request/job ID passed through POST /plan and POST /execute; Adapters for POST /browser/result/:commandId and Mac action receipts; The existing GET /jobs/:jobId/receipts and GET /workbench/jobs/:jobId/handoff semantics; A relay event envelope for pendant bookmark and alert events


## What it asked for

_Nothing._
## Its own summary

This round produced three capabilities and one integration change. The strongest owner-facing one is cross-surface bookmark recall: the already-shipped pendant bookmark becomes a private moment card containing redacted Mac/browser context, so a later spoken request can explain and reopen exactly what was happening. I also proposed a physical pendant abort that cancels queued Mac/browser work and reports the completed prefix, an evidence-preserving research-to-Mac-note/audio pipeline with claim-level citations, and a correlated event ledger for reliable “what happened?” answers. The recorder flagged the abort and ledger as close to existing ideas, but recorded them; future work should sharpen their missing contracts rather than rename them.

**Biggest unknown:** The live system still lacks verified contracts for semantic Mac document identity, browser tab identity/redaction, relay-to-worker cancellation, claim-level citation storage, and durable cross-surface event correlation. I do not need another permission this round; those are implementation gaps. The owner still needs to decide retention/privacy defaults for stored context cards and research excerpts.

