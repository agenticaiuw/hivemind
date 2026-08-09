# Harness derivation — faculty-action — round 255

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Did you actually send that message, or did it only get drafted? Prove it without sending anything twice.”"
- **useful because:** Today a receipt can say an executor ran while the owner still cannot know whether the final external state changed. This gives a concise, honest answer—verified, draft-only, failed, or unknown—by joining the executor receipt with an independent fresh Mac/browser postcondition check. It is the single most useful trust feature for an action-taking assistant.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for receipt assembly; realtime only to answer the spoken question
- **latency:** Under 3 seconds for a recent job; up to 10 seconds when a fresh browser snapshot is required
- **cost:** Low: one background synthesis plus existing verifier/receipt reads; dominated by a browser snapshot, not model tokens
- **security:** Never expose message body or secrets to the pendant; return status and minimal provenance only. Sending, deletion, and purchase still require the existing approval policy. If verification is stale or contradictory, say unknown and do not retry automatically.
- **missing:** A stable operation/attempt correlation field on executor receipts and verifier calls; A small owner-facing status vocabulary that distinguishes submitted, draft-only, verified, and unknown

### "“Start this multi-step task, but if the Mac, browser, or pendant link changes halfway through, stop at a safe checkpoint and let me resume from there.”"
- **useful because:** A long task currently has an unsafe middle ground: an executor can time out after some steps and a retry can duplicate side effects. This creates resumable transactions with explicit step checkpoints, independent postcondition verification, and a physical pendant resume/cancel choice after interruption. It is useful for workflows such as filing, booking, or editing several apps where partial completion is better than blind retry.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background planner for the step graph; realtime only for the owner's interruption and resume conversation
- **latency:** Checkpoint after every side-effecting step; resume decision surfaced within 2 seconds of link recovery
- **cost:** Moderate: additional verifier calls and durable journal writes; model cost is small compared with browser execution
- **security:** Only resumable steps with declared idempotency and rollback behavior may be auto-retried. Pending state must contain opaque IDs, not page contents or credentials. A physical resume gesture is required after uncertainty; cancellation must be safe and explicit.
- **missing:** Step-level idempotency/rollback metadata in operation plans; A durable checkpoint state machine that survives relay and link restarts; Pendant rendering for resume-vs-cancel distinct from ordinary success

### "“While I’m moving or in a sensitive situation, keep the pendant quiet and only surface urgent alerts; let normal notifications wait until I’m still again.”"
- **useful because:** A wearable assistant should not read private content aloud or distract the owner at the wrong moment. The pendant's owned IMU can classify moving/still transitions locally, while the relay applies an urgency policy and the Mac/browser retain the full notification payload. On becoming still, it gives a compact queued-count cue and lets the owner request a summary.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** device firmware for motion classification; background relay policy for notification ranking; realtime only when the owner asks for the queued summary
- **latency:** Local motion state under 200 ms; notification suppression immediate; queued summary on demand under 3 seconds
- **cost:** Low recurring cost: firmware signal plus one cheap background ranking pass for batched notifications
- **security:** Raw IMU never leaves the pendant. Default to quiet on uncertain motion state. Notifications are encrypted and retained only until acknowledged or expired; secrets and message bodies never enter haptic payloads. Owner-configured urgency rules override model guesses.
- **missing:** Firmware integration of the existing LSM6DSOX on i2c2; A relay notification policy keyed by urgency and motion state; A compact notification inbox/expiry contract between Mac, relay, and pendant

### "“Before you do it, show me everywhere this request would change—apps, files, browser sessions, messages, and the pendant—and let me remove one target without rebuilding the whole task.”"
- **useful because:** The owner cannot currently see the complete cross-surface blast radius of a natural-language request. A single impact map would expose resolved targets, hidden side effects, and missing permissions before execution, then let the owner edit scope surgically. This is not an approval prompt: it is a human-readable, cross-device scope editor that prevents an otherwise correct plan from acting on the wrong account, tab, file, or recipient.
- **path:** pendant → relay → mac-bridge → browser → iOS → dashboard
- **model tier:** background planner for impact analysis; realtime only to answer scope edits
- **latency:** Initial map in 5 seconds; each include/exclude edit re-plans only affected steps in under 2 seconds
- **cost:** Moderate per invocation: fresh host/browser/iOS inspection and one planning pass; much cheaper than recovering a mis-scoped action
- **security:** Display labels and hashes, not message bodies, credentials, or secrets, on the pendant. Treat unresolved targets as excluded by default. Do not execute until the owner explicitly accepts the edited scope under existing action policy.
- **missing:** A typed cross-surface target model (app, file, browser session, iOS object, recipient); Planner support for scope patches without regenerating unrelated steps; A compact pendant/dashboard scope-diff representation

### "“Give me one private, searchable memory of what I saw and decided today, even when the browser, Mac, and pendant were involved—but never save raw audio or page contents unless I ask.”"
- **useful because:** The owner currently has fragmented notes, browser history, action receipts, and voice interactions with no shared, user-searchable decision trail. This would create a privacy-preserving event ledger: local hashes and short owner-approved summaries link a pendant bookmark to the exact browser/app state and decision, so “what did I decide about that?” is answerable without retaining a surveillance transcript.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background summarization and indexing; realtime only for a direct lookup
- **latency:** Bookmark acknowledgement under 1 second; searchable summary available within 30 seconds
- **cost:** Low-to-moderate: one summary/index pass per bookmark; storage and hashing dominate, not realtime inference
- **security:** Raw microphone audio and page contents stay on-device unless explicitly promoted. Store redacted summaries, target hashes, timestamps, and sensitivity labels; encrypt at rest; support immediate deletion and per-source opt-out. The pendant receives only IDs and haptic confirmation.
- **missing:** A user-facing private decision-ledger schema joining bookmark, app/browser state, and action outcome; Local redaction/consent gate before any summary leaves the Mac; Search over the resulting event graph with deletion propagation

