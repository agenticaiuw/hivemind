# Harness derivation — mac-terminal — round 113

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac execution readiness and observability** — The live Mac agent is operational and FULL_CONTROL_MODE is enabled, but computer-use vision is disabled because Accessibility and Screen Recording are both ungranted; browser extension is offline with 10 pending commands. The read-only journal currently reports 120 retained jobs, 146 actions, 19 failures, 80 writes, and 0 undoable actions; routing reports 57% of requests avoid planner while planner baseline is 8,837 estimated tokens/request.
  - evidence: GET /ops/status, GET /journal, GET /routing returned HTTP 200 on Round 113.

## Capabilities it proposed

### "If my Mac or browser is unavailable, still answer what you can: use public web sources as a fallback, clearly say when a private logged-in source could not be reached, and resume the private task automatically when the connection returns."
- **useful because:** Today the relay and Mac bridge are online but the browser extension is offline with 10 pending commands; without an explicit fallback the owner gets silent failure or a misleading completion. This makes the hive degrade gracefully while preserving the boundary between public facts and private account data.
- **path:** pendant → relay → mac-planner → browser-harness → browser-extension → dashboard
- **model tier:** Deterministic routing and health checks first; background gpt-4.1-mini for public-source synthesis; planner only when the fallback requires ambiguous task decomposition. No realtime model call unless the owner is actively speaking.
- **latency:** Health decision under 200 ms; public fallback 2–8 seconds; private retry runs in background on bridge heartbeat and posts a receipt rather than holding the conversation.
- **cost:** Near-zero for health/status and retry scheduling; one small background synthesis call only when public pages must be summarized (typically 1–3k input tokens).
- **security:** Never send authenticated URLs, cookies, page text, or account identifiers to public fallback. Mark every result as public-fallback or private-source with timestamp and URL; require explicit owner confirmation before any resumed private mutation.
- **missing:** A source-aware task state that distinguishes public fallback from private-unavailable and survives reconnect; A reconnect trigger that drains pending browser work only after the extension heartbeat confirms the same session/tab; A deterministic response contract that refuses to imply private access when only public fallback ran

### "When my Mac, logged-in browser, and relay have conflicting facts about the same task, tell me exactly what disagrees and ask one small clarifying question before acting. Keep both pieces of evidence attached so I can say which one is right and continue without starting over."
- **useful because:** Today the hive can collect receipts and page evidence, but it cannot recognize that two surfaces disagree—for example, Safari showing an appointment as cancelled while Calendar still shows it active. Silent selection of one source can cause a real-world mistake. The owner gets a compact conflict explanation and a resumable decision instead of a confident guess or a dead end.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** Deterministic entity/time/value comparison first; background model to normalize labels and extract candidate conflicts; realtime only to phrase the one clarification question during an active conversation. Planner is reserved for genuinely ambiguous reconciliation after the owner answers.
- **latency:** Detect conflicts while assembling a result in under 300 ms; speak the clarification within 2 seconds. Preserve the pending action indefinitely in the relay and resume within one heartbeat after the owner answers.
- **cost:** Usually no model call for exact field conflicts; roughly 1–3k background input tokens only for semantic normalization across unlike page labels. Reconciliation after an answer uses one planner call when needed.
- **security:** Keep private page evidence and account identifiers local to the Mac/browser bridge; relay stores opaque conflict IDs, redacted summaries, and hashes unless the owner explicitly asks for details. Never perform a mutation while an unresolved conflict affects its target.
- **missing:** A shared typed identity resolver linking Calendar events, browser records, Mac files, and relay jobs to one entity; A conflict record with source snapshots, freshness, confidence, and the exact field/value disagreement; A resumable clarification protocol from pendant speech to the same pending faculty-action plan; Dashboard and spoken output that distinguish stale data from a genuine contradiction


## What it asked for

_Nothing._
## Its own summary

Round 113 established live evidence: Mac FULL_CONTROL_MODE and relay bridge are healthy, but computer-use is unusable (Accessibility and Screen Recording ungranted) and the browser extension is offline with 10 queued commands. The journal shows 19 failures among 146 actions, zero undoable actions, and routing still leaves planner requests at an 8,837-token baseline. I recorded this and proposed a genuinely cross-surface degraded-mode capability: distinguish private-source failure from public fallback, answer from public sources when safe, and resume private work only after the same browser session reconnects.

**Biggest unknown:** The newly granted Mac diagnostic interfaces still have no implementation, so I cannot independently verify host state through those tools; and I still cannot test reconnect/drain behavior because the browser extension is offline. The already-requested Accessibility/Screen Recording grants and diagnostic implementation remain the concrete prerequisites.

