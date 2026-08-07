# Harness derivation — faculty-perception — round 124

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **device-registry** — Live device discovery currently shows Safari on MacIntel and home-macbook-bridge ONLINE; cloudflare-contract-test mobile OFFLINE. No nRF9160 pendant or ESP32 bridge is registered in the relay device table, so wearable delivery cannot be verified through the relay yet.
  - evidence: discover(devices) at Round 124 returned exactly three items and no pendant/ESP32.
- **audio-path-observation** — The Mac bridge has completed a 24,000 Hz mono s16le TTS render (75,734 PCM bytes, 1,578 ms audio, zero clipped samples) and relay accepted it as waiting for the nRF9160; this verifies render/upload metadata, not physical playback.
  - evidence: GET /pipeline returned job_309f5663... TTS done with sampleRate 24000, pcmBytes 75734, clippedSamples 0, followed by relay_result done.
- **device-status-route** — The Mac local agent still has no GET /v1/devices/status route; attempting it returns 404. Device presence can currently be observed only through the devices discovery projection, not a live authenticated status API.
  - evidence: probe_http GET /v1/devices/status Round 124 returned HTTP 404 No such route.

## Capabilities it proposed

### "“What actually happened while I was away?” Give me a short, cited timeline of completed, blocked, queued, and stale work across my Mac, browser, relay, and wearable, and say what still needs me."
- **useful because:** Today the system can show a completed Mac plan, a relay object waiting for a nonexistent pendant, stale browser-watch reports, and scheduled jobs—but there is no single truthful account that distinguishes those states. This is the highest-value perception capability: it prevents the owner acting on work that only appeared to complete.
- **path:** relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → unified
- **model tier:** Use a cheap background model to summarize an evidence graph; use realtime only when the owner asks live. Perception should deterministically classify status from timestamps and receipts before any model wording.
- **latency:** Under 5 seconds for an on-demand timeline; under 30 seconds for a full cross-surface scan. Most work is parallel reads, not model time.
- **cost:** About $0.01–$0.04 per on-demand summary; dominated by one background-model synthesis, with route reads negligible.
- **security:** Private browser titles/content and job receipts leave the Mac only as already authenticated route results. Redact secrets and page bodies by default; include URLs and short source excerpts only with owner permission. Never infer physical playback from relay acceptance.
- **missing:** A normalized event envelope joining pipeline events, Mac job receipts, browser inspection/watch reports, and device-registration observations; A deterministic status taxonomy (observed-complete, accepted-not-delivered, blocked, stale, failed) with freshness thresholds; Citations in the spoken answer that map each claim to route, timestamp, and surface

### "“Tell me when the system disagrees with itself.” Detect contradictions such as a Mac job marked complete while its approval event is waiting, a relay response accepted while no wearable is registered, or a browser heartbeat that has gone stale, then present the smallest evidence bundle for my decision."
- **useful because:** The owner currently receives plausible success language from individual surfaces that can be mutually false. A perception-level contradiction alert catches unsafe handoffs before judgement or action trusts them, without requiring the owner to inspect dashboards.
- **path:** faculty-perception → relay-realtime → mac-planner → browser-extension → unified → faculty-judgement
- **model tier:** Run deterministic rules and timestamp checks continuously or on each event; use a cheap background model only to name the conflict in one sentence. Realtime is unnecessary unless the owner is actively asking.
- **latency:** Rules should fire within 1 second of an event; spoken explanation under 3 seconds on demand.
- **cost:** Near-zero for rule evaluation; under $0.005 for occasional short explanation. Storage is a bounded event index, not audio or page bodies.
- **security:** Do not expose private page content in alerts; report only source surface, identifiers, state, and timestamps. Contradiction alerts must be advisory and never auto-send, delete, purchase, or replay commands.
- **missing:** A monotonic cross-surface event stream with clock-skew correction; Explicit state-transition contracts for pipeline, job receipts, browser heartbeats, and device delivery; A durable acknowledgement record so the same contradiction is not spoken repeatedly

