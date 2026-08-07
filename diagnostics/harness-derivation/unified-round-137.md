# Harness derivation — unified — round 137

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Is my pendant audio working?” — run a complete end-to-end check while it is plugged into my Mac, then tell me exactly what failed."
- **useful because:** The owner is explicitly trying to ship the 24 kHz path. A one-command test that exercises nRF9160 I2S, Opus encode/decode, USB serial, ESP32 resampling, and A2DP playback turns invisible audio regressions into a result they can trust today.
- **path:** pendant → mac-planner → relay-realtime → dashboard
- **model tier:** background for the deterministic test and report; realtime only if the owner asks follow-up questions
- **latency:** Under 60 seconds for a full loopback; spoken verdict under 2 seconds after completion.
- **cost:** <$0.01 per invocation; almost all work is local tones, packet counters, and DSP measurements, not model tokens.
- **security:** No speech or account data needs to leave the Mac. Require explicit confirmation before sending any captured microphone sample to the relay; default to synthetic tones and discard buffers.
- **missing:** A serial test/control protocol on the nRF9160 and ESP32; A relay or Mac route to inject synthetic audio and collect per-stage counters; A signed, versioned audio acceptance profile for 24 kHz/60 ms frames; A dashboard receipt showing stage-by-stage measurements

### "“Keep this conversation going if I unplug the Mac.”"
- **useful because:** Today the pendant is physically testable only over USB, while production LTE is half-duplex and lossy. A true handoff would let the owner walk away without ending a thought: pause at a sequence boundary, resume over LTE, and reconcile late USB packets without duplicated speech.
- **path:** pendant → mac-planner → relay-realtime → dashboard
- **model tier:** realtime for the live session; background model only for post-call reconciliation and diagnostics
- **latency:** A handoff gap under 500 ms at a clean boundary; never silently drop or replay a frame.
- **cost:** <$0.03 per handoff, dominated by realtime audio inference during the call; control frames and reconciliation are negligible.
- **security:** The relay must authenticate the same pendant session on both transports and reject replayed sequence numbers. Show a visible LED pattern and spoken notice when routing changes; never upload buffered microphone audio after a user-selected privacy stop.
- **missing:** A USB serial audio transport alongside the LTE WebSocket; A session identity and monotonic audio sequence protocol shared by both links; Relay jitter/reconciliation logic and link-health measurement; Firmware governor for half-duplex bitrate and bounded local buffering; An explicit user privacy-stop state that survives transport changes

### "“When I say ‘pin this moment’, save enough context that I can find it later.”"
- **useful because:** A wearable is present exactly when something happens, while the Mac can see the active app, Safari tabs, calendar, and files. Combining a short local audio marker with a timestamped, cited Mac context gives the owner a reliable memory anchor without requiring them to stop and type.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** realtime only to recognize the explicit pin command; background model extracts a compact title and searchable entities after capture
- **latency:** LED acknowledgement within 150 ms; context snapshot within 5 seconds; no blocking of the live conversation.
- **cost:** <$0.01 per marker when audio stays local; occasional background transcription/extraction is the dominant cost.
- **security:** Default to a 2–5 second ring buffer and redact secrets/password fields from browser context. The marker must be visibly acknowledged, list exactly what was captured, and provide one-tap deletion; never capture arbitrary screen pixels unless separately enabled.
- **missing:** A pendant-local ring buffer and explicit pin gesture/voice event; A Mac snapshot API that returns active app, selected browser tabs, and current project with provenance; Browser redaction of password/payment/secret fields; A durable marker index searchable from voice and dashboard; Retention and deletion controls for marker audio and context

### "“Did that reply actually reach my pendant, and which connection carried it?”"
- **useful because:** The live pipeline already records contradictory-looking facts (a recent nRF9160 audio job says live LTE and uploaded, while the device inventory says the pendant is not registered). A spoken, evidence-backed delivery verdict prevents the owner from guessing whether silence came from the relay, modem, USB path, or headphones.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** background lookup and deterministic receipt synthesis; realtime only to answer during an active call
- **latency:** Under 1 second from an end-of-call button press; include a later correction if delayed telemetry arrives.
- **cost:** Negligible API cost; query and receipt formatting dominate, not model inference.
- **security:** Receipts may reveal timestamps and connection metadata, so bind them to the owner's authenticated session and retain only short-lived summaries. Never claim playback success from upload alone; distinguish accepted, downloaded, decoded, and audible.
- **missing:** One unified receipt index joining relay job, pipeline events, pendant sequence acknowledgements, and ESP32 playback counters; A monotonic delivery state machine with explicit unknown state; Firmware/bridge acknowledgements for download, decode, and A2DP enqueue; A voice/dashboard endpoint that can query the last interaction by time or utterance

