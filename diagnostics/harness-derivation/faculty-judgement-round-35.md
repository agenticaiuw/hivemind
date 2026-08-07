# Harness derivation — faculty-judgement — round 35

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **cross-surface readiness** — As of the live /ops/status and /browser/status probes, relay is reachable and mac bridge heartbeat is recent, but Mac Accessibility is not trusted, Screen Recording is not granted, computer-use loop is disabled, and the browser extension is offline with 3 pending commands. The agent reports ready:false despite automation grant cache.
  - evidence: GET /ops/status HTTP 200; GET /browser/status HTTP 200 at 2026-08-07T10:41Z

## Capabilities it proposed

### "“Tell me what actually matters today, and only interrupt me when the evidence changes or two of my sources disagree.”"
- **useful because:** The owner currently gets either failed account reads or noisy scheduled briefs. This would reconcile calendar, mail, tasks, travel, and authenticated pages into one time-bounded decision view, distinguish a real obligation from stale/duplicate signals, and escalate only material changes. The pendant supplies immediate interruption and spoken acknowledgement; the relay keeps watching; the Mac and browser gather private evidence they alone can reach; the owner never has to remember which surface held the truth.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** A cheap background model extracts normalized facts and deduplicates changes; faculty-judgement is invoked only for conflicts, deadline/impact scoring, or an interruption decision; realtime is used only to speak a short alert and accept a response.
- **latency:** Background reconciliation can take 1–5 minutes after a scheduled run or source change. A material alert should reach the pendant within 10 seconds; acknowledgement should be one spoken turn. No source access or action is attempted while its surface is offline.
- **cost:** Roughly $0.01–$0.08 per daily reconciliation depending on page volume; conflict adjudication dominates. Realtime cost is limited to rare alerts. Storage is small normalized facts plus evidence hashes, not page copies by default.
- **security:** Private mail, calendar, and logged-in page snippets stay on the Mac/browser boundary; relay receives only normalized facts and minimal evidence needed for adjudication. Never send, delete, purchase, or change an appointment automatically. Each alert needs source citations, freshness, confidence, and an expiry; conflicting low-confidence facts should be shown as uncertain rather than guessed.
- **missing:** A durable source connector contract for Mac and authenticated browser reads with typed freshness/confidence and evidence hashes; A shared change/conflict event schema and deduplication store across scheduled jobs and live browser observations; A policy engine mapping impact, urgency, quiet hours, and owner acknowledgement state to pendant interruption vs queued brief; The already-requested cross-surface recovery/preflight and intent-continuity primitives, wired into this watcher; A verified end-to-end 24 kHz audio path so the resulting brief and alerts are intelligible on the pendant

### "“Before I commit to this, show me what each option would do to my actual schedule, messages, files, and accounts—and let me choose without changing anything yet.”"
- **useful because:** Today the owner can ask for a draft or an action, but cannot safely compare realistic consequences across private surfaces before deciding. This would turn the pendant into a decision instrument: the owner speaks a goal, the relay coordinates parallel read-only inspections, the Mac and authenticated browser build isolated counterfactuals, and judgement explains the smallest meaningful differences. The owner gets agency without needing to understand which system contains each consequence.
- **path:** relay-realtime → pendant → mac-planner → mac-vision → browser-extension → mac-terminal → faculty-perception → faculty-judgement → faculty-action → unified
- **model tier:** Use deterministic planners and read-only adapters to enumerate affected entities; use a cheap background model to summarize each scenario; invoke faculty-judgement only to resolve tradeoffs, uncertainty, or hidden dependencies. Realtime is only for the spoken choice and clarification.
- **latency:** Initial impact scan in 5–20 seconds for common cases; deeper account or file simulations may run asynchronously for several minutes. The pendant should speak a two-sentence headline immediately and offer a queued detailed comparison.
- **cost:** Approximately $0.03–$0.20 per comparison, dominated by private-page extraction and scenario summarization; deterministic reads and cached entity graphs keep repeated options inexpensive.
- **security:** All simulations must be read-only and sandboxed: no form submission, email send, purchase, deletion, or calendar mutation. Private page contents remain on the Mac/browser boundary; relay receives normalized impacts and evidence hashes. Every result needs source, freshness, confidence, assumptions, and an explicit statement of what was not simulated. Approval must be tied to the exact selected scenario and expire if source state changes.
- **missing:** A cross-surface counterfactual/impact graph that can represent calendar conflicts, message recipients, file mutations, account state, and dependencies in one typed schema; Read-only browser and Mac adapters that can clone form state or calculate diffs without touching live state; Scenario IDs with immutable assumptions, evidence snapshots, expiry, and invalidation when a source changes; A faculty-judgement comparison format that presents tradeoffs rather than silently choosing for the owner; A final action handoff that can execute only the selected, still-valid scenario through the existing admission and evidence gates


