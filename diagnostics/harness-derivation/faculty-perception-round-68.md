# Harness derivation — faculty-perception — round 68

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **machine-state** — At 2026-08-07T12:34:49Z, Mac bridge is online, but /observe reports foreground app Claude (com.anthropic.claudefordesktop, pid 55646); AI Pendant Agent is running as com.aipendant.agent. Accessibility and Screen Recording are false, inputReachability failed, and UI actions cannot be trusted.
  - evidence: GET /observe HTTP 200 response observedAt 2026-08-07T12:34:49.788Z
- **environment-contradiction** — Owner memory says timezone America/Chicago, while live Mac machine-context reports timezone America/New_York. This contradiction is unresolved and makes calendar/reminder 'today' and scheduled spoken times unsafe to infer.
  - evidence: discover owner remembered.ok text and GET /machine-context machine.timezone
- **browser-state** — At 2026-08-07T12:34Z the browser extension is offline with 5 pending commands; durable browser sessions exist (3 tabs including time.is/UTC and two probe forms), but no authenticated live tab is currently reachable.
  - evidence: GET /ops/status and GET /observe HTTP 200; devices discovery home-chrome offline
- **audio-path** — The Mac pipeline has successfully rendered and uploaded a 24,000 Hz mono s16le response: 75,734 PCM bytes, 1,578 ms audio, 0 clipped samples, accepted by relay for pendant playback. This verifies the Mac TTS/upload leg, not speaker playback on the pendant.
  - evidence: GET /pipeline HTTP 200, pipeline job_309f5663... tts done and relay_result done events at 2026-08-07T12:00:39Z

## Capabilities it proposed

### "Before answering time-sensitive questions or acting across devices, tell me if your view of my world is stale or contradictory, identify the conflict, and ask which source to trust."
- **useful because:** Today the owner profile says America/Chicago while the live Mac says America/New_York; browser connectivity and UI permissions can also silently invalidate actions. A spoken warning prevents wrong calendar times, false completion claims, and unsafe browser work.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background for periodic health snapshots; realtime only to explain a detected conflict in one short spoken sentence
- **latency:** Under 300 ms for cached health; up to 2 s when refreshing Mac/browser state
- **cost:** Near-zero for cached typed signals; occasional small text-model call (roughly <$0.01) only to summarize multiple conflicts; no audio generation unless owner asks
- **security:** Conflict packets must contain only metadata (source, timestamp, freshness, permission state), not page contents or secrets. Timezone and calendar source selection requires owner confirmation; never silently overwrite remembered preferences.
- **missing:** A first-class perception-health/contradiction record with source precedence, TTL, and severity; A precondition hook in judgement/action that blocks or qualifies time-sensitive plans when health is red; Browser heartbeat freshness and pending-command state exposed to the shared context projection; Owner confirmation endpoint for selecting authoritative timezone

### "Did I actually hear the last thing you sent me? If not, tell me exactly where delivery stopped and offer to replay only the missing audio."
- **useful because:** Today the system can prove that Mac rendered 24 kHz audio and the relay accepted it, but it cannot distinguish queued, downloaded, played, interrupted, or never-heard on the pendant. The owner needs an honest answer rather than a false completion claim, especially for reminders and safety-relevant briefings.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** background state machine and deterministic receipts; realtime model only for the owner's short spoken question and explanation
- **latency:** Under 500 ms for a cached answer; under 2 s after requesting a fresh pendant status; replay begins as soon as the missing segment is identified
- **cost:** Negligible metadata storage and relay traffic; no model call for normal state transitions, with a small text-model call only for ambiguous interruptions
- **security:** Store audio identifiers and timing, not transcript or raw audio in the receipt. Do not infer that sound was heard from DAC start alone; expose uncertainty. Replaying private content requires the pendant to remain paired to the owner.
- **missing:** Pendant firmware playback lifecycle events: downloaded, decoder-started, DAC-started, paused, interrupted, completed, and local failure reason; A durable per-audio delivery state machine spanning relay upload/download and pendant playback acknowledgements; A replay-from-last-unheard-segment command with deduplication and expiry; A clear distinction between physical playback and confirmed human hearing


## Changes it proposed to its own stack

### `context` — Implement a perception-health compiler that polls /machine-context, /observe, /ops/status, /browser/status, and relay telemetry; emits signed typed observations with observedAt, TTL, source, confidence, and severity; detects contradictions (starting with owner timezone vs Mac timezone), stale browser heartbeats, and permission-invalid UI reachability. Expose a compact health packet to judgement and a human-readable dashboard/pendant warning. Add a hard precondition for time-sensitive scheduling and claims of UI completion, while allowing non-UI AppleScript reads to proceed.
- **owner gets:** The system will stop confidently telling the owner the wrong time or claiming a click happened. It will explain exactly what is unavailable and recover automatically when the browser or permissions return.
- effort: Medium: shared schema/compiler, 5 adapters, freshness tests, and one judgement precondition; no new model training.  ·  risk: Overblocking if a source is merely stale or the timezone difference is intentional. Recover with explicit severity levels, a one-tap owner confirmation for authoritative timezone, and automatic green transition after fresh matching observations.
- cost: Negligible compute/storage; one small metadata request per health interval. No page content leaves the Mac.  ·  latency: <300 ms from cached packet; refresh adds up to 1 s only for tasks requiring current state.
- security: Improves safety by keeping secrets out of health packets and preventing untrusted UI receipts; timezone preference is sensitive and must be confirmed before persistence.
- depends on: Typed context projection service with provenance/TTL; Judgement precondition hook; Owner-confirmed authoritative timezone; Browser heartbeat freshness adapter

### `integration` — Add a cross-surface 'witness ledger' that assigns one event ID and monotonic sequence to each pendant utterance, relay receipt, Mac planning result, browser command, audio render, download, and physical button interruption. Each node appends only signed facts with its own clock and uncertainty; the relay reconciles them into a causal timeline without pretending wall-clock agreement. Expose a query that returns the last known state and the exact missing acknowledgement for any owner request.
- **owner gets:** The owner can ask 'what happened?' and receive a truthful causal account even when the Mac timezone differs, the browser is offline, or the pendant reconnects late. It prevents a server receipt from being mistaken for an action or a rendered file from being mistaken for something heard.
- effort: High: protocol/schema design, firmware flash-persistent sequence counter, relay append-only storage, Mac/browser adapters, clock-skew reconciliation, and dashboard rendering.  ·  risk: Extra writes and complex reconciliation could consume pendant flash or create duplicate events after power loss. Bound the local journal, use idempotent event IDs, and mark uncertain ordering instead of guessing; rotate and expire sensitive payload references.
- cost: Small relay D1/R2 metadata growth and occasional telemetry bytes; no additional inference cost. Pendant firmware needs a few kilobytes of journal metadata and wear-levelled flash writes.  ·  latency: No added latency on the hot voice path if events are buffered locally; timeline queries may take 1–2 seconds while reconnecting nodes flush journals.
- security: The ledger must contain opaque content hashes and metadata rather than transcripts, URLs, or secrets; encrypt in transit and limit owner-visible history. A tamper-evident chain improves auditability but must not be marketed as proof that the owner heard audio.
- depends on: A firmware-persistent monotonic event counter and bounded journal; Relay append-only event ingestion and deduplication; Mac/browser adapters emitting lifecycle facts; A shared causal-event schema with clock uncertainty


## What it asked for

_Nothing._
