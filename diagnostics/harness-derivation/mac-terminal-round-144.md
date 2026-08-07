# Harness derivation — mac-terminal — round 144

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Make the pendant audio work reliably, and keep it sounding as clear as the connection allows.”"
- **useful because:** This is the first genuinely end-to-end wearable experience: the pendant button and mic, nRF9160 encoder, LTE/USB transport, relay transcode, ESP32 I2S/A2DP bridge, and headphones cooperate instead of each assuming a fixed format. A quality controller can negotiate 24 kHz superwideband when CPU and link budget permit, fall back to 16 kHz without dropping the conversation, and resume from short USB/LTE interruptions. The owner gets intelligible, continuous speech rather than having to know which node is broken.
- **path:** pendant → relay-realtime → mac-planner → new-surface
- **model tier:** Realtime model only for the spoken control and immediate diagnosis; a cheap background worker computes rolling packet-loss/jitter/CPU metrics and selects profiles.
- **latency:** Format/profile switch under 300 ms; speech end-to-end under 700 ms on LTE-M and under 250 ms over USB; metrics can lag by 2 seconds.
- **cost:** About $0.002–$0.01 per minute of relay audio depending on transcoding and storage; bandwidth and Opus CPU dominate, not model tokens.
- **security:** Audio remains in the existing relay path and should not be retained merely for quality control; send aggregate counters, not raw voice, to Mac diagnostics. A profile change is reversible and needs no confirmation; expose a physical LED/beep when the device is offline.
- **missing:** A negotiated audio-profile protocol shared by firmware, relay, and ESP32; 24 kHz capture/upsampling budget measured on the nRF9160; A USB-serial transport mode that can stand in for unregistered LTE-M; Per-hop sequence numbers and a jitter/latency telemetry packet; A bridge firmware update that can accept profile changes without starving A2DP

### "“Run an end-to-end pendant audio test now, tell me exactly where quality or latency fails, and leave the fixes ready to apply.”"
- **useful because:** Today nobody can distinguish a bad microphone, Opus CPU starvation, serial/LTE loss, relay transcoding, or ESP32/A2DP silence without manually inspecting several machines. This command would start a bounded test tone/voice fixture from the pendant, collect synchronized timestamps and sequence counters at nRF9160, Mac USB serial, relay, and ESP32, then return one spoken diagnosis plus a replayable repair plan. It turns the owner's current 24 kHz shipping goal into a measurable test they can run while wearing the hardware.
- **path:** pendant → mac-planner → relay-realtime → new-surface
- **model tier:** Background/cheap model summarizes structured measurements; realtime model is used only to answer a follow-up question or explain the diagnosis aloud.
- **latency:** Start within 2 seconds; a 20-second test completes in under 30 seconds; diagnosis under 3 seconds after collection.
- **cost:** Under $0.01 per test in relay compute/storage if raw audio is discarded; most cost is one short fixture stream and local serial capture.
- **security:** Default fixture is synthesized tones and a spoken prompt, never the microphone recording; if real speech is requested, retain only locally and delete it after the report. Applying firmware or bridge changes remains an explicit owner action, while collecting diagnostics is unattended.
- **missing:** A Mac USB-serial capture tool for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA with monotonic timestamps; A deterministic test-fixture mode and loopback marker packet in pendant firmware; Cross-node correlation IDs carried through relay and A2DP bridge; A machine-readable latency/loss report and repair-plan schema; A typed firmware/bridge update action with rollback metadata

