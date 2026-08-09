# Harness derivation — faculty-action — round 213

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Make the change, but don't tell me it worked until you independently prove every step and stop safely if any proof fails."
- **useful because:** This turns the system from an executor that reports its own receipt into a trustworthy cross-surface operator. A Mac/browser action can be performed, checked against fresh state by faculty-perception, and surfaced on the pendant as verified, safe-to-retry, unknown, or cancelled. If step 2 fails verification, later steps are not run and the owner gets the exact boundary of uncertainty.
- **path:** faculty-judgement creates a typed multi-step operation and risk summary → mac-planner submits the plan and mac-vision/browser-extension execute concrete Mac/browser steps → faculty-action dispatches each step and records correlation IDs → faculty-perception independently verifies each postcondition using fresh Mac/browser state → relay-realtime delivers the compact outcome to the pendant → pendant renders the already-accepted tactile_action_outcome_beacon
- **model tier:** Use the cheaper background planner for decomposition and receipt summarization; use realtime only when the owner is waiting for an interactive confirmation or spoken status. Verification should be deterministic/read-only, not an extra generative judgement.
- **latency:** For a short operation, 1–3 seconds per step is acceptable; never hide a verification timeout. A timeout yields unknown and halts the dependent chain.
- **cost:** Low-to-moderate: one planning call plus bounded verification calls per step; dominated by model planning, while postcondition checks should be local/read-only and cheap.
- **security:** Never send page secrets or full form contents to the pendant. Bind every verification to operation_id, step_id, expected locator, and a short-lived state hash. Require the existing physical approval latch for risky actions; a receipt from the executor alone can never close the operation. On mismatch or stale evidence, halt rather than retrying a potentially non-idempotent step.
- **missing:** A coordinator that enforces verify-before-next-step and treats unknown as a first-class terminal state; Correlation fields connecting POST /execute receipts to verify_operation_step calls and the final pendant beacon; A policy for which failures are safely retryable versus requiring owner re-approval

### "I missed that—repeat the last answer, starting from the point I didn't hear, without making me ask the whole question again."
- **useful because:** A dropped syllable or a noisy moment should not force the owner to reconstruct context. A physical repeat gesture on the future rotary encoder/new button selects the last delivered response locally, while the relay fetches only the missing cursor range and the bridge plays it. It works when the Mac is busy or the browser is irrelevant, and it distinguishes 'audio arrived but was missed' from a transport failure.
- **path:** pendant rotary encoder/new button selects repeat and sends an opaque response ID plus cursor, never raw secrets → relay-realtime retains a bounded, encrypted response manifest and serves the requested range → ESP32 audio bridge resumes at an Opus frame boundary and reports playback start/finish → faculty-perception or relay receipt logic confirms the requested range was actually delivered
- **model tier:** No model call for the common case: response IDs, frame cursors, and manifests are deterministic. Use a cheap background model only if the requested segment has expired and a short textual recap is needed; do not invoke realtime merely to replay bytes.
- **latency:** Haptic acknowledgement under 150 ms; replay begins within 500 ms when cached. If unavailable, say so immediately rather than silently replaying an unrelated answer.
- **cost:** Near-zero for cached replay; storage and bandwidth dominate. A fallback recap costs one inexpensive model call.
- **security:** The pendant receives only an opaque response ID, codec/rate, byte/frame range, expiry, and checksum—not conversation text or credentials. Enforce replay count/expiry, bind requests to the authenticated device, and refuse a cursor outside the manifest. USB is not assumed as a product transport.
- **missing:** Rotary encoder and an additional physical button, as planned by the owner; A relay endpoint that serves bounded response ranges by opaque ID and cursor; Firmware gesture and playback resume support that does not overload sw0 recording or sw1 bookmarking

