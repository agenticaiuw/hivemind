# Harness derivation — faculty-action — round 199

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Undo the last thing you did.” For the next few seconds after a verified Mac/browser action, let me cancel it from the pendant without reopening the app."
- **useful because:** Pre-execution approval protects against unintended actions, but it cannot help when an action was technically authorized yet produced the wrong result. A short, explicit post-action escape hatch makes real-world automation recoverable while the owner still remembers what happened.
- **path:** relay-realtime → faculty-judgement → faculty-action → faculty-perception → mac-planner → browser-extension
- **model tier:** Realtime only to interpret the spoken undo and classify the prior action; background/local code performs the compensating operation and verification.
- **latency:** Outcome beacon within 1 s; undo request acknowledged within 500 ms and compensating action attempted within 3 s. Window expires after a policy-selected 15 s.
- **cost:** ~$0.001–$0.01 per invocation; most work is local routing and verification, with model spend only for ambiguous spoken references.
- **security:** Only actions with a declared, reversible compensator may expose undo. Require the original transaction nonce, owner-visible summary, expiry, and physical confirmation for a destructive compensator. Never claim undone until faculty-perception verifies the postcondition; otherwise report unknown.
- **missing:** A compensating-operation registry keyed by executed operation type; A bounded post-action undo lease and pendant gesture protocol; Verifier support for comparing the restored state to a pre-action snapshot

### "“Show me exactly what is about to happen, then wait.” Have the pendant deliver a compact, spoken-and-tactile action card assembled from the Mac/browser plan before I approve it."
- **useful because:** The current approval primitive can safely gate an action, but a nonce or terse status is not enough to catch a wrong account, recipient, amount, or browser session. A structured preview gives the owner one last chance to detect semantic mistakes without exposing page secrets to firmware.
- **path:** faculty-judgement → mac-planner → browser-extension → faculty-perception → relay-realtime → faculty-action
- **model tier:** Use a cheaper background model/local planner to render a deterministic card; realtime is only for the owner's follow-up or correction.
- **latency:** Card generated in under 2 s after planning; pendant acknowledgement within 1 s; no action may start until the card is accepted or expires.
- **cost:** ~$0.002–$0.02 per card, dominated by planning/context serialization; rendering and delivery are negligible.
- **security:** Allowlisted fields only (app/site, target identity, operation, amount/count, reversibility, expiry). Redact secrets, message bodies, tokens, and arbitrary DOM. Sign/hash the exact card so the approved bytes are the bytes executed; stale cards must be rejected.
- **missing:** A typed action-card schema with sensitivity labels and deterministic redaction; A relay-to-pendant compact renderer for more than success/failure patterns; A commit check binding the approved card digest to the executor receipt

### "“If the Mac vanished halfway through, recover safely.” Resume a pending cross-surface action only after reconnecting to the same browser session and independently checking whether each step already happened."
- **useful because:** A dropped bridge or sleeping Mac currently forces a human to guess whether an email, purchase, edit, or upload happened. Safe recovery should converge on one truthful result—completed, not-started, or unknown—without replaying a side effect.
- **path:** relay-realtime → faculty-action → faculty-perception → mac-planner → browser-extension → unified
- **model tier:** Background/local state machine handles retries and reconciliation; realtime is only needed if the owner asks for an explanation.
- **latency:** Detect stale work within 10 s; reconcile within 5 s of Mac/browser return; never auto-retry an unverified non-idempotent step.
- **cost:** ~$0.001–$0.01 per interrupted job; primarily relay storage and read-only verifier calls.
- **security:** Bind work to browser session identity, operation nonce, step id, and expiry. Treat missing or changed sessions as unknown, not equivalent. Secrets stay on the browser/Mac; relay stores hashes and minimal receipts. Require physical approval again if reconciliation cannot prove the original approval still applies.
- **missing:** A durable per-step state machine distinguishing not-started/running/receipt-present/verified/unknown; Reconnect-time browser session identity and freshness proof; Executor idempotency keys and a recovery endpoint that cannot blindly replay side effects

### "“Make sure this actually went through, and tell me only when it matters.” After I authorize an action such as submitting an application, sending a message, or uploading a file, watch the relevant browser/Mac evidence for the expected external confirmation and alert me on the pendant when it is confirmed, delayed, rejected, or genuinely unknowable."
- **useful because:** Today an automation receipt only says that a local step ran; the owner still has to remember to check whether the outside system accepted it. This closes the loop from intent to externally observable outcome without pretending that a click equals completion.
- **path:** faculty-judgement → faculty-action → faculty-perception → mac-planner → browser-extension → relay-realtime
- **model tier:** Use a background state machine and cheap local checks for polling and parsing. Invoke realtime only when the owner asks a natural-language follow-up or when evidence is ambiguous.
- **latency:** Register a watch in under 2 seconds. Check event-driven browser/email evidence immediately when available, otherwise use bounded backoff (for example 1 minute, 5 minutes, 30 minutes) and stop at the declared deadline.
- **cost:** ~$0.001–$0.03 per watched task; relay scheduling and structured selectors dominate, with model calls only for ambiguous confirmation text.
- **security:** The watch must be scoped to one transaction, one account/session, one expected confirmation, and an expiry. Store hashes and minimal snippets rather than whole mail/page content. Never infer success from absence of an error; return unknown on session loss, changed selectors, or deadline expiry. Require approval before any follow-up action.
- **missing:** A durable outcome-watch primitive with deadline, backoff, selector/evidence specification, and cancellation; A typed confirmation grammar spanning browser fields, URLs, downloaded files, and Mail messages; A pendant status vocabulary for waiting, confirmed, rejected, and unknown, with deduplicated alerts

