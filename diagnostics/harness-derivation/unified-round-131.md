# Harness derivation — unified — round 131

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Keep my conversation going when I move between LTE and my Mac—don't make me repeat myself if the pendant loses signal or is plugged in.”"
- **useful because:** Today a dropped LTE link can lose speech, while the physically connected pendant is already testable over USB. A resumable session would make the pendant feel dependable: the Mac can carry audio and control while available, and LTE can resume later without restarting or replaying the whole request.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → dashboard-ux
- **model tier:** Realtime model only for the live turn; a cheap background worker reconciles transport state, packet gaps, and session receipts.
- **latency:** Transport handoff under 500 ms when USB is present; at most one short spoken status if recovery takes longer.
- **cost:** Negligible model cost during handoff; roughly $0.001–$0.01 per recovered session for relay metadata and any retransmitted audio, dominated by storage and LTE egress.
- **security:** USB serial must authenticate the same pendant identity as LTE and never expose microphone audio to arbitrary local processes. Encrypt cached frames, expire them quickly, and require explicit opt-in before Mac fallback; no raw audio should leave the Mac except through the relay.
- **missing:** A signed USB-serial transport adapter in the Mac agent; Session-level sequence numbers and resumable uplink/downlink cursors in the relay and pendant; A transport arbitration state machine with duplicate suppression and bounded replay; An end-to-end handoff test using /dev/cu.usbmodem00096003658* and the ESP32 bridge

### "“Why did you do that, and what did you see?”"
- **useful because:** When the system acts across Safari, Mac apps, and the relay, a single action log is not enough: the owner needs a spoken, chronological explanation tied to the exact page evidence, command, approval, and result. The pendant is the fastest place to ask while away from the desk; the Mac/dashboard can show expandable source evidence and undo links.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard-ux
- **model tier:** Use a cheap structured summarizer for routine receipts; escalate to the realtime model only when the owner asks a follow-up or the evidence conflicts.
- **latency:** A short spoken explanation within 2 seconds; detailed evidence can load on the dashboard within 5 seconds.
- **cost:** About $0.002–$0.02 per explanation, dominated by summarizing selected receipts rather than replaying full conversation context.
- **security:** Redact secrets and private page content by sensitivity class. Only the owner’s authenticated session may query a job; preserve immutable hashes of evidence rather than copying full page bodies into prompts. Never let an explanation endpoint itself execute or mutate anything.
- **missing:** A unified event schema linking pendant utterance IDs, relay decisions, browser tab/DOM evidence, Mac action receipts, and resulting state; A query endpoint that builds a bounded causal timeline for a job or spoken reference; Dashboard drill-down with source snippets and one-click undo where supported; A spoken disambiguation flow when 'that' maps to multiple recent jobs

### "“Keep listening to this conversation, but fork off the research and come back when you have a sourced answer—don't make me wait in silence.”"
- **useful because:** A wearable conversation is often interrupted by a slow authenticated lookup or Mac workflow. This lets the owner continue walking or thinking while a background branch works, then receives a concise spoken result with citations and can ask to merge it into the original task. It combines realtime presence with durable, asynchronous work instead of forcing either a blocking voice turn or a disconnected job.
- **path:** pendant → relay-realtime → relay → mac-planner → browser-extension → dashboard-ux
- **model tier:** Realtime model acknowledges and manages the branch; background research and extraction use a cheaper model, with realtime reserved for the final spoken merge and ambiguity resolution.
- **latency:** Acknowledge/fork in under 700 ms; first progress signal within 5 s; final result whenever complete, with quiet-hours and interruption policy.
- **cost:** Roughly $0.01–$0.10 per branch depending on browser pages and extraction; background model tokens and authenticated browser dwell dominate, not the brief realtime acknowledgement.
- **security:** Branch inherits the parent conversation's permissions but cannot broaden them. Keep private-page citations scoped to the owner, show exactly which tabs were read, redact secrets from spoken output, and require confirmation before the branch performs any mutation. Allow immediate cancellation from pendant and dashboard.
- **missing:** A first-class branch/parent job model with independent cancellation, checkpoints, and merge receipts; A realtime event channel that can announce completion without stealing an active turn; Context snapshots that freeze the relevant utterance and permissions at fork time; A dashboard view showing branch status, evidence, and merge/dismiss controls

### "“Translate this conversation for me in real time, and use the terminology from the document open in my browser.”"
- **useful because:** The owner could use the pendant as an interpreter while walking through a meeting or phone conversation, while the Mac/browser supplies private glossary context that the pendant alone cannot access. The system would speak short translated turns through the audio bridge and show the source/translation pair on the Mac for correction.
- **path:** pendant → audio bridge → relay-realtime → mac-planner → browser-extension
- **model tier:** Realtime model for turn-by-turn translation; a cheaper background model extracts a terminology glossary from the explicitly selected browser document.
- **latency:** Translated speech begins within 1.5 seconds of an utterance, with incremental playback for longer turns.
- **cost:** Approximately $0.01–$0.08 per translated minute, dominated by realtime audio tokens and transcription; glossary extraction is a small background cost.
- **security:** Never inspect browser tabs implicitly: the owner must select the source document. Keep original and translated audio ephemeral, visibly indicate recording/translation, and require confirmation before retaining a glossary or transcript.
- **missing:** A full-duplex translation mode in the relay; Language identification and interruption-safe turn segmentation; A browser-to-translation glossary handoff with explicit tab consent; Pendant controls for repeat, slow down, and stop

