# Harness derivation — faculty-action — round 135

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live execution surfaces** — Safari browser bridge is online with 3 tabs and no pending commands; Mac agent reports fullControlMode and AppleScript/browser capability, but the relay device table still does not list the physically USB-attached pendant or ESP32 bridge.
  - evidence: GET /ops/status returned browserExtension.online=true, pendingCommands=0, fullControlMode=true; discover devices returned only Safari, home-macbook-bridge, and an offline mobile device.

## Capabilities it proposed

### "When I tap the pendant and speak a quick thought, turn it into the right action on my Mac: understand the note, use whichever Safari tab or project is relevant, create the task/note/draft, and buzz me with exactly what was created."
- **useful because:** A fleeting idea becomes useful without opening an app or later retyping it. The worn button supplies an intentional boundary, the bridge supplies audio, the relay supplies transcription/classification, and the Mac supplies private context and execution.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use realtime only to transcribe the short utterance and acknowledge; use a cheaper background planner to classify and execute against Mac/browser context.
- **latency:** Acknowledge in under 1 s; transcription and reversible creation within 5 s; haptic receipt even if the Mac is temporarily unavailable.
- **cost:** About $0.003–$0.02 per short capture depending on realtime transcription; Mac/browser execution dominates latency, not tokens.
- **security:** Audio leaves the bridge only for transcription; private tab contents stay on the Mac. Never send or submit external messages from this gesture; drafts and task creation need an explicit action policy and a receipt.
- **missing:** A pendant button/audio capture event delivered over the currently real USB serial link; Short-utterance transcription endpoint and intent/action schema; Context join from current browser tab, active project, and Mac applications; Haptic receipt command back to the pendant

### "If I walk away from my pendant, protect my private work automatically: pause or cancel pending reversible actions, hide authenticated browser sessions, and tell me what was protected when I return."
- **useful because:** The pendant is the one object that reliably indicates the owner's physical presence. This prevents an unattended Mac or logged-in Safari window from continuing a sensitive workflow, without requiring the owner to remember a lock command.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** No expensive model for the trigger; deterministic presence and policy logic. Use a background model only to summarize interrupted jobs when the owner returns.
- **latency:** Detect loss of the USB/BLE pendant link and apply privacy actions within 2 s; restore/review state within 10 s of reconnection.
- **cost:** Negligible model cost; local serial presence and browser commands dominate implementation, with an occasional cheap summary.
- **security:** Fail closed: disconnect must never unlock anything. Do not destroy drafts or data; pause/cancel only according to per-job policy. Reconnection must require the pendant's physical button for sensitive-session restoration, not proximity alone.
- **missing:** Presence-loss and reconnection events from pendant firmware over USB now (BLE/LTE later); Mac lock/privacy action with a reliable acknowledgement; Browser command to hide or suspend authenticated tabs without losing session state; Per-job interruption policy and durable resume/cancel receipts

### "Before you send, submit, purchase, or delete anything, show me the exact final change on the Mac and let me approve it with a deliberate two-tap pendant gesture tied to that specific preview; reject stale or mismatched approvals and leave a receipt."
- **useful because:** The owner can safely delegate real-world actions while keeping a physical, unambiguous final say. It is faster than returning to a screen and safer than voice-only confirmation, especially for authenticated browser transactions.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheap deterministic verifier for nonce, expiry, preview hash, and target binding; reserve realtime for the spoken explanation or clarification.
- **latency:** Render the preview and announce the approval challenge within 2 s; accept the two-tap gesture and execute within 3 s; refuse after a short expiry (for example 60 s).
- **cost:** Near-zero model cost for the approval path; browser/Mac execution and evidence capture dominate.
- **security:** Approval must bind to a hash of the exact target, fields, account, and before-state, with single use and expiry. Never treat a voice utterance or mere pendant presence as approval. Record before/after evidence and expose undo where possible.
- **missing:** Pendant gesture event and local two-tap debounce; Signed challenge/nonce channel between relay, Mac, and pendant; Preview hash and final-state verifier shared by browser and Mac action runners; A physical receipt pattern plus durable audit record

