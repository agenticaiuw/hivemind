# Harness derivation — mac-planner — round 138

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-and-audio-handoff** — Browser bridge is currently offline with 11 pending commands and no attached tab; relay and Mac bridge are reachable. Pipeline history shows 24-kHz TTS output is working (24,000 Hz PCM), but an owner utterance was captured at 15,625 Hz and 937,500 PCM bytes, confirming the remaining gap is uplink capture/wideband negotiation rather than playback alone.
  - evidence: GET /browser/status returned online:false, pendingCommands:11, tabId:null. GET /ops/status reported relay reachable and macBridgeOnline:true. GET /pipeline showed TTS metadata sampleRate:24000 and inputTelemetry sampleRate:15625.

## Capabilities it proposed

### "When my browser is offline, queue this request safely, do whatever can be completed on my Mac without the browser, and resume the authenticated browser steps when the bridge returns; tell me on the pendant exactly what completed, what is waiting, and what still needs my approval."
- **useful because:** The current browser can be offline with orphaned tabs and pending commands. Today a request either fails or leaves the owner wondering whether retrying will duplicate work. This makes the hive resilient: the pendant remains the control surface, the relay owns durable intent, the Mac performs independent reversible preparation, and the browser resumes only the missing authenticated steps with a clear receipt.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use the realtime model only for the short spoken status and ambiguity resolution; use a cheaper background model for intent decomposition, dependency analysis, retry scheduling, and receipt summarization.
- **latency:** Acknowledge on the pendant in under 1 second; decompose and persist the plan in under 3 seconds; resume automatically within one heartbeat after browser recovery. Do not block local Mac work on browser availability.
- **cost:** About $0.01–$0.05 per queued request depending on decomposition and final summary; most retries, heartbeat checks, and receipt generation are deterministic and should not invoke the expensive model.
- **security:** Persist intent and step state, not browser cookies or page bodies, in the relay. Keep authenticated extraction on the existing browser bridge; redact secrets from receipts. Never send or submit a browser mutation automatically after recovery: preserve the owner's existing destructive confirmation policy and show before/after evidence. Quarantine stale leases and require idempotency keys so reconnects cannot duplicate a form submission.
- **missing:** A durable dependency-aware intent record that can split Mac-local and browser-only steps and survive reconnects; Lease expiry/quarantine for stale browser commands plus resumable checkpoints keyed by request and step id; A typed handoff receipt that joins Mac job receipts, browser results, and pendant audio/status events; A browser recovery event or heartbeat contract that distinguishes a fresh bridge from an old session

### "When I say “save this for later” on the pendant, capture the thought, identify what I was looking at in the browser and what meeting or project it relates to, then create one private, cited Markdown note in my AI-Pendant-Workspace and tell me where it was saved. If the browser or Mac is temporarily unavailable, hold the capsule and finish it automatically when they return."
- **useful because:** The owner can speak an idea while walking away from the computer and later recover not just the words, but the page, project, and time context that make the idea useful. No single surface can do this: the pendant has the moment of capture, the relay can retain the intent, the browser has private page context, and the Mac has the durable workspace and local calendar/project data.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Use the realtime tier only to detect the short capture command and acknowledge it. Use a cheaper background model to transcribe, resolve page/project context, generate the Markdown note, and produce the final receipt.
- **latency:** Acknowledge capture in under 1 second and persist the raw capsule immediately. Finalize within 10 seconds when all surfaces are online; otherwise tell the owner it is held and complete it within one browser/Mac heartbeat after recovery.
- **cost:** Approximately $0.005–$0.03 per capsule; transcription and context resolution dominate. Deterministic storage, file creation, retries, and receipts should not invoke a model.
- **security:** Audio should be discarded after transcription unless the owner explicitly chooses retention. Browser content may contain secrets, so store only the minimum cited excerpt and URL, redact credentials and tokens, and never include private page text in spoken acknowledgements. Writing a note is permitted by the owner's current policy, but the file path and sources must be shown in the receipt.
- **missing:** A first-class offline capture capsule with durable id, transcript, source timestamp, and retry state; A browser-context snapshot API that returns the active tab's URL/title plus a bounded cited excerpt without requiring a live UI scrape; A context joiner that can associate the capsule with Calendar/project entities while preserving provenance and freshness; An idempotent Mac note writer that creates one Markdown artifact and updates it rather than duplicating it after retries; A pendant acknowledgement and later-completion event contract for held capsules


## Changes it proposed to its own stack

### `hardware` — Replace the prototype 15,625-Hz I2S microphone path with a production audio front end that captures 24 kHz (preferably 32 kHz I2S/PDM with hardware decimation), and ship a coordinated 24-kHz Opus profile end to end: pendant capture/encode, relay transcode and congestion control, and ESP32 playback. Add a tiny local jitter/packet-loss telemetry record (sequence gaps, encode/decode time, queue depth) that the pendant sends as compact events; have the Mac planner collect those receipts during calls and write a dated diagnostic bundle in ~/AI-Pendant-Workspace. Keep a negotiated fallback to the current 16-kHz uplink/24-kHz downlink profile when LTE-M budget is insufficient.
- **owner gets:** The owner gets genuinely wideband speech instead of a 24-kHz playback path fed by narrowband capture, while the system automatically falls back rather than dropping speech. When quality is poor, the Mac can explain whether the cause was radio contention, codec CPU, or playback buffering instead of making the owner guess.
- effort: High: select and validate a 24/32-kHz low-power microphone and clocking; firmware DMA/Opus profile and RAM/CPU measurements; relay negotiation and bitrate/QoS changes; Mac receipt collector and regression fixtures across radio contention and reconnects.  ·  risk: A higher-rate uplink can worsen the already measured half-duplex LTE-M contention (388 uplink packets lost during simultaneous speech), and the current nRF9160 CPU is already ~87% utilized when encode and decode run together. Recover with negotiated fallback, bounded queues, and watchdog-triggered profile downgrade; never make the new mode mandatory until packet-loss and latency thresholds pass.
- cost: Prototype API cost is negligible; relay compute/storage rises modestly with larger audio packets and telemetry. Hardware estimate: roughly $3–$10 incremental microphone/clock/analog-front-end BOM, with a small continuous power increase (validate against the final battery target).  ·  latency: Potentially +10–30 ms from larger frames/queues under contention; target <150 ms mouth-to-ear in wideband mode and immediate downgrade when queue age or loss exceeds threshold.
- security: Diagnostic bundles must contain timing and counters only, not PCM/audio or transcript; store locally with the existing workspace permissions and honor the existing audio retention/deletion policy.
- depends on: A firmware/relay negotiated audio-profile protocol (24-kHz wideband versus current fallback); A real packet-loss/queue telemetry event schema on POST /pipeline/events; A Mac read-only diagnostic collector or receipt endpoint; current mac_readonly_inspect cannot read call telemetry; Owner hardware acceptance target for speech quality, battery life, and maximum tolerable latency


## What it asked for

_Nothing._
