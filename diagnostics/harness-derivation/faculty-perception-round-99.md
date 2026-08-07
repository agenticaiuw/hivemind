# Harness derivation — faculty-perception — round 99

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **macOS timezone** — Live /machine-context reports machine timezone America/New_York, while owner memory says authoritative timezone America/Chicago; timezone is unresolved and scheduled routines should not be interpreted without an explicit authority.
  - evidence: GET /machine-context at 2026-08-07T14:28:23Z returned machine.timezone=America/New_York; owner remembered context says timezone America/Chicago.
- **live computer reachability** — Mac bridge is online and relay reachable, but browser extension is offline with 10 pending commands; computer-use UI input is not trustworthy because Accessibility and Screen Recording are denied for the running AI Pendant Agent binary.
  - evidence: GET /ops/status returned relay.reachable=true, macBridgeOnline=true, browserExtension.online=false, pendingCommands=10, permissions.ready=false; GET /observe returned uiActionsWillReachTheScreen=false and inputReachability.status=failed.
- **pendant presence** — No physical pendant is registered or online; only home-macbook-bridge is online among reachable devices. Pendant pipeline records are historical/simulated, not evidence of current wearable connectivity.
  - evidence: discover(devices) returned home-macbook-bridge online, home-chrome offline, cloudflare-contract-test offline, with no pendant; GET /pipeline contains historical nrf9160 events.
- **24 kHz audio reality** — The Mac bridge generated a 24 kHz mono s16le PCM response (75,734 bytes, 1,578 ms, no clipping) and relay accepted the payload in a historical pipeline run, but there is no evidence of pendant download or playback because no pendant is registered.
  - evidence: GET /pipeline returned completed TTS event with sampleRate=24000, format=s16le, pcmBytes=75734, clippedSamples=0, followed by relay_result accepted; discover(devices) showed no pendant.

## Capabilities it proposed

### "“Did that actually reach me?” — give me one trustworthy delivery answer for any spoken reply or background result, saying which surface received it, when, and whether it was merely queued, downloaded, or played/read."
- **useful because:** Today the relay can report an accepted PCM payload even when no pendant is registered, and the Mac pipeline mixes historical nRF9160 records with live Mac jobs. The owner needs a reality-based receipt, not a success-looking upload: distinguish Mac/browser presentation, relay acceptance, pendant download, and confirmed playback/read, and explicitly say when no wearable exists.
- **path:** relay-realtime → relay → mac-planner → browser-extension → unified → faculty-perception
- **model tier:** Use deterministic event reconciliation and a cheap background model only to phrase ambiguous timelines; reserve gpt-realtime-2.1 for the owner's live follow-up question.
- **latency:** Live status lookup under 500 ms; background reconciliation within 1 minute of each event. No expensive model call for normal receipts.
- **cost:** Usually near-zero model cost for structured events; occasional short text synthesis under $0.001 per receipt. Storage and polling dominate.
- **security:** Receipts may expose private page titles or spoken-response text, so return minimal metadata by default and retain exact payload provenance only under the owner's authenticated account. Never claim playback from relay upload alone; require device acknowledgment with monotonic event ID and reject stale or simulated records.
- **missing:** Authoritative relay device registry plus delivery/download/playback acknowledgments for each audio event; A single event schema tagging live versus historical/simulated pipeline records and correlating relay job, Mac job, audio object, and device receipt; Browser extension reconnect/heartbeat so browser presentation can be distinguished from a queued command; Owner confirmation of authoritative timezone (machine currently says America/New_York while owner memory says America/Chicago)

