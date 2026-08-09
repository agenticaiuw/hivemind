# Harness derivation — unified — round 266

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “what did that website change?”, show me the exact before/after evidence from the bound browser tab and tell me whether the change was actually committed."
- **useful because:** Today a successful browser command or spoken receipt can mean only that a click was dispatched. This gives the owner a trustworthy answer grounded in page state, not an optimistic action log—especially valuable for purchases, settings, and forms.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** background for DOM diff extraction and compact summarization; realtime only to answer the follow-up question
- **latency:** Under 5 seconds after the page settles; otherwise report pending rather than guessing
- **cost:** ~$0.01–$0.04 per verification, dominated by one small background model call if deterministic DOM diffing is insufficient
- **security:** Only inspect the explicitly bound tab/session and redact secrets before relay storage. Never include passwords, payment fields, or full page text in the evidence capsule. Require confirmation before any additional browser mutation.
- **missing:** A browser result contract carrying pre-action and post-settle DOM/accessibility fingerprints, changed selectors, and screenshot hashes; A relay-side evidence capsule joined to the existing action receipt and an owner-facing query; A browser settle/verification action that can wait for navigation/network idle without clicking anything

### "If my Bluetooth headphones disconnect while you are speaking, stop the reply locally before any private audio comes out of the bridge, and tell me whether it was muted, rerouted, or lost."
- **useful because:** A relay can report that audio was delivered while the ESP32 is already sending to nowhere or falling back to a speaker. The bridge is the only node that knows the actual A2DP route, so this prevents private speech from leaking and makes a dropped reply explainable.
- **path:** pendant → relay → mac-bridge
- **model tier:** deterministic firmware/bridge state machine; realtime model only to phrase the resulting event
- **latency:** Mute or hold within one Bluetooth status interval, target under 100 ms; resume only after a stable reconnect window and an explicit policy decision
- **cost:** Negligible model cost; roughly 1–2 KB firmware state and a few bytes per delivery event
- **security:** Fail closed on unknown route state. Do not auto-fallback to the Mac speaker. Persist only route state and opaque audio artifact IDs, never PCM. Resume must be tied to the same artifact and deduplicated.
- **missing:** ESP32 A2DP connection/output-route callback exposed to the audio scheduler; A bridge-to-relay signed route-state and mute receipt, joined to audio_delivery_ack_queue; A policy value for hold-versus-discard after disconnect, with conservative hold as the default

### "Did you actually hear and answer my last press? Give me one status that separates microphone capture, relay receipt, transcription, model completion, and physical playback."
- **useful because:** A dropped modem packet, a stalled STT turn, and audio that never reached the headphones currently collapse into vague silence. This lets the owner retry the missing stage instead of repeating an entire request or trusting a false 'done'.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** Deterministic correlation and counters; background model only to summarize an unusual failure in plain language
- **latency:** Normal answer under 1 second from locally cached receipts; full reconciliation under 4 seconds
- **cost:** Near-zero model cost; bounded metadata index of at most a few dozen turn records, around 100–200 bytes each
- **security:** Use opaque turn IDs and sequence/checksum metadata, not transcript or PCM in the status path. Bind queries to the owner's active session and expire records. Never retry an external action merely because a turn is incomplete.
- **missing:** A single turn ID propagated from pendant capture through relay STT/model and bridge playback; A durable, deduplicated state machine with explicit states capture_started, uplink_accepted, transcript_committed, response_ready, bridge_received, playback_started, playback_finished; A read-only owner query and compact pendant status event for the first failed stage

### "When I ask “what am I looking at?”, describe the currently focused Mac window or browser tab through the pendant, identify the important controls and warnings, and let me ask a follow-up about one visible item without saving the screenshot."
- **useful because:** The owner can reach logged-in pages and Mac apps through the system, but the wearable cannot presently turn the visual state in front of him into an on-demand, privacy-bounded spoken explanation. This would make the pendant useful when his hands and eyes are occupied while avoiding a permanent visual record.
- **path:** pendant → mac-bridge → browser → relay → mac-bridge
- **model tier:** Realtime vision-language inference for the first description and follow-up; deterministic OCR/accessibility extraction first to reduce image tokens and cost
- **latency:** Initial description within 3 seconds; follow-up within 2 seconds while the bound window remains unchanged
- **cost:** Approximately $0.02–$0.10 per request depending on whether a screenshot is required; no storage cost because the image is discarded after the response
- **security:** Require an explicit spoken/button trigger; capture only the focused, explicitly bound window; redact passwords, payment fields, and private notifications before inference; do not persist screenshots or inferred page contents; refuse if the focus changed before answering.
- **missing:** A read-only focused-window capture/accessibility snapshot route that works without granting broader Accessibility or Screen Recording permissions to unrelated binaries; A short-lived, session-bound visual context token so follow-ups cannot inspect a different tab; A pendant delivery path for the spoken description and a receipt proving the image was discarded

