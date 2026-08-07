# Harness derivation — mac-planner — round 143

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **execution truth** — Live pipeline data contains a job whose Mac plan is waiting for approval on run_shell, while the granted Mac contract says FULL_CONTROL_MODE is ON and approval classification is bypassed. This is a cross-surface status contradiction requiring reconciliation rather than another approval gate.
  - evidence: GET /pipeline returned pipelineId job_309f5663... with agent waiting event detail 'Running a shell command needs your approval'; granted context states executor.js FULL_CONTROL_MODE ON and actionRisk is never consulted.

## Capabilities it proposed

### "“What’s going on on my computer right now, and did the thing I asked you to do actually finish?”"
- **useful because:** A pendant user often cannot look at the Mac, especially after leaving it unattended or when a connection dropped. This gives a compact, current, read-only situation report: foreground app and running apps, browser tabs/session identity, the latest correlated job receipt, and whether the result was delivered to the pendant. It turns ambiguous status into an answer grounded in fresh Mac observations rather than stale conversation memory.
- **path:** pendant → relay → mac-vision → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic read-only inspectors and receipt reducer first; use the cheap background model only to compress many app/tab names into a spoken summary. Reserve realtime for the owner's follow-up voice turn.
- **latency:** Under 1 second for Mac/browser/receipt reads on LAN; under 3 seconds if relay must reconcile a delayed job. Speak immediately with a short 'checking' cue only when remote reconciliation is needed.
- **cost:** Near-zero model cost for one-line deterministic status; roughly $0.001–$0.01 for optional cheap summarization, dominated by context transfer if many tabs/apps are returned.
- **security:** This can reveal sensitive app names, URLs, and job paths aloud. Default to app categories and domains only, redact titles/paths, require an explicit 'details' follow-up for exact data, and never include page bodies or keystrokes. Scope browser results to the authenticated session and mark every observation timestamp.
- **missing:** An implementation behind the granted mac_readonly_inspect schema (it currently returns 'schema but has no implementation yet'); A shared correlation/reconciliation reducer that joins Mac receipts with relay/pipeline delivery states; A pendant-safe redacted status rendering and freshness indicator

### "“If something on my Mac or logged-in browser changed while I was away, tell me whether it was me, the Pendant, or an unknown process—and let me shut down only the suspicious session.”"
- **useful because:** Today the owner can receive action receipts, but cannot reliably distinguish their own activity from automation, a stale/replayed command, or an unexpected browser session. A cross-device provenance and anomaly report would make unattended automation safer without imposing approval gates on the owner's chosen maximum-access workflow. The pendant can speak a short warning while the Mac dashboard preserves exact evidence.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard-ux
- **model tier:** Use deterministic event correlation, signed session identities, timestamps, and OS/browser audit facts for detection. Use a cheap background model only to explain an already-established anomaly in plain language; use realtime solely for the owner's follow-up conversation.
- **latency:** Passive correlation within 5 seconds of an action or browser heartbeat; pendant warning within 2 seconds after a high-confidence anomaly. Session shutdown should complete within 3 seconds on a reachable Mac.
- **cost:** Low API cost: mostly local reducers and hashes; occasional cheap explanation under $0.01. Storage is a bounded append-only event ledger, with detailed evidence retained briefly.
- **security:** The ledger itself is sensitive because it can expose URLs, app names, file paths, and activity patterns. Keep raw evidence on the Mac, send only redacted hashes and classifications to relay, encrypt authenticated dashboard access, bind events to device/session keys, and require explicit owner confirmation only for terminating a session—not for ordinary automation. A false positive must never delete data or silently cancel unrelated work.
- **missing:** Per-action cryptographic provenance from the Mac executor and browser bridge, including actor identity (owner input, relay command, local automation, or unknown); A browser-extension heartbeat/session identity that survives tab navigation and detects duplicate or stale command replays; A Mac-local read-only audit adapter for app/file/browser mutations that does not depend on Accessibility or Screen Recording; Relay anomaly correlation, alert severity, and a scoped revoke-session command; A dashboard and pendant protocol for redacted evidence cards and owner-confirmed session shutdown


## Changes it proposed to its own stack

