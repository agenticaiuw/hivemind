# Harness derivation — faculty-perception — round 185

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac permission state** — The running AI Pendant Agent currently reports Accessibility and Screen Recording trusted, requiredMissing/optionalMissing empty, and permissions.ready=true; browser extension is online on Safari DoorDash tab 3032326. This supersedes earlier denied-state observations.
  - evidence: GET /ops/status and GET /browser/status returned HTTP 200 at 2026-08-08T22:18Z; ops status explicitly reports accessibility.trusted=true, screenRecording.granted=true, ready=true, browser online=true.

## Capabilities it proposed

### "“Tell me what changed while I was away, what is still true now, and which actions would be unsafe because their evidence is stale or contradictory.”"
- **useful because:** This is the single most useful perception capability: it would distinguish a Mac action that really completed from a relay delivery that was merely socket-written, expose stale browser/session facts, and explain contradictions instead of presenting a falsely coherent digest. Unlike a simple catch-up list, it produces a time-ordered causal account with freshness, source authority, and explicit unknowns.
- **path:** relay-realtime → mac-planner → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use deterministic event normalization and freshness rules first; use a cheap background text model only to summarize the already-selected evidence. Reserve realtime for the owner's spoken follow-up.
- **latency:** Under 2 seconds for the bounded snapshot and contradiction scan; under 5 seconds for an optional spoken explanation. No live UI scraping beyond existing read routes.
- **cost:** Near-zero model cost for the scan; roughly $0.001–$0.01 for an optional short summary, dominated by context tokens rather than inference.
- **security:** The output must preserve source provenance and never infer owner-heard audio from relay delivered/completed states. Browser URLs, page titles, and job details can be sensitive; redact secrets and require confirmation before exposing them aloud or using stale evidence for an action.
- **missing:** A persistent cross-surface event envelope with source timestamp, observed-at timestamp, monotonic sequence, and causal parent IDs; existing stores have incompatible count/byte retention.; A contradiction/freshness evaluator that consumes the snapshot without treating /ops/snapshot truncation as complete history.; A relay-to-Mac correlation ID for browser reads and speech deliveries; relay browser reads currently mint no ID or hash.; A device-originated played/consumed event when a pendant exists; current delivery state is not hearing evidence.

### "“Before I rely on the pendant, run a one-minute commissioning test and tell me exactly which link failed: USB/device, audio bridge, relay, transcription, or playback.”"
- **useful because:** Today the Mac and browser are live but the pendant is absent from the relay registry, so recorded pipeline audio can be mistaken for present hardware. A commissioning result would give the owner a concrete go/no-go answer before trusting a wearable conversation, and would be useful again after firmware updates or cable changes.
- **path:** pendant → mac-terminal → mac-planner → relay-realtime → faculty-perception → faculty-action
- **model tier:** Deterministic probes and a fixed synthetic utterance/audio fixture; no language model needed except a cheap final explanation. Realtime is not appropriate for the test itself.
- **latency:** 60 seconds maximum, with early failure in under 5 seconds when a stage is absent. The owner explicitly starts it; no background polling.
- **cost:** Negligible API/model cost. USB serial and audio fixture are local; a single relay health/registration request is the dominant network operation.
- **security:** The test must use a synthetic phrase and non-sensitive audio, never record the owner's speech, and must not write routine data to the microSD failure buffer. Relay credentials and raw serial output stay local; report only bounded counters and stage verdicts.
- **missing:** A real bounded USB serial exchange capability for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; the accepted mac_usb_serial_diagnostics request is a build proposal, not a callable route.; A commissioning protocol: firmware build/session beacon, loopback sequence, expected relay registration/heartbeat, and an audio bridge echo marker.; A relay test endpoint that reports registration and an end-to-end test receipt without treating socket writes as playback.; A fixture or safe test mode in firmware that emits a known audio pattern and does not save it to SD.

### "“When you are about to act on something you saw earlier, prove the evidence is still current—or stop and ask me to refresh it.”"
- **useful because:** A browser tab, relay read, and Mac action can all report success while the underlying page, permission, session, or device state has changed. This gives the owner a practical safety boundary: stale or uncorrelated evidence cannot silently drive a purchase, message, deletion, or other consequential action.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Deterministic freshness, content-hash, session-identity, and revocation checks; use a small background model only to explain why evidence failed. Realtime speaks the concise hold/refresh request.
- **latency:** 200 ms for local capsule/session checks; at most 2 seconds when a browser refresh is required. Block the action until the check completes.
- **cost:** Usually zero model cost; one optional short explanation costs well under $0.005. Browser refresh latency dominates.
- **security:** Never read or repeat secret fields while refreshing. Treat tab/session IDs and capsule hashes as opaque join keys, not user-facing content. A stale check must fail closed for destructive or financial actions, while allowing harmless reads.
- **missing:** Mount the existing browserProvenance routes and make every browser result carry a capsule/provenance link; that module currently exists but is not mounted.; A relay browser-read ID and content hash so cloud browser output can be compared with a Mac capsule instead of being an untraceable string.; A policy table mapping action risk to freshness bounds and requiring explicit confirmation when evidence is expired, revoked, or from a different tab/session.; A shared pre-action gate consumed by faculty-action, rather than a warning shown only in the dashboard.

