# Harness derivation — faculty-action — round 189

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""When I'm back at my Mac, finish the draft application in the browser, but stop before any irreversible submit and ask me on the pendant.""
- **useful because:** Lets the owner state a goal while away and have the system resume only when the Mac and authenticated browser session are actually available. It crosses relay persistence, Mac presence, browser session, pendant approval, and independent verification instead of making the Mac do a one-shot task.
- **path:** relay-realtime → mac-planner → browser-extension → faculty-judgement → faculty-action → faculty-perception
- **model tier:** background for waiting/state reconciliation; realtime only for the owner's short confirmation conversation
- **latency:** Immediate acknowledgement; resume within 10 seconds of Mac/browser presence; no action after a 24-hour expiry without re-asking.
- **cost:** Usually <$0.01 per invocation; background polling/state events dominate, with a small model call only when the saved goal needs replanning.
- **security:** Persist only a redacted goal and opaque session/job IDs, never form secrets or page contents in relay state. Require physical_transaction_approval_latch at the irreversible boundary. Abort on browser account/session change, stale page, or expired intent; verify the postcondition independently after execution.
- **missing:** presence/unlock event from the Mac bridge; a durable deferred-goal record distinct from the existing offline audio OUTBOX; browser-session identity and expiry binding; a planner/action contract that can pause at an irreversible boundary and resume without duplicating prior steps

### ""Clean up these files, but show me exactly what will change and let me approve one grouped change on the pendant; if anything differs during execution, stop and leave the rest untouched.""
- **useful because:** Gives the owner a genuinely safe batch operation: a Mac-side action can prepare a concrete diff, receive one physical approval for that exact digest, apply only the unchanged set, and stop safely on drift. This is more useful than approving every file individually and safer than trusting an executor receipt.
- **path:** relay-realtime → mac-planner → mac-terminal → faculty-judgement → faculty-action → faculty-perception
- **model tier:** background/cheap model for grouping and summarizing; realtime only to answer clarification or approval prompt
- **latency:** Preview in under 15 seconds for up to 100 files; approval expires in 10 minutes; apply and verify within 30 seconds.
- **cost:** <$0.02 for a normal batch; filesystem inspection and diff generation dominate, not model tokens.
- **security:** Approval envelope contains only operation ID, file-list digest, byte counts, and reversible/irreversible class—not file contents. Require owner approval for destructive groups. Recheck every file hash immediately before mutation, execute atomically per group, and independently verify resulting file state; report partial completion explicitly.
- **missing:** a first-class dry-run/diff receipt with stable per-item hashes; grouped approval envelope support in physical_transaction_approval_latch; atomic per-group executor with drift detection; file-state verifier support for directory trees and rollback of reversible moves

### ""If I lose the link while you are doing something important, tell me whether it completed, is definitely safe to retry, or is unknown—and give me one safe recovery action on the pendant.""
- **useful because:** The owner gets a truthful decision at the moment failures matter: not a generic error, but a classified outcome based on fresh Mac/browser evidence and a safe recovery path. It combines executor receipts, independent perception, and a physical recovery gesture.
- **path:** relay-realtime → mac-planner → browser-extension → faculty-action → faculty-perception → faculty-judgement
- **model tier:** cheap background classifier for receipt reconciliation; realtime only when speaking the concise result to the owner
- **latency:** Classify within 5 seconds of link restoration; never auto-retry an unknown side effect; recovery action expires after 15 minutes.
- **cost:** <$0.01 per incident; dominated by one verifier call and a small reconciliation model call.
- **security:** Use idempotency keys and operation-step IDs. Independent verifier must inspect only the specified app/file/browser postcondition and return provenance, not secrets. Pendant recovery gesture may cancel or retry only when the operation is proven safe-to-retry; unknown remains staged for explicit approval.
- **missing:** a standard three-state outcome schema (verified-success, safe-to-retry, unknown) in job receipts; automatic verifier invocation after reconnect; idempotency-key propagation through browser and Mac action executors; pendant recovery UI/haptic patterns for retry versus cancel versus unknown

