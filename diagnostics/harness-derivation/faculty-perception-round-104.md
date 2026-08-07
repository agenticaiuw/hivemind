# Harness derivation — faculty-perception — round 104

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac input and vision permissions** — At 2026-08-07T14:43:35Z AI Pendant Agent is running but Accessibility trusted=false, synthesized events rejected, inputReachability failed, screenRecording=false; computer-use loop disabled and vision upload consent absent.
  - evidence: GET /observe and GET /ops/status live responses.
- **Reachable devices** — At 2026-08-07T14:43Z home-macbook-bridge is online; home-chrome extension is offline; no pendant device is registered in live device discovery.
  - evidence: discover devices plus GET /ops/status and GET /browser/status.

## Capabilities it proposed

### "What changed since my last check, and which device or permission caused the change?"
- **useful because:** A point-in-time status is not enough for a wearable: the owner needs to know that Chrome went offline, a Mac action became approval-blocked, or a relay response arrived after a link outage without confusing old telemetry for current reality. A signed, correlated delta lets judgement react to transitions rather than repeatedly re-reading snapshots.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → faculty-perception → faculty-judgement → dashboard
- **model tier:** No expensive model for collection or correlation; use a deterministic event correlator and a cheap summarizer only when spoken output is requested.
- **latency:** Continuous ingestion; publish a delta within 1 second of an event, and retain a compact 24-hour transition history.
- **cost:** Low API cost: structured events and hashes dominate storage, not inference. One short summarization call only when the owner asks for a spoken explanation.
- **security:** Store hashes, timestamps, status, and provenance—not page text, audio, or secrets. Bind deltas to request/job/pipeline IDs and mark clock uncertainty. Never infer delivery from an optimistic local receipt.
- **missing:** A durable cross-surface correlation stream carrying one request ID from capture through relay, Mac/browser action, receipt, and audio delivery; Deterministic transition/diff endpoint with monotonic sequence numbers and freshness/clock metadata; Per-surface event acknowledgements so perception can identify a missing hop rather than report generic failure

### "Make sure that change actually took effect, and tell me immediately if the screen, browser, or wearable disagrees with the expected result."
- **useful because:** Today an action can receive a local success receipt while doing nothing, be queued in an offline browser, or finish on the Mac without producing the expected external state. The owner should have an independent witness that verifies the postcondition—not merely that a command was accepted—and explains the first point of disagreement.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** Use deterministic postcondition checks first (accessibility tree, browser DOM/page state, relay/device acknowledgement); invoke the slower vision model only when structured checks cannot establish the result. Use realtime only for the owner-facing alert.
- **latency:** Verify within 2 seconds for Mac/browser changes and within the next confirmed wearable heartbeat for pendant effects. Alert only on disagreement or timeout, not on every successful action.
- **cost:** Low for structured checks; occasional screenshot/vision inference is the dominant cost and should be sampled only when needed.
- **security:** Screenshots, DOM extracts, and sensor evidence may contain private content; keep evidence local by default, redact secrets, retain short-lived hashes plus minimal excerpts, and require confirmation before transmitting visual/audio evidence to the relay. Never claim verification when permissions are missing.
- **missing:** A postcondition contract attached to each action (expected app/browser/device state, timeout, and acceptable variants); Independent verification adapters for Mac accessibility/screen, browser DOM/tab state, relay delivery/playback acknowledgement, and pendant hardware state; A disagreement resolver that marks results as verified, contradicted, unknown, or stale and routes only actionable failures to the owner


## Changes it proposed to its own stack

### `integration` — Add a deterministic perception event ledger that assigns a monotonic sequence and correlation ID to every cross-surface transition (pendant capture, relay accept, Mac plan, browser command/result, approval block, receipt, TTS upload/playback). Expose GET /perception/deltas?since=cursor and GET /perception/trace/:correlationId. Each record must include observedAt, source clock, freshness, and terminal evidence; no record may claim success from an optimistic enqueue.
- **owner gets:** When the owner asks what happened, they get the exact missing hop—e.g. “Chrome was offline, so the command stayed queued”—instead of a misleading success or a stale pendant story.
- effort: Medium: schema plus append-only D1/file ledger, adapters at existing pipeline/browser/job/relay event writers, cursor endpoint, and a compact dashboard/voice rendering.  ·  risk: Duplicate or out-of-order events could produce confusing traces; recover with idempotency keys, sequence gaps marked explicitly, and rebuild from existing pipeline/job logs. Avoid storing sensitive payloads; retain metadata and hashes only.
- cost: Negligible inference cost; modest D1/storage writes and reads per event.  ·  latency: Sub-millisecond local append, typically under 1 second end-to-end for delta visibility.
- security: Improves auditability while reducing data exposure if payloads are excluded. Correlation IDs must be unguessable and endpoints bearer-protected.
- depends on: Owner must eventually connect a pendant for live device events; until then mark pendant edges absent rather than simulated.; Browser extension heartbeat must become online for browser edges to be observed.; Existing pipeline, browser, jobs, and relay writers must emit stable request/correlation IDs.


## What it asked for

_Nothing._
