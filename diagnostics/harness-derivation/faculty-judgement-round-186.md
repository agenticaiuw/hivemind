# Harness derivation — faculty-judgement — round 186

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Let the pendant tell me, in one sentence, whether the whole system is trustworthy right now: audio path, USB link, Mac agent, browser bridge, and last requested job."
- **useful because:** Today each surface can look healthy while the owner hears silence, stale browser work, or a job that never completed. This gives a single honest go/no-go answer before relying on the system, with measured evidence rather than a generic health green light.
- **path:** pendant → mac-planner → mac-terminal → browser-extension → relay-realtime
- **model tier:** background for measurement and deterministic aggregation; realtime only to phrase the final one-sentence answer
- **latency:** Under 20 seconds when USB-tethered; most time is on-device audio probe and serial round trips, not model inference.
- **cost:** Usually <$0.01; deterministic checks dominate and the model is optional.
- **security:** Read-only diagnostics only. UART logs, job identifiers, and browser connectivity status stay local unless the owner explicitly asks for a bug draft; redact tokens and page contents.
- **missing:** A typed USB serial health probe that can run the existing scripts/audio-quality-probe.mjs against the live pendant and ESP32 bridge; A stable aggregate verdict schema with per-surface evidence references; A relay-side read of the latest authenticated pendant delivery ACK, or an explicit 'not registered' result

### "Run a nightly hardware-in-the-loop check while the pendant is plugged into my Mac, and tell me only if today's audio path regressed; if it did, leave a reviewable bug draft with the exact failing metric and the last known good run."
- **useful because:** The owner currently has to discover regressions by hearing them. A scheduled check catches framing, underruns, alias rejection, mic drops, and tx starvation before the next conversation, while preserving the measured acceptance criteria already proven on hardware.
- **path:** relay-realtime → mac-planner → mac-terminal → pendant
- **model tier:** Background deterministic runner; use a cheap model only to summarize a confirmed regression and never to decide pass/fail.
- **latency:** 2–5 minutes overnight, with no interruption; the spoken result is deferred to the morning brief or an urgent alert only for a hard failure.
- **cost:** <$0.02 per run; USB serial capture and audio analysis dominate, with near-zero model cost on passing runs.
- **security:** No microphone content needs to leave the Mac. Store metric vectors and firmware/build hashes, not PCM. Bug drafts must never auto-submit and should include only redacted UART excerpts.
- **missing:** A routine executor that can acquire the two live USB serial devices exclusively and run a bounded test sequence; A durable baseline store for metric vectors and firmware/build identity; A scheduled-job lease/timeout so a crashed test cannot remain marked processing; A safe rule connecting confirmed regression output to pendant_diagnostics_and_bug_draft

### "When a device failure appears, have the system investigate it end to end: correlate UART and audio metrics, reproduce it on the plugged-in pendant, research the likely upstream cause in the browser, and leave me a cited issue draft plus a one-sentence explanation of what changed."
- **useful because:** A raw log is not actionable. This turns the pendant's failure evidence into a reproducible, reviewable diagnosis that combines hardware truth, local reproduction, and current upstream documentation—without silently filing or exposing the owner's data.
- **path:** pendant → mac-terminal → mac-planner → browser-extension → relay-realtime
- **model tier:** Background model for hypothesis generation and citation synthesis; deterministic parsers and local reproduction run first, and the model must label hypotheses separately from measured facts.
- **latency:** 1–3 minutes after the owner asks or a scheduled regression; final spoken answer under 10 seconds once the draft is ready.
- **cost:** $0.03–$0.15 depending on web research length; UART parsing and local reproduction dominate wall time.
- **security:** Only public upstream pages and redacted local metrics leave the Mac. Never upload raw PCM, auth headers, browser cookies, or private page text. Draft is local/review-only; submission requires explicit confirmation.
- **missing:** A structured issue-diagnosis orchestrator that can launch a bounded local reproduction before web research; Citation records joining each hypothesis to a UART metric, reproduction run, or public URL; A review UI that clearly separates measured fact, inferred cause, and proposed fix; A durable cross-surface correlation key linking relay job, Mac run, browser research, and draft

