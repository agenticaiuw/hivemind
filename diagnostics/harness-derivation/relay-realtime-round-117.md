# Harness derivation — relay-realtime — round 117

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "What happened to the thing I asked you to do?"
- **useful because:** Owners routinely ask for status while away from their Mac. A reliable spoken status closes the loop without forcing them to open a laptop.
- **path:** pendant → relay → mac-bridge → mac-planner
- **model tier:** realtime for the voice prompt; a cheaper tier can format stored receipts into a sentence if needed, but no heavy reasoning is required.
- **latency:** Under a second when a receipt exists locally; otherwise a graceful fallback that says it’s still queued or unknown and offers to check later.
- **cost:** Very low per invocation: one relay metadata read and a short spoken reply. The dominant cost is storage reads if receipts are large, so store summaries.
- **security:** Job receipts may contain sensitive titles or URLs. Store and return only what the owner needs to hear, and redact anything beyond a short task name and status.
- **missing:** Implemented relay_job_status tool or equivalent relay endpoint; today it’s a schema-only grant.; Durable job receipt storage in the relay (D1 or Durable Object).; A consistent job ID returned to the relay whenever work is handed to the Mac.

### "Handle this across my Mac and authenticated browser, and keep going if I walk away; if one step fails, recover or reroute automatically, then tell me exactly what was completed, what was skipped, and what I need to decide."
- **useful because:** Today the owner must remain in the voice turn and manually reconcile partial results. A single cross-surface transaction would let the worn pendant start work, the Mac and browser cooperate, and the relay return a trustworthy outcome even after LTE or Mac interruptions—something no individual node can provide.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use realtime only to capture the request and speak urgent exceptions; use a cheaper background planner/worker for execution, retries, reconciliation, and final summarization.
- **latency:** Acknowledge intent within 1 second; execute asynchronously. Speak only urgent ambiguity/failure immediately, otherwise deliver a compact completion report when the pendant reconnects (target under 30 seconds after final action).
- **cost:** Roughly $0.01–$0.10 per multi-step job depending on retries and browser/Mac model calls; realtime cost is limited to the initial and exception turns, while action execution dominates.
- **security:** The job may use authenticated browser sessions and mutate Mac data. Persist only scoped task state and redacted receipts, bind every action to the initiating session, encrypt queued payloads, and make the owner able to cancel/undo from the pendant or dashboard. Do not transmit page contents to the realtime model unless needed for a decision.
- **missing:** A durable cross-surface transaction record with idempotency keys, leases, retry/reroute policy, and dependency-aware checkpoints; A worker that can resume jobs after Worker/Mac/browser disconnects and correlate typed results from both surfaces; A pendant downlink/event inbox that can queue a completion or urgent exception until the next connection; A unified result schema that distinguishes completed, skipped, failed, and owner-decision-required steps

### "Why did you do that, and show me the evidence? For any action taken through my pendant, give me a short spoken explanation tied to the exact Mac/browser observations, plan decision, and resulting change."
- **useful because:** The owner currently gets action outcomes but cannot audit the reasoning across surfaces from the wearable. A provenance answer would make autonomous assistance trustworthy: it separates what the system saw, inferred, attempted, and changed, instead of asking the owner to inspect scattered logs and browser state.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Generate the provenance record deterministically during execution; use a cheaper background model to summarize it, and realtime only when the owner asks the spoken question.
- **latency:** Return a two-sentence spoken answer in under 2 seconds when records are available; offer a dashboard drill-down asynchronously for full evidence.
- **cost:** Low, about $0.001–$0.02 per explanation; storage/indexing and occasional summarization dominate, not realtime inference.
- **security:** Evidence can contain private page text, file names, and screenshots. Keep raw artifacts local to their originating surface, redact secrets before relay transmission, enforce per-owner job/session access, and let the owner delete provenance with the underlying job.
- **missing:** A durable provenance graph linking utterance, planner decision, observation IDs, typed actions, receipts, and compensating actions; Stable evidence references and redaction at the Mac and browser boundaries rather than copying entire page contents; A relay query that resolves spoken references such as 'that email one' or 'the thing you just changed' to a provenance node; A compact pendant-safe spoken renderer plus dashboard expansion for citations and screenshots

### "Keep an eye on work I started, but do not interrupt me unless it is genuinely urgent; batch ordinary updates and tell me the important ones when I next press the pendant button."
- **useful because:** The owner should be able to delegate attention, not merely actions. Today every surface can produce events or receipts, but nothing jointly decides whether an event deserves an interruption, queues low-priority updates for the wearable, and gives the owner one concise digest on demand.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use deterministic urgency rules and event aggregation first; use a cheap background model to classify and summarize batches. Reserve realtime for a genuinely urgent alert or the owner's button-triggered digest.
- **latency:** Urgent alerts within 3 seconds of a qualifying event; non-urgent events are batched with no spoken interruption and summarized within 2 seconds of a button press.
- **cost:** About $0.001–$0.03 per batch, primarily classification/summarization; urgent deterministic routing can be nearly free.
- **security:** Do not infer sensitive personal circumstances from microphone data. Store event metadata and redacted summaries, not raw page/file contents. Make quiet mode, urgency threshold, and retention visible and controllable from the pendant/dashboard; never silently expose authenticated browser content in an alert.
- **missing:** A durable event inbox with priority, expiry, deduplication, and per-owner attention policy; A pendant uplink/downlink protocol for queued digests and urgent notifications, including reconnect delivery and button acknowledgment; A common event envelope emitted by Mac actions, browser results, and relay jobs; An explicit owner-configurable interruption policy and an audit trail showing why an event was or was not surfaced


