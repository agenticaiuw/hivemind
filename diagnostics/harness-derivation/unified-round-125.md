# Harness derivation — unified — round 125

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Before I send or submit anything, say “safety check this” and have you inspect the proposed text and its source context across my open Safari tabs, Mac drafts, and the pendant transcript; flag secrets, personal data, wrong recipients, stale facts, and irreversible consequences, then return a redacted ready-to-send version plus a spoken risk summary. Never send it automatically."
- **useful because:** The existing review flows show before/after mutations, but do not protect the owner from accidentally leaking a credential, sending to the wrong person, or relying on stale private-page data. This gives one consistent safety gate across browser, Mac, and voice context before the owner approves.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-terminal → dashboard
- **model tier:** Use the realtime model only to understand the spoken request and read back the concise risk summary; use a cheaper background model for secret/PII classification, stale-source comparison, and draft redaction.
- **latency:** 3 seconds for an initial risk banner; up to 10 seconds for cross-surface evidence and a complete redacted draft.
- **cost:** Roughly $0.01–$0.05 per check; most cost is private-page extraction and classification, not the final spoken sentence.
- **security:** Data stays within the authenticated browser/Mac/relay path, but the checker necessarily sees the draft and source context. Never persist raw secrets; retain only hashed evidence and the owner's approval decision. Sending/submitting remains confirmation-gated.
- **missing:** A cross-surface draft context collector with source locators and freshness timestamps; A deterministic secret/recipient/irreversibility scanner and redaction policy; A typed approval payload binding the exact redacted bytes to the eventual send action

### "If I press and hold the pendant button and say “stop everything,” immediately silence playback, cancel queued Mac and browser work, and freeze any staged send or purchase; then tell me exactly what was interrupted and what, if anything, is safe to resume. The stop must work even if the conversation link is degraded."
- **useful because:** A single wearable kill switch is the clearest trust boundary for an AI that can act in private browsers and on a Mac. It lets the owner interrupt a runaway loop, an embarrassing read-aloud, or an imminent transaction without finding the phone or laptop, while preserving a truthful recovery point.
- **path:** pendant → ESP32 audio bridge → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** The pendant and relay perform the stop deterministically with no model call; a cheap background model may summarize interrupted jobs afterward. Realtime is used only for the short spoken acknowledgement when the link is healthy.
- **latency:** Local mute and cancellation signal under 150 ms; relay acknowledgement under 1 second; explanation within 5 seconds.
- **cost:** Near-zero per stop; a few cents only if a model is used to explain a complex interrupted workflow.
- **security:** The local gesture must not depend on authentication or the network, and must never be overridden by a queued job. It can reveal that a job was running via LED/audio, so use a neutral local signal. Resume requires a fresh explicit confirmation bound to the saved checkpoint.
- **missing:** A firmware button-hold interrupt handler and persistent stopped latch; A relay cancel broadcast with idempotent cancellation tokens understood by Mac and browser workers; A unified interrupted-job receipt and safe-resume checkpoint

### "When something I asked you to do fails, don’t just say it failed: tell me the precise step and reason in one spoken sentence, preserve the evidence, and offer the safest alternate route—Mac, browser, or a draft—for one-tap approval to retry. Never blindly replay a partially completed action."
- **useful because:** Today a failed browser heartbeat, Mac job, or serial audio attempt leaves the owner guessing whether anything happened. A failure-aware handoff turns an opaque error into a recoverable decision while preventing duplicate sends or repeated destructive steps.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-terminal → dashboard
- **model tier:** Use deterministic receipts and error classes first; use a cheaper background model to translate unusual failures into a concise explanation and suggest alternatives. Realtime only reads the final sentence.
- **latency:** Surface the failure within 2 seconds of a receipt; generate an alternate plan within 8 seconds.
- **cost:** Usually under $0.02 per failure; model cost is limited to novel-error explanation, while receipts and retry safety are deterministic.
- **security:** Evidence may include private URLs or file paths, so redact secrets and restrict receipts to the owner. Retry tokens must be single-use and bound to the exact unfinished step; sending, deletion, and purchase still require confirmation.
- **missing:** A normalized error taxonomy spanning relay, Mac, browser, serial, and audio workers; Partial-progress checkpoints with explicit completed/unsafe-to-repeat steps; An alternate-route planner that can produce a draft instead of retrying an irreversible action

