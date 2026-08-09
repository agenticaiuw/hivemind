# Harness derivation — faculty-action — round 183

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac_agent_access_and_browser** — As of round 183, Mac agent is fully ready: Accessibility and Screen Recording are granted, computer-use vision upload consent is true, browser bridge is online on Safari at chatgpt.com, and relay/mac bridge are reachable. No pendant appears in the live relay/device inventory; only Mac bridge and offline mobile are listed.
  - evidence: GET /ops/status HTTP 200 at 2026-08-08T04:38Z; GET /browser/status HTTP 200; discover(devices) returned Safari on MacIntel, home-macbook-bridge, cloudflare-contract-test.

## Capabilities it proposed

### ""Finish this multi-step task, but if anything fails tell me exactly what happened and safely recover what you can.""
- **useful because:** Today execution can stop after a partial Mac/browser change, leaving the owner to guess whether a message was sent, a file moved, or a form submitted. A saga coordinator would make the system useful for real-world tasks: it records each step, independently verifies postconditions, compensates only reversible steps, and surfaces an explicit verified/unknown outcome through the pendant rather than claiming success from an executor receipt.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for plan/compensation analysis; realtime only for the owner's short status exchange
- **latency:** Under 1 s to acknowledge and stage; 2–10 s per Mac/browser step; no silent retries for irreversible steps
- **cost:** ~$0.01–$0.08 per multi-step task depending on planner/verifier calls; browser and Mac I/O dominate latency, not tokens
- **security:** Never compensate an irreversible action automatically. Each step carries risk, deadline, idempotency key, and a redacted canonical summary. The pendant approves the transaction digest, while verification reads fresh Mac/browser state without receiving form secrets. Unknown state must be reported and require owner choice.
- **missing:** A saga/compensation state machine around existing job receipts; Per-step idempotency and dependency metadata in POST /execute and job records; A verifier adapter that invokes verify_operation_step after every concrete step; A user-facing recovery choice (retry, undo, leave unknown) on the pendant/dashboard

### ""Fill this private browser form, but keep the values secret from the pendant and prove afterward that only the intended fields changed.""
- **useful because:** The browser session is the one place that can hold credentials and private values, while the pendant is the safest place for deliberate approval. This gives the owner a practical way to authorize sensitive browser work without shipping page contents or form secrets through the wearable or relay, and catches a wrong-tab or wrong-field failure before claiming completion.
- **path:** pendant → relay → browser-extension → mac-bridge → dashboard
- **model tier:** realtime for the short approval conversation; background model for field mapping and postcondition comparison
- **latency:** Stage in under 2 s; one deliberate physical approval; fill and verify in under 8 s; block if the tab or origin changes
- **cost:** ~$0.02–$0.10 per form depending on field mapping and verification; browser inspection and screenshots dominate payload size
- **security:** The relay sees only origin, field labels, value HMACs and a transaction digest; plaintext values remain in the browser extension. The pendant receives no form data. Require origin pinning, expiry, one-use nonce, and fresh browser_field/browser_url verification; refuse if an extra field changes.
- **missing:** A blind browser command that accepts extension-local value handles rather than plaintext; Field-level before/after hashes and an allowlist of intended mutations; Digest binding between browser command, pendant approval and verifier result; Redacted audit receipt that proves scope without retaining secrets

### ""I was away—tell me only what materially changed across my Mac, browser, calendar, and messages since I left, and let me drill into any one change.""
- **useful because:** The owner should not need to reconstruct a missed afternoon from unrelated apps. A departure/return capsule would capture privacy-preserving baselines when the owner leaves, compare them on return, suppress noise such as clock counters, and present a concise cross-surface change narrative with links to the exact current item. This is situational awareness, not another action executor or scheduled briefing.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background model for clustering and summarization; realtime only when the owner asks a follow-up
- **latency:** Capture baseline in under 3 s; return digest within 10 s; drill-down under 2 s per source
- **cost:** ~$0.01–$0.05 per return digest; local snapshotting dominates, with only changed metadata sent for summarization
- **security:** Baselines remain on the Mac by default. Relay receives source names, timestamps, and redacted change summaries, not message bodies or page contents. Owner must explicitly enable each source and set retention; sensitive changes should be summarized locally or omitted.
- **missing:** A departure/return lifecycle trigger from pendant button/IMU or explicit voice command; Versioned, field-level snapshots for selected Calendar, Mail/Messages, Files, and browser sessions; Cross-source change clustering and noise suppression; A drill-down endpoint that retrieves the current item only after owner request

