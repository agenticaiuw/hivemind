# Harness derivation — faculty-action — round 216

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I say “pause everything” or the pendant detects that I have fallen or started moving rapidly, cancel any staged computer action before it commits, and tell me whether cancellation was confirmed."
- **useful because:** A voice assistant can queue a dangerous action while the owner's attention is elsewhere. The pendant is the only surface physically attached to the owner and can provide a last-moment safety interlock; motion-triggered cancellation protects against accidental execution during a fall, pocket squeeze, or hurried movement.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-judgement → faculty-perception
- **model tier:** Realtime only for interpreting the explicit cancel phrase and low-latency relay; deterministic firmware motion classification and relay policy handle the safety decision without an expensive model.
- **latency:** Motion event to relay cancellation request under 300 ms on a live link; staged operations must have a bounded commit grace period (for example 2 s) so the interlock is meaningful.
- **cost:** Near-zero model cost for IMU events; occasional realtime turn cost only when speech is needed. Firmware integration and relay policy dominate engineering cost.
- **security:** A motion event may cancel but must never approve. Require an opaque operation nonce and monotonic event counter; fail safe on stale, duplicated, or ambiguous motion packets. Do not transmit raw accelerometer traces by default—send a classified event and short confidence/window metadata. A network drop must leave the operation staged, never commit it.
- **missing:** i2c2 firmware enable and LSM6DSOX driver/calibration; relay route to cancel a specific staged operation from a signed pendant event; operation state machine that honors a short commit grace period; owner-configurable motion sensitivity and explicit opt-out for activities such as running

### "When I am in a meeting, keep the pendant completely silent but still let me ask it to queue notes or Mac actions; give me private haptic outcomes and read everything aloud only after the meeting ends."
- **useful because:** The pendant should remain socially invisible without becoming useless. The Mac can recognize the active meeting app and the browser can identify the meeting tab, while the worn device supplies a private tactile channel and the relay can defer speech until it is safe.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception
- **model tier:** Use deterministic app/browser state for meeting detection and a cheap background model for summarizing queued outcomes; reserve realtime for the owner's actual spoken request and only when audio is permitted.
- **latency:** Meeting-state changes reflected within 2 seconds; haptic acknowledgement under 500 ms. Deferred spoken recap may wait until the owner explicitly exits meeting mode.
- **cost:** No model cost for state detection or haptic patterns; modest background summarization cost proportional to queued notes/actions.
- **security:** Meeting detection must be conservative: unknown state means do not capture or transmit meeting audio. Never record microphone audio merely to detect a meeting. Keep private haptic patterns non-descriptive enough that bystanders cannot infer message content; store only encrypted queued intents and action receipts, with expiry and explicit owner review before executing queued mutations.
- **missing:** meeting-state adapter from frontmost Mac app and browser session identity; relay-held silent-mode policy and deferred-audio queue; pendant firmware mode bit plus distinct haptic acknowledgement patterns; explicit owner command or rotary gesture to exit meeting mode and release queued speech/actions

### "When I miss your last answer, turn the pendant wheel one click and press to hear that answer again; turning farther should move through the last few answers, without asking the model to regenerate them."
- **useful because:** A missed spoken answer is not a failed network delivery. The pendant is the only surface that knows the owner wants a replay immediately, and replaying the original artifact is faster, cheaper, and more faithful than regenerating speech. A wheel gives this a discoverable control without stealing either existing button.
- **path:** pendant → relay-realtime → mac-planner
- **model tier:** No model for selection or replay; use the original audio artifact and its delivery cursor. A cheap background model may generate a compact index label, but it is optional.
- **latency:** Wheel selection haptic within 100 ms and playback start within 500 ms when the artifact is cached; if not cached, fetch only the missing range and report unavailable rather than regenerate.
- **cost:** Zero inference cost for replay; storage and bandwidth for a bounded recent-artifact cache dominate.
- **security:** Persist only opaque response IDs, checksums, codec/sample rate, expiry, and playback cursor—not transcript content by default. Verify checksum before playback, deduplicate delivery acknowledgements, expire private answers, and require the owner to press the wheel to play; never replay sensitive audio automatically in a public setting.
- **missing:** rotary encoder and second selection button in the jewellery enclosure; firmware wheel event protocol and bounded recent-response index; relay lookup/fetch for original audio artifacts by opaque ID and range; private-mode policy that suppresses replay when the owner has not explicitly requested it

### "When I get interrupted, let me say “where was I?” and hear a short, exact resume capsule: the last audio point, the Mac app and browser session I was using, any unfinished job, and the next safe step—without reconstructing the task from memory."
- **useful because:** Interruption is where a wearable assistant loses the owner's trust. A durable cross-surface cursor can restore the precise working state in seconds instead of making the owner repeat context or risking a duplicate action.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception
- **model tier:** Deterministic state assembly first; use a small background model only to compress already-collected state into a short spoken capsule. Realtime is reserved for the spoken request and playback.
- **latency:** Return a capsule within 2 seconds on a live link; stale or missing components must be labeled explicitly rather than guessed.
- **cost:** Low: mostly structured state and one short compression call. Storage is bounded to the latest few interruption checkpoints.
- **security:** Do not include page secrets, form values, or raw meeting audio. Each component needs its own freshness and sensitivity label; an old checkpoint must never be presented as current. Resuming a mutation requires a new approval, not implicit continuation.
- **missing:** atomic checkpoint envelope spanning audio cursor, Mac observation, browser session, and job state; relay endpoint to assemble and expire interruption checkpoints; pendant command/input for requesting a capsule; redaction policy for browser and focused-app state

