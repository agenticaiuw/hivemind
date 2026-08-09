# Harness derivation — faculty-action — round 248

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “get me into my next meeting,” have the system find the next calendar event, open the right meeting URL in the authenticated browser, verify that the page is actually ready, and tell me on the pendant whether I’m in or what blocked it."
- **useful because:** It turns a time-sensitive intention into a reliable, cross-device outcome: the relay can wake the workflow, the Mac owns calendar and app launching, the browser owns authenticated sessions, and the pendant gives an immediate result without requiring me to look at the Mac.
- **path:** relay → mac-planner → browser-extension → pendant
- **model tier:** Background model plans the calendar-to-URL workflow; realtime model handles only the brief spoken request and final response.
- **latency:** Initial response under 2 seconds; launch and verification within 15 seconds of the request or scheduled event.
- **cost:** Usually one cheap planning call plus local Mac/browser actions; under $0.03 excluding rare fallback reasoning.
- **security:** Meeting URLs and calendar titles are private. Keep them on the Mac/relay job envelope; pendant receives only a redacted meeting label and outcome. Opening or joining must obey the owner’s approval policy; default to opening but never submitting a join form or enabling camera/mic without confirmation.
- **missing:** Calendar event-to-join-link extractor with explicit redaction; Browser readiness verifier for meeting lobby state; A routine trigger that can invoke a multi-surface job at event start

### "After I ask you to do something important, give me a truthful ‘finished / blocked / needs me’ result on the pendant, and keep trying only the safe recovery steps when the Mac or browser drops offline."
- **useful because:** Today an action can be handed off and then disappear into an opaque queue. This makes execution dependable in the real world: relay persists the job, Mac and browser resume idempotently, faculty-perception verifies the postcondition, and the pendant distinguishes success from an owner decision or an unknown state.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Cheap background orchestration and deterministic retry; realtime model only interprets the owner’s short request and speaks the final status.
- **latency:** Immediate acknowledgement under 1 second; retries over minutes with exponential backoff; final status as soon as an independent verifier has fresh evidence.
- **cost:** Low: mostly local actions and receipts, with one verifier call per retry or terminal attempt; under $0.02 typical.
- **security:** Never retry irreversible or externally visible actions automatically. Classify each step, require the existing physical transaction latch for high-risk work, cap attempts, and include action/attempt correlation so a stale receipt cannot be mistaken for completion. Do not send page secrets to the pendant.
- **missing:** Idempotency keys and attempt correlation carried through POST /execute and browser commands; A safe-retry policy that consumes existing actionRisk.js classifications; A durable cross-surface job state machine that links executor receipts to verify_operation_step

### "When I bookmark a moment on the pendant, turn it into a useful follow-up automatically: capture what I was looking at, create a cited note, and—if I say ‘remind me’—schedule the reminder with the source attached."
- **useful because:** A physical bookmark is the only low-friction way to mark a fleeting moment while walking or listening. The pendant supplies exact timing, the relay preserves it across link loss, the browser supplies authenticated page context, and the Mac produces a durable, searchable artifact rather than an orphaned timestamp.
- **path:** pendant → relay → browser-extension → mac-planner
- **model tier:** Realtime model only transcribes the short spoken annotation; a cheaper background model extracts title, URL, selected text/excerpt, and reminder intent.
- **latency:** Haptic acknowledgement immediately; source card within 10 seconds; reminder scheduling within 20 seconds after link/browser context is available.
- **cost:** Typically one small extraction call plus local file/reminder writes; under $0.02 per bookmark.
- **security:** Page content may be private. Store only the minimum excerpt, redact credentials and payment data, preserve URL/title provenance, and require confirmation before creating reminders that contain sensitive text or send anything externally.
- **missing:** A single typed bookmark envelope joining pendant event ID, relay time, browser session, and optional speech; Atomic cited-note writer with deduplication on event ID; Reminder creation that stores source provenance and handles an unknown pendant timezone honestly

### "When I ask you to fill out a form with my usual details, identify the fields, fetch the matching values privately from my Mac, show me only the categories and destination on the pendant, and release the actual values only after I approve that exact field set."
- **useful because:** The owner gets fast form completion without sending addresses, phone numbers, or payment details through the model or relay. The browser, Mac, relay, and pendant each enforce a different boundary: field discovery, secret custody, orchestration, and physical consent.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** A cheap deterministic field classifier handles ordinary forms; the realtime model only interprets the owner’s request and asks for clarification when fields are ambiguous.
- **latency:** Field preview in 2 seconds; approval-to-fill under 3 seconds; no secret should leave the Mac.
- **cost:** Usually local browser and Keychain/Contacts operations with little or no model usage; under $0.01 per form.
- **security:** Secrets must never enter model context, relay logs, pendant storage, or browser command summaries. Bind approval to origin, tab identity, field names, and a short expiry; refuse hidden fields, cross-origin changes, and submit actions unless separately approved.
- **missing:** A Mac-local secret broker that returns one-time values directly to the browser executor; Browser field classification with origin and frame binding; A field-level approval envelope integrated with the existing physical transaction latch

