# Harness derivation — relay-realtime — round 27

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Keep the conversation usable even when LTE is congested—let me interrupt, and don’t lose what I said while you’re speaking.”"
- **useful because:** The owner currently experiences a ~7.8-second uplink collapse and hundreds of dropped packets when downlink speech overlaps speech. A congestion-aware session would make the pendant feel conversational rather than requiring the owner to wait for audio to finish or repeat themselves. It is genuinely cross-node: the pendant measures capture/queue health, the relay chooses transport behavior in real time, and the Mac/ESP32 bridge reports playback occupancy and can pause/resume the SBC stream without destroying the turn.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Use relay-realtime only for the live turn and transport decisions; no additional model call is needed. If a turn is irrecoverably damaged, a cheap background repair/transcription pass can reconstruct the partial utterance rather than spending the realtime tier again.
- **latency:** Congestion detection and mode changes under 150 ms; interruption acknowledgment under 300 ms. Preserve no more than 250 ms of speech before and after a mode switch. A resumed answer may begin within 1 second after the owner stops speaking.
- **cost:** Negligible model cost beyond the existing realtime session. Storage/telemetry is small; bandwidth may decrease because degraded mode uses lower bitrate and sends short control frames instead of repeatedly retransmitting audio.
- **security:** Audio and loss telemetry remain within the existing relay session and bridge link; do not upload raw replay buffers unless needed for the current turn. The dashboard should expose mode changes and dropped-frame counts, and automatically expire any repair buffer after the turn. Playback pause/resume and codec changes must be authenticated to the paired pendant/bridge so a spoofed control packet cannot inject audio.
- **missing:** A negotiated session-state protocol carrying packet-loss rate, uplink queue depth, playback occupancy, and explicit half-duplex/degraded/normal modes; Pendant firmware support for a small rolling pre-encode PCM/Opus window, sequence numbers, VAD boundaries, and local backpressure signaling (not a user-facing offline note feature); Relay jitter buffer and turn assembler that can splice an interrupted utterance, issue a brief local/relay acknowledgment, and resume TTS from a checkpoint; ESP32/SBC bridge controls for pause, drain, and resume plus a report of actual playback occupancy; current SBC-only path otherwise hides congestion; A deterministic acceptance harness that injects LTE contention and verifies no more than 250 ms of owner speech is lost and that an interrupted response resumes exactly once

### "“When I walk back to my Mac, hand off the thing I asked you to do on the pendant, finish it in the right browser/app, and tell me on the pendant exactly what happened.”"
- **useful because:** Today a worn-device request cannot reliably bridge the moment when the owner is away to the moment an authenticated Mac/browser becomes available. This would turn a spoken intent into a durable, owner-visible handoff rather than losing it in a disconnected extension or forcing the owner to repeat themselves. It depends on the pendant, always-awake relay, Mac planner, and browser sessions together.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Relay-realtime only captures and acknowledges the initial intent. A cheaper background planner handles the queued goal and browser/Mac execution; realtime is used again only to deliver a concise completion or failure summary when the owner is reachable.
- **latency:** Immediate spoken acknowledgment in under 500 ms. Handoff detection under 5 seconds after the Mac bridge/browser session becomes available. Completion notification should arrive within 2 seconds of the downstream receipt; never claim success before a signed result receipt is returned.
- **cost:** One short realtime turn for capture and one for the final spoken summary; planning/execution uses the cheaper Mac tier. Durable metadata is a few KB per handoff, with no need to retain raw audio after transcription.
- **security:** The relay must bind a handoff to the paired pendant and a specific Mac/browser session, show the target app/domain and action summary in the dashboard, and encrypt queued intent/result data. Authenticated browser cookies stay in the browser harness; the relay receives only the minimum structured goal and result. If the owner cancels from the pendant, the queued job must stop before the next mutating action.
- **missing:** A durable handoff object with lifecycle states captured, waiting-for-surface, executing, blocked, completed, and canceled; Presence/availability signals from Mac bridge and browser extension with freshness and identity, not merely a boolean online flag; A relay-to-Mac/browser claim protocol preventing duplicate execution when both reconnect or two workers race; Signed, human-readable result receipts that can be summarized over voice and correlated to the original spoken request; A one-button pendant cancel/retry interaction and a dashboard timeline showing queued handoffs without exposing browser credentials