### "“Run an end-to-end hearing check.” Send a known spoken test through the actual Mac-to-relay-to-pendant-to-ESP32 path, verify each hop and the 24 kHz/31.25 kHz/44.1 kHz format boundaries, then tell me exactly where it stopped—without storing the recording."
- **useful because:** A successful TTS render and relay upload currently look like success even when no pendant is registered. A one-button, disposable fixture would establish whether the owner can actually hear the response and localize failures to render, upload, modem, nRF decode, I2S, ESP32 resampling, or Bluetooth.
- **path:** mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action → unified
- **model tier:** No expensive model needed: a deterministic audio fixture and telemetry collector should do the work. Use realtime only to announce the concise result.
- **latency:** 30–60 seconds including reconnect/handshake; stop after 2 minutes and report the first missing hop.
- **cost:** Under $0.01 per test; dominated by transient audio transfer. Generate the fixture locally and delete it immediately.
- **security:** Use synthetic text, never microphone capture. Do not retain PCM or Bluetooth payload. Require explicit confirmation before any test that could interrupt an active call; otherwise it is reversible and read-only.
- **missing:** A test-run protocol with nonce carried through Mac render, relay object, nRF firmware, I2S bridge, and optional headphone acknowledgment; Per-hop telemetry including queue time, packet loss, decode underruns, resampler lock, and Bluetooth connection state; A disposable-audio retention policy and a final signed receipt that distinguishes ‘played’ from merely ‘queued’

### "“Set up this pendant for me.” Put the physically connected nRF9160 and ESP32 into a named owner device, verify firmware identity and clock, enroll it with the relay, run a synthetic audio handshake, and refuse to call it ready until the owner-facing receipt proves which hops passed."
- **useful because:** Today a board can be physically present yet absent from the relay, while old pipeline records make delivery look successful. The owner needs a single commissioning action that turns hardware on the desk into a trustworthy wearable—or names the exact failed boundary.
- **path:** mac-terminal → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action → unified
- **model tier:** Deterministic firmware/serial and relay checks; a cheap model may turn raw diagnostics into one short explanation. Realtime is only for the final spoken receipt.
- **latency:** Up to 3 minutes, including modem registration and a bounded retry window; never wait indefinitely.
- **cost:** Under $0.02 per commissioning attempt, dominated by transient relay traffic; no audio retention.
- **security:** Enrollment is security-sensitive: require a physical button press or USB confirmation and display the device fingerprint before binding it. Never upload raw UART, SIM identifiers, or microphone data. A failed attempt must revoke any partial enrollment.
- **missing:** Authenticated device-enrollment and revocation endpoints; A nonce-based serial handshake implemented by both firmware images; A commissioning receipt schema that distinguishes identity, registration, transport, decode, and playback evidence; A physical confirmation primitive beyond the current single conversation button, or an explicit USB-only enrollment mode

### "“Tune the pendant for my ears.” Play a short set of synthetic calibration tones through the actual ESP32/Bluetooth path, measure clipping, latency, dropouts, and perceived volume with my confirmation, then store a per-headphone playback profile that keeps speech intelligible without touching microphone recordings."
- **useful because:** The current path performs several sample-rate conversions and has a known tight RAM/Bluetooth budget, but the owner has no way to know whether a particular headphone pair is too quiet, clipped, delayed, or intermittently starved. A personal calibration makes everyday speech usable rather than merely technically delivered.
- **path:** mac-terminal → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action → unified
- **model tier:** Deterministic signal analysis and firmware counters; no expensive model required. Use realtime only to guide the owner through the brief confirmation prompts.
- **latency:** 90 seconds per headphone pair, with a 10-second repeat check after reconnect.
- **cost:** Under $0.01 per calibration and no ongoing inference cost; store only a small profile.
- **security:** Synthetic tones only; never retain microphone or headphone audio. Require confirmation before changing volume. Keep profiles keyed to a local device fingerprint and permit one-command reset.
- **missing:** A calibration mode spanning nRF9160 decode, 31.25 kHz I2S, ESP32 44.1 kHz resampling, and A2DP output; Per-hop counters for underruns, packet loss, clipping, and end-to-end latency; A safe volume ramp and local profile store keyed by headphone identity; A user confirmation signal that is available while the pendant is playing

