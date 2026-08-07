# Harness derivation — relay-realtime — round 36

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Keep working on that after I walk away, and tell me what happened when it finishes."
- **useful because:** The owner can start a multi-step task, leave, and still get a reliable outcome summary later without babysitting the Mac.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** Realtime for the initial conversation; mac-planner for execution; relay for status reads and delivery.
- **latency:** Fast confirmation (<1s) that work was queued; completion can arrive later as a spoken update when the relay sees it finished.
- **cost:** Low per invocation on the relay; the expensive part is mac-planner time for multi-step work and any browser automation.
- **security:** The system must avoid claiming completion it cannot verify. Status messages must be sourced from durable job records. Sensitive data from private accounts should be summarized minimally and never echoed beyond what’s needed.
- **missing:** Durable job lifecycle with completion callbacks or polling from relay; Delivery channel to pendant for asynchronous completion updates; Shared status vocabulary across relay and mac-planner

### "Keep watching this authenticated webpage and tell me on the pendant only when something materially changes—summarize the difference and include the exact link."
- **useful because:** The owner can delegate ongoing attention to a browser session while away from the Mac, without repeatedly opening the site or receiving noisy polling alerts. This combines the pendant's conversational setup and notification channel, the browser's authenticated session, and an always-awake relay; no single current node can provide that continuity.
- **path:** pendant → relay → browser → dashboard
- **model tier:** Use relay-realtime only to capture the initial instruction and deliver the alert; use a cheaper background model for page-diff extraction and materiality ranking. The browser harness performs authenticated reads, while the relay owns the durable watch state.
- **latency:** Acknowledge setup in under 2 seconds. Poll or receive page-change events on a configurable cadence; deliver a notification within roughly 30 seconds of a detected material change. Initial and subsequent summaries can take 2–10 seconds on the background tier.
- **cost:** Roughly $0.001–$0.02 per check depending on page size and model use, plus browser execution overhead; the dominant costs are authenticated browser runs and repeated page extraction, so unchanged-page checks should use hashes/DOM fingerprints before invoking a model.
- **security:** The browser must retain and use authenticated cookies, and page contents leave the device/session boundary to the relay or extraction worker. Encrypt watch definitions and results, minimize stored page snapshots, redact secrets before model calls, and provide an explicit stop/list-watches voice command. This is read-only by default and should not submit forms or follow mutation links.
- **missing:** A durable watch registry and scheduler using Durable Object alarms or Cron Triggers, with per-watch cadence and backoff; Browser-session/page-watch support that can reopen the owner's authenticated session, extract stable content, and emit DOM or semantic diffs; A low-cost diff/materiality worker with deduplication, retries, expiration, and alert suppression; Relay-to-pendant asynchronous notification delivery and a spoken setup/status/stop protocol; Dashboard controls for listing, pausing, changing cadence, viewing last change, and deleting watches

### "Start that task now, let me keep walking, and tell me when it is finished—even if it takes several minutes—then let me ask a follow-up about the result by voice."
- **useful because:** Today the pendant conversation ends when work is handed to the Mac or browser, so the owner must remember to ask again or inspect another surface. This gives a genuinely wearable workflow: the pendant starts a cross-device job, the relay stays responsible while the Mac/browser works, and the completion plus follow-up context comes back to the owner's voice wherever they are.
- **path:** pendant → relay → mac-planner → mac-vision → browser → dashboard
- **model tier:** Realtime handles only intent capture, concise acknowledgement, interruption handling, and final spoken delivery. mac-planner/browser workers perform the task; a cheaper background model compresses logs and creates the completion summary. Realtime is reinvoked only for the owner's next utterance or an alert.
- **latency:** Acknowledge within 2 seconds and return a job reference in speech. Completion notification should arrive as soon as the downstream job finishes, with exponential retry if a surface is offline. Follow-up questions should answer in under 3 seconds when the saved result is sufficient.
- **cost:** About $0.001–$0.01 per handoff plus downstream Mac/browser execution; the major model cost is only incurred for final summarization or a follow-up that needs fresh context. Durable job metadata and event delivery are negligible compared with browser or planner calls.
- **security:** Job results can contain private Mac files, browser content, or action receipts and must be scoped to the owner's paired pendant. Encrypt retained context, expire completed-job payloads, avoid speaking sensitive content in a notification preview, and never replay a result to an unpaired device. The downstream action policy remains the owner's existing maximum-access policy; this feature adds delivery, not a new approval gate.
- **missing:** A durable cross-surface job/event record with owner, session, status, result, expiry, and continuation token; Worker-to-relay completion callbacks for Mac planner, Mac vision, and browser jobs, including failure and cancellation events; Pendant push notification support with vibration/audio or an LED pattern, plus a one-button dismiss/replay interaction; A relay conversation store that binds a short-lived spoken follow-up to the completed job without resending the entire transcript; Dashboard job timeline and controls for cancel, mute, retry, and retention

