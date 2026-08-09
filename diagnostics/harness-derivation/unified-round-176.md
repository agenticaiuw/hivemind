# Harness derivation — unified — round 176

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Run a wired pendant check, then tell me whether I can trust it for a call.” The Mac should use the physically connected nRF9160 and ESP32 bridge to run the existing bidirectional audio fixture, collect serial counters, optionally inject a bounded loss profile, and speak one owner-facing HEALTHY/DEGRADED/FAILED verdict with the failed acceptance criterion and a receipt."
- **useful because:** The hardware is physically present and LTE is not registered, so this gives the owner a useful answer today instead of pretending cloud health means wearable health. It catches codec, framing, bridge, and USB transport failures before a real conversation.
- **path:** pendant → mac-bridge → mac-planner → relay-realtime
- **model tier:** background
- **latency:** 30–90 seconds for the normal fixture; up to 3 minutes when the owner explicitly requests fault injection.
- **cost:** Low API cost; one short background orchestration and a few serial/test commands dominate, not realtime model tokens.
- **security:** Synthetic audio only by default; never records room audio. Fault injection must be opt-in and isolated to the test session. Speak only aggregate counters and retain the receipt locally unless the owner asks to upload it.
- **missing:** A Mac-bridge command that identifies both serial ports and runs the existing audio_path_diagnostic_fixture end to end; A typed result schema mapping fixture counters to HEALTHY/DEGRADED/FAILED; An owner-facing route that starts the test and returns a durable receipt

### "“Finish this booking/purchase, but wait for me at the last irreversible step.” The browser extension should stage the exact bound page action, the Mac should prepare a digest and world snapshot, the pendant should display pending and require its physical transaction approval, and only then should the browser submit; return a receipt that distinguishes staged, approved, submitted, and confirmed."
- **useful because:** This is the first genuinely safe way for the pendant to reach authenticated browser sessions without sending page secrets through the relay or making the owner approve a vague spoken description. It turns the physical approval latch into something the owner can actually use for consequential tasks.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-bridge
- **model tier:** background
- **latency:** Stage within a few seconds; pause indefinitely for the owner's physical approval; submit within 5 seconds after approval.
- **cost:** Low-to-moderate per task: planner/browser calls dominate, with a small background model call only for ambiguous page labels. No realtime tier needed.
- **security:** The relay carries only opaque transaction nonce, digest, expiry, and redacted labels; secrets and page contents stay in the browser. Require physical approval for off-machine, irreversible-write, and uncontained actions; refuse on digest/world drift, expiry, replay, or missing delivery receipt.
- **missing:** Wire the existing approvalHandoff/physical_transaction_approval_latch to relay persistence and browser command execution; A browser-side staged-submit protocol with digest and world fingerprint verification; A privilege boundary so approval is not equivalent to the Mac bearer token used for execution; A real delivery path that can present the pending challenge on the pendant during the next conversation

### "“Keep this conversation alive even if the network path changes.” Start on the wired pendant/ESP32 bridge through the Mac, migrate to LTE when available (or back to USB when LTE degrades), and preserve turn IDs, unfinished speech, and playback position so the owner hears neither a duplicate answer nor a gap without explanation."
- **useful because:** Today the pendant is testable over USB but unregistered on LTE. A turn-boundary migration would make the device useful now while making standalone LTE a later transport upgrade rather than a second product, and it directly protects the owner's conversation from modem or relay outages.
- **path:** pendant → mac-bridge → mac-planner → relay-realtime
- **model tier:** realtime
- **latency:** Detect loss within 1 second; migrate only at a turn boundary within 2 seconds, with a short spoken continuity cue if audio cannot be preserved.
- **cost:** Low incremental model cost; transport telemetry, Opus buffering, and duplicate suppression dominate. Realtime tokens are used only for the live conversation itself.
- **security:** Authenticate each transport with the same session nonce; never replay captured microphone frames after a handoff. Keep at most the current turn's bounded encoded buffer in volatile memory and discard it once the new path acknowledges the sequence.
- **missing:** A transport supervisor coordinating USB ownership, LTE registration, and bridge state; A relay session protocol with monotonic turn/frame IDs and idempotent handoff acknowledgements; Playback resume/duplicate suppression using the existing audio delivery acknowledgement queue; A migration test matrix covering simultaneous uplink/downlink loss

### "“Show me every promise you made that is still waiting on me.” The system should list commitments extracted from prior conversations, query only the explicitly bound Mac apps/tabs for evidence, and speak each as waiting, satisfied, or unable to verify—with no action taken automatically."
- **useful because:** The owner can currently make commitments in conversation and lose them among jobs, browser work, and reminders. A provenance-bound review turns the pendant into a reliable memory without pretending that absence of evidence means completion.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** background
- **latency:** A few seconds for the local index; evidence checks may take up to 15 seconds and should be resumable.
- **cost:** Moderate background-model cost for extracting and summarizing commitments; evidence queries and receipts dominate latency.
- **security:** Search only declared app/tab bindings, never the whole browser or filesystem. Preserve evidence URLs/timestamps, redact content in spoken output, and require confirmation before converting a waiting commitment into a reminder or action.
- **missing:** A durable commitment index with owner-visible provenance and expiry; A detector that emits candidate commitments rather than asserting they are true; A policy for bindings and retention, especially since the owner's retention/deletion policy is still unspecified