### "“If my Mac is lost, stolen, or unexpectedly unlocked, freeze every pending action and tell me exactly what was stopped when I regain control.”"
- **useful because:** The current approval model protects individual actions but does not give the owner a single emergency brake across queued Mac, browser, relay, and pendant work. A device-independent revocation capability would halt not-yet-committed operations, invalidate outstanding approval nonces, and produce a later audit of what was cancelled versus already committed.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic relay/security path; no model needed for the freeze, background model only for the later audit summary
- **latency:** Freeze propagation under 2 seconds while connected; relay must enforce it even if the Mac is offline
- **cost:** Low recurring cost; signed revocation events and queue scans, with a small background summary after recovery
- **security:** The freeze gesture must be physically deliberate and safe under false positives; it must never delete evidence or undo committed external actions. Revocation keys must be independent of the Mac and survive relay restart. Recovery requires a separate owner-authenticated re-enable, not a spoken phrase alone.
- **missing:** A relay-global revocation epoch checked by every executor and browser command; A pendant emergency gesture/hold distinct from ordinary approval and bookmark controls; A recovery ceremony and audit view for stopped versus already-committed work


## Changes it proposed to its own stack

### `relay` — Add a first-class operation_attempt record shared by planner, executor, verifier, undo, and the pendant outcome beacon. Each side-effecting step gets an opaque operation_id, attempt_id, step_id, declared postconditions, idempotency class, and terminal evidence status; receipts and verification results append to the same immutable journal rather than being joined heuristically by timestamps.
- **owner gets:** When the owner asks what happened, the system can point to the exact attempt and step instead of confusing retries, drafts, and similarly timed actions. Failures become safe to explain and resume rather than silently duplicate.
- effort: Medium: schema migration, adapters at execute/verify/undo, and dashboard rendering.  ·  risk: Old jobs lack IDs and must remain readable as legacy/unknown. A bad join could falsely certify a side effect, so certification must require exact IDs and fresh verifier evidence; otherwise return unknown.
- cost: Negligible storage and request overhead; no new model call is required.  ·  latency: Adds one journal append per step and negligible read latency; verification remains the dominant delay.
- security: Opaque IDs reduce accidental content leakage. Never store page contents in the operation record; store hashes/minimal provenance according to sensitivity.
- depends on: The existing verify_operation_step tool; A narrow actionId/attemptId addition to verifier input/output; Existing action ledger and approval handoff

### `firmware` — Integrate the owned LSM6DSOX through i2c2 and emit a tiny signed motion-state event stream (still, walking, vigorous-motion, uncertain) with hysteresis and local raw-data discard. Pair it with a pendant quiet-state bit and bounded notification-count inbox, not audio or raw IMU uploads.
- **owner gets:** The pendant can stop speaking private notifications while the owner is moving, then quietly indicate that something is waiting. It makes the wearable socially safe without requiring the Mac to see or retain movement traces.
- effort: Medium: enable devicetree i2c2, add sensor polling/calibration, low-power thresholds, event signing, and relay policy integration; bench-test over USB before any product transport work.  ·  risk: False still/moving classifications could suppress an urgent alert. Urgent policy must bypass suppression, uncertain must default quiet, and a watchdog should disable sensing rather than block recording/audio. No hardware flashing is authorized by this proposal.
- cost: No new parts; modest battery draw from periodic IMU polling, likely a few mA while active, to be measured on the 500 mAh cell.  ·  latency: Under 200 ms state transitions with a 50–100 Hz sensor sample; negligible impact on the 24 kHz codec if work is event-driven.
- security: Raw accelerometer/gyro data stays local and is discarded; only coarse signed state and counters leave the device.
- depends on: Existing LSM6DSOX and i2c2 wiring; A relay notification urgency policy; A device-event ingestion contract on POST /pipeline/events


## What it asked for

_Nothing._
## Its own summary

Fresh inventory: Mac bridge and Safari are online; the nRF9160 pendant is still offline in the relay device table, so no LTE-dependent execution can be claimed. I recorded five concrete items: (1) owner-facing proof of whether an action was externally committed versus draft/unknown, using receipts plus independent verification; (2) interruption-safe, checkpointed multi-step operations requiring physical resume/cancel after uncertainty; (3) motion-aware privacy suppression using the owned LSM6DSOX; (4) a shared operation/attempt/step correlation journal; and (5) firmware integration for coarse signed motion states with raw IMU discarded locally. The strongest item is truthful postcondition proof: it turns “the click ran” into an honest answer about what actually happened.

**Biggest unknown:** The remaining blockers are implementation contracts, not another discovery round: exact operation_id/attempt_id fields across POST /execute, receipts, undo, and verify_operation_step; a durable checkpoint/idempotency schema; the relay's notification urgency policy; and owner approval of which notifications may bypass quiet mode. The IMU is owned but i2c2 is disabled and firmware changes/flash are not authorized. The pendant's USB bench presence cannot be treated as product transport, and its relay status remains offline.

