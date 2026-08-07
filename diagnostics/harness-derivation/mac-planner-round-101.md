# Harness derivation — mac-planner — round 101

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac/browser liveness** — At 2026-08-07T12:53Z the Mac bridge and relay are reachable and browser extension reports online, but home-chrome has no tabId/tabCount and 7 pending commands; computer-use loop is disabled, Accessibility and Screen Recording are not granted, while AppleScript automation grants are present.
  - evidence: GET /ops/status returned 200 with browserExtension online=true, tabId=null, tabCount=null, pendingCommands=7, computerUse.loopEnabled=false, accessibility.trusted=false, screenRecording.granted=false, automation grants cached.

## Capabilities it proposed

### "“If I start a multi-step task and then close my laptop or lose the browser, keep the work safe, resume it when the right device returns, and tell me exactly what was completed, skipped, or still needs me.”"
- **useful because:** Today the relay, Mac, and browser can each be online while a job still has seven queued browser commands, no usable tab identity, and no durable user-facing explanation of where execution stopped. This would turn an interrupted workflow into a recoverable one: the owner gets a concise pendant update and a Mac evidence folder instead of a silent timeout or duplicate submission. It is deliberately review-only for browser mutations; it can resume reads and drafts, but never silently sends or submits.
- **path:** pendant → relay → browser-extension → mac-planner → dashboard-ux
- **model tier:** Use a cheap background model for checkpoint reconciliation, stale-step classification, and summarization; reserve realtime only for the pendant's live explanation or a direct follow-up question.
- **latency:** A start acknowledgement in under 2 seconds; resume automatically within 30 seconds of a device heartbeat; final evidence brief within 1 minute after the last step. No repeated model call while waiting for a device.
- **cost:** Roughly $0.01–$0.05 per interrupted job, dominated by one small reconciliation/summarization call; storage and heartbeats are negligible. Avoid replaying page contents or resending full context at every retry.
- **security:** Persist only step metadata, redacted result snippets, source URL/tab/session IDs, hashes, and receipts; keep authenticated page bodies local to the browser/Mac evidence folder unless explicitly requested. Use idempotency keys and step leases so reconnects cannot duplicate a form fill or submission. Require explicit owner confirmation for any irreversible browser action, even though the Mac owner policy allows maximum local access.
- **missing:** A durable cross-surface checkpoint record with step state (pending/running/completed/expired/needs-owner), lease expiry, idempotency key, and dependency graph; A heartbeat and stale-step reaper that distinguishes browser offline, Mac offline, and an actually failed step; queued browser commands need dead-letter visibility instead of indefinite pending state; Resume semantics that reattach a browser session/tab when available and correlate Mac /execute job IDs with action receipts and the final evidence bundle; A small pendant notification/ack path for resumed, blocked, and completed states, plus a dashboard timeline showing before/after evidence and skipped steps

### "“I’m leaving my desk—freeze this work exactly where it is, and when I come back, restore the useful parts and remind me what I was doing.”"
- **useful because:** The owner loses working context whenever they close the laptop, move between locations, or return after an interruption. Today the system can act on individual Mac or browser jobs, but it cannot preserve the human’s live workspace as a resumable handoff: which documents and tabs mattered, what was unsaved, what the next intended action was, and what must not be reopened. This would create a private, time-bounded work capsule rather than another task queue.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard-ux
- **model tier:** Use a cheap background model to label the captured workspace and produce a short resume note; use the realtime model only if the owner asks follow-up questions through the pendant.
- **latency:** Acknowledge the freeze in under 2 seconds, capture a bounded manifest within 10 seconds, and restore or explain unavailable items within 20 seconds after the Mac returns.
- **cost:** Usually below $0.02 per capsule; the dominant cost is one small summarization call. Keep document contents local and summarize only metadata and explicitly selected snippets.
- **security:** The capsule may expose sensitive filenames, URLs, and unsaved text. Encrypt it, give it an expiry, allow an immediate pendant delete gesture, redact secret-like fields, and never silently reopen a private page or send a draft. Restoration should show a manifest first and require confirmation for reopening sensitive tabs or unsaved files.
- **missing:** A Mac workspace-capture adapter that records bounded app/document/browser manifests and unsaved-state warnings without requiring Screen Recording; An encrypted, expiring capsule format shared by relay and Mac, with a local-only option; Browser APIs for exporting and restoring a selected tab set with session affinity, without copying page bodies to the relay; A resume planner that distinguishes safe reopening from potentially destructive restoration and produces a cited next-step note; A pendant trigger and return-to-desk signal, such as an explicit button phrase plus Mac heartbeat reappearance

