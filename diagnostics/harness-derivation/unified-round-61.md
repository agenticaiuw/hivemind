# Harness derivation — unified — round 61

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **current audio/browser integration state** — The live pipeline can render 24 kHz mono PCM (160.8 KiB, 3.43 s, zero clipped samples), but captured uplink telemetry is still 15,625 Hz and a response remains queued for nRF9160. Browser extension is offline with 5 pending commands, so authenticated browser work cannot currently complete.
  - evidence: GET /pipeline returned job_165a9c9a… with input sampleRate 15625 and TTS sampleRate 24000; GET /browser/status returned online:false and pendingCommands:5.

## Capabilities it proposed

### "“Check my private accounts for the answer, but only tell me what is safe to say aloud—and tell me how fresh and certain it is.”"
- **useful because:** Today the system can reach authenticated browser pages and speak a result, but it has no dependable cross-surface privacy boundary or freshness warning. This would let the owner use the pendant in public without accidentally hearing or repeating a password, access token, private message body, or stale account state, while still getting useful answers from browser-only sources.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use the realtime tier only for the short spoken request and final response. Use a cheaper background model for page extraction, sensitivity classification, freshness comparison, and provenance assembly; deterministic code should enforce redaction and policy rather than asking a model to decide alone.
- **latency:** Under 2 seconds for an answer from an already-open tab; up to 10 seconds for a multi-tab authenticated lookup. The pendant should say “I found it, but it is private” immediately when policy blocks spoken disclosure.
- **cost:** About $0.01–$0.08 per lookup depending on page count and background extraction; realtime audio and browser session access dominate, while deterministic redaction is negligible.
- **security:** Private page text must stay within the authenticated Mac/browser path unless explicitly permitted. Build a typed sensitivity policy (credentials, financial identifiers, health data, private message content, and user-defined terms), redact before TTS and before dashboard previews, and attach source URL/tab, capture time, and freshness. Never log unredacted text; require explicit confirmation to reveal a blocked field on the dashboard, and never speak it by default.
- **missing:** A shared sensitivity-and-freshness envelope carried from browser extraction through relay to TTS; A deterministic pre-TTS redaction gate with a fail-closed behavior when classification is uncertain; Per-owner spoken privacy policy and configurable safe categories; Provenance/freshness receipts that survive a Mac disconnect and can be reviewed later; An authenticated browser extraction contract that returns field-level evidence rather than an undifferentiated page blob


## Changes it proposed to its own stack

### `integration` — Add an end-to-end audio conformance gate that runs a deterministic spoken/DTMF test through the actual nRF9160 I2S capture, Opus uplink, Cloudflare relay transcode, downlink, ESP32 resampler/A2DP path, and headphone loopback. It records per-segment sequence numbers, PLC events, one-way latency, clipping, underruns, and speech continuity; fails deployment unless the 24 kHz target and simultaneous-talk loss budget pass. Store only compact metrics and hashes, not routine audio.
- **owner gets:** The owner gets a pendant that can be trusted before a firmware or relay update, instead of discovering during a real conversation that speech is missing, delayed, or silent.
- effort: Medium: firmware test mode and sequence markers, relay test endpoint, ESP32 loopback instrumentation, CI artifact parser, and a dashboard receipt. Requires physical headphone/bridge runs for final acceptance.  ·  risk: Test hooks could leak into production audio or retain recordings. Compile them out or protect behind an authenticated test build; retain metrics only. A false pass is mitigated by requiring a physical loopback stage and signed fixture results.
- cost: Negligible runtime/API cost; CI relay traffic and a small R2/D1 metrics record per test. Hardware fixture time is the dominant cost.  ·  latency: None in normal calls; test mode adds marker frames only.
- security: Test endpoint must be authenticated and isolated from owner recordings; metrics should contain no speech content.
- depends on: A defined 24 kHz end-to-end acceptance contract (latency, loss, MOS or intelligibility, clipping, and underrun thresholds); A link-aware duplex governor so the test can distinguish intentional bitrate adaptation from defects; A physical bridge/headphone fixture and an audio_pipeline_validate implementation

