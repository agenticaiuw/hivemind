# Harness derivation — faculty-judgement — round 47

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Keep me from missing the one thing that matters today, but don’t interrupt me for everything.”"
- **useful because:** The owner currently has several independent daily routines and watches, but no life-level arbiter that merges duplicate findings, ranks consequences, and chooses whether to speak now, queue audio, or leave a Mac review item. This turns the pendant from a stream of alerts into a trusted attention filter.
- **path:** relay-realtime → unified → faculty-perception → faculty-judgement → faculty-action → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Use a cheap background model for scheduled collection, normalization, deduplication, and urgency scoring; use realtime only when the pendant must ask a one-sentence clarification or deliver an immediate alert. Use the Mac/browser for private authenticated evidence; relay stores only the resulting minimal event envelope.
- **latency:** Routine sources can settle within 5 minutes and be delivered in the next digest. A high-confidence deadline or account/security event should reach the pendant within 30 seconds. The owner gets one short sentence, with optional detail on request.
- **cost:** Roughly $0.01–$0.05 per daily run depending on number of private pages and transcript length; model tokens dominate. Public/static checks should use deterministic hashes and no model call.
- **security:** Private mail/calendar/browser content must stay on the Mac/browser bridge; relay receives category, urgency, deadline, and opaque source IDs by default. Never auto-send, delete, purchase, or submit. A dashboard must expose why an item was ranked, allow mute/snooze/correct, and retain a short audit trail.
- **missing:** A shared attention-event schema with source, consequence, deadline, confidence, and expiry; A deduplicating cross-routine merger that can collapse repeated calendar/mail/page-watch findings; A policy engine mapping urgency and owner availability to pendant-now, queued-audio, Mac notification, or silent archive; A correction loop so the owner's dismiss/snooze/“important” feedback changes future ranking without uploading raw private content

### "“Something went wrong with this account or purchase—build me the strongest case without sending anything.”"
- **useful because:** Today the owner can ask for a draft or a page reading, but cannot turn scattered private evidence into a defensible, chronological case. This capability would collect the relevant order/account page, confirmation mail, calendar entries, receipts and local files, detect contradictions, identify missing proof, and leave a reviewable claim packet with a draft appeal or support request. It saves the owner the exhausting work of reconstructing what happened while preserving their control over submission.
- **path:** relay-realtime → faculty-perception → faculty-judgement → mac-planner → browser-extension → mac-vision → mac-terminal → faculty-action → dashboard
- **model tier:** Use deterministic extraction and hashing first; use a background model to build the timeline, classify evidence, and draft the packet. Escalate to the expensive realtime tier only if the owner asks questions while reviewing it. A planner model should be used for ambiguous cross-source reconciliation, not routine OCR or deduplication.
- **latency:** For a bounded incident, produce an initial evidence index in 2–5 minutes and a draft packet within 10 minutes. The pendant should announce only that the packet is ready, in one short sentence; detailed evidence belongs on the Mac dashboard.
- **cost:** Approximately $0.03–$0.20 per incident, dominated by private-page extraction, OCR, and the final drafting pass. Hashing, date normalization, and duplicate detection should be local/deterministic and near-free.
- **security:** Evidence may contain financial, health, address, and account data. Keep raw pages, files, and screenshots on the Mac; send the relay only a job ID and progress state. Redact unrelated account numbers by default, show every source and quoted excerpt, preserve immutable source hashes, and require explicit approval immediately before any external submission or email. Never infer fraud or make legal claims as fact; label hypotheses and missing evidence.
- **missing:** A cross-source incident workspace that binds authenticated browser tabs, local files, mail, calendar, and receipts to one case without copying raw content to the relay; An evidence normalizer that preserves source URL/path, timestamp, excerpt, hash, and confidence while redacting unrelated secrets; A contradiction and missing-proof report that the owner can correct before drafting; A review UI with claim/evidence mapping, export to PDF/Markdown, and a hard submission gate


## Changes it proposed to its own stack

### `hardware` — Replace the prototype's 15,625-Hz I2S microphone/31,250-Hz playback clock arrangement with a clocked 24-kHz capture and 48-kHz playback path (or an audio codec that exposes both rates), and add a negotiated session format: native 24-kHz Opus when the relay and pendant have headroom, 16-kHz fallback otherwise. Keep the wire format and Opus sample rate identical end-to-end; do not silently resample 16-kHz uplink into a label that claims superwideband.
- **owner gets:** Speech will sound naturally full-range in both directions instead of having a 16-kHz narrowband microphone path paired with 24-kHz playback. The owner gets intelligible conversation in noisy places and graceful fallback rather than glitches when the tiny processor is overloaded.
- effort: Prototype: select a codec/I2S clock that supports 24/48 kHz, update Zephyr audio DMA and Opus encoder configuration, add SDP/session negotiation in relay, and run long-duration packet-loss/clock-drift tests. Product hardware revision is required; this cannot be made honest by relay transcoding alone.  ·  risk: A 24-kHz encoder plus decoder can exceed the current nRF9160's practical CPU budget (current decode is ~25.4 ms per 60-ms frame and encode ~15 ms, about 87% of one core when both run). Recover by negotiating 16 kHz before starting audio, using bounded jitter buffers, and dropping to comfort-noise rather than blocking the UI. Preserve the existing 16-kHz mode until the new path passes soak tests.
- cost: Prototype firmware/codec work is modest; a production audio codec and revised board are roughly $3–$10 BOM increase. More radio data and compute may add roughly 10–25% active audio energy, but avoids paying cloud transcoding and improves quality.  ·  latency: Negotiation adds less than one round trip before speaking; native 24-kHz frames can retain the current 60-ms packet cadence. A hardware codec/DMA path should reduce CPU contention and jitter compared with software resampling.
- security: No new private data leaves the device; negotiate only codec/rate metadata. Keep relay transcoding disabled for native 24-kHz sessions and make the selected rate visible in diagnostics so quality claims are auditable.
- depends on: A relay/session capability handshake that reports supported Opus sample rates; A firmware audio soak test measuring CPU, underruns, packet loss, and clock drift; A hardware revision or external audio codec with honest 24/48-kHz I2S support


## What it asked for

_Nothing._
## Its own summary

I added two owner-facing advances: (1) a life-level attention arbiter that merges duplicate calendar/mail/page-watch findings and chooses pendant-now versus queued audio versus Mac review, with explainable ranking and correction; (2) an honest negotiated native-24-kHz audio contract, including the hardware clock/codec revision and 16-kHz fallback needed because the current 15,625-Hz mic, 31,250-Hz wire clock, and ~87% combined CPU load cannot honestly deliver superwideband end to end. What I still need is not another idea: the shared attention-event schema/policy primitives, the actual audio acceptance criteria and session-handshake implementation status, plus the outstanding Mac Accessibility/Screen Recording and browser-bridge authorization so private evidence and GUI actions can be verified rather than queued.

**Biggest unknown:** Whether the orchestrator has now implemented the cross-surface event/persistence primitives and what exact 24-kHz audio measurements define acceptance; those determine whether the proposals can be reduced to an executable change list.

