# Harness derivation — relay-realtime — round 276

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Tell me when that’s done."
- **useful because:** This is the single most useful experience: the owner can start a task and move on, then get a spoken update when it completes, without polling or keeping the Mac awake.
- **path:** relay → mac-bridge → pendant → phone → dashboard
- **model tier:** mac for planning/execution; relay for low-latency conversation; background watch should use a cheaper tier than realtime
- **latency:** Start/confirm within a second or two; completion delivery can be minutes later.
- **cost:** Cheap per watch (one job status read loop), but potentially frequent; avoid realtime model except for the spoken confirmation.
- **security:** Completion summaries may expose sensitive task names. Only deliver to owner devices. Require confirmation before sending to phone/dashboard if it includes potentially sensitive content.
- **missing:** A real job completion watcher that runs after the voice session ends; A reliable delivery mechanism to pendant/phone/dashboard (relay_event_push is currently unresolved); Durable offline delivery semantics for pendant/phone

### "“Why did you do that?” — after any Mac, browser, or phone action, explain in one spoken answer exactly what I asked, what evidence you used, what action ran, and what changed; if the result is uncertain, say so and offer undo."
- **useful because:** A wearable assistant that acts across several surfaces is otherwise unauditable. The owner needs a fast way to recover trust and diagnose mistakes without finding a laptop or reconstructing logs.
- **path:** pendant → relay → mac-planner → mac-vision → browser → ios → dashboard
- **model tier:** Use relay-realtime only to interpret the spoken follow-up and render the short answer; retrieve structured receipts and have a cheaper background model assemble the causal timeline.
- **latency:** Under 2 seconds for a completed job; under 5 seconds if a journal and browser evidence must be joined.
- **cost:** About $0.01–$0.04 per explanation, dominated by background summarization; receipt retrieval itself is negligible.
- **security:** The explanation must inherit the original job's redaction and surface permissions; never read hidden browser values merely to explain an action. Undo must remain explicit and target the exact job receipt.
- **missing:** A durable causal receipt linking utterance, projected context, planner decision, concrete actions, evidence snapshots, and resulting state across Mac/browser/iOS; A relay voice query that resolves “that” to the most recent action and fetches its joined receipt; A redacted, user-facing explanation schema plus exact inverse/undo metadata

### "“Change the plan: do the same thing, but skip the email and save the draft instead.” — while a long Mac/browser job is running, let me interrupt it from the pendant, inspect its checkpoint, edit one step in plain speech, and resume without restarting everything."
- **useful because:** Long workflows currently force the owner to wait, cancel blindly, or repeat work. A worn interrupt-and-edit control would make multi-surface automation practical when the owner is away from the Mac.
- **path:** pendant → relay → mac-planner → mac-vision → browser → ios
- **model tier:** Relay-realtime handles the interruption and confirmation language; a cheaper planner patches the remaining action graph; the executor applies only the suffix after a durable checkpoint.
- **latency:** Acknowledge the interrupt within 500 ms and expose a checkpoint within 3 seconds; resume within 5 seconds after the owner's edit.
- **cost:** $0.02–$0.08 per edit, mostly the planner's graph patch and a compact state summary.
- **security:** Checkpoint state can contain private page text and draft contents, so retain only encrypted, redacted state with an expiry. Never replay already-completed mutations; show the owner the exact changed suffix before resuming.
- **missing:** Cooperative cancellation at action boundaries for Mac, browser, and iOS executors; Durable checkpoint records containing completed actions, observed state hashes, and a replay-safe remaining graph; A pendant-facing job-control route supporting pause, inspect, patch, resume, and abort; Idempotency keys and compensation metadata for actions that cannot be safely replayed

### "“Keep this private.” — for the next spoken request, execute it normally but do not retain audio, transcript, screenshots, browser findings, or derived memory beyond the live turn; tell me on the pendant when the private boundary begins and ends."
- **useful because:** The owner wears the device in unpredictable places and may need to handle sensitive matters. A real, bounded privacy mode is more useful than hoping every downstream surface happens to redact the right artifact.
- **path:** pendant → relay → mac-planner → mac-vision → browser → ios → dashboard
- **model tier:** Relay-realtime owns the boundary and uses deterministic deletion/retention controls; use no background summarizer inside the boundary.
- **latency:** Boundary acknowledgment under 300 ms; cleanup completion and a spoken receipt within 2 seconds of the turn ending.
- **cost:** Negligible model cost beyond the request itself; storage deletion and audit markers dominate operational work.
- **security:** The privacy promise must be enforceable, not merely a prompt instruction: block memory writes, screenshot/browser persistence, long-term logs, and completion pushes containing content. Keep only a minimal tamper-evident event that private mode was invoked, without utterance text.
- **missing:** A per-turn retention lease propagated from relay to planner, browser, iOS, and Mac vision; Transactional suppression and deletion hooks for audio, transcript, screenshots, browser findings, journals, and memory; A post-turn verifier that proves no content-bearing artifact escaped the lease; A physical pendant gesture or unmistakable spoken state transition that prevents accidental activation


## Changes it proposed to its own stack

### `relay` — Implement a real asynchronous completion delivery mechanism for jobs (pendant/phone/dashboard), with durable offline handling and TTLs, and wire it into job completion watching.
- **owner gets:** They can start a task, stop talking, and still get the result later without checking back.
- effort: Medium-high: requires durable storage for pending notifications and a delivery pipeline.  ·  risk: Duplicate or out-of-order notifications; mitigate with idempotent receipts and job state checks.
- cost: Moderate: storage for pending notifications and periodic job polling.  ·  latency: Improves perceived responsiveness by removing the need to keep a session open.
- security: Must ensure only the owner’s devices receive notifications; sensitive content handling required.
- depends on: Pending notification store; Reliable device addressing/registration

### `relay` — Add a USB-local pendant session bridge: when the nRF9160 and ESP32 are attached to the owner's Mac, a signed local serial/WebSocket adapter should present them to the relay as the active voice endpoint, forward uplink/downlink audio and button/LED state, and expose the same session identity and health telemetry used by LTE. It must fail closed when the serial device identity changes and must clearly label the session as USB-local.
- **owner gets:** The owner can wear and test the real pendant today even though LTE registration is absent, with the same end-to-end voice experience rather than a simulator or manual capture workflow.
- effort: Medium-high: local adapter, relay session authentication, audio framing integration, reconnect handling, and firmware status mapping.  ·  risk: A compromised Mac USB process could impersonate the pendant or capture audio; use per-device keys, explicit local pairing, short-lived session leases, and a visible USB-local indicator. Recover by dropping the local session and returning to normal offline memo behavior.
- cost: Low recurring API cost; modest engineering cost. No new hardware required because both chips are already physically connected over USB serial.  ·  latency: Potentially lower than LTE; target under 100 ms serial-to-relay overhead and preserve the existing 24 kHz/60 ms framing.
- security: Adds a local trust boundary and must not silently broaden access to the Mac. Authenticate the serial identities and bind each session to the paired pendant key.
- depends on: A local signed serial adapter for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; Relay support for a USB-local transport alongside LTE; A session capability/health record that distinguishes USB-local from LTE


## What it asked for

_Nothing._
