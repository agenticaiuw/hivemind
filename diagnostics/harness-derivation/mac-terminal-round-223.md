# Harness derivation — mac-terminal — round 223

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Let me say “high quality voice” and have the system switch the pendant’s playback to the 24 kHz path, verify the ESP32/A2DP chain is actually delivering audio, and fall back with one spoken sentence if it is not."
- **useful because:** The owner gets a perceptibly better voice mode without guessing whether the prototype audio chain is silently starving. It uses the worn microphone/button, relay codec, Mac/USB bridge, and headphones as one tested instrument rather than treating each link as healthy in isolation.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal
- **model tier:** Realtime only for the short mode decision and spoken result; a cheap background verifier should inspect counters and UART diagnostics.
- **latency:** Mode acknowledgement under 2 seconds; verification may take up to 10 seconds after the first reply.
- **cost:** Usually one realtime turn plus a small background check; roughly $0.01–$0.05, dominated by the voice turn, with negligible local compute cost.
- **security:** Audio remains on the existing relay path. Changing codec mode is reversible, but the system must never claim success from a configured sample rate alone; require observed frame/ack counters and an audible-chain health result.
- **missing:** A negotiated audio-profile command spanning relay and nRF9160; A bounded dual-chip UART health/counter reader on the Mac; A bridge-side report of A2DP connection and underrun counters; An owner-visible fallback that preserves the current conversation turn

### "Read the page I am looking at in Safari into my pendant, let me ask two follow-up questions hands-free, and save only the cited claims—not the page—to my notes."
- **useful because:** This is the first genuinely wearable browser workflow: the browser contributes an authenticated tab the relay cannot reach, the Mac contributes the active tab and notes, and the pendant supplies interruption-free questions while walking. Saving claims rather than HTML keeps the result useful and bounded.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a cheaper background model to extract and cite page claims; reserve realtime for the two short follow-up answers and interruption handling.
- **latency:** First spoken summary in 5 seconds, each follow-up in 3 seconds; saving claims can finish asynchronously within 15 seconds.
- **cost:** About $0.01–$0.06 per page depending on extracted text; browser and Mac operations are local and dominate no API cost.
- **security:** The browser session may contain private data. The extension must send only the requested page's structured text, URL, title, and selected evidence; never screenshots or unrelated tabs. Persisting claims needs an explicit host/URL provenance and a short retention policy.
- **missing:** A pendant-triggered browser-read session that holds exactly two follow-up turns; A streaming handoff from browser structured snapshot to relay voice context; A notes writer that stores memory/browser findings with evidence capsules and URL; A tab-selection and privacy indicator so the owner knows which authenticated page was read

### "Finish the last Mac task after a restart: tell me what step was completed, resume only the uncompleted steps, and speak the final result through the pendant without repeating side effects."
- **useful because:** A long task should not become the owner's debugging problem when the Mac agent or laptop restarts. The pendant provides the durable request and truthful state, the relay reconnects it, and the Mac ledger supplies step-level recovery; no one node can provide that continuity alone.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal
- **model tier:** Use a cheap background reconciler at Mac startup and for ledger inspection; use realtime only to resolve an ambiguous resume choice or speak the concise result.
- **latency:** Detect stale work within 10 seconds of agent startup; resume automatically when every remaining step is replay-safe, otherwise ask one short question.
- **cost:** Near-zero API cost for deterministic ledger reconciliation; under $0.01 for an occasional spoken status.
- **security:** Never replay a step marked non-reversible or with unknown post-state. Bind the request to a job and action id, reject stale pendant intents, redact command output before speaking, and keep the owner’s existing maximum-access policy unchanged.
- **missing:** Boot-time reconciliation of processing jobs and open ledgers; A real jobId-to-ledger join and ledger close on every terminal outcome; Exactly-once action execution using the existing executionContext machinery; A relay resume message that carries the pendant request id and replay cursor; A compact spoken receipt that distinguishes completed, skipped, failed, and unknown steps

### "When you tell me something factual, let me ask “prove it” and hear the source, timestamp, and whether it came from my Mac, browser session, or your own inference—without repeating the whole answer."
- **useful because:** A wearable answer is easy to trust and hard to inspect. This gives the owner a fast way to distinguish an authenticated page, a local file, a live device reading, and model inference while walking, without opening a dashboard or losing the original conversation.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Use a cheap background model to normalize provenance records and classify evidence; realtime only speaks the compact source explanation and handles the short “prove it” exchange.
- **latency:** Source response in under 2 seconds when the evidence capsule is already present; otherwise say “I need to re-check” and complete within 10 seconds.
- **cost:** Usually a few hundred tokens and one local lookup, under $0.01; re-checking an external page is the dominant variable cost.
- **security:** Never read private URLs, file paths, or secret values aloud unless the owner explicitly asks. Keep source metadata scoped to the requesting turn, redact query parameters and tokens, and mark model inference as inference rather than laundering it as evidence.
- **missing:** A provenance envelope attached to every spoken claim, including source kind, observed-at time, confidence, and evidence pointer; A cross-surface provenance resolver for Mac status, browser pages, relay jobs, and pendant telemetry; A pendant interaction that requests provenance for the immediately preceding claim without starting a new recording turn; A concise spoken renderer with a privacy-aware detail level

