# Harness derivation — faculty-action — round 184

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac harness permissions and browser bridge** — As of round 184, GET /ops/status reports AI Pendant Agent ready with Accessibility and Screen Recording granted, all listed automation grants present, browser bridge online in Safari with one Start Page tab and zero pending commands. This supersedes older denied-permission context for current live state.
  - evidence: GET /ops/status returned HTTP 200 with permissions.accessibility.trusted=true, screenRecording.granted=true, requiredMissing=[], browser.online=true, pendingCommands=0.

## Capabilities it proposed

### ""Finish the checkout form, but stop before the final purchase and ask me on the pendant.""
- **useful because:** This makes the system useful for real multi-step browser work without turning a spoken request into an irreversible purchase: the Mac/browser can fill and validate fields, faculty-perception independently checks each checkpoint, and the pendant remains the only place that can release the final commit.
- **path:** relay-realtime → mac-planner → browser-extension → mac-vision → faculty-perception → faculty-judgement → faculty-action
- **model tier:** background for planning and field extraction; realtime only for the owner's spoken confirmation
- **latency:** Visible progress within 2 seconds per step; verification under 1 second; pause indefinitely at the commit checkpoint until physical approval.
- **cost:** Usually 1–3 cheap planner/verification calls plus browser actions; realtime cost only for the final conversational prompt. Browser screenshots and form values dominate payload size.
- **security:** Never send payment secrets to the pendant or relay. Mask sensitive fields in evidence. Require the existing physical_transaction_approval_latch for the final commit, and independently verify that the page, merchant, amount, and destination still match the approved digest immediately before submission.
- **missing:** A transaction-level coordinator that binds browser command IDs, operation/step IDs, approval nonce, and verifier receipts into one durable record.; A browser-side redaction and stable locator contract for sensitive fields.; An explicit final-submit action class routed through the existing owner policy rather than an invented default.

### ""I plugged the pendant in. Run the complete bench acceptance test and tell me exactly what failed, without flashing anything.""
- **useful because:** The owner can turn today's physically connected USB pendant and ESP32 bridge into an honest, repeatable hardware test session instead of guessing from firmware labels. The Mac gathers serial and audio evidence, the relay stores a receipt, and perception reports measured pass/fail criteria.
- **path:** mac-terminal → mac-planner → relay-realtime → faculty-action → faculty-perception → dashboard-ux
- **model tier:** background/cheap model for test orchestration and report synthesis; realtime only to answer a spoken follow-up
- **latency:** Discover ports and begin within 3 seconds; a 30–60 second audio run is acceptable; return a concise spoken result plus a durable detailed receipt.
- **cost:** One orchestration call and one report call; audio fixture data should remain local and only hashes/metrics leave the Mac. The dominant cost is the 30–60 second device measurement, not tokens.
- **security:** Read-only by default: no flashing, reset, or source modification. Explicitly display the serial paths and test duration before starting. Store raw UART/audio locally, upload only selected metrics and hashes, and distinguish 'not connected' from 'failed'.
- **missing:** A concrete read-only Mac diagnostic operation with enum values for serial_ports, jlink_probes, build_status, and test_results.; A serial capture adapter that can correlate nRF9160 and ESP32 lines with timestamps without exposing secrets.; A test runner that invokes the existing audio_path_probe and scripts/audio-quality-probe.mjs, then persists provenance in a job receipt.

### ""I'm on the move—capture what I say, don't make me look at the Mac, and bring the unfinished things back when I'm stationary.""
- **useful because:** A wearable should adapt to whether the owner's hands and attention are available. IMU-derived motion state can keep the pendant in capture-only mode during walking or transit, prevent surprise Mac/browser actions, and later resume the queued work when the owner is still—without relying on a guessed calendar or a manually toggled mode.
- **path:** pendant → relay-realtime → mac-planner → faculty-judgement → faculty-action → faculty-perception
- **model tier:** tiny/local classifier for motion state and queue policy; background model for later transcription and task grouping; realtime only for capture acknowledgement
- **latency:** Local motion classification and haptic acknowledgement under 100 ms; no screen action while moving; resume prompt within 5 seconds of a stable stationary window.
- **cost:** Near-zero token cost for local classification; one background transcription/grouping call per captured item. IMU summaries (not raw motion traces) are enough for the relay.
- **security:** Do not infer or retain a location. Keep raw IMU on-device and upload only coarse states with short retention. Motion must be a safety throttle, never authorization: consequential actions still require the existing approval latch and fresh verification. Provide an explicit physical override for false positives.
- **missing:** Firmware integration for the owned LSM6DSOX on enabled i2c2, with a small motion-state event protocol and calibration persistence.; Relay state machine that changes permissible action classes while moving and reopens them after a stationary hysteresis window.; A durable association between captured utterances and deferred Mac/browser jobs, with expiry and cancellation semantics.