### `hardware` — For the wearable revision, replace the development-kit audio chain with a dedicated low-power full-duplex audio codec and a cellular MCU/module with hardware audio/DSP headroom, while retaining an explicit 24 kHz PCM interface. Keep the ESP32 bridge only as a temporary compatibility path; expose clock negotiation rather than hard-coding 15,625/31,250 Hz and 44.1 kHz conversions.
- **owner gets:** Conversations remain intelligible and responsive when the owner talks over the agent, without the pendant dropping speech because encoding and decoding consume nearly the whole current core.
- effort: High: product-board schematic/layout, codec and power validation, cellular certification, enclosure/antenna redesign, and a migration firmware mode for the current bridge.  ·  risk: New RF/audio hardware can introduce certification, battery, or driver regressions. Ship it behind the existing bridge protocol, run both boards in parallel, and retain the prototype as a fallback.
- cost: Prototype NRE is substantial; roughly $8–$25 in added low-volume components per unit (codec, PMIC, revised module/PCB), with modest idle-power reduction but codec and LTE bursts still dominating.  ·  latency: Potentially lowers encode/decode and resampling latency by removing software-heavy conversions; no guaranteed improvement until measured.
- security: No new data class; codec is local. Cellular module secure-boot and key storage must meet the production threat model.
- depends on: The conformance gate proposed this round; A product-level 24 kHz compatibility decision (headphones/phone companion versus A2DP bridge); A defined battery/runtime target and production pendant constraints beyond the current nRF9160 DK

### `integration` — Introduce a fail-closed spoken-disclosure firewall between every browser/research result and any audio output. Each extracted field is wrapped in a signed envelope containing sensitivity class, source tab/URL, capture time, freshness deadline, and allowed surfaces. The relay may summarize only fields whose policy permits voice; uncertain or expired fields become a spoken refusal with a dashboard-only evidence card. The same envelope is checked again immediately before TTS, so a compromised or stale intermediate planner cannot bypass the boundary.
- **owner gets:** They can ask the pendant questions over private accounts in public and trust that the answer will not accidentally speak secrets or present stale information as current; blocked details remain available for deliberate review on the dashboard.
- effort: Medium-high: define the envelope and policy schema, add browser field-level extraction, implement deterministic redaction and a second pre-TTS check in the relay, add signed receipts and dashboard review UI, then test disconnect/replay cases.  ·  risk: Over-redaction could make answers unhelpful, while under-redaction is a privacy incident. Default to blocking uncertain fields, provide a clear dashboard explanation, and use synthetic secret fixtures plus adversarial replay tests.
- cost: Small per-request CPU/storage overhead; background extraction and one extra policy pass add roughly $0.005–$0.03 per lookup. No routine audio retention is needed.  ·  latency: Adds roughly 50–200 ms for deterministic policy checks; field extraction remains the dominant delay.
- security: Improves confidentiality and provenance, but introduces policy and signing keys that require rotation, device-bound authorization, and no plaintext sensitive fields in logs, D1, R2, or model prompts beyond the minimum needed for extraction.
- depends on: Field-level browser evidence rather than whole-page blobs; A relay pre-TTS interception point on the real audio path; Owner-configurable spoken privacy categories and dashboard-only escalation; A key-management and replay-protection design shared by pendant, Mac, browser bridge, and relay


## What it asked for

_Nothing._
## Its own summary

Discovered the live system and added two new items. First, an end-to-end audio conformance gate is needed: the relay currently emits clean 24 kHz TTS, but live uplink remains 15,625 Hz, so only a physical nRF9160→relay→ESP32/A2DP loopback can prove the owner's requested path. Second, I proposed a production hardware direction with a dedicated codec/DSP and negotiated clocks, because the current nRF9160 prototype spends ~87% of its core on audio. Live evidence also shows the browser extension offline with five pending commands, and a response queued for the pendant.

**Biggest unknown:** The actual 24 kHz product acceptance contract is still missing: permitted one-way latency, packet-loss/PLC budget, intelligibility target, headphone/phone compatibility, battery/runtime target, and whether the current ESP32 A2DP bridge is allowed in the final product. I also still need the physical audio loopback fixture and the requested audio validation tool; discovery shows no new granted items this round.