### ""Fill this form from my instructions, but before submitting, read back every field that changed, identify where each value came from, and let me correct any one field from the pendant.""
- **useful because:** Form filling is where a wrong autofill can cause real harm. This gives the owner a compact field-by-field correction loop across an authenticated browser, the Mac planner, and the pendant, rather than an opaque 'done' claim. It is useful even when the owner cannot look at the screen.
- **path:** relay-realtime → browser-extension → mac-planner → faculty-perception → faculty-judgement → faculty-action
- **model tier:** cheap model for extraction and field summaries; realtime only for the owner's corrections and final confirmation
- **latency:** Draft and provenance list within 15 seconds; each correction under 3 seconds; submission requires a fresh physical approval and postcondition verification.
- **cost:** <$0.03 per form, dominated by browser inspection and a few structured model calls; never send raw secrets to the relay model.
- **security:** Keep secret fields masked and local to the browser agent. Each proposed value carries source class (owner utterance, existing page value, local file, or inference); inferred values are never submitted without explicit correction/approval. Bind approval to a digest of field names and values, invalidate on any page mutation, and independently verify the submission result.
- **missing:** field-level browser extraction and redacted diff route; a pendant interaction protocol for selecting/correcting one field (rotary encoder plus second button would make this practical); source/provenance metadata in browser command receipts; digest-bound final approval and verifier postconditions for submitted forms

### ""When I turn the pendant face-down, make the whole system private immediately—and when I pick it up, tell me what was paused before anything resumes.""
- **useful because:** This gives the owner a physical, screen-free privacy boundary that spans the actual hive: the pendant stops capture locally, the relay stops accepting or forwarding live audio, and Mac/browser work pauses rather than continuing while the owner expects privacy. On return, it reports a bounded pause receipt instead of silently resuming.
- **path:** relay-realtime → mac-planner → browser-extension → faculty-action → faculty-perception → unified
- **model tier:** Firmware and relay state machine; no model call for the immediate privacy transition. A cheap background model may summarize paused work only after the owner explicitly asks.
- **latency:** Local microphone mute and LED/haptic acknowledgement under 100 ms; relay revocation under 1 second; resume requires an explicit owner gesture and a fresh state check.
- **cost:** Negligible per event; mostly firmware and relay implementation. Optional summary costs <$0.01.
- **security:** The privacy transition must fail closed: local mute happens before any network event, queued microphone data is not uploaded, and in-flight Mac/browser actions are cancelled or frozen at their next safe boundary. Face-down detection must have a deliberate confirmation gesture or configurable debounce to prevent accidental pauses. Never infer that picking up means consent to resume; require explicit resume. Persist only timestamps, state transitions, and opaque job IDs.
- **missing:** firmware IMU integration and a calibrated face-down gesture on the owned LSM6DSOX; a relay-level kill/resume lease that immediately rejects audio and pushes pause to Mac/browser agents; executor pause-at-safe-boundary semantics for active jobs; a local privacy-state indicator and crash-safe state persistence; an explicit resume gesture, preferably the incoming rotary encoder/second button rather than overloading sw0

### ""If the pendant detects that I may have fallen, buzz me, give me a short chance to cancel, and if I do not respond, notify my chosen emergency contact with only my preset message and the time.""
- **useful because:** A worn device can notice a physical event when the Mac, browser, and relay cannot. It turns the pendant into a safety net without opening the microphone: local IMU detection, local countdown/haptic confirmation, relay delivery, and a narrowly scoped message are useful even when the owner cannot reach a screen.
- **path:** relay-realtime → faculty-action → faculty-perception → unified
- **model tier:** No model for detection or escalation; deterministic firmware thresholds and a relay template. Model use is optional only for an owner-requested post-event summary.
- **latency:** Detect and alert locally within 2 seconds of a confirmed event; 20–30 second cancel window; relay delivery retry for 10 minutes.
- **cost:** Low per event; SMS or chosen notification provider dominates. No continuous inference API cost.
- **security:** Must be opt-in, with a hardware-local cancel gesture and a loudness/haptic test mode. Never transmit audio, coordinates, contacts, or health inference beyond the preset message and timestamp. Require explicit emergency-contact configuration and surface false-positive history. If link is unavailable, queue a minimal alert envelope and disclose delivery uncertainty.
- **missing:** validated fall/impact and immobility firmware using the owned LSM6DSOX; local countdown and haptic driver integration via i2c2/DRV2605L; relay emergency notification route with delivery receipts and bounded retry; owner-configured contact/message and a clear opt-in policy

