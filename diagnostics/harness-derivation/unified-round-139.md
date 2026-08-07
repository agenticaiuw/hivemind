# Harness derivation — unified — round 139

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Start a private meeting capture.” When I press the pendant button at the start and end, use the Mac microphone/connected pendant to capture the conversation, identify decisions and commitments, cross-check names and dates against my Calendar and logged-in browser, and leave me a cited summary plus draft reminders—never send or share anything."
- **useful because:** The pendant supplies an unmistakable physical privacy boundary and the Mac/browser supply calendar and project context; neither alone can turn a real conversation into reliable follow-through without guessing. It saves the owner from reconstructing commitments after meetings while keeping publication under review.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Realtime only for button-state and live utterance segmentation; a cheaper background model extracts decisions after capture and a small deterministic pass resolves calendar entities.
- **latency:** Button acknowledgment under 300 ms; no need for live full transcription. End-of-meeting spoken confirmation under 10 s, with the cited workbench ready within 60 s.
- **cost:** Roughly $0.02–$0.15 per 30-minute meeting depending on audio transcription volume; storage and browser/Mac time dominate, not realtime reasoning.
- **security:** Raw audio and transcripts are sensitive and should remain on the Mac by default, with only redacted excerpts sent to the relay/model. The physical start/stop gesture must gate capture, show the pendant LED state, and auto-delete audio after extraction unless the owner explicitly keeps it. Calendar/browser access is read-only; reminders remain drafts requiring approval.
- **missing:** A local USB meeting-capture controller that can start/stop and expose an unambiguous recording indicator; Mac audio capture and diarization/transcription route with retention controls; Calendar/browser entity citation joiner; A review UI showing source timestamps before creating reminders

### "“Tell me what needs me now, not everything that happened.” The relay should combine pending Mac jobs, browser changes, calendar deadlines, and pendant-captured interruptions into one urgency-ranked queue, then speak only the top item when I ask or tap twice; each item must say why it is urgent, what source proves it, and what the next reversible step is."
- **useful because:** Today these surfaces produce separate briefings and job receipts, forcing the owner to be their own dispatcher. A single queue makes the worn device useful in the moment while preserving the Mac/browser evidence needed to avoid false urgency.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Background model periodically ranks and deduplicates signals; realtime only renders the already-ranked top item and accepts a short dismissal/snooze command.
- **latency:** Queue refresh within 2 minutes of a source event; double-tap response under 500 ms; spoken item under 15 s.
- **cost:** Under $0.01 per refresh with event-driven extraction and a small ranking model; realtime usage is limited to explicit taps.
- **security:** The queue must not leak secret browser content through an unattended pendant. Require an owner-presence gesture for sensitive items, redact notification text by default, and retain source pointers rather than copying page bodies. Dismiss/snooze must be reversible and logged.
- **missing:** A cross-surface event normalizer for jobs, watches, calendar and capture records; Urgency/deduplication policy with owner-tunable quiet hours; Pendant double-tap/LED queue interaction; A dashboard queue with evidence and snooze controls

### "“When I plug in the pendant, prove the whole voice path works.” Run a guided 60-second USB acceptance test: exercise the nRF9160 mic/button/LED, ESP32 Bluetooth bridge, Mac serial links, relay audio loop, and playback; report measured round-trip latency, packet loss, clipping, and battery draw in a dated receipt, and refuse to call the device ready if any threshold fails."
- **useful because:** The owner can test the actually-worn hardware today over USB instead of discovering a silent microphone or broken Bluetooth path during a real conversation. A single pass/fail receipt makes hardware confidence tangible and catches regressions across chips, Mac, and relay.
- **path:** pendant → mac-terminal → relay-realtime → dashboard
- **model tier:** Deterministic firmware test vectors and signal measurements first; a cheap text model turns the receipt into plain language. No realtime model is needed except an optional spoken result.
- **latency:** Start within 2 s of USB insertion; complete in 60 s; spoken result within 3 s of completion.
- **cost:** Negligible API cost (<$0.01/run); local CPU, Bluetooth test audio, and a small relay echo payload dominate.
- **security:** Use synthetic test tones and discard captured audio. Never connect to the owner's live headphone output without explicit consent. Store only aggregate metrics, firmware hashes, and failure snippets; serial identifiers should be access-controlled.
- **missing:** USB serial discovery and coordinated test protocol for both connected chips; Firmware diagnostic commands for deterministic tone, loopback, LED/button, packet counters and power sampling; Relay echo endpoint and calibrated acceptance thresholds; A durable receipt view and optional pendant spoken verdict

