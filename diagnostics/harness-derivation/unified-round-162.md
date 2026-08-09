# Harness derivation — unified — round 162

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Move this conversation from the Mac to the pendant" or "bring it back to USB without losing my place.""
- **useful because:** The owner can walk away from the Mac or return to it without restarting, repeating himself, or hearing duplicated replies. A turn-boundary handoff makes the currently real USB-attached pendant useful today while preserving LTE as a future transport.
- **path:** pendant → relay → mac-bridge → mac-planner
- **model tier:** Realtime only for the handoff utterance and boundary decision; deterministic relay state machine plus background reconciliation for the transfer.
- **latency:** Acknowledge within 250 ms; complete at the next turn boundary, normally under 2 s. Never cut an audio frame mid-playback.
- **cost:** <$0.001 per handoff; dominated by one small realtime turn and no extra audio generation.
- **security:** Transfer a conversation handle and monotonic turn checkpoint, never raw transcript by default. Bind both transports to the same device/session nonce; reject stale or duplicated checkpoints and expire an unclaimed handoff after 60 s. Require the owner’s normal button press/voice request, not silent migration.
- **missing:** transport-neutral turn journal with atomic checkpoint records; USB serial and LTE session ownership events surfaced to the relay; bridge-side acknowledgment of the last played frame and relay-side acknowledgment of the last accepted uplink frame; a small handoff command/status route

### ""Stage this form, show me exactly what will be submitted, and only send it after I approve on the pendant.""
- **useful because:** This is the missing end-to-end version of physical approval: the browser can hold the authenticated page, the Mac can inspect the proposed submission, the relay can bind a digest and expiry, and the pendant can provide offline-safe consent. It prevents the current dangerous failure mode where the system says it is waiting for approval but discards the blocked plan.
- **path:** browser-extension → mac-planner → relay → pendant → dashboard
- **model tier:** Background/planner model to summarize and verify fields; deterministic digest/world checks and physical approval state machine; realtime only to explain the staged proposal.
- **latency:** Stage in under 5 s; owner gets a concise spoken/readable preview immediately. Approval execution starts within 1 s of a valid physical approval, with no execution if the tab/world digest changes.
- **cost:** <$0.01 per staged form; one planner call dominates, deterministic browser inspection and relay storage are negligible.
- **security:** Never send page secrets to the pendant. Bind approval to tab/session, field digest, world fingerprint, nonce, expiry, and one-use counter. Treat approval as consent for that exact submission, not general browser authority; redact sensitive field values in speech/dashboard. Fail closed on changed DOM, expired lease, duplicate nonce, or missing delivery receipt.
- **missing:** relay implementation of the existing approval handoff store contract; a production caller from browser staging into prepare/approve; delivery of the staged nonce to the pendant and ingestion of its physical approval event; a real dashboard approve/status surface and separate least-privilege execution credential; browser post-submit verification and receipt correlation

### ""Why didn't I hear your last answer?" and then, if I say yes, diagnose and retry only the missing delivery."
- **useful because:** The owner gets an understandable answer to the real failure boundary—relay accepted it, bridge decoded it, or the speaker never started—instead of a generic retry. A confirmed retry can use the existing artifact without spending another model turn.
- **path:** pendant → relay → mac-bridge → mac-planner
- **model tier:** Deterministic telemetry join and policy first; cheap background summarization only when the evidence is ambiguous; no realtime generation unless the owner asks a new question.
- **latency:** Diagnosis spoken in under 2 s from the owner’s question; retry begins within 500 ms after confirmation and preserves the original artifact.
- **cost:** <$0.001 when telemetry is sufficient; storage and joins dominate, not inference.
- **security:** Use opaque artifact/session IDs and redact transcript text. Retry only an artifact explicitly bound to the owner’s current session, never an arbitrary previous recording. Refuse if privacy latch was active, the artifact expired, or delivery evidence is contradictory; do not silently replay sensitive content.
- **missing:** owner-facing route joining pipeline, relay job, and audio-delivery receipts by artifact ID; bridge receipt for playback start/finish/interruption correlated to the Opus stream; bounded relay retention of the last few generated artifacts with deletion/expiry; a confirmation action that cannot be mistaken for a new question

