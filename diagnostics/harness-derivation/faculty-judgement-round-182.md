# Harness derivation — faculty-judgement — round 182

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Prepare this email, purchase, or browser form, then tell me exactly what will happen and let me approve it once from the pendant—but refuse if the page or facts changed.”"
- **useful because:** This is the safest way to make the Mac and authenticated browser genuinely act for the owner: preparation can be complex, but the final side effect is bound to a fresh recheck and a deliberate physical approval. It prevents stale-tab submissions, wrong-recipient mail, and price changes while keeping routine preparation fast.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → mac-terminal → pendant → unified → faculty-judgement → faculty-action
- **model tier:** Use the cheap deterministic policy and revalidation path for every request; use the expensive realtime model only to resolve ambiguity in the proposed summary or changed fields.
- **latency:** Preparation 1–5 seconds; approval preflight under 500 ms; if state changed, explain the diff in one spoken sentence and require a new prepare step.
- **cost:** Usually <$0.01 per request; model cost only when the plan or changed-state explanation is ambiguous. Browser/Mac execution and revalidation dominate latency, not tokens.
- **security:** The pendant receives only an opaque plan hash, target class, bounded human-readable summary, expiry, and nonce—not form secrets or page bodies. Revalidate browser/Mac state immediately before commit, run autonomy_policy_evaluate fail-closed, and require the existing physical_transaction_approval_latch for external or irreversible effects. A stale plan, changed recipient, changed amount, expired nonce, or uncertain permission must stop.
- **missing:** Wire physical_transaction_approval_latch into the Mac/browser commit endpoint, not just local preparation.; Persist a relay↔Mac↔browser plan correlation ID and approval decision; current IDs meet only in telemetry.; Make revalidate_pending_plan return typed changed fields and have POST /execute refuse the old plan.; Expose a compact pendant-safe summary/hash and a receipt linked to explain_action_provenance.

### "“When the pendant audio glitches, tell me whether it was the radio, codec, bridge, or relay—and leave a ready-to-file bug draft with the exact evidence.”"
- **useful because:** The owner explicitly wants a pendant that files its own bug reports, and the hardware is physically testable over USB now even without LTE registration. A correlated diagnosis is far more useful than a UART dump: it can distinguish a 24 kHz decode budget problem from packet loss, ESP32 playback starvation, relay generation delay, or a delivery interruption.
- **path:** pendant → mac-terminal → mac-planner → relay-realtime → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Run deterministic counters, packet/event correlation, and acceptance scripts first; use a cheaper background model to summarize the evidence and propose likely causes. Reserve realtime for the owner's spoken question.
- **latency:** Automatic local capture under 1 second after an anomaly; draft in under 10 seconds. Never block live audio on model analysis.
- **cost:** Near-zero API cost for parsing and metrics; <$0.02 only when a model writes a human-readable diagnosis. USB capture and local scripts dominate wall time.
- **security:** UART records must be scrubbed for credentials and audio payloads before leaving the Mac. Draft-only is the default: never file externally without explicit confirmation. Correlate opaque pipeline/artifact IDs, not transcript or raw PCM, and preserve signed pendant delivery ACKs for provenance.
- **missing:** A production Mac USB serial collector for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA with bounded rotation and crash recovery.; A typed join from UART sequence/time to pipeline ID, packet metrics, audio artifact, and record_pendant_delivery_event event.; Automated execution of scripts/audio-quality-probe.mjs plus threshold classification (alias rejection, codec CPU, mic drops, tx_starved, pre-speech samples).; A reviewable local GitHub/email issue draft writer that uses pendant_diagnostics_and_bug_draft output and never submits.

### "“If I’m interrupted or the link drops during a briefing, resume the exact item and position later—or let me say ‘next’ without losing my place.”"
- **useful because:** A briefing is only useful if it behaves like an owned queue rather than disposable speech. The pendant is the only surface that knows whether audio was actually downloaded and heard; the relay knows the semantic item; the Mac/browser can supply the source. Combining those lets the owner stop, defer, annotate, or resume without repeating or silently skipping content.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use deterministic item/cursor state and delivery ACK reconciliation; use a cheap background model only to produce a shorter replacement summary when the owner asks for one. Realtime is needed only for barge-in conversation.
- **latency:** Pause/next/defer under 300 ms locally; resume decision under 1 second after reconnect; never wait for model generation to stop playback.
- **cost:** <$0.005 for ordinary cursor operations; model cost only for requested compression or annotation. Storage and event reconciliation dominate engineering, not inference.
- **security:** Persist opaque item IDs, cursor tokens, source references, and playback positions—not raw spoken content on the pendant. Deduplicate offline ACKs by event ID and reject out-of-order or unverifiable events. A stopped item must not be replayed without an explicit resume/next decision; universal_stop_latch cancels it across surfaces.
- **missing:** A durable semantic audio manifest mapping each briefing item to an opaque artifact and source evidence, with stable cursor tokens.; Wire audio_brief_item_action pause/resume/next/previous/defer/create_note/create_reminder to the actual audio scheduler and preserve position across reconnect.; Consume record_pendant_delivery_event to reconcile downloaded/started/finished/interrupted states, including offline replay and duplicates.; Have attention_arbitrate and universal_stop_latch update the same item state instead of independently enqueueing or interrupting.; Expose an owner-visible playback receipt and source explanation through explain_action_provenance.

