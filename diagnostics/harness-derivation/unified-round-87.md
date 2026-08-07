# Harness derivation — unified — round 87

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **audio pipeline asymmetry** — The live pipeline currently renders outbound speech as 24 kHz mono PCM, but a recent realtime inbound event reports 15,625 Hz mono PCM capture; the pendant hardware spec separately documents 16 kHz/16 kbps Opus uplink and 24 kHz decode. The 24 kHz goal is therefore not end-to-end yet.
  - evidence: GET /pipeline returned pcm sampleRate=24000 for TTS and inputTelemetry sampleRate=15625 for a realtime event; get_hardware_spec(audio) reports 15,625 Hz capture and 16 kHz Opus uplink.

## Capabilities it proposed

### "“Remember this for the project I’m working on: [spoken thought].” Later, “What did I remember about that project?”"
- **useful because:** The owner can turn a fleeting thought into a properly filed, retrievable project note without stopping to open an app. The pendant supplies the words and timing, the Mac supplies the active project and browser/app context, and the relay makes the capture survive a dropped connection. This is more useful than a generic voice memo because it returns the surrounding evidence and destination.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background for transcript cleanup, project classification, and indexing; realtime only for the initial spoken acknowledgement
- **latency:** Acknowledge locally/streaming in under 1 second; save and enrich the note within 5 seconds. Retrieval should be a deterministic indexed lookup, escalating to the planner only when the project reference is ambiguous.
- **cost:** Typically one short background inference (roughly 500–1,500 input tokens) per capture and none for exact retrieval; dominant costs are transcription and optional browser-context extraction, not the realtime acknowledgement.
- **security:** The captured audio/transcript and surrounding page title/URL may be sensitive. Default to metadata plus a short selected snippet, never full page contents; redact secrets and authentication tokens; keep retention bounded and show provenance in the dashboard. No external sharing or destructive action occurs, so no confirmation is needed beyond the owner’s explicit capture phrase.
- **missing:** A pendant capture trigger and local acknowledgement that can queue an event while offline; A typed capture envelope joining audio transcript, active project, browser tab metadata, timestamp, and sensitivity; A durable Mac note/index writer with conflict-safe append and source provenance; A retrieval route that can answer from the project index and cite the originating capture

### "“Use the page I’m looking at to help me, but don’t let passwords, tokens, personal identifiers, or unrelated private text leave my Mac.”"
- **useful because:** Today the system can combine a logged-in browser page, Mac planning, relay reasoning, and pendant speech, but it lacks a trustworthy content boundary between those surfaces. The owner should be able to get the benefit of authenticated context without having to choose between blind automation and exporting an entire private page.
- **path:** browser-extension → mac-planner → relay → pendant → dashboard
- **model tier:** Deterministic local redaction and policy evaluation first; a cheap background model may classify ambiguous fields. Realtime is used only to acknowledge that context was filtered, never to perform the filtering.
- **latency:** Add at most 150 ms for local DOM/clipboard redaction before a request leaves the Mac; ambiguous content should fail closed and be omitted rather than block the owner indefinitely.
- **cost:** Near-zero API cost for regex/structured-field redaction; occasional background classification is under 1,000 tokens and should be rare. The dominant cost is local implementation and maintaining site-independent detectors.
- **security:** Secrets can be encoded, split across DOM nodes, or visually rendered. The browser extension must redact password inputs, authorization headers, cookies, hidden fields, credit-card/SSN-like patterns, and unrelated regions before serialization; send only an allowlisted semantic region plus provenance. Keep an inspectable local audit showing what was withheld, allow owner override only per request, and never log raw content in relay diagnostics.
- **missing:** A Mac-local content firewall that runs before browser data enters planner or relay requests; A typed allowlist for which DOM regions, clipboard fields, screenshots, and accessibility text may leave the Mac; A redaction report attached to each evidence capsule so the pendant can explain omissions; A fail-closed test suite covering DOM, screenshot OCR, clipboard, and encoded secrets


## Changes it proposed to its own stack

