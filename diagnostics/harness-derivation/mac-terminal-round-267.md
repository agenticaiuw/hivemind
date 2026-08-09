# Harness derivation — mac-terminal — round 267

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **bench USB observability** — The newly granted mac_usb_serial_diagnostics schema still does not resolve against the live inventory; no serial/USB capability is callable. The two chips cannot be inspected through that tool today, only through existing shell capture scripts dispatched as run_shell.
  - evidence: mac_usb_serial_diagnostics call returned unresolved; nearest action:get_mac_status score 0.225, no serial/USB inventory capability.

## Capabilities it proposed

### "“Test my pendant audio end to end and tell me whether it is actually ready to wear.”"
- **useful because:** The owner currently has a prototype that can encode, decode, resample, and bridge audio, but no single command proves that the microphone, nRF9160, ESP32, relay, and playback path work together. A spoken pass/fail with measured round-trip latency, packet loss, underruns, clipping, and codec CPU margin would turn debugging from guesswork into a wearable-quality answer. This is the single most useful capability in this round.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** background for the test plan and measurements; realtime only to narrate the final result if the owner asks by voice
- **latency:** Start within 2 seconds; a 30–60 second fixture run is acceptable; final spoken summary under 5 seconds after capture
- **cost:** Usually <$0.02 per run; most cost is local capture and measurement, not model tokens
- **security:** The test should use a generated signal or a local speaker/loopback fixture, never an open microphone recording. Store only aggregate metrics and a short hash of the firmware/build, with raw audio deleted unless the owner explicitly asks to retain it.
- **missing:** A bounded host serial reader/parser for the two currently connected USB devices, or a documented shell wrapper around diagnostics/dual_chip_autocapture.sh; A known acoustic fixture or electrical loopback path for the ESP32 output; A shared test-run ID emitted by pendant, bridge, relay, and Mac so packet and audio measurements can be joined

### "“Why did that thing fail? Reconstruct what the pendant heard, what the relay dispatched, what the Mac ran, and what actually changed.”"
- **useful because:** Today the owner can see fragments—job status, journal, relay state, and (eventually) UART logs—but has to manually correlate unrelated IDs and timestamps. A single spoken forensic answer would distinguish queued, dispatched, started, failed, cancelled, orphaned, or completed-with-no-observed-effect, then offer the next safe retry. This is a genuinely hive-only answer: the pendant has intent and transport evidence, the relay has delivery, and the Mac has execution and filesystem/UI evidence.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background model for correlation and summarization; realtime only for the short spoken answer
- **latency:** Under 3 seconds when records are already present; up to 15 seconds to collect missing local records
- **cost:** <$0.01 for normal correlation; token cost is bounded by sending event summaries, not raw logs
- **security:** Redact command environment, bearer tokens, mail contents, and raw audio before correlation. File mutations and retries remain separate actions and require the owner's existing confirmation policy. Persist only hashes, IDs, statuses, timestamps, and selected error text.
- **missing:** A durable correlation key propagated from pendant turn ID through relay job, POST /execute job, action receipt, and browser command; A server-side read-only evidence joiner that reads GET /jobs/:jobId, GET /journal/:jobId, GET /jobs/:jobId/receipts, relay job status, and pendant UART summaries; Boot reconciliation that marks interrupted jobs honestly before the explainer runs; currently processing records can survive a crash forever

### "“I’m leaving my Mac—tell me whether the pendant can carry on without it, what is queued, and what will be lost when I walk away.”"
- **useful because:** The owner wears the pendant but the current system has no honest boundary report between Mac-backed and wearable-only behavior. A one-sentence handoff would inspect pendant link/battery and queued turns, relay reachability, unfinished Mac/browser jobs, and the last known audio transport state, then state exactly which requests will continue, pause, or expire. It prevents walking away believing a Mac action or conversation is still running when only a stale LED says so.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background model assembles the handoff from structured status; realtime reads it aloud on the pendant
- **latency:** 2 seconds from a button request; no network retry longer than 5 seconds; offline mode must still produce a locally cached, age-stamped answer
- **cost:** <$0.005 per handoff; mostly structured status retrieval
- **security:** Expose only action names, statuses, ages, and capability boundaries—not command strings, browser page text, audio, or secrets. Never claim LTE continuity from USB-only evidence; distinguish Mac-attached bench mode from wearable mode.
- **missing:** A single authenticated handoff endpoint that joins pendant transport state, relay reachability, Mac active jobs, browser sessions, and queued outbox records; A capability matrix saying which operation can migrate from Mac to relay/pendant and which must stop; A compact cached handoff record on the pendant with monotonic timestamp and freshness, rather than inferring readiness from the LED pattern alone

