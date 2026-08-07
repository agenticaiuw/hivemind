# Harness derivation — faculty-action — round 118

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **current device reachability** — As of Round 118, home-macbook-bridge is online and authenticated Safari has three tracked tabs/sessions; no pendant is connected and the mobile test device remains offline since 2026-07-31. The Mac job/receipt path is live, but at least one browser navigation receipt is marked irreversible and unlinked to evidence.
  - evidence: discover(devices) and GET /browser/sessions, GET /jobs

## Capabilities it proposed

### "When I tell you to change something across my Mac and a logged-in website, carry it through as one transaction: show me what changed, recover safely from a dropped connection or partial step, and tell me exactly what still needs my hands."
- **useful because:** Today the mind can decide an outcome but execution can split across browser, Mac, relay, and absent pendant. This gives the owner one accountable result instead of silent partial completion or duplicate clicks.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use the realtime model only to collect intent and deliver a short status; use the cheaper background planner for step decomposition, reconciliation, and receipt summarization.
- **latency:** Acknowledge in under 2 seconds; reversible steps may run asynchronously for up to 2 minutes; stop immediately at an irreversible checkpoint and wait for owner approval.
- **cost:** About $0.01–$0.08 per transaction, dominated by background planning and browser evidence extraction; realtime status should be a few cents or less.
- **security:** Private page data and action evidence cross the Mac/relay boundary. Store redacted signed receipts, bind every step to tab/session and an idempotency key, and require explicit confirmation for sending, deleting, purchasing, or external side effects. Never replay an unacknowledged step after reconnect.
- **missing:** A durable transaction coordinator that understands partial completion and compensating actions (the current receipt/undo work has no gates or preconditions); Signed step proofs and a reconnect-safe pendant acknowledgement protocol; A deterministic reconciliation worker that compares intended, observed, and completed state across Mac and browser; A clear dashboard timeline for pending approval, completed, compensated, and needs-owner states

### "Let me approve a prepared Mac or logged-in-browser action with one physical press on the pendant, but only when the pendant is demonstrably near my Mac; show me the exact action on the pendant first, and keep it paused if the pendant, relay, or browser session is not the same one that prepared it."
- **useful because:** Today approval is logically possible but not strongly tied to the owner’s physical presence or to the exact prepared browser state. This would let the owner safely approve from the pendant without opening the laptop, while preventing a stale, replayed, or remotely substituted transaction from executing.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use the realtime tier only to parse the spoken approval and provide a brief status; use deterministic firmware/relay verification and a cheaper background model only for explaining a blocked or changed transaction.
- **latency:** Pendant should display the prepared action class within 500 ms, accept the press in under 1 second, and have the Mac execute or report a mismatch within 3 seconds.
- **cost:** Usually below $0.01 per approval; cryptographic verification and BLE/proximity checks dominate, with model cost only when a human-readable mismatch explanation is needed.
- **security:** Bind approval to a transaction hash, Mac bridge identity, browser session/tab identity, expiry, and one-time nonce. Do not treat BLE presence alone as authorization for high-risk actions; require a distinct long press and retain the existing confirmation policy for sending, deleting, purchasing, or other irreversible effects. Keep page contents off the pendant and relay except for a short redacted summary.
- **missing:** A pendant hardware identity and authenticated proximity channel to the Mac; A signed transaction envelope containing action hash, target session/tab, expiry, and risk class; Firmware rendering of a short redacted action summary and a distinct approval gesture; Relay verification that rejects stale, replayed, cross-device, or session-changed approvals; Mac/browser execution hook that consumes the one-time approval atomically


## Changes it proposed to its own stack

### `hardware` — Replace the prototype nRF9160-only pendant interaction path with a production companion module that provides authenticated BLE plus UWB ranging to the Mac bridge, a secure element for device keys, and a small haptic actuator. Keep the existing button/LED as fallback, but make proximity proofs and approval feedback local hardware functions rather than model or browser behavior.
- **owner gets:** The owner can approve a prepared computer action from the pendant with confidence that the approval is happening beside their own Mac, and can feel success, rejection, or expiry without opening the laptop or relying on speech in a noisy environment.
- effort: High: select and integrate a low-power ranging radio and secure element, add firmware drivers and signed challenge-response, add a Mac bridge verifier, and validate battery, enclosure, and radio coexistence. This is a product-hardware change, not a firmware-only patch to the current development kit.  ·  risk: Extra radio and key-management complexity can increase power draw and false 'not nearby' results. Fall back to no approval (never fail open), retain button/LED behavior, and provide a dashboard diagnostic explaining ranging failures.
- cost: Roughly $15–$35 additional prototype BOM, plus several mA during ranging bursts; production cost depends on radio choice and antenna design. No per-action API cost beyond small verification events.  ·  latency: Typical local proximity proof in 0.5–2 seconds; haptic acknowledgement is immediate. Battery life will be lower unless ranging is duty-cycled around pending approvals.
- security: Device keys must be hardware-protected and rotatable; use challenge-response and distance bounds, not RSSI alone. Never transmit page contents over the proximity link, and treat failed or ambiguous ranging as a hard stop.
- depends on: A signed transaction-envelope format shared by relay, Mac/browser harness, and pendant firmware; A connected pendant prototype for RF, power, and interaction validation; Owner approval policy defining which risk classes may use physical approval


## What it asked for

### `s4-366w` (skill) — offline_action_cancel_latch
- does: When the pendant has displayed or received a pending physical/computer action token, a long press (for example 1.5 seconds) marks that token cancelled locally and transmits the cancellation when connectivity returns. A short press only acknowledges status; it must never approve an irreversible action. LED patterns distinguish pending, cancelled, and unknown/no-token.
- must be on-device because: Cancellation must work during a dropped relay/Mac link and must be physically available while the owner is away from the keyboard. Server-side cancellation alone cannot stop a queued retry quickly enough.
- trigger: A long press of the single user button while a pending action token is locally cached; also a server push may clear the token but cannot approve it.
- storage: One compact record in nonvolatile settings: transaction UUID/hash (32 B), expiry (8 B), state and counter (~16 B), signature/tag (~32 B), plus two rotating records for crash recovery: under 256 B total.
- RAM budget: ~2–4 kB including event queue, debounce/timer state, and crypto verification buffers; leave the audio/Opus buffers untouched within the 211,608 B application RAM budget.