### "What changed since yesterday? Give me only the three changes that affect me, across my notes, Downloads, browser work, and Mac tasks, and let me ask which source caused each change."
- **useful because:** The owner currently has to remember where yesterday’s work lived. A cross-surface delta turns the Mac, authenticated browser, relay job history, and wearable into one daily situational answer instead of four separate inventories.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Run collection and deduplication in a cheap background job; use realtime only to rank the top three changes and answer a source follow-up.
- **latency:** A scheduled delta can be ready before the morning brief; an on-demand answer should speak in under 8 seconds and continue refining asynchronously.
- **cost:** Low: mostly local metadata and existing provenance; roughly $0.01–$0.04 for ranking and summarization.
- **security:** Compare metadata and explicitly authorized content only. Do not silently inspect unrelated authenticated tabs. Exclude secrets, raw browser text, and deleted-file contents; expose each change’s source and observed timestamps.
- **missing:** A durable cross-surface daily snapshot with content hashes and source-specific retention; A browser-side change feed for pages the owner has explicitly enrolled; A normalized event schema for notes, Downloads, browser work, and Mac jobs; A pendant-friendly three-item delta card with source drill-down

### "Start a meeting mode from the pendant: capture only decisions and action items from the conversation, show me a spoken checkpoint before saving, and put the confirmed actions next to the right calendar event."
- **useful because:** The pendant is present in the room while the Mac may be closed. This turns an ephemeral conversation into reviewable work without asking the owner to type, while requiring a deliberate checkpoint so an overheard remark is never silently turned into a task.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Use realtime for the low-latency recording-state feedback and end-of-meeting checkpoint; use a cheaper background model for diarization-free extraction of decisions and action items.
- **latency:** Start/stop acknowledgement under 1 second; checkpoint within 10 seconds of stopping; calendar writes after confirmation within 15 seconds.
- **cost:** Audio processing dominates, approximately $0.05–$0.30 per meeting hour depending on transcription volume; local calendar writes are negligible.
- **security:** Require an explicit start signal, a visible/tonal recording indicator, and a spoken stop/checkpoint. Do not infer identities or silently send invitations. Retain only extracted decisions after confirmation unless the owner asks to keep the transcript; redact secrets before persistence.
- **missing:** A meeting-mode recorder that emits a consent/status signal through the pendant; Streaming speech segmentation and decision/action extraction without relying on the Mac microphone; A calendar-event matcher with an ambiguity checkpoint; A confirmation card/voice summary that supports editing before note and task creation


## Changes it proposed to its own stack

### `firmware` — Add a single end-to-end audio diagnostic frame format shared by nRF9160 and ESP32: monotonic turn id, capture/encode/decode/playback counters, queue depth, underruns, codec profile, and CRC. Emit it only on a bounded diagnostic request and have the Mac correlate both UART streams by turn id.
- **owner gets:** When the pendant sounds silent, delayed, or distorted, the system can say which link failed instead of making the owner retry blindly or blaming the wrong device. This directly advances the requested 24 kHz superwideband path.
- effort: Medium: reserve a compact binary frame, add counters at existing audio boundaries, implement the Mac correlator, and add one diagnostic command; test under USB with both chips.  ·  risk: Instrumentation must not run in the real-time audio path or inflate queues. Keep counters lock-free or snapshot-only, cap output rate, and disable diagnostics by default. Recovery is simply turning the diagnostic stream off.
- cost: No API cost; roughly 1–2 KB firmware code plus a few hundred bytes of counters per side. Negligible power when disabled.  ·  latency: No production latency; diagnostic snapshots may take 1–2 seconds.
- security: Frames contain timing and health metadata, not audio. Keep them on the local USB bench path and never upload raw UART logs automatically.
- depends on: The existing audio_link_truth_and_recovery firmware behavior; A bounded Mac USB serial reader (currently missing as a live capability); A negotiated 24 kHz profile command


## What it asked for

_Nothing._
## Its own summary

Produced four new recorded proposals: (1) spoken “high quality voice” mode with end-to-end 24 kHz verification and fallback, (2) Safari authenticated-page read/follow-up conversation that saves only cited claims, (3) restart-safe Mac task continuation with exactly-once replay and spoken receipts, and (4) a concrete firmware change adding correlated nRF9160/ESP32 audio diagnostic frames. I also tested the newly granted Mac USB serial and diagnostics schemas: both still resolve to nothing in the live inventory, so no serial health read occurred. I asked relay-realtime to confirm whether any live 24 kHz negotiation exists.

**Biggest unknown:** Whether the relay already exposes an audio-profile negotiation/counter route; without it, the 24 kHz proposal remains connective work requiring a new protocol. The Mac USB serial reader and read-diagnostics tools are still unresolved despite being granted, so bench truth requires the existing shell capture scripts.