### `integration` — Introduce a cross-surface execution-truth protocol with one correlation ID and monotonic state machine spanning relay, Mac /plan→/execute, jobTracker/receipts, pipelineTrace, and pendant delivery. Every accepted command must emit planned, dispatched, started, per-action result, terminal (completed/partial/failed/cancelled), and delivered states; terminal state is derived only from Mac receipts, while approval-required is an explicit policy state that cannot be synthesized from an old planner trace. Relay and pendant should reconcile out-of-order/replayed events, expose the last durable receipt plus action-level errors, and suppress duplicate spoken updates. Add a watchdog that marks stale in-flight jobs unknown (not successful) and lets the owner ask 'what actually happened?' from the pendant.
- **owner gets:** The owner gets trustworthy answers after walking away or losing LTE: no phantom 'waiting for approval,' no premature 'done,' and a concise spoken result that distinguishes completed, partially completed, failed, or not delivered. This matters especially when a Mac action changes files or browser state and the pendant is the only place the owner hears the outcome.
- effort: Medium-high: shared event schema and reducer in relay/Mac, adapters for existing pipeline and job receipts, replay/idempotency tests, plus a small pendant status renderer.  ·  risk: A stricter reducer may expose old jobs as unknown or partial instead of falsely successful; recover by replaying receipts and allowing explicit retry/cancel. Event metadata could reveal app names, URLs, or file paths, so redact sensitive fields in pendant speech and retain full detail only in authenticated Mac dashboard.
- cost: Negligible steady-state API cost; a few hundred bytes of event metadata per action and occasional cheap reconciliation requests. No new hardware cost.  ·  latency: One local receipt acknowledgment before terminal speech, typically tens to hundreds of milliseconds; stale-job watchdog is background.
- security: Improves integrity and auditability but creates a cross-surface action history. Bind correlation IDs to authenticated sessions, redact speech payloads, and retain configurable short TTL for detailed events.
- depends on: Existing POST /plan and POST /execute handoff; Existing jobs and GET /jobs/:jobId/receipts; Existing POST /pipeline/events and pipelineTrace; Existing pendant delivery path and relay job records

### `integration` — Add an append-only, hash-chained activity ledger shared by the Mac agent and browser bridge. Each plan, browser command, Mac action, receipt, cancellation, and delivery event gets a canonical event ID, parent ID, actor class, device/session key ID, monotonic local timestamp plus relay time, and redacted resource digest. The Mac signs the event batch locally; relay verifies signatures and stores only the chain head plus short-lived encrypted detail. Add a reconciliation endpoint that reports gaps, replayed IDs, clock inversions, and actor mismatches, without changing the owner's no-gate execution policy.
- **owner gets:** The owner can finally tell whether an unexpected change came from them, the Pendant, a local automation, or a stale/unknown session, even after the Mac was asleep or LTE disconnected. It provides trustworthy evidence for the new anomaly report instead of merely combining existing logs that can disagree or be replayed.
- effort: High: define the event schema and key lifecycle, instrument planner/executor/browser bridge/pipeline delivery, implement local signing and relay verification, add gap/replay reconciliation and retention tests.  ·  risk: Clock skew, lost batches, or key rotation can produce false gaps; recovery requires explicit unknown intervals rather than inventing a successful history. Compromise of the Mac signing key could forge local events, so rotate keys, keep the relay's verification history, and label trust boundaries. Do not make the ledger a destructive control path.
- cost: Small local CPU/storage overhead for hashing and signing; bounded encrypted detail storage. Negligible model/API cost. Hardware changes are unnecessary unless a stronger hardware-backed key is later desired.  ·  latency: Sub-millisecond to a few milliseconds per local event batch; relay verification is asynchronous and must not delay ordinary actions or speech.
- security: Improves provenance integrity while introducing signing keys and sensitive activity metadata. Store private keys in macOS Keychain, minimize relay detail, use short TTLs, and expose revocation/audit events to the owner.
- depends on: Existing job receipts and execution journal; Existing browser session and heartbeat identity; A durable cross-surface execution state reducer; Relay support for authenticated event-batch verification and bounded retention


## What it asked for

_Nothing._
## Its own summary

Recorded a new capability for detecting and scoped-shutting down unexpected Mac/browser activity, plus the missing integration layer: a signed, hash-chained cross-surface activity ledger with actor identity, replay/gap detection, and redacted evidence. This goes beyond the backlog’s ordinary receipts/history because it establishes trustworthy provenance across disconnected relay, Mac, browser, and Pendant surfaces.

**Biggest unknown:** The exact Mac-local sources available for observing file/app/browser mutations without Accessibility or Screen Recording, and whether macOS Keychain-backed signing can be deployed in the agent binary.