### "Stop everything you are doing right now, and tell me what actually stopped, what was undone, and what may still have happened."
- **useful because:** Approval protects actions before they run; this is the missing panic brake after work has started. One deliberate physical emergency gesture on the future extra button (or an unambiguous wheel-and-button chord) would cancel queued Mac jobs, withdraw pending browser commands, request undo for reversible completed steps, and explicitly report irreversible or unknown steps. The owner gets a bounded failure instead of wondering whether an action continued in the background.
- **path:** pendant detects the dedicated emergency gesture locally and emits a signed monotonic stop event without opening the microphone → relay-realtime fans the stop event to the Mac agent and records its deadline → mac-planner cancels queued jobs and invokes existing undo/cancel routes; browser-extension withdraws pending commands → faculty-action reconciles cancellation and undo receipts, while faculty-perception checks the resulting app/file/browser state → relay sends a compact stopped/undone/unknown summary and the pendant renders the outcome beacon
- **model tier:** Deterministic control path only; no model call is allowed before honoring the stop. Use a cheaper background model later to explain the collected receipts if the owner asks.
- **latency:** Local gesture acknowledgement under 150 ms; dispatch cancellation within 300 ms when the relay is reachable. If disconnected, the pendant must persist the stop event and show that delivery is pending rather than claiming success.
- **cost:** Near-zero model cost; bounded relay and Mac requests. Undo/reconciliation work dominates compute, not inference.
- **security:** The gesture must be hard to trigger accidentally and must never execute new actions. Cancellation is best effort for already-submitted irreversible operations; state each unknown explicitly. Authenticate and monotonic-sequence the stop event, deduplicate it, and do not include private action contents in the pendant message.
- **missing:** A dedicated physical input path: the current sw0/sw1 meanings leave no safe emergency gesture; use the owner's planned extra button or a tested two-control chord; A fan-out stop coordinator with a deadline and per-surface acknowledgements; A read-only post-stop verifier that distinguishes undone, still-running, and unknown

### "Before you send anything anywhere, tell me exactly which private fields will leave my Mac, who will receive them, and let me approve only that disclosure—not a vague 'send it.'"
- **useful because:** The owner can approve an action today without seeing the complete data-disclosure boundary. This capability makes cross-surface automation safe for forms, email, uploads, and browser workflows: it identifies every field or file leaving the Mac/browser, detects newly requested fields, and requires a fresh physical approval when the disclosure changes. It is especially valuable when logged-in browser sessions contain secrets that the pendant and relay must never receive.
- **path:** faculty-judgement converts the request into a disclosure manifest and risk summary → mac-planner/browser-extension inspect the target form, recipient, and outbound fields locally → faculty-perception computes a redacted field-level diff and verifies the live page still matches the approved manifest → faculty-action submits only the approved fields, then verifies the resulting confirmation state → relay-realtime sends the pendant a compact recipient/category/count summary; the pendant's physical approval latch authorizes the manifest hash, never the secret values
- **model tier:** Use a cheap model for drafting a human-readable summary only after deterministic field extraction. The approval decision and manifest comparison must be deterministic; realtime is only for the owner's live spoken interaction.
- **latency:** Manifest preview within 2 seconds for a normal form; any DOM or recipient change invalidates approval immediately. Never silently continue after a timeout or navigation.
- **cost:** Low-to-moderate: local inspection dominates; one small summary call only when needed. No secret values need leave the Mac, reducing relay/model cost.
- **security:** Secrets, message bodies, and file contents stay on the Mac/browser. The relay and pendant receive only sensitivity labels, destination, field names/categories, sizes, and a cryptographic manifest digest. Bind approval to recipient, origin, exact field set, attachment hashes, expiry, and one submission attempt; refuse if any changes. This complements physical approval without treating a generic approval as consent to undisclosed data.
- **missing:** A browser/Mac disclosure inspector that returns typed outbound fields and attachment hashes without exposing values; A manifest-diff gate between inspection and submission; A pendant summary vocabulary for recipient, sensitivity classes, and changed-field refusal