## Changes it proposed to its own stack

### `relay` — Implement a real relay capability inventory endpoint and expose it to agents (e.g., GET /relay/capabilities) plus a job-status read endpoint (e.g., GET /relay/jobs/:jobId) backed by durable storage. Keep it read-only and cheap: list tool schemas, route visibility, and recent job receipts without requiring a Mac round trip.
- **owner gets:** The pendant can tell the owner what it can do and what happened to their requests even when the Mac is asleep. That means fewer dropped tasks, less confusion, and faster, clearer voice interactions.
- effort: Medium: add a small router module, durable storage reads, and schema serialization; coordinate with orchestrator to register the surface.  ·  risk: Low: read-only endpoints. Risk is exposing internal details; mitigate by returning only capability names, versions, and redacted parameters, and by keeping job receipts summarized.
- cost: Low API cost: a single cheap GET per session or troubleshooting moment. No heavy model calls.  ·  latency: Improves latency for status queries because the relay can answer immediately without contacting the Mac.
- security: Ensure the endpoint is bearer-protected and omits sensitive payloads. Return only metadata and user-facing status strings.
- depends on: A relay-local job receipt store (or durable object) that records plan/execute results; otherwise the endpoint has nothing authoritative to read.

### `hardware` — Add a low-power vibration motor with a simple driver and expose three firmware patterns (urgent, acknowledged, queued-digest). Keep the existing one-button/one-LED interface, and make haptic delivery local so an alert remains perceivable when LTE audio is delayed or the owner is in a noisy environment.
- **owner gets:** They can receive a discreet, reliable signal that something truly needs attention without broadcasting private speech or staring at a screen. A long press can acknowledge or request the queued spoken digest when they are ready.
- effort: Moderate hardware spin: motor, transistor/driver, mechanical mounting, firmware pattern API, enclosure and battery testing; also add relay delivery acknowledgments and event-priority mapping.  ·  risk: Added vibration and mechanical noise may annoy the owner or drain the battery; provide a hardware/firmware disable mode and rate limits, and fall back to LED/audio if the motor fails. Validate that vibration does not interfere with the button or enclosure sealing.
- cost: Approximately $1–$3 in components and assembly at prototype quantities; roughly 10–30 mW only while vibrating, with negligible average draw under rate limits.  ·  latency: Local haptic onset can be under 100 ms after a queued packet reaches the pendant; no model round trip is needed.
- security: Improves privacy by reducing reliance on audible alerts. Firmware must authenticate notification packets and avoid encoding sensitive information in distinguishable patterns.
- depends on: A durable, priority-aware relay event inbox and pendant downlink acknowledgment protocol; Owner-configurable quiet hours and interruption policy; Firmware power-budget and enclosure validation


## What it asked for

### `t17-6ymj` (tool) — relay_event_push
- why: The relay needs a way to deliver asynchronous completion updates to the pendant (or to a paired phone) after the voice session ends. Without it, users have to poll for status, which is awkward and unreliable for long-running tasks.

```json
{
  "type": "object",
  "properties": {
    "jobId": {
      "type": "string",
      "description": "The job to monitor for completion."
    },
    "event": {
      "type": "string",
      "enum": [
        "complete",
        "failed",
        "needs_attention"
      ],
      "description": "High-level outcome."
    },
    "spoken": {
      "type": "string",
      "description": "A short user-facing sentence to play on the pendant."
    },
    "ttl_seconds": {
      "type": "integer",
      "description": "How long the notification should be kept if the device is offline."
    }
  },
  "required": [
    "jobId",
    "event",
    "spoken"
  ]
}
```

## Its own summary

Recorded three distinct owner-facing gaps: cross-surface resumable transactions with recovery and exact outcomes; spoken provenance explaining observations, decisions, and changes; and an attention-aware exception channel that batches routine updates. Also recorded a hardware change adding private haptic alerts to the pendant. What remains needed is chiefly connective infrastructure: durable event/provenance records, resumable workers, authenticated pendant downlink/acknowledgment, redaction, and owner-configurable attention policy—not another standalone Mac or browser action.

**Biggest unknown:** Whether any unobserved relay firmware routes already provide durable downlink, event persistence, or notification acknowledgment; this round's instruction prohibited further discovery.

