# Harness derivation — mac-terminal — round 172

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When a Mac command fails, fix it for me: show me the exact failure, make one safe corrective attempt, and tell me what changed."
- **useful because:** Today a failed shell job loses the exit code and cannot be retried intelligently; the owner has to diagnose and reissue it manually. This turns the pendant into a practical operator rather than a one-shot command launcher.
- **path:** pendant → relay → mac-planner → mac-terminal
- **model tier:** background for diagnosis and repair planning; realtime only for the short spoken result
- **latency:** Under 3 seconds to report the failure; up to 30 seconds for one corrective attempt
- **cost:** Usually one cheap background inference; dominant cost is command execution, not tokens
- **security:** The repair can mutate files or processes under the owner's deliberately unrestricted Mac policy. Return command, cwd, exit code, stderr, diff/receipt, and never claim success without a post-check; require explicit confirmation only for destructive repairs if owner policy changes.
- **missing:** Capture real exit code, signal, pid, argv/env provenance, and rewritten-vs-submitted command in the shell receipt; A bounded repair loop with one retry and idempotency key; current cancellation cannot interrupt exec and no job retry is wired; Join job record to action ledger and close/reconcile ledgers so a repair can resume after restart

### "Save this page as evidence."
- **useful because:** A spoken request from the pendant should preserve the exact authenticated page the owner is looking at, not just a URL: snapshot the visible state, relevant text, timestamp, and provenance so it can be revisited even after the session changes.
- **path:** pendant → relay → browser-extension → mac-planner → mac-terminal
- **model tier:** background model extracts a concise title and evidence summary; realtime only acknowledges capture
- **latency:** Acknowledge in under 1 second; persist the bundle within 5 seconds
- **cost:** Low: one small extraction call; storage and screenshot dominate, with no web-search call
- **security:** Authenticated page contents leave the browser and are sensitive. Default to local Mac storage, encrypt the bundle, redact passwords/tokens/forms, show domain/title before persistence, and make sharing/export a separate explicit request.
- **missing:** Browser command that atomically captures sanitized DOM/text, screenshot, URL, tab identity, and page timestamp; Mac-side encrypted evidence-bundle store with content hash and retention policy; Relay index and pendant lookup by spoken title/date, including offline queued capture receipt

### "Watch this long-running task and interrupt me only if it needs me."
- **useful because:** The owner can hand off a build, sync, export, or research job and stop babysitting it. The Mac observes output and process health while the always-awake relay filters routine progress; the pendant speaks only a failure, permission prompt, completion, or a decision it cannot make.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension
- **model tier:** Cheap background classifier over incremental output; realtime model only when escalation is actually spoken
- **latency:** Detect an actionable event within 5 seconds; no periodic spoken chatter
- **cost:** Low-to-moderate: polling and local parsing dominate; model calls only on novel output or escalation candidates
- **security:** Output may contain source code, URLs, or secrets. Parse locally first, redact tokens, retain bounded excerpts, and never auto-answer a prompt that can grant permissions or send data. The pendant must label stale monitoring after Mac disconnect.
- **missing:** A supervisor job type that attaches to a PID/process group and streams bounded stdout/stderr incrementally; Event classifier with deduplication, quiet hours, escalation severity, and owner acknowledgement state; True process cancellation/reattachment and restart reconciliation; current /jobs cancel is cooperative between steps and exec has no signal

### "While I’m away, keep this task moving until morning, but stop at the first ambiguity and leave me a concise handoff."
- **useful because:** The owner can delegate a multi-hour workflow—such as a build, export, download, or research collection—without leaving the Mac unattended blindly. The system makes measurable progress, pauses when judgment is required, and gives the owner a ready-to-resume state instead of a vague failure.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension
- **model tier:** Background model for planning and checkpoint summaries; realtime only for an actual urgent escalation
- **latency:** Start within 2 seconds; checkpoint every 10 minutes or meaningful milestone; morning handoff under 10 seconds
- **cost:** Moderate background inference for milestones; local process observation and storage dominate
- **security:** A delegated task may access authenticated browser sessions and local files. Require a bounded lease, explicit allowed applications/projects, no silent privilege grants, encrypted checkpoints, and automatic expiry at the requested time.
- **missing:** A lease-based autonomous-work supervisor with deadline, scope, pause, and escalation state; Checkpoint format containing completed steps, pending decision, inputs, outputs, and exact resume action; Scheduler integration that survives Mac-agent restart and hands the checkpoint to the relay

