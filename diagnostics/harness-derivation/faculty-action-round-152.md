# Harness derivation — faculty-action — round 152

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Stop everything you’re doing right now.”"
- **useful because:** A single unmistakable emergency stop is safer than hunting for the Mac window or relying on network connectivity. One deliberate gesture on the pendant can cancel queued relay jobs, signal the Mac executor to abort the current reversible step, pause browser commands, mute playback, and lock the Mac if the owner chooses that policy.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-action
- **model tier:** No expensive model is needed: firmware/relay event handling and a deterministic Mac safety handler should execute it; use realtime only to acknowledge.
- **latency:** Local audio mute and pending-command cancellation under 250 ms; Mac/browser cancellation under 2 seconds; speak “stopped,” “partially stopped,” or “unknown.”
- **cost:** <$0.01 per invocation; mostly durable event and receipt writes.
- **security:** The gesture must be physically distinct from approval and work without LTE through USB when tethered. Do not silently claim cancellation: return per-step cancelled/completed/unknown receipts, preserve an audit record, and require a separate deliberate action to resume. Locking the Mac and closing tabs must be owner-configured, conservative defaults only cancel and mute.
- **missing:** a high-priority stop event accepted by relay and Mac bridge even when normal job queues are busy; abort semantics for each executor action type and a durable stop epoch fencing stale workers; pendant firmware gesture/LED/audio pattern distinct from approval; a reconciler that verifies cancelled postconditions

### "“Do that same safe action again.”"
- **useful because:** Owners often repeat a just-completed action—send the same templated message, reopen the same document, rerun a reversible cleanup—without restating every parameter. A bounded replay token lets the pendant and relay repeat only the exact previously verified operation, not reinterpret fresh speech, while still showing what will happen and preserving an undo path.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-perception → faculty-action
- **model tier:** Deterministic replay and policy checks should use no LLM; a small model may resolve which recent action “that” refers to only when the owner names a time/context, otherwise ask a clarification.
- **latency:** Identify and present the candidate in 1 second; after approval, execute in 2–10 seconds and independently verify.
- **cost:** <$0.02 per replay; storage and verification dominate, not inference.
- **security:** Never replay irreversible, secret-bearing, or context-sensitive actions by default. Bind a replay token to the exact operation digest, browser tab/session, target identifiers, expiry, and risk class; require pendant approval for any external side effect; reject if the page/app state has materially changed; redact the spoken summary. Log whether it was an exact replay or refused.
- **missing:** a durable last-safe-action token with canonical inputs and redacted human summary; idempotency and context-drift checks in Mac/browser executors; a policy allowlist for replayable action classes and explicit owner configuration; verification of both preconditions and postconditions before committing

### "“Watch this item and, if it reaches $X before Friday, buy it—but only once, and tell me exactly what happened.”"
- **useful because:** The owner gets a genuinely delegated outcome rather than a reminder: the relay can monitor while the Mac sleeps, the browser can use the authenticated session, and the pendant can provide the final physical consent at the moment the condition becomes true. This combines time, changing web state, safe purchase execution, and truthful recovery across surfaces.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-judgement → faculty-perception → faculty-action
- **model tier:** Use a cheap scheduled watcher and deterministic threshold/idempotency logic; invoke the expensive model only when the page changes materially or the condition is ambiguous.
- **latency:** Detect a qualifying change within the configured polling interval (1–15 minutes); present a compact pendant/browser preview within 2 seconds; submit or decline within 10 seconds of approval.
- **cost:** $0.02–$0.20 per day depending on polling frequency and page complexity; browser sessions and change interpretation dominate.
- **security:** Never purchase without fresh physical approval unless the owner separately enables an explicit policy. Bind the condition to product identity, seller, currency, maximum total including shipping/tax, expiration, and one-shot idempotency. Keep payment secrets in the browser; relay receives only redacted previews and hashes. If price, seller, stock, address, or checkout fields change, pause and ask again. Record verified success, verified refusal, or unknown—never infer purchase from a click receipt.
- **missing:** durable conditional-watch objects with expiry and one-shot execution tokens; browser-side product/price extraction with change fingerprints and seller identity; a final-approval notification path that survives Mac sleep and LTE loss; purchase-specific postcondition verification and duplicate-charge fencing