### "When I tap the pendant twice and say “focus here,” snapshot my current Mac windows and Safari tabs, ask what outcome I want, then switch to a minimal work set and silence nonessential audio/notifications for a chosen duration. When the timer ends—or I tap again—restore the exact prior workspace and give me a short completion note."
- **useful because:** The owner can enter and leave focused work from the device on their body without manually arranging windows, losing browser state, or remembering what they had open. The reversible snapshot makes the interruption boundary trustworthy and works across the Mac, authenticated browser, relay, and pendant rather than being just a Mac shortcut.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-terminal → dashboard
- **model tier:** Realtime handles the short spoken goal and confirmation; a cheaper model or deterministic rules select the work set from window/tab titles and restore metadata. No expensive model is needed for the timer or restoration.
- **latency:** Acknowledge the tap locally in under 200 ms; switch surfaces within 5 seconds; restore within 5 seconds of expiry.
- **cost:** Usually below $0.01 per session; API cost is limited to interpreting the optional spoken goal, with most work done by Mac/browser actions.
- **security:** Window titles and private tab URLs are sensitive. Keep the snapshot encrypted and local to the Mac, store only opaque identifiers in the relay, exclude password/payment tabs by default, and require confirmation before closing anything not safely restorable.
- **missing:** A transactional workspace snapshot/restore service spanning macOS windows and Safari tabs; A pendant double-tap gesture and timer state that survives a dropped link; A notification/audio policy adapter with a deterministic allowlist and rollback receipt

### "When my Mac or browser is unavailable, let me queue a request from the pendant with an expiry, a maximum scope, and a “draft only” or “may act” setting. When the right surface reconnects, carry out only the still-valid steps, tell me what changed since I spoke, and discard or re-confirm anything stale."
- **useful because:** The owner should not have to repeat a request merely because they walked away from the laptop or Safari bridge. This is more than an offline note: it preserves intent with explicit time and authority bounds, then revalidates the world before acting so an old command cannot unexpectedly send, buy, or modify something.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** The relay persists and schedules the intent deterministically; a cheaper background model re-plans only when reconnect-time state differs. Realtime is used solely for the initial spoken capture and the eventual concise receipt.
- **latency:** Local capture acknowledgement under 300 ms; reconnect detection within 10 seconds; stale-intent review within 15 seconds.
- **cost:** A few cents for a deferred request that needs replanning; storage and reconnect checks are negligible.
- **security:** Persist encrypted intent and least-privilege scope, never raw credentials or full page contents. Require fresh confirmation whenever recipients, prices, permissions, or source facts changed; enforce expiry even if a worker is delayed.
- **missing:** An encrypted intent envelope with expiry, authority scope, and revalidation predicates; A reconnect-triggered planner that can safely downgrade action to draft; A durable cross-surface queue with explicit owner-visible state transitions


## Changes it proposed to its own stack