### "“Learn when and why you misunderstand me, then quietly tune the pendant for my voice and surroundings—or tell me to repeat before you act.”"
- **useful because:** The owner should not have to discover after a mistaken message, purchase, or reminder that the microphone was clipped, the room was loud, or LTE loss damaged the utterance. This would turn the pendant’s local capture verdict, relay transcription confidence, browser/Mac action outcome, and the owner’s correction into a personal reliability model that can say “I heard this clearly” versus “I need a repeat,” before action.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Keep the reliability score, acoustic features, packet statistics, and repeat decision deterministic/on-device or in the relay. Use a cheap background model to cluster recurring failure causes and recommend firmware/profile changes; realtime only handles the immediate repeat request.
- **latency:** The pendant must decide repeat versus forward within 150 ms of utterance end. Relay confidence and action-outcome correlation can update asynchronously within 10 seconds.
- **cost:** Near-zero inference cost for each turn; occasional background clustering costs less than $0.01 per batch. Bandwidth is limited to compact quality metrics and hashes, never raw audio by default.
- **security:** Voice-quality traces can reveal location, health, or social context. Keep raw audio local and expiring; upload only quantized metrics, model/version IDs, and opaque utterance IDs. Never let a low-confidence transcript trigger an irreversible action without confirmation.
- **missing:** A cross-surface utterance ID joining the pendant capture sentinel, relay transcription, Mac/browser action, and any owner correction.; A bounded personal reliability profile with separate scores for microphone quality, network loss, transcription, and action grounding; it must not silently rewrite the owner’s memory or preferences.; A deterministic policy that maps quality verdicts to repeat, confirm, or proceed, with risk-aware thresholds for messages, purchases, and deletions.; A safe adaptation channel for audio/VAD/Opus settings and a visible explanation of every change; no routine writes to the SD failure buffer.

### "“Before this conversation leaves any device, show me a compact privacy receipt: what was captured, what crossed the relay, what was retained, and how I can erase it.”"
- **useful because:** The owner currently cannot establish the data boundary of a voice turn: local audio, relay speech, browser page text, announcements, and Mac logs have different retention rules and some advertised expiry is not enforced. A per-turn receipt would make the wearable trustworthy in ordinary life, not just technically functional.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → faculty-perception → faculty-action
- **model tier:** Generate the receipt from deterministic byte counts, classifications, retention policies, and deletion outcomes; use no model for the facts and a cheap text model only to phrase the summary.
- **latency:** A terse receipt within 300 ms after each turn; detailed retention/deletion verification within 3 seconds when requested.
- **cost:** Negligible model cost; bounded metadata writes and one optional background summarization dominate.
- **security:** The receipt itself must not contain transcript or secret content by default. Use content classes, sizes, hashes, destination, and expiry/deletion status. Erasure must require confirmation for shared or legally relevant records and must distinguish “withheld from reads” from physically deleted.
- **missing:** A per-turn data-flow ID spanning pendant capture, relay audio/STT, Mac pipeline, browser evidence, announcements, and model calls.; A machine-readable retention/deletion receipt with actual deletion verification rather than advertised TTLs.; A user-facing redaction classifier that runs before relay upload, with an explicit fail-closed mode for sensitive turns.; An authenticated erase/revoke operation that propagates across D1, R2, Mac files, browser provenance, and the pendant’s bounded NVS queue.


## Changes it proposed to its own stack

### `integration` — Install a fail-closed evidence gate between faculty-perception and faculty-action. For each proposed action, it accepts only a referenced browser capsule/job receipt/device beacon, checks revocation, source/session identity, content hash, and age, and emits an explicit observed/stale/contradictory/unknown verdict. It must reject relay 'delivered' and Mac 'completed' as hearing evidence unless a future device playback event exists.
- **owner gets:** The owner stops getting actions based on facts that were true minutes ago, belonged to another tab, or were only acknowledged by a server write. A high-risk action becomes explainable: “I paused because the page changed” rather than a silent wrong click.
- effort: Medium: mount the existing browser provenance routes, define the verdict schema and risk thresholds, then add one call in faculty-action. Relay browser correlation and pendant playback remain follow-on work.  ·  risk: A false stale verdict could interrupt harmless work; default low-risk reads to warn-only and destructive/financial actions to block. If the provenance store is unavailable, preserve the current read-only behavior but never claim the action was grounded.
- cost: Negligible runtime cost; bounded local JSON reads and hashes. Optional explanation uses a cheap text model.  ·  latency: Typically <200 ms locally; browser refresh or relay correlation may add 1–2 seconds.
- security: Improves safety by preventing ungrounded actions, but provenance metadata can reveal URLs and session relationships; redact content and retain opaque IDs only in action logs.
- depends on: Mount local-agent/browserProvenance.js routes (currently unmounted).; Add relay browser-read correlation ID/content hash; current read_web_page returns neither.; Define device playback telemetry when a pendant is deployed; until then keep audio-heard status unknown.


## What it asked for

_Nothing._
## Its own summary

Established a new live fact: the exact AI Pendant Agent binary now has Accessibility and Screen Recording, permissions.ready=true, and all listed automation grants; Safari browser bridge is online on a DoorDash tab. Proposed three owner-facing capabilities: (1) an evidence-grade “what changed while I was away” causal account with freshness/contradiction handling, (2) a one-minute cross-node pendant commissioning test that identifies the failing link, and (3) a fail-closed stale-evidence boundary before consequential browser/Mac actions. Also proposed installing that evidence gate as an integration change. The key current constraint is not permissions anymore: there is still no pendant presence/playback proof, relay browser reads still lack IDs/hashes, and browser provenance exists but is unmounted.

**Biggest unknown:** Whether the physical nRF9160 and ESP32 are connected and responsive on USB right now; no callable serial reader exists in this harness, and the relay cannot infer that state from its registry.