### "Compare these two authenticated pages and tell me what changed, without exposing either page to the internet."
- **useful because:** The owner can compare two private dashboards, invoices, project views, or account pages using the browser session they already have. The system extracts only the relevant differences locally and speaks a short answer, instead of requiring screenshots, copy-paste, or an external web service.
- **path:** pendant → relay → browser-extension → mac-planner → mac-terminal
- **model tier:** Local deterministic DOM/table diff first; background model summarizes ambiguous differences; realtime speaks only the final result
- **latency:** First diff within 5 seconds; summary within 10 seconds for ordinary pages
- **cost:** Low to moderate: local parsing is cheap; one background summary call for irregular layouts
- **security:** Both pages may contain financial or work data. Keep raw DOM and screenshots on the Mac, redact credentials and hidden fields, send only a minimal diff to the model, and bind comparison to the current tab/session identities.
- **missing:** A browser capture API for two selected tabs or snapshots with stable semantic fields and timestamps; Local structured diff engine for tables, amounts, statuses, and changed text, including page-state validation; A relay request schema that carries tab references rather than URLs or page contents

### "Pick up the workflow where it stopped, even if the Mac restarted, and show me the one step you will repeat before doing it."
- **useful because:** A crash, sleep, update, or lost USB link should not erase a half-completed multi-app workflow. The owner gets a truthful resume point and can avoid duplicate uploads, messages, purchases, or file mutations while still recovering useful work.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension
- **model tier:** Background model reconstructs intent from a deterministic action checkpoint; realtime model explains the proposed next step
- **latency:** Reconstruct state within 3 seconds after Mac reconnect; resume after the owner’s spoken acknowledgement
- **cost:** Low: checkpoint validation is local; model is used only when the next action is ambiguous
- **security:** A stale browser session or changed page can invalidate a checkpoint. Revalidate tab identity, URL origin, file hashes, and preconditions; refuse to replay a side effect when state differs, and keep secrets out of checkpoints.
- **missing:** Crash-safe per-step checkpoint records shared by /execute, browser commands, and relay jobs; Idempotency keys and postcondition validators for browser and shell side effects; Startup reconciliation that distinguishes completed, interrupted, and unsafe-to-replay steps, then exposes a single resume plan


## Changes it proposed to its own stack

### `model-routing` — Add a local Mac failure-and-progress parser before any LLM call. It classifies exit status, common compiler/test/package-manager errors, permission prompts, and completion markers; only ambiguous excerpts go to the background model, and only owner-facing escalations reach realtime.
- **owner gets:** Long commands become quieter, faster, and cheaper: routine success is silent, familiar failures get an immediate precise explanation, and the expensive voice model is reserved for decisions that genuinely need conversation.
- effort: Medium: local parser, bounded stream reader, redaction, confidence thresholds, and routing hooks in the job supervisor.  ·  risk: A parser can misclassify a failure as success or suppress an important prompt. Use conservative completion rules, retain raw receipts locally, and escalate low-confidence events rather than dropping them.
- cost: Reduces inference spend substantially for builds and scripts; negligible CPU cost on the Mac.  ·  latency: Sub-second classification for known patterns; ambiguous cases add one background call.
- security: Less command output leaves the Mac; redaction happens before relay/model upload.
- depends on: A shell receipt carrying exit code and process identity; Incremental stdout/stderr streaming or bounded tail capture; Supervisor/monitor job type


## What it asked for

_Nothing._
