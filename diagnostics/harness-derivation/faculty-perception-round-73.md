# Harness derivation — faculty-perception — round 73

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent-current-state-round73** — At 2026-08-07T12:49:56Z the Mac agent is online v0.5.0 with fullControlMode and LLM planner enabled, but computer-use loop disabled because visionUploadConsented=false; Accessibility and Screen Recording are false, permissions.ready=false, and /observe says synthesized UI input will report success while doing nothing. AppleScript automation grants are present for listed apps. Browser extension home-chrome is offline with 7 pending commands. Relay is reachable and mac bridge online.
  - evidence: GET /ops/status and GET /observe HTTP 200 in Round 73
- **pipeline-audio-observation-round73** — Current pipeline history contains a completed routine news run whose TTS rendered 24,000 Hz mono PCM (75,734 bytes, 1,578ms, no clipping), while another realtime run recorded inputTelemetry audio at 15,625 Hz PCM and is still marked processing. A stale nrf9160 pipeline surfaced 2 held alerts from microSD. This is historical pipeline state, not evidence of current pendant connectivity.
  - evidence: GET /pipeline HTTP 200, pipeline runs and event metadata
- **briefing-duplication-round73** — GET /research/briefings shows at least 12 unplayed schedule briefings for the same topic and headline ('Today's schedule — Friday, August 7'; 3 meetings, next Ask Jorge at 9:00 AM), each ~39.8 seconds and mostly identical file paths, created repeatedly from 11:13 through 12:37. This indicates repeated generation without played-state or content deduplication; it is an observation of stored records, not proof the pendant played any of them.
  - evidence: GET /research/briefings HTTP 200 at 2026-08-07T12:49Z

## Capabilities it proposed

### "Tell me what is true right now about the thing I asked you to do—even if the Mac, browser, relay, or pendant disagreed—and say what is stale, offline, blocked, or only believed."
- **useful because:** Today the system can report individual jobs and receipts, but not establish one cross-surface reality. The live evidence shows why this matters: the browser is offline with 7 queued commands, a pipeline run remains processing, and a prior run is blocked on approval while audio was already rendered and uploaded. The owner needs one honest answer that never upgrades a queued, stale, or locally-reported success into completion.
- **path:** pendant → relay → mac-planner → browser-extension → unified → dashboard
- **model tier:** background for normal reconciliation; deterministic status joins first, escalating to planner only when records conflict or the owner asks for interpretation. Realtime is used only to speak the short result.
- **latency:** Under 2 seconds for deterministic joins across current records; up to 8 seconds only when reconciling conflicting receipts or asking a surface for a fresh heartbeat.
- **cost:** Usually near-zero model cost (typed joins over /ops/snapshot, /jobs, receipts, /pipeline, browser status, and relay records); occasional conflict resolution around 2k–5k background tokens. Realtime/TTS cost only when spoken.
- **security:** Must not expose secret captures or private page contents merely because they are in diagnostics. Return minimum necessary evidence, source and observedAt for each claim; redact tokens and sensitive values. Never retry or mutate work while checking status. Require confirmation before converting an unresolved state into any new action.
- **missing:** A single typed cross-surface status schema with freshness TTLs and contradiction precedence; A relay-readable pendant continuity/ack snapshot (currently requested but not available to this agent); Browser extension heartbeat/queue semantics that distinguish pending, delivered, executed, and expired commands; A durable correlation ID linking relay job, Mac job, pipeline ID, browser command, and pendant playback acknowledgement

### "Before I rely on you, tell me whether you can hear me, answer me, reach my Mac and private browser, and deliver speech to the pendant right now—and if one path is degraded, tell me exactly what still works and choose a safe fallback."
- **useful because:** The owner currently has to infer availability from silent failures, stale queues, or misleading action receipts. This would be an honest spoken 'reliability envelope' for the current moment: conversational audio, pendant delivery, relay reachability, Mac automation, browser sessions, and freshness of each signal. It lets the owner decide whether to trust an answer before asking for something consequential, without exposing internal diagnostics or requiring them to inspect a dashboard.
- **path:** pendant → relay → mac-planner → browser-extension → unified → dashboard
- **model tier:** Deterministic typed health evaluation for all measurements; background model only to turn an unusual combination into a short explanation. Realtime speaks the result when asked through the pendant.
- **latency:** Under 1 second from cached heartbeats; up to 3 seconds when a fresh relay/Mac/browser probe is needed. Never block ordinary conversation on an unavailable surface.
- **cost:** Near-zero model cost for the health vector and threshold rules; occasional background explanation under 500 tokens. No vision or planner call.
- **security:** Expose capability states, timestamps, and failure classes—not URLs, page text, private app names, tokens, or stored captures. Do not silently test or mutate applications. Clearly distinguish 'not measured' from 'unavailable' and never claim microphone or speaker health without a device-originated signal.
- **missing:** A signed, device-originated pendant health/ack heartbeat covering microphone capture, network link, speaker playback, queue depth, and last-played sequence; A shared freshness and confidence schema for relay, Mac, browser, and pendant observations; A non-invasive browser heartbeat that reports whether the extension can execute commands, separate from merely having queued commands; A spoken fallback policy that prefers pendant, then Mac audio, then dashboard notification without duplicating delivery


## Changes it proposed to its own stack

### `routines` — Make briefing generation idempotent per semantic content hash and delivery state: before writing a scheduled briefing, compare topic, normalized headline, source window, and audio payload hash against the newest unplayed item; suppress duplicates, retain one canonical artifact, and emit a diagnostic event when a duplicate request is coalesced. Add an explicit 'superseded' state so a newer schedule can replace an older unplayed one without claiming playback.
- **owner gets:** The owner gets one morning brief instead of a dozen identical queued recordings and will not waste battery or attention hearing repeated alerts. A changed schedule still replaces the old brief, while an unchanged retry becomes invisible noise rather than another pendant item.
- effort: Medium: shared briefing fingerprint/state model, atomic check-and-write, migration for existing duplicates, and dashboard/relay display of coalesced attempts.  ·  risk: A too-aggressive hash could suppress a genuinely updated brief; use source-window and normalized content plus a bounded time window, and preserve audit records. Recovery is to mark a coalesced item deliverable manually or regenerate with force=true.
- cost: Negligible API cost; modest local disk/database cleanup. Avoids repeated TTS generation and audio storage.  ·  latency: Adds one local read/hash comparison, typically <100 ms; avoids repeated TTS latency on retries.
- security: No new data leaves the Mac. Hash only normalized briefing metadata/audio; do not hash or log private calendar contents in a way that expands exposure.
- depends on: A durable played/acknowledged state shared by briefing, relay, and pendant playback; currently records show played=false but no proof of device playback.; A stable semantic content hash and source-window identifier in /briefing and relay delivery records.

### `firmware` — Add a monotonic, locally persisted delivery ledger in the pendant firmware. Every captured utterance and every received audio/alert gets a sequence number, source, byte count, checksum, and terminal state (captured, uploaded, received, playback-started, playback-complete, or locally-held). The device emits a compact heartbeat containing only the ledger watermark and fault bits, and exposes a long-press spoken/haptic diagnostic ('last reply delivered', 'held offline', or 'not confirmed') without needing the Mac.
- **owner gets:** The owner can know whether a reply was actually heard instead of trusting that a cloud upload or Mac render means delivery. After a dropped link or reboot, the pendant can say exactly what is waiting and avoid replaying or losing a response. This is a physical, local guarantee unavailable from today's server-side records.
- effort: High: firmware state machine, flash-safe append/compaction, checksum validation, boot recovery, relay protocol fields, and playback-driver integration; requires end-to-end fault-injection tests for power loss and link drops.  ·  risk: Flash wear, ledger corruption, or a stuck playback state could create false holds or duplicate audio. Use bounded journal rotation, CRC plus atomic commit markers, and make replay user-invoked or explicitly acknowledged. Recovery can rebuild the watermark from the last valid record and mark uncertain items 'unknown' rather than claiming completion.
- cost: No per-use API cost. Small firmware/storage work; negligible steady-state power for heartbeat, with brief radio overhead on state changes. Hardware cost is $0 if existing flash and button/LED/audio paths suffice; otherwise a larger nonvolatile partition may be needed.  ·  latency: Adds a few milliseconds to receive/playback bookkeeping and a short local diagnostic interaction; does not add model latency.
- security: Ledger stores metadata and hashes, not raw speech or audio. Sequence identifiers must be unguessable enough not to reveal conversation volume over an unpaired link; pair/authenticate heartbeat and allow local erase.
- depends on: A relay schema carrying device sequence watermarks and acknowledgements; A clearly defined exactly-once/replay policy shared by relay and Mac pipeline; Device-originated live observability, which is currently the largest unanswered perception gap


## What it asked for

_Nothing._
## Its own summary

Round 73 established fresh truth: Mac agent and relay are reachable, but browser is offline with 7 pending commands; Accessibility, Screen Recording, and vision upload consent remain absent, making GUI/computer-use receipts untrustworthy. Pipeline history confirms one 24 kHz TTS render, but also a still-processing realtime run with 15,625 Hz input telemetry. Stored briefings contain 12+ identical unplayed schedule recordings, so I recorded that finding and proposed idempotent briefing deduplication. I also proposed a cross-surface reality report, though the system flagged it as close to an existing idea; the distinct actionable gap is the missing correlation/freshness layer between surfaces.

**Biggest unknown:** Whether the pendant actually received or played any queued audio/alerts. I still need the outstanding live pendant observability and continuity acknowledgement snapshot, plus durable correlation IDs across relay job, Mac job, pipeline, browser command, and pendant playback. I also need a browser heartbeat to establish whether the 7 pending commands are executable or stale. Accessibility/Screen Recording remain owner-granted constraints, not something this agent can obtain.

