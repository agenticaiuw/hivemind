# Harness derivation — mac-terminal — round 31

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If something I asked you to do gets stuck or fails, figure out what went wrong, try the safe alternative, and ask me on the pendant only if you truly need me.”"
- **useful because:** Today a Mac/browser job can be queued and eventually reported, but a failure is mostly an endpoint rather than a recoverable conversation. This would turn unattended work into a resilient handoff: the Mac classifies the failure, the browser facet can refresh or reattach a session when appropriate, the relay keeps the job alive across sleep, and the pendant receives one concise question only when recovery needs owner input.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension → dashboard
- **model tier:** gpt-5.6-luna for failure diagnosis and recovery planning; gpt-4.1-mini only for deterministic browser/UI retries; relay-realtime speaks the short interruption, while background diagnosis uses the cheaper planner tier where possible.
- **latency:** Normal recovery under 10 seconds after a failure; never hold the live voice turn open. Queue diagnosis immediately, try at most two bounded alternatives, and notify the pendant within 30 seconds if blocked.
- **cost:** About $0.01–$0.08 per failed job depending on whether a planner retry needs screenshots/page text; most successes add negligible cost because the executor emits structured failure data without another model call.
- **security:** Command output, URLs, and browser excerpts may leave the Mac for diagnosis, so redact secrets and send only the failing step plus bounded evidence. Automatic recovery must be limited to idempotent/reversible retries; anything that could submit, send, purchase, delete, or duplicate must stop and ask. Keep an audit trail of every attempted alternative and its result.
- **missing:** A typed failure envelope from run_shell and browser actions (exit code, timeout/signal, stderr classification, step id, idempotency/reversibility, and redacted evidence).; A recovery state machine with retry budgets, compensating actions, and session reattachment for sleeping/restarted Macs.; A relay endpoint for owner questions that binds the reply to the paused job, plus pendant-friendly “resume/cancel” controls.; Dashboard UI showing the failed step, attempted alternatives, and exact next action before escalation.

### "“Don’t just do it—make sure it actually happened, check the result from the right source, and tell me if anything disagrees.”"
- **useful because:** Today the system can report that a Mac or browser action completed, but completion of a command is not proof that the owner's intended real-world state changed. This capability would verify the postcondition independently—for example, confirm a calendar event in the logged-in web account after creating it, confirm a downloaded file exists and opens on the Mac, or confirm a setting is reflected in the app—then reconcile conflicting observations instead of claiming success from an exit code alone.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension → dashboard
- **model tier:** Use gpt-5.6-luna for selecting the postcondition and reconciling evidence; use deterministic Mac/browser reads for collection; use relay-realtime only to speak the concise result. Background verification can run on a cheaper planner tier.
- **latency:** For local checks, 2–5 seconds; for browser/account checks, up to 20 seconds asynchronously. The pendant should immediately say that verification is in progress, then deliver verified, contradicted, or inconclusive status.
- **cost:** Usually $0.005–$0.04 per verification for structured reads; $0.05–$0.15 when reconciliation needs screenshots, page extraction, or a second model pass. The dominant cost is authenticated page context, not the Mac reads.
- **security:** Verification may access more private state than the initiating action. Each check should use the minimum source needed, redact values in relay speech and dashboard previews, and preserve source URL/app, timestamp, and evidence hashes. Never silently “repair” a contradiction; any corrective mutation remains a separate owner-directed action.
- **missing:** A first-class postcondition specification in each action/job, including acceptable evidence sources and freshness window.; Cross-surface verification adapters that can query Mac state, browser state, and relay receipts under one correlation ID.; An evidence reconciler that distinguishes command success, observed state change, stale cache, and contradictory sources.; A pendant/dashboard result format with confidence, evidence links, and a clear “verified / not verified / needs you” outcome.


## Changes it proposed to its own stack

### `mac-harness` — Add a failure-aware execution envelope and recovery journal around every Mac and browser action without narrowing FULL_CONTROL_MODE. Before execution, record a generated step ID, intent, idempotency/reversibility class, timeout, and retry budget. Afterward persist exit code or browser error class, duration, redacted stdout/stderr tail, affected app/tab/session, and a compact evidence hash. A classifier maps failures into transient transport/session, missing dependency, permission, semantic mismatch, or irreversible-uncertainty. The job runner may automatically retry only declared-idempotent steps, reattach a browser tab or relaunch an app when the class permits, and produce a compensation suggestion for everything else. Expose a single timeline to relay_job_status and the dashboard, with machine-readable pause/resume/cancel tokens.
- **owner gets:** When they leave a job running, they get an honest explanation and a useful next attempt instead of “failed.” They can resume after a Mac sleep or browser restart without repeating completed work, and can see exactly which alternative was tried. This preserves the owner's maximum-access policy while making failure recovery and trust substantially better.
- effort: Medium-high: executor/job schema, redaction and journal persistence, retry state machine, browser reattachment hooks, relay status projection, and dashboard timeline; roughly 1–2 weeks for a robust first version.  ·  risk: Retries could duplicate side effects if an action is misclassified, and captured output could contain secrets. Default unknown actions to no automatic retry, use idempotency keys where possible, redact credential-like patterns, and keep compensation advisory rather than silently mutating. Recovery is straightforward by replaying the journal and marking a job paused.
- cost: Low storage and compute overhead per step; roughly 1–5 KB of metadata plus bounded output per action. Fewer planner calls on transient failures should reduce API cost; diagnosis costs an extra small planner call only on failure.  ·  latency: Negligible for normal actions if journaling is append-only/local; a few milliseconds per step. Recovery adds seconds only after failure, with retries bounded and asynchronous.
- security: Improves auditability without adding approval gates or reducing access. Sensitive command output and URLs must be redacted before relay/dashboard projection; retain full evidence locally under existing Mac trust boundary and expire it by job retention policy.
- depends on: The existing receipt/undo records need a common step identifier and reversible/irreversible metadata.; Durable relay job records and browser session/tab affinity must expose pause/resume semantics.; A small, shared redaction library must run before evidence leaves the Mac.


## What it asked for

_Nothing._
## Its own summary

Discovered the live Mac tools and backlog, then proposed a new cross-surface capability: failed Mac/browser work should diagnose itself, attempt bounded safe recovery, and ask the owner on the pendant only when needed. I also proposed the concrete mac-harness change: structured failure envelopes, redacted evidence, idempotent retry budgets, browser reattachment, compensation suggestions, and pause/resume tokens—without gates or reduced access. I do not need another permission or tool this round; implementation still needs the typed failure schema, shared redaction, and durable pause/resume contract described in the proposals.

**Biggest unknown:** The exact existing job/receipt schema and whether browser and Mac executors can already expose stable step IDs and session reattachment hooks; the previously requested observability context was not granted.

