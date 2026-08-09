# Harness derivation — faculty-action — round 246

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I asked you to do something, but the computer or network may have timed out. Tell me whether it happened, and recover without sending it twice.”"
- **useful because:** Timeouts currently force either an unsafe blind retry or an unhelpful 'I don't know.' This makes uncertain execution a first-class, truthful workflow: reconcile fresh Mac/browser state before retrying, and only retry when the original did not take effect.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** gpt-5.6-luna for planning and reconciliation; gpt-4.1-mini only for cheap visual state capture; realtime tier only to explain the result live.
- **latency:** Under 3 seconds for receipt lookup; up to 10 seconds for fresh verification; never retry before verification completes.
- **cost:** Usually <$0.03 per incident; dominated by one planner turn and optional browser/Mac verification, not by storage.
- **security:** A retry can duplicate a purchase, message, or form submission. Bind every attempt to an operation ID, require fresh postconditions, redact private evidence, and require the existing physical approval latch for irreversible retries. Unknown must remain unknown rather than becoming success.
- **missing:** A durable retry/reconciliation state machine joining executor attempt IDs to verify_operation_step evidence; A standard mapping from action intent to idempotency key or safe-retry predicate; A user-visible explanation when verification cannot distinguish success from failure

### "“Before an important conversation, quietly check that the pendant can deliver speech clearly, and warn me if the audio path is degraded.”"
- **useful because:** The owner should not discover a broken bridge, codec regression, packet-loss burst, or silent playback only after missing an important answer. A short fixture-based check can validate the end-to-end path without opening the microphone or recording private speech.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** No expensive conversation model for the test: deterministic device/relay probe; use gpt-4.1-mini only to summarize abnormal measurements. Realtime remains reserved for the live conversation.
- **latency:** 2–5 seconds for a short golden fixture; run on explicit request or before a scheduled high-stakes session, never continuously.
- **cost:** Near-zero API cost; dominant cost is the brief cellular/bridge transfer and local playback energy.
- **security:** Use a synthetic speech/sweep fixture, never owner microphone content. Do not persist raw audio; persist only hashes and measurements. Require explicit opt-in before audible playback, with a silent capabilities/loopback mode for background checks.
- **missing:** A relay-triggered health-check contract that identifies the exact pendant/ESP32 bridge pair; Threshold policy for packet loss, decode latency, tx starvation, and playback completion; A compact owner-facing result format and a way to suppress the check during quiet hours

### "“After you finish, tell me exactly what changed on my Mac or in the browser—not just that the action succeeded.”"
- **useful because:** A success receipt is not enough when an action edits files, changes a calendar, or submits a browser form. An owner needs a compact, privacy-filtered before/after diff and provenance so they can spot an unintended side effect without opening the Mac.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** gpt-4.1-mini for extracting a concise diff from structured receipts; gpt-5.6-luna only when the result is ambiguous or needs interpretation.
- **latency:** Deliver a short result within 5 seconds of completion; defer large diffs to the dashboard and send only a summary over the pendant.
- **cost:** <$0.02 for ordinary actions; dominated by fresh state reads, with no model call needed for simple structured changes.
- **security:** Never send page secrets or full private file contents to the pendant. Use hashes, names, field labels, and redacted snippets according to sensitivity; require fresh independent verification for claims of submission. Keep the raw evidence local and expire it.
- **missing:** A structured before/after capture attached to each action attempt; A redaction and sensitivity policy shared by Mac, browser, relay, and pendant; A compact diff envelope that tactile_action_outcome_beacon can reference without carrying private content

### "“Use my logged-in account to complete this form, but do not show my passwords, payment numbers, private messages, or one-time codes to the AI or relay.”"
- **useful because:** Today an agent can either lack access to a logged-in workflow or risk exposing the very secrets that make the workflow useful. A local browser privacy broker would let the owner delegate completion while keeping sensitive values and page contents inside the browser/Mac boundary; the relay receives only field labels, validation state, and an approval digest.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** gpt-5.6-luna plans from redacted field metadata; a deterministic browser-side broker performs secret lookup and typing; realtime is used only for the owner's conversation.
- **latency:** Ordinary fields under 5 seconds; OTP or payment submission pauses for explicit physical approval and can wait for the owner.
- **cost:** <$0.05 per workflow, dominated by planner turns; no secret values are sent to model APIs.
- **security:** The browser broker must classify secret fields locally, deny screenshots/DOM extraction for protected values, isolate clipboard and accessibility reads, bind every protected write to an opaque transaction digest, and expire it. The pendant confirms only the human-readable destination, amount, and site—not the secret. A failed classification must fail closed.
- **missing:** A browser-local secret-field broker with an explicit protected-field taxonomy; An opaque handle protocol for requesting a local secret without returning its value; A redacted DOM/state schema and an audit proving protected values never enter relay logs or model context; Owner-controlled vault integration and site-specific classification overrides


## Changes it proposed to its own stack

### `hardware` — Add a small secure element (for example, an ATECC608-class device on the existing I2C bus) in the next jewellery enclosure revision. Generate and retain the pendant signing key inside it; have firmware sign physical approval decisions, queue receipts, and device identity attestations without exporting the private key. Keep the current software path working with a development-key fallback only on the bench, never in a product build.
- **owner gets:** A stolen or cloned pendant should not be able to approve a bank transfer, unlock a workflow, or impersonate the owner's device. This makes the deliberate physical gesture a trustworthy security boundary rather than merely a button event, while fitting the owner's jewellery-sized product direction.
- effort: Moderate hardware spin plus firmware I2C driver, provisioning ceremony, relay public-key registry, and migration for existing latch envelopes. Prototype on the bench before enclosure fabrication.  ·  risk: Provisioning mistakes or bus failure could make the pendant unable to approve actions. Recover with a factory enrollment/revocation path and a clearly surfaced 'device cannot authenticate' state; never silently fall back to an unauthenticated approval in the field.
- cost: Roughly $1–3 in components and a small assembly/BOM increase; negligible steady-state power, with brief I2C wake current. Engineering cost is substantially larger than component cost.  ·  latency: Typically milliseconds per signature; approval acknowledgement may add tens of milliseconds, acceptable relative to human gesture and cellular latency.
- security: Strongly improves key isolation and anti-cloning. Requires secure provisioning, public-key rotation/revocation, and no private key in firmware logs, SD, USB diagnostics, or relay payloads.
- depends on: physical_transaction_approval_latch (s10-j9l4); tactile_action_outcome_beacon; An authenticated relay device registry; A production enclosure/PCB revision


## What it asked for

_Nothing._
## Its own summary

Recorded four non-duplicate directions this round: (1) reconcile uncertain Mac/browser executions before any retry, with independent postcondition verification; (2) a synthetic, microphone-free end-to-end audio health check; (3) secure-element-backed signing for the physical approval latch; and (4) privacy-filtered before/after diffs so the owner learns what actually changed. I still need implementation contracts, not another broad grant: an operation/attempt idempotency schema and safe-retry policy; a relay-to-pendant audio-test pairing and thresholds; production secure-element provisioning/rotation and device registry; and structured before/after evidence plus redaction rules. The live Mac bridge and Safari are online, but the pendant itself is not LTE-registered, so none of these should be claimed as field-tested yet.

**Biggest unknown:** Which action classes the owner considers safe to retry or safe to summarize without an approval prompt; until the owner sets that policy, default to staged approval and report unknown rather than infer success.

