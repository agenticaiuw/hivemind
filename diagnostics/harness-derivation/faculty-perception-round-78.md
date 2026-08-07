# Harness derivation — faculty-perception — round 78

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-device-presence** — As of 2026-08-07T13:06Z, the reachable device registry lists home-macbook-bridge online, home-chrome offline, and cloudflare-contract-test offline; no pendant is registered. Local /ops/status independently reports relay macBridgeOnline=true and browser online=false.
  - evidence: discover:devices plus GET /ops/status and GET /browser/status
- **mac-input-reachability** — The running AI Pendant Agent cannot currently post synthesized UI input or capture screen: accessibility.trusted=false, screenRecording.granted=false, inputReachability.status=failed, and uiActionsWillReachTheScreen=false. AppleScript automation grants are present, but the Mac agent is not ready for trusted UI control.
  - evidence: GET /observe at 2026-08-07T13:06:38Z and GET /ops/status
- **telemetry-time-boundary** — The pipeline contains completed historical 24 kHz TTS and nRF9160-sourced events, but these are persisted records, not proof of a currently connected pendant. One recent nRF9160 run remains status=processing despite no pendant in the live device table.
  - evidence: GET /pipeline plus discover:devices
- **browser-observability** — Browser bridge is presently offline with 7 pending commands and three durable sessions visible in /observe, including time.is/UTC and two form pages. No current tab/window is available through the extension.
  - evidence: GET /browser/status and GET /observe

## Capabilities it proposed

### "Can you reach my pendant right now, and which parts of what you’re showing me are live versus stale?"
- **useful because:** Today the system can report persisted nRF9160 audio and alert events even though no pendant is registered, and can report Mac/browser status separately. A single answer needs to fuse relay device presence, Mac bridge reachability, browser reachability, and pipeline timestamps, explicitly refusing to present historical telemetry as current. This prevents the owner trusting a queued or old alert as delivered.
- **path:** relay → mac-planner → browser-extension → unified
- **model tier:** deterministic; no model call needed
- **latency:** under 2 seconds for parallel status reads
- **cost:** negligible API cost; four authenticated GETs and a small structured response dominate
- **security:** Read-only metadata only: device IDs, online/last-seen times, pipeline event timestamps, and bridge state. Do not expose audio contents or secrets. Mark last-seen as uncertainty rather than claiming a lease; use connection epoch/ACK only once the relay adds those semantics.
- **missing:** Relay-owned connectionEpoch, reconnect watermark, and durable event ACK semantics (currently last-seen only); A shared clock/monotonic timestamp normalization between relay and Mac pipeline; A first-class status schema that labels each fact live, recently observed, queued, or historical

### "Why didn’t that last answer reach me? Walk me through the exact chain from my button press to audio playing, and identify the first missing handoff."
- **useful because:** The owner cannot currently distinguish a failed capture, a relay upload, Mac planning, TTS rendering, relay acceptance, pendant download, or speaker playback. A causal, event-by-event postmortem would turn mysterious silence into an actionable answer and would expose replayed/test telemetry instead of treating it as delivery.
- **path:** pendant → relay → mac-planner → unified
- **model tier:** background deterministic correlation first; use a cheap summarizer only to turn the structured trace into one short spoken sentence
- **latency:** under 5 seconds for a recent trace; up to 30 seconds for a day-wide search
- **cost:** Low: indexed event joins dominate; approximately one small background-model call only when a spoken explanation is requested
- **security:** The trace can contain transcript text and timing patterns. Default to event labels, IDs, byte counts, and statuses; reveal transcript/audio only on explicit request. Require confirmation before exporting a trace off-device. Preserve immutable source timestamps so a late ACK cannot rewrite history.
- **missing:** A durable cross-surface correlation ID spanning button/input, relay job, Mac pipeline, TTS object, pendant download, and speaker playback; Relay journal entries for download and playback ACKs, including reconnect epoch and duplicate/replay markers; An indexed trace query with a defined terminal state and first-failure rule


## Changes it proposed to its own stack

### `integration` — Add a read-only evidence-normalization endpoint that joins relay device presence, Mac bridge /ops/status, /observe input reachability, browser status, and pipeline events into per-fact records: {value, observedAt, source, freshness, confidence, deliveryState}. It must reject the inference 'pipeline event exists => pendant is connected' and label nRF9160 records as historical/undeliverable when no pendant lease is present. Keep the raw source timestamps and emit a clock-skew warning when they cannot be compared.
- **owner gets:** When the owner asks whether something actually reached the wearable, they get an honest answer with the reason and age of each fact instead of a confident blend of stale telemetry and live Mac state.
- effort: Medium: define schema, implement parallel reads and freshness policy, add fixtures for no-pendant and reconnect races, and expose it to the unified voice path.  ·  risk: A bad freshness threshold could hide a valid delayed delivery or falsely call a device stale. Recover by preserving raw evidence, showing the threshold used, and allowing a later receipt/ACK to upgrade the state; this remains read-only and cannot block actions.
- cost: Negligible per-query API cost; modest storage for normalized snapshots and raw source references.  ·  latency: Adds roughly one parallel network round-trip, target under 2 seconds; no LLM latency.
- security: Metadata only, but device IDs and event timing are sensitive. Enforce bearer auth, redact audio/text payloads by default, and never project captured secrets into the evidence record.
- depends on: Relay connectionEpoch/reconnect watermark and durable event ACK semantics; A documented clock/freshness policy shared by relay and Mac agent


## What it asked for

_Nothing._
## Its own summary

Fresh observation completed. Live state is: Mac bridge online; no pendant registered; browser extension offline with 7 pending commands; Mac Agent UI input and screen capture are not reachable (Accessibility and Screen Recording false); pipeline contains persisted 24 kHz/nRF9160 records, including one processing run, but those records are not current-device proof. I recorded these facts and proposed an evidence-normalization layer plus a deterministic owner-facing reachability report that distinguishes live, queued, stale, and historical evidence. What I still need is not another model permission: (1) an actually registered pendant to verify the end-to-end 24 kHz path, (2) relay connection epoch/reconnect watermark and durable event ACK semantics, and (3) owner-granted Accessibility/Screen Recording if trusted UI control must be verified. Until (1), 24 kHz claims remain source/history observations rather than live hardware verification.

**Biggest unknown:** Whether the persisted nRF9160 'processing' event represents a real device that disconnected, a replay/test artifact, or a relay record awaiting acknowledgement; the current live registry cannot distinguish those without a relay lease/ACK journal.

