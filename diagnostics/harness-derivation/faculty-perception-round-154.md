# Harness derivation — faculty-perception — round 154

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **local-agent liveness and route boundary** — The authenticated process I can probe is the AI Pendant Mac Local Agent v0.5.0 and /health is 200. GET /v1/devices/status is not a route on this process (404), so this probe cannot establish relay device registration.
  - evidence: GET /health returned {ok:true, service:'AI Pendant Mac Local Agent', version:'0.5.0'}; GET /v1/devices/status returned 404 with 'No such route on this agent'.

## Capabilities it proposed

### "Before I leave, run a one-minute pendant check and say whether the button, mic, speaker, Mac link, and relay are all genuinely ready."
- **useful because:** This is a user-facing go/no-go test rather than a dashboard: it catches a dead cable, stale bridge, broken audio path, or missing relay registration before the owner relies on the wearable away from the Mac.
- **path:** pendant → mac-terminal → mac-planner → relay → relay-realtime
- **model tier:** No expensive model for measurements; use a deterministic test, with a cheap model only to turn failures into one sentence.
- **latency:** 60 s hard maximum; button loopback and audio tone/capture should run concurrently, with a result in under 10 s when USB is present.
- **cost:** Near-zero API cost; local serial/audio probes dominate. Optional spoken diagnosis is <$0.001.
- **security:** Do not upload microphone test audio or serial logs by default. Persist only pass/fail metrics and firmware/session IDs; require confirmation before sending raw logs to the relay.
- **missing:** a Mac serial test harness for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; a deterministic test command in firmware/bridge for button loopback, mic RMS, speaker return, and packet counters; a relay test session that reports registration and round-trip freshness without creating a real conversation; a single signed result schema so a stale prior test cannot be mistaken for current readiness

### "When I press the pendant button, give me one safe, context-aware next step from what is on my screen, my calendar, and my open browser — and do not act unless I say go."
- **useful because:** It turns the wearable into an immediate decision surface: perception gathers the current browser page and schedule, judgement proposes one bounded next step, and action waits for explicit approval. The owner avoids opening apps and losing context while walking or working.
- **path:** pendant → browser-extension → mac-vision → mac-planner → relay-realtime
- **model tier:** Realtime for the short spoken suggestion; deterministic extraction first, and background models only for complex page/calendar synthesis.
- **latency:** Under 4 s from button press to suggestion; browser inspection and calendar read run in parallel; approval-to-action under 3 s.
- **cost:** One short realtime turn per press, generally <$0.03; most calls should be answered by structured browser/calendar facts without a second model pass.
- **security:** Screen and calendar data leave the Mac only as minimized structured context. Never include secrets or full page bodies; action tools require a second explicit confirmation and a visible receipt. Treat web content as untrusted.
- **missing:** a low-latency context join that snapshots active tab, selected text, and next calendar constraint atomically; a pendant button mode distinct from conversation start/end; a judgement contract that emits exactly one reversible suggestion plus confidence and missing context; action receipts linked to the originating snapshot so the owner can tell what evidence drove the action

### "If I ask for something while I am offline, remember the exact request, sync it when I reconnect, and ask me before doing anything that could change the world."
- **useful because:** The wearable remains useful outside LTE coverage without pretending an action happened. It preserves the owner's words in the existing failure buffer, then lets the Mac and relay recover, transcribe, deduplicate, and present a safe confirmation when connectivity returns.
- **path:** pendant → mac-terminal → mac-planner → relay → relay-realtime
- **model tier:** Local deterministic buffering and checksums first; background transcription/planning after reconnection; realtime only for the eventual confirmation conversation.
- **latency:** Offline capture acknowledgement under 300 ms; reconnect inventory under 5 s; transcription and presentation within 30 s of the Mac seeing the buffer.
- **cost:** No cloud cost while offline; one background transcription/planning call per recovered utterance, typically <$0.02. USB serial transfer and local storage dominate.
- **security:** Requests may contain secrets. Encrypt or device-bind the bounded SD failure-buffer, expire recovered audio after transcription, and never execute a recovered request without an explicit owner confirmation. Include sequence/checksum and a 'captured offline' label in every receipt.
- **missing:** a firmware offline-request record format that is separate from routine SD writes and obeys the failure-buffer-only rule; Mac serial importer that verifies monotonic sequence, checksum, and duplicate records before upload; relay endpoint and job state that preserve offline provenance through transcription, planning, and confirmation; a recovery UI/voice mode that distinguishes 'heard offline' from 'action completed'

