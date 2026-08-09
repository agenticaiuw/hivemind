# Harness derivation — faculty-action — round 162

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Do this on my Mac, and keep trying safely until you can prove it worked—or tell me exactly what is unknown.”"
- **useful because:** This would turn the system from a fire-and-forget remote control into a truthful executor: faculty-judgement can stage a multi-step plan, faculty-action can execute it across Mac and browser, and faculty-perception independently verifies each postcondition. If a step fails, the relay can retry only idempotent steps or run a declared compensation; the owner gets a single result of verified, safely rolled back, or unknown instead of a misleading success.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for planning and reconciliation; realtime only for the short spoken confirmation and urgent cancellation
- **latency:** 1–3 seconds to stage; ordinary steps may take up to 60 seconds; never claim completion before independent verification
- **cost:** Roughly $0.01–$0.08 per workflow, dominated by planner/reconciliation model calls; verification and receipts are local/HTTP reads
- **security:** Action summaries, not secrets or page contents, go to the pendant. Irreversible or ambiguous steps require the existing physical approval latch. Retries need idempotency keys, deadlines, and a visible unknown state; compensation must never be guessed.
- **missing:** A workflow executor that persists step dependencies, idempotency keys, compensation policy, and verified/unknown terminal states; A relay fan-in that correlates mac_run_actions/browser_run_actions receipts with verify_operation_step results; Owner-configured risk policy for which classes may retry or compensate

### "“When the pendant is plugged into my Mac, make it work as a real local voice terminal automatically; if the cable disappears, continue through LTE or queue safely without losing my turn.”"
- **useful because:** The hardware is physically present over USB today while LTE registration is not. A tether-aware session would make the wearable useful now: button, microphone, speaker and Mac bridge form a low-latency local path, while the relay preserves conversation identity and hands off to LTE when available. The owner should not have to know which transport is carrying a turn or repeat a request after a cable/link transition.
- **path:** pendant → relay → mac-bridge → Mac → dashboard
- **model tier:** Realtime for the active voice turn; a cheap background worker reconciles transport handoff, queued audio, and receipts
- **latency:** USB local audio acknowledgement under 150 ms; transport handoff under 2 seconds; queued turns must survive arbitrary disconnects
- **cost:** Near-zero incremental model cost for transport selection; $0.001–$0.02 per deferred turn for background transcription/summarization, dominated by audio retention and STT
- **security:** The Mac bridge must authenticate the serial device and bind a session to a device nonce; never accept arbitrary serial input as owner speech. Local recordings remain ephemeral unless upload fails, following the existing failure-only SD rule. Handoff must reject duplicate turn IDs and replayed audio.
- **missing:** A production serial daemon implementing the nRF9160/ESP32 framing, HELLO and CRC negotiation, with reconnect and backpressure; Relay transport/session handoff keyed by device identity and monotonic turn cursor; An explicit local-vs-LTE routing policy and a user-visible indicator of queued versus delivered turns

### "“For the next hour, let this specific task run within the limits I just gave you; stop immediately if it exceeds them, and let me revoke it from the pendant.”"
- **useful because:** Today every consequential action needs to be staged individually, while broad unattended automation would be unsafe. A bounded delegation capsule would let the owner authorize a narrow goal—such as triaging one mailbox label or preparing a travel search—without exposing credentials to the pendant or granting the Mac an open-ended mandate. The capsule expires, is scoped to named apps/data/action classes, and can be revoked physically.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for capsule planning and progress evaluation; realtime only for the owner’s initial spoken grant and revocation acknowledgement
- **latency:** Grant and revocation feedback under 1 second; capsule execution can run for the owner-specified duration with periodic progress updates
- **cost:** About $0.02–$0.15 per capsule, dominated by planning and periodic policy evaluation; revocation and enforcement are local protocol operations
- **security:** The pendant receives only a human-readable scope summary and opaque capsule ID, never credentials or page contents. Mac/browser executors must enforce scope independently, deny privilege expansion, attach every action to the capsule, and fail closed at expiry or link loss. Destructive actions remain separately gated.
- **missing:** A capability-token format with scope, app/site allowlist, data-class restrictions, expiry, budget, and revocation counter; Enforcement hooks in Mac and browser executors before every action, not merely relay-side logging; A compact pendant display/LED/audio vocabulary for scope, expiry, progress, and revoked states

### "“Move the selected private value from the logged-in browser into the correct Mac app, but do not show the value to the model, relay, dashboard, or pendant—and prove the destination matches.”"
- **useful because:** This would enable practical cross-surface work with passwords, API keys, medical identifiers, and payment details without making the AI a holder of those secrets. The browser bridge would read the selected field locally, the Mac agent would deliver it through an OS-protected handoff, and perception would verify only a cryptographic commitment or field-state result.
- **path:** browser → mac-bridge → Mac → relay → dashboard
- **model tier:** Realtime only to clarify the destination; all extraction, transfer, and verification should be deterministic local code
- **latency:** Under 2 seconds for a normal field transfer; never upload raw secret bytes or put them in model context
- **cost:** Effectively zero model cost after intent clarification; implementation cost is local integration and OS keychain/secure-paste work
- **security:** Raw values must remain on the Mac/browser trust boundary, with one-shot handles, zeroization, origin and destination binding, expiry, and user confirmation for high-risk destinations. Verification must use type/length/hash or a destination-specific non-secret marker, never echo the value.
- **missing:** A browser-bridge secret-handle API that returns an opaque one-shot reference rather than field text; A Mac local-agent secure handoff into approved apps, avoiding the general clipboard and model-visible logs; Destination-specific postcondition verifiers that can prove insertion without reading the secret back

