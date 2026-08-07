# Harness derivation — relay-realtime — round 90

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “I’m leaving,” save the current state of my work; when I later say “I’m back,” tell me only what changed in my Mac and authenticated browser tabs, and what deserves my attention."
- **useful because:** The owner is usually away from the Mac. Today the pendant cannot create a trustworthy before/after handoff across the unattended Mac and session-bearing browser. This would let them leave without losing context and return to a concise, evidence-backed delta instead of reopening every app and tab.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → browser → dashboard
- **model tier:** Use relay-realtime only for the two short voice intents and final spoken summary; use mac-planner/mac-terminal for cheap state capture and diffing, and browser-extension/server browser reads for authenticated tab snapshots. No model should continuously watch or summarize unchanged state.
- **latency:** A leave acknowledgement should be under 1 second. A return acknowledgement can say “I’m comparing your snapshot now” within 1 second; the cited delta should arrive within 10–20 seconds, with partial results if one surface is offline.
- **cost:** Roughly one low-cost planner/background invocation per leave and return plus a short realtime response; dominant costs are authenticated page extraction and the final synthesis, not the pendant transport. Retain compact hashes/excerpts rather than full pages to control storage and tokens.
- **security:** Browser data and Mac window/document metadata leave their devices only to the relay for the owner’s request. Snapshots must be encrypted, scoped to the owner and a pairing epoch, and expire automatically; exclude passwords, page forms, clipboard contents, and audio unless explicitly requested. The spoken report should cite which surface produced each change and say when a surface was unavailable. Reading is default; any proposed follow-up action must be separately requested.
- **missing:** A cross-surface snapshot schema with stable item identifiers and redacted summaries; A leave/return state machine persisted by the relay, including pairing epoch and expiry; Mac read-only snapshot and diff routes for open apps, reminders, files, and recent task receipts; Browser authenticated-tab snapshot/diff support in the extension/browser harness; A cheap background diff/summarizer and a compact cited spoken-report format; An explicit return trigger (voice or button) and offline-safe pending state on the pendant

### "Why didn’t that work? Reconstruct the last failed request across my pendant, Mac, and browser, explain the first failure in plain English, and tell me whether anything actually changed."
- **useful because:** Today a failure can be split across voice-run history, relay jobs, Mac receipts, and browser command results; the owner has no single forensic answer and may retry a mutation that already partially succeeded. A cross-surface replay would make the wearable a reliable incident console while they are away from the Mac.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → browser → dashboard
- **model tier:** Use deterministic correlation and typed receipt parsing first. Invoke a cheaper background model to summarize the causal chain; reserve relay-realtime for the short spoken explanation and one follow-up question. Do not use the realtime model to inspect raw logs wholesale.
- **latency:** Speak an immediate acknowledgement in under 1 second; return a first diagnosis in 5–10 seconds and progressively attach deeper evidence in the dashboard. If a surface is offline, explicitly mark that portion unknown rather than guessing.
- **cost:** Low per invocation: log retrieval and correlation dominate latency, with one small summarization call. Store normalized event references and hashes instead of duplicating full transcripts or page content.
- **security:** The report may contain private URLs, filenames, browser titles, or command arguments, so enforce owner pairing and redact secrets, cookies, tokens, clipboard data, and form values before model input. It must be read-only and clearly distinguish confirmed receipts from inferred causes. Never retry or undo automatically; an undo can be offered only as a separate spoken request.
- **missing:** A shared event envelope carrying correlation ID, surface, timestamp, action type, result, and receipt reference; A relay endpoint that gathers one bounded time window across voice runs, jobs, Mac receipts, and browser command results; Deterministic partial-success detection and redaction before model summarization; A causal-chain renderer with cited evidence and an explicit unknown state; A pendant phrase/button shortcut for “last failure” and a dashboard drill-down


## Changes it proposed to its own stack

### `relay` — Publish a relay capability and route inventory endpoint (e.g., GET /relay/capabilities) and a typed intent envelope for routing. The envelope should include intent label, utterance, confidence, required surface, and privacy level, and it should be logged with a jobId for later status queries.
- **owner gets:** The pendant can reliably hand tasks to the right place and later explain what happened, with fewer misroutes and less re-asking. It also reduces hidden failures when a route is missing or changed.
- effort: Medium: define schema, implement route, add logging, and wire to existing planner/execute flow.  ·  risk: Misrouting could cause unintended actions. Mitigate with typed intent labels, strict validation, and receipts. If routing fails, fall back to asking a clarifying question.
- cost: Small per request; mostly schema validation and logging.  ·  latency: Tiny overhead at handoff time; negligible compared to planning/execution.
- security: Intent logs contain sensitive utterances; encrypt at rest, minimize retention, and redact where possible.
- depends on: Implement relay_route_intent tool/route rather than schema-only grant


## What it asked for

_Nothing._
## Its own summary

Recorded two capabilities: a leave/return cross-surface delta briefing, and a read-only cross-surface incident replay that explains partial failures. Both require new relay correlation/state machinery plus Mac and authenticated-browser snapshot/receipt adapters; neither assumes the currently wired tools are sufficient.

**Biggest unknown:** Whether the backlog already contains a materially identical leave/return handoff or incident-replay proposal; the recorder flagged both as adjacent, but I was instructed not to discover further this round.