### "“If my flight, appointment, or delivery is disrupted, recover the day for me.” Monitor the logged-in reservation and tracking pages, correlate a disruption with my Calendar and current location/time on the Mac, find feasible alternatives, and present one spoken recommendation on the pendant. If I approve with the pendant, rebook or reschedule through the browser, update Calendar, and leave an evidence-backed receipt; never commit a paid change without that physical approval."
- **useful because:** The owner currently has separate browser checks, calendar access, and reminders, but no system that can reason across a real disruption and carry the recovery through to completion. This is a high-value failure case where the worn device can authorize a consequential action while the browser reaches private accounts and the Mac supplies local schedule context.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Background monitoring and alternative search use a cheaper model; realtime is reserved for the short approval conversation and spoken recommendation. Deterministic policy checks validate price, timing, and required fields before submission.
- **latency:** Detect within 5 minutes of a watch/event update; produce alternatives within 60 seconds; pendant approval response under 500 ms; browser commit and receipt within 2 minutes.
- **cost:** Approximately $0.03–$0.20 per disruption, dominated by authenticated page reads and alternative searches; routine polling should be event-driven and use a low-cost model.
- **security:** Reservation, location, and identity data are highly sensitive. Keep page content on the Mac where possible, send only extracted alternatives to the model, require a fresh physical approval bound to the exact before/after itinerary and total price, expire approval after 2 minutes, and provide an immediate undo/cancel path where the provider supports it.
- **missing:** A disruption correlator joining authenticated page watches, Calendar events, and local time/location without copying full page contents; A provider-aware alternative-ranking and fare/penalty validator; A physical pendant approval token bound to an immutable transaction preview; Browser transaction execution with provider-specific confirmation and durable before/after evidence; A recovery policy for partial commits, provider timeouts, and duplicate submissions

### "“Reconcile this expense for me.” From a receipt I mention on the pendant or a photo/PDF on the Mac, find the matching transaction and calendar event across my logged-in accounts, classify it under my expense rules, fill the reimbursement form, and read me the exact amount and destination before I approve submission with the pendant."
- **useful because:** The owner should not manually reconcile receipts, card transactions, and calendar context across disconnected surfaces. The pendant gives a simple approval boundary while the browser can reach the private expense portal and the Mac can inspect local receipts.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Cheap background extraction and deterministic matching first; realtime only for clarification and final spoken confirmation.
- **latency:** Find matches in under 30 seconds for a single receipt; approval prompt under 2 seconds after the preview is ready; submit within 60 seconds of approval.
- **cost:** About $0.01–$0.08 per receipt; OCR and authenticated portal interaction dominate.
- **security:** Financial data must stay minimized and encrypted. Never infer a reimbursement destination silently; show amount, category, payee, and destination, require a fresh button approval bound to that preview, and retain an auditable source trail without storing full receipts indefinitely.
- **missing:** Local receipt/OCR ingestion with provenance; Cross-account transaction matching and confidence thresholds; Expense-policy validator and portal-specific form adapter; Physical approval bound to amount and destination; Partial-submit recovery and duplicate prevention

### "“Find the thing I was looking at.” Use my spoken description, recent pendant audio markers, open Safari tabs, Mac documents, and recent agent jobs to resolve the exact artifact or page I mean, then bring it to the front and tell me why it matched. If there are multiple plausible matches, ask one focused question instead of guessing."
- **useful because:** Human memory is referential—“that invoice,” “the chart from yesterday”—but today each surface loses the others’ context. Joining recent private browser state, local files, and the owner’s spoken markers would make the pendant a practical memory interface rather than a command-only remote.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** A small retrieval/reranking model over metadata and short snippets; realtime only handles the spoken reference and clarification. Never send full documents unless retrieval requires it.
- **latency:** Resolve a single reference within 5 seconds; open the selected page/file within 3 seconds; clarification should be one turn.
- **cost:** Less than $0.01 per lookup with local indexing and compact metadata; occasional embedding/index maintenance is the main cost.
- **security:** Index private browser and document metadata locally, partition by source, and expose only the winning snippet and provenance. Do not search secrets by default; require a deliberate “search everywhere” phrase and log the selected source.
- **missing:** A unified local temporal index for pendant markers, Safari tabs, files, jobs, and citations; Stable artifact IDs that survive tab reloads and file moves; A privacy-aware retrieval policy and ambiguity threshold; Mac/browser bring-to-front action with source explanation