### "Let me ask the pendant, 'what did you actually say while I was away?' and get the last spoken item, its exact playback position, and whether it finished or was interrupted—without replaying private text unless I request it."
- **useful because:** A generated reply is not the same as a delivered reply. USB drops, queue loss, and accidental interruption currently leave the owner guessing. This gives a truthful delivery receipt and a safe short status by default, using the pendant's authenticated ACK rather than the relay's assumption.
- **path:** pendant → relay-realtime → mac-planner
- **model tier:** Deterministic receipt lookup and redacted status phrasing; realtime model only if the owner asks for a summary of several missed items.
- **latency:** Under 2 seconds for the latest item; under 10 seconds for a bounded history.
- **cost:** <$0.005 per lookup; storage query dominates and no model is needed for the default answer.
- **security:** Default response exposes only item title/status/position, not content. Full text requires an explicit owner request and must pass the existing delivery redaction policy. Device ACKs are authenticated, deduplicated, and scoped to the owner's session.
- **missing:** A durable query route over record_pendant_delivery_event results, including offline replay and duplicate suppression; A stable mapping from opaque artifactId to briefing item without putting spoken text on the pendant; A spoken-safe formatter that distinguishes generated, downloaded, started, finished, and interrupted

### "Let the pendant automatically keep spoken replies private in public: detect when nearby voices or a conversation are present, move sensitive replies to a private bone-conduction/ear-coupled channel, and otherwise use the normal speaker—without sending room audio to the cloud."
- **useful because:** Today the pendant has no bystander or acoustic-privacy boundary, so a correct answer can still be unsafe to say aloud. The owner should not have to predict every room change or manually choose a mode before asking for help.
- **path:** pendant → relay-realtime → mac-planner
- **model tier:** On-device deterministic acoustic classifier for occupancy/conversation likelihood; relay policy decides content class and destination. Use the realtime model only for the conversation itself, never to classify raw room audio remotely.
- **latency:** Under 300 ms to select the output path; no extra conversational turn. Calibration may take a few seconds when entering a new environment.
- **cost:** Prototype hardware roughly $15–$60 for an ear-coupled/bone-conduction output, ambient microphone and low-power DSP; ongoing inference cost near zero because classification is local.
- **security:** Raw ambient audio must never leave the pendant. Emit only coarse signed states such as quiet, speech-nearby, or unknown. Unknown must choose the private channel for sensitive content. The owner needs an explicit policy table for which classes may use the open speaker; secrets and credentials should default to private or silent.
- **missing:** A private output transducer and driver; the current ESP32 bridge is an open speaker sink; A second ambient microphone or validated acoustic-isolation arrangement; the existing conversation mic cannot safely double as a bystander sensor without careful echo and privacy analysis; Firmware-local occupancy classification and signed state events that work offline; A destination-aware speech policy connecting sensitivity to speaker versus private channel; A physical prototype and hearing-safety/volume limiter validation

### "When my hands are busy, have the system guide me through a real-world task one safe step at a time: find the authoritative manual in the browser, turn it into short spoken steps, wait for my physical confirmation, and remember exactly where I stopped."
- **useful because:** A general assistant gives a wall of instructions at the moment the owner cannot look at a screen. This would make the pendant useful for repairs, setup, cooking, and unfamiliar procedures while preventing the next step from being spoken or attempted until the owner confirms the current one.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Background model extracts and cross-checks procedures from cited sources; realtime model handles only the current step and a short clarification. A deterministic state machine owns ordering, confirmation, and stop behavior.
- **latency:** First step in under 15 seconds; subsequent steps under 2 seconds. Physical confirmation must be immediate and local even if the network drops.
- **cost:** $0.02–$0.10 per procedure depending on research and source length; most step transitions are local and model-free.
- **security:** Never infer that a dangerous step is complete from silence. Require deliberate physical confirmation, show source and risk level on the Mac, and stop on universal_stop_latch. Do not expose private browser page content to third-party models unless the owner-approved origin policy allows it.
- **missing:** A durable procedure state machine with step IDs, prerequisites, stop conditions, and resumable cursor; A pendant-local confirmation event that works offline and binds to the current step, extending the accepted physical transaction approval primitive; A browser research extractor that preserves citations and detects contradictory manuals; Risk classification and owner-configurable confirmation rules for electrical, financial, medical, or destructive steps; A cross-surface procedure cursor that survives Mac/browser restarts and reconnects


