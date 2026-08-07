# Harness derivation — faculty-perception — round 15

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac/browser availability** — Mac agent v0.5.0 is reachable and relay is reachable with macBridgeOnline=true, but browser extension home-chrome is offline with 2 pending commands. Computer-use loop is disabled; Accessibility trusted=false and Screen Recording granted=false, so Mac agent reports ready=false.
  - evidence: GET /ops/status at 2026-08-07: browser online=false, pendingCommands=2, loopEnabled=false, accessibility trusted=false, screenRecording granted=false, relay reachable=true and macBridgeOnline=true.
- **Time-zone truth** — Owner memory says timezone America/Chicago, while live Mac machine-context reports America/New_York. Time-dependent answers and schedules have an unresolved two-hour timezone discrepancy.
  - evidence: owner projection remembered timezone America/Chicago; GET /machine-context liveResponse machine.timezone=America/New_York.
- **Pendant offline queue** — Pipeline contains held offline pendant events: one bookmark captured with link_at_capture=down and two held-alert deliveries surfaced from microSD; these runs remain status=processing rather than terminal.
  - evidence: GET /pipeline: nrf9160 events at 07:12 bookmark, 07:16 held alert (1), 07:22 held alerts (2), metadata storage=microSD origin=pendant-offline-store and status=processing.
- **24 kHz response path** — A recent realtime response was rendered as 24,000 Hz mono PCM, 164,650 bytes, 3,430 ms, with zero clipped samples; relay accepted it for nRF9160 playback. Input telemetry was 15,625 Hz mono PCM, 937,500 bytes, live LTE uploaded, 1,441 ms transcription.
  - evidence: GET /pipeline run job_165a9c9a... events: TTS done 24000 Hz mono PCM, pcmBytes 164650, clippedSamples 0; relay_result done; inputTelemetry sampleRate 15625, uploadState uploaded.

## Capabilities it proposed

### "“Did my last message get through?” (or “What happened to the thing I said when I was offline?”)"
- **useful because:** Today the owner can hear a reply yet still have no trustworthy answer about whether audio uploaded, was held on microSD, reached the relay, was transcribed, or was played back. This gives one evidence-backed delivery receipt across the pendant, relay, Mac bridge, and dashboard, including gaps and stale/non-terminal states.
- **path:** pendant → relay → Mac bridge → dashboard → iOS
- **model tier:** Use the realtime tier only to recognize the spoken query and give a short spoken acknowledgment; use a background/cheap planner to correlate immutable pipeline IDs, pendant offline-store events, relay receipt, Mac job receipt, and playback telemetry, then return a concise result.
- **latency:** A spoken acknowledgment under 500 ms; final receipt within 3 seconds when online. If pendant/relay are disconnected, say exactly what is known locally and queue reconciliation rather than guessing.
- **cost:** Roughly $0.001–$0.01 per query depending on whether transcription/realtime is already active; dominant cost is context/audio, not correlation. Dashboard rendering is negligible.
- **security:** Delivery metadata may reveal message timing and snippets; retain only IDs, timestamps, byte counts, state, and short redacted text by default. Never expose audio contents in the receipt unless requested. No confirmation needed because this is read-only.
- **missing:** A canonical delivery-state schema and correlation IDs shared by nRF9160 offline events, relay jobs, Mac pipeline runs, and playback acknowledgments.; Terminal state transitions for currently-stuck processing runs and an explicit unknown state rather than treating processing as success.; The requested playback-lifecycle telemetry skill on the pendant/bridge, or an equivalent playback acknowledgment event.; A relay/Mac read API that can query one message across all stores without dumping broad history.

### "“When I reconnect, tell me exactly what I missed while the pendant was offline, in order, and what still needs my attention.”"
- **useful because:** The owner currently gets isolated held-alert and bookmark events, not a trustworthy chronological recovery of the offline interval. This would turn intermittent connectivity into a recoverable session: the pendant contributes local event IDs and timestamps, the relay contributes arrival/forwarding history, the Mac reconciles related jobs and notes, and the dashboard presents one ordered, confidence-labeled catch-up with unresolved gaps.
- **path:** pendant → relay → Mac bridge → dashboard → iOS
- **model tier:** Use a cheap background reconciliation model for ordering and summarization; use the realtime model only if the owner asks verbally and needs a short spoken summary.
- **latency:** On reconnect, ingest and index events within 2 seconds; produce a first terse spoken catch-up within 5 seconds, with a detailed dashboard view arriving asynchronously.
- **cost:** About $0.002–$0.02 per reconnect interval, dominated by summarizing event text/audio; most intervals can use deterministic state reconciliation with no model call.
- **security:** Offline events can contain private speech and location-sensitive timing. Encrypt local and relay records, use event IDs and hashes in the default receipt, retain raw audio only under the existing failure-buffer policy, and require confirmation before turning inferred follow-ups into reminders or actions.
- **missing:** A pendant-side append-only event manifest containing monotonic sequence, boot/session ID, capture time, link state, and content hash for every offline alert, bookmark, and failed upload.; A relay reconciliation endpoint that accepts manifests idempotently and returns per-event states: held, uploaded, transcribed, forwarded, played, expired, or unknown.; Mac-side joins between relay event IDs and pipeline/job/note records, with explicit clock-skew handling rather than trusting wall-clock order.; A durable catch-up record and dashboard timeline that preserves uncertainty and prevents already-acknowledged events from being repeated.


## Changes it proposed to its own stack

### `context` — Add a signed timezone authority record with explicit source precedence: owner profile timezone is authoritative for spoken schedules (currently America/Chicago), while machine timezone is retained as an observation (currently America/New_York). Every scheduled job and time answer must display the source timezone and raise a conflict event when they differ; do not silently overwrite the owner setting from machine-context refresh.
- **owner gets:** Reminders and answers about “now,” morning briefs, and daily routines will stop drifting by two hours when the Mac is configured differently from the owner's actual location or preference.
- effort: Small-to-medium: typed context field, conflict detector, scheduler conversion tests, and one dashboard warning; migrate existing routines without changing their wall-clock intent.  ·  risk: Existing routines could be interpreted differently during migration. Recover by preserving original local wall times, showing a review list, and requiring confirmation only for ambiguous routines.
- cost: Negligible API cost; a few context tokens and one D1 preference/conflict record.  ·  latency: No meaningful interactive latency; one cached context lookup.
- security: Timezone is low sensitivity, but avoid inferring location from IP or LTE. Store owner-declared timezone separately from device observations.


## What it asked for

_Nothing._
## Its own summary

Established live facts: Mac agent and relay are reachable, but browser bridge is offline with 2 queued commands; computer-use is disabled and Accessibility/Screen Recording are not granted, so the agent is not ready. The owner's declared timezone (America/Chicago) conflicts with the Mac's live timezone (America/New_York). Pendant pipeline evidence shows offline microSD bookmark/held-alert events and non-terminal processing states. A recent response did complete the 24 kHz PCM render and relay handoff with zero clipping. Proposed a new cross-node delivery-receipt capability and a timezone-authority context change. Still needed: canonical message correlation/state schema, terminal/unknown pipeline semantics, and playback-lifecycle telemetry; these are the decisive unknowns for claiming delivery rather than merely relay acceptance.

**Biggest unknown:** Whether the pendant actually completed local speaker playback for the recent 24 kHz response, and whether the held microSD events were durably acknowledged after surfacing. The unavailable pendant diagnostics/playback telemetry prevent establishing end-to-end user-heard state.

