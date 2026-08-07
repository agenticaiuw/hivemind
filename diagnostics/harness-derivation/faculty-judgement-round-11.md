# Harness derivation — faculty-judgement — round 11

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I’m back—what happened while I was away?”"
- **useful because:** Today a dropped LTE link, dead battery, or headphones disconnected can make completed work indistinguishable from lost work. This gives the owner one trustworthy catch-up across the pendant, always-awake relay, Mac jobs, and authenticated browser work, without replaying every notification.
- **path:** pendant detects reconnect/charging and sends its last acknowledged event sequence → relay retains a compact ordered stream of job, approval, failure, and urgency events while the pendant is unreachable → mac-planner and browser-extension attach evidence links and completion receipts for work done during the gap → faculty-perception deduplicates events and separates heard, completed, blocked, and awaiting approval → relay-realtime speaks a one-sentence digest; pendant haptics indicate whether more items are waiting; Mac workbench holds full details
- **model tier:** Use a cheap background summarizer (gpt-5.6-luna or equivalent) to cluster and prioritize the retained event stream; use realtime only for the short spoken digest and follow-up questions. Browser/Mac evidence extraction happens at job completion, not at reconnect.
- **latency:** Under 2 seconds for a short digest after reconnect, assuming cached event metadata; under 10 seconds only when evidence must be fetched. Never block the digest on a slow browser page.
- **cost:** About $0.01–$0.05 per reconnect digest, dominated by summarization and any fresh evidence extraction; cached metadata should keep most reconnects near the low end.
- **security:** The relay must retain event metadata without retaining private page contents longer than policy allows. Browser links/snippets should be fetched only for items the owner requests. Spoken output can expose sensitive subjects in public; default to neutral titles and require a button press or voice request for details. Never imply an irreversible action occurred unless the Mac/browser receipt is cryptographically tied to its idempotency key.
- **missing:** A durable cross-surface event stream with per-pendant acknowledgment cursor and replay protection; A compact completion/blocked/approval receipt schema shared by Mac and browser jobs; Reconnect-triggered pendant push and optional haptic status patterns; Retention and redaction policy for offline event metadata

### "“Put us in silent mode—I need to use you without speaking or taking out my phone.”"
- **useful because:** The owner cannot reliably use the assistant in a meeting, on transit, or anywhere speech would be inappropriate. A true silent mode would turn the wearable into a discreet two-way interface instead of merely muting spoken output.
- **path:** a revised pendant with a small capacitive touch strip or two tactile controls and a haptic motor accepts a constrained tap language and renders short replies as distinct haptic patterns → relay-realtime switches the conversation into a low-bandwidth silent session and sends only compact intents/results → mac-planner and browser-extension perform the same authenticated work as voice sessions, but expose a terse status/result vocabulary → the Mac workbench retains the full text transcript and evidence for later review, while the pendant receives only the minimum needed to choose the next step
- **model tier:** Use the cheaper background model for intent classification, result compression, and action planning; reserve realtime for a brief transition command or if the owner exits silent mode. No expensive model should be spent generating prose the pendant cannot convey.
- **latency:** Local tap acknowledgment under 100 ms; common status/result patterns under 1 second; complex work can run asynchronously with haptic progress and a full Mac receipt.
- **cost:** Approximately $0.01–$0.05 per silent interaction, dominated by model calls; hardware revision adds roughly $5–$15 in controls, haptic actuator, driver, and enclosure changes, plus engineering.
- **security:** Haptics are observable by touch and can be misunderstood. Limit silent mode to reversible actions by default; require an explicit multi-tap confirmation for sending, deleting, purchasing, or sharing. Do not encode sensitive content in publicly guessable patterns. Show the full proposed action and evidence on the Mac before any irreversible operation.
- **missing:** A silent-mode protocol with a small, tested intent/result vocabulary; Pendant input hardware beyond the current single button and output beyond the current LED; Relay session state that can switch modalities without losing the conversation or action idempotency; Mac/browser UI for reviewing silent-session transcripts and pending confirmations


## Changes it proposed to its own stack

### `hardware` — Design the wearable revision with (1) a low-power fuel-gauge IC on the currently unused I2C bus, (2) a small vibration motor with a dedicated driver, and (3) a playback-reference line into the audio front end for hardware-assisted echo cancellation. Publish battery/charging state and haptic acknowledgment as signed pendant events; relay and Mac use them to track whether a queued job was heard, delivered, or needs retry. Define three tactile patterns (heard, waiting, urgent/failure), with quiet hours and an explicit double-press dismissal. Keep the current single-button/LED as fallback and do not add RAM-heavy logic to the nRF9160; the application remains within its 211,608 B budget.
- **owner gets:** The owner can walk away from the screen and still know that the pendant heard a request, is waiting on a long Mac/browser job, or failed before the result is lost. A fuel gauge prevents an apparently ignored request that was actually dropped during an LTE-M transmit burst. Echo cancellation makes natural interruption possible instead of forcing button choreography. This is a wearable-to-relay-to-Mac feedback loop, not merely a Mac notification.
- effort: Hardware revision and enclosure/audio-layout work; I2C fuel-gauge and haptic-driver firmware; relay event schema and Mac job-state integration; end-to-end tests for low battery, link loss, headphone playback, and dismissal. Medium-high, 4-8 weeks for a robust prototype.  ·  risk: Motor noise can couple into the microphone and worsen audio; mitigate with mechanical isolation, duty-cycle limits, and playback-reference AEC tests. Incorrect battery readings could create false reassurance; expose confidence/charging state and retain LED error codes. If the motor or gauge is absent, firmware falls back to LED and spoken receipts. Haptics must never silently approve destructive actions.
- cost: Roughly $3-8 in prototype components (fuel gauge, motor, driver, passives), plus board/enclosure redesign; motor adds tens of mA only while pulsing and the gauge is sub-mA. No meaningful per-request API cost; fewer repeated voice retries may reduce realtime usage.  ·  latency: Haptic heard acknowledgment can occur locally within tens of milliseconds; waiting/urgent patterns arrive with relay event latency. Hardware AEC adds a small fixed audio-front-end delay but should improve perceived turn-taking.
- security: Battery and delivery events contain no message content. Use authenticated, monotonic event IDs so a replay cannot appear to confirm an action. Keep haptic 'heard' semantically distinct from 'executed' and require the existing explicit confirmation boundary for irreversible actions.
- depends on: A durable cross-surface job/event state with idempotent event IDs; 24 kHz playback path and playback-reference access in the audio design; A pendant firmware event channel and relay-to-pendant push path


## What it asked for

_Nothing._
## Its own summary

I proposed a new wearable feedback layer: add an I2C fuel gauge, isolated haptic motor/driver, and playback-reference AEC input, then connect signed pendant events through relay to Mac/browser job receipts. This lets the owner know locally whether a request was heard, waiting, urgent, or actually completed, even away from a screen. I also proposed the owner-facing reconnect command, “I’m back—what happened while I was away?”, with a deduplicated spoken catch-up backed by retained cross-surface event cursors. I still need the durable event stream, acknowledgment/replay semantics, reconnect push path, and retention/redaction policy; the orchestrator’s pending context/tool requests should provide some of these, but none are visible to me yet.

**Biggest unknown:** Whether the existing cross-surface job/event persistence work already has an acknowledgment cursor and authenticated completion receipt. Without that, haptics and reconnect summaries risk reporting 'heard' as 'done'.