### "“Tune the pendant audio to my hearing and headphones.”"
- **useful because:** The current path has fixed gain, fixed resampling, and a generic 24 kHz voice target. A short guided test through the actual pendant microphone, ESP32 bridge, and headphones could create a personal EQ, loudness, and intelligibility profile so speech is clear without unsafe volume.
- **path:** pendant → mac-planner → relay-realtime → dashboard
- **model tier:** background for the deterministic hearing/calibration test; realtime only for spoken guidance
- **latency:** A 3–5 minute first-time calibration; profile application under 100 ms on subsequent calls.
- **cost:** Under $0.02 per calibration; tone generation and DSP are local, with model use limited to explaining results.
- **security:** Calibration recordings should remain local and be discarded. Enforce a hard maximum output level and require explicit confirmation before raising it. Do not infer medical hearing loss or present this as a clinical test.
- **missing:** A tone/sweep generator and microphone-response measurement on the nRF9160/ESP32 path; Per-owner profile storage with versioning and reset; Safe loudness limiter and profile-aware 24 kHz playback DSP; A Mac/dashboard calibration wizard and receipt

### "“During my meeting, quietly keep me oriented and only interrupt me when something is urgent.”"
- **useful because:** The pendant is the one surface that can hear the owner and speak privately, while the Mac knows the calendar event and browser documents. A meeting mode could identify the active meeting, maintain a low-cost private transcript, surface names/decisions/action items on demand, and reserve spoken interruptions for explicit urgency.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** realtime for wake-word/urgent interruption decisions; background model for rolling notes, entity linking, and post-meeting summary
- **latency:** On-demand answers under 1.5 seconds; ordinary notes batched every 30–60 seconds; urgent alert under 500 ms.
- **cost:** Roughly $0.05–$0.30 per hour depending on transcription and context volume; background summarization should dominate rather than realtime reasoning.
- **security:** Meeting audio and private browser pages are highly sensitive. Require an explicit physical-button start, a visible LED recording state, participant disclosure controls, local-first buffering, automatic deletion window, and never send browser secrets or unrelated tabs into the meeting context.
- **missing:** A meeting-mode lifecycle tied to Calendar event identity; Low-latency local/VAD transcription with bounded rolling context; A private pendant output policy distinguishing urgent from nonurgent cues; Browser/document context allowlists and redaction; Participant consent and retention controls

### "“If the pendant gets too loud, distorted, or hot, protect me and tell me why.”"
- **useful because:** The owner currently has no dependable local indication that the audio chain is clipping, starving, or behaving dangerously; LTE contention has already caused long uplink loss and the bridge has tight RAM margins. A local safety controller could mute or attenuate before an artifact reaches the owner, then explain the fault later through the Mac and relay.
- **path:** pendant → mac-planner → relay-realtime → dashboard
- **model tier:** No model for the safety cutoff; background model may summarize diagnostics after the event
- **latency:** Hardware cutoff under 20 ms; spoken explanation after reconnection, never blocking the protective action.
- **cost:** Near-zero API cost. Small firmware/bridge CPU and flash overhead; possible <$5 BOM addition for a temperature/current sensor in a product revision.
- **security:** The cutoff must be fail-safe and local, not dependent on cloud availability. Never auto-resume at a louder level. Persist only compact fault telemetry unless the owner explicitly requests audio evidence.
- **missing:** Output peak/RMS and distortion telemetry at the bridge; ESP32 and pendant temperature/current sensing or safe proxy limits; A local mute/attenuation state machine with hysteresis; Fault codes carried through pipeline receipts and spoken/dashboard explanation; Product hardware review for thermal and battery limits


## Changes it proposed to its own stack

### `integration` — Build a physical-link audio test harness that opens /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA, sends a versioned test command to the nRF9160, drives synthetic full-duplex frames through the ESP32 bridge, and emits a signed stage receipt (I2S capture, Opus, serial, resampler, A2DP) into the existing pipeline/job journal. Keep test mode synthetic by default and expose a single dashboard/voice action.
- **owner gets:** They can plug in the real pendant today and know in under a minute whether the audio path actually works, instead of debugging from a misleading green connection or listening for intermittent silence.
- effort: Medium: serial protocol and firmware test endpoint, ESP32 diagnostic mode, Mac harness, receipt schema, and one dashboard panel.  ·  risk: A diagnostic command could collide with a live call or starve the ESP32 Bluetooth buffers. Gate it on an idle session, use bounded test packets, and recover by resetting both serial devices; receipts must clearly say synthetic versus microphone audio.
- cost: No meaningful API cost. Approximately $0 hardware because both boards are connected; engineering time is the cost.  ·  latency: Adds no latency to normal calls; diagnostic takes up to 60 seconds.
- security: Synthetic mode sends no owner speech. Device commands need authenticated session binding and a physical-button or Mac confirmation before microphone capture tests.
- depends on: A versioned USB serial control protocol; A deterministic 24 kHz acceptance profile; Mac serial access from the local agent; ESP32 diagnostic instrumentation


## What it asked for

_Nothing._