### "“What of mine is stored right now, and who can reach it?” Give me a live, plain-language inventory across pendant SD, Mac workspace, relay D1/R2, browser sessions, and generated audio: contents, retention, access surface, last access, and one-tap revoke/delete controls for each category."
- **useful because:** The owner currently has audio retention, browser sessions, memory, captures, scheduled jobs, and local files spread across surfaces, but no trustworthy answer about their combined privacy state. This lets them use the system every day without guessing where a private conversation or credential-bearing page ended up.
- **path:** relay-realtime → mac-planner → browser-extension → mac-terminal → faculty-perception → faculty-judgement → faculty-action → unified
- **model tier:** Inventory and retention calculations should be deterministic. Use a cheap model only to compress the result into the owner's preferred one-sentence spoken summary; realtime is not needed for the scan.
- **latency:** Under 10 seconds for the summary; deletion/revocation receipts may take up to 30 seconds and must remain observable.
- **cost:** Under $0.01 per inventory; storage cost is dominated by existing audio/page artifacts, not this feature.
- **security:** The inventory itself is sensitive and must be shown only to the authenticated owner. Never include secret values such as captured credentials. Deletion must be explicit, scoped, irreversible only after confirmation, and produce a receipt; revoking browser access must not silently destroy unrelated sessions.
- **missing:** A unified data-asset catalog spanning local files, D1/R2 objects, browser session state, memory, captures, and pendant SD; Per-asset provenance, retention deadline, access log, and sensitivity classification; Scoped revoke/delete APIs with verified completion receipts; A dashboard and spoken rendering that reveal metadata without revealing secret contents


## Changes it proposed to its own stack

### `mac-harness` — Add a USB serial hardware-observer daemon that opens the known nRF9160 and ESP32 serial candidates, fingerprints each board, captures boot/version/registration lines, and publishes a signed short-lived observation to the Mac bridge and relay. Correlate that observation with the relay device registry so “physically connected over USB,” “firmware alive,” “LTE registered,” and “relay delivery acknowledged” are four separate states. Include a one-shot diagnostic command and a dashboard card; do not upload raw UART continuously.
- **owner gets:** The owner can wear or test the hardware today, yet the relay currently reports no pendant and cannot distinguish unplugged, boot-looping, modem-unregistered, or merely unpaired. This gives an immediate truthful answer and makes every future audio claim testable without pretending relay history is live hardware.
- effort: Medium: Node serial watcher, firmware line parser for both existing logs, signed observation endpoint, dashboard state card, and reconnect tests. No firmware change is required for the first version if existing boot/telemetry lines are sufficient.  ·  risk: Serial ports can be busy or firmware output can be malformed; use read-only exclusive-open with backoff, never reset or flash. If parsing confidence is low, publish unknown rather than infer. Recover by closing ports on disconnect and expiring observations after 30 seconds.
- cost: Negligible API cost and one small local process. No cloud storage beyond the latest compact observation; raw UART remains local unless the owner explicitly requests a diagnostic bundle.  ·  latency: USB presence within 1–2 seconds; firmware/registration state within one log heartbeat. No impact on realtime voice path.
- security: UART may contain identifiers or network diagnostics. Keep raw lines on the Mac, publish only hashed device ID, state, firmware version, and timestamps over bearer-authenticated routes; never include credentials or audio.
- depends on: The Mac bridge must be allowed to open /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A compact authenticated observation route and dashboard renderer; A parser fixture suite built from firmware/nrf9160 and firmware/esp32-airpods-bridge logs


## What it asked for

_Nothing._