### "“If the answer comes from my private Mac or browser, don’t read sensitive details aloud when other people may be nearby—give me a discreet cue and let me unlock the full answer with the pendant.”"
- **useful because:** The pendant is worn away from the Mac and its speaker is inherently public. Today a successful browser/Mac retrieval can accidentally turn private mail, work, or account information into an audible disclosure. A privacy-aware delivery mode would let the owner use the hive in public without giving up authenticated Mac/browser access.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic relay policy for classification and short cues; use no extra model for ambient-level estimation. Mac/browser agents attach sensitivity labels and a concise safe summary. Realtime speaks only the safe cue; a full response is generated/spoken after the owner’s explicit button gesture or a private audio route is verified.
- **latency:** Safe cue under 500 ms after a result receipt. Ambient/privacy state should update within 1 second and never block ordinary low-sensitivity answers. Unlock gesture must be recognized within 300 ms, with a 10-second expiry.
- **cost:** No additional model call for policy; a small amount of metadata travels with each result. Optional private full-answer playback through the existing bridge has normal audio cost only.
- **security:** Sensitivity labels must be fail-closed when absent or contradictory, and the relay must never infer that a browser result is safe merely because the request was spoken. The full answer should require a deliberate button gesture, expire quickly, and be auditable in the dashboard without storing the secret text. Ambient detection should retain only a boolean/short-lived confidence, not recordings.
- **missing:** A result-envelope schema carrying source, sensitivity, safe-summary, and disclosure policy from Mac planner/browser harness to relay; Pendant firmware support for a distinct long-press/double-click unlock and LED acknowledgment, with replay-resistant sequence numbers; A local ambient speech/noise privacy estimator and a configurable owner policy (always discreet, adaptive, or unrestricted); A private playback capability or authenticated bridge route that can be proven to be the owner’s listening device; End-to-end tests proving sensitive browser/Mac content is never emitted on the public speaker without the unlock gesture


## Changes it proposed to its own stack

### `interaction` — Add a relay-visible, read-only telemetry endpoint and typed status schema for live audio path health (uplink packet loss, LTE contention, half-duplex state, codec/sample-rate currently negotiated, buffer depth, and whether mac bridge/browser extension are online). Include last-updated timestamps and a minimal rolling window for trend. Provide a matching tool in the relay to fetch it.
- **owner gets:** When speech starts breaking up or responses are delayed, the pendant can tell the owner what’s happening (“your network is congested; I’m switching to a safer mode”) instead of guessing or failing silently.
- effort: Medium: define a schema, implement read-only aggregation on the relay, wire metrics from modem/bridge where available, and expose a tool.  ·  risk: Low. Biggest risk is exposing sensitive diagnostics; mitigate by returning only coarse metrics and avoiding user-identifying data. If metrics are missing, return nulls rather than blocking.
- cost: Low per call. A small JSON payload; dominated by whatever upstream collection already costs.  ·  latency: Small improvement. Faster, clearer failure modes; avoids expensive retries.
- security: Diagnostics could reveal environment details; restrict to authenticated relay and avoid precise location or network identifiers.
- depends on: A metrics collection hook on the pendant/bridge to publish uplink loss and contention signals (or a firmware shim that emits them).

### `hardware` — Add a low-power audio front end between the pendant microphone/speaker path and the nRF9160: an external I2S/PCM codec with DMA-backed ring buffers and hardware sample-rate conversion, plus a small control channel for congestion/occupancy telemetry. Keep LTE and application logic on the nRF9160, but move continuous capture/playback buffering and resampling out of the 87%-busy application core. Expose independent capture and playback queues so the relay can interrupt or resume speech without corrupting the shared full-duplex stream.
- **owner gets:** The owner gets substantially more reliable natural conversation and true 24 kHz playback while speaking over an answer, instead of clipped words, long pauses, or repeated requests. It also makes the pendant less sensitive to the current single-I2S/CPU contention and gives the adaptive transport a truthful measure of audio that is actually heard.
- effort: Board respin, codec selection, power and EMC validation, nRF9160 driver/firmware work, bridge protocol updates, and end-to-end contention testing. Moderate-to-high hardware effort; prototype first on an external codec breakout before committing to a PCB.  ·  risk: Added component or clocking faults could introduce noise, latency, or battery drain; a failed codec must fall back to the existing direct I2S path. Require a boot-time self-test, watchdog bypass, and firmware feature flag so the current audio path remains recoverable.
- cost: Roughly $3–$10 per unit for codec, clocking, passives, and PCB changes; likely tens of milliwatts additional draw depending on codec. No meaningful per-call API cost; reduced retransmission and fewer repeat turns may lower total model usage.  ·  latency: Adds an estimated 5–20 ms buffering latency, but removes multi-second stalls caused by contention and CPU starvation. Tune ring-buffer depth dynamically rather than adding a fixed large delay.
- security: No new cloud data path. Codec telemetry is non-content metadata; ensure debug captures are disabled by default and firmware updates are signed.
- depends on: Define the negotiated audio/congestion session-state protocol; Add relay/bridge playback occupancy and pause/resume controls; Validate codec clocking against the existing 15.625 kHz capture and 24 kHz decode requirements


## What it asked for

_Nothing._
## Its own summary

Recorded three new proposals: congestion-resilient interruptible conversation across pendant/relay/bridge; durable away-from-Mac handoff with authenticated completion; and privacy-aware disclosure of Mac/browser results. Also recorded a hardware change adding an external audio front end to relieve nRF9160/I2S contention, plus a discreet-result capability that requires a pendant unlock gesture and sensitivity metadata. The remaining needs are implementation contracts: audio session telemetry/control, durable handoff claims and receipts, sensitivity-labeled result envelopes, and firmware/bridge support for gestures and playback occupancy.

**Biggest unknown:** Whether the pendant enclosure and power budget can accommodate an external codec/audio front end and whether the existing bridge has a controllable private playback route; these require hardware and bridge-owner validation rather than further relay discovery.