### "Let me say “private curtain” and have every surface immediately stop exposing or retaining sensitive context, show me a private haptic confirmation, and keep any queued action paused until I explicitly reopen the curtain."
- **useful because:** The owner needs a single physical/voice escape hatch when another person enters the room or a confidential screen appears. Today privacy is fragmented across relay audio, Mac observation, browser state, and queued jobs; one command should make the whole hive conservative.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Deterministic policy propagation and local redaction; no model is needed to enter or leave the curtain. Realtime may acknowledge the command, but must not echo the sensitive triggering phrase or context.
- **latency:** Haptic acknowledgement under 300 ms locally; relay and Mac/browser redaction state under 1 second. If a surface cannot confirm, report partial privacy rather than claiming success.
- **cost:** Negligible inference cost. Engineering cost is in a signed mode protocol, local cache scrubbing, and testing races with in-flight browser/Mac commands.
- **security:** The curtain must be fail-closed on link loss and survive relay restarts. It must stop new captures, discard unsent sensitive buffers, redact observation payloads, suspend mutation commits, and expire queued approvals. Leaving private mode must require an explicit owner gesture or phrase; never infer it from silence. A signed mode epoch prevents stale 'open' messages from reopening a newer curtain.
- **missing:** privacy-mode epoch propagated across relay, Mac, browser, and pendant; Mac/browser hooks that stop capture and redact already-buffered observations; bounded purge protocol for pending audio/context data; owner-visible per-surface confirmation and explicit reopen gesture

### "After you answer a factual question, let me ask “show me the source” and hear or view the exact browser page, document, or Mac file that supported that answer, with the source timestamp and a statement of what was actually checked."
- **useful because:** A spoken answer is hard to trust when the owner cannot inspect its basis. This links the wearable's audio artifact to concrete browser/Mac evidence, making errors discoverable without asking the model to explain itself or silently browsing again.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception
- **model tier:** Use a cheap structured provenance assembler and only a realtime turn for the owner's follow-up. Do not regenerate the original answer; retrieve the recorded evidence pointers and snippets.
- **latency:** Source index within 1 second from cached evidence; opening the exact browser page or file within 3 seconds. If evidence is stale or unavailable, say so plainly.
- **cost:** Low inference cost; bounded provenance metadata and optional short redacted snippets dominate storage and bandwidth.
- **security:** Never expose passwords, tokens, private form fields, or unrestricted page text. Store opaque source IDs, URL/file hashes, timestamps, selectors, and minimal redacted excerpts. Access must be authorized in the owner's current browser session; expired or changed sources become 'not verified' rather than silently refreshed.
- **missing:** answer-to-evidence provenance envelope linking audio/response ID to source records; browser and Mac evidence capture with redaction and immutable timestamps; pendant command to request provenance and a compact spoken rendering; retention and invalidation policy for private or changed sources


## Changes it proposed to its own stack

### `firmware` — Enable i2c2 and integrate the existing LSM6DSOX plus DRV2605L as a local event subsystem: calibrated motion classes (still, walking, fall-like impulse, deliberate shake) with hysteresis and a monotonic event counter, and private haptic patterns for queued/cancelled/unknown action outcomes. Emit only signed classified events over the relay protocol; never stream raw IMU data in normal operation.
- **owner gets:** The pendant becomes a reliable physical safety and feedback channel: it can cancel a staged action when the owner's body says something is wrong and can communicate privately without a visible gadget-style LED or spoken audio.
- effort: Medium firmware work: devicetree/CMake integration, I2C driver setup, calibration persistence, event debounce, protocol fields, and bench validation while USB-connected. No new sensor or motor purchase is needed.  ·  risk: False motion classifications could cancel harmless actions or miss a fall. Default to cancellation-only (never approval), require explicit opt-in for motion cancellation, expose sensitivity, and log only bounded counters. Recover by disabling the motion policy remotely while retaining basic haptics.
- cost: No material API cost; existing parts. Rough incremental power draw depends on sensor mode, likely a few mA, and should be measured against the 500 mAh cell.  ·  latency: Local classification and haptic start should be tens of milliseconds; relay cancellation remains network-limited.
- security: Improves safety if signed and replay-protected. Raw motion data is sensitive and should remain on-device; use nonce/counter plus device authentication for event envelopes.
- depends on: relay operation cancellation endpoint keyed by opaque operation ID; owner policy for whether motion cancellation is enabled; calibration procedure on the actual enclosure


## What it asked for

_Nothing._
## Its own summary

Recorded three cross-surface capabilities and one firmware change: (1) IMU-triggered fail-safe cancellation of staged Mac/browser actions, (2) socially invisible meeting mode with haptic acknowledgements and deferred speech, (3) wheel-based replay of original undelivered/missed answer artifacts without regeneration, and (4) integrating the owned LSM6DSOX/DRV2605L over i2c2 for classified motion and private feedback. What I still need is not another permission this round: concrete relay cancellation keyed by operation nonce, a meeting-state source and silent-mode policy, and the future rotary encoder/wheel plus its event protocol. The current pendant has only sw0/sw1, so replay selection cannot be built honestly until the owner’s planned wheel/second button is wired. I also need the owner to choose whether motion cancellation is opt-in and how sensitive it should be; I will not invent that policy.

**Biggest unknown:** Whether the owner wants motion cancellation enabled at all, and what physical motion should count as an emergency cancel. The existing hardware supports measuring it, but no safe default can be inferred. Also, tactile_action_outcome_beacon appeared as an unrecognized named piece in proposal composition despite being granted context, so its concrete relay/firmware contract still needs inventory before implementation.