### `firmware` — Replace the current fixed audio timing with an end-to-end clocked audio governor and acceptance harness: timestamp every 24 kHz decoded frame at the nRF9160, carry jitter/underrun markers over the USB-serial test link, have the ESP32 bridge adapt its 31,250→44,100 resampler phase instead of accumulating drift, and run a loopback sweep that measures gap rate, one-way latency, clipping, and intelligibility before a build is called shippable. Fail closed to a short local tone and a diagnostic receipt rather than silently emitting stretched or missing speech.
- **owner gets:** Spoken replies will stay natural and intelligible for long briefings instead of gradually drifting, clicking, or going silent—especially with the current 25 ms decode cost and SBC-only Bluetooth bridge. The owner gets a concrete pass/fail answer on whether the pendant audio is trustworthy, not an optimistic connection indicator.
- effort: Moderate-to-large: firmware timestamp/telemetry, ESP32 resampler control, relay metric propagation, and a USB fixture that exercises both physically connected chips.  ·  risk: Clock correction can create an audible tick or alter latency; gate changes behind a feature flag, keep the existing fixed resampler as fallback, and store a bounded diagnostic trace for reproduction.
- cost: No per-request API cost. Adds a small telemetry payload per audio session; development fixture and test headphones are the main cost (roughly $30–$100).  ·  latency: A governor adds under 10 ms buffering; avoiding accumulated drift reduces long-session effective latency and dropouts.
- security: Telemetry contains timing and error counts only, never PCM or transcript. The USB diagnostic endpoint must be local-only and authenticated.
- depends on: A serial diagnostic protocol between the Mac, nRF9160, and ESP32; An audio acceptance tool (the pending audio_pipeline_validate request); A typed audio-path preflight receipt and documented 24 kHz acceptance thresholds

### `hardware` — Add a low-power skin/proximity sensor and a hardware-gated audio path to the next pendant revision, with a simple worn/unworn state exposed to firmware. On removal, cut microphone bias and playback at the hardware gate before software notification; on wear, require a deliberate button gesture to re-enable capture. Include a small sealed test pad so the Mac fixture can verify the gate and sensor during manufacturing.
- **owner gets:** The pendant cannot accidentally keep listening or speak private material after it is taken off, placed on a desk, or handed to someone else. Privacy becomes a physical property that survives a crashed firmware task, lost relay link, or stale queued command—not merely a preference in software.
- effort: New pendant carrier schematic, sensor placement and enclosure validation, analog audio gating, firmware state machine, and privacy/false-trigger testing across clothing and pocket use.  ·  risk: False removal could interrupt a conversation; use hysteresis and a short grace period for movement, while the hardware mute remains immediate. Sensor failure should default to microphone/playback disabled and expose a clear LED fault pattern.
- cost: Approximately $1–$4 BOM increase for sensor, analog switch/gate, and passives; under 1 mA while worn-state sensing, with no relay/API cost.  ·  latency: Hardware mute is immediate; wear re-enable adds a deliberate gesture and roughly 100 ms debounce.
- security: Improves privacy by enforcing a physical mute independent of network and model state. Sensor state itself should not leave the device except as coarse diagnostic status.
- depends on: A production pendant carrier redesign beyond the current nRF9160 DK; A firmware local privacy state machine; A documented owner policy for wear detection and deliberate re-enable


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing advances: (1) a cross-surface “safety check this” gate that scans drafts for secrets, wrong recipients, stale facts, and irreversible consequences before approval; (2) a pendant-local “stop everything” kill switch that mutes audio and cancels/freeze Mac and browser work even during link degradation; and (3) failure-aware recovery that explains the exact failed step, preserves evidence, and offers a safe alternate route rather than blindly replaying. I also proposed an end-to-end audio clock governor and physical acceptance harness for the live nRF9160 + ESP32 prototype, so long 24 kHz sessions do not drift or silently drop speech.

What I still need is implementation, not another discovery round: the cross-surface evidence/redaction scanner; a firmware stop latch plus relay-wide idempotent cancellation and resume checkpoints; normalized partial-progress/error receipts; and the serial audio telemetry, ESP32 adaptive resampler, and acceptance fixture. The pending audio validation/threshold decisions remain the main product unknown. The connected chips are testable over USB today, but the pendant is still not LTE-registered, so network-independent stop and diagnostics must be exercised first.

**Biggest unknown:** Whether the current physical audio path can meet intelligibility and dropout thresholds under simultaneous Opus encode/decode and SBC Bluetooth load; no live acceptance measurement has established that yet.