## Changes it proposed to its own stack

### `hardware` — Add a low-power 6-axis IMU and a skin/contact or capacitive-wear sensor to the next pendant revision, exposed over the currently free I2C bus, with a signed coarse state stream: worn, set down, moving, and unknown. Do not transmit raw motion; the firmware emits only state transitions and confidence.
- **owner gets:** The system can stop speaking private or urgent material into a room after the owner takes the pendant off, defer a conversation when it is left on a desk, and recognize that a physical stop or pickup happened even when the Mac/browser are busy. This supplies the missing bodily context no Mac signal can provide.
- effort: Medium hardware revision plus firmware classifier and relay policy integration; prototype on a breakout board first, then validate false transitions during walking, charging, and pockets.  ·  risk: False 'worn' or 'set down' states could suppress a needed alert. Fail open for emergency inbox items, expose the state and confidence, and require a stable transition window before changing speech policy. Sensor data could be sensitive if raw traces leak, so discard raw samples immediately.
- cost: Roughly $2–$8 BOM increase and milliwatts or less with duty cycling; no per-event API cost.  ·  latency: 100–500 ms transition detection; no effect on codec path if sampling is on a low-priority sensor task.
- security: Improves by making bystander/public uncertainty explicit, but introduces a new physical telemetry signal. Persist only coarse state, rotate session identifiers, and never upload raw accelerometer or capacitive readings.
- depends on: A policy input for worn/public uncertainty in attention_arbitrate and autonomy_policy_evaluate; Firmware event signing and offline queueing alongside the accepted audio delivery ACK queue; A product enclosure and sensor placement study; the current dev kit is explicitly provisional

### `hardware` — Add a discrete secure element with monotonic counter and protected key storage to the production pendant, wired on the currently unused I2C bus. Bind the button, privacy latch, audio-delivery ACKs, and firmware identity to device-generated signatures; make the relay reject replayed or downgraded events.
- **owner gets:** The owner gets a device whose 'I stopped this', 'I heard this', and 'I approved this' statements remain trustworthy after a dropped link, reboot, or cloned software image. That is the difference between a wearable control surface and an ordinary remote microphone.
- effort: Medium product-hardware and firmware effort: secure-element provisioning, signed-envelope protocol, monotonic-counter recovery, factory replacement procedure, and relay verification. Prototype with a dev-board secure element before a PCB spin.  ·  risk: Lost or replaced hardware can strand a device if recovery is poor; provide owner-mediated re-enrollment and a revocation path, never a silent key reset. Counter corruption must fail closed for mutation/approval but preserve read-only diagnostics.
- cost: Approximately $0.50–$3 BOM increase plus manufacturing provisioning; negligible runtime power and no model/API cost.  ·  latency: Sub-millisecond to a few milliseconds per signature depending on bus and operation; perform signing outside the audio deadline and pre-authorize only bounded envelopes.
- security: Substantially improves authenticity and replay resistance, but creates a high-value root key. Require per-device identity, relay-side revocation, signed firmware version binding, and no exportable private key.
- depends on: A concrete signed-envelope protocol shared by pendant, relay, Mac, and browser; Relay persistence for device revocation and monotonic-counter state; Production key-injection and recovery operations; the current Nordic development kit is explicitly provisional


## What it asked for

_Nothing._
## Its own summary

This round produced four owner-facing capabilities: a trustworthy whole-system verdict, nightly hardware-in-loop regression detection, end-to-end fault investigation with a cited draft, and a truthful 'what did you actually say?' playback receipt. I also proposed a next-pendant wear-state sensor that lets attention and privacy policy account for whether the device is being worn. The recorder flagged the health verdict and wear sensor as close to existing backlog ideas, so they should be treated as refinements, not wholly new primitives.

**Biggest unknown:** The concrete USB-tethered local voice feasibility remains unanswered. To turn the hardware proposals into executable work, the system still needs a bounded serial-test contract (device locking, commands, timeouts, and metric output), a durable correlation from artifact/job to pendant ACK, and a clear owner policy for what 'trustworthy' and 'urgent' mean. I did not re-request denied permissions or declined owner preferences.