### "When you carry out a multi-step request across my Mac and logged-in sites, either finish it completely or show me exactly which steps succeeded, compensate the reversible ones, and leave a recovery plan for anything irreversible."
- **useful because:** Today a browser or app can change halfway through a task and leave the owner to reconstruct what happened. A cross-surface transaction with explicit compensation turns partial failure into a recoverable outcome rather than hidden damage.
- **path:** relay-realtime → mac-planner → mac-terminal → browser-extension → dashboard → pendant
- **model tier:** Use deterministic orchestration and receipts for execution and compensation; use a cheaper background model only to draft the recovery explanation. Realtime is needed only if an immediate pendant escalation is required.
- **latency:** Normal steps should proceed at current tool speed; detect a failed precondition within 2 s, stop before the next irreversible boundary, and present a recovery state within 5 s.
- **cost:** Small storage and orchestration overhead; no additional model call for successful tasks, roughly $0.001–$0.01 for a generated recovery summary.
- **security:** Never claim rollback for an external send, purchase, or deletion that cannot be reversed. Store per-step before/after evidence, compensation status, and an explicit irreversible boundary; require owner confirmation before retrying with changed inputs.
- **missing:** A durable cross-surface saga/state-machine runner; Typed compensating actions for Mac and browser operations; A common step receipt and failure taxonomy; Dashboard and pendant presentation of partial-success/recovery states

### "Before anything leaves my Mac—an email, form, message, upload, or calendar invite—check the final payload against my private data rules, identify secrets or sensitive facts, and offer a redacted alternative while preserving the exact original for my review."
- **useful because:** Approval alone does not tell the owner that an attachment contains a credential, or that a browser form is sending private information to the wrong recipient. This is a last-mile privacy check across apps and authenticated sites.
- **path:** mac-planner → mac-terminal → browser-extension → relay-realtime → dashboard → pendant
- **model tier:** Use deterministic secret/recipient/policy checks first; use a cheap classifier for ambiguous sensitivity. Reserve realtime for a concise spoken warning, not inspection or execution.
- **latency:** Inspect a normal payload in under 1 s and show a redaction diff within 3 s; block the outbound action until resolved.
- **cost:** Usually local CPU and hashing only; ambiguous text may cost under $0.005 per outbound action.
- **security:** Inspection must happen locally where possible; never upload raw secrets to the relay. Keep originals encrypted and short-lived, redact dashboard logs, and distinguish a warning from an approval. No payload may be sent on classifier confidence alone.
- **missing:** A common outbound interception point for AppleScript, browser, and terminal actions; Owner-editable sensitivity rules and recipient trust policy; Local secret/PII detector with explainable spans; A redaction-diff UI and a hard pre-send gate

### "Let me give you a goal with a deadline and a bounded budget, then keep working across my Mac and logged-in browser until it is done, blocked, or the budget is exhausted; if blocked, ask me one precise question through the pendant instead of abandoning the task."
- **useful because:** The owner should be able to delegate outcomes rather than micromanage steps. A deadline and budget make autonomy predictable, while a single targeted escalation prevents long jobs from silently stalling.
- **path:** relay-realtime → mac-planner → mac-terminal → browser-extension → pendant → dashboard
- **model tier:** Use a cheaper background planner for long-running decomposition and retries; use realtime only for the one-question escalation and the final spoken result.
- **latency:** Accept the goal immediately, make progress asynchronously, escalate only on a real blocker, and deliver a completion/blockage receipt by the deadline.
- **cost:** Background planning and tool calls dominate; cap model spend per job and avoid realtime except for escalation.
- **security:** Enforce hard time, step, API-call, and monetary budgets; pause at irreversible actions; disclose which accounts and data were accessed; expire the delegation lease at the deadline.
- **missing:** A durable goal-level scheduler with deadline and resource budgets; A blocker detector that can formulate one minimal question; Pendant notification/reply routing with timeout handling; Budget-aware retries and a final evidence-based outcome record


## Changes it proposed to its own stack