### ""After you finish, tell me exactly what changed—not just that it succeeded—and let me challenge any change before it becomes permanent.""
- **useful because:** Today the system can execute jobs and collect receipts, but the owner cannot obtain one coherent, human-readable before/after account across a Mac app, files, and a browser session. This gives them an inspectable change ledger: what was intended, what actually changed, what was independently observed, and which parts remain unknown, without exposing secrets to the pendant.
- **path:** relay-realtime → mac-planner → browser-extension → mac-vision → faculty-action → faculty-perception → faculty-judgement → dashboard-ux
- **model tier:** Cheap background model for diff normalization and summarization; realtime only for the owner's spoken challenge or approval.
- **latency:** A short spoken summary within 3 seconds of completion; detailed evidence available within 10 seconds. Challenging an item pauses only the affected compensating action, not unrelated completed work.
- **cost:** One small summarization call per composite operation. Hashes and structured diffs should remain local; screenshots or snippets are fetched only for a challenged item.
- **security:** Evidence must be sensitivity-labelled and redacted before leaving the Mac/browser. Never claim a change was undone unless a fresh postcondition verifier confirms it. A challenge must create a new operation, not mutate historical receipts, and irreversible external effects must be marked permanently non-compensable.
- **missing:** A cross-surface change ledger that records intended effect, observed before-state, observed after-state, provenance, sensitivity, reversibility, and unknowns per step.; A user-facing challenge protocol that maps a spoken objection to a specific ledger item and creates a compensating plan requiring the existing physical approval latch where appropriate.; Stable before-state capture for files, app state, and browser fields; current receipts are execution-centric rather than a complete causal diff.

### ""Cancel everything the pendant has authorized or queued right now.""
- **useful because:** There is no single physical escape hatch today. A pendant gesture should be able to revoke pending relay work, cancel queued Mac jobs, withdraw browser commands, and mark already-running operations as stopped or unknown, even when the owner cannot reach the Mac. This is materially different from approving or undoing one job.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-action → faculty-perception
- **model tier:** Deterministic firmware/relay control path; no model call for the stop itself. A background model may later explain which operations were stopped or remain unknown.
- **latency:** Revoke new execution within 250 ms at the relay; propagate cancellation to Mac and browser within 2 seconds; return a haptic acknowledgement even if the Mac is offline.
- **cost:** Negligible token cost. Small durable revocation records and cancellation receipts dominate storage, not API usage.
- **security:** This must be fail-closed and idempotent: revocation prevents new work but cannot pretend to reverse an external side effect already submitted. Use a monotonic epoch, signed device event, replay protection, and explicit stopped/unknown outcomes. Never put secrets or page contents on the pendant.
- **missing:** A global revocation epoch enforced by relay, Mac executor, and browser command poll/result paths.; A pendant-resident emergency-stop gesture distinct from ordinary recording/bookmark and approval gestures, ideally using the future rotary/button hardware or a deliberately documented two-button chord.; A cancellation receipt that independently reports which workers observed the new epoch and which operations are irreversibly unknown.

### ""Answer privately when my AirPods are connected; otherwise give me only a haptic cue and put the full answer in a safe place on the Mac.""
- **useful because:** The owner cannot safely use the same spoken response mode everywhere. This capability routes content according to the actual listening path: private audio through the ESP32 bridge when authenticated AirPods are present, a nonverbal cue when they are not, and a retrievable full answer on the Mac. It prevents secrets, messages, and reminders from being spoken aloud in public.
- **path:** pendant → ESP32 audio bridge → relay-realtime → mac-planner → faculty-judgement → faculty-action
- **model tier:** Deterministic routing for privacy state; cheap model only for compressing a response into a safe haptic/status summary.
- **latency:** Detect route changes within 1 second; deliver a haptic-only fallback within 300 ms; never wait on a long model call before choosing the safe route.
- **cost:** Negligible additional model cost; Bluetooth/bridge presence telemetry and a small local status record are the main resources.
- **security:** Presence is not identity: require a paired bridge/session token and fail closed when its state is stale or ambiguous. Do not speak secrets merely because a Bluetooth device is nearby. Full text remains on the Mac with sensitivity labels and expires according to policy.
- **missing:** A bridge capability event reporting authenticated AirPods route, freshness, and confidence to the relay.; A response policy that classifies content sensitivity before audio rendering and has a guaranteed haptic/status fallback.; A local Mac inbox for private deferred responses with retention and explicit readout controls.


## Changes it proposed to its own stack

### `firmware` — Integrate the owned LSM6DSOX on i2c2 and add a low-rate motion-state publisher (still, walking-like, vigorous/unknown) with hysteresis, calibration version, sequence number, and a physical override event. Publish only state transitions and aggregate confidence; never raw accelerometer traces. Keep the existing two-button recording/bookmark behavior unchanged.
- **owner gets:** The pendant can recognize that the owner's hands are busy and safely defer Mac/browser work while still capturing thoughts, then resume when attention is available. It also makes the device feel like jewelry rather than a tiny remote with a screen.
- effort: Medium: enable/configure i2c2, add sensor driver and calibration, bounded state machine, UART/relay event framing, and bench validation against known motions.  ·  risk: False motion classification could delay an action or cause an unwanted prompt. Use conservative defaults (capture-only), hysteresis, an explicit sw1 override, watchdog recovery, and log only aggregate counters. If the sensor is absent, fall back to stationary/unknown and never unlock risky actions.
- cost: No new hardware cost; roughly tens of KB flash and a few KB RAM. IMU polling adds modest MCU duty cycle and battery draw, to be measured rather than assumed.  ·  latency: State transitions can be available in 100–300 ms; no impact on 24 kHz codec if polling is low priority and bounded.
- security: Motion state is sensitive behavioral metadata; keep raw data local, minimize retention, and treat it only as a safety throttle—not consent or identity.
- depends on: Enable i2c2 in the pendant devicetree; A relay protocol for motion-state transitions; The existing physical_transaction_approval_latch remains the only authorization for consequential actions


## What it asked for

_Nothing._
