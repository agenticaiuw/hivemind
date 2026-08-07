# Harness derivation — relay-realtime — round 144

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Run a quick audio health check and tell me if my mic, bridge, and network are behaving before I start a call."
- **useful because:** When the owner is about to ask for help, a fast “your setup is good” reduces friction and prevents a bad experience from packet loss or miswired audio.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Realtime only for the spoken result; diagnostics and analysis should be automated and cheap.
- **latency:** A few seconds. It should be short enough to run right before a conversation.
- **cost:** Cheap: a brief tone/loopback and a small diagnostic report. Biggest cost is any cross-surface coordination and logging.
- **security:** No sensitive content is needed; use synthetic audio. Log only counters and timestamps. Avoid storing the test audio unless the owner asks.
- **missing:** A device skill to generate and loop back a test signal on the pendant/bridge; Cross-surface USB presence detection and truthful counters (packet loss, jitter, buffer underruns); A relay-visible event/report channel for diagnostics results

### "Put completed tasks in my pendant inbox so I can hear them later with a button press."
- **useful because:** The owner can stay hands-free and away from the Mac. The pendant becomes a lightweight notification and review device, not just a live mic.
- **path:** relay → pendant → mac-bridge
- **model tier:** Realtime for playback and short summaries; cheaper summarizer can prepare the message when the job completes.
- **latency:** Delivery can be delayed; playback should start quickly when the button is pressed.
- **cost:** Small: a short summary and references. Avoid attaching large artifacts; provide links or IDs instead.
- **security:** Summaries may contain sensitive info. Require clear provenance and avoid speaking secrets in public. Provide a way to skip or delete.
- **missing:** A completion-summary queue and storage for short audio/text summaries; A device skill for button-driven inbox playback and navigation; Relay events for button pickup and a quiet-mode interaction model

### "“When I press and hold the pendant button in an emergency, quietly let my trusted contact know where I am, keep a live check-in open, and tell me whether help acknowledged.”"
- **useful because:** A worn, one-button device is the only surface available when the owner cannot reach a phone or Mac. It turns the pendant into a dependable safety lifeline rather than merely a voice remote.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime handles the immediate spoken acknowledgement and intent; a cheap background worker maintains retries and acknowledgement state. The Mac/browser performs the authenticated messaging or calling workflow when available.
- **latency:** Local button acknowledgement under 300 ms; first outbound notification under 10 s; retry and acknowledgement tracking may continue for minutes.
- **cost:** About $0.01–$0.05 per incident in model/relay work, dominated by any SMS/voice provider and cellular data.
- **security:** Requires explicit enrollment of trusted contacts, signed device events, anti-replay sequence numbers, and encrypted location. Location and emergency text leave the device; a long press must be deliberate and a visible dashboard audit trail should exist. Never expose contact data to the model beyond the selected policy.
- **missing:** LTE-registered pendant event uplink and authenticated button-event endpoint; GNSS/location acquisition and encrypted location storage; durable retry/alarm worker with provider adapters; trusted-contact enrollment and acknowledgement callbacks; Mac/browser workflow for sending the notification when relay-only delivery is unavailable

### "“While I am walking, keep a private rolling audio transcript of the last 90 seconds; when I say ‘save that’, bookmark the moment, summarize the useful idea later on my Mac, and let me retrieve it by asking the pendant.”"
- **useful because:** Ideas and instructions disappear before the owner can reach a keyboard. A short rolling buffer gives them reliable recall without permanently recording everything, and combines the worn microphone, always-awake relay, and Mac for cheap delayed organization.
- **path:** pendant → relay → mac-planner → mac-terminal → dashboard
- **model tier:** Realtime only detects the save command and confirms it. An inexpensive background model transcribes and summarizes bookmarked segments on the Mac; the relay stores compact indexed metadata for later voice retrieval.
- **latency:** Save confirmation under 1 s; transcription within 30 s of bookmark; voice retrieval under 3 s for indexed notes.
- **cost:** Roughly $0.01–$0.10 per saved clip depending on audio duration and transcription model; storage is small, with audio retention configurable.
- **security:** The rolling audio must be encrypted and automatically discarded unless bookmarked. The pendant needs a conspicuous LED pattern and spoken confirmation; dashboard must show retention and deletion controls. Nearby voices may be captured, so owner-configured recording mode and local-only default are required.
- **missing:** On-device or bridge rolling PCM/Opus ring buffer with bookmark event; Authenticated relay clip upload and encrypted object storage; Background transcription/indexing job and semantic retrieval endpoint; Pendant playback/query response path and deletion controls

