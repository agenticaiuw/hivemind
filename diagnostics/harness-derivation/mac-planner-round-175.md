# Harness derivation — mac-planner — round 175

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Diagnose the last failed audio session from the pendant's USB diagnostic fixture and pipeline logs, tell me the likely failing stage in one sentence, and file a timestamped report with the counters and a suggested next test."
- **useful because:** Audio failures currently require an engineer to manually align serial output, modem counters, and relay pipeline events. A single spoken diagnosis plus a durable local report would make the wearable maintainable by its owner and catch regressions in the already-shipped 24 kHz path.
- **path:** pendant → mac-planner → relay-realtime → faculty-perception → faculty-judgement
- **model tier:** Cheap background model for counter classification and report generation; escalate to the expensive tier only when counters conflict or the diagnosis is ambiguous.
- **latency:** Read serial and relay evidence in under 5 s; spoken diagnosis under 2 s after evidence collection; report completion under 15 s.
- **cost:** About $0.005-$0.02 per diagnosis; almost all cost is the small classification/summarization call.
- **security:** Diagnostic mode must be explicitly armed and must never capture microphone content. Reports stay local in ~/AI-Pendant-Workspace unless the owner explicitly asks to upload them. Include firmware version and counters, but redact serial identifiers by default.
- **missing:** A live Mac USB-serial exchange capability for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA (the pending mac_serial_exchange request); A relay endpoint to retrieve and correlate fixture results with /pipeline/:pipelineId/audio/:direction; A stable diagnostic report template and automatic firmware/build identifier

### "When I leave a bookmark while the Mac is disconnected, reconcile it when the Mac returns: identify the active calendar item, project, and browser tab around that timestamp, create a private follow-up note with confidence and missing evidence called out, and put a short alert on the pendant."
- **useful because:** An offline bookmark is currently durable but context-poor. This makes it useful in the real dead-zone-to-desk transition: the pendant records the moment, the relay preserves it, and the Mac later supplies the surrounding work context without pretending uncertain matches are facts.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Background model for matching and uncertainty explanation; no realtime model is needed except to speak the resulting alert if requested.
- **latency:** Reconcile within 30 s of the Mac heartbeat returning; pendant alert should be queued immediately after the match is committed.
- **cost:** About $0.01 per bookmark reconciliation; calendar/browser reads dominate operationally, not tokens.
- **security:** Only metadata around the bookmark window should be read; do not ingest page bodies or mail. Store the confidence score and evidence IDs with the note, and expire unmatched bookmarks after an owner-configured period. External actions such as sending or filing into third-party systems require confirmation.
- **missing:** A durable bookmark-to-Mac reconciliation queue with idempotency keys; A browser inspection response that includes tab timestamp/last-active metadata rather than only current tabs; A relay-to-pendant alert delivery path that can reference the created local note

### "When I reconnect the pendant to my Mac after being away, give me a one-sentence 'since you left' update that merges offline bookmarks, queued pendant alerts, failed or completed Mac jobs, and browser changes; then let me ask for any one item to be reopened or replayed."
- **useful because:** Today each surface knows only its own backlog. A reconnect digest is the moment the wearable and Mac can jointly restore continuity: it prevents missed alerts and turns unattended work into a concise, actionable handoff instead of a pile of notifications.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Background model builds the bounded digest and ranks items; realtime model is used only to speak the one sentence and answer a follow-up.
- **latency:** Detect reconnect within 3 s; produce the digest within 10 s; reopening one selected item within 5 s.
- **cost:** About $0.01-$0.03 per reconnect; ranking a small set of event receipts dominates, not the device transport.
- **security:** Digest must use metadata and redacted snippets by default. Never read page bodies or mail merely because the pendant reconnects. Replaying a job or reopening a sensitive browser tab must be an explicit follow-up, with the existing owner policy deciding whether confirmation is required.
- **missing:** A serial reconnect event and authenticated pendant identity/sequence cursor; A cross-surface event ledger that can deduplicate the same job, bookmark, and alert; A small spoken-digest and item-selection protocol between relay and pendant

### "Show me a private, tamper-evident receipt for the last day proving when the pendant microphone and speaker were active, when privacy latch was engaged, and which Mac/browser surfaces were read or acted on—without storing or exposing the underlying audio, page contents, or secrets."
- **useful because:** The owner cannot currently answer the basic trust question, 'what did this system actually hear or read while I was away?' A compact cross-node receipt would make an always-present wearable auditable rather than requiring blind trust. It is not a transcript or a new alert queue: it is an independently checkable activity and privacy record spanning the pendant, relay, Mac, and browser.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception
- **model tier:** No expensive model for collection or verification; use a cheap background summarizer only to turn verified events into the owner's one-sentence explanation.
- **latency:** Append each event within 2 seconds; answer a receipt query within 10 seconds, with verification performed before summarization.
- **cost:** Under $0.01 per day of normal use; storage and cryptographic signing dominate, not inference.
- **security:** The receipt itself is sensitive because it reveals activity timing. Keep it encrypted locally and relay-side, redact URLs/app names by default, rotate signing keys, and make export an explicit owner action. The system must record denied/unknown observations rather than claiming proof; missing telemetry must be visible as a gap.
- **missing:** A shared event-envelope format with monotonic timestamps and sequence numbers across pendant, relay, Mac, and browser; Hardware- or OS-backed signing/attestation for pendant privacy-latch and audio-state events, plus a relay append-only hash chain; Mac and browser emitters for read/action events that include scope, redaction class, and outcome without content; A receipt viewer and spoken query route that verifies the chain before presenting it


## What it asked for

_Nothing._
## Its own summary

Round 175 produced three non-duplicate capabilities: USB diagnostic concierge for the 24 kHz path; offline-bookmark reconciliation into a confidence-labeled private follow-up; and a reconnect 'since you left' digest spanning pendant, relay, Mac jobs, and browser state. The initial bug-report proposal collided with an existing backlog item, so I did not count or restate it.

**Biggest unknown:** The physically connected pendant is still not usable as a live Mac/relay event source from this agent: mac_serial_exchange remains unavailable. The next enabling pieces are authenticated USB reconnect/sequence events, a cross-surface deduplicating event ledger, and a small pendant digest/selection protocol. I did not re-request the pending tool.

