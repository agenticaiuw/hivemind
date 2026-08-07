# Harness derivation — mac-terminal — round 104

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If something I asked you to do fails while I’m away, figure out why, retry safely when possible, and tell me exactly what happened when I’m back."
- **useful because:** Today failures are recorded but the owner must manually interpret them: the live store shows 18 failed actions, repeated browser_navigate failures, an offline browser bridge, and nine queued browser commands. The pendant should turn that into recovery rather than a dead-end error. The system can distinguish transient bridge timeouts, offline prerequisites, command nonzero exits, and irreversible partial completion; it should retry only transient/idempotent steps, resume from the last receipt, and speak a concise result when the owner returns.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision
- **model tier:** background for classification, retry planning, and post hoc summaries; deterministic rules for idempotency, receipt-based resume, backoff, and bridge health; realtime only to speak the final status if the owner asks live
- **latency:** Immediate acknowledgment under 1 second; retries use exponential backoff up to 15 minutes and continue while the Mac/relay are awake; final spoken summary under 3 seconds after the pendant reconnects
- **cost:** Usually <$0.01 per failed job: deterministic classification and retries are free, with one small gpt-4.1-mini call (~2k prompt tokens) only for ambiguous diagnosis; no planner-tier call unless recovery is genuinely ambiguous
- **security:** Failure diagnostics may contain shell output, URLs, private page text, or file paths. Keep raw stdout/stderr on the Mac, send only redacted error class and receipts to relay, and require the existing owner confirmation policy for any non-idempotent continuation; never retry submit/send/delete actions automatically
- **missing:** A durable retry state machine keyed by job/action idempotency key and receipt checkpoint; Structured shell/process result metadata (exit code, signal, timeout, cwd, duration, bounded/redacted stdout and stderr); A bridge-health-aware browser queue that pauses and resumes pending commands instead of timing each one out independently; Relay push event and pendant reconnect digest for recovered/failed jobs; Failure taxonomy and retry policy shared by Mac shell, browser, and mac-vision actions

### "When my Mac or browser comes back online, tell me what was waiting, what expired, and what you resumed—then let me say 'resume the safe ones' or 'drop them' from the pendant."
- **useful because:** The live Mac currently reports the browser offline with nine pending commands, while the job history contains repeated 45-second browser timeouts. A reconnect is otherwise silent and leaves stale work indistinguishable from active work. This gives the owner a short, wearable control surface for queued work without opening the Mac, while preserving the existing no-gate maximum-access policy for ordinary actions.
- **path:** relay → pendant → mac-planner → browser-extension → mac-vision
- **model tier:** Deterministic queue reconciliation and safety classification; background model only to turn job receipts into a concise spoken digest; realtime for the pendant conversation when reconnecting
- **latency:** Digest within 2 seconds of a bridge heartbeat or pendant reconnect; resume/cancel acknowledgement under 1 second; queued work continues asynchronously
- **cost:** Near-zero for heartbeat, queue reconciliation, and receipt lookup; <$0.005 per reconnect digest using gpt-4.1-mini only when more than three heterogeneous jobs need summarization
- **security:** Digest must not speak raw private URLs, shell output, or page content in public settings; use local redaction and job labels. 'Resume safe ones' may only resume idempotent/read-only checkpoints; send, submit, delete, payment, and other irreversible actions remain parked for the owner's existing confirmation path. Expire commands with a visible reason rather than silently discarding them.
- **missing:** A durable pending-command lease with created/expiry/last-heartbeat state and retry lineage; A reconnect event from browser bridge to relay, rather than polling-only status; A pendant intent endpoint mapping resume-safe/drop commands to job IDs; A deterministic resume classification from existing receipt effect and undoability metadata; A compact redacted spoken digest formatter

### "When I’m trying to focus, quietly watch what is happening across my Mac and logged-in browser, and tell me only when something genuinely time-critical changes—otherwise hold everything until I’m free."
- **useful because:** The owner currently has separate action, browser, calendar, and briefing mechanisms, but no cross-surface attention manager that understands both the work on screen and incoming obligations. This would prevent noisy interruptions while still surfacing a deadline, meeting change, or account event that cannot safely wait. It is not merely a morning briefing or page watch: it continuously reasons about the owner's current task, active window, calendar constraints, and authenticated changes, then chooses whether to interrupt the pendant, queue a digest, or do nothing.
- **path:** mac-planner → mac-vision → browser-extension → relay → pendant → faculty-perception → faculty-judgement
- **model tier:** Deterministic local perception for active app/window, focus state, calendar proximity, and change severity; background model for semantic urgency ranking across sources; realtime only for a truly urgent pendant interruption
- **latency:** Local signals under 500 ms; change triage within 5 seconds; nonurgent items batched for the next quiet-period digest; urgent spoken/haptic alert under 2 seconds after classification
- **cost:** Low: local event filtering handles most activity; roughly $0.01–$0.03 per day for background ranking of changed items, with no model call for unchanged state and no realtime use except actual urgent alerts
- **security:** Active-window titles, browser page metadata, calendar, and private account changes are sensitive. Keep raw observations on the Mac, send relay only a redacted urgency event and short owner-approved summary, support per-source opt-out and quiet hours, and never mutate or dismiss an item automatically. Screen content should require the existing explicit vision consent.
- **missing:** A local focus/attention state service combining active app/window, keyboard/idle signals, Calendar events, and pendant focus mode; A normalized cross-surface event bus with deduplication, source provenance, severity, expiry, and quiet-period buffering; A policy engine that distinguishes interrupt-now, queue, and suppress, with owner-tunable urgency rules; Browser change notifications that carry semantic diffs rather than raw page snapshots; A relay-to-pendant priority notification channel supporting haptic-only, spoken, and deferred delivery


## What it asked for

_Nothing._
## Its own summary

Fresh discovery completed. Live Mac status: FULL_CONTROL_MODE is on, relay and Mac bridge are reachable, but the browser extension is offline with 9 pending commands; Accessibility and Screen Recording are not granted, so mac-vision is not ready. The job store retains only 120 jobs and currently reports 18 failures, 79 writes, zero undoable jobs, and 112 unattributed routing tiers. I recorded two genuinely useful connective capabilities: failure-aware receipt-based recovery, and a pendant reconnect digest that reconciles, resumes only safe queued work, or drops it by spoken command. I also confirmed the newly granted Mac diagnostic/execution tools are schemas only and have no implementation.

**Biggest unknown:** Whether the existing open browser-runner/causal-ledger backlog is actually implemented in the current checkout; the live endpoints show receipts and journal views, but not durable retry leases, reconnect events, or structured run_shell exit/output metadata. What I still need is implementation of those missing pieces—not more permissions—and, if mac-vision is intended, the owner must grant Accessibility and Screen Recording.