### "“Start a meeting companion.” After an explicit start gesture, the pendant marks the meeting, the Mac/browser captures only the selected meeting tab or app, the relay produces a speaker-labeled transcript and action-item list, and the owner can later ask the pendant “what did I agree to?” without recording outside the active session."
- **useful because:** The owner gets reliable meeting memory without an always-on microphone or ambient recording. The pendant supplies deliberate physical start/stop and the browser supplies the authenticated meeting context that the relay cannot reach by itself.
- **path:** pendant → mac-bridge → mac-planner → browser-extension → relay-realtime
- **model tier:** background
- **latency:** Start/stop acknowledgement under 2 seconds; transcript and action items available within 1–3 minutes after the meeting.
- **cost:** Moderate background transcription and summarization cost proportional to meeting duration; no realtime model needed except short control speech.
- **security:** Capture is strictly opt-in and bounded to a selected app/tab. Show an active LED/state indicator, retain raw audio only for the configured processing window, redact secrets before relay upload, and require confirmation before creating reminders or sending follow-ups.
- **missing:** An explicit meeting-session state machine bound to the pendant’s physical start/stop; A browser/Mac capture adapter that identifies the selected meeting source and speaker metadata; A retention and deletion policy for transcripts and derived action items; A query route joining meeting artifacts to commitment evidence

### "“Before you upload or send this, show me exactly what private information will leave my devices.” The Mac/browser should compute a local outbound-data manifest, the relay should classify destinations and sensitivity, and the pendant should read a compact redacted summary; the owner can approve only the specific fields and destination, not a vague whole job."
- **useful because:** The owner can use the system’s powerful browser and Mac access without having to trust an opaque automation step. It makes privacy understandable at the moment data crosses from a local authenticated session to an external destination.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → mac-bridge
- **model tier:** background
- **latency:** Manifest in under 3 seconds for a single form/message; up to 10 seconds for a multi-file upload.
- **cost:** Low-to-moderate background classification cost; local extraction and hashing dominate for large payloads.
- **security:** Sensitive values must be classified locally where possible and never sent to the relay in raw form. Show destination, field names, sizes, and hashes rather than secrets. Approval must expire if the page, destination, or payload changes.
- **missing:** A local outbound-data manifest extractor for browser forms, attachments, and Mac messages; Destination identity and sensitivity policy; Field-level approval rather than action-level approval; A redacted spoken rendering that remains useful without leaking the very data being protected

### "“Give me a private, local-only answer.” The pendant should establish a session whose audio, transcript, model request, and result remain on the Mac and connected hardware; the browser bridge must be unavailable during that session, the relay must receive only a session status receipt, and the pendant must clearly indicate local-only mode."
- **useful because:** The owner sometimes needs the assistant precisely when sending data to a cloud relay is unacceptable. This provides a useful privacy mode rather than merely muting the device, while still allowing the Mac and pendant to cooperate over the currently available USB connection.
- **path:** pendant → mac-bridge → mac-planner → relay-realtime → browser-extension
- **model tier:** realtime
- **latency:** Conversation latency comparable to the normal wired session; enter/exit confirmation under 2 seconds.
- **cost:** Potentially higher local compute cost and no relay-token cost; depends on a local speech/model stack, with the Mac doing the expensive work.
- **security:** Enforce network egress at the Mac process/session boundary, not by convention. Disable browser actions and relay uploads, encrypt or purge temporary audio/transcripts, and make the LED/state receipt explicit. If local inference is unavailable, refuse rather than silently falling back to cloud.
- **missing:** A local speech/model execution path with bounded memory and audio handling; A session-level egress firewall or network sandbox for the Mac agent; A pendant-visible local-only state and authenticated enter/exit receipt; Tests proving browser and relay paths cannot receive content during the session


## Changes it proposed to its own stack

### `integration` — Add a signed, monotonic 'privacy convergence receipt' protocol: the pendant emits latch generation and local capture/playback state; relay, Mac bridge, and browser each attest their own stopped/exposed state; the relay stores only the compact receipt and computes PASS, FAIL, or UNKNOWN. Any missing or stale attestation is fail-closed.
- **owner gets:** When the owner long-presses privacy, they can know—not merely hope—that audio stopped everywhere and that an in-flight browser or relay operation is not still exposing it.
- effort: Medium: define a small receipt schema, implement read-only attestations on each surface, and add integration tests for dropped links and stale jobs.  ·  risk: False UNKNOWN may be inconvenient but is safer than false PASS. Recover by retrying attestations; never weaken the latch or delete evidence automatically.
- cost: Negligible storage and API cost; one small receipt per latch transition.  ·  latency: No impact on local mute response; convergence check typically adds 1–5 seconds.
- security: Improves fail-closed privacy and provenance. Must avoid putting raw audio, page content, or secrets in receipts.
- depends on: local_privacy_latch; privacy_convergence_check; relay persistence for per-surface attestations


## What it asked for

_Nothing._
