# Harness derivation — unified — round 80

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Keep my pendant conversation usable while I move through bad LTE coverage: automatically use the nearby Mac/phone path when it is better, return to LTE when it recovers, and tell me only if privacy or continuity is at risk."
- **useful because:** The current 16 kbps uplink plus 24 kbps downlink already drops speech under simultaneous talk. A worn device that silently loses 7–8 seconds of speech is not dependable. Combining the pendant's local radio, the nearby Mac/phone, and the always-awake relay can preserve a conversation instead of merely reporting failure.
- **path:** pendant → mac-planner → relay-realtime → browser-extension → unified
- **model tier:** Realtime model only for the live conversation and path handoff decision; a cheap background model can summarize link incidents after the call.
- **latency:** Detect degradation within 300 ms, switch at a packet boundary within 1 s, and avoid more than 500 ms of duplicated or missing audio. No spoken announcement during ordinary handoff; announce a short warning only when the fallback is unavailable or privacy policy requires it.
- **cost:** Negligible model cost during calls (telemetry-driven state machine, not an LLM); roughly $0.01–$0.05 per incident for optional post-call diagnosis, dominated by transcription/summary. Hardware retrofit is separate.
- **security:** A fallback can expose microphone/audio through the Mac or phone and may cross a private browser session. Require an explicit owner-selected fallback device and a local privacy latch; never use an unpaired host, and require confirmation before enabling a new host. Relay should exchange only encrypted media and short-lived path tokens.
- **missing:** A bidirectional local audio transport (the current ESP32 is SBC A2DP source-only) or a phone companion that can carry microphone return audio; Firmware path-quality telemetry and a relay handoff protocol with sequence-numbered, deduplicated frames; A concrete owner-approved phone/Mac fallback and privacy boundary; End-to-end audio acceptance thresholds and fault-injection tests


## Changes it proposed to its own stack

### `hardware` — Replace the current ESP32 A2DP-source-only bridge with a bidirectional local audio bridge: BLE LE Audio/ISO or USB Audio Class to the Mac/phone, with an encrypted control channel for path selection, sequence numbers, jitter buffering, and a hardware privacy indicator. Keep the existing SBC A2DP output as compatibility mode, but add a microphone return path and a way for the relay to select LTE-M versus local transport.
- **owner gets:** When LTE-M is congested, the pendant can continue a natural conversation through a trusted nearby device instead of dropping speech. The owner gets continuity while retaining a visible, local indication of which device is carrying their voice.
- effort: High: new bridge hardware and enclosure/power design, firmware on both bridge and pendant, relay media-router changes, Mac/phone companion, and RF/audio certification. Prototype first with USB Audio Class on the Mac before committing to LE Audio silicon.  ·  risk: New radio/audio firmware can introduce latency, pairing failures, or accidental audio routing. Recover by retaining LTE-M-only fallback, requiring explicit pairing and a physical privacy latch, and logging every path transition. Do not ship automatic fallback until packet-loss, echo, and reconnect tests pass.
- cost: Prototype: roughly $15–$40 in bridge components plus enclosure work; production BOM likely +$5–$15 depending on LE Audio/USB controller. Power draw rises during local radio use by approximately 20–80 mA at 3.3 V; API cost is negligible.  ·  latency: A local path should add 20–80 ms one-way; handoff target under 1 s. Existing LTE path remains unchanged when healthy.
- security: Adds another paired endpoint and attack surface. Use per-device keys, encrypted media/control, host allowlisting, explicit pairing gesture, and a hardware mute/privacy state that overrides software.
- depends on: Owner-approved Mac/phone fallback and privacy boundary; Bidirectional audio transport implementation; Relay handoff protocol with sequence-numbered frames; End-to-end audio acceptance thresholds and fault injection

