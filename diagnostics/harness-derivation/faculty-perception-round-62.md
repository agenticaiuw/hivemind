# Harness derivation — faculty-perception — round 62

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-observation-2026-08-07T12:20Z** — The running AI Pendant Agent is not Accessibility-trusted or Screen Recording-enabled: /observe reports inputReachability=failed, uiActionsWillReachTheScreen=false, and warns UI actions may report success while doing nothing. /ops/status reports permissions.ready=false. Browser extension is offline with 5 pending commands. Relay and Mac bridge are reachable.
  - evidence: GET /observe and GET /ops/status both returned HTTP 200 at 2026-08-07T12:20:51Z; exact fields are in responses.

## Capabilities it proposed

### "Before you tell me a task is done, independently check whether it really happened across my Mac, browser, relay, and pendant, and say what is verified versus merely reported."
- **useful because:** Today a UI action can return a success-shaped receipt while /observe says synthesized events do not reach the screen; browser commands can sit pending while the extension is offline; and pipeline records can remain processing after late events. The owner needs trustworthy truth, not optimistic receipts.
- **path:** mac-planner → mac-vision → browser-extension → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use cheap/background model for routine receipt reconciliation; reserve realtime for the owner's spoken request or an ambiguous contradiction. Perception should be deterministic first, with model summarization only after evidence collection.
- **latency:** 2–5 seconds for a post-action check; immediate local checks (<500 ms) for permission, browser-online, and terminal pipeline state. If a remote/browser probe exceeds 5 seconds, return pending with a timestamp rather than claim success.
- **cost:** Usually near-zero model cost for typed state comparisons; roughly one small text-model call only when evidence conflicts and needs a spoken explanation. Dominant cost is Mac/browser/relay round trips, not inference.
- **security:** Reads job receipts, pipeline metadata, browser tab metadata, and local observation state; must not upload page contents or secrets merely to verify an action. Destructive actions still require existing confirmation. Mark UI actions unverified whenever Accessibility or Screen Recording is unavailable, rather than inferring from the action response.
- **missing:** A first-class verification endpoint/job that accepts an action receipt and gathers /observe, /ops/status, /pipeline, /browser/status, and job receipt evidence with one correlation ID; Typed evidence states (verified, contradicted, pending, unverifiable) and freshness/expiry on each observation; A policy in faculty-judgement that refuses to convert an unverifiable UI receipt into 'done'

### "When I reconnect after being offline, tell me exactly what I missed and what I actually received: reconstruct the ordered chain from pendant capture through relay, Mac work, browser changes, audio delivery, and my acknowledgement, and highlight any gaps or duplicates."
- **useful because:** Today the system can know that a command, response, or alert exists in separate logs, but the owner cannot get one trustworthy account of their lived continuity. This matters when LTE drops, the pendant stores alerts, the bridge reconnects late, or audio is rendered but never played. It distinguishes 'created', 'delivered', 'heard', and 'acknowledged' instead of silently treating them as the same event.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Use a deterministic event join and a cheap background summarizer; use the realtime tier only when the owner asks while reconnecting and needs a short spoken account. No expensive model is needed to identify missing links or duplicates.
- **latency:** Return a first timeline in under 2 seconds from stored events; enrich it asynchronously when a bridge or browser comes back. Never wait indefinitely for a missing device—label the link unknown with its last observation time.
- **cost:** Low: event joins and hashes dominate, with at most one small summarization call per reconnect. Storage grows with compact event metadata, not audio or page contents.
- **security:** The timeline may reveal private browser destinations, messages, or audio text. Keep sensitive payloads on their originating surface; expose redacted labels and hashes by default, with explicit owner request for content. Do not claim an audio item was heard without pendant playback telemetry and acknowledgement.
- **missing:** A cross-surface event envelope with stable event IDs, parent IDs, monotonic device sequence numbers, observedAt, deliveredAt, playedAt, and acknowledgedAt; Pendant-local durable playback and acknowledgement telemetry that survives link loss; A relay reconciliation endpoint that joins offline pendant events with Mac pipeline/job records without duplicating late arrivals; A compact owner-facing timeline and gap vocabulary: created, forwarded, delivered, played, acknowledged, expired, duplicate, or unknown


## Changes it proposed to its own stack

### `context` — Add a read-only perception evidence correlator that runs after every action receipt. It assigns one correlation ID, snapshots /observe, /ops/status, /browser/status, /pipeline, and the relevant /jobs/:jobId/receipts or /journal/:jobId, then applies deterministic rules: terminal pipeline + matching receipt + reachable target = verified; Accessibility/Screen Recording false for GUI steps = unverifiable; browser offline or pending command = pending; contradictory target state = contradicted. Persist only hashes, statuses, timestamps, and source pointers, not page contents. Expose GET /verification/:correlationId and include its verdict in spoken completion receipts.
- **owner gets:** The owner stops hearing 'done' when an action only produced a receipt-shaped response. They get a compact explanation such as 'reported success, but not verified because the agent cannot reach the screen' or 'verified in Calendar at 12:21.'
- effort: Medium: typed schema, correlator worker, route, and integration into job completion; deterministic test fixtures for stale, pending, contradictory, and inaccessible states.  ·  risk: A stale observation could be mistaken for current truth; every evidence item needs observedAt and a short TTL, and expired evidence must become unknown. A verifier must never retry or mutate an action. Recovery is to show raw source pointers and let faculty-action re-check explicitly.
- cost: Negligible API/model cost for typed comparisons; small D1/storage growth for compact evidence records. No page content or audio needs to be retained.  ·  latency: Adds <500 ms for local state and up to 2–5 s when waiting for bridge/browser status. Completion can be delivered as pending rather than blocking on a slow or offline surface.
- security: Improves safety by preventing false claims. Evidence is least-privilege metadata; sensitive browser contents remain on the browser/Mac and are not sent to the verifier.
- depends on: A stable correlation ID carried from POST /plan or POST /execute through job receipts and pipeline events; Faculty-judgement consuming verification verdicts instead of raw action success; Existing /observe, /ops/status, /pipeline, /browser/status, and receipt routes


## What it asked for

_Nothing._
