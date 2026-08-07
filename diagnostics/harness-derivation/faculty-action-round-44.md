# Harness derivation — faculty-action — round 44

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If my Mac goes to sleep or I leave it, keep carrying out the approved task on whatever connected surface can safely finish it, then tell me exactly where it stopped or completed."
- **useful because:** Today an approved task is stranded when the Mac or private browser disappears, and retrying risks doing part of it twice. This would make the hive behave like one dependable agent: the relay preserves the intent and evidence, the Mac resumes local work when available, and the browser or pendant provides continuity and control without losing the owner’s place.
- **path:** pendant: announces that work was paused, offers cancel/revoke by button, and speaks the final outcome → relay-realtime: stores the signed intent, checkpoint, expiry, and idempotency key while the owner and Mac are absent → mac-planner: decomposes the task into checkpointed, resumable steps and reports durable state → mac-vision: resumes GUI steps only from a verified visual/state checkpoint, never from a guessed screen → browser-extension: reattaches to the same authenticated tab/session when available and returns provenance for each step → unified: reconciles receipts from all surfaces into one completion or partial-completion answer → faculty-perception: verifies the current target state before resuming a step → faculty-judgement: decides whether migration is safe and which step classes may resume automatically → faculty-action: executes only the currently leased step and records an idempotent receipt
- **model tier:** Use background model for checkpoint summarization and migration planning; use realtime only for the owner’s live spoken interaction and urgent pause/cancel. Use deterministic state checks for idempotency and completion proofs.
- **latency:** Immediate spoken acknowledgement under 2 seconds; pause is recorded locally/relay-side within 5 seconds. Resume begins on the next valid heartbeat, typically under 15 seconds, with no model call for deterministic steps.
- **cost:** Low-to-moderate: mostly D1/checkpoint writes, heartbeats, and deterministic verification. One background-model call per migration or ambiguous checkpoint; realtime tokens only when the owner is actively speaking.
- **security:** Never migrate secrets or authenticated browser work to an untrusted/public surface. Bind leases to device identity, session/tab identity, action hash, and expiry; require fresh owner confirmation for sending, deleting, purchasing, or any irreversible step after interruption. Encrypt checkpoint payloads, redact page contents from receipts, and expose revoke-all from the pendant.
- **missing:** A shared checkpoint schema that records preconditions, postconditions, provenance, and idempotency keys across Mac, relay, and browser; A lease/revocation protocol that can survive Mac sleep and prevent duplicate execution; A heartbeat-triggered resume coordinator with explicit safe-to-migrate action classes; State verification hooks in mac-vision and browser bridge before replaying a step; Pendant firmware support for paused-task status and a local cancel/revoke gesture; Owner-side Accessibility, Screen Recording, and Browser Bridge activation so the execution surfaces can actually participate


## Changes it proposed to its own stack

### `integration` — Add a cross-surface execution-readiness handshake and lease. Before any approved action, the relay asks Mac agent for a signed preflight containing Accessibility/Screen Recording readiness, browser-heartbeat freshness, target tab/session affinity, and current queue capacity. If a required surface is unavailable, persist the approved intent as a paused job with an expiry and cancellation token; the relay retries on heartbeat recovery, while the pendant announces 'waiting for browser' and a long-press cancels. Emit one terminal receipt with preflight failures, retry timestamps, and the exact action outcome—never a client-side timeout masquerading as failure.
- **owner gets:** A spoken request will either complete across the Mac and private browser or clearly wait and recover when the missing surface comes back. The owner no longer has to guess whether an action happened, repeat it after a timeout, or discover stale browser commands later; they can cancel from the pendant.
- effort: Medium: shared preflight schema and signed lease in relay/Mac agent, heartbeat-triggered retry worker, pending-job UI/status, pendant notification/cancel mapping, and failure-injection tests for permissions/browser dropouts.  ·  risk: A paused approved action could execute later than expected; enforce short leases, action-class expiry, idempotency keys, and require reconfirmation for destructive actions after any suspension. Recover by cancellation and receipt audit; never auto-retry send/delete/purchase classes.
- cost: Low ongoing API cost: deterministic checks and retry orchestration; only invoke a model for ambiguous recovery messaging. Small D1/JSON state growth per pending job and heartbeat.  ·  latency: Adds sub-second preflight when healthy; unavailable surfaces return immediately as paused instead of waiting ~45s for a browser timeout. Recovery latency is heartbeat cadence plus action execution.
- security: Signed, scoped leases prevent replay and bind intent to a specific Mac/browser session; receipts must avoid page secrets. Requires explicit owner policy for which reversible classes may resume automatically.
- depends on: Enable Accessibility and Screen Recording for AI Pendant Agent; Bring Browser Bridge extension online and polling; Durable job runner and receipt/undo storage


## What it asked for

_Nothing._
## Its own summary

Round 44 established that execution primitives are present (Mac full-control planner, durable jobs, receipts/undo/cancel, reachable relay), but the action path is not operationally ready: Accessibility and Screen Recording are denied, the computer-use loop is disabled, and the browser bridge is offline with three pending commands. I sent faculty-judgement the evidence and recorded a new integration change: a signed cross-surface readiness preflight/lease that pauses approved reversible jobs, retries on heartbeat recovery, supports pendant cancellation, and produces a truthful terminal receipt. I also informed relay-realtime.

**Biggest unknown:** Whether the owner will enable Accessibility/Screen Recording and bring the Browser Bridge online; without those grants I cannot verify an end-to-end browser or vision action this round.