### "“When you finish something for me, tell me at the first moment I can actually absorb it—not while I’m presenting or driving—and escalate only if it is genuinely time-critical.”"
- **useful because:** A completed job is not useful if its result arrives during a meeting, focused writing, or an audio conversation and is then forgotten. Today results can be produced and queued, but there is no shared interruptibility decision across the relay, pendant, calendar, and Mac state. This would make completion delivery part of the task: urgent items break through with a concise alert, while everything else waits for a safe attention window and arrives as one grouped, sourced update.
- **path:** relay-realtime → pendant → mac-planner → dashboard-ux
- **model tier:** Use a small background model for urgency classification and grouping; use realtime only for a live spoken alert when the owner is already interacting with the pendant.
- **latency:** Classify on job completion in under 1 second; defer nonurgent results until the next detected safe window, with a configurable maximum delay such as 30 minutes. Urgent alerts should reach the pendant within 3 seconds.
- **cost:** A few cents per day at most; classification can use a compact model and calendar/app metadata, with no need to resend the original task context.
- **security:** Calendar titles, foreground-app names, and job contents are sensitive. Keep raw metadata local where possible, send only a redacted interruptibility signal to relay, expose why an alert was escalated, and provide a physical pause gesture. Never infer that a meeting is safe to interrupt merely because the calendar is empty.
- **missing:** A shared interruptibility state with calendar quiet periods, active pendant conversation, foreground app, and explicit owner pause/resume; A result mailbox that groups completed receipts by urgency and prevents duplicate audio or desktop notifications; A pendant delivery primitive supporting concise alert, deferred digest, and acknowledgement/snooze; A policy evaluator that can explain urgency and distinguish deadline risk from ordinary completion; A local Mac notification/Calendar adapter that works without Accessibility or Screen Recording


## Changes it proposed to its own stack

### `relay` — Add a cross-surface execution ledger and coordinator between existing /plan, /execute, browser command results, and job receipts. Every multi-step job gets a durable DAG of idempotent steps, a lease/heartbeat, required surface, input/output hashes, and monotonic sequence. A reconnecting browser or Mac claims only expired steps; a stale browser command is moved to dead-letter with its reason; completed steps are never replayed. Emit one normalized timeline to the dashboard and a compact pendant event. Keep payloads redacted and store full evidence only on the Mac when available.
- **owner gets:** When the laptop sleeps, browser extension disappears, or a request times out, the owner can trust that work will resume once—not run twice—and can see exactly what happened without inspecting logs or guessing whether a form was submitted.
- effort: Medium: schema/migrations, coordinator state machine, browser and Mac adapters, retry tests, and dashboard timeline. No new model training.  ·  risk: A bad idempotency key could suppress a legitimate retry, while an overly short lease could cause duplicate work. Recover with explicit step fingerprints, conservative lease expiry, dead-letter/manual-retry controls, and receipt reconciliation before any mutation. Existing jobs should be imported as unknown/legacy rather than guessed complete.
- cost: Small D1/storage and heartbeat traffic; one cheap background reconciliation call only for ambiguous failures. No realtime-token increase during offline waits.  ·  latency: Adds milliseconds to normal job dispatch; reconnect recovery is faster than today's repeated 20–45 second browser timeouts because stale commands are classified immediately.
- security: Improves auditability and prevents duplicate authenticated actions. Do not persist page bodies in relay; retain redacted snippets/hashes and local Mac evidence paths. Irreversible browser steps remain explicitly owner-confirmed.
- depends on: A stable idempotency-key convention shared by browser and Mac adapters; Receipt schema that includes requestId, stepId, and before/after evidence; A browser-side tab/session reattachment endpoint; A pendant event consumer for compact job-state notifications


## What it asked for

_Nothing._