### "“Save exactly what I’m looking at right now so I can find and trust it later.”"
- **useful because:** A voice note or bookmark loses the surrounding evidence. This would bind a deliberate pendant gesture to the active browser tab, capture a redacted page title/URL, selected text or DOM excerpt, timestamp, and content hash, then let the owner retrieve the same evidence later—even if the page changes or disappears.
- **path:** pendant → browser-extension → mac-planner → relay → faculty-perception → faculty-action
- **model tier:** Use deterministic browser extraction and hashing; use a small model only to generate an optional short label or resolve a spoken retrieval query.
- **latency:** Capture confirmation in under 2 seconds; archive upload and hash completion within 10 seconds; retrieval should return the evidence bundle in under 3 seconds.
- **cost:** <$0.03 per capture plus storage; screenshots/archived excerpts dominate bandwidth and storage.
- **security:** Do not archive passwords, payment fields, private messages, or hidden DOM values. Apply browser-side sensitivity classification before data leaves the Mac, allow the owner to choose URL-only, excerpt, or full visible-page evidence, encrypt the archive, and support source-linked deletion. Clearly distinguish a live URL from an immutable captured snapshot.
- **missing:** browser command to capture the active visible tab with sensitivity-aware redaction; content-addressed encrypted evidence storage with retention and deletion controls; a pendant gesture that binds the capture to the currently focused tab rather than a guessed tab; retrieval and verification that can show whether the live page still matches the archived hash


## Changes it proposed to its own stack

### `integration` — Turn the currently USB-attached nRF9160 pendant and ESP32 bridge into a local, authenticated action/receipt transport when LTE is absent. The Mac bridge should multiplex button/approval events, pending-action LED/audio cues, and signed commit/cancel receipts over the two serial links, while relay job records retain the same idempotency key and later reconcile the USB receipts with cloud state. The transport must be explicit USB mode, never pretend LTE registration, and expose link loss as unknown rather than success.
- **owner gets:** The owner can use the pendant as a real physical approval and cancellation device today at their Mac—even with no registered LTE device—and actions do not disappear merely because the wearable link is down.
- effort: Medium-high: serial framing and authentication, bridge daemon integration, relay reconciliation, and fault-injection tests.  ·  risk: A stale USB receipt could approve the wrong action; bind every receipt to operation id, step id, nonce, digest, and monotonic counter, reject replay, and surface conflicting receipts as unknown. Recovery is to leave the action staged and require a fresh approval.
- cost: No API cost beyond small relay reconciliation calls; engineering only. Existing hardware, no new BOM.  ·  latency: ~10–100 ms local cue/receipt latency; reconciliation after reconnect is seconds.
- security: Improves security by making physical consent available offline, but creates a local attack surface; use per-device keys, challenge-response, and never transmit form contents or secrets over serial.
- depends on: physical_transaction_approval_latch (s10-j9l4); truthful action status with unknown state; Mac bridge serial access to /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; relay operation reconciliation endpoint

### `hardware` — Add a small secure element to the pendant design, provisioned at manufacture with a non-exportable device key and monotonic counter, and route approval, cancellation, and offline-watch execution receipts through it. The nRF9160 firmware should verify the secure element signature locally and the relay should reject receipts whose counter, operation digest, or expiry does not match the staged operation.
- **owner gets:** The owner can trust a physical approval or conditional action even when the pendant is USB-tethered or temporarily offline; a compromised Mac, replayed serial packet, or restored firmware image cannot silently manufacture consent.
- effort: High for a hardware revision and provisioning pipeline; medium firmware/relay integration and migration for the current board.  ·  risk: Provisioning mistakes could permanently brick trust for a device, and loss of the pendant key requires a replacement/recovery process. Keep current software receipt validation as a compatibility fallback, visibly mark it as lower assurance, and provide factory recovery that does not expose the private key.
- cost: Approximately $1–$4 BOM increase per unit plus manufacturing provisioning; negligible runtime power beyond brief signing operations.  ·  latency: A few milliseconds to tens of milliseconds per receipt; acceptable for approval and cancellation.
- security: Strongly improves anti-replay and device authenticity. It does not protect a malicious owner-authorized Mac from making legitimate actions, so operation digests and independent postcondition verification remain required.
- depends on: physical transaction approval envelope format; USB-local pendant transport; durable operation/step identifiers; firmware manufacturing and key-rotation process


## What it asked for

_Nothing._
