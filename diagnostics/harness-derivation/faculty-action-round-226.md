# Harness derivation — faculty-action — round 226

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Send this exact message to Alex, wherever it is open, but don't let it go to anyone else.”"
- **useful because:** The mind can safely bridge a draft between a logged-in browser and native Mac app, preserve the exact recipient/body, require the pendant's deliberate approval, then independently verify the sent state. This solves the everyday failure mode where an assistant edits the right text but submits it in the wrong account or thread.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → faculty-judgement → faculty-perception → faculty-action
- **model tier:** Use the realtime model only to capture the owner's short instruction; use the cheaper local planner for app/browser routing and faculty-perception for postcondition checks.
- **latency:** Stage a draft in 3–8 s; approval prompt under 1 s after staging; submit and verify within 5 s. Never submit while recipient identity or account is ambiguous.
- **cost:** Usually one realtime turn plus low-cost local planning; verification is a small structured call. Dominant cost is browser/native inspection, not generation.
- **security:** Only a recipient label, account label, and body digest should reach the pendant; never send credentials or full private page contents to firmware. Require physical approval for submission, bind approval to a hash of recipient/account/body, expire it after 2 minutes, and stop on any mismatch. A failed verification must be reported unknown, never success.
- **missing:** A first-class cross-surface draft handoff object with canonical recipient/account/body hash; Action executor support for binding an approval nonce to that object; Perception adapters that can verify sent state in both native apps and browser sessions

### "“Only interrupt me if this is genuinely urgent; otherwise remember it and tell me when I’m free.”"
- **useful because:** The pendant becomes an interruptibility-aware front door instead of vibrating at arbitrary times. Relay events can arrive while the Mac or browser is unavailable; the Mac contributes foreground/session context, while the worn device contributes motion and playback context that the Mac cannot see.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a cheap classifier/ruleset for urgency and quiet-hour policy; reserve realtime inference for ambiguous owner speech or an emergency exception.
- **latency:** Urgent decision in under 500 ms after an event; nonurgent events enqueue immediately and should not wake audio. Re-evaluate queued items when presence/context changes.
- **cost:** Near-zero model cost for ordinary events; occasional small classification call. Device-side context is compact and avoids streaming sensor data.
- **security:** Keep IMU data local and export only coarse states (moving/still, playback-active). Do not infer location. Do not let urgency bypass physical approval for consequential actions. Make every interrupt decision auditable with event ID, policy version, and reason.
- **missing:** Firmware integration of the already-owned LSM6DSOX over enabled i2c2, with coarse motion/playback state only; A relay inbox policy that distinguishes urgent, deferred, and expired events; A Mac lock/wake or equivalent availability signal (currently unknown); A queue-drain trigger on observed foreground/browser changes

### "“That action may have partly happened—find out before doing anything again, and fix it if it’s safe.”"
- **useful because:** Partial browser/Mac failures currently leave the owner choosing between dangerous retry and tedious investigation. This capability reconciles receipts with fresh state, identifies whether the intended postcondition already holds, and chooses one bounded recovery (no-op, undo, resume, or ask) without duplicate sends or edits.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → faculty-perception → faculty-action → faculty-judgement
- **model tier:** Use a cheap deterministic reconciler over receipts and typed postconditions; invoke a stronger model only when state evidence conflicts or the recovery is ambiguous.
- **latency:** Return a first truthful status in 2 s from receipts; fresh verification in another 2–5 s. Never auto-retry an outbound or destructive step.
- **cost:** Low: structured receipt/state comparison dominates; model calls are exceptional. Saving one duplicate action is worth more than the small verification cost.
- **security:** Bind every recovery to operation and step IDs, a state snapshot hash, and an expiry. Read-only verification must precede mutation. Undo only when the receipt declares it reversible and the current state still matches; otherwise surface unknown and require approval. Haptic outcome must distinguish repaired, already-done, and unknown.
- **missing:** A reconciliation state machine with explicit no-op/resume/undo/ask outcomes; Receipt fields for idempotency key, reversibility, and intended postcondition; A way to ask faculty-perception for fresh evidence before executor retry; Owner-visible compact explanation of the evidence used

