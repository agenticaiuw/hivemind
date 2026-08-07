# Harness derivation — mac-planner — round 122

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-planner live integration state 2026-08-07 round 122** — Mac agent is reachable and relay bridge online, but browser extension is offline with 9 pending commands; accessibility and screen recording are still ungranted; granted mac_readonly_inspect and mac_read_sources tools remain schema-only (no implementation). Full-control mode is enabled, while computer-use loop is disabled and vision upload consent is false.
  - evidence: GET /ops/status returned browser.online=false, pendingCommands=9, accessibility.trusted=false, screenRecording.granted=false, fullControlMode=true, computerUse.loopEnabled=false, visionUploadConsented=false; calls to mac_readonly_inspect and mac_read_sources returned 'schema but has no implementation'.

## Capabilities it proposed

### ""Continue that web task when my browser comes back, without repeating anything or losing where you got to.""
- **useful because:** Today nine queued browser commands can sit behind an offline extension, while a retry can duplicate clicks or form edits. This would let the pendant accept a long-running authenticated task, pause it safely when the browser disappears, resume from the last verified step when the extension returns, and report exactly what was completed versus skipped. It needs all four surfaces: the pendant captures the request and speaks a compact status; the relay owns the durable lease and wakes on heartbeats; the Mac bridge executes owner-private browser steps; the browser extension returns step receipts and page evidence.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** background for planning/retry classification; realtime only for the owner's initial request and status questions
- **latency:** Acknowledge in under 1 second; checkpoint each browser step within 2 seconds; resume within 10 seconds of a healthy heartbeat. Never burn a retry on a stale/offline session.
- **cost:** Low per task: one short background planning call plus small receipt/status events; dominant cost is authenticated page extraction, not the lease protocol.
- **security:** Private page text and cookies remain in the browser/Mac lane; relay stores only an opaque job, step hashes, timestamps, and redacted receipts. A resume must verify extension/session identity, URL/origin, and a page-state fingerprint before any write. Never replay a non-idempotent click/type step; mark it unknown and ask the owner. Destructive sends/purchases remain explicitly owner-confirmed even under maximum-access policy.
- **missing:** A durable cross-node job record with step leases and idempotency keys (not merely a pending command queue); Extension heartbeat carrying session identity and current tab/page fingerprint; Receipt protocol distinguishing applied, not-applied, and unknown after timeout; Resume/reconcile worker wired from relay to Mac bridge and browser result stream

### ""When I step away from my Mac, keep track of what changed and give me a private, spoken catch-up when I return—without reopening or replaying anything.""
- **useful because:** The owner currently has no dependable boundary between an active desk session and being away. Browser work can stall, Mac state can change, and important Calendar/Mail or authenticated-page changes are fragmented across surfaces. A return briefing tied to the actual away interval would explain only deltas, preserve unfinished work, and avoid reopening sensitive pages merely to reconstruct history.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use a cheap background model to diff and rank captured metadata; use realtime only to answer the owner's spoken follow-up questions.
- **latency:** Detect departure within 30 seconds and seal a checkpoint within 2 minutes. On return, deliver a 20–60 second spoken summary within 5 seconds, with a dashboard drill-down available later.
- **cost:** Low: metadata/event diffs dominate; one small summarization call per away interval. No page-body upload is needed for intervals with no relevant changes.
- **security:** Departure and return signals are sensitive. Keep raw browser URLs, mail subjects, and calendar details on the Mac unless explicitly requested; relay stores encrypted checkpoint IDs and redacted summaries. Never reopen tabs, send messages, or modify tasks automatically. Require an explicit spoken command before reading private details aloud in public, and provide a pendant privacy gesture to suppress playback.
- **missing:** A reliable cross-surface presence/away signal shared by pendant and Mac; A local append-only change journal for browser session metadata, Calendar/Mail deltas, and unfinished Mac jobs; A checkpoint format that can be resumed without replaying actions; A privacy-aware spoken delivery policy distinguishing a private return from a public environment; A relay-to-pendant event that delivers the sealed checkpoint summary after reconnection

