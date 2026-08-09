# Harness derivation — faculty-perception — round 151

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-observability-2026-08-08** — At 2026-08-08T02:10Z, Mac agent is fully ready: Accessibility and Screen Recording granted, inputReachability verified, browser extension online with 9 Safari tabs, relay reachable and D1-backed; no pendant appears in the live device inventory (only Mac bridge online and mobile offline).
  - evidence: GET /ops/snapshot and GET /observe returned 200; /ops/snapshot status.permissions.ready=true, inputReachability not in snapshot but /observe says verified, browser online=true, relay.payload.store=d1; discover devices lists only home-macbook-bridge and cloudflare-contract-test.
- **existing-watch-capability** — GET /watches is live and already stores structured URL/field/pattern watches with interval scheduling, observed/previous values, checkCount/changeCount, and enabled state. The only visible watch is UTC clock and it is disabled.
  - evidence: describe GET /watches returned liveStatus 200 and watch wch_ccdecb34-2963-46b9-bb04-13bac50e66f4 with 15-minute schedule, structured fields, and enabled:false.

## Capabilities it proposed

### "Keep an eye on this page and tell me only when something important changes."
- **useful because:** The owner can delegate a live web watch while they work; the browser holds authenticated state, the Mac can inspect the actual tab, and the relay can evaluate changes while the owner is away. It avoids repeatedly reading pages and produces a concise, grounded alert only on material change.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → unified
- **model tier:** Use a cheap scheduled/background model for periodic extraction and diff classification; reserve realtime for delivering an alert or answering follow-up.
- **latency:** Initial capture under 3 seconds; polling every 5–15 minutes; alert delivery under 10 seconds after a detected material change.
- **cost:** Roughly $0.01–$0.05 per watched page per day depending on polling frequency; browser capture and hashing dominate, with model calls only for semantic diffs.
- **security:** Authenticated page text stays on the Mac unless the owner explicitly authorizes relay analysis; redact secrets and form fields before sending diffs. Require confirmation before turning a detected change into any external action.
- **missing:** A durable watch record with URL/tab/session affinity, cadence, last content hash, and owner-approved notification policy; A browser-to-Mac capture result that emits a content hash and grounded provenance on every poll; A relay scheduler trigger and deduplicated announcement path for material changes

### "Before I send this, check the open browser tab, verify the recipient and amount, and ask me once if anything does not match."
- **useful because:** This is the single most useful safety behavior: it combines the browser's private authenticated session, Mac vision/accessibility, relay judgement, and the pendant's explicit confirmation channel so a plausible-looking draft cannot silently become a purchase, message, or transfer.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → pendant → unified
- **model tier:** Cheap deterministic extraction first (DOM/accessibility labels, URL and field values); use a stronger model only for ambiguity; realtime is used only for the final one-sentence confirmation.
- **latency:** Verification in 2–5 seconds; never send until the owner confirms. If the browser or pendant is offline, fail closed and show the mismatch on Mac.
- **cost:** About $0.01–$0.08 per verification; most cases are deterministic, while vision/model reasoning dominates ambiguous pages.
- **security:** Never upload passwords, payment numbers, or full page text. Hash and redact sensitive fields, bind the verification to tab/session and a short expiry, and require a fresh owner confirmation for changed recipient, amount, or destination. Destructive and financial actions remain confirmation-gated.
- **missing:** A signed, short-lived verification capsule linking the inspected tab, extracted fields, and intended action; A policy engine that classifies recipient/amount/destination mismatches and prevents execution; A pendant confirmation message with nonce binding and replay protection

### "Tell me when a commitment I made changes anywhere—email, calendar, or an authenticated web page—and show me exactly what changed before suggesting what I should do."
- **useful because:** The owner currently has separate reminders, routines, browser reads, and briefings, but no commitment-level view. This would catch a rescheduled appointment, changed deadline, or altered reservation even when the source is private and the owner is away, while keeping judgement separate from action.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → unified
- **model tier:** Use a cheap background extractor to normalize dates, parties, obligations, and status; use a stronger model only when two sources conflict. Realtime is reserved for the short alert and follow-up.
- **latency:** Source polling every 15–30 minutes; alert within 2 minutes of a material change; immediate local detection for an open tab.
- **cost:** Approximately $0.02–$0.10 per day for a modest set of watched sources; semantic conflict resolution dominates. Raw private content should remain local whenever possible.
- **security:** Email and authenticated pages may contain secrets. Extract locally into minimal commitment records, transmit only redacted deltas and source fingerprints, and require confirmation before creating, changing, or cancelling anything.
- **missing:** A local commitment entity model with source, deadline, confidence, change history, and supersession links; Connectors that can extract structured commitments from Mail, Calendar, browser sessions, and private pages without sending bodies to the relay; A cross-source conflict resolver and owner-facing change receipt with exact before/after values

### "Keep working on this while I’m away, and when I return give me only the decisions that require me—not a transcript and not a pile of alerts."
- **useful because:** Today background routines, browser work, Mac jobs, and relay announcements can each complete, but they do not converge into a bounded decision queue. The owner should return to a small set of actionable choices with evidence, stale work removed, and no duplicate interruptions.
- **path:** relay-realtime → mac-planner → mac-terminal → browser-extension → mac-vision → pendant → unified
- **model tier:** Use a cheap background planner and deterministic job monitor for long-running work; invoke the expensive model only to merge conflicting results into a decision packet. Realtime is only for the return handoff.
- **latency:** Start work in under 5 seconds; background tasks may run for hours; return digest assembled in under 10 seconds from stored receipts.
- **cost:** $0.05–$0.50 per multi-step assignment depending on browser and research calls; model summarization and repeated authenticated-page reads dominate.
- **security:** The owner must define what the system may do autonomously versus merely draft. Keep a per-task budget, deadline, and allowed domains; never send, buy, delete, or submit without confirmation. Store evidence references rather than raw private page bodies and expire stale decision packets.
- **missing:** A durable task contract containing objective, allowed actions, budget, deadline, stop conditions, and owner-confirmation requirements; A decision-packet store that joins Mac job receipts, browser provenance, research outputs, and relay state while collapsing duplicates; A return-time handoff trigger that knows the owner is available and can deliver one bounded packet through the available surface