### "“Lock down my whole AI setup right now, and tell me exactly what was revoked and what could not be reached.”"
- **useful because:** A lost pendant, unattended Mac, or exposed browser session is a multi-surface privacy event, not a single-device logout. The owner cannot currently issue one authoritative spoken panic command that revokes relay work, closes browser sessions, disables Mac execution, ends iPhone-mirroring control, and clears sensitive pending payloads while honestly reporting unreachable surfaces. This would provide a decisive emergency action rather than a collection of manual logouts.
- **path:** pendant → relay → mac-bridge → browser → iOS → dashboard
- **model tier:** realtime for the immediate command and terse result; background for post-event verification and an audit summary
- **latency:** Begin locally on the pendant in under 300 ms; revoke reachable sessions within 5 seconds; continue verification asynchronously and report stale/unreachable surfaces with age
- **cost:** Usually <$0.01; dominated by verification requests, not model inference
- **security:** This is intentionally destructive to active sessions and queued work, so require a dedicated physical confirmation on the pendant or a pre-authorized emergency phrase. Use signed, replay-resistant revocation tokens; never transmit secrets in the spoken response. The pendant must fail closed locally even if relay and Mac are unreachable.
- **missing:** A revocation protocol shared by relay, Mac agent, browser extension, iOS-control facet, and pendant firmware; A local pendant panic state that stops recording/playback, invalidates cached turn credentials, and queues revocation until connectivity returns; Idempotent revoke endpoints with per-surface receipts, expiry, and an explicit unreachable result; A recovery flow for re-authentication and restoring only explicitly chosen queued work

### "“Let this task use my browser and Mac for the next hour, but nothing else—and show me when that permission expires.”"
- **useful because:** The current system has broad standing reach, but no owner-visible, time-limited delegation that follows one task across the pendant, relay, Mac, browser, and iPhone surface. A scoped lease would let the owner authorize a concrete goal without granting an indefinite ambient power, and would make expiry, use, and attempted out-of-scope actions understandable from the pendant.
- **path:** pendant → relay → mac-bridge → browser → iOS → dashboard
- **model tier:** realtime for interpreting and confirming the lease; background for policy compilation, expiry checks, and audit summarization
- **latency:** Issue or revoke a lease in under 2 seconds; enforce it before every cross-surface action; expiry must work offline on the pendant and relay
- **cost:** <$0.01 per lease; most work is local policy evaluation and signed state propagation
- **security:** A lease must be narrow by surface, action family, target, and duration, with a physical confirmation for sensitive scopes. No model should be able to silently broaden it. Store hashes and receipts rather than page contents or secrets, and make revocation win over queued work.
- **missing:** A signed capability-lease format with subject, allowed surfaces/actions, target constraints, expiry, nonce, and revocation status; Enforcement hooks in relay dispatch, Mac /execute, browser commands, and iOS-control actions; Offline pendant storage for the active lease and a truthful expired/revoked indicator; A dashboard view showing exactly which actions consumed the lease


## What it asked for

_Nothing._
## Its own summary

Recorded two capabilities that are not available today: a cross-surface emergency lockdown with truthful unreachable reporting, and time-limited signed capability leases spanning pendant, relay, Mac, browser, and iOS. Both require new protocol/enforcement work rather than merely wiring existing routes.

**Biggest unknown:** Whether an existing backlog item already covers emergency revocation or delegated leases under different names; I did not perform further discovery as instructed.

