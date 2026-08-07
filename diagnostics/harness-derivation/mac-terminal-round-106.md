# Harness derivation — mac-terminal — round 106

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent readiness and control reachability** — Live /ops/status and /observe show fullControlMode=true, but agent ready=false because Accessibility is not trusted and Screen Recording is missing. Synthesized UI events are explicitly reported as success while doing nothing; browser extension is offline with 9 pending commands. Relay is reachable and mac bridge online.
  - evidence: GET /ops/status 200 at 2026-08-07T13:59Z; GET /observe 200: accessibility trusted=false, eventsPost=false, screenRecording=false, uiActionsWillReachTheScreen=false, browser online=false pendingCommands=9.
- **Mac execution observability** — The durable journal currently contains 120 jobs / 146 actions, 18 failures, and 0 undoable actions; routing has 57% of requests off planner but 112 jobs lack tier attribution. Repeated browser_list_tabs has 34 runs / 7 failures; one browser_navigate idempotency key has 8/8 failures.
  - evidence: GET /journal and GET /routing live responses at 2026-08-07T13:59Z.

## Capabilities it proposed

### "When something fails on my Mac, tell me exactly what ran, what it could reach, why it failed, and what you recommend next — in one short spoken explanation."
- **useful because:** Today the Mac can return a receipt, but receipts can claim UI success despite Accessibility being unavailable, and 112 recent jobs lack tier attribution. This gives the owner a causal, trustworthy explanation rather than a generic failure.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** deterministic first for status, receipt, and permission facts; background model only to compress the trace into speech; planner only when choosing among genuinely different recovery paths.
- **latency:** Under 1 second for deterministic diagnosis; under 3 seconds if a short background summary is needed.
- **cost:** Usually zero model cost; roughly 2k background prompt tokens only for ambiguous multi-step traces. Dominant cost is existing execution, not diagnosis.
- **security:** Trace must contain hashes and typed metadata by default, not shell command arguments, page text, tokens, or private URLs. Reveal sensitive details only when the owner explicitly asks; never send raw environment variables to relay.
- **missing:** A durable causal execution-trace schema linking request, routing decision, health snapshot, action, receipt, and recovery attempt; A pendant/relay query that renders that trace as a concise spoken diagnosis; Explicit distinction between attempted, OS-accepted, and externally verified UI outcomes

### "Make this true everywhere: after I ask you to change something, keep checking the Mac and my logged-in browser until the requested end state is verified, then tell me whether it is actually done—not merely whether an action ran."
- **useful because:** Today an action receipt can say success even when macOS ignored UI events, and browser commands can remain stranded while the extension is offline. The owner needs outcome verification across the surfaces that hold the real state, not a claim that an instruction was dispatched.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Deterministic state predicates and verification first; background model to translate evidence into a short update; planner only to select a recovery when the predicate remains false or evidence conflicts.
- **latency:** Immediate acknowledgement under 1 second; verification within 5 seconds for local state and continued background monitoring for remote/browser state.
- **cost:** Normally no model call for typed predicates and receipts; occasional background summary around 1–3k prompt tokens. Cost is dominated by browser/session verification, not inference.
- **security:** Verification must use the same authenticated browser session without exporting page contents unnecessarily. Store only predicate results, source surface, timestamps, and redacted evidence hashes. Never infer completion from an unverified click or replay a non-idempotent mutation.
- **missing:** An owner-facing end-state predicate language covering Mac files/apps/settings and authenticated page state; A cross-surface verifier that can compare Mac state, browser DOM/session state, and relay-held job state; A convergence monitor with bounded, idempotent retries and explicit inconclusive/blocked outcomes; Pendant speech and dashboard views that distinguish dispatched, observed, verified, and contradicted