### `integration` — Add an end-to-end pipeline reconciler that derives job state from signed stage events across relay, Mac bridge, and pendant. It must mark a run terminal only after the relay-result receipt is acknowledged by the pendant (or explicitly expired), detect contradictory states such as 'Realtime plan ready' followed by a job still marked processing, and emit one concise owner-facing completion/failure receipt with the last durable event and retry/undo affordance.
- **owner gets:** The owner should not have to guess whether a spoken answer, queued alert, or Mac action actually arrived. It turns late delivery and half-completed audio jobs into a trustworthy answer—especially when the pendant reconnects after an outage.
- effort: Medium: shared event schema, idempotent reducer, durable acknowledgements, watchdog, and dashboard/voice receipt formatting; add replay tests using existing /pipeline history.  ·  risk: A bad reducer could prematurely call work complete or duplicate receipts. Use monotonic sequence numbers, event signatures, idempotency keys, explicit unknown/expired state, and replay against historical runs before enabling automatic closure.
- cost: Low API cost; storage is a few hundred bytes per stage event plus retention sweeper. Background reconciliation can run on the cheap tier or as a Worker cron.  ·  latency: No added hot-path audio latency; receipt may be delayed up to one reconnect/ack timeout. Contradiction detection target under 5 seconds.
- security: Receipts may reveal private command text or browser results. Encrypt durable event payloads, minimize spoken summaries, and apply existing sensitivity/retention policy.
- depends on: Durable event IDs and stage sequence numbers at relay, Mac bridge, and pendant; A pendant delivery acknowledgement for response audio and held alerts; Existing job receipts/undo storage; A defined timeout policy for offline pendant and browser devices

### `firmware` — Introduce a timestamped, end-to-end audio clock contract instead of treating each resampler as an independent rate converter. The pendant must stamp capture frames from its actual 15,625 Hz clock; relay transcoding must preserve media time; and playback must use a bounded drift controller against the 31,250 Hz I2S clock, with concealment for missing frames and explicit discontinuity markers on reconnect. Expose accumulated drift, concealment count, and playout underrun in the existing pipeline events so a call can be diagnosed rather than merely sounding degraded.
- **owner gets:** They should be able to wear the pendant for a long conversation without voices slowly slipping out of sync, periodic clicks, stretched speech, or silence after a brief LTE loss. Today the capture, Opus, and playback clocks are different, and the owner has no trustworthy indication when the audio path is accumulating error.
- effort: Medium-high: firmware timestamping and jitter buffer changes, relay metadata preservation, a fixed-point drift controller, and hardware-in-loop soak tests with simultaneous speech and packet loss. This is a new audio correctness layer, not a UI trim of the current prototype.  ·  risk: An unstable controller could create audible pitch or timing modulation, and incorrect timestamps could worsen recovery. Gate it behind telemetry, use conservative ppm limits, retain the current path as a rollback mode, and validate with long-duration loopback and injected loss before enabling by default.
- cost: No per-call model cost. Firmware flash/RAM impact should stay small (roughly 8–16 kB flash and 4–12 kB RAM for metadata, jitter, and diagnostics); test hardware and audio measurement are the main cost.  ·  latency: Adds roughly one bounded jitter-buffer frame (60–120 ms) when needed; healthy-link latency can remain near current behavior. Recovery should avoid replaying stale audio.
- security: Audio timestamps and diagnostics can reveal call timing but not content; encrypt them with the existing media channel, redact payloads from logs, and enforce short retention for diagnostics.
- depends on: A versioned media-frame metadata schema shared by pendant, relay, and playback bridge; End-to-end audio acceptance thresholds; Audio link fault-injection and long-duration clock-drift tests; A durable receipt for reconnect/discontinuity events


## What it asked for

_Nothing._
## Its own summary

Discovered that the Mac bridge is online, but the browser extension is offline with 7 pending commands. The live pipeline already renders 24 kHz mono PCM successfully (74 KiB/1.58 s in a recent run), while a realtime audio job remains marked processing after a ready event—evidence for the pipeline reconciler proposal. I recorded two new items: a cross-surface conversation-continuity capability that fails over between LTE-M and a trusted nearby Mac/phone, and the hardware/integration needed for a bidirectional local audio bridge and receipt reconciliation.

**Biggest unknown:** The owner's approved Mac/phone fallback and privacy boundary, plus the end-to-end audio acceptance thresholds and fault-injection results. Those determine whether automatic local failover is safe; the current ESP32 bridge is A2DP-source-only and cannot carry microphone audio back.