### "“If I walk away from the Mac or lose LTE, keep my conversation alive and continue it when the pendant reconnects.”"
- **useful because:** The pendant is physically testable over USB today but not LTE-registered, so a dropped link currently makes the wearable feel dead. A durable handoff would let relay hold the turn, Mac bridge buffer only encrypted short audio, and the pendant resume with a compact spoken status instead of losing the question. It uses the wearable's physical presence, the Mac's USB reach, and the always-awake relay in a way none can provide alone.
- **path:** pendant → mac-planner → relay-realtime → new-surface
- **model tier:** Realtime for the active conversation; a cheap background process maintains the reconnect queue and compacts stale turn metadata without resending full context.
- **latency:** Detect loss in 1 second, acknowledge locally in under 150 ms, resume audio within 2 seconds of reconnection; queue metadata must stay under 8 kB per interrupted turn.
- **cost:** Negligible model cost; at most a few cents/day of relay storage for short encrypted pending turns, with audio deleted after successful replay or 10 minutes.
- **security:** Never persist raw microphone audio by default. Persist encrypted turn IDs, transcript snippets only after transcription, and a hash of unplayed response audio; bind the queue to the pendant identity and Mac session. Replaying an assistant answer is safe, but any queued Mac/browser action must expire and require the existing owner confirmation policy.
- **missing:** A pendant-local reconnect state machine with an offline chime and queue counters; A Mac USB serial proxy that can switch between direct relay streaming and local buffering; Relay turn leases, replay cursors, and deduplication across LTE and USB paths; A compact audio response cache and resume marker in the ESP32 bridge; A spoken 'resumed/expired' status event exposed to the realtime agent

### "“When I say ‘save this moment,’ put the useful context around what I’m looking at and hearing into one private note I can find later.”"
- **useful because:** The owner can currently create notes or inspect a Mac/browser state, but cannot atomically preserve the moment across the worn device, the active Mac window, authenticated Safari tabs, and the live voice turn. This would make the pendant a physical bookmark for real life: one utterance captures the spoken intent, the focused Mac app/document, selected open-tab titles/URLs, and a short transcript window, then leaves a concise, searchable note in ~/AI-Pendant-Workspace with provenance. It is useful precisely because no single node knows all four pieces.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → new-surface
- **model tier:** Realtime model extracts the owner's intent and chooses what context is relevant; a cheaper background model formats and deduplicates the note after capture.
- **latency:** Acknowledge the bookmark locally within 150 ms; gather Mac/browser context within 3 seconds; write the note within 8 seconds. If the browser is offline, save the voice and Mac portions immediately and attach the browser portion later.
- **cost:** Usually under $0.01 per bookmark; model input and optional transcript context dominate, while note storage is negligible.
- **security:** Authenticated page content must remain within the browser bridge and be reduced to explicitly selected snippets; never copy passwords, form fields, cookies, or hidden page text. Show a local confirmation tone and retain a delete command. Saving is reversible by deleting the generated note, but the spoken request itself should not silently trigger external actions.
- **missing:** A pendant-local bookmark event with a monotonic timestamp and conversation turn ID; A Mac context snapshot returning focused app/window/document and a bounded text selection without screenshots by default; A browser endpoint that returns only the active tab's owner-visible title, URL, and selected extraction, bound to a heartbeat/session; A cross-surface context joiner that correlates the pendant event with Mac and browser observations in a short time window; A note writer that stores provenance and supports one-command deletion

### "“While I’m wearing and holding the pendant, let it act as the key to a private working session across my Mac and browser; when I release it, stop sharing that context everywhere.”"
- **useful because:** The owner gets a physical, understandable privacy boundary that no software-only node can provide. A button-held session can authorize the relay to correlate the live voice turn with the focused Mac window and authenticated browser tab; releasing the button immediately ends correlation and prevents later queued work from using that context. This makes the wearable materially safer for sensitive work without reducing the owner's normal maximum-access workflow.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → new-surface
- **model tier:** Realtime model handles the live conversation; authorization and revocation are deterministic firmware/relay logic with no model call, and a cheap background cleanup expires stale snapshots.
- **latency:** Grant/revoke under 200 ms from button event; all surfaces observe revocation within 1 second; no extra latency on ordinary speech once the session is established.
- **cost:** Near-zero inference cost; small encrypted session records in relay D1 and local agent memory dominate.
- **security:** The pendant button is a proximity signal, not biometric proof: expose session state clearly with LED/beep and expire it on disconnect, timeout, or modem identity change. Do not treat it as permission to send mail, buy, delete, or submit forms; it only governs context visibility. Browser and Mac must erase cached sensitive projections on revoke.
- **missing:** Cryptographic pendant identity and signed button-session events; Relay-enforced capability leases understood by Mac and browser bridges; A context projection API that can be revoked and purged, rather than copied into prompts permanently; Mac/browser hooks to clear in-flight and cached private observations on lease expiry; A visible local session indicator and a recovery path for accidental disconnects