### `integration` — Add a local USB-serial pendant gateway in the Mac agent: open /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA with exclusive, read-only-safe framing; normalize button, audio-ready, disconnect, and bridge playback events into authenticated pipeline events; route haptic/LED receipts back only after the relay records the job receipt. Include reconnect backoff, sequence numbers, and a simulator mode so no flash or firmware change is needed.
- **owner gets:** The pendant and audio bridge that are physically on the owner's desk become usable today: a tap can start an action and the owner gets a trustworthy physical receipt instead of a silent server-side success.
- effort: Medium: serial framing, device discovery, event schema, and integration tests against simulators; no hardware flash.  ·  risk: A malformed serial frame could trigger an unintended action. Default all new events to capture-only, require explicit policy opt-in for execution, validate lengths/sequence, and close ports on errors. Recovery is reconnect and replay only idempotent events.
- cost: No meaningful API cost; one small local daemon and negligible CPU/power.  ·  latency: Under 100 ms for local button-to-relay event; serial reconnect may take seconds.
- security: Device identity must be pinned to VID/PID and serial path plus challenge response; do not trust arbitrary USB serial input as approval.
- depends on: A documented serial protocol from the firmware source; A pipeline event type for device-originated input; Owner-approved action policy for capture versus execution

### `relay` — Introduce an immutable action manifest exchanged between judgement and action: canonical target, account/session, before-state digest, intended mutation, expiry, and one-time nonce. The Mac/browser runners must verify the manifest immediately before execution and emit a signed before/after receipt; any changed page, stale nonce, or missing evidence becomes a refusal rather than a best effort.
- **owner gets:** The system can finally tell the owner exactly what it is about to change and prove that the thing it changed was the thing they approved, even when a page or application shifts underneath it.
- effort: Medium-high: canonicalization shared across Worker and Mac, browser extraction digesting, refusal states, and receipt UI.  ·  risk: Overly strict digests can refuse harmless dynamic pages. Separate volatile fields from mutation fields and offer a re-preview, never silently broaden the target.
- cost: Small storage and hashing overhead; no extra model call on the normal path.  ·  latency: Tens of milliseconds for hashing, plus one evidence read before and after.
- security: Strongly improves anti-confusion and replay resistance; manifests must avoid storing raw secrets and redact sensitive values in dashboard receipts.
- depends on: A physical or explicit approval channel; Typed browser/Mac action results; Durable receipt storage and undo routes

### `firmware` — Add a minimal presence/beacon state machine to the pendant firmware that emits signed connect, disconnect, button, and monotonic-counter frames over USB serial, with a local red LED pattern for armed/privacy state. Keep all policy and action decisions on the Mac/relay; firmware only reports physical state and renders receipts.
- **owner gets:** The owner gets a dependable physical boundary for privacy and approval without putting cloud credentials or risky decision logic on a tiny wearable.
- effort: Medium: frame format, counter persistence, debounce, watchdog-safe serial task, and host simulator; requires owner-controlled build/flash later.  ·  risk: Firmware bugs could cause missed presence or stuck LED. Fail closed in the host, watchdog the task, and make the Mac treat silence as unknown—not approval.
- cost: Negligible runtime power; a few KB flash/RAM. Build/flash remains owner-controlled because secrets/toolchain are protected.  ·  latency: Immediate local event reporting; no model latency.
- security: Signed/countered frames prevent replay of an old button press; no secrets need to live in firmware if host challenge-response is used.
- depends on: Owner-run firmware build and protocol review; Mac USB gateway; A host-side challenge-response key provisioned separately


## What it asked for

_Nothing._
## Its own summary

Produced three new cross-device capabilities: (1) a deliberate pendant-tap voice capture that classifies a fleeting thought using private Mac/browser context, creates the appropriate reversible artifact, and returns a physical receipt; (2) presence-bound privacy that protects authenticated work when the pendant leaves and restores/reviews it on return; and (3) a nonce-bound two-tap physical approval for exact browser/Mac transactions. Also proposed three implementation changes: a USB serial gateway for the actually connected nRF9160/ESP32 devices, immutable before/after action manifests, and a minimal signed presence/button firmware state machine. The live Mac surface is strong: full-control mode and Safari bridge are online with zero pending commands. All proposals were recorded, though the recorder noted the first and third are adjacent to existing capture/approval work; their genuinely new parts are the physical serial path, presence binding, and exact manifest verification.

**Biggest unknown:** I still need the owner-controlled serial protocol (or a simulator contract) for the pendant and audio bridge, plus the explicit policy defining which pendant gestures are capture versus approval. I also need a host challenge-response key/provisioning decision before treating a physical gesture as trustworthy. The relay device table still does not expose the USB-attached pendant, so end-to-end testing cannot yet prove the physical event path.

