# Harness derivation — relay-realtime — round 34

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Keep working on that while I head out, and let me know what happened when it’s done."
- **useful because:** It matches how people actually behave with a wearable: they start something, move on, and later need a concise, reliable update without checking a screen.
- **path:** pendant/relay: capture the handoff and confirm what will happen → relay: create a job record and spoken receipt; offer status checks via job reference → mac-bridge: plan and execute the work; report progress and completion back to relay → browser-harness: if the task involves web sessions, perform authenticated steps there, and public steps via server-browser when possible → always-awake relay: keep the status available even if the Mac sleeps, and speak the outcome when asked
- **model tier:** Realtime for the initial handoff; cheaper planner/executor for the long-running work; relay_job_status for follow-up queries.
- **latency:** Under ~1s for the spoken handoff receipt; completion can take minutes depending on the task.
- **cost:** Low per handoff; cost dominated by downstream planning/execution and any browser automation time, not the relay.
- **security:** Ensure job receipts don’t leak sensitive task details; status responses should be verbatim and sourced. Require explicit confirmation before irreversible actions downstream.
- **missing:** A durable job ledger shared between relay and mac-bridge with progress updates and completion receipts; A consistent job reference that the owner can use by saying 'that' later; A mechanism for downstream agents to report progress back to relay without the Mac being online; Optional: notifications to the pendant when a job completes

### "“I’m away from my Mac—give me a private, spoken handoff of what I left open and what I was in the middle of, and when I get back, restore that exact working set.”"
- **useful because:** Today the pendant can converse and downstream agents can act, but there is no cross-surface continuity capsule. The owner loses the state of an interrupted task when physically separated from the Mac. This would combine Mac window/document state, the browser extension’s authenticated tab/session state, relay memory, and a later pendant request into one capability without requiring the owner to remember or narrate the context.
- **path:** pendant → relay → mac-planner → mac-vision → browser → dashboard
- **model tier:** Use realtime only to recognize the short spoken request and read a cached capsule. A background/cheap model creates the capsule from structured Mac and browser observations, and a cheap model compresses it for speech; mac-planner/mac-vision execute restoration only after the owner explicitly says “restore it.”
- **latency:** Spoken status from an existing capsule in under 2 seconds. Capsule capture should complete opportunistically in 5–15 seconds; restoration can take up to 30 seconds with progress receipts, without disturbing unrelated work.
- **cost:** Roughly $0.01–$0.08 per capture/restore depending on model use and screenshot/OCR volume; most cost is browser and Mac observation plus vision, not the short realtime utterance. A structured-state-first implementation keeps routine handoffs near the low end.
- **security:** The capsule may contain document names, window titles, URLs, and snippets from authenticated pages. Encrypt it at rest and in transit, retain only the latest few capsules by default, redact secrets/form fields, and never speak sensitive titles in public until the owner asks for the private handoff. Restoration must be scoped to the recorded app/session set, report conflicts, and avoid closing or overwriting anything; export/delete controls belong in the dashboard.
- **missing:** A versioned cross-surface continuity-capsule schema with provenance and redaction rules; Mac-side read-only snapshot of windows, active documents, unsaved-change indicators, and resumable app state; Browser-extension snapshot API for authenticated tabs, scroll position, and safe page metadata without exposing cookies; Relay storage and retrieval keyed to a spoken session/time, with encryption and retention limits; A Mac restoration planner that can reopen/reposition recorded state and return per-item receipts; A way to distinguish the owner’s explicit restore request from a merely informational handoff

### "“Ask the authenticated browser session what changed about [topic], read me only the relevant answer, and if it needs action, put a concise draft on my Mac.”"
- **useful because:** A one-shot spoken query against a browser session is useful precisely when the owner is away from the Mac and cannot open the portal themselves. It is different from a scheduled briefing: the owner initiates it, the browser reads the session it already holds, and the relay turns the result into a short answer or a draft rather than pretending the realtime model can access the site.
- **path:** pendant → relay → browser → mac-planner → dashboard
- **model tier:** Realtime handles intent, clarification, and the spoken summary only. The browser harness extracts the page and a cheaper background model ranks relevant passages and produces a citation-backed answer. mac-planner creates a draft or task only when the owner asks; no realtime model is needed for page processing.
- **latency:** Acknowledge immediately; return a useful answer in 5–12 seconds for an already-open page, or up to 30 seconds if navigation and loading are required. Draft creation may continue with a spoken completion receipt.
- **cost:** About $0.01–$0.06 per query, dominated by authenticated-page extraction, OCR where necessary, and the summarization context; the realtime voice turn is a small fraction.
- **security:** This crosses private browser data to the relay and spoken audio. Require explicit invocation per query, use an allowlisted active tab/session, redact credentials/tokens and unrelated page content, retain the extracted text only ephemerally, and include the source URL/title and quoted evidence in the receipt. Drafts must be marked drafts and never sent or submitted automatically.
- **missing:** A browser-session RPC that accepts a narrow user question, navigates only within an approved authenticated session, and returns evidence spans rather than raw cookies or full page dumps; Relay support for streaming a browser job’s progress and answer into the live voice session; A context-minimizing evidence/ranking worker with URL and timestamp provenance; A Mac planner operation to create a clearly labeled draft from the answer without sending it; Per-session allowlists and dashboard controls for which authenticated browser sessions may answer voice queries

