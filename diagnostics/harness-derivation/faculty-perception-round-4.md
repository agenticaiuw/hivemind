# Harness derivation — faculty-perception — round 4

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent-readiness** — As of 2026-08-07T09:14Z, Mac local agent v0.5.0 is healthy and online, but Accessibility is not trusted, Screen Recording is missing, computer-use loop is disabled, and browser extension is offline with 2 pending commands.
  - evidence: GET /ops/status liveResponse HTTP 200; GET /browser/status liveResponse HTTP 200.
- **pendant-audio-path** — Pendant prototype captures at 15,625 Hz and uplinks Opus at 16 kHz/16 kbps; playback decodes Opus at 24 kHz/60 ms and resamples to 31,250 Hz I2S. Encode ~15.0 ms and decode ~25.4 ms per call; simultaneous work uses ~87% of one core.
  - evidence: get_hardware_spec(audio) live hardware specification.
- **pendant-connectivity** — No connected pendant, J-Link, serial, or firmware flash endpoint has been established in this round; available live observations are Mac HTTP routes and static hardware specifications.
  - evidence: devices discovery showed only home-macbook-bridge online; routes discovery exposed Mac agent routes, no device/flash route; hardware spec says faculty-perception is remote.
- **timezone-conflict** — Owner memory says timezone America/Chicago, while the live Mac machine-context reports timezone America/New_York; timezone is unresolved and scheduled briefs/reminders could be off by one hour.
  - evidence: owner discovery remembered.text says timezone America/Chicago; GET /machine-context liveResponse reports machine timezone America/New_York.

## Capabilities it proposed

### "“Run a pendant audio self-test and tell me exactly where the path works or fails.”"
- **useful because:** Today the system can report that services are online, but cannot establish that microphone capture, LTE delivery, relay transcoding, Mac pipeline receipt, and speaker playback all succeeded. A short spoken test with a localized evidence receipt prevents false confidence before relying on the pendant.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** Use a cheap background model to correlate timestamped test events; reserve realtime only if the owner speaks the test phrase live.
- **latency:** 10–20 seconds for a 5-second test; dashboard should stream stages as they arrive and finish with pass/fail per hop.
- **cost:** Roughly $0.01–$0.05 per invocation, dominated by any uploaded test audio and correlation; synthetic tone mode can be nearly free.
- **security:** A spoken test phrase leaves the pendant and may be stored temporarily. Default to a generated tone or a locally generated phrase; if recording voice, show retention and delete test artifacts automatically. No external action needs confirmation.
- **missing:** Pendant firmware diagnostic mode that emits capture-start/frame-count/CRC/playback-start markers and a loopback tone; Relay correlation IDs and a bounded diagnostic-event endpoint; Mac pipeline endpoint that acknowledges received and rendered audio with timestamps; Dashboard view for per-hop evidence, clock skew, and automatic expiry of test recordings

### "“If I lose signal halfway through a request, keep the request safely, resume it when any connection returns, and tell me exactly what was completed and what still needs me.”"
- **useful because:** A wearable is often used precisely when connectivity is unreliable. Today a dropped LTE or Mac/browser link can leave the owner unsure whether the request was heard, duplicated, or abandoned. This would turn interruption into a recoverable handoff: preserve the owner’s intent on the pendant, let the relay reunite it with the Mac/browser when available, and return an exactly-once completion receipt.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic queues, hashes, and state transitions for transport and deduplication; use a cheaper background model only to summarize the final receipt. Do not spend realtime inference on reconnection bookkeeping.
- **latency:** Immediate local acknowledgement in under 300 ms; resume within 5 seconds of a reachable node; if offline, notify on the next pendant connection and provide a final receipt within 30 seconds of completion.
- **cost:** About $0.005–$0.03 per resumed job, dominated by any model summarization; transport retries and hashes are negligible.
- **security:** Pending requests may contain private speech, account context, or browser session references. Encrypt the pendant queue, bind jobs to the owner and device key, expire abandoned jobs, never replay irreversible browser actions automatically, and require confirmation again if the original approval window has expired. The owner should be able to cancel locally while offline.
- **missing:** A durable encrypted pendant outbox with monotonic job IDs, payload hashes, expiry, and cancellation records; Relay-side exactly-once state machine with acknowledgements and replay protection across LTE, Mac, and browser links; Mac/browser adapters that can resume only idempotent or explicitly approved steps and emit signed completion receipts; Pendant UI/audio cues for queued, resumed, blocked-for-confirmation, completed, and expired states; A recovery protocol for interrupted audio upload and transcript finalization that avoids retaining raw audio longer than necessary


