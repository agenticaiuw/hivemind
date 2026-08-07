# Harness derivation — mac-terminal — round 75

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac execution readiness and cross-node recovery** — Live /ops/status shows Mac agent FULL_CONTROL_MODE=true and relay reachable, but mac accessibility and screen recording are not granted; browser extension is offline with 5 pending commands. Existing /journal is read-only and already derives receipts, undoability, routing, focus, and evidence capsules, but current payload does not expose shell cwd/exit/stdout/stderr/retry metadata.
  - evidence: GET /ops/status 200 at 2026-08-07T12:24:13Z; GET /journal 200 at 2026-08-07T12:24:13Z

## Capabilities it proposed

### "“Did that actually happen?” — give me one trustworthy answer about a multi-step task, including what the Mac did, what Safari changed, whether the relay delivered it, and what remains uncertain after an interruption."
- **useful because:** Today the owner can get separate job receipts, browser results, and relay status, but cannot obtain a single causal account when a task crosses surfaces or the connection drops. This would prevent duplicate actions and false confidence: the pendant could say “the form was filled but not submitted,” “the Mac command exited successfully but the browser confirmation never arrived,” or “the result is unknown; here is the exact safe point to inspect.” It is an evidence-and-uncertainty capability, not another action history.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic event correlation first; use the cheaper background model to summarize conflicting evidence, escalating to the planner only when evidence is incomplete or contradictory. Realtime is used only to answer the owner's spoken question.
- **latency:** Under 2 seconds for a status assembled from existing receipts; under 10 seconds when reconciling several event streams or generating an uncertainty explanation.
- **cost:** Usually near-zero model cost for correlation; roughly one background call for ambiguous cases, with planner escalation uncommon. Storage is a compact event graph and hashes rather than full duplicated payloads.
- **security:** The graph may link sensitive browser URLs, shell commands, and form values. Keep raw values local to the owning surface, send relay only redacted event claims and stable IDs, encrypt the cross-surface graph, and clearly label unknown versus verified facts. Never infer successful submission from a mere click or network dispatch.
- **missing:** A shared cross-surface task/run identifier propagated through Mac jobs, browser commands, relay delivery, and pendant acknowledgement; An append-only event envelope with timestamps, causal parent IDs, idempotency keys, outcome confidence, and redacted evidence references; A reconciler that detects contradictory or missing terminal events and produces explicit unknown states; A pendant/dashboard presentation for a causal timeline and a recommended inspection or resume point


## Changes it proposed to its own stack

### `mac-harness` — Add a replayable shell-execution record and recovery loop without changing FULL_CONTROL_MODE: every run_shell job captures normalized command/argv (with secret-value redaction), cwd, start/end time, timeout, exit status/signal, stdout/stderr tails plus hashes, environment/tool-version fingerprint, and whether the action is known reversible. On failure or timeout, persist a structured failure receipt and a retry plan (same command, extended timeout, alternate cwd, or planner escalation) rather than only an opaque error. Expose GET /journal and GET /jobs/:id/receipts with these fields, and let the relay/pendant receive a compact completion/failure event containing job id, cause, recovery options, and exact replay command; retries remain agent-initiated and unrestricted, never approval-gated.
- **owner gets:** When a long Mac task fails after the owner walks away, the pendant can say exactly what failed and offer a sensible continuation instead of making them reconstruct the command. Successful work becomes auditable and reproducible; failures caused by the wrong project directory, expired PATH, or timeout can recover automatically. This complements existing receipts/undo and does not reduce the owner's maximum-access policy.
- effort: Medium: executor wrapper and durable schema migration, bounded output capture/redaction, journal fields, relay event, and planner retry policy; add crash/timeout tests.  ·  risk: Capturing output can expose secrets or large logs; redact common token/password patterns, cap tails, store hashes for full output, and apply existing workspace retention. Automatic retries can duplicate non-idempotent commands, so retry classification must be advisory and only the planner chooses; no new gate is introduced.
- cost: Negligible API cost; a few KB per job in local JSON/D1, plus one cheap background/planner call only when recovery reasoning is needed.  ·  latency: Near-zero execution overhead for metadata; failure reporting is immediate, with optional background retry analysis.
- security: Improves forensics but creates a sensitive command/output record. Encrypt or permission-protect the local journal, redact secrets before relay, and send only summaries across the network.
- depends on: Existing action receipts and GET /journal/GET /jobs/:jobId/receipts; Relay job-status/event path for pendant notification; A durable shell-job identity/idempotency field in the executor

### `integration` — Introduce a cross-surface causal event ledger, not another job log. At task creation, mint a runId and propagate it through every Mac action, browser command, relay delivery, and pendant acknowledgement. Store only immutable redacted claims with parent event, idempotency key, actor/surface, monotonic and wall-clock time, terminality (dispatched/observed/committed/unknown), and evidence reference. Add a reconciliation pass that marks a run explicitly UNKNOWN when a terminal event is absent or contradictory, and emits the smallest next inspection action rather than guessing success. Existing /journal, browser results, receipts, and relay status become adapters into this ledger.
- **owner gets:** The owner gets an honest answer about the state of a task spanning devices, even after a dropped connection, instead of a misleading collection of individually successful-looking receipts. They can resume from the last proven boundary without repeating a submission or shell mutation.
- effort: High: define an event schema, adapters for Mac/browser/relay/pendant, durable storage and reconciliation, clock-skew handling, redaction, and dashboard/pendant rendering.  ·  risk: Incorrect correlation or clock skew could join unrelated actions. Require explicit runId propagation, idempotency keys, parent validation, and an UNKNOWN state whenever causality cannot be proven. Never convert dispatch into commit.
- cost: Small durable event storage cost; deterministic reconciliation is cheap, with background summarization only for human-readable explanations.  ·  latency: No added latency to individual actions if events are appended asynchronously; status queries may take tens to hundreds of milliseconds for reconciliation.
- security: Creates a sensitive cross-surface metadata trail. Keep raw page values and shell output behind local evidence references, encrypt the ledger, redact relay payloads, and enforce per-owner run access.
- depends on: A shared runId/idempotency contract across Mac and browser adapters; Durable relay delivery receipts and pendant acknowledgement events; An append-only local/relay event store; Dashboard and pendant status rendering


## What it asked for

_Nothing._