### "“Stop whatever the Mac or browser is doing right now, preserve what it already changed, and tell me exactly where it stopped.”"
- **useful because:** While away from the Mac, the pendant is the only surface the owner can reach quickly. Today a long-running delegated Mac/browser job has no common voice cancellation path; an accidental navigation, runaway loop, or simply changed mind can continue without an immediate remote stop. This is a cross-node control primitive, not a permission gate: it gives the owner a fast abort and a truthful checkpoint.
- **path:** pendant → relay → mac-planner → mac-vision → browser → dashboard
- **model tier:** Realtime performs deterministic wake-word/intent recognition and immediately sends a cancellation signal; no expensive reasoning is required. Each downstream worker records a cheap structured checkpoint and a background model can summarize it afterward. Use gpt-5.6-luna only if recovery or resume planning is requested.
- **latency:** Cancellation acknowledgment within 500 ms at the relay and best-effort downstream halt within 1–2 seconds. Checkpoint summary within 5 seconds after workers respond; behavior under a dropped Mac link must still be reported honestly.
- **cost:** Negligible per abort (under $0.01); cost is implementation and durable job state, not inference. Optional checkpoint summarization adds roughly $0.01.
- **security:** A false trigger could interrupt work, so require an explicit spoken stop phrase or the pendant’s button-plus-voice gesture, but do not require a confirmation once recognized. Cancellation must be idempotent, never roll back unknown mutations, and clearly distinguish halted, completed, and unreachable. Persist only job IDs, action receipts, and minimal checkpoint metadata; expose the full audit trail in the dashboard.
- **missing:** A shared job identity and cancellation protocol spanning relay, Mac planner/vision, and browser extension; Abort endpoints in each executor with cooperative checkpoints between actions and hard timeouts for stuck actions; Durable cancellation state in the relay so reconnecting workers cannot resume an aborted job; A spoken status path that reports partial completion and unreachable nodes without claiming success; Dashboard controls for job history, checkpoint inspection, and explicit resume-from-checkpoint planning


## Changes it proposed to its own stack

### `integration` — Introduce a shared, durable job ledger that spans relay and mac-bridge, with states (queued/running/paused/succeeded/failed), progress text, and completion receipts. Downstream agents append updates; relay answers status via relay_job_status without contacting the Mac.
- **owner gets:** They can start something from the pendant, walk away, and later ask "what happened?" and get a trustworthy answer even if the Mac is asleep.
- effort: Medium to high. Requires storage, a small schema, and update APIs; plus changes in mac-planner to emit progress and final receipts.  ·  risk: Inconsistent states if updates fail; mitigated with idempotent updates, versioned records, and timeouts. If a receipt is missing, relay should say unknown rather than guessing.
- cost: Low per job; storage and a few API calls. Main cost is execution time of downstream tasks, not the ledger.  ·  latency: Adds negligible overhead to handoff; improves status latency because relay can answer locally.
- security: Job metadata may contain sensitive info; encrypt at rest where possible and redact spoken summaries. Access control should bind records to the owner and current session.
- depends on: A storage backend for the ledger (Durable Object/D1/R2); A small protocol for progress updates from mac-bridge/browser-harness to relay

### `routines` — Add a scheduler capability (cron-like) that can trigger jobs and page watches at defined times or intervals, implemented via Cloudflare Cron Triggers or Durable Object alarms, with a typed schedule registry.
- **owner gets:** They can say "check this each morning" or "watch this page once a day" and actually have it happen without leaving a Mac app running.
- effort: High. Requires wiring cron/alarm infrastructure, persistence for schedules, and safe execution paths for triggered jobs.  ·  risk: Runaway schedules or noisy alerts; mitigate with limits, quiet hours, and backoff. Provide clear disable controls.
- cost: Ongoing cost scales with number of schedules and checks. Keep it bounded with cadences and change-detection.  ·  latency: No real-time requirement; runs in background and delivers concise results when ready.
- security: Triggered jobs may touch authenticated sessions; must use least-privilege session access and avoid exfiltration. Provide audit logs for triggered actions.
- depends on: Schedule storage and management UI/API; Durable job ledger for triggered runs; Browser harness support for authenticated page checks


## What it asked for

_Nothing._
## Its own summary

Recorded three new capabilities: cross-surface work handoff/restoration, owner-initiated spoken queries against an authenticated browser session with evidence-backed answers and optional Mac drafts, and a universal pendant voice abort with truthful checkpoints for Mac/browser jobs. Each proposal lists the missing protocol, storage, executor, and UI changes required.

**Biggest unknown:** The existing Mac planner, browser extension, and relay job implementations may expose incompatible job identifiers or lack cooperative cancellation/snapshot hooks; those interfaces must be inspected during implementation, not assumed.

