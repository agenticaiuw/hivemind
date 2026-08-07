# Harness derivation — faculty-action — round 72

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Do this across my Mac and browser, and keep going if one step fails—tell me exactly what completed, what did not, and safely undo whatever can be undone.”"
- **useful because:** Today a multi-surface request can leave a half-finished real-world state: a calendar event created but an email draft not, or a browser form changed after the Mac step failed. This gives the owner one durable transaction with explicit checkpoints, idempotent retries, compensating actions, and a concise pendant-visible partial-failure report instead of guessing or silently repeating side effects.
- **path:** faculty-judgement → relay-realtime → relay-job-runner → home-macbook-bridge → browser-extension → pendant → dashboard
- **model tier:** Use the cheap/background planner to compile a typed saga and classify retry/compensation; use realtime only to obtain an owner confirmation for an irreversible step or report a live failure. Deterministic executors and receipts do the actual work.
- **latency:** Queue immediately and acknowledge in under 1 second; reversible steps may run asynchronously. Retry transient failures with bounded backoff, and report each checkpoint within 5 seconds. Pause before any irreversible or ambiguous compensation.
- **cost:** Low API cost: one planning call per transaction plus cheap status synthesis; most execution is deterministic Mac/browser work. Storage is small (step definitions, hashes, receipts, and compensation records), with configurable retention.
- **security:** Never retry non-idempotent actions without an idempotency key and a fresh proof of current state. Require explicit pendant confirmation for sends, purchases, deletion, or compensation that could lose data. Store only redacted before/after evidence; authenticated page content stays on the Mac/relay boundary. A stale browser tab or changed DOM must fail closed, not click by coordinates.
- **missing:** A durable saga/transaction coordinator spanning Mac and authenticated browser jobs; Per-step precondition checks, idempotency keys, retry policy, and declared compensating action; A common receipt schema linking browser command IDs and Mac action receipts; Pendant/dashboard rendering of running, paused, partially-complete, and safely-undoable states; A verified compensation endpoint and owner confirmation handshake

### "“After you do it, verify that the real-world result actually happened—not just that the click or command succeeded—and tell me if it didn’t.”"
- **useful because:** Current automation can report that an action was queued or a UI interaction completed, but the owner cannot reliably know whether the external system accepted it: a calendar invite may not be created, a support form may time out after submission, or a payment may remain pending. This capability closes the loop by checking an independent confirmation surface and escalating ambiguity instead of claiming success.
- **path:** faculty-judgement → relay-realtime → home-macbook-bridge → browser-extension → relay → pendant → dashboard
- **model tier:** Use a cheap background verifier for deterministic polling, matching, and evidence comparison; reserve realtime for speaking an urgent ambiguity or asking whether to retry. Use the expensive model only when evidence conflicts or the verifier needs semantic interpretation.
- **latency:** Return immediate execution acknowledgement, then verify on a task-specific schedule (for example 10 seconds, 2 minutes, and 15 minutes). Speak only on confirmed success, confirmed failure, or a timeout requiring owner input.
- **cost:** Usually a few deterministic reads and one low-cost synthesis; cost is dominated by authenticated browser reads and any repeated verification window, not generation. Retain compact evidence hashes and redacted snippets rather than full pages.
- **security:** Verification must never mutate state or accidentally trigger duplicate submission. Bind it to the original account, tab/session, and expected result; treat a changed login or ambiguous matching record as unknown. Do not infer success from a toast alone. Require confirmation before any remedial retry, cancellation, or duplicate action.
- **missing:** A first-class outcome-verification job linked to an originating action, with expected-result predicates and deadlines; Read-only authenticated browser and Mac probes that can inspect an independent confirmation surface after the originating tab closes; Deduplication and correlation rules for confirmation IDs (event IDs, appointment IDs, order numbers, or message IDs); A receipt schema with execution evidence versus external-outcome evidence as separate states; Pendant/dashboard notifications for confirmed, pending, failed, and ambiguous outcomes


## Changes it proposed to its own stack

### `interaction` — Add a pendant long-press emergency stop protocol distinct from conversation press: holding the sole button for ~1.5 s emits a signed cancel-all-active-jobs event, the relay atomically marks cancellable Mac/browser steps cancelled, and the bridge aborts queued/not-yet-started commands. The pendant gives a short haptic/LED acknowledgement if available (otherwise a distinct LED flash), and the dashboard shows which already-started steps could not be reversed. Require a second press only to resume, never to confirm a destructive action.
- **owner gets:** With no microphone open, the owner can stop a runaway browser click loop, duplicate retry, or unexpectedly long Mac job instantly—even while the voice session is unavailable—without hunting for the Mac window or trusting speech recognition.
- effort: Medium: firmware button state machine and signed event; relay cancellation endpoint plus job-state transition; Mac/browser executors poll cancellation between steps and abort queued commands; dashboard and receipts add cancelled-by-owner reason. Test races between cancel and step commit.  ·  risk: A long press could cancel an important benign job, so distinguish it with a deliberate hold and announce the affected job IDs on the next available audio/status channel. Cancellation cannot retract an already-sent email or completed purchase; receipts must say that plainly. Recover by allowing resume only from a fresh plan, never automatic replay.
- cost: Negligible API cost and storage; one small firmware update. Hardware cost $0 on the prototype; production should add a tactile button with a clear long-press feel, roughly <$1 and no meaningful extra draw.  ·  latency: Local event acknowledgement should be <200 ms; relay cancellation target <1 s, with executor polling at each action boundary.
- security: Use a device-bound signing key and replay-protected event counter; cancellation is high-impact but not destructive, and must be accepted only for the owner's active device/session. Do not transmit microphone audio—button event and job IDs only.
- depends on: Durable job state transitions with atomic cancel-vs-commit ordering; Mac/browser executors honoring cancellation between typed actions; A relay route for signed pendant events and a common active-job index; Owner-facing receipts that distinguish cancelled, completed, and irreversible side effects


## What it asked for

_Nothing._
## Its own summary

Recorded two action-focused gaps. First, a cross-surface transaction coordinator that connects existing /plan, /execute, job receipts, Mac actions, and browser commands with preconditions, idempotent retries, compensation, and honest partial-failure reporting. Second, a genuinely distinct pendant long-press emergency stop: signed button event cancels active queued Mac/browser work without requiring a microphone, with LED acknowledgement and receipts distinguishing completed irreversible effects from cancelled work. What remains needed is implementation of the coordinator’s atomic cancel-vs-commit state machine, executor cancellation polling, signed pendant-event relay route, and the pending permission to modify/build pendant firmware (plus a production tactile button if this prototype graduates).

**Biggest unknown:** Whether the current relay/job runner can atomically prevent a step commit racing with cancellation; until that invariant is tested, 'stop now' can only reliably cancel queued work, not guarantee that an in-flight browser or Mac action has not already committed.

