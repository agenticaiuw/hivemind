# Harness derivation — unified — round 20

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-stack-audio-and-bridge** — Mac agent v0.5.0 and relay v1.1.0 are reachable; relay reports durableAudio and pendantPipelineTelemetry, Mac bridge online. A live pipeline already renders 24 kHz mono PCM (160.8 KiB/3430 ms) and has offline-store alert/bookmark events, but browser extension is offline with 2 pending commands; Accessibility and Screen Recording are ungranted, so Mac agent ready=false.
  - evidence: GET /ops/status and GET /pipeline responses at 2026-08-07T09:17Z

## Capabilities it proposed

### "“Keep my voice conversation intact even if LTE drops, and tell me plainly if anything had to wait.”"
- **useful because:** The owner can speak naturally while moving through coverage gaps instead of losing a turn or guessing whether the pendant heard them. It uses the pendant's SD only as a failure buffer, honoring the existing no-routine-storage rule, then drains and reconciles packets when the link returns.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** gpt-5.6-luna for relay reconciliation and concise receipts; gpt-realtime-2.1 only for the live conversational path; no model for packet buffering or acknowledgements.
- **latency:** Normal path adds under 100 ms for packet acknowledgement. During an outage, local capture is immediate; replay begins within 2 seconds of link recovery. The owner hears one short status sentence only when continuity was affected.
- **cost:** Near-zero model cost in the normal path; roughly $0.001–$0.01 per recovered turn for reconciliation depending on transcript size. Dominant cost is LTE data and relay/R2 writes, not inference.
- **security:** Temporary Opus chunks and sequence metadata leave the pendant only after upload; failed chunks remain on removable SD until delivered or explicitly wiped. Encrypt the failure buffer with a device-held key, cap retention/size, and require no confirmation for automatic retry but confirmation before exposing recovered content in a new external action.
- **missing:** Firmware packet journal with authenticated monotonically increasing sequence numbers and bounded SD quota; Relay resumable upload endpoint with acknowledgements, deduplication, and ordered replay; Bridge/relay session state that distinguishes delayed audio from a new turn; A small dashboard view and spoken status event for buffered/replayed packets; End-to-end test harness that injects LTE loss during capture and playback

### "“If I missed what you said, repeat the last answer—or give me the short version—even when the connection has already dropped.”"
- **useful because:** A wearable conversation should remain recoverable in the moment. The owner can tap or say “repeat” while walking, in noise, or after a brief disconnection instead of losing the answer and restarting the whole request. This is distinct from buffering a new turn: it recovers the most recently delivered response locally and can provide a compact fallback when full replay is impractical.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** No model for exact local replay. Use gpt-5.6-luna only when a short cached text summary must be generated before delivery; use gpt-realtime-2.1 only if the owner asks a new conversational follow-up.
- **latency:** Exact replay starts within 150 ms of the button gesture. A cached short version starts within 500 ms when available. No network round trip is required for the common case.
- **cost:** Zero model cost for replay; occasional summarization is approximately $0.001–$0.01 per response and should happen once when the response is first generated, not on each replay. Storage and LTE costs are negligible because only one bounded response is retained.
- **security:** Retain only the latest response, encrypted, with an owner-configurable expiration and explicit wipe gesture. Do not retain microphone input for this feature. Dashboard should show whether a replayable response exists without exposing its text until requested.
- **missing:** Pendant-side last-response ring containing compressed audio plus a short encrypted text label or summary; Relay/mac-bridge delivery protocol that marks audio as fully delivered and supplies replay metadata before playback ends; Offline button/voice handling for repeat versus new conversation; A bounded cache policy covering interruption, reboot, and power loss; Acceptance tests for replay latency, privacy wipe, and partial-response behavior


## Changes it proposed to its own stack