### `integration` — Add a durable capture-envelope adapter between the pendant pipeline and Mac context services. On an explicit capture event, it records transcript/audio reference, UTC and owner timezone timestamps, active project id, browser session/tab metadata, foreground app, sensitivity, and provenance into an append-only envelope; asynchronously resolves the project, writes a project note, and exposes deterministic retrieval with source links. If enrichment fails or the link drops, retain the raw envelope for retry instead of reporting success.
- **owner gets:** A spoken thought becomes a filed project note with enough context to find and trust later, even when the Mac or browser is briefly unavailable.
- effort: Medium: one shared schema, relay retry/idempotency, a Mac writer/index, and a small retrieval endpoint; add end-to-end tests for duplicate events, offline replay, and redaction.  ·  risk: A capture could be filed under the wrong project or include sensitive page metadata. Mitigate with confidence thresholds, an unfiled inbox fallback, explicit provenance, metadata-only defaults, and user deletion. Recover failed writes by replaying the immutable envelope.
- cost: Negligible storage and background inference cost; avoid realtime calls after acknowledgement. A small local index and bounded audio retention are the main operational costs.  ·  latency: Sub-second acknowledgement; enrichment is asynchronous and normally completes in under 5 seconds. Retrieval is local/deterministic for known project ids.
- security: Sensitive content stays on the relay/Mac path, with field-level redaction and bounded retention. Never transmit full authenticated page bodies by default; store URL/title and a hash or owner-selected excerpt.
- depends on: A device-side explicit capture event and local acknowledgement; A typed capture-envelope contract with idempotency key; A durable project-note/index writer on the Mac; Owner privacy policy for whether selected browser snippets may be retained

### `browser-harness` — Insert a Mac-local Context Firewall as the mandatory serialization boundary for browser inspection, research, capture enrichment, screenshots, clipboard text, and planner requests. It applies ordered detectors and an allowlist of semantic regions, replaces sensitive spans with typed redaction markers, emits a hash-only redaction manifest, and refuses any unclassified payload. Evidence capsules and pipeline events carry the manifest so downstream agents know exactly what they did not see.
- **owner gets:** The owner can ask the pendant to work with a private logged-in page without accidentally handing over credentials or unrelated personal information, while still receiving useful answers and an explanation when a field was withheld.
- effort: High: implement DOM and screenshot/clipboard paths, detector tests, policy versioning, extension/server enforcement, and a dashboard review of redaction decisions.  ·  risk: Over-redaction could make tasks fail; under-redaction is a privacy incident. Recover by preserving the original only on the Mac, offering a narrowly scoped owner-approved retry for one region, and versioning every decision for audit.
- cost: Small local CPU/memory overhead; negligible API cost when deterministic detectors suffice. Occasional ambiguous classification adds a low background-model cost.  ·  latency: Usually below 150 ms locally; screenshot OCR and ambiguous classification may add seconds and should be skipped or fail closed in realtime.
- security: Materially reduces secret exfiltration risk, but must itself avoid logging raw payloads, protect policy configuration, and treat redaction manifests as potentially sensitive metadata.
- depends on: A browser-extension serialization hook before /browser/inspect results are returned; A shared evidence-capsule schema carrying redaction provenance; Owner-visible policy defaults and an explicit per-request override; Tests against authenticated pages, screenshots, clipboard, and encoded secrets


## What it asked for

_Nothing._
## Its own summary

Discovered that the Mac agent exposes capture, project, browser-session, pipeline, context-graph, journal, and briefing routes, and that the bridge is online while Chrome is offline. Recorded a new cross-surface capability: explicit pendant “remember this for my project” captures, enriched with active Mac/browser context, retried through relay, and retrieved with provenance. Recorded the integration change needed to connect the existing routes. Also verified a real audio gap: outbound TTS is 24 kHz, while inbound capture is 15,625 Hz (with 16 kHz Opus uplink), so the 24 kHz path is not end-to-end yet.

**Biggest unknown:** The remaining blockers are owner/product decisions already pending: authoritative 24 kHz end-to-end acceptance thresholds, headphone compatibility target, production pendant constraints, acceptable phone-companion/privacy boundary for retaining browser context, queued-action resume policy, and whether selected authenticated-page snippets may be stored. No new grants appeared in this round; I did not re-request existing pending tools or denied macOS TCC permissions.