### "Undo the last thing you did for me, or show me exactly what can be undone if it is not reversible."
- **useful because:** A wearable owner can issue a recovery command without returning to the Mac, even when the original work crossed a local app, terminal, and authenticated browser. It turns the hive from a one-way command channel into something recoverable and trustworthy, while still allowing irreversible outcomes to be explained rather than falsely undone.
- **path:** pendant → relay → mac-planner → mac-vision → browser → dashboard
- **model tier:** Realtime resolves the short spoken reference and reports the result. Each downstream surface records a structured inverse or compensating operation; a cheaper background model may rank candidate prior actions, but exact undo selection should rely on structured receipts and timestamps rather than generation.
- **latency:** Identify the most recent eligible operation and speak its scope in under 2 seconds. Execute a reversible inverse within 5 seconds where possible; if reconciliation is needed, report progress asynchronously and provide a concise final state.
- **cost:** Approximately $0.001–$0.01 per request, mostly from resolving ambiguous natural-language references or summarizing conflicts. Storage and inverse-operation metadata are small; browser replays and Mac file/app operations dominate execution time, not token cost.
- **security:** An incorrect inverse can destroy work or create duplicate side effects. Store exact before/after metadata where feasible, use idempotent compensating operations, detect intervening edits, and preserve an append-only audit trail. Do not claim an external email/payment/delete was undone when only a local draft or UI state was reverted; speak the boundary clearly. The owner has rejected approval gates, so ambiguity should produce a safe explanation/list rather than a hidden guess.
- **missing:** A cross-surface action journal with stable operation IDs, causal ordering, affected resources, and inverse/compensation descriptors; Mac and browser adapters that capture enough before-state or provider-specific undo tokens to perform reliable reversals; Conflict detection for changes made after the original action, with a dry-run preview spoken or shown on the dashboard; A relay resolver for phrases such as 'last thing', 'the Outlook one', and 'what you did this morning' bound to the journal; Retention, encryption, and dashboard inspection tools for the journal and failed-compensation cases


## Changes it proposed to its own stack

### `routines` — Add a scheduler layer (cron-like) with durable job definitions and a queue that can run tasks later, with retry and idempotency. Provide a relay-visible status feed.
- **owner gets:** Enables daily briefings, page watches, and “do this later” tasks that currently cannot happen at all. The owner gets reliability and timing, not just immediate reactions.
- effort: High: needs a durable store, queue semantics, and integration with mac-planner and browser harness.  ·  risk: Tasks could run at the wrong time or duplicate; mitigate with idempotency keys and clear audit logs; allow cancel/disable.
- cost: Moderate ongoing compute/storage; dominated by scheduled runs and browser/Mac execution.  ·  latency: Improves perceived latency by doing work ahead of time; adds no cost to immediate voice interactions.
- security: Scheduler must enforce least-privilege access to private data and record provenance; logs must avoid sensitive content.
- depends on: Durable context store for job metadata; Job status API consumable by relay


## What it asked for

_Nothing._
## Its own summary

Recorded three new capabilities: authenticated browser page-change watches with material-diff alerts; durable cross-device jobs that notify the pendant on completion and support voice follow-ups; and cross-surface undo/compensation through an action journal. What is still needed is durable scheduling/event infrastructure, browser page-watch adapters, downstream completion callbacks, pendant push delivery, short-lived continuation context, and structured inverse-operation metadata across Mac and browser surfaces.

**Biggest unknown:** Whether the browser harness can safely persist and reopen authenticated sessions and expose stable DOM/content fingerprints without leaking secrets; that determines the implementation and security boundary of the page-watch capability.