### ""If you tell me something important from my Mac or a logged-in website, let me ask 'why?' and hear exactly where it came from and how fresh it is.""
- **useful because:** Today a spoken summary can collapse Calendar, Mail, browser pages, and local job receipts into an answer without giving the owner a trustworthy way to inspect the evidence. This would make the hive auditable: the pendant answers a follow-up with source, timestamp, account/session, transformation steps, and uncertainty, while the dashboard can show the underlying redacted evidence without exposing it to the relay by default.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use a cheaper background model to assemble and normalize provenance records; realtime only renders the short spoken explanation and handles follow-up questions.
- **latency:** Initial spoken answer unchanged; a provenance follow-up in under 2 seconds if the evidence capsule is cached, under 8 seconds if the Mac/browser must be queried.
- **cost:** Small metadata storage and occasional summarization; page/mail bodies remain local, so network and model costs stay low.
- **security:** Evidence must be capability-scoped and redacted. Relay receives signed provenance IDs and confidence, not raw private content. Dashboard access requires the paired owner session. A source that has expired, changed, or lost authentication must be reported as stale rather than silently refreshed.
- **missing:** A signed provenance envelope shared by Mac jobs, browser results, Calendar/Mail reads, and relay summaries; Evidence lineage from each spoken claim back to source records and transformations; A pendant command for 'why / how fresh / show me' with compact spoken output; Dashboard rendering of redacted evidence and source-session identity; Retention and deletion controls for provenance separate from content retention


## Changes it proposed to its own stack

### `integration` — Add a cross-node execution ledger shared by relay, Mac bridge, and browser extension. Each requested task gets a durable taskId and ordered step records with idempotency key, expected origin/URL fingerprint, lease owner, lease expiry, and terminal state (applied, not_applied, unknown). The relay grants one short lease at a time; the extension heartbeat renews only while the same session/tab is present; POST /browser/result/:commandId atomically closes the step. On reconnect, reconcile pending commands against the ledger and quarantine unknown writes instead of replaying them. Surface the ledger through the existing /jobs and receipts APIs so the pendant can say exactly where the task stopped.
- **owner gets:** A dropped browser connection would stop being a source of duplicate submissions, repeated purchases, or uncertainty. The owner could safely say "resume" and receive a precise completion report rather than guessing whether the last action happened.
- effort: Medium-high: schema and atomic state transitions in relay D1, Mac bridge adapters, extension heartbeat/result changes, plus crash/reconnect tests for timeout at every step boundary.  ·  risk: A false page fingerprint could pause a harmless task or, worse, permit a mismatched page. Default to quarantine on mismatch; recovery is manual resume after a fresh inspection. Ledger corruption should leave steps paused, never replayed.
- cost: Negligible storage and event overhead; one small D1 write per step and occasional heartbeat. No additional model call is required for retries.  ·  latency: Adds roughly 50–150 ms per step for lease/receipt persistence; resume waits for the next heartbeat (target under 10 s).
- security: Improves security by binding writes to origin/session/page state and limiting replay. Relay must not store page bodies or credentials; encrypt or hash fingerprints and redact receipt text.
- depends on: chg-16bc5dee durable browser runner remains unimplemented; browser-extension offline-queue reconciler / stale-command pause; A result contract that can report unknown after a timeout

### `context` — Attach a compact, signed environment capsule to every server-to-Mac plan: machine-context revision, browser session/tab identity and heartbeat age, active project/session, and the plan's allowed origin/app targets. Before each mutating step, the Mac bridge compares the capsule to a fresh read-only snapshot; on drift it pauses and returns a structured stale-plan receipt (what changed, which step was withheld), while read-only observations may continue. Keep the capsule as hashes and IDs rather than page text. This is observability and correctness, not an approval gate.
- **owner gets:** Plans would stop acting on yesterday's browser tab, a different account, or a changed project after the owner has resumed work. The owner gets a clear "paused because the page/account changed" explanation instead of a silent wrong edit.
- effort: Medium: add revision counters to machine/browser state, snapshot-and-compare middleware in POST /execute and browser dispatch, and stale-plan receipts in the existing job journal.  ·  risk: Over-sensitive revisions could pause harmless tasks during normal tab title changes; compare only security-relevant fields (origin, session, tab ID, app target) and allow explicit rebase. If the snapshot cannot be read, fail closed for writes and report uncertainty.
- cost: Tiny: hashes and a few metadata fields per plan/step; no extra model calls.  ·  latency: One local snapshot comparison per mutating step, target under 100 ms; no perceptible delay for reads.
- security: Reduces confused-deputy and cross-account writes by binding execution to the observed session and origin. Do not put cookies, page bodies, or secrets in the capsule.
- depends on: GET /machine-context and POST /machine-context/refresh; GET /browser/status and POST /browser/heartbeat; POST /execute and GET /jobs/:jobId/receipts; A real implementation of the granted read-only Mac inspection/source tools or equivalent local snapshot route


## What it asked for

_Nothing._
## Its own summary

Recorded two new capabilities: away/return change tracking with private spoken catch-up, and provenance-aware spoken answers that can explain source, freshness, and uncertainty across Mac/browser data. Both require new cross-surface wiring despite existing component routes.

**Biggest unknown:** Whether the owner would prefer automatic departure detection or an explicit pendant gesture for sealing an away checkpoint; no context request made because discovery is closed this round.