### "Tell me when the system’s story disagrees with itself — for example, when a Mac receipt says done but the browser still shows the old state — and name exactly which evidence conflicts."
- **useful because:** Today each surface can report a locally plausible success, while nobody exposes contradictions across relay, Mac, browser, and device. The owner would hear calibrated uncertainty before trusting a false completion.
- **path:** faculty-perception → relay → mac-planner → browser-extension → pendant
- **model tier:** Deterministic correlation and freshness checks first; a cheap background model may summarize the conflict; realtime speaks only when the contradiction is owner-relevant.
- **latency:** Detect within 5 seconds of the second receipt or browser observation; spoken warning under 2 seconds after detection.
- **cost:** Near-zero for hashes, timestamps, and state joins; under $0.01 only when a natural-language explanation is needed.
- **security:** Expose only minimal snippets and provenance, never full private page contents. Treat stale or unauthenticated observations as weak evidence, not as proof of contradiction.
- **missing:** cross-surface correlation IDs shared by Mac jobs, browser mutations, relay jobs, and device events; a freshness-weighted contradiction engine with explicit evidence-strength rules; an owner-facing warning state distinct from completed/failed; durable links from the warning to each supporting receipt or capsule

### "For a sensitive action, make me physically press the pendant after seeing the final details, then execute exactly that approved version — not whatever the browser or Mac happens to show later."
- **useful because:** This creates a hardware-backed last-look consent boundary for sending, purchasing, deleting, or changing account settings. A remote prompt or stale browser tab cannot silently substitute for the version the owner approved.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → relay
- **model tier:** Deterministic nonce and payload hash; realtime model only explains the proposed action in one sentence. No model should decide whether the physical confirmation matches.
- **latency:** Approval challenge expires after 30 seconds; action begins within 2 seconds of a valid pendant press.
- **cost:** Negligible API cost; cryptographic hashing and one short relay round trip dominate.
- **security:** Bind the nonce to account, action, exact redacted parameters, and expiry; reject replay and altered payloads. Never put secret values into spoken confirmation or logs. Destructive actions still require the owner’s explicit policy permission.
- **missing:** a pendant button event authenticated with a monotonic counter or device key; relay challenge/response support that binds the physical press to a Mac/browser action digest; Mac action executor enforcement that refuses execution without a matching unexpired challenge; receipt fields proving what exact payload was physically approved

### "When I ask you to do something involving several surfaces, show me a tiny live chain — observed, decided, acted, verified — and stop at the first missing link instead of saying it succeeded."
- **useful because:** The owner currently has scattered job, pipeline, browser, and device records but no honest end-to-end transaction view. This would make partial success visible: a browser mutation may be complete while relay delivery or physical playback remains unknown.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-perception → faculty-action
- **model tier:** Deterministic state machine and receipts; use a cheap model only to phrase the chain for speech.
- **latency:** Initial chain visible within 1 second; each stage updates as telemetry arrives; no polling longer than 5 seconds for an active action.
- **cost:** Very low; event storage and correlation dominate, with optional <$0.005 summarization per multi-stage task.
- **security:** Redact action parameters and page content in the chain. Scope visibility to the owner’s session, retain only bounded metadata, and make unknown a first-class state rather than inferring success from Mac completion.
- **missing:** a single transaction ID propagated across plan, browser command, Mac action, relay job, and pendant event; stage contracts with explicit terminal states and freshness/timeout semantics; a reader that refuses to collapse 'Mac done' into 'owner heard'; bounded durable receipts accessible from the pendant and Mac


## What it asked for

_Nothing._
