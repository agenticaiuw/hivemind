# Harness derivation — relay-realtime — round 124

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Reconcile my project across the web and my Mac: compare the authenticated project board with my local notes and git state, tell me what conflicts, and—after I say ‘apply’—update each system so they agree. Keep me informed through the pendant even if I walk away.”"
- **useful because:** Today the browser, Mac, and pendant can each be operated, but none can resolve contradictions between them as one explainable task. This gives the owner a trustworthy spoken ‘source-of-truth’ workflow: cited discrepancies first, an explicit compact diff, then coordinated updates with a final spoken receipt. It is specifically useful while away from the Mac because the pendant remains the control and notification surface.
- **path:** pendant → relay → browser → mac-planner → mac-terminal → dashboard
- **model tier:** Use the low-latency relay-realtime model only to capture the request, summarize evidence, and ask for the apply decision. Use a cheaper background planner for cross-system comparison and action sequencing; use browser/mac execution agents for their respective surfaces.
- **latency:** Initial acknowledgment under 1 second; evidence collection and comparison may take 10–30 seconds with progress events; apply and verification may take 10–60 seconds. The owner may leave immediately and receive a compact completion summary on the pendant when finished.
- **cost:** Roughly 2–4 background model calls plus one short realtime turn; browser and Mac execution dominate wall time, while token cost is dominated by extracted page/local-file content. Compress evidence into hashes, citations, and only conflicting snippets before sending it to realtime.
- **security:** Authenticated browser content and private local files leave their respective devices only as narrowly scoped extracts. Never transmit whole pages or repositories by default. The comparison is read-only; applying changes must require the owner's explicit spoken ‘apply’ for this task, with a typed per-system diff, idempotency key, before/after receipts, and undo where available. A failed half-apply must be reported rather than silently claiming consistency.
- **missing:** A durable cross-surface coordinator that can hold one reconciliation job and its evidence snapshots after the voice turn ends; A common evidence/diff schema shared by browser and Mac agents; An explicit apply checkpoint and idempotent per-system commit/verification protocol; Pendant delivery of progress, decision prompts, and completion receipts while the owner is away; Scoped browser extraction and local-project adapters for board, notes, and git providers


## Changes it proposed to its own stack

### `relay` — Implement the granted relay_route_intent schema as a real routing endpoint that accepts a concise intent + utterance and forwards to the correct downstream surface (mac-planner, browser harness, or server browser) while returning a job reference. Add a matching status read path that maps to existing job records and receipts, so the relay can speak progress and results without inventing a protocol.
- **owner gets:** They can say something like “open my calendar and find my next meeting” and hear a clear confirmation that the request was queued, then later ask “what happened to that?” and get a truthful status update even if the Mac went to sleep.
- effort: Medium. Needs a small router in the Worker, a canonical intent mapping table, and integration with existing plan/execute job records.  ·  risk: Misrouting or ambiguous intents could trigger the wrong surface. Mitigate with conservative defaults, explicit target selection when confidence is low, and robust logging/receipts for audit and undo.
- cost: Low per call (single Worker request + job record write). Main cost is downstream planning/computer-use when invoked.  ·  latency: Small added overhead at the relay (<50ms typical). Downstream work dominates.
- security: Intent and utterance are sensitive; log minimization and redaction needed. Ensure only authenticated sessions can call it and job status is scoped to the owner.
- depends on: A durable job record/receipt path that the relay can read consistently (job runner/receipt store maturity).

### `routines` — Add a scheduler capability to the stack (Cloudflare Cron + Durable Object alarms) to support delayed and recurring tasks like morning briefings, page watches, and follow-up checks. Provide a unified job definition (task type, cadence, last run, next run, state) and a safe handoff to mac-planner or browser harness.
- **owner gets:** They can rely on the system to prepare summaries and watch important pages while they sleep, without having to ask at the exact moment.
- effort: High. Requires new infrastructure, job persistence, retry semantics, and clear ownership of tasks across surfaces.  ·  risk: Over-eager automation could spam notifications or repeat work. Mitigate with quiet hours, idempotency keys, backoff, and explicit scopes for what can run unattended.
- cost: Moderate ongoing cost for scheduled runs; cost dominated by downstream web reads and planning. Tight token budgets and caching are important.  ·  latency: No added latency for interactive voice; scheduled work runs out-of-band.
- security: Schedules may encode sensitive intent (e.g., watch a bank page). Encrypt stored definitions and scope execution to the owner.
- depends on: Reliable background runner and durable storage for schedules and job state.; Browser harness capability to read authenticated sessions safely when needed.

### `integration` — Build a cross-surface reconciliation coordinator rather than another executor: create a durable ReconciliationJob containing an owner-scoped request, source snapshots (browser tab/session and Mac paths), normalized claims with provenance, a conflict graph, a proposed per-surface diff, an explicit apply checkpoint, idempotency keys, and post-commit verification. Extend the existing /plan → /execute → /jobs/:jobId/receipts chain so browser and Mac steps participate in one parent job, and emit typed progress/decision/completion events to the relay/pendant. Preserve the current receipt and undo mechanisms for each child action; if one child fails, expose the exact partial state and retry only the failed child.
- **owner gets:** The owner can ask one spoken question about inconsistent project state and get an evidence-backed answer and coordinated fix, instead of manually comparing tabs, files, and git. They can walk away without losing the task or being falsely told that every system was updated.
- effort: Medium-high: shared schema and parent/child job persistence, adapters for a first browser board plus local notes/git, planner prompt changes, event delivery, and end-to-end crash/retry tests.  ·  risk: Stale pages, merge conflicts, duplicate writes, or a Mac/browser disappearing mid-job. Mitigate with snapshot timestamps, source citations, idempotency keys, optimistic version checks, child receipts, explicit partial-failure state, cancellation, and verification reads before completion.
- cost: No new realtime model call for each progress event. One background comparison call and one planning call per reconciliation, with extracted snippets rather than full documents; storage is small JSON snapshots and receipts. API cost rises mainly with the number and size of source extracts.  ·  latency: Adds roughly 5–20 seconds for evidence normalization and verification, but provides immediate acknowledgment and asynchronous progress so conversational latency stays low.
- security: Requires least-scope source adapters and redaction before cross-surface transfer. Keep browser credentials and raw local files on their origin surfaces; relay receives citations, hashes, and conflict snippets. Apply remains an explicit owner decision, with an audit trail and undo.
- depends on: A durable Worker/DO job store or equivalent parent-job persistence; A shared typed evidence/diff schema between browser-extension and mac-planner; Pendant-capable relay event delivery and resumable completion summaries; First-party adapters for the owner’s selected project board, local notes, and git state


## What it asked for

_Nothing._
## Its own summary

Discovered current toolset and newly granted items, verified relay health and device status, and confirmed that the new relay tools are schemas without implementations. Proposed making intent routing real at the relay and adding a scheduler layer for unattended work.

**Biggest unknown:** There’s still no reliable always-on execution story: the relay can’t actually route intents yet, server-side browser actions aren’t implemented, and there’s no durable scheduler/runner. We also need a typed, minimal context service to avoid re-sending expensive context every turn.