## Changes it proposed to its own stack

### `integration` — Implement cable-presence pairing as a short-lived, hardware-bound capability: when the nRF9160 and ESP32 serial identities are simultaneously present, the Mac agent performs a nonce challenge over both ports, displays a six-word confirmation on the Mac, and asks for one physical pendant-button press. The relay then mints a scoped session token limited to this pendant, Mac, browser extension, and audio pipeline; unplug, timeout, or a second button hold revokes it. Persist only public device IDs, token expiry, and an audit receipt—not raw serial traffic.
- **owner gets:** The owner can securely bring the real wearable online today just by plugging it in and pressing once, without copying pairing codes or leaving a permanently trusted device behind. It also makes a stolen pendant, browser session, or relay token less useful on its own.
- effort: Medium: serial challenge firmware on both boards, Mac coordinator, relay token endpoint, extension handoff, and a small pairing UI.  ·  risk: A dropped USB link during pairing could strand a half-issued token; make issuance transactional and expire incomplete ceremonies after 60 seconds. A lost pendant button or duplicate serial IDs require a Mac-side recovery/unpair action. Do not silently pair on cable insertion.
- cost: Near-zero API cost; one relay D1 write per pairing. Firmware flash and roughly 1–2 kB RAM per challenge state.  ·  latency: 10–30 seconds for first pairing, then no conversational latency impact; revocation should propagate within 5 seconds.
- security: Improves security by binding trust to physical presence and short-lived scope. It introduces a nonce/token implementation that must use a cryptographic RNG, prevent replay, and avoid exposing device secrets in logs.
- depends on: USB serial access to /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A relay endpoint for scoped multi-surface session tokens; Browser extension support for receiving and revoking the scoped session; A firmware diagnostic/identity command on each board


## What it asked for

### `s14-pb96` (skill) — physical_usb_pairing_ceremony
- does: While USB-connected, exposes a signed device identity and nonce challenge, shows pairing state through the single LED, and requires one deliberate button press to authorize the Mac/relay session. A long hold cancels and revokes the local session. It never emits microphone audio during the ceremony.
- must be on-device because: The server cannot establish that the owner is physically present or distinguish a genuine pendant from a replayed serial client; the button, LED, and device identity are local hardware facts and must remain safe if the relay is unreachable.
- trigger: USB serial connection followed by a Mac-issued challenge; button press or long hold on the pendant.
- storage: Public device identity and an anti-replay counter in protected flash; transient nonce and state in RAM. Under 256 B persistent data and under 128 B RAM.
- RAM budget: ~128 B state plus existing serial buffers; well below the 211,608 B application RAM budget, with no audio buffers allocated.

## Its own summary

Round 139 produced three owner-facing capabilities and one stack change. New proposals: button-bounded private meeting capture with cited follow-up drafts; a cross-surface urgency queue spoken only on an explicit pendant gesture; and a USB-started whole voice-path acceptance test with measured pass/fail receipts. Also proposed hardware-bound cable-presence pairing and queued the required pendant firmware skill for nonce/button/LED authorization. Live discovery confirms the Mac bridge, Safari extension, relay, and both prototype chips are real, but the pendant is still not relay-registered; Accessibility and Screen Recording remain unavailable. The proposal recorder flagged the first two as close to existing meeting/offline-digest ideas, so the genuinely distinct new work is the physical USB test and cryptographic pairing ceremony.

**Biggest unknown:** Whether the orchestrator will grant the missing implementation surfaces: coordinated dual-USB serial access, firmware diagnostic/identity commands, relay echo/scoped-token endpoints, and a durable acceptance/pairing receipt. I still need the owner’s explicit privacy/retention policy for meeting capture before treating that capability as safe to implement.

