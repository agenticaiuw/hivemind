# Harness derivation — faculty-action — round 111

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I say something while the pendant is offline, carry it out safely when it reconnects—once, with the right current context—and tell me exactly what happened or ask me to resolve a conflict."
- **useful because:** The owner can issue commands anywhere without guessing whether the link is alive. Reconnection should not replay stale or duplicate actions, silently apply changed context, or lose the request; this coordinates the wearable, always-on relay, Mac executor, and browser sessions.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use realtime only to capture/acknowledge the short intent; use a cheaper background model to classify and reconcile queued intents. Deterministic relay/job logic should perform deduplication, expiry, leases, and conflict checks; invoke the model only for ambiguous natural-language conflicts.
- **latency:** Immediate local enqueue and spoken receipt when offline (<300 ms); on reconnect, status within 2 s and execution as soon as the Mac/browser is online. Conflicts must pause rather than guess.
- **cost:** Usually <$0.01 per queued command; deterministic queue/receipt work dominates no model cost. Ambiguous conflict resolution may use one small background-model call, roughly $0.001–$0.01.
- **security:** Queued intents may contain private context and must be encrypted at rest and scoped to the owner/device. Expire intents whose authorization or page session changed; never replay sends, purchases, deletes, or submissions without fresh confirmation. Show source time, target surface, and exact action receipt; allow cancellation before lease acquisition.
- **missing:** A durable pendant-side/offline intent spool and reconnect protocol; Per-intent idempotency plus context/session version preconditions at execution; A lease/expiry/conflict state machine that can pause and request owner resolution; A reconnect event from the pendant and a dashboard/spoken review of pending conflicts

### "Put everything back the way it was before that task, across my Mac and logged-in browser, and show me what was restored and what could not be safely reversed."
- **useful because:** Today a multi-surface task can leave changes split across apps, tabs, files, and server jobs; a single last-job undo is not enough. The owner needs recovery from a partially successful task without manually remembering every mutation.
- **path:** mac-planner → mac-vision → browser-extension → relay → dashboard
- **model tier:** Use deterministic action journals and typed compensating operations first; use the background model only to map an unfamiliar reversible mutation to a proposed compensation. Realtime is unnecessary except for a brief spoken status.
- **latency:** Build the recovery plan within 3 seconds for a recent task; execute reversible compensations sequentially with verification, pausing immediately on ambiguity or an irreversible step.
- **cost:** Typically <$0.01 per recovery; journal lookup and typed compensation are deterministic. A rare model-assisted mapping costs roughly $0.001–$0.02.
- **security:** Recovery must be scoped to one owner-approved task and never infer permission to delete, send, purchase, or overwrite. Show each before/after value and require fresh confirmation for any destructive compensation. Keep sensitive page values redacted in the journal while retaining hashes sufficient for verification.
- **missing:** A task-level mutation journal spanning Mac and browser actions, not merely per-action receipts; Typed compensating actions with preconditions and postcondition verification for files, app state, and authenticated page fields; A dependency-aware rollback planner that stops when a later mutation depends on an earlier one; A recovery report that distinguishes restored, changed-by-owner, expired-session, and irreversible states


## Changes it proposed to its own stack

### `relay` — Add a reconnect-safe intent coordinator between the pendant event stream and the existing job/execute/receipt routes. Each intent gets a device-generated idempotency key, capturedAt, expiry, required-context hash, authorization class, and target surface. On reconnect, the coordinator leases one intent at a time, revalidates Mac/browser session and context versions, atomically transitions queued→leased→executing→receipt, and parks stale or irreversible intents in conflict_pending. Duplicate events return the original receipt; cancellation wins before lease; every transition is emitted through /pipeline/events and exposed through the existing job status/receipts APIs.
- **owner gets:** A sentence spoken in a dead zone becomes one safe action instead of being lost, duplicated, or applied hours later to the wrong page. The owner gets a clear pending/conflict/complete answer and can cancel before anything consequential happens.
- effort: Medium-high: relay state machine and schema, pendant reconnect event integration, Mac/browser precondition probes, and dashboard/spoken status handling; deterministic tests for crash/retry/race cases.  ·  risk: A crash between side effect and receipt can still create uncertainty; recover with idempotency keys, read-after-write verification, and a parked 'unknown outcome' state rather than retrying blindly. Expired browser sessions or changed pages must halt. Roll out read-only/reversible intents first.
- cost: Small persistent queue/metadata cost; no extra model call for normal cases. Occasional background conflict classification is <$0.01. No hardware cost.  ·  latency: Offline capture is local; reconnect adds one validation round trip (typically <2 seconds) before execution. Paused conflicts intentionally wait for owner input.
- security: Encrypt queued payloads, minimize retained content, bind leases to device and owner, and enforce fresh confirmation for destructive/browser-submit classes. Do not log secrets in receipts.
- depends on: offline_intent_spool on the pendant or an equivalent local durable queue; action lease and cancellation semantics; typed Mac/browser precondition and outcome verification; owner-facing pending/conflict review surface

### `integration` — Add strict typed-action validation and canonicalization at the /execute/mac action boundary before a job is persisted or sent to the Mac. Validate required fields by action type (open_app.appName, run_shell.command, run_applescript.script, etc.), reject malformed plans with a structured validation_error and repair hint, and preserve the original natural-language command separately. Add contract tests that exercise planner output through /execute and ensure no misleading 'failed execution' receipt is created for a request that never reached an executor.
- **owner gets:** Recent jobs for 'Launch/Activate/Open AI Pendant Browser Bridge' were recorded as failed because required fields were missing, even though the intended action was never attempted. The owner gets an honest, immediately repairable explanation instead of a confusing failed-action history.
- effort: Low-medium: shared action schema, preflight validator, planner serializer fix, route tests, and dashboard rendering for validation errors.  ·  risk: A schema that is too strict could reject a newly supported action; version the schema and allow an explicit compatibility envelope. Existing malformed jobs remain historical but become clearly classified.
- cost: Negligible CPU/storage; reduces wasted Mac/model calls.  ·  latency: Adds milliseconds of local validation; avoids unnecessary executor round trips.
- security: Improves safety by preventing under-specified shell/script actions from reaching execution. Validation errors must not echo secrets embedded in commands.
- depends on: typed action definitions behind POST /execute; planner-to-action serialization contract; receipt status taxonomy distinguishing validation_error from execution_failed


## What it asked for

_Nothing._
## Its own summary

Discovered live state: Mac bridge is online and healthy (v0.5.0), Chrome bridge is offline with zero tabs, and no pendant is currently connected. Existing pipeline proves 24 kHz mono PCM rendering is functioning on the Mac→relay leg (24,000 Hz, 16-bit, no clipping), while one live audio input was 15,625 Hz; end-to-end pendant acceptance remains unverified. I recorded two new items: a reconnect-safe offline-intent coordinator that adds leases, idempotency, expiry, context/session preconditions, conflict parking, and receipt reconciliation across pendant/relay/Mac/browser; and strict typed-action preflight validation, motivated by live jobs that were falsely recorded as execution failures when required fields (appName/command/script) were missing. I still need a connected pendant and online browser bridge to verify the physical/reconnect path, the owner-controlled TCC/browser-bridge setup, and the already-pending 24 kHz acceptance criteria and audio probe. I will not re-request the denied TCC grants or already-pending tools.

**Biggest unknown:** Whether the pendant's actual microphone/playback firmware and reconnect event path can sustain the intended 24 kHz end-to-end behavior; current evidence only verifies Mac-side TTS output and relay acceptance.