### "“Print the document I’m looking at, but only on my home printer, double-sided, and never if it contains the wrong account or extra pages.”"
- **useful because:** Today the mind can choose a browser tab and issue a Mac action, but it cannot safely bind a logged-in browser document to a specific printer configuration and prove that the printed artifact was the intended one. This would make a physical-world action trustworthy: discover the document, render a preview fingerprint, stage printer/options, obtain deliberate pendant approval, submit, and verify the spooler/job metadata without exposing document contents to the pendant.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision → faculty-judgement → faculty-action → faculty-perception
- **model tier:** Use a cheaper local planner for tab/document and printer enumeration; use realtime only for the owner's spoken constraints. Use perception for deterministic preview and spooler verification, not a generative claim that printing succeeded.
- **latency:** Stage in 5–10 s; approval prompt immediately after a stable preview fingerprint; submit in under 3 s; return queued/completed/unknown status within 5 s. Never print on ambiguous account, page count, or printer identity.
- **cost:** Low model cost; local PDF rendering and printer inspection dominate. A compact hash and page count are cheaper and safer than sending document text through the relay.
- **security:** The pendant receives only printer label, page count, duplex/color settings, and a document digest—not document contents. Bind the physical approval to document hash, account/session identity, printer ID, and options with a short expiry. Treat spooler acceptance as queued, not completed; verify only through read-only printer state and report unknown if the printer cannot attest completion. Support cancellation before submission and never silently fall back to another printer.
- **missing:** A typed print-intent and rendered-document fingerprint shared by browser, Mac printer executor, and verifier; Read-only printer inventory and spooler postcondition verification on the Mac; A browser adapter that can export a stable, privacy-preserving print preview hash for the active document; Physical approval binding that includes non-browser targets and option hashes


## Changes it proposed to its own stack

### `integration` — Add a typed CrossSurfaceDraft object shared by planner, browser executor, native Mac executor, and faculty-action: {operation_id, account_id, destination_id, body_hash, attachment_hashes, source_session, approval_nonce, expiry, intended_postcondition}. Executors must reject any step whose live destination/account/body hash differs, and faculty-perception verifies the postcondition before the operation is committed.
- **owner gets:** The owner can say one sentence and trust that the exact person, account, and text—not a similarly named tab or stale draft—gets used. A mismatch becomes a safe stop instead of a silent wrong send.
- effort: Medium: schema and adapters across planner/browser/native action paths, plus tests for account and recipient swaps.  ·  risk: Older jobs lack the new fields; migrate them as unbound and require a fresh approval. If verification is unavailable, report unknown and leave the draft untouched.
- cost: Negligible storage and token overhead; one short digest per operation.  ·  latency: Adds roughly 1–3 s for canonicalization and postcondition verification.
- security: Improves least privilege: firmware receives only digest/labels, never message contents or credentials. Hashes must be domain-separated and exclude sensitive plaintext from logs.
- depends on: A stable operation/step ID shared by POST /prepare, POST /approve, POST /execute, browser commands, and verify_operation_step; Owner policy defining which destinations require physical approval

### `firmware` — Integrate the owned LSM6DSOX on i2c2 and export only a three-state local context bitfield (moving, playback_active, recently_handled) to the relay. Use it to suppress nonurgent tactile/audio interruptions during motion or active playback, while retaining an explicit urgent override and a compact queued-event count.
- **owner gets:** The pendant stops startling the owner while they are walking, talking, or already listening, yet urgent items are not silently lost; deferred events arrive as one concise catch-up instead of a burst of vibrations.
- effort: Medium: enable i2c2, add sensor polling and calibration, define low-power thresholds, and connect the bitfield to the existing inbox/outcome beacon.  ·  risk: False still/moving classifications could delay an alert. Default to conservative delivery for urgent events, expose the reason in the event receipt, and fail open to current behavior if the IMU or bus is unhealthy.
- cost: No new parts; small firmware flash/RAM increase and modest periodic current draw, with duty-cycled polling to limit battery impact.  ·  latency: Context updates within about 250 ms; no added latency for urgent delivery.
- security: No raw accelerometer/gyro leaves the device; only coarse state and sensor-health code are transmitted.
- depends on: Existing relay inbox/event priority policy; A compact event queue for deferred notices; The pending motion_context_safety_gate request must resolve into a concrete firmware contract


## What it asked for

_Nothing._
## Its own summary

Recorded three end-to-end capabilities: hash-bound cross-surface sending with physical approval and verification; interruptibility-aware urgent/deferred delivery; and evidence-first partial-operation reconciliation. Also recorded two concrete changes: a shared CrossSurfaceDraft contract and local IMU-derived interruption context. The recorder flagged the latter two capabilities as connective work, which is useful: the missing value is the typed contracts and state machines between existing routes, not more endpoints.

**Biggest unknown:** I still need the exact live semantics and payloads of /prepare and /approve, plus an owner decision on which destination/account classes may be sent proactively versus always requiring approval. For the IMU proposal, I need the pending motion_context_safety_gate contract resolved into thresholds and fail-safe behavior; I did not re-request it.

