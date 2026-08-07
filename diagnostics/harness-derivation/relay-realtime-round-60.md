# Harness derivation — relay-realtime — round 60

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What changed across my Mac and the browser since I last checked, and interrupt me only if it is urgent?” Give me a short spoken digest with sources, and let me mark items handled by voice."
- **useful because:** Today the owner must separately inspect apps and browser tabs or receive disconnected notifications. A single wearable-aware change inbox would preserve attention while they are away, deduplicate the same event seen by multiple surfaces, and support spoken acknowledgement without losing provenance.
- **path:** Mac watcher observes selected app/file/calendar/mail state and emits signed change events → browser harness watches explicitly enrolled authenticated tabs and emits page/account changes without exposing session secrets → relay stores a durable per-owner event ledger, correlates duplicates, ranks urgency, and serves a low-latency voice digest → pendant announces only policy-approved urgent changes via audio/LED and accepts button/voice acknowledgement → Mac/browser agents receive acknowledgement or follow-up commands and return receipts with cited evidence
- **model tier:** Use a cheaper background model for event normalization, deduplication, and urgency ranking; use relay-realtime only for the live spoken query and concise response. Escalation to a planner happens only when the owner asks for action.
- **latency:** Event ingestion can be eventual (seconds to a few minutes); spoken query should begin within 1 second and produce the first digest in under 3 seconds. Urgent push should reach the pendant within 10 seconds of a verified event.
- **cost:** Low ongoing cost for local event extraction and a compact relay ledger; roughly one background summarization call per event batch, with realtime tokens only when the owner speaks. Browser polling/trigger volume and digest generation dominate.
- **security:** Browser events may contain sensitive authenticated content, so enrollment must be explicit per tab/domain and payloads should be minimized, encrypted in transit, and retained briefly. Never speak secrets aloud by default; require a spoken disambiguation for sensitive fields. Every item needs source, timestamp, confidence, and an undo/ignore state.
- **missing:** A durable event-ingestion and ledger service on the relay with per-surface cursors, deduplication, retention, and acknowledgement state; Mac-side change watchers with an explicit enrollment API; Browser-side authenticated page-watch hooks that emit typed, redacted deltas rather than screenshots by default; A relay-to-pendant push channel and local notification policy (including quiet hours and urgency); Voice commands for acknowledge, snooze, mute-source, and drill-down with evidence receipts

### "“While I was away, what did the pendant, Mac, and browser do on my behalf, what evidence justified each step, and undo the last reversible step?”"
- **useful because:** Existing action receipts are machine-oriented and fragmented. The owner needs a trustworthy, spoken causal timeline spanning all substrates, especially when an unattended Mac or authenticated browser acted while the pendant was away. This makes autonomous behavior legible and recoverable without opening dashboards.
- **path:** pendant provides the natural-language query and optional button-held confirmation for a selected undo → relay maintains a tamper-evident cross-surface causal graph linking utterance, intent, plan, actions, evidence, and receipts → Mac planner/terminal and browser extension attach structured before/after snapshots and reversibility metadata to every operation → relay-realtime narrates a concise timeline with uncertainty and source citations, then routes an explicit undo request to the owning surface → Mac/browser return idempotent undo receipts; relay updates the spoken timeline and durable state
- **model tier:** Use a small background model to index and summarize the causal graph; use relay-realtime only for interactive explanation, disambiguation, and the final undo routing. No expensive reasoning is needed to list known receipts.
- **latency:** Timeline overview in under 2 seconds from a cached index; evidence drill-down in under 5 seconds. Undo should return a receipt within 10 seconds when the relevant surface is online, otherwise remain queued with a clear blocker.
- **cost:** Mostly local structured logging and indexed storage; background summarization is the dominant API cost, with low realtime usage because the response is grounded in existing records.
- **security:** The graph can contain email, page text, file names, and commands. Encrypt it, redact secret values, enforce per-owner access, and expose provenance without reading sensitive payloads aloud by default. Undo must be constrained to operations explicitly marked reversible and must never pretend success when a surface is offline.
- **missing:** A shared causal-event schema and append-only ledger across relay, Mac, and browser; Standard before/after evidence and reversibility fields in Mac and browser receipts; Relay query APIs for time range, causal links, and evidence redaction; Idempotent undo endpoints and explicit offline/expired-session failure states on each acting surface; A spoken timeline/undo interaction and compact pendant UX for selecting an event


## Changes it proposed to its own stack

### `relay` — Wire a real routing shim for relay intents instead of relying on tool-name inference. Implement a relay-facing intent tool (the granted relay_route_intent) with validation, logging, and mapping to downstream calls (mac_delegate, mac_run_actions, browser_run_actions, web_search) so the realtime model can explicitly declare intent and target and receive a consistent job reference.
- **owner gets:** Fewer misroutes and less conversational friction. The owner can say what they want and the system routes it reliably, even as new surfaces (server-side browser, future devices) appear.
- effort: Medium: define schema, add adapter layer, tests for mapping and fallbacks, update orchestrator/tool registry so describe(name) resolves.  ·  risk: If the mapping is wrong, tasks could be sent to the wrong surface. Mitigate with explicit target selection, idempotency keys, and receipts; keep a safe fallback to mac_delegate for ambiguous intents.
- cost: Low per call; adds a small logging and validation overhead. Main cost is engineering time.  ·  latency: Minimal; intent parsing is cheap and avoids extra round trips caused by misrouting.
- security: Moderate: logging must avoid storing sensitive utterance content unnecessarily; redact or hash where possible and enforce least retention.
- depends on: Tool registration/implementation so relay_route_intent is describable and callable in the live tool registry.


## What it asked for

_Nothing._
## Its own summary

Recorded two new capabilities: (1) a cross-device change inbox that merges Mac and authenticated-browser deltas, ranks urgency, pushes only policy-approved alerts to the worn pendant, and supports voice acknowledgement; (2) a spoken, evidence-backed causal timeline of everything pendant/Mac/browser did while the owner was away, including safe reversible undo. Both require new durable relay infrastructure and cross-surface schemas rather than assuming today’s wiring exists.

**Biggest unknown:** Whether the backlog already contains an event-ingestion/attention-inbox proposal under a name not visible in the truncated index; I deliberately made the first proposal specifically about cross-surface deduplication, wearable push, and acknowledgement, and the second specifically about owner-facing causal replay rather than generic receipts.