### "If my Mac and a logged-in website disagree about whether something is finished, warn me and show both pieces of evidence before doing anything else."
- **useful because:** A browser submission, local file change, or app action can succeed on one surface while the other remains stale or disconnected. The owner currently gets no cross-surface contradiction signal and may repeat a transaction or assume a private account is updated when it is not.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision
- **model tier:** Deterministic typed comparison and freshness checks; background model only to summarize the disagreement; planner only for a proposed repair after the owner chooses which source is authoritative.
- **latency:** Under 2 seconds after each relevant action or browser heartbeat; spoken alert only when the disagreement is material and persists beyond a short freshness window.
- **cost:** No model call for most comparisons; roughly 1–2k background prompt tokens only when evidence descriptions need compression.
- **security:** Keep raw logged-in page data and local file contents on their originating device. Send relay only redacted field names, values where permitted, timestamps, and evidence hashes. Never auto-resolve a conflict involving money, messages, account settings, or submissions.
- **missing:** A shared entity/field identity and freshness model connecting Mac artifacts to browser page fields; A contradiction detector that distinguishes stale observations from true disagreement; A concise evidence card available through the pendant and dashboard; Owner-selectable authority and repair plans without automatic mutation


## Changes it proposed to its own stack

### `mac-harness` — Add a live capability-health handshake and dead-letter recovery loop. Before UI/browser actions, publish a typed snapshot from /ops/status + /observe (accessibility reachability, screen-recording, browser-extension heartbeat, pending-command age, relay reachability). Mark UI actions as untrusted when eventsPost=false instead of accepting success receipts; route eligible work to shell/AppleScript or relay/public-browser paths, and move stale browser commands into a retry/dead-letter state with reason, expiry, and idempotency key. Reconcile the result into /journal and /routing so every action has a tier and health snapshot.
- **owner gets:** The pendant will stop telling you that it clicked or typed when macOS ignored the event, and it will recover from a sleeping browser extension instead of silently accumulating nine commands. You get an honest spoken answer and a usable fallback without adding approval gates or reducing the owner's maximum-access policy.
- effort: Medium: shared health schema, preflight in executor/browser bridge, stale-command sweeper, and journal/routing fields; add integration tests for inaccessible UI and extension reconnect.  ·  risk: A fallback could choose the wrong surface or replay a non-idempotent browser action. Mitigate by only auto-retrying declared-idempotent reads, never replaying mutations, and retaining the original receipt/evidence; dead-letter rather than execute when ambiguity remains.
- cost: Negligible storage and one cheap deterministic status pass; avoids wasted planner calls and repeated failed browser actions.  ·  latency: Adds tens of milliseconds for local health checks; avoids 120-second hangs and repeated retries.
- security: No new authority and no gates. Health snapshots must redact URLs, tab contents, and environment secrets; only capability/status metadata crosses relay.
- depends on: Existing GET /ops/status and GET /observe observability routes; Existing browser heartbeat/poll/result queue and idempotency keys; Existing durable /journal and /routing receipts; A typed fallback matrix for shell/AppleScript versus browser actions

### `integration` — Introduce a single execution-trace ID propagated from relay request through planner routing, Mac executor, browser bridge, receipts, and journal. Persist a compact event chain: requested intent, selected surface/tier, health snapshot hash, exact typed action (or redacted shell fingerprint), OS-level result, external verification result, retry/fallback, and final owner-visible status. Backfill tier attribution for new jobs and expose GET /journal/:jobId/trace plus a relay-friendly redacted form.
- **owner gets:** When a task goes wrong, the pendant can distinguish 'the command failed,' 'the Mac accepted it but the screen was unreachable,' and 'the browser never received it.' You can trust the explanation and choose a recovery, instead of repeating an action blindly.
- effort: Medium, touching relay request metadata, planner receipts, executor/jobTracker, browser bridge, and dashboard display; low-risk migration because existing jobs remain readable without traces.  ·  risk: Trace growth and accidental leakage of commands or private page data. Use bounded event counts, retention, redaction/fingerprints, and sensitivity labels; if trace persistence fails, execution must continue and emit a degraded receipt.
- cost: Small D1/local JSON overhead; no extra model calls. Reduces repeated planner calls caused by opaque failures.  ·  latency: One in-memory correlation ID and append per event; typically <10 ms, with asynchronous persistence where safe.
- security: Improves auditability while requiring strict redaction. Raw shell, URLs, tab text, and secrets stay local; relay receives only typed summaries unless explicitly requested.
- depends on: Existing action receipts and /journal persistence; Existing /routing tier receipts; Existing browser command IDs/idempotency keys; Relay request metadata propagation


## What it asked for

_Nothing._
