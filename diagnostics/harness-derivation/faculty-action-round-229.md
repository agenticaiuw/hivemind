# Harness derivation — faculty-action — round 229

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “remember this moment,” capture the pendant audio bookmark and the exact Mac/browser context I was looking at, then file one searchable note I can return to later."
- **useful because:** The owner can preserve the meaning of a fleeting moment without stopping to explain which app, page, or document was on screen; the worn button supplies time-local intent while the Mac supplies context the pendant cannot see.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background for note assembly; realtime only to acknowledge capture
- **latency:** haptic acknowledgement under 300 ms; context snapshot under 3 s; filing may finish asynchronously
- **cost:** Low: one small realtime event plus a cheap background summarization call; storage and Mac/browser reads dominate, not model tokens.
- **security:** Context may include private page text or secrets. Default to app name, URL, document title, selection hash, and a short user-approved snippet; never upload passwords or page bodies by default. Filing a note is reversible and may be proactive; external sharing is never implied.
- **missing:** A typed cross-surface moment record schema linking pendant event ID, Mac observation, browser session, and resulting note; A Mac/browser context snapshot route that returns provenance without requiring Screen Recording; A note writer that atomically links raw capture, redacted context, and final note

### "If I say “do it” after asking you to change something, execute the staged action only if the exact app, account, target, and final state still match what I approved; otherwise keep it pending and tell me what changed."
- **useful because:** This is the single most useful action capability: it turns conversational intent into dependable real-world completion without silently acting on a stale tab, wrong account, or changed form. It combines the pendant's deliberate confirmation with independent postcondition truth.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-judgement → faculty-perception → faculty-action → dashboard
- **model tier:** Realtime for the short approval exchange; deterministic routes and a cheap verifier for execution and commit
- **latency:** Approval feedback under 500 ms; preflight under 2 s; execution may take minutes but must expose progress and final truth
- **cost:** Low-to-moderate: mostly deterministic Mac/browser calls; one verifier/model call only when the UI is ambiguous. Cost is dominated by long-running browser workflows.
- **security:** The pendant receives only an opaque transaction summary, digest, expiry, and outcome—not secrets or page contents. Bind approval to target/account/final-state digests, expire quickly, reject replay, and require confirmation for destructive or external-send classes. If verification is unavailable, report unknown and never claim success.
- **missing:** A commit coordinator that binds physical_transaction_approval_latch to an action plan digest and attempt ID; A mandatory verify_operation_step call for every externally visible postcondition before marking committed; A stable browser identity/account locator and stale-state detection in the browser harness

### "While I am walking or moving, keep risky computer actions staged; let me approve harmless actions, but require me to be still and deliberate before sending messages, buying, deleting, or changing security settings."
- **useful because:** The pendant is worn in motion and a pocket press, stumble, or accidental contact should not approve a consequential action. Using motion as a safety signal makes the physical approval boundary fit daily life rather than assuming a desk posture.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-judgement → faculty-action → dashboard
- **model tier:** Realtime only for sensor/event classification; deterministic policy for gating and action routing
- **latency:** Motion classification under 200 ms; haptic explanation immediately; safe actions continue without perceptible delay, risky actions wait for stillness
- **cost:** Low: IMU sampling and local thresholds are cheap; no model call is needed for ordinary still/moving classification. Firmware integration and calibration dominate.
- **security:** Motion is a safety signal, not consent. Never use stillness alone as approval; combine it with the existing nonce-bound deliberate gesture. Keep raw IMU local, transmit only coarse state and confidence, fail closed on sensor/link faults, and allow an emergency cancel gesture.
- **missing:** Firmware integration for the owned LSM6DSOX (enable i2c2, sampling, calibration, local motion-state FSM); A motion_context_safety_gate policy seam that classifies action risk and combines motion state with physical_transaction_approval_latch; A user-visible calibration and override flow that does not weaken the safe default

### "Let me say “prepare this for later” and have the system carry the task across the relay, Mac, and browser until the exact prerequisites are true, then ask me once—without losing the page, draft, files, or reasoning if any device sleeps or disconnects."
- **useful because:** Today a task that spans a logged-in browser, local files, and a later human decision is fragile: a dropped link or sleeping Mac forces the owner to reconstruct it. This would make the system a durable personal handoff rather than a one-shot command runner.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-judgement → faculty-perception → faculty-action → dashboard
- **model tier:** Background model for decomposition and resumption; realtime only for the final concise prompt and physical confirmation
- **latency:** Capture and acknowledgement under 1 s; resumption within 10 s of prerequisites becoming true; no requirement that all devices be online simultaneously
- **cost:** Moderate: durable state and periodic cheap checks dominate; use the expensive model only when a prerequisite or plan meaningfully changes.
- **security:** Persist only encrypted references and redacted summaries, never browser secrets or page contents in the relay. Bind every resume to the original plan, expiry, account, and target digest. Require fresh verification and approval before external or destructive effects.
- **missing:** A durable cross-surface task object with checkpoints, prerequisite predicates, expiry, and resumable artifacts; Atomic handoff/import/export between relay, Mac planner, and browser session; A scheduler/event watcher that wakes only on relevant prerequisite changes; A human-readable recovery view showing exactly what is ready, blocked, or stale

