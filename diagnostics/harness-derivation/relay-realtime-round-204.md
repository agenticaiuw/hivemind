# Harness derivation — relay-realtime — round 204

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If you can’t reach the internet, save my request and try again when connectivity returns."
- **useful because:** The owner can speak a task once and trust the system to eventually deliver it, instead of failing silently or asking them to repeat themselves.
- **path:** pendant → relay → mac-bridge
- **model tier:** Realtime for immediate acknowledgement and fallback messaging; queued retry logic should live in firmware/relay and run cheaply.
- **latency:** Immediate acknowledgement under 1s; retry is opportunistic.
- **cost:** Low; dominant cost is durable storage and retry attempts.
- **security:** Queued items may contain sensitive speech. Encrypt at rest where possible and minimize payloads.
- **missing:** Typed durable outbox for non-audio requests beyond the existing voice memo failure path; A retry policy shared between pendant and relay; Conflict handling to avoid duplicate execution when retries overlap

### "“Turn what I just said into the right finished artifact—update the project file, prepare the browser form or message, and tell me exactly what changed.”"
- **useful because:** This is the most useful missing end-to-end ability: the owner can speak an intent while away from the desk and receive a completed, inspectable result rather than a memo or a plan. The relay preserves the utterance and constraints, the Mac edits local material, and the browser handles a session the Mac agent alone cannot safely reconstruct.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Realtime relay extracts the short intent and constraints; mac-planner performs the multi-step plan with the cheaper planner tier; browser harness executes authenticated browser steps; relay returns a concise spoken receipt while dashboard exposes the artifact and provenance.
- **latency:** Acknowledge in under 500 ms; first spoken progress within 3 s; completion can take 30–120 s asynchronously.
- **cost:** About $0.01–$0.08 per request depending on planner/browser turns; browser and Mac execution dominate, not the short realtime interpretation.
- **security:** The utterance, selected local files, and browser page data leave the pendant and may cross the relay. The owner policy permits trusted execution, but the result must include exact files/pages touched, action receipts, and an easy voice undo for reversible edits; never claim completion without verification.
- **missing:** A typed artifact-intent envelope shared by relay, mac-planner, and browser harness; A cross-surface execution journal that links each mutation to its source utterance and verification; A result handoff that can deliver a compact receipt to the pendant after the live turn

### "“I’m leaving now—keep working on this task across my Mac and browser, recover from a transient failure, and tell me only when there is a real result or a decision you need from me.”"
- **useful because:** The owner currently must remain in a voice turn or manually poll. This would make the pendant a true handoff point: it can launch a long, cross-surface job while the owner walks away, distinguish a recoverable failure from a decision, and deliver a useful result later.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Realtime only classifies the handoff and captures constraints; a background planner/executor and browser worker do the work; a small summarizer turns verified receipts into a spoken alert.
- **latency:** Immediate acceptance under 1 s, durable job start under 5 s, completion notification whenever finished; retries should not require the owner to reconnect.
- **cost:** Roughly $0.02–$0.20 per job, dominated by multi-step planner calls and browser retries; idle waiting should cost near zero via alarms/queues.
- **security:** Long-lived credentials and unattended mutations are the main risk. Persist least-needed job context, redact secrets from receipts, make retry idempotent, and notify on ambiguity rather than guessing. Data must be encrypted in transit and expire after completion.
- **missing:** A real durable queue with retries and idempotency keys; Worker Cron/ Durable Object alarms or equivalent background execution; A job state machine with blocked/needs-owner states and durable event delivery; Browser and Mac leases so two workers cannot mutate the same session concurrently


## Changes it proposed to its own stack

### `integration` — Make the physically connected nRF9160 pendant and ESP32 audio bridge usable as a first-class USB-tethered voice transport: a local Mac bridge should expose the same session/job/event contract as LTE, automatically switch between USB and LTE, and surface transport health and queued inbox/outbox state to the relay without creating a second audio protocol.
- **owner gets:** The owner can test and use the worn pendant today while it is attached to the Mac, instead of pretending it is LTE-registered and debugging through synthetic requests. A walk-away session can begin on USB, survive unplugging by switching transports, and return queued audio/alerts when reconnected.
- effort: Medium-high: implement a signed local bridge daemon, transport negotiation, reconnect/resume sequence numbers, and integration tests on both serial devices; then add relay-side transport selection.  ·  risk: A bad handoff could duplicate audio, lose a spoken response, or expose the local serial device to another process. Use monotonic message IDs, acknowledgements, bounded replay, and a visible LED/voice indication of offline state; fall back to the existing LTE path and offline store.
- cost: Low recurring API cost; approximately 1–2 weeks engineering. No new hardware required because both USB serial devices are live. The bridge adds modest Mac CPU and USB power draw.  ·  latency: USB should reduce round-trip latency by tens of milliseconds; reconnect negotiation may add up to 2 s but must resume without replaying completed chunks.
- security: The local bridge becomes a privileged voice/audio endpoint. Bind to localhost, authenticate the serial device, encrypt local IPC where practical, and never accept arbitrary browser-originated commands through the bridge.
- depends on: A shared transport/session envelope with resumable sequence numbers; A local Mac bridge process for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; Relay routing that can select USB versus LTE and emit truthful transport health


## What it asked for

_Nothing._