### "Before submitting a form, read back only the fields I changed, their normalized values, and the destination domain; let me correct one field by name without rereading the whole page."
- **useful because:** The owner can already drive forms, but cannot reliably audit what the system is about to submit while hands-free. A compact changed-field readback catches wrong recipients, amounts, dates, and account settings before they leave the browser.
- **path:** browser → pendant → relay → mac-bridge
- **model tier:** Deterministic DOM/accessibility extraction and field normalization; realtime language only for the owner's correction and confirmation
- **latency:** Readback under 2 seconds after the form stabilizes; field correction under 3 seconds
- **cost:** Usually <$0.01 per use; extraction and normalization are deterministic, with a small realtime call for ambiguous labels
- **security:** Never speak or transmit password/token fields; classify sensitive inputs locally and say only “a protected field is filled.” Bind the preview to form action, origin, and a short expiry. Do not submit after a correction without a fresh explicit confirmation.
- **missing:** A browser-side form diff/normalization result that identifies changed fields without exposing secrets; A pendant interaction contract for field-name correction and confirmation, bound to the exact form fingerprint; A browser submit guard that refuses if the DOM, origin, or changed values differ from the preview


## Changes it proposed to its own stack

### `integration` — Add a signed, monotonic turn-envelope propagated unchanged from pendant capture through relay pipeline events, model completion, and ESP32 bridge playback. Store only the bounded state transitions and artifact hashes; expose a read-only reconciliation endpoint that returns the first missing stage and never retries side effects.
- **owner gets:** When a reply disappears, the owner gets an exact answer—“your voice reached the relay but playback never started”—and can retry only the missing conversation turn instead of guessing or repeating themselves.
- effort: Medium: schema and correlation changes across pendant/relay/bridge plus deterministic tests for loss, reconnect, duplicate packets, and late receipts.  ·  risk: Clock skew or reconnects could create false gaps; use monotonic per-device sequence numbers and explicit unknown states. Never infer playback from relay acceptance. Roll back by treating envelopes as optional metadata while retaining existing pipeline behavior.
- cost: Negligible storage and bandwidth (tens of bytes per transition); no recurring model cost.  ·  latency: No added audio-path latency; reconciliation is asynchronous. A local cached status query should be sub-second.
- security: Improves provenance without retaining content; sign IDs/hashes and redact transcript/audio. Prevent replay by device counter plus session binding.
- depends on: A stable per-turn identifier in POST /pipeline/events and POST /pipeline/audio; Bridge playback acknowledgements from the existing audio_delivery_ack_queue; A read-only route joining pipeline artifacts to GET /jobs/:jobId/receipts

### `hardware` — Replace the prototype ESP32 classic A2DP-source bridge with a production bridge that supports a modern low-latency Bluetooth codec (LC3/LE Audio where the headphone target permits it), hardware audio-route detection, and an isolated watchdog-controlled output path. Keep the 24 kHz pendant stream as the source contract; perform only the negotiated headphone adaptation at the bridge.
- **owner gets:** The owner gets faster, more reliable speech with fewer Bluetooth stalls and a bridge that can fail closed when headphones disappear, instead of silently buffering or leaking audio through an unintended route.
- effort: High: select and validate a production radio/codec module, port the bridge protocol, qualify target headphones, and repeat on-device audio acceptance and loss tests.  ·  risk: Headphone compatibility may be worse during transition and a new codec can introduce interoperability failures. Retain the current SBC bridge as a fallback fixture and gate rollout by measured packet loss, startup time, and route-disconnect behavior.
- cost: Prototype-to-product module likely adds roughly $10–$30 BOM and modest standby power; recurring API cost is none.  ·  latency: Potentially reduces Bluetooth buffering by tens of milliseconds, but must be measured per headphone; no change to the pendant's 60 ms Opus framing.
- security: Hardware route sensing and fail-closed output reduce accidental speaker leakage. Pairing keys must remain in protected storage and never transit the relay.
- depends on: A formal bridge route-state/playback acknowledgement contract; Repeated audio_pipeline_validate and audio_link_fault_inject coverage for each supported headphone profile; A production hardware decision for enclosure, battery, and thermal limits


## What it asked for

_Nothing._
## Its own summary

Recorded three distinct capabilities this round: (1) Bluetooth-route-aware fail-closed speech privacy when the ESP32 loses headphones, (2) a turn-integrity query that distinguishes capture, relay/STT/model, bridge receipt, and physical playback, and (3) a signed monotonic turn-envelope integration change implementing that correlation without retaining PCM. A browser before/after verification idea was also recorded as connective work. The extracted-fact review proposal was correctly rejected as an existing capability, so I did not restate it.

**Biggest unknown:** The remaining blocker is implementation ownership and exact schemas between the existing pipeline endpoints and the ESP32 bridge: specifically whether bridge playback acknowledgements can be emitted and whether a stable per-turn ID can be threaded through POST /pipeline/events and POST /pipeline/audio. I do not need another permission request this round; those are engineering gaps to build.