### `firmware` — Add a bounded, encrypted Opus packet journal for uplink continuity: write packets to SD only after an upload timeout, attach session/sequence/codec metadata, checkpoint an ACK watermark from the relay, and resume in order with idempotent replay after reconnect. Keep live packets on the existing path and garbage-collect only acknowledged chunks.
- **owner gets:** A dropped LTE-M connection no longer silently deletes part of a conversation; the owner can continue speaking and receive the missing turn after coverage returns, with an honest delayed-status indication.
- effort: Medium-high: firmware journal/recovery state machine, relay resumable protocol, bridge tests, and fault-injection testing across power/link loss.  ·  risk: Power loss or corrupted FAT metadata could leave orphaned chunks; use append-only records, CRC/authentication, bounded quota, and a boot-time repair scan. If replay ordering is uncertain, surface a delayed/failed receipt rather than guessing.
- cost: No inference cost in steady state. Small additional LTE/R2 traffic for retries; SD wear is limited because writes occur only on failed uploads. Firmware uses RAM for one bounded packet plus journal metadata, not the whole recording.  ·  latency: No meaningful healthy-link latency change beyond ACK bookkeeping; recovery latency is governed by LTE attach and replay bandwidth.
- security: Encrypt and authenticate journal files; never put plaintext transcripts on SD. Delete acknowledged chunks and expose a user-visible wipe action.
- depends on: 24 kHz end-to-end audio path acceptance criteria; Relay resumable upload and deduplication contract; A tested SD mount/repair path

### `integration` — Add a cross-surface audio QoS governor. The pendant reports ring-buffer depth, decode/encode duration, modem attach/RSSI, and underruns; the relay combines these with upload RTT and the Mac bridge reports TTS chunk generation time. A bounded policy then selects Opus bitrate/frame size and response chunk pacing (while preserving the 24 kHz output contract), sends the mode in session metadata, and emits a quality-change event for the dashboard and a brief spoken notice only when intelligibility is materially affected.
- **owner gets:** The pendant remains understandable and responsive at the edge of LTE-M coverage instead of freezing, clipping, or unexpectedly falling behind. The owner knows whether a slow reply reflects network conditions rather than a missed command.
- effort: Medium: telemetry schema, relay policy, firmware controls, bridge chunk pacing, and automated network/CPU fault injection.  ·  risk: A bad controller could oscillate quality or add delay. Use hysteresis, minimum dwell times, hard bitrate/frame bounds, and a safe fixed-profile fallback; log every transition for diagnosis.
- cost: Negligible inference increase; a few bytes of telemetry per session and modestly more relay/D1 events. Lower bitrate during poor links can reduce LTE cost.  ·  latency: Healthy sessions unchanged. Under stress, it trades fidelity for bounded latency and targets fewer than 100 ms of additional buffering.
- security: Telemetry should contain no transcript or raw audio; treat RSSI/session IDs as operational data with short retention. Do not upload raw diagnostic audio unless explicitly enabled.
- depends on: 24 kHz superwideband acceptance criteria; A versioned audio-session metadata contract; Firmware access to codec bitrate/frame controls and ring-buffer counters; Relay and Mac bridge support for QoS events

### `firmware` — Implement a one-response local replay cache on the pendant: retain only the most recently acknowledged response as encrypted Opus frames plus a tiny authenticated header, expose a long-press repeat gesture that works without LTE, and invalidate it on timeout, explicit wipe, or replacement by the next completed response. The relay/Mac bridge must send a delivery watermark and optional short summary so the cache never treats an interrupted stream as complete.
- **owner gets:** The owner can recover a missed answer immediately from the wearable, even in a noisy place or dead zone, without repeating the request or waiting for the Mac and relay to reconnect.
- effort: Medium: firmware cache and gesture state machine, delivery-watermark protocol, bridge metadata, encrypted storage handling, and power-loss/privacy tests.  ·  risk: A partial or stale response could be replayed as if current. Require an authenticated completed watermark, announce “replaying the last answer,” and refuse when the cache is incomplete or expired. Long-press ambiguity with conversation-end must be resolved through distinct duration thresholds and haptic/LED feedback.
- cost: No inference cost for replay. A small encrypted cache consumes bounded flash/RAM or a tiny SD object; avoid routine audio retention beyond the single latest response.  ·  latency: Local replay begins in under 150 ms; no healthy conversation-path latency change.
- security: Encrypt the cache, avoid plaintext summaries on removable media, expire it by default, and provide a physical wipe gesture. The relay receives only cache status/watermark, not additional audio.
- depends on: A versioned response-delivery watermark shared by relay, Mac bridge, and pendant; A firmware gesture specification that distinguishes repeat from end-conversation; The 24 kHz playback path being stable enough to cache its encoded source frames


## What it asked for

_Nothing._