### "“Keep trying this only while the conditions I named remain true.” Stage a conditional action—such as purchasing, booking, or submitting—then re-check price, recipient, availability, account, and deadline immediately before execution; wake me for physical approval if any condition changes."
- **useful because:** A scheduled automation can become harmful while it waits: a price changes, inventory disappears, or a form's recipient changes. The owner should be able to delegate patience without delegating judgment, and receive one precise reason when the condition no longer holds.
- **path:** relay-realtime → faculty-judgement → faculty-action → faculty-perception → mac-planner → browser-extension
- **model tier:** Background model/local rules evaluate typed predicates and deadlines; realtime is reserved for asking the owner to resolve a changed condition.
- **latency:** Wake on a relevant browser/relay event where possible; otherwise bounded polling. Revalidation must finish within 2 seconds before any side effect, with execution aborted if fresh evidence is unavailable.
- **cost:** ~$0.002–$0.03 per conditional task, dominated by browser/session polling; model use is near zero for typed predicates.
- **security:** Conditions are immutable and signed into the transaction. A stale approval cannot survive a changed predicate, account/session, or deadline. Never silently widen a threshold. Any condition evaluation of private data remains on Mac/browser and returns only pass/fail plus provenance.
- **missing:** A typed predicate/deadline scheduler rather than a free-form reminder; Fresh pre-commit browser and Mac evidence binding conditions to the action digest; A safe wake-and-reapprove path when a condition changes

### "“Tell me when you need my hands, and leave everything else alone.” When a browser task reaches a CAPTCHA, biometric prompt, device approval, or one-time-code step, pause at that exact page, alert the pendant with a redacted explanation, let me complete only the human step, then resume and verify the original task."
- **useful because:** Today an automation either stalls invisibly or pressures the owner to hand over secrets. A bounded human checkpoint would let the system cross the parts only the owner can perform while preserving the browser session, task intent, and audit trail.
- **path:** browser-extension → mac-planner → faculty-action → faculty-perception → relay-realtime
- **model tier:** Local/browser classifiers detect known challenge states; use a small model only to summarize the challenge without reading or transmitting its secret contents.
- **latency:** Challenge alert within 2 seconds; preserve the session for a configurable 5 minutes; resume within 3 seconds after the browser reports the challenge cleared.
- **cost:** ~$0.001–$0.02 per checkpoint; browser events and session retention dominate.
- **security:** The relay and pendant must never receive CAPTCHA images, OTP values, biometric data, or page secrets. Bind resume to the same browser session, tab, transaction digest, and short-lived nonce. If the challenge changes the destination or requested action, stop and require a new approval.
- **missing:** A browser challenge detector and pause/resume protocol; A redacted challenge taxonomy and pendant alert renderer; A session-bound resume nonce plus post-challenge verification


## Changes it proposed to its own stack

### `firmware` — Integrate the owned DRV2605L haptic controller and LSM6DSOX on i2c2, add a signed outcome-pattern service to the nRF9160 firmware, and use motion-qualified acknowledgement gestures for queued action outcomes. Keep the existing single-button recording edge untouched; a deliberate tilt/tap sequence acknowledges only a pending status beacon and can never approve an operation.
- **owner gets:** The owner can understand success, failure, retry, or unknown while the pendant is in a pocket or the Mac is out of sight, without a bright gadget-like LED or opening a screen. The same physical language works when the link is temporarily down.
- effort: Medium: enable i2c2/devicetree, integrate two sensor drivers, calibrate thresholds, reserve a small event queue, and bench-test patterns against the existing ESP32 audio bridge.  ·  risk: False motion acknowledgements or I2C lockups could hide a status. Require a time-qualified gesture, watchdog/reset the bus, retain the compact event ID until relay acknowledgement, and fall back to the LED/audio cue. Do not let this path touch action approval.
- cost: No new hardware purchase; roughly 5–15 mA peak during haptic pulses and modest firmware flash/RAM use.  ·  latency: Outcome pattern starts under 150 ms after a signed beacon; gesture qualification adds roughly 300–700 ms only to acknowledgement.
- security: The pendant receives only opaque outcome IDs and pattern classes, never page contents or secrets. Signed envelopes, monotonic counters, expiry, and the existing physical approval boundary remain mandatory.
- depends on: tactile_action_outcome_beacon behavior already accepted; Enable i2c2 and add DRV2605L/LSM6DSOX devicetree bindings; Relay-side signed outcome envelope and deduplicated pending-event delivery


## What it asked for

_Nothing._
## Its own summary

Recorded four new action-focused deliverables: a short post-action compensating-operation window; a signed, redacted action card bound to the approved digest; reconnect-time per-step reconciliation that refuses blind replay; and firmware integration of the already-owned DRV2605L/LSM6DSOX for pocket-readable outcomes. The second proposal is intentionally adjacent to an existing preview idea, but the new requirement is cryptographic binding of exactly what was previewed to exactly what executes.

**Biggest unknown:** The system still lacks an observed, end-to-end contract for operation step identity and idempotency across POST /execute, browser sessions, receipts, and verify_operation_step. I still need the live schemas/semantics for those records before I can implement recovery or compensating actions without risking a duplicate side effect.

