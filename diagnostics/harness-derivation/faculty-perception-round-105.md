# Harness derivation — faculty-perception — round 105

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac control reachability** — At 2026-08-07T14:46Z the AI Pendant Agent is running, but Accessibility and Screen Recording are not trusted for com.aipendant.agent; synthesized UI events are rejected and UI actions are explicitly untrustworthy despite reporting success. AppleScript automation grants are present and relay/mac bridge are reachable.
  - evidence: GET /observe and GET /ops/status both returned trusted=false, screenRecording=false, inputReachability.status=failed, uiActionsWillReachTheScreen=false; automationMissing=[]; relay reachable and macBridgeOnline=true.
- **browser handoff** — At 2026-08-07T14:46Z the browser extension home-chrome is offline with 11 pending commands and no active tab metadata; browser actions fail rather than execute.
  - evidence: GET /browser/status returned online=false, pendingCommands=11; GET /logs records browser_navigate failure: extension offline and repeated bridge-launch attempts failed due malformed action payloads (missing command/script/appName).
- **pipeline continuity** — The pipeline contains an old nrf9160 alert-delivery run and a cloud-relay spoken-reply run still marked processing, while a later routine run completed but blocked on shell approval; this is historical telemetry, not evidence of a connected pendant.
  - evidence: GET /pipeline returned nrf9160 run job_27616... status=processing created 2026-08-07T07:22Z, cloud-relay run job_165a... status=processing, and completed routine job_309f... with waiting-for-approval event; device discovery shows no pendant registered.
- **device-status route scope** — The Mac agent does not expose GET /v1/devices/status; querying it here returns 404. Current device presence must come from the orchestrator device registry, not this local route.
  - evidence: probe_http GET /v1/devices/status returned HTTP 404 with 'No such route on this agent'.

## Capabilities it proposed

### "What was I doing around that moment?"
- **useful because:** The owner cannot today reconstruct a trustworthy, private timeline across bodies: a pendant conversation, the Mac app in front of them, authenticated browser activity, and relay jobs remain separate logs. This would answer questions such as when a thought was captured, which document was open, whether a browser form was only drafted, and whether a spoken result actually reached a device—without pretending that any one log is the whole truth.
- **path:** pendant → mac-planner → mac-vision → browser-extension → relay-realtime → unified → faculty-perception
- **model tier:** A cheap background correlator builds the timeline and embeddings; use the expensive realtime tier only when the owner asks conversationally and needs an immediate spoken answer.
- **latency:** Timeline entries may settle within 30–60 seconds; an on-demand answer should return in under 3 seconds from indexed metadata. Raw audio or page content is fetched only for an explicitly requested interval.
- **cost:** Low ongoing cost: local/event metadata correlation and compact hashes dominate; occasional small-model summarization is under $0.01 per query. No continuous expensive-model call.
- **security:** This is highly sensitive behavioral data. Keep raw audio, screenshots, and private page text on-device with short retention; relay receives only encrypted event IDs, coarse timestamps, and delivery state. Require explicit opt-in, visible recording indicator, per-source pause controls, and confirmation before exposing another person's content. Never infer that a UI action occurred from a receipt alone.
- **missing:** A consented cross-body event ledger with monotonic device timestamps and clock-offset calibration; A local pendant event marker for button presses, audio segment boundaries, disconnects, and resumptions that survives offline periods; Mac foreground-app and browser-session event adapters that emit metadata without page content by default; Relay correlation IDs and delivery acknowledgements that link spoken input/output to the same episode; A query/index layer that returns cited intervals and confidence instead of an ungrounded narrative; Owner-configurable retention, export, and deletion controls across local storage and relay copies


## Changes it proposed to its own stack

### `context` — Add a perception evidence contract and freshness reconciler: every job/action receipt is joined with contemporaneous /observe, /browser/status, relay device status, and pipeline delivery state. Classify claims as observed-success, acknowledged-only, queued, stale, blocked, or unverifiable; attach source timestamps and invalidate UI-action success when inputReachability is failed. Persist only compact hashes/metadata, not page contents or screenshots.
- **owner gets:** The owner gets honest answers instead of a green receipt for an action that never reached the screen, or an old pendant pipeline record presented as live. Failures become actionable (grant TCC, reconnect bridge, or wait for device) without exposing private content.
- effort: Medium: define evidence schema, reconciliation worker, and adapters for existing routes; add tests for offline browser, absent pendant, stale processing, and failed TCC input.  ·  risk: A conservative classifier may say unverifiable when an action really succeeded; recover by showing the raw receipt and allowing an explicit refresh. Clock skew and delayed relay acknowledgements need bounded grace windows.
- cost: Negligible storage for metadata and hashes; one cheap background reconciliation pass per job. No additional model call for classification.  ·  latency: Adds roughly 100–300 ms for parallel local reads when a live answer is requested; background reconciliation is asynchronous.
- security: Reduces leakage by avoiding content capture; stores only route names, timestamps, status, and evidence hashes. Access to raw evidence remains bearer-protected.
- depends on: A typed cross-surface perception snapshot (new); A durable stale-run/watchdog policy; Existing /observe, /ops/status, /browser/status, /pipeline, /jobs and relay device-status reads


## What it asked for

_Nothing._
## Its own summary

Fresh perception is established and recorded: Mac bridge/relay are reachable, but Accessibility and Screen Recording are false for com.aipendant.agent, so UI actions cannot be trusted; browser home-chrome is offline with 11 pending commands; malformed bridge-launch actions failed; pipeline contains historical/still-processing records and no live pendant is registered. I sent these facts to mac-vision and faculty-judgement. I also recorded a new context-layer change: reconcile every receipt against contemporaneous observation and classify it verified, contradicted, queued, stale, blocked, or unverifiable. I still need no additional system context this round. What remains is owner-side: grant TCC permissions if GUI control is wanted, reconnect/enable the browser bridge for private web access, and register a real pendant before claiming wearable delivery. Note that /v1/devices/status is not a route on the Mac agent; device presence must come from the orchestrator registry.

**Biggest unknown:** Whether the owner will manually enable the exact AI Pendant Agent binary in macOS Privacy settings and reconnect the browser extension; neither can be changed or verified as ready from this agent.

