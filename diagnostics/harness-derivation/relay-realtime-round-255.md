# Harness derivation — relay-realtime — round 255

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Only interrupt me on the pendant when something is both urgent and actionable; otherwise hold it, group related updates, and tell me during my next check-in.”"
- **useful because:** Every alert currently competes with the owner's attention or is invisible until they ask. A cross-surface attention policy would let the worn device protect concentration while still catching a real deadline, security event, or human escalation. The relay would combine browser watches, Mac state, and calendar/mail signals, deduplicate them, and explain why it interrupted.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Use a cheap background classifier for urgency/actionability and deterministic grouping; reserve relay-realtime for the actual interruption sentence and the owner's clarification. Use mac-planner or browser-extension only to collect the event and its source, not to decide independently.
- **latency:** Critical events should reach the pendant within 15 seconds of detection; noncritical events can wait for a scheduled digest or explicit check-in. The owner should hear one sentence, with a button press for details.
- **cost:** About $0.01–$0.05 per event batch; polling and event normalization dominate, while classification can run on a low-cost model. Audio delivery is negligible compared with inference.
- **security:** Mail and authenticated pages may be sensitive. Store only source URL/app, urgency rationale, and a short redacted summary; never expose full message bodies in an unsolicited spoken alert. Require explicit opt-in per source and provide a physical mute gesture. The system must distinguish “could not check” from “nothing urgent.”
- **missing:** A unified event-ingestion adapter for Mac notifications, browser watches, and local relay jobs.; A durable per-owner attention policy with quiet hours, escalation rules, and deduplication state.; A live trigger/worker path that evaluates events without an active voice turn; existing routines and watches provide shapes but not this cross-source arbitration.; A pendant inbox delivery endpoint wired to the already-implemented offline alert inbox.

### "“When you tell me something you learned from my Mac or a signed-in page, let me ask ‘why?’ and hear the exact source, timestamp, and the short evidence behind it—not just your conclusion.”"
- **useful because:** A spoken conclusion is hard to trust when the owner cannot see the screen. Evidence-on-demand makes remote assistance auditable without forcing every answer to become a long citation recital. The relay keeps a compact chain from spoken claim to the Mac window, browser URL, extracted text, and capture time; a button press or “why?” surfaces only the relevant proof.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Use deterministic provenance records and retrieval first. Use relay-realtime only to explain the selected evidence in one or two spoken sentences; use a cheaper model offline to compress long page excerpts. Never ask the realtime model to invent citations.
- **latency:** Normal answer remains under 3 seconds after the underlying job. A “why?” response should be under 2 seconds from stored provenance; fetching a missing source may take up to 10 seconds and must be announced.
- **cost:** $0.005–$0.04 per explanation, dominated by optional excerpt summarization; storage and indexing are the main engineering costs, not model calls.
- **security:** Sources can contain secrets. Keep full excerpts on the originating Mac/browser surface, send only a minimal redacted span to the relay, bind provenance to the owner session, expire it with the job, and refuse to read passwords or hidden fields aloud. A source link alone is not evidence if the page has changed, so retain hash and capture timestamp.
- **missing:** A provenance schema attached to every browser/Mac observation and spoken claim, including source surface, locator, capture time, content hash, and redacted excerpt.; A relay retrieval route that can select evidence by claim ID during a live turn and deliver a short response to the pendant.; Mac/browser capture adapters that return stable locators rather than only final text.; A small pendant gesture or spoken command mapping for “why/source/again.”