### "Only interrupt me when it is worth breaking my concentration; otherwise queue it and give me one calm summary when I surface."
- **useful because:** The system currently has ways to deliver events, but not a shared decision about when an interruption is harmful. This would combine Mac foreground/app state, browser activity, calendar context, and the pendant's motion/interaction state to defer low-value alerts while still escalating urgent or owner-requested events. The owner experiences one intentional wearable instead of a stream of badly timed pings.
- **path:** Mac observation reports foreground app, browser activity, and calendar-derived focus context → relay maintains a durable priority queue and expiry for incoming events → faculty-judgement classifies urgency and interruption cost without exposing private contents → pendant firmware uses IMU/button interaction and haptic patterns to mark unavailable, defer, or surface-now states → relay delivers a compact digest when the owner presses the planned control or exits a focus state
- **model tier:** Deterministic rules for urgent classes, quiet hours, active calls, and explicit owner preferences; a cheap background model may cluster deferred titles into a digest. Realtime is used only if the owner asks for the queue aloud.
- **latency:** Urgent events surface within 1 second; nonurgent events may wait until a clear interaction boundary. The pendant must acknowledge receipt locally even when it defers presentation.
- **cost:** Low ongoing cost: event metadata and rules dominate; summarization is occasional and batched.
- **security:** Do not infer sensitive activity from raw keystrokes or microphone audio. Keep page/message contents on the Mac; send only event class, urgency reason, expiry, and opaque IDs. The owner must be able to override defer for a sender/category and inspect why an event was suppressed.
- **missing:** A shared interruption policy and explainable priority schema; Firmware integration for the owned LSM6DSOX IMU and DRV2605L haptic controller via i2c2; A digest trigger and queue view that distinguish deferred from lost events


## Changes it proposed to its own stack

### `hardware` — Add a low-power secure element with a protected device key and monotonic counter to the jewellery pendant revision, wired on the existing I2C bus. Move signing of approval, bookmark, stop, and disclosure-manifest events into the secure element; provision a per-device public key during manufacturing and reject rollback/replay counters at the relay.
- **owner gets:** The owner gets confidence that a physical press really came from their pendant, even if firmware storage is copied or a lost device is restored. It makes remote approvals, privacy disclosures, and emergency stops auditable across link drops instead of trusting an extractable software key.
- effort: Medium hardware revision plus firmware/relay provisioning and recovery UX. Prototype against the existing bench pendant would need an external secure-element breakout; production needs enclosure and PCB integration.  ·  risk: Lost or failed hardware can become unrecoverable if key backup and replacement enrollment are wrong. Use a recovery ceremony requiring the owner's existing authenticated Mac/phone plus an explicit physical gesture; never export the private key. Preserve a software-signed compatibility mode only for bench testing, clearly marked untrusted.
- cost: Roughly $1–$4 BOM increase per unit, negligible idle power over the current battery budget, plus manufacturing provisioning and replacement support.  ·  latency: Typically milliseconds per signature; batch only compact event digests and do not sign audio payloads.
- security: Strongly improves anti-replay and device authenticity, but does not itself prove the owner intended a gesture; retain the physical approval semantics and relay-side expiry. Avoid putting secrets or conversation content in signed envelopes.
- depends on: A production pendant PCB/enclosure revision; Relay device enrollment, key rotation, and revocation; Firmware integration of secure-element I2C transactions without blocking the audio path


## What it asked for

_Nothing._
## Its own summary

This round produced three non-duplicate directions: (1) a user-facing execute-and-prove workflow that halts on unknown verification, (2) owner-initiated repeat-from-cursor for missed audio using the planned rotary control, and (3) a physical emergency stop that fans out cancellation/undo and reports verified residual risk. The bookmark-context idea and generic operation-correlation schema were rejected as already present in the backlog, so I did not count them.

**Biggest unknown:** I still need the exact live contract for the operation coordinator between POST /execute receipts and verify_operation_step, plus the physical design decision for the extra emergency-control input. The current two buttons are already committed to recording and bookmarking; no safe panic gesture should be invented on top of them. The other concrete missing pieces are bounded response-range serving for replay and a policy for cancellation outcomes (stopped, undone, still-running, unknown).

