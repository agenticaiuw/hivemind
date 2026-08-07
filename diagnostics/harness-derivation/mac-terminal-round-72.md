# Harness derivation — mac-terminal — round 72

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac execution observability and cross-surface state** — The live Mac agent is v0.5.0 with FULL_CONTROL_MODE and planner enabled. Its read-only journal covers 120 retained jobs, 147 actions, 14 failures, 76 writes, but reports 0 undoable and 112 routing requests unattributed to a tier. Browser extension home-chrome is offline with 5 pending commands; mac-vision loop is disabled and vision upload consent is false; Accessibility is not trusted.
  - evidence: GET /ops/status, GET /journal, GET /routing, GET /browser/status

## Capabilities it proposed

### "“For that request I made earlier, show me the complete chain of what happened, what is still queued, what failed, which device did each step, and roughly how much model time it cost.”"
- **useful because:** Today the owner gets separate Mac jobs, routing receipts, and browser queue state, but no single trustworthy, human-readable explanation joining them. This would make cross-device behavior understandable after delays, dropped connections, partial completion, or duplicate attempts—without requiring the owner to inspect technical logs.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background for assembling and summarizing existing structured records; deterministic joins and totals first, with a small model only for concise spoken wording. Realtime is unnecessary unless the owner asks during a live conversation.
- **latency:** Under 2 seconds for a recent request from retained records; under 5 seconds if browser reconnect reconciliation is needed. The pendant can say 'I am checking the Mac and browser trace' while the background job assembles it.
- **cost:** Usually near-zero model cost when records are structured; roughly 1–3k input tokens and a short completion only when summarization is needed. Dominant cost is not inference but retaining and joining bounded trace metadata.
- **security:** The report may reveal private URLs, shell commands, file paths, account names, and model prompts. Store raw spans locally with short retention, redact secrets and sensitive arguments, expose opaque IDs and summaries by default, and require owner-authenticated access for detailed views. Never include bearer tokens or full private page contents in relay speech.
- **missing:** A shared request-lineage ID propagated from relay routing into Mac jobs, shell actions, and browser commands; A bounded redacted trace store that survives the current 120-job eviction window through aggregate summaries; Browser reconnect reconciliation that records whether pending commands eventually completed, failed, or remain indeterminate; A join endpoint or dashboard view combining routing, journal, job receipts, and browser queue state

### "“After anything gets interrupted, tell me what is definitely complete, what is only partly done, and what cannot be verified—and offer the next safest way to reconcile it without blindly repeating the action.”"
- **useful because:** A dropped Mac connection, browser disconnect, timeout, or process crash currently leaves the owner to guess whether a command ran before the failure. This capability distinguishes completed, failed, and indeterminate effects, then proposes inspection or continuation rather than silently replaying potentially permanent work.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Background/deterministic for effect-state calculation from receipts, exit codes, checkpoints, browser acknowledgements, and reconnect state; use the planner tier only to explain ambiguous cases or formulate a recovery plan. Realtime is only needed to read the short result aloud.
- **latency:** Initial interruption classification under 2 seconds from local records; reconciliation under 10 seconds when it needs a live Mac or browser check. The owner should get an immediate compact uncertainty report, followed by an update if a device reconnects.
- **cost:** Near-zero for deterministic classification; roughly 1–3k model input tokens only for an ambiguous multi-step recovery explanation. Most cost is local state tracking, not inference.
- **security:** Recovery inspection can expose private files, authenticated pages, and command arguments. Keep evidence local by default, redact secrets, require explicit owner choice before any compensating mutation, and make the spoken summary disclose uncertainty rather than claiming success.
- **missing:** Per-step effect checkpoints with an explicit unknown/indeterminate state rather than only job success or failure; Command- and browser-operation effect probes that can verify postconditions without replaying the original action; A recovery-plan record that separates read-only reconciliation from compensating mutations and records the chosen outcome; Cross-device acknowledgement and reconnect handling so a late browser result or Mac receipt can close an uncertain step


## Changes it proposed to its own stack

### `integration` — Add a cross-surface causality and cost trace, not another shell runner: mint one lineage ID at the pendant/relay utterance, propagate it through routing decisions, planner calls, Mac jobs, each run_shell subprocess, browser-extension commands, receipts, and spoken completion. Make /journal and /routing joinable by lineage, with parent/child spans, model tier/token estimates, queue and execution latency, browser-online state, and terminal outcome. Backfill attribution for new jobs and show a compact 'because you asked X → planner chose Y → Mac/browser did Z' receipt; keep the existing 120-job retention but export aggregate lineage summaries before eviction.
- **owner gets:** When a request crosses the pendant, server, Mac, and browser, the owner gets one trustworthy explanation instead of disconnected job IDs—and can tell whether a delay was model time, Mac execution, or the browser being offline. It also prevents expensive duplicate work when a queued browser action is mistaken for a failed Mac action.
- effort: Medium: define a shared trace envelope, propagate it through relay routing and local-agent job creation/browser bridge, add join/aggregation in journal and routingStats, and add reconnect reconciliation tests.  ·  risk: Trace metadata could leak command text, URLs, or account context; store opaque IDs and redacted summaries by default, with sensitive fields local-only. Clock skew and retries can produce confusing spans; use monotonic durations and explicit attempt numbers. Export must be bounded and non-blocking so telemetry cannot delay actions.
- cost: Negligible local storage and network overhead (small metadata per action); saves planner/API cost by making duplicate/retry causes visible. No new model call needed for receipts.  ·  latency: Sub-millisecond to a few milliseconds for ID propagation and local aggregation; no user-visible model latency.
- security: Creates a sensitive map of activity across devices. Encrypt local trace storage, apply short retention to raw spans, redact shell args/URLs and tokens, and expose only owner-authenticated summaries.
- depends on: A shared lineage envelope in relay and local-agent request schemas; A non-blocking local trace sink with bounded retention


## What it asked for

_Nothing._