### "“When I arrive at my studio, prepare the exact work context I was using before I left—reopen the right Mac apps and browser tabs, restore drafts, and tell me what changed while I was away.”"
- **useful because:** The owner loses time reconstructing context after travel or interruption. The pendant provides physical arrival and identity continuity, the relay coordinates state, and the Mac/browser can restore authenticated work without requiring a spoken multi-step command.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** A background, low-cost classifier compares signed departure/arrival capsules and produces a restore plan. Realtime is used only for a short arrival confirmation or correction; Mac planner executes the reversible restore and browser extension restores session-bound tabs.
- **latency:** Detect arrival within 15 s; owner hears a concise ready/status response within 5 s after confirmation; restoration completes within 60 s.
- **cost:** Under $0.02 per arrival, dominated by a small state-diff model; no recurring model cost while idle. Browser and Mac API calls dominate execution time.
- **security:** Arrival geofences and work context are sensitive. Store coarse location hashes, not raw tracks, and sign departure/arrival events. Restoring tabs may expose private pages to anyone near the Mac, so require the pendant's authenticated proximity proof and provide an immediate lock/undo action.
- **missing:** Reliable pendant proximity/geofence events (GNSS or local beacon); Durable context capsules capturing Mac windows, browser tabs, drafts, and departure timestamp; Authenticated browser tab snapshot/restore and diff API; Arrival-triggered job scheduler and reversible Mac restore actions; Proximity proof stronger than bearer session identity

### "“Translate this conversation for me in real time: whisper the other person’s speech in my ear, and speak my replies in their language when I press the button.”"
- **useful because:** The pendant and audio bridge can mediate a face-to-face conversation without the owner holding a phone or looking at a screen. The Mac can supply a richer language model when nearby, while the relay keeps the interaction usable when it is not.
- **path:** pendant → relay → mac-planner → mac-terminal → dashboard
- **model tier:** Realtime speech detection, translation, and short utterance generation use the low-latency tier; a cheaper background model maintains a per-conversation glossary and language detection. The Mac is an optional high-quality fallback, not a requirement.
- **latency:** Detect speech and start translated playback within 1.5 s for short utterances; button-to-spoken reply under 2 s; degrade to buffered translation rather than fabricate when confidence is low.
- **cost:** Approximately $0.05–$0.30 per minute of active translated speech, dominated by streaming transcription and synthesis; idle cost is zero.
- **security:** Conversation audio leaves the pendant and may include bystanders. Require an explicit start/stop gesture, a visible recording LED, encrypted transport, configurable no-retention mode, and no transcript persistence by default. The owner should be able to cancel playback instantly.
- **missing:** Full-duplex low-latency audio transport between ESP32 bridge, relay, and pendant; Streaming ASR/translation/TTS with interruption and echo cancellation; Language selection and confidence signaling on the one-button/one-LED UI; Optional Mac fallback that does not expose browser credentials; Per-session retention and deletion controls


## Changes it proposed to its own stack

### `integration` — Add a cross-surface device presence and custody channel: signed pendant/bridge presence events from the Mac when USB is attached, plus relay-visible TTL capsules for tasks that require the device to be present.
- **owner gets:** Tasks that need the pendant (audio tests, playback, button interactions) won’t fail mysteriously; they run only when the device is actually available.
- effort: Medium. Requires signing, event propagation, and TTL handling.  ·  risk: If presence lies, the system will misbehave. Use signatures and short expiries; fall back to asking the owner to reconnect.
- cost: Low runtime overhead; some engineering across Mac and relay.  ·  latency: Small; presence checks should be cached and quick.
- security: Presence becomes a control signal; must be authenticated and tamper-resistant.
- depends on: Mac-side presence daemon and serial detection; Relay event ingestion route and verification

### `firmware` — Add a local audio self-test mode: generate a known tone or spoken test pattern, loop it through the mic/codec/bridge path, and report counters (packet loss, underruns, decode failures) without sending real user audio.
- **owner gets:** They can confirm the hardware path works before a call, preventing confusing failures.
- effort: Medium. Requires audio generation, loopback plumbing, and counter reporting.  ·  risk: Could interfere with normal capture if it fails to exit cleanly. Use a clear state machine and timeout.
- cost: Minimal compute; no extra components. Some firmware complexity and testing time.  ·  latency: A few seconds to run; negligible otherwise.
- security: Safer than using live audio. Only synthetic signals and counters are transmitted.
- depends on: A diagnostics reporting channel from device to relay; USB commissioning/calibration flow on the Mac bridge


## What it asked for

_Nothing._
