# Harness derivation — faculty-perception — round 16

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent-status-2026-08-07** — Mac local agent v0.5.0 is reachable and relay-connected, but not ready: Accessibility trusted=false and Screen Recording granted=false; browser extension offline with 2 pending commands; computer-use loop disabled and vision upload consented=false.
  - evidence: GET /ops/status returned 200 with ready:false, missing Accessibility and Screen Recording, browser online:false pendingCommands:2, loopEnabled:false.
- **relay-status-2026-08-07** — Cloud relay v1.1.0 is reachable, paired, API-key configured, speech-to-text configured, and Mac bridge online; pendant pipeline telemetry, speech, persistent state, and durable audio are advertised.
  - evidence: GET /ops/status relay.payload returned ok:true, reachable:true, macBridgeOnline:true, capabilities pendantPipelineTelemetry/pendantSpeech/persistentAgentState/durableAudio true.
- **browser-status-2026-08-07** — Authenticated Chrome bridge is currently offline, has no active tab and unknown tab count, last seen 2026-08-07T09:21:08.821Z, and has 2 pending commands.
  - evidence: GET /browser/status returned online:false, tabId:null, tabCount:null, pendingCommands:2.

## Capabilities it proposed

### "“Before you try anything, tell me which parts of you are actually available right now—and warn me if a queued request is stuck.”"
- **useful because:** The system currently has contradictory-looking surfaces: the relay and Mac bridge are reachable while the Mac is not ready and the browser is offline with queued commands. A short spoken readiness report prevents the owner from believing a browser or GUI task ran when it could not.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for periodic health snapshots; realtime only to answer an immediate spoken readiness question
- **latency:** Under 2 seconds for an on-demand spoken response; periodic snapshot every 5 minutes without model invocation
- **cost:** Near-zero for periodic checks (structured status aggregation); about $0.001–$0.01 only if a text model must translate unusual failures into speech, dominated by TTS/audio delivery
- **security:** Expose only capability state, timestamps, queue counts, and permission names—not tokens, page contents, URLs, or sensitive memory. Require confirmation before discarding queued browser commands. Mark every state with freshness and source so stale relay data cannot be mistaken for live device state.
- **missing:** A shared typed readiness contract across relay, Mac agent, pendant, and browser extension with freshness/TTL and blocker severity; Pendant-side compact spoken/status event to request and receive readiness without starting a full task; Mac bridge heartbeat carrying permission readiness and browser queue health; Dashboard card and alert policy for stale or blocked nodes

### "“Mark that moment.” Later: “What was I looking at and talking about when I marked it?”"
- **useful because:** A worn assistant should preserve a user-initiated moment across substrates, not merely remember a spoken sentence. Today the pendant, relay, Mac foreground state, and authenticated browser context are separate and there is no privacy-bounded, time-indexed moment capsule that can answer this later with evidence.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background model for capsule enrichment and cross-source summarization; realtime only for the immediate spoken acknowledgement and later short answer
- **latency:** Acknowledge the mark in under 500 ms locally/relay-side; assemble the capsule asynchronously within 30 seconds; retrieve a later answer in under 3 seconds
- **cost:** About $0.01–$0.05 per marked moment, dominated by optional speech transcription and enrichment; cheap retrieval and structured metadata are negligible. No continuous model call is needed.
- **security:** Capture only after an explicit button/voice mark, with a configurable pre-roll (for example 20 seconds) and automatic expiry. Browser data must be limited to the active tab's title/origin and owner-approved extracted text, never passwords or arbitrary page contents. Encrypt the capsule, label every fact with source/time, provide deletion/export, and require confirmation before sharing it.
- **missing:** A pendant-local mark event with a small pre-roll audio ring buffer and an LED/haptic acknowledgement, surviving a dropped LTE link; A relay protocol for authenticated, time-synchronized moment IDs and delayed upload of the marked audio only; A Mac bridge snapshot API that atomically records foreground app/window, project, and active browser tab state at mark time; A browser extension consented snapshot endpoint that returns provenance-carrying page metadata/content for the marked tab; A durable capsule schema, retention/deletion controls, and dashboard timeline/search UI


## Changes it proposed to its own stack

### `integration` — Add a cross-device readiness lease and queue quarantine protocol. The relay periodically polls signed Mac-agent status, assigns each node a freshness deadline, and classifies capabilities as ready/degraded/blocked. Browser commands are held in a durable quarantine when the extension is offline or Mac readiness is false; they cannot execute on reconnection until their TTL, tab/session identity, and risk class are revalidated. The pendant receives only a compact readiness vector and can speak the blocker; the dashboard shows source timestamps and lets the owner inspect or discard queued work.
- **owner gets:** The owner gets an honest answer before waiting: reachable is not the same as usable. A command cannot silently sit for hours and then act against a changed page or newly focused computer.
- effort: Medium: shared schema and relay lease worker, Mac heartbeat endpoint/client, browser queue state machine, pendant status message, dashboard view, and integration tests for offline/reconnect/expired command cases.  ·  risk: A transient network outage could quarantine benign work and feel overly cautious; recover by allowing explicit owner retry and preserving the original plan/receipt. Never auto-replay irreversible actions. Clock skew and stale leases could misclassify a node; use server receive time and monotonic sequence numbers.
- cost: Low ongoing API cost: structured heartbeats and D1 state; roughly $0.001/day per active device at ordinary polling, storage/egress dominate rather than model calls.  ·  latency: Adds at most one status round trip (typically <300 ms) before starting a task; no model latency for classification.
- security: Improves safety by preventing stale browser replay. Requires signed device identity, least-privilege status fields, encrypted queue metadata, and redaction of URLs/page text from pendant and relay logs.
- depends on: Mac-agent status/auth route accessible to relay; browser extension reconnect/heartbeat implementation; relay-to-pendant status event; dashboard queue inspection and explicit discard/retry controls


## What it asked for

_Nothing._
## Its own summary

Established live truth and recorded it: Mac agent v0.5.0 and relay v1.1.0 are reachable; relay is paired/configured and advertises pendant telemetry, speech, persistent state, and durable audio. Mac is not ready because Accessibility and Screen Recording are missing; computer-use is disabled and vision upload consent is absent. Chrome bridge is offline with no active tab and 2 pending commands. Informed judgement, action, and realtime agents. Proposed a cross-device readiness lease/queue quarantine plus an owner-facing spoken readiness capability so stale or blocked work cannot masquerade as completed.

**Biggest unknown:** Whether the owner will grant Accessibility/Screen Recording and reconnect the Chrome extension; without those, GUI/browser claims remain blocked. I also still lack direct authenticated pendant diagnostics and the requested 24 kHz implementation/playback telemetry, so I cannot establish current on-device audio behavior beyond the hardware/configuration facts.