### "Remember this moment so I can ask about it later—what I said, what was on my screen, and which browser page it came from—and let me revoke it if I change my mind."
- **useful because:** The owner currently has isolated capture, browser evidence, and context-graph mechanisms, but no single owner-visible memory event tying speech, screen state, and authenticated-page provenance together. This would make 'remember this' reliable instead of requiring the owner to reconstruct the moment later.
- **path:** pendant → relay-realtime → mac-vision → browser-extension → mac-planner → unified
- **model tier:** Use realtime only to recognize the short capture command; local deterministic capture and hashing do the rest. Use a cheaper background model to produce a searchable summary and entity links.
- **latency:** Begin capture within 500 ms of the command; seal the memory event within 3 seconds after speech ends; retrieval under 2 seconds.
- **cost:** Usually under $0.02 per memory event; local screen/browser capture dominates latency, while optional summarization is the main API cost.
- **security:** Screen and speech can contain passwords, financial data, or other people. Require an explicit capture phrase, redact sensitive controls locally, never upload raw audio unless configured, encrypt the local body, expose source/capture time prominently, and make revocation erase or tombstone every linked derivative.
- **missing:** A single memory-event record joining audio transcript, screen snapshot, browser capsule, timestamp, active app, and owner-provided label; A voice-triggered local capture transaction with a short pre-roll and atomic sealing across Mac and pendant; Search and revocation fan-out across capture, evidence, provenance, and context-graph stores


## Changes it proposed to its own stack

### `interaction` — Add a cross-surface interruption governor. The Mac agent samples foreground app, secure-input state, active browser tab, and current computer-use job; the relay assigns each pending announcement an urgency and expiry; the browser bridge reports whether the owner is actively typing. Non-urgent speech is held while secure input, a destructive form, a meeting/video app, or an active computer-use step is detected, then released as one deduplicated summary when the state becomes safe. The pendant's offline-reality-beacon health frame is used only to avoid claiming delivery when it is absent.
- **owner gets:** The system stops talking at the worst possible moment and stops interrupting an in-progress purchase or message. When the owner is free, they get one short catch-up instead of a burst of stale alerts.
- effort: Medium: a Mac context sampler and policy endpoint, relay-side announcement arbitration, and a small browser heartbeat field. Existing observation and announcement records can carry most state; new tests must cover crash/restart and expiry.  ·  risk: A false busy signal could delay a time-sensitive alert. Preserve a hard emergency class, show held-item counts in the dashboard, and expire ordinary items rather than replaying stale speech. If the relay is unreachable, the Mac should locally suppress only low-priority audio and never block actions.
- cost: Negligible API cost; one low-rate local sample and a few relay state writes per announcement. No hardware cost.  ·  latency: Adds at most one local sample interval (1–2 seconds) before speaking; summary release should be under 2 seconds after the owner becomes available.
- security: Foreground app names and browser activity are sensitive. Keep raw titles local, send only policy booleans and urgency classes, and bind any browser-derived state to the existing session pseudonym.
- depends on: A defined urgency taxonomy for announcements and an owner-configurable emergency bypass; A durable, bounded held-announcement queue with explicit expired/superseded states; A real device playback acknowledgement before the UI labels anything heard; until then say queued or socket-delivered only

### `integration` — Add a USB bench mode that makes the physically connected nRF9160 and ESP32 testable as a first-class local device without pretending they are LTE-registered. The Mac bridge should enumerate the two serial ports, stream firmware health/audio counters into a namespaced local device record, optionally tunnel the nRF WebSocket over the relay, and mark every result as usb-bench rather than online-pendant. A single test command should run a 24 kHz round trip and emit a signed receipt with firmware build, packet counters, and measured playback completion.
- **owner gets:** The owner can actually wear/test the hardware on the desk today and know whether a failure is firmware, USB/audio bridge, relay, or absent LTE registration. It turns the currently invisible pendant into a verifiable bench device without reporting a false cloud presence.
- effort: Medium-high: serial framing and port discovery, a local-to-relay device identity, test orchestration, and dashboard labeling. Do not merge bench telemetry into the production pendant registry.  ·  risk: A serial disconnect or stale health frame could be mistaken for live health. Use monotonic sequence numbers, explicit USB connection state, and a hard 10-second freshness fence; never send actions to a bench device unless the owner explicitly requests bench mode.
- cost: No API cost and no new hardware; modest Mac CPU/USB traffic. A future isolated USB hub may cost $20–$40 but is optional.  ·  latency: Health updates under 1 second locally; round-trip test completion depends on the 24 kHz 60 ms framing and relay path, typically a few seconds.
- security: Serial logs can include speech/audio metadata. Keep raw PCM local, redact tokens from UART output, and use a separate scoped bench credential that cannot access production announcements or external actions.
- depends on: A Mac serial transport with port allowlisting for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A relay device identity and status schema that distinguishes usb-bench from production online; A playback receipt path; current device_playback has readers but no emitter


## What it asked for

_Nothing._