### "“Let my colleague use the pendant for ten minutes, but only for translation and directions—nothing from my accounts, memory, or browser.”"
- **useful because:** A wearable is physically shareable, but today its identity and permissions are effectively all-or-nothing. A time-limited guest mode would let the owner hand it to someone safely, preserving the owner's private context while still making the device useful in a meeting, trip, or emergency.
- **path:** pendant → relay-realtime → relay → dashboard-ux → mac-planner
- **model tier:** Cheap policy/model routing handles the capability allowlist; realtime is used only for the guest's live conversation.
- **latency:** Guest activation and visible confirmation within 2 seconds; revocation should take effect on the next request and locally within one button cycle.
- **cost:** Under $0.01 per guest session beyond normal realtime audio; cost is dominated by a small policy lookup and session metadata.
- **security:** Use a separate ephemeral principal, cryptographic session token, hard expiry, and local LED/audio indication. Guest requests must be denied access to memory, browser cookies, Mac actions, and recordings by construction—not merely by prompt instruction. Owner revocation must work offline when possible.
- **missing:** Ephemeral guest principals and capability-scoped authorization; A local guest-mode state and expiry indicator on the pendant; Relay enforcement that prevents guest context from entering owner sessions; Dashboard controls to create, inspect, and revoke a guest session


## Changes it proposed to its own stack

### `hardware` — Add a low-power 6-axis IMU and a capacitive touch/proximity electrode to the pendant, with an interrupt line exposed to the nRF9160. Define local gesture primitives (double-tap, long-hold, wrist-cover) and make them available to the relay as signed events; retain the existing single button as the hard stop. Use the IMU's FIFO so the nRF9160 does not continuously sample at high CPU cost.
- **owner gets:** The owner could control and silence the assistant without looking at or finding a tiny button: double-tap to replay or acknowledge, long-hold to cancel, and covering the pendant to mute its output in a meeting. These gestures still work when LTE is down and make urgent alerts usable while walking or driving.
- effort: Moderate hardware revision plus Zephyr driver, gesture debouncing/calibration, signed event protocol, and end-to-end usability testing across clothing and motion. Prototype first with an I2C breakout because the pendant's I2C bus is currently free.  ·  risk: False gestures could cancel speech or expose a private response. Keep cancellation as button-only until confidence is high, require a deliberately long gesture for mute, and provide LED confirmation. If the sensor fails, the original button path remains fully functional.
- cost: Approximately $2–$6 BOM increase for an IMU, electrode/analog front end, and board changes; sensor draw roughly 20–200 µA depending on FIFO/interrupt mode. No per-call API cost.  ·  latency: Local gesture acknowledgement under 100 ms; negligible relay latency because events are sent out-of-band.
- security: Gesture events are control signals, not audio, but must be authenticated and replay-protected. A physical mute gesture should latch locally before any server confirmation.
- depends on: A firmware event envelope with monotonic counters and replay protection; A local output-mute latch implementation (currently requested, not yet delivered); A user-configurable gesture map and safe defaults in dashboard settings

### `firmware` — Add a local acoustic-environment governor that classifies only coarse conditions—quiet, speech-overlap, wind/noise, and likely headphone feedback—using short-lived spectral features on the nRF9160, then adjusts Opus bitrate, VAD thresholds, LED behavior, and playback ducking before sending a signed mode event to the relay. Do not retain or transmit the classifier audio or raw features.
- **owner gets:** The pendant would remain understandable in a street, vehicle, or crowded room without the owner manually changing settings. It could reduce interruptions when someone else is speaking, warn locally about feedback, and spend less LTE bandwidth in noise while preserving speech intelligibility.
- effort: Substantial firmware DSP work and field calibration across wind, traffic, restaurants, and speech overlap; likely needs a small fixed-point classifier and careful coexistence with the current high CPU Opus path.  ·  risk: Misclassification could clip the owner's speech or suppress an important response. Defaults must fail open for uplink, apply only gradual parameter changes, and expose a physical-button override. Validate against recorded test signals without storing owner conversations.
- cost: No per-call API cost. Roughly $0–$3 BOM cost if the existing microphone is sufficient; perhaps 5–15% additional CPU and a few kilobytes of RAM for feature windows/classifier.  ·  latency: Local adaptation in under 100 ms; no extra network round trip.
- security: Improves privacy because raw environmental audio remains local and classifier output is coarse. Signed mode events must be authenticated and rate-limited so a compromised client cannot force unsafe audio settings.
- depends on: A firmware audio-mode event envelope; A relay policy for accepting device quality hints; A test harness for noisy and overlapping-speech audio conditions


## What it asked for

_Nothing._
