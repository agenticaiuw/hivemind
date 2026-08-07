# Harness derivation — relay-realtime — round 118

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Pick up the task I started on my pendant yesterday, show me what is still unresolved, and let me finish it from whichever device I’m using.” The system should preserve a task as a resumable thread across the pendant, Mac, and authenticated browser rather than treating each voice turn as a new job."
- **useful because:** Today a spoken handoff loses the working set, evidence, and pending choices when the owner walks away or changes surfaces. This would let the owner start hands-free, continue at a Mac or browser, and return to the pendant with a concise list of unresolved decisions—useful precisely because no one node has all of the conversation, local files, and browser sessions.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use the realtime relay only to identify the task and answer a short status question. A cheaper background model should periodically normalize task state and evidence; mac-planner and browser harness remain the executors, not the realtime model.
- **latency:** Initial acknowledgment under 500 ms; task-state retrieval under 2 s from the relay. Cross-surface reconciliation may take several seconds and must return a partial state rather than blocking the owner.
- **cost:** Roughly one short realtime turn plus a small background summarization call per state change; dominant cost is re-sending accumulated task context, so store a compact state delta and evidence references rather than replaying transcripts.
- **security:** Authenticated browser content and local Mac data must remain scoped to the task and be encrypted at rest. The owner needs a visible list of linked sources and a one-tap/one-button way to unlink or delete a task. Never expose browser cookies or raw private pages in a pendant response; destructive or externally visible actions still need an explicit task-level confirmation even though ordinary reversible work does not.
- **missing:** A durable cross-surface task object with versioned state, unresolved-choice records, source/evidence references, and owner-controlled retention/redaction; A handoff protocol that lets Mac and browser agents append typed progress and citations while preserving causality and detecting conflicting updates; A relay endpoint and pendant UX for listing/resuming/forgetting tasks, plus a browser/Mac picker to attach the current tab or workspace; A reconciliation worker to compact transcript and receipts into state deltas without repeatedly paying for full context

### "“Is that actually done everywhere, or did one surface fail?” The pendant should be able to reconcile a task’s claims against the Mac’s receipts/state and the authenticated browser’s current inspection, explain any disagreement, and offer the smallest repair."
- **useful because:** A job receipt only says what an agent reported; it does not establish that a browser tab, local file, or external service ended in the intended state. The owner is often away from the Mac and cannot manually compare surfaces. A spoken, evidence-backed discrepancy answer prevents silent partial completion and avoids repeating an already-successful action.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use the realtime model only for the owner-facing question and concise explanation. Run evidence collection and comparison with deterministic checks first, then a cheaper background model only for conflicting or unstructured evidence; escalate to the Mac planner for repair.
- **latency:** Return an initial “checking Mac/browser” acknowledgment immediately and a result within 3 seconds when both surfaces are online. If either is offline, say exactly which evidence is stale and preserve the check for the next connection.
- **cost:** Usually no model call beyond the short realtime response; deterministic receipt/state comparison dominates. A small fallback summarization call is needed only when evidence is textual. This is cheaper than replaying the original task context.
- **security:** Evidence must be source-scoped and time-stamped; authenticated page contents should be reduced to claims, not copied into logs or spoken aloud. Never infer success from a missing receipt. Repairs must be separately represented from verification, and externally visible changes should be announced before execution.
- **missing:** A typed verification record linking intended outcome, action receipts, Mac observations, browser inspection snapshots, timestamps, and freshness; A cross-surface comparator that detects stale, contradictory, or insufficient evidence and returns confidence plus the missing observation; A relay query route and pendant response format for verification status, with an optional repair handoff to the appropriate executor; Automatic post-action observation hooks from Mac and browser so verification is not dependent on a later manual query


## Changes it proposed to its own stack

### `relay` — Publish a relay /capabilities endpoint (and wire it into list_capabilities for this surface) that enumerates relay routes, granted tools, and feature flags, including whether schemas like relay_route_intent/server_browser_actions are implemented. Include version and compatibility info.
- **owner gets:** When something doesn’t work, I can tell the owner immediately what exists and what’s missing, instead of guessing or re-probing random paths. That reduces confusion in voice interactions and speeds up recovery when the Mac is away.
- effort: Medium: expose an internal inventory similar to the Mac agent’s /capabilities and keep it in sync with routing/tool registration.  ·  risk: Low: the endpoint could leak internal details if exposed broadly. Mitigate by requiring auth and returning only what’s safe for the owner’s agent to see.
- cost: Low API cost per call; small response payload. Biggest cost is maintenance to keep the inventory accurate.  ·  latency: Positive: fewer exploratory probes and fewer failed attempts.
- security: Requires access control; avoid returning secrets or tokens.
- depends on: routing/tool registration metadata available at runtime

### `relay` — Add a durable, append-only outcome ledger between job execution and owner-facing voice. Every planned action gets an intent hash and expected outcome; Mac and browser surfaces append typed observations (success, failure, stale, or unknown) with timestamps, source identity, and evidence references. A relay reconciler emits a compact discrepancy record and invalidates stale “complete” claims when a later observation contradicts them. Expose one owner-facing query that returns status, confidence, unresolved discrepancy, and the next safe observation—not raw logs.
- **owner gets:** The owner can ask the pendant whether a remote task truly finished and receive an honest answer grounded in current evidence, instead of trusting an agent’s completion sentence or repeating actions that may already have happened.
- effort: Medium-high: ledger schema and migrations, observation adapters in Mac/browser executors, reconciliation rules, retention/redaction, and a small voice response contract; add fault-injection tests for offline and contradictory surfaces.  ·  risk: A late or incorrectly scoped observation could mark a valid task stale or associate evidence with the wrong task. Recover with immutable source/version IDs, monotonic timestamps, explicit unknown status, and never auto-repair from a discrepancy. Existing receipts remain available as audit history.
- cost: Low storage and negligible API cost for structured observations; occasional cheap summarization only for unstructured evidence. No additional hardware cost.  ·  latency: Action completion need not wait for reconciliation. The owner gets an immediate checking response, then a result after parallel observations; offline surfaces produce a stale/unknown result rather than blocking.
- security: Do not persist page bodies, cookies, or arbitrary command output by default—store hashes, field-level claims, and redacted evidence pointers. Enforce per-task source scope and owner deletion/retention controls.
- depends on: A durable cross-surface task identity and versioned state object; Mac and browser post-action observation hooks; A relay route for querying reconciled outcome state; A compact pendant response format for confidence and discrepancy


## What it asked for

_Nothing._
## Its own summary

Inventory shows the production tools list is unchanged (get_mac_status, mac_run_actions, browser_run_actions, web_search, mac_delegate, read_web_page, relay_job_status). New items in this run are a few granted schemas (relay_route_intent, server_browser_actions) and permissions, but the key schemas are still not implemented. Devices indicate the Mac bridge is online while the browser surface is offline. I also probed relay health and confirmed the relay itself is up, with pairing required and macBridgeOnline true. Proposed a relay change: publish its own capabilities/status endpoint so discovery doesn’t depend on guesswork.

**Biggest unknown:** Which of the granted schemas and proposed tools (relay_route_intent, server_browser_actions, relay_job_status implementation) will be implemented next, and whether a scheduler/cron-like capability will be added; without those, I still need to route via mac_* tools and cannot run server-side browser workflows or scheduled work.