### "Give me a private “show me only what I need” mode: when a task involves sensitive browser or Mac content, let the browser keep the real values local while the pendant and relay receive only structured facts, redacted previews, and a one-line action summary."
- **useful because:** The owner can use the hive for banking, health, work, and private communications without putting page contents or secrets into the relay or spoken audio. This is a usable privacy boundary, not merely a promise not to log data.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** Local deterministic extraction first; a small background model may classify/redact; realtime model receives only the sanitized projection
- **latency:** Redaction and projection under 300 ms for ordinary fields; complex pages under 2 s; never delay an emergency cancel
- **cost:** Low-to-moderate: local extraction is cheap; occasional background classification for unknown fields. Storage and encryption dominate.
- **security:** Default-deny transmission for unknown fields; typed sensitivity labels for normal/private/secret; secrets remain in the browser process. Redaction must be fail-closed, with hashes or opaque handles instead of guessed masking. Owner can inspect and revoke each projection.
- **missing:** A browser-side typed redaction engine that understands form fields, account identity, message bodies, and payment/security secrets; A capability-based projection token so relay actions can refer to a local value without receiving it; End-to-end audit records proving what left the browser and which model saw it; A pendant vocabulary for saying “withhold details” versus “read details aloud”

### "When the system cannot finish a multi-device task, hand me a precise recovery card: what step completed, what remains uncertain, what I can safely retry, and what must not be repeated—available by voice on the pendant and as a full view on the Mac."
- **useful because:** A truthful partial failure is more useful than “something went wrong.” The owner can recover from a dropped connection, browser navigation, or Mac sleep without duplicate purchases, messages, or edits.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-perception → faculty-action → dashboard
- **model tier:** Deterministic receipt/state synthesis; cheap background model only to compress the explanation into one spoken sentence
- **latency:** Recovery status under 2 s after a failure; pendant summary under one spoken sentence; detailed Mac view can load asynchronously
- **cost:** Low: mostly existing receipts and verifier results; model cost is limited to wording ambiguous recovery summaries.
- **security:** Do not speak sensitive values aloud. Use opaque step IDs and redacted target labels. The retry recommendation must be derived from idempotency and verified state, never guessed. Require confirmation for any retry with external side effects.
- **missing:** A structured partial-completion state machine with per-step idempotency and retry safety; A receipt synthesizer that distinguishes completed, failed, unknown, cancelled, and never-started; A cross-surface recovery-card protocol and compact haptic/voice encoding; A user-facing history that retains the card until acknowledged or superseded


## Changes it proposed to its own stack

### `firmware` — Integrate the owned LSM6DSOX on i2c2 and add a local motion-state stream (still, walking, abrupt-motion, sensor-fault) with hysteresis, calibration, and a compact signed state report. The stream must never authorize an action; it only informs the relay policy gate and remains safe when stale or disconnected.
- **owner gets:** Consequential approvals will not accidentally happen from a moving hand or pocket bump, while harmless actions stay fast. The owner gets a physical safety boundary that matches how a pendant is actually worn.
- effort: Medium: devicetree and driver integration, calibration persistence, bounded sampling task, signed event format, and bench validation against the existing 211,608 B application RAM budget.  ·  risk: False movement could delay an action; false stillness must never approve one. Recover by failing closed, expiring state quickly, exposing a cancel gesture, and logging sensor-fault reasons without raw motion upload.
- cost: No new hardware cost; roughly 1–5 mA while sampling depending on duty cycle, plus small firmware flash/RAM use. No API cost for local classification.  ·  latency: Under 200 ms for state transitions with a 25–50 Hz sample loop; no added delay for low-risk actions.
- security: Improves safety only when combined with the existing nonce-bound physical approval. Raw IMU stays local; relay receives coarse state, confidence, counter, and expiry.
- depends on: Enable &i2c2 and integrate the owned LSM6DSOX; motion_context_safety_gate policy seam; physical_transaction_approval_latch

### `integration` — Add a target-binding firewall before browser or Mac execution: normalize the planned app, browser session, account identity, target recipient/resource, and final-state digest; require an exact match against the approved plan, and route any mismatch to pending rather than executing. Store the comparison and verifier provenance in the action ledger.
- **owner gets:** A stale tab, switched account, changed recipient, or edited amount becomes a safe pause instead of an embarrassing or expensive mistake. The owner can trust that “do it” means the thing they actually saw and approved.
- effort: Medium: canonical binding schema, browser identity locators, preflight comparison, executor hook, and ledger/receipt fields; no new physical hardware.  ·  risk: Sites with unstable DOM identifiers may create false mismatches and require re-approval. Recovery is explicit re-preview and approval, never a fuzzy fallback for high-risk actions.
- cost: Low API cost; mostly deterministic hashing and existing browser/Mac actions. One extra verification call for ambiguous identity.  ·  latency: Adds about 0.5–2 seconds before execution for preflight and verification; no material cost after a stable binding.
- security: Reduces confused-deputy and replay risk. Secrets remain in the browser; only normalized identity labels and digests cross the relay boundary.
- depends on: A commit coordinator for physical_transaction_approval_latch; verify_operation_step with attempt/action correlation; Stable browser session/account identity metadata


## What it asked for

_Nothing._