### ""Save that answer to my Mac as a note, with the exact source and time I heard it.""
- **useful because:** The pendant is the place the owner experiences the answer, while the Mac is the place that can retain and search it. This creates a deliberate, provenance-preserving memory bridge rather than silently storing conversation audio or relying on the owner to reconstruct it later.
- **path:** pendant → relay → mac-planner → mac-bridge
- **model tier:** Realtime only to acknowledge the request; deterministic artifact lookup and Apple Notes write; background model optional for a short title, never for the source text.
- **latency:** Confirm the target and create the note within 3 s. If the Mac is offline, queue a typed note request and report it on reconnect; never duplicate on retry.
- **cost:** <$0.001 per save; mostly Mac/relay I/O, with optional title generation under $0.001.
- **security:** Require a deliberate button/voice confirmation because this exports content to durable Mac storage. Include provenance (session, artifact ID, heard timestamp, source URL if any) but no raw audio unless separately requested. Deduplicate by artifact ID and honor the unresolved owner retention/deletion policy rather than inventing retention.
- **missing:** a signed pendant-to-relay save intent bound to one artifact; a relay-to-Mac durable handoff with idempotency and receipt; Apple Notes action that records source/provenance fields; owner-configurable retention/deletion policy before automatic cleanup

### ""Read the important parts of what I'm looking at" or "what does this chart mean?" while the relevant Safari tab is open."
- **useful because:** The pendant becomes an audio lens for the owner's authenticated browser: it can explain a chart, compare visible values, or read only the salient parts while the owner is away from the screen. This is more useful than a generic browser click because the answer is grounded in the exact tab the owner is viewing and can be heard hands-free.
- **path:** pendant → relay-realtime → mac-bridge → browser-extension → mac-vision
- **model tier:** Local Mac vision/OCR and a cheaper planner extract the page region and question context; realtime is used only to conduct the short spoken exchange. Send the minimum derived evidence to the relay, not the full page, unless the owner explicitly permits cloud vision.
- **latency:** Acknowledge in under 300 ms and speak a first useful finding within 3 s; charts or long pages may continue as a bounded background readout.
- **cost:** $0.002–$0.02 per query depending on whether local OCR/vision succeeds; cloud vision is the dominant cost and should be an explicit fallback.
- **security:** Bind capture to the active tab/session and show a visible browser indicator. Never inspect other tabs, password fields, or hidden DOM. Redact secrets locally; require confirmation before sending a screenshot or page text off the Mac. Expire the extracted evidence after the answer and record a provenance receipt without retaining page contents.
- **missing:** a typed active-tab visual-query command from pendant/relay to the browser extension; local OCR/chart extraction and a region-selection protocol; a privacy-preserving evidence envelope that distinguishes derived facts from raw page content; spoken answer delivery over the already-shipped pendant audio path; an owner setting for local-only versus cloud-vision fallback


## Changes it proposed to its own stack

### `relay` — Add a transport-neutral, signed turn checkpoint ledger shared by USB serial, LTE-M, and the Mac bridge. Each checkpoint records session nonce, monotonic turn number, last uplink frame, last downlink frame actually acknowledged by the bridge, transport owner, and expiry. Make claim/release compare-and-set and recover abandoned ownership after a short lease; resume only from a checkpoint whose replay safety is idempotent or additive.
- **owner gets:** If the cable is unplugged, the owner hears a clean pause and can continue on LTE (or return to USB) instead of losing the turn or hearing the answer twice.
- effort: Medium-high: relay schema/state machine, bridge acknowledgments, firmware USB event hooks, and fault-injection tests for detach during capture/playback.  ·  risk: A bad migration could duplicate audio or accept an old turn. Recover by requiring monotonic counters, signed session binding, lease expiry, and fail-closed cold restart when checkpoints are ambiguous; test with simultaneous uplink/downlink loss.
- cost: A few hundred bytes per active session and one small relay write per turn; no model cost.  ·  latency: Negligible steady-state; handoff adds up to one turn boundary and typically <2 s.
- security: Improves replay resistance, but checkpoint metadata is sensitive conversation linkage; encrypt at rest and retain only a bounded recent window.
- depends on: usb_fallback_audio_session; relay job lease/requeue work; bridge playback-start/finish acknowledgments; audio_delivery_ack_queue


## What it asked for

_Nothing._
## Its own summary

Round 162 produced four recorded proposals: turn-boundary conversation migration between USB/LTE/Mac; exact browser-form staging with pendant physical approval; owner-facing diagnosis and confirmed retry of an undelivered answer; and deliberate provenance-preserving save of a heard answer into Mac Notes. The most important connective work is still the missing durable handoff/approval wiring between already-live routes, not new model features. Fresh live discovery also changed a prior assumption: /ops/status now reports Accessibility and Screen Recording granted for AI Pendant Agent, browser online with 9 Safari tabs, relay reachable, and Mac bridge online. The pendant itself is not represented as relay-registered in the live device list, so USB is the immediate test path.

**Biggest unknown:** The physical pendant/ESP32 USB session is not exposed as a typed live device or receipt surface. I still need a verified serial-level turn/frame acknowledgment path and the owner's retention/deletion and personal-timezone policies before making durable-note retention or routine behavior automatic. The owner’s phone-companion and interruption policies also remain open decisions; I will not silently assume them.