### ""Let this sensitive task run only while I am actively wearing the pendant; if it leaves my body or stops acknowledging me, revoke the lease before the next external side effect.""
- **useful because:** A single approval is insufficient for a long workflow: the owner may walk away, lose the pendant, or change their mind. A renewable physical presence lease makes consent continuous and lets the wearable revoke a queued Mac/browser action before its next irreversible step.
- **path:** relay-realtime → mac-planner → browser-extension → faculty-action → faculty-perception → unified
- **model tier:** Deterministic lease and device signals; use a cheap model only to explain the paused workflow. No realtime model is needed for enforcement.
- **latency:** Lease renewal every 5 seconds; revoke locally and at relay within 1 second of a missed renewal or explicit cancel; executor must honor the boundary before each side effect.
- **cost:** Negligible API cost; implementation work is in firmware, relay, and executor checkpoints.
- **security:** The pendant must not send secrets or page contents. Use monotonic counters, expiry, and a per-operation digest. Fail closed on clock/link ambiguity, replay, or device reset; report the operation as unknown rather than claiming cancellation. Do not use face-down inference alone as proof—combine an explicit start gesture with periodic local acknowledgement.
- **missing:** renewable lease protocol bound to operation-step digest; device-local presence/acknowledgement signal using the owned IMU and haptic hardware; executor checkpoints that refuse side effects after lease expiry; relay fan-out of revocation to Mac and browser agents plus independent verification


## What it asked for

### `s11-n2sf` (skill) — tactile_action_outcome_beacon
- does: When the relay sends a signed operation outcome, the pendant renders a short haptic pattern for verified success, safe-to-retry, unknown, or cancelled. A press acknowledges the pattern; it never approves or executes an action. If several outcomes arrive offline, it queues only compact event IDs and presents them oldest-first.
- must be on-device because: The owner may be away from a speaker, screen, or network and needs a private, immediate distinction between success and uncertainty. The pendant is the only surface that can deliver this offline and without opening a microphone.
- trigger: Relay push event, then local button acknowledgement; queued events replay after reconnect.
- storage: At most 16 compact envelopes in the existing typed inbox; roughly 64 bytes each plus manifest metadata, under 2 KB total. Delete only after acknowledgement is durably reported.
- RAM budget: About 8 KB for queue, I2C/DRV2605L driver state, pattern table, and event parser; well below the 211,608 B application RAM, subject to measuring the current firmware image. Requires enabling i2c2 and adding the already-owned DRV2605L/motor wiring; no new hardware.

### `t28-329e` (tool) — mac_presence_snapshot
- why: Deferred cross-surface actions need to know when the owner’s Mac is awake, unlocked, and the bound browser session is available before resuming. Existing get_mac_status reports bridge health but not user/session presence, and browser heartbeat does not establish unlock or session identity.

```json
{
  "type": "object",
  "properties": {
    "max_age_ms": {
      "type": "integer",
      "minimum": 1000,
      "maximum": 60000
    },
    "include_browser": {
      "type": "boolean"
    }
  },
  "required": [
    "max_age_ms"
  ]
}
```

## Its own summary

Recorded four new owner-facing capabilities: resume a deferred goal only when the Mac/browser session is present; digest-bound grouped file changes with drift detection; truthful reconnect outcomes with safe recovery classification; and field-by-field browser form filling with provenance and correction. Also queued device skill s11-n2sf for private haptic outcome beacons using the owned DRV2605L (i2c2 firmware integration required), and requested mac_presence_snapshot tool t28-329e. The common missing connective tissue is not another executor: it is durable pause/resume state, digest-bound approval, field provenance, and independent postcondition verification.

**Biggest unknown:** Whether the Mac bridge can safely expose unlock/presence and a stable browser-session binding without Accessibility or secret leakage. Until mac_presence_snapshot (or an equivalent owner-approved signal) exists, deferred actions must remain staged rather than resume automatically.