### "“Why did you tell me that?” — for any answer or status report, show me the compact evidence trail that supported it: the observed source, observation time, live-versus-history status, conflicting facts, and exactly what remains unverified."
- **useful because:** The owner currently cannot distinguish a directly observed fact from stale pipeline history, a relay acceptance, an inferred answer, or a failed GUI action that only produced a success-looking receipt. This gives them an inspectable explanation of the system's belief without requiring them to trust the agent's wording.
- **path:** faculty-perception → unified → relay-realtime → mac-planner → browser-extension → dashboard-ux
- **model tier:** Deterministic evidence assembly first; use a cheap background text model only to compress the evidence into plain language. Use realtime only when the owner asks verbally during a live conversation.
- **latency:** Evidence lookup and rendering under 1 second for recent events; historical trace retrieval under 3 seconds. No model call on the normal path.
- **cost:** Near-zero model cost for structured traces; occasional compression below $0.001. Storage cost is the dominant expense because immutable observation metadata must be retained.
- **security:** Evidence can reveal private URLs, mail subjects, account names, or audio metadata. Redact secrets and minimize content by default; require authenticated access for full traces. Preserve source hashes and timestamps, not unnecessary payload copies. Clearly label inference and never allow the explanation layer to upgrade an unverified event into fact.
- **missing:** An immutable, append-only observation ledger shared by relay, Mac, browser, and pipeline, with source, timestamp, freshness, live/history provenance, confidence, and correlation IDs; A contradiction record that keeps mutually inconsistent observations instead of silently selecting one; A response-to-evidence link from every spoken or dashboard answer to the exact observations used; A dashboard and voice schema for stating unverified, stale, and impossible-state conditions

### "“Is my pendant actually ready for the day?” — run a preflight that verifies the wearable’s microphone and speaker loopback, clock, storage, radio registration, relay reachability, and Mac handoff, then give me one report with each check’s last verified time and the first failing link."
- **useful because:** A wearable can appear connected while audio capture, playback, storage, clock, or relay delivery is broken. The owner should learn this before relying on it, rather than discovering the failure during an important conversation. The report must remain useful when the pendant is absent by explicitly saying which checks are impossible, not passing historical telemetry as readiness.
- **path:** pendant → relay-realtime → relay → mac-planner → unified → dashboard-ux
- **model tier:** Firmware and relay perform deterministic tests and produce structured results; a cheap text model formats the report. Realtime is only needed if the owner asks for the result by voice.
- **latency:** Local checks under 5 seconds; network and Mac checks under 15 seconds with per-link timeouts. A failed or absent device must return promptly rather than waiting for retry exhaustion.
- **cost:** No routine model cost; one small relay status exchange and occasional diagnostic audio payload. Hardware cost is zero for existing sensors, with optional loopback fixture during manufacturing.
- **security:** Do not upload microphone loopback content; use a generated tone or cryptographic test pattern and discard it. Device identity and radio status must be authenticated. Never silently change firmware, pairing, or network settings during preflight; any repair action requires separate confirmation.
- **missing:** A pendant-local diagnostic protocol for mic/speaker loopback, RTC, flash/microSD integrity, battery, and radio state; An authenticated relay challenge/response and device registration lease; A Mac-side handoff test that does not rely on unsafe GUI input; A readiness state machine with per-check freshness and explicit absent/unknown/failing states


## Changes it proposed to its own stack

### `relay` — Partition pipeline telemetry into live device sessions and archival history, with a device-presence lease and a provenance field on every event. The relay must reject or quarantine nRF9160 upload/download/playback events when no corresponding device registration and active lease exists; historical/simulator fixtures remain queryable only under an explicit history view. Add a reconciliation endpoint that reports impossible transitions (for example “response waiting for pendant” while no pendant is registered) instead of presenting them as current success.
- **owner gets:** The owner will stop being told that audio is waiting on or reached a pendant that does not exist. Every answer about what happened will reflect the physical world, while old test data remains available for debugging without masquerading as live behavior.
- effort: Medium: D1 schema/event-state migration, lease heartbeats, ingestion validation, and updates to /pipeline plus dashboard labels; add fixture migration and tests for offline, reconnect, duplicate, and stale-device cases.  ·  risk: Existing historical dashboards or tests may expect mixed records and appear empty after the split. Recover by preserving immutable archive rows and providing an explicit history query/compatibility view; never delete telemetry.
- cost: Negligible model cost; small D1/R2 metadata growth and one heartbeat write per connected device. No additional hardware cost.  ·  latency: One local registry/lease lookup on ingestion, typically under 20 ms; no impact on audio streaming path if validation is asynchronous with a quarantine fallback.
- security: Improves privacy and integrity by preventing stale device claims. Device leases and acknowledgments must be authenticated and scoped to a paired device; do not expose payload text in public status.
- depends on: Authoritative relay device registry and authenticated device lease/ack semantics; A typed live-vs-history provenance field shared by relay and Mac pipeline; Explicit /pipeline?view=live versus /pipeline?view=history semantics


## What it asked for

_Nothing._