## Changes it proposed to its own stack

### `firmware` — Add an opt-in audio-path diagnostic protocol spanning pendant, relay, and Mac: each test gets a UUID and monotonic sample counters; firmware emits compact capture, LTE enqueue/ack, decode, I2S-DMA underrun, and playback markers to microSD, while relay and Mac append their receive/render timestamps. On reconnect, upload only the diagnostic summary (not raw audio) and expire raw artifacts locally.
- **owner gets:** When the pendant sounds silent or delayed, the owner gets a definitive answer such as “mic captured 4.8 s; LTE delivered; relay decoded; speaker had 2 underruns,” instead of having to guess whether to reboot or re-pair.
- effort: Medium-high: firmware event schema and flash-safe logging, relay correlation/storage, Mac acknowledgement route, and a small dashboard receipt; must fit the existing 211,608 B application RAM and one full-duplex I2S peripheral.  ·  risk: Extra logging can worsen SD/LTE timing or consume storage. Use a fixed-size ring buffer, event sampling, and compile-time diagnostic mode; if upload fails, retain only counters and retry summary. Never let diagnostics block the audio task.
- cost: Negligible API cost for summaries; small microSD writes and LTE bytes during explicit tests. No hardware cost if existing microSD is used.  ·  latency: No normal-path impact when disabled; test receipt adds up to one LTE round trip and reconnect delay for offline units.
- security: Diagnostic summaries avoid raw audio by default; UUIDs and timestamps still reveal use patterns, so authenticate uploads and apply short retention.
- depends on: A firmware build/flash or OTA path has to be established; Relay must expose authenticated diagnostic-event ingestion; Mac pipeline must acknowledge audio receipt/rendering; Clock-skew estimation between pendant, relay, and Mac

### `hardware` — Add a small secure element plus a dedicated low-power nonvolatile queue store to the wearable product design: the secure element holds a device identity/key and the queue store holds encrypted job envelopes, monotonic counters, cancellation tombstones, and receipt hashes. Keep microSD for bulk logs/audio only, never as the authority for pending actions.
- **owner gets:** The owner can trust that an offline pendant will neither lose a request nor execute an old request twice after reconnecting, and can cancel a queued request from the button without exposing private pending work on removable storage.
- effort: Moderate product redesign: select and route an I2C secure element and FRAM/MRAM or protected flash, add provisioning and recovery procedures, and implement firmware/relay key rotation and queue semantics.  ·  risk: Provisioning mistakes or damaged hardware could strand queued work. Use a replaceable-device enrollment flow, bounded queue with explicit expiration, and a recovery mode that discards pending actions while preserving only harmless diagnostics.
- cost: Approximately $1–$4 added BOM depending on secure element and memory; a few milliamps only during writes, essentially no continuous draw. API cost is negligible.  ·  latency: Sub-millisecond local queue commit; reconnect authorization adds one handshake round trip before relay processing.
- security: Strongly improves authenticity and confidentiality of offline jobs, but creates key-management responsibility. Never export private keys; require authenticated enrollment and remote revocation.
- depends on: Define the interrupted-request exactly-once protocol and user confirmation rules; Choose a production pendant rather than relying on the current Nordic development kit; Implement relay key registration, revocation, and encrypted job-envelope handling


## What it asked for

_Nothing._
## Its own summary

Established live truth: Mac agent v0.5.0 is healthy but Accessibility and Screen Recording are unavailable; computer-use is disabled; browser is offline with two pending commands. Pendant audio is still asymmetric (15.625 kHz capture/16 kHz uplink versus 24 kHz playback), with one full-duplex I2S peripheral and ~87% CPU for simultaneous Opus work. I recorded a timezone conflict (owner says Chicago; Mac says New York), shared readiness facts with judgement/action, and proposed a new cross-node audio self-test with UUIDs, hop-by-hop acknowledgements, underrun counters, and privacy-preserving summaries.

**Biggest unknown:** No connected pendant, J-Link/serial device, firmware build/flash/OTA route, or verified 24 kHz end-to-end test has been established. The next useful evidence requires a real device/flash path and a diagnostic event contract across pendant, relay, and Mac.