### "“Watch this logged-in page for the condition I described, notify me on the pendant with a compact proof when it becomes true, and only then offer the next action—never keep clicking on my behalf.”"
- **useful because:** The owner cannot currently turn a browser session into a trustworthy standing sensor. This would let the browser extension observe a specific field or URL transition over hours or days, while the relay sleeps, then wake the pendant with evidence and a bounded next step. It is useful for appointment openings, package status, price changes, and application status without an agent repeatedly taking actions or silently using stale state.
- **path:** browser → relay → pendant → dashboard → mac-bridge
- **model tier:** Cheap background polling/event evaluation; realtime model only when the owner asks what changed or wants to authorize the next action
- **latency:** Polling interval chosen per site and rate limit; alert delivery within one interval plus a few seconds; no continuous model invocation
- **cost:** Usually under $0.01/day per watch, dominated by browser/relay uptime and page fetches; model cost only for ambiguous changes or owner questions
- **security:** Watch definitions must be bound to a browser profile/session and origin, with encrypted storage and explicit expiry. Evidence sent to the pendant must be minimized and redact sensitive fields. The watcher is read-only until a fresh physical approval for a separate action; stale alerts cannot authorize execution.
- **missing:** A durable browser-session watch worker that can survive bridge restarts and preserve tab affinity; A change detector returning locator-scoped evidence, timestamp, URL, and freshness rather than whole-page snapshots; A pendant alert/inbox protocol with deduplication, snooze, expiry, and an explicit read-only boundary


## Changes it proposed to its own stack

### `hardware` — Add a sealed low-power ERM/LRA haptic motor and a second tactile switch to the wearable revision, with a tiny driver controlled by a dedicated GPIO. Keep the current sw0 active-edge path unchanged; assign sw1 to deliberate gestures (repeat, cancel, or approval) and use haptic patterns for pending, accepted, cancelled, and link-lost states. The firmware should expose the same event envelope over USB/LTE so the relay remains the authority.
- **owner gets:** The owner can operate and safely confirm actions in public or noisy places without putting private audio on the speaker, and a second button removes the current ambiguity between instant talk and deliberate approval/replay gestures.
- effort: Moderate hardware revision: board layout, enclosure, driver, current draw characterization, firmware gesture/state machine, and manufacturing prototype.  ·  risk: Added motor noise can leak into the microphone and false gestures can be dangerous. Require debounce, a physically distinct switch, conservative defaults, and preserve the existing approval latch semantics. If the motor fails, LED/audio cues remain available.
- cost: Approximately $1–$4 BOM increase in volume, plus PCB/enclosure NRE. Typical haptic pulse is tens of mA for under 200 ms; negligible average draw if used only for state transitions, but LTE battery impact must be measured.  ·  latency: Immediate local feedback (<50 ms) and no model/relay latency. Haptic actuation must not block audio or LTE tasks.
- security: Improves privacy by replacing audible confirmation cues. The second switch is not authority by itself: relay-issued nonce, expiry, digest, and monotonic counter remain mandatory.
- depends on: physical_transaction_approval_latch; last_response_replay_cursor; A firmware gesture contract that reserves sw0 for active-edge conversation start/stop and sw1 for deliberate gestures


## What it asked for

### `s9-mx5h` (skill) — last_response_replay_cursor
- does: Keeps a crash-safe cursor and a bounded cache of the last successfully delivered agent response. A deliberate gesture on sw1 (or the existing end-of-turn control once gesture semantics are specified) asks the relay/Mac bridge to replay from the last acknowledged audio cursor, and the pendant can request “repeat” even if the original downlink was interrupted. It must distinguish replay from a new turn and never enqueue a duplicate owner command.
- must be on-device because: The pendant is the only surface that knows the owner missed audio at the moment it happened and the only one that remains available during a USB/LTE transition. A local cursor survives a dropped link and prevents the owner from having to reconstruct a request by voice.
- trigger: A dedicated sw1 gesture or a relay push indicating an interrupted downlink; do not overload sw0 active-edge behavior without changing the firmware gesture contract.
- storage: Persist only a small manifest in the existing typed INBOX: response ID, cursor, codec/rate, expiry, checksum, and replay count (well under 1 KB). Audio payload remains in the existing failure-path SD/relay object store; do not make a second always-on audio archive.
- RAM budget: About 4–8 KB for cursor state and one Opus frame/packet staging buffer, plus existing audio buffers; no PCM ring buffer. This stays comfortably below the 211,608 B application RAM budget, but firmware must measure peak heap/stack with the current 24 kHz decoder.