### "If I take the pendant off or it detects an unusual motion pattern, immediately freeze staged computer actions and sensitive browser sessions, then tell me what was stopped when I put it back on or explicitly recover it."
- **useful because:** It turns the worn device into a real physical security boundary. A stolen or unattended Mac session cannot continue executing queued actions merely because the relay still has connectivity, while ordinary motion or a dropped link does not falsely lock the owner out.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Firmware and relay use deterministic rules; no expensive model is needed except optional background tuning of the owner’s motion baseline.
- **latency:** Local motion/removal detection under 500 ms; Mac/browser freeze within 3 seconds when connected; recovery status within 5 seconds.
- **cost:** Near-zero inference cost. Main work is firmware integration, relay event handling, and Mac/browser session controls.
- **security:** Motion data is sensitive and should remain coarse and short-lived. Use signed monotonic events, hysteresis, and a recovery challenge to avoid denial-of-service from false positives. Never erase data automatically; freeze and preserve an auditable state.
- **missing:** Enable and integrate the owned LSM6DSOX through i2c2; A signed worn-state/removal classifier with calibration and false-positive safeguards; Mac and browser actions that freeze pending jobs and revoke or suspend sensitive sessions

### "Let me say “make this safe to share” while viewing a document or webpage, and have the system produce a redacted copy, show me exactly what categories were removed on the pendant, and place the result beside the original without overwriting it."
- **useful because:** The owner can prepare emails, documents, and screenshots for sharing without manually hunting for addresses, account numbers, API keys, or private names. The original remains intact, and the pendant provides a quick physical review checkpoint even when the Mac display is busy.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** A background model or local deterministic scanner identifies likely sensitive spans; realtime is unnecessary except for the owner’s short command and a concise result.
- **latency:** Preview within 10 seconds for ordinary documents; no external send occurs until the owner explicitly approves the redacted artifact.
- **cost:** Typically one cheap extraction/redaction pass and local file/browser writes; under $0.05 for a long document.
- **security:** Source content is private and must stay on the Mac wherever possible. Redaction must be conservative, preserve a reversible audit map locally, never overwrite the source, and require approval before copying or sending externally. Unknown classifications must be reported rather than silently removed.
- **missing:** A local content redaction engine with typed detectors and confidence thresholds; Browser/document export that writes a new artifact atomically beside the source; A compact pendant summary of redaction categories and a review/approval binding to the artifact hash


## Changes it proposed to its own stack

### `interaction` — Add a pending-action carousel driven by the owner’s planned rotary encoder: the pendant receives only compact redacted labels and risk classes for up to 8 staged operations, gives a distinct haptic tick per item while turning, and uses sw1 hold to select/approve or sw1 short press to cancel/leave unchanged. The existing physical transaction approval latch remains the cryptographic authority; this is only the safe local selector that prevents approving the wrong item when several jobs arrive offline.
- **owner gets:** The owner can safely manage several waiting actions without opening the phone or remembering which vibration meant what. It makes the pendant useful as a real control surface rather than a one-bit approval button, especially when disconnected and then reconnected.
- effort: Firmware input and state machine, i2c/rotary driver and compact inbox schema; relay endpoint for redacted pending summaries; bench validation over USB before any product transport work.  ·  risk: A stale or ambiguous label could cause the owner to select the wrong operation. Bind every display item to the opaque transaction nonce and monotonic counter, expire summaries aggressively, require the existing deliberate hold, and refuse approval if the server hash no longer matches. Recover by cancelling the local selection and re-fetching the queue.
- cost: No new server model cost beyond small inbox messages. Requires purchasing and mechanically integrating a rotary encoder (roughly $3–$15 prototype component); negligible additional power compared with audio.  ·  latency: Haptic feedback under 100 ms per detent locally; queue synchronization opportunistic and can tolerate link loss.
- security: Improves security by making multi-operation selection explicit, but labels must never contain secrets, page contents, or full URLs. Approval still requires the existing signed nonce protocol.
- depends on: Owner’s rotary encoder and second button product decision; Enable firmware i2c2 only if the chosen encoder/haptic wiring uses that bus; physical_transaction_approval_latch; tactile_action_outcome_beacon; A relay endpoint that returns redacted pending-operation summaries


## What it asked for

_Nothing._