## Changes it proposed to its own stack

### `firmware` — Ship an audio-profile v1 across nRF9160 firmware, relay, and ESP32 bridge: keep the microphone's physical 15,625 Hz I2S clock but use a fixed-point 15,625→24,000 resampler before Opus, advertise encoder/decoder CPU headroom and packet size, and have the bridge accept mono 24 kHz PCM then perform its existing 31,250→44,100 output conversion. Add sequence numbers, profile IDs, and a 1-byte loss marker to every frame so the relay and Mac can distinguish silence from missing audio.
- **owner gets:** The owner can actually hear the promised superwideband path instead of a nominal 24 kHz decoder fed by a 16 kHz uplink, while the bridge remains compatible with the existing headphones. If the nRF9160 cannot sustain the profile, the negotiation has a truthful fallback rather than stuttering or silent A2DP.
- effort: Medium-high: fixed-point resampler and packet framing in nRF firmware, relay pass-through/transcode updates, ESP32 parser and buffering changes, then USB-serial and LTE-M soak tests.  ·  risk: The nRF9160 has only 211,608 B application RAM and current encode+decode already consumes roughly 87% of one core; 24 kHz encoding may overrun. Recover by refusing the profile based on measured CPU budget and falling back to the existing 16 kHz mode. Bridge buffer changes could recreate the known A2DP starvation; keep buffers bounded and retain the current small-buffer baseline.
- cost: No recurring model cost; roughly $0 hardware if existing chips suffice. A future external audio codec would add about $5–15 and ~20–50 mA only if measurements prove the nRF path inadequate.  ·  latency: Adds about one 20–40 ms resampler/frame stage; negotiated profile should remain below 700 ms end-to-end, with sequence telemetry making regressions visible.
- security: No new data leaves the device; frame metadata is non-sensitive. Do not persist diagnostic audio, and ensure profile negotiation cannot be interpreted as a queued action.
- depends on: USB serial access to both live devices during tests; A versioned audio-profile handshake in relay-realtime; A real end-to-end 24 kHz fixture and loss/latency measurement report; ESP32 firmware update and rollback path


## What it asked for

### `s19-raeg` (skill) — audio_link_truth_and_recovery
- does: On each button press and every 500 ms during an active conversation, detect whether the nRF9160 has a live USB serial or LTE-M audio route, whether frames are being acknowledged, and whether encoder timing exceeds its budget. Give distinct local tones/LED patterns for connecting, streaming, stalled, and resumed; on a stall, stop feeding stale frames, preserve only the current turn ID and replay cursor, and automatically restart the transport when the link returns.
- must be on-device because: Only the pendant can truthfully know button state, local encoder deadlines, modem/USB reachability, and whether its speaker path is producing frames while disconnected from the relay. It must provide feedback offline and survive a dropped cloud link.
- trigger: Button press starts monitoring; transport callbacks and a 500 ms timer update it; button release ends monitoring.
- storage: One compact reconnect record in reserved flash or microSD: turn ID (16 B), profile ID, replay cursor, last sequence, reason code, and timestamp; under 128 B, plus no raw audio.
- RAM budget: Under 2 kB: state machine, counters, and one packet buffer, safely below the 211,608 B application RAM budget; avoid allocating Opus buffers or filesystem objects in the watchdog path.

## Its own summary

Round 144 produced three new owner-facing capabilities: adaptive end-to-end audio that negotiates 24 kHz and survives profile fallback; a spoken, bounded end-to-end audio test that locates failures across pendant/Mac/relay/ESP32; and conversation handoff across USB/LTE loss. I also recorded a concrete audio-profile firmware/relay/bridge change and queued an on-device audio-link truth/recovery skill. The most important missing piece is not another planner route: it is a versioned audio-profile protocol with sequence/loss telemetry and a real fixture test over the two physically connected serial devices. I asked relay-realtime to identify its framing constraints.

**Biggest unknown:** Whether the nRF9160 can sustain 24 kHz fixed-point resampling plus Opus encode under its measured ~87% combined CPU load, and whether the current ESP32 bridge can accept profile changes without reproducing its known A2DP starvation. Until a USB-serial soak test measures this, 24 kHz is a design target rather than a truthful shipped mode.