### "“Keep your voice intelligible and safe wherever I am—quietly adapt playback to the room, protect my hearing, and tell me when the environment is too loud for private audio.”"
- **useful because:** The current 24 kHz path improves fidelity but does not know whether the owner can hear it, whether the bridge is clipping, or whether raising volume would become unsafe. A closed-loop acoustic controller would make the pendant dependable in streets, offices, and transit instead of merely technically correct on a bench.
- **path:** pendant → ESP32 audio bridge → relay-realtime → mac-planner → unified
- **model tier:** Deterministic local DSP and safety limits should make all real-time decisions. Use a cheap background model only to classify repeated acoustic conditions for tuning; never put a model in the safety loop.
- **latency:** <50 ms for limiter/ducking; <2 s for a stable environment estimate; no network round trip for protection or intelligibility.
- **cost:** Negligible inference cost. Engineering cost is firmware DSP, bridge telemetry, and hardware validation; optional microphone calibration dominates any component cost.
- **security:** Use coarse local sound-pressure bands, not stored ambient recordings. Never upload room audio. A hard maximum output and monotonic attenuation must win over any user or model request to increase volume.
- **missing:** A calibrated output-level model for the ESP32 sink and pendant speaker/headphone path.; Firmware/bridge telemetry for output RMS, clipping, underruns, and coarse ambient RMS or SNR.; A safety limiter and hysteresis state machine that runs locally before Opus playback.; A relay/Mac policy that downgrades private content to a visual or queued form when acoustic privacy cannot be established.

### "“When I travel, have reminders, quiet hours, and spoken deadlines follow where I actually am—and show me when the system cannot establish my location instead of pretending.”"
- **useful because:** The system currently has a Mac timezone and a separate unresolved owner timezone, while the pendant has no captured NITZ, GNSS, or valid device instant. That makes portable routines and ‘this morning’ semantics fundamentally ambiguous. A provenance-backed location/time lease would make travel behavior honest without silently borrowing the Mac’s zone.
- **path:** pendant → relay-realtime → mac-planner → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use deterministic timezone database lookup and signed clock/location observations. Use the expensive model only to explain a conflict in plain language; never infer a timezone from conversational wording alone.
- **latency:** Local state update within 30 seconds of a trustworthy network/location observation; routine decisions under 500 ms; if no observation exists, explicitly return unknown rather than blocking unrelated local actions.
- **cost:** Low API cost. Hardware/firmware work and GNSS acquisition power dominate; LTE NITZ can avoid GNSS when registered.
- **security:** Store coarse timezone/offset and confidence, not a location trail. Require explicit owner policy before using location to alter reminders or disclose whereabouts. Sign observations, expire them, and preserve the current zone when a newer observation is weak or contradictory.
- **missing:** Pendant firmware support for authenticated NITZ capture when LTE is registered and an optional low-duty GNSS/time source in a future hardware revision.; A durable observation record carrying source, instant, timezone, confidence, and expiry, distinct from the Mac’s authoritative local zone.; A conflict resolver that presents ‘Mac zone vs pendant zone vs owner-declared zone’ rather than choosing silently.; Routine and briefing schedulers that consume the resolved zone and expose an unknown state to the owner.


## Changes it proposed to its own stack

### `hardware` — Add a low-power wear-state sensor to the pendant enclosure—prefer a clip/contact or capacitive presence sensor, with an explicit unknown state rather than guessing. Have the firmware emit only signed state transitions (worn, removed, unknown), never raw proximity data. The relay and Mac should use this state as a hard precondition for spoken private output and as a signal to defer nonurgent audio.
- **owner gets:** The system would stop speaking private material when the pendant is sitting on a desk, in a bag, or handed to someone else. Today it has Mac idle signals but no evidence that the pendant is actually being worn, so timing and confidentiality decisions can be wrong even when every software policy is correct.
- effort: Medium hardware revision plus firmware driver, calibration, USB test harness, and policy integration across relay and Mac. Preserve fail-closed behavior when the sensor is unknown.  ·  risk: False removed readings could suppress useful audio; false worn readings must never authorize sensitive speech. Recover by treating unknown as non-private and allowing the owner to request a public summary. Mechanical contact sensors can wear; capacitive sensing can be affected by clothing and humidity.
- cost: Roughly $0.50–$3 in components and PCB/enclosure changes; negligible average power if duty-cycled, but adds calibration and manufacturing complexity.  ·  latency: State transitions should reach the relay in under a second when USB/LTE is available; local firmware can immediately gate playback before reporting upstream.
- security: Improves disclosure safety without collecting identity or location. The signed transition should be monotonic and replay-resistant; raw sensor readings must remain local.
- depends on: A firmware playback gate that distinguishes public audio from private audio; A shared policy field defining what output is allowed when wear state is unknown; A relay/Mac consumer for signed wear-state transitions


## What it asked for

_Nothing._