### "“During a meeting, quietly tell me on the pendant when my name, a decision I own, or a direct question is detected—and after the meeting give me only my commitments.”"
- **useful because:** The pendant can be a private attention channel instead of another screen. The Mac can hear the meeting and maintain a transcript while the relay handles low-latency, owner-specific cues; the owner does not need to keep looking at a laptop or share the whole transcript aloud. The post-meeting commitment list turns passive transcription into something actionable.
- **path:** pendant → relay → mac-planner → mac-vision
- **model tier:** Run VAD, speaker/name matching, and transcript chunking locally on the Mac where possible. Use a cheap background model to classify questions/commitments; use relay-realtime only to phrase an urgent one-sentence cue. Use the expensive tier for ambiguous references or a final commitment summary, never for every audio frame.
- **latency:** A cue within 2 seconds of a detected question or assignment. End-of-meeting commitments within 30 seconds after the owner presses stop. If confidence is low, say “possible question” rather than asserting it.
- **cost:** $0.05–$0.40 per meeting depending on duration and whether local transcription is available; continuous transcription is the dominant cost. A low-rate relay channel and short cues add little.
- **security:** Meeting audio may include other people and confidential material. Default to on-device capture/transcription, upload only short feature-bearing excerpts when confidence requires it, show a visible Mac recording indicator, require the owner to start/stop with the pendant, encrypt and auto-delete raw audio/transcript after the commitment summary, and never silently record after release or outside the explicit session.
- **missing:** A Mac meeting-audio capture/transcription adapter with explicit start/stop and local retention controls.; A streaming low-latency event channel from Mac to relay for classified cue events, separate from the normal voice turn.; A commitment ledger that stores speaker attribution, confidence, evidence timestamp, and owner acknowledgement.; A pendant notification path that can play a brief cue without interrupting a response, while respecting its one-button/one-LED interaction model.; A model-routing policy that keeps continuous meeting audio off the expensive realtime tier.

### "“Let me start a conversation while the pendant is plugged into my Mac, walk away, and keep talking over LTE without losing the turn or hearing the reply twice.”"
- **useful because:** The hardware is physically testable over USB today, but the owner wears it away from the Mac and the LTE device is not yet registered. A session that migrates between USB serial and LTE would make the pendant feel continuous rather than like two unrelated devices: begin with low-latency local transport, roam out of range, and resume with the relay retaining exactly-once audio and conversation state.
- **path:** pendant → relay → mac-planner
- **model tier:** Keep migration, packet deduplication, and replay deterministic in firmware/relay. Use relay-realtime for the conversation only; do not spend model calls to reconcile duplicate packets. Use a cheaper background worker to close abandoned sessions and produce a short recovery notice.
- **latency:** Link migration should pause audible speech for less than 1 second when both transports are available. If LTE registration takes longer, the pendant should give a local status cue and resume automatically when authenticated; no duplicate sentence or lost user utterance is acceptable.
- **cost:** Negligible model cost; engineering and LTE data dominate. Expect a small per-session control overhead and normal audio data charges once LTE is used.
- **security:** Bind both transports to a device key and monotonically increasing session/packet sequence. Reject replayed USB or LTE frames, rotate session keys on migration, and do not fall back to an unauthenticated serial command channel for actions. Retain only the minimum handoff metadata and obey the existing SD failure-only audio rule.
- **missing:** Real LTE registration and a tested pendant-to-relay data path; today the nRF9160 and ESP32 are USB-connected but the pendant is not registered.; A transport abstraction in firmware exposing one ordered stream above USB serial and LTE-M.; Relay-side session migration with exactly-once packet acknowledgement, replay protection, and audio sequence reconciliation.; A migration-aware audio pipeline that can resume 24 kHz/60 ms Opus framing without resetting the conversational turn.; A device status/diagnostic event that tells the owner whether the link is local, LTE, or in handoff.


## What it asked for

_Nothing._
## Its own summary

Discovered current categories, tools, devices, hardware, and routes. The relay has job status reading available (relay_job_status) and a job completion watch that resolves to GET /jobs/:jobId. A push-style completion notification tool exists only as a schema and does not resolve to a real endpoint. Devices show the Mac bridge online; the wearable is connected via the Mac bridge rather than relay-registered LTE. The stack exposes many Mac routes, including routines and pipeline endpoints, but the relay still lacks a self-inventory route equivalent to the Mac’s /capabilities.

**Biggest unknown:** How the relay should deliver and persist post-session completion notifications (to pendant/phone/dashboard) in a way that is actually implemented, given that relay_event_push is unresolved and there is no confirmed relay-side notification delivery path.