### ""Use my pendant as a physical presence key to release this one private credential to the browser, without sending the credential to the relay or storing it in the pendant.""
- **useful because:** Approval proves intent, but it does not currently provide a way to unlock a secret without exposing that secret to the cloud or wearable. A presence-bound browser vault would let the owner safely approve a password, passkey operation, or payment token while keeping plaintext on the Mac's secure enclave/keychain and releasing only a one-use, origin-bound capability to the browser.
- **path:** pendant → relay → mac-bridge → browser-extension
- **model tier:** realtime for the owner's immediate confirmation; no model should ever receive the secret
- **latency:** Under 2 s from gesture to browser release; expire the capability after 30 s or first use
- **cost:** Usually <$0.01 per use; cryptographic operations and local keychain access dominate, not model inference
- **security:** The relay must see only an opaque request digest. The pendant must receive no secret, page contents, or account identifier beyond a redacted human-readable purpose. Bind the release to browser origin, tab identity, field/action type, nonce, and expiry; deny if any changes. This needs a secure element or OS-backed key agreement rather than pretending a normal button latch is a credential store.
- **missing:** A secure-element-backed key on the pendant or bridge, provisioned during owner pairing; A Mac Keychain/Secure Enclave broker that performs origin-bound one-use release; Browser-extension support for capability handles instead of plaintext values; A relay protocol carrying only challenge, digest, and completion receipt


## Changes it proposed to its own stack

### `firmware` — Integrate the owned LSM6DSOX and DRV2605L on i2c2, and add a local deliberate-gesture classifier for approval/status interactions: detect a stationary, intentional sw1 press/release with a short IMU stability window; reject motion-induced presses, emit distinct haptic patterns for pending/accepted/rejected/expired, and include only a compact motion-quality code in the signed event. Keep sw0's active-edge recording behavior unchanged. This is an amendment to the existing physical transaction approval latch, not a second approval protocol.
- **owner gets:** A pendant worn as jewelry will be bumped, brushed, and moving while walking. The owner gets fewer accidental approvals and can understand pending versus rejected actions without looking at a one-color LED or hearing an audio cue in a meeting.
- effort: Medium: enable i2c2 devicetree, add LSM6DSOX/DRV2605L drivers and calibration, implement a <2 KB classifier/state machine, then hardware-test false-accept and false-reject rates across walking, pocket, and deliberate gestures.  ·  risk: Bad calibration could reject legitimate approvals or create nuisance vibration. Fail closed on sensor/I2C errors and retain the existing explicit approval gesture as a fallback only when motion quality is unknown; never turn a failed sensor read into approval. Recover by disabling the classifier through a signed firmware configuration.
- cost: No new hardware cost; existing sensor and motor controller. Rough additional flash 15–35 KB and under 8 KB RAM; haptic bursts add negligible battery draw, IMU polling adds a few mA while pending.  ·  latency: Adds roughly 100–250 ms stability confirmation before accepting sw1; status haptic begins immediately so the owner is not left wondering.
- security: Improves physical-presence assurance but is not cryptographic proof. Sign the motion-quality code with the existing event nonce, avoid storing raw motion traces, and keep all page contents/secrets off-device.
- depends on: physical_transaction_approval_latch (s10-j9l4); i2c2 currently disabled in devicetree; A firmware-side signed event envelope and replay counter

### `new-surface` — Add a local pendant 'context capsule' surface that records a signed departure marker and a compact return marker, then asks the Mac agent to snapshot only owner-selected state domains at those boundaries. The capsule should support a per-domain privacy mode (counts/timestamps only, redacted semantic diff, or local-only full detail), immutable baseline IDs, retention expiry, and an owner command to erase one capsule without touching ordinary notes, audio, or action receipts.
- **owner gets:** The owner gets a reliable answer to “what changed while I was gone?” without turning the pendant into an always-on recorder or mixing temporary situational state into long-term memory.
- effort: High: define a new capsule schema and lifecycle, add Mac snapshot adapters for browser/calendar/messages/files, implement signed boundary events and local diffing, then build a small dashboard and spoken drill-down path.  ·  risk: A buggy adapter could expose more than intended or miss an important change. Default to metadata-only, show the domains covered, retain the original baseline for audit, and fail closed when a source cannot be snapshotted. Recovery is deletion of the capsule and disabling the affected domain.
- cost: No pendant hardware required for the first version; modest Mac storage (typically KB–MB per capsule). Background summarization costs roughly <$0.03 per capsule when enabled.  ·  latency: Departure capture should be nearly immediate; return comparison may take 3–10 seconds across multiple sources.
- security: This creates a new sensitive state class. Encrypt capsules at rest, keep full content local, redact before relay transmission, and make retention/deletion explicit. Do not infer physical location from the pendant clock or assume timezone beyond the Mac's authoritative zone.
- depends on: A signed pendant boundary-event protocol; Mac adapters with field-level snapshot and diff support; Owner-selected source-domain privacy and retention policy; A dashboard/voice drill-down route


## What it asked for

_Nothing._