## Changes it proposed to its own stack

### `integration` — Make scheduled and ad-hoc briefs readiness-aware: before collecting anything, snapshot Mac Accessibility/Screen Recording, browser bridge heartbeat, relay reachability, and source-level authorization. Partition the brief into verified, stale, and unavailable sections; never imply that a failed read was empty. Queue a retry with exponential backoff, emit one concise pendant notice when a source becomes available, and attach a machine-readable failure receipt to the dashboard. Treat pending browser commands as recoverable only when their session/tab affinity is still valid.
- **owner gets:** The owner asked repeatedly for Gmail/GitHub/calendar and received failures, while scheduled briefs can still report completion. They should know whether there is nothing to say or whether the system could not look, without manually debugging permissions or reconnecting a browser.
- effort: Medium: readiness adapter, source result types, scheduler retry state, and spoken/dashboard rendering; test offline, stale, reconnect, and partial-success cases.  ·  risk: A transient outage could create duplicate alerts or repeated retries. Bound retries, use idempotency keys, and let the owner mute a source. Recovery is automatic on heartbeat and every receipt preserves the last verified timestamp.
- cost: Negligible storage and background compute; one extra readiness request per run. No realtime model call unless an owner-facing alert is needed.  ·  latency: Adds under 1 second to a run when healthy; retries are asynchronous and do not block a concise partial brief.
- security: Improves security by preventing stale/private data from being presented as current and by exposing only source status, not credentials. Do not log page contents in failure receipts.
- depends on: Browser bridge reconnect/heartbeat and typed pending-command ownership; Mac readiness endpoint with authoritative permission state; Durable job/event persistence and the cross-surface recovery/preflight primitives already requested

### `model-routing` — Add a deterministic receipt path for status, time, battery, connectivity, permission, and completed-job queries. Parse the intent, read typed state, and render the owner's one-sentence format without sending the full fleet context to an LLM; escalate only when the receipt requires interpretation or conflict resolution. Record token savings and preserve a cited machine-readable payload behind the sentence.
- **owner gets:** Simple questions such as “what time is it?”, “what is my battery?”, or “what happened with the last job?” should be immediate and dependable, not fail or spend a large context window. The owner gets the short spoken answer they prefer while detailed evidence remains available on request.
- effort: Small-to-medium: intent classifier/rules, typed receipt templates, and regression tests for timezone, stale state, partial failures, and destructive-action wording.  ·  risk: A too-broad parser could misclassify an action request as a harmless status query. Use an allowlist of read-only intents and escalate any ambiguity; never mutate state on this path.
- cost: Near-zero model cost for deterministic receipts and materially lower repeated context transfer; occasional planner escalation remains unchanged.  ·  latency: Typically tens of milliseconds locally instead of ~1 second+ background inference.
- security: Less private context leaves the device. Receipts must redact secrets and preserve sensitivity labels in the typed payload.
- depends on: Typed source/readiness results from the readiness-aware brief change; A stable timezone and owner preference projection; Receipt schema shared by relay, Mac agent, dashboard, and pendant


## What it asked for

_Nothing._
