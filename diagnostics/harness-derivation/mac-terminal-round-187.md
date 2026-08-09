# Harness derivation — mac-terminal — round 187

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live cross-surface state** — Mac agent, relay, and Safari extension are all online. Relay last saw Mac bridge at 2026-08-08T03:13:27Z; Safari active tab is X Home with 9 tabs. GET /browser/inspections is empty even though GET /jobs contains a recent successful browser_read_page receipt with evidence capsule.
  - evidence: GET /ops/status, GET /browser/inspections, GET /jobs

## Capabilities it proposed

### "“Why did that task fail, and what exactly happened?” Give me a spoken, evidence-backed postmortem for the last thing I asked the pendant to do."
- **useful because:** Today the owner gets a vague failed message. This would join the pendant turn, relay pipeline, Mac job/action receipts, shell stderr/exit status, and browser command result into one causal timeline, distinguishing planner failure, transport loss, command failure, and partial completion. It turns an opaque autonomous system into something the owner can actually diagnose hands-free.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime model only for the short spoken explanation; a cheap background summarizer builds the causal trace from receipts and journal records.
- **latency:** Under 2 seconds for the first answer from existing records; under 10 seconds if a background trace must be assembled.
- **cost:** ~$0.002–$0.01 per explanation; dominated by realtime speech response, not log collection.
- **security:** Shell output and authenticated browser metadata may contain secrets. Redact environment variables, cookies, tokens, and likely-secret patterns before relay/model exposure; provide a local-only detailed view in the dashboard and speak only the minimum evidence.
- **missing:** Capture shell exit code, signal, pid/process-group, effective cwd, timeout, and rewritten-command provenance in the durable receipt.; Persist a common correlation ID from the pendant turn through relay job, Mac job, action ledger, and browser command.; A server-side causal-trace assembler and redaction layer; current /jobs and /journal are separate and do not join reliably.

### "“Keep working on this until it is actually finished, even if the Mac agent restarts or the browser loses its connection.” Treat this as one durable mission and tell me only when it reaches a verified stopping condition."
- **useful because:** A multi-step browser-plus-Mac task currently behaves like a sequence of one-shot jobs: a crash, browser disconnect, or transient command error strands it and leaves the owner guessing. A durable mission would checkpoint after every observable milestone, reattach after restart, retry only explicitly idempotent steps, and require a fresh verification before claiming success.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Background/cheap model for checkpoint classification and retry planning; realtime model only for owner updates or ambiguity.
- **latency:** No extra latency for individual steps; recovery within 15 seconds of agent/browser heartbeat returning. Spoken updates should begin within 1 second.
- **cost:** ~$0.01–$0.05 per mission depending on retries and browser screenshots; most checkpoint work is deterministic.
- **security:** Persist only task intent and step hashes, never page cookies or raw shell environment. A replay must reject non-idempotent steps unless an explicit compensating action exists. Owner must be able to say “stop” from the pendant and see the exact checkpoint.
- **missing:** A durable mission record distinct from transient jobs, with step preconditions, idempotency class, checkpoint and verified-stop predicate.; Boot reconciliation that converts stale processing jobs into resumable missions, closes ledgers, and can terminate/reap orphaned shell process groups.; Browser heartbeat-aware resume and a cross-surface cancel/stop command that reaches the actual child process.

### "“What am I looking at, and what is the next useful action?” Use the active Safari page, the visible Mac app, my active project, and the last few pendant turns to answer in one short spoken response; if I say “do it,” carry out that next action."
- **useful because:** This is the core hive-mind experience: the browser alone cannot know the local project or voice context, and the Mac alone cannot see authenticated page semantics. It eliminates the costly ritual of explaining context aloud and makes the pendant a hands-free bridge from perception to action.
- **path:** pendant → relay-realtime → mac-vision → mac-planner → browser-extension → dashboard
- **model tier:** Cheap vision/text model fuses screenshot and DOM summaries; realtime model speaks the concise answer and resolves the owner's “do it” confirmation.
- **latency:** Initial answer within 3 seconds, action dispatch within 1 second after “do it.” Capture can happen concurrently across Mac and browser.
- **cost:** ~$0.01–$0.04 per query, dominated by screenshot/vision tokens; cache unchanged DOM and project summaries to avoid resending context.
- **security:** Authenticated page content and screenshots leave the device only for the requested turn; redact password fields, payment data, and hidden DOM. Never execute inferred actions without the explicit follow-up phrase. Keep a local audit link to the exact screenshot/DOM snapshot used.
- **missing:** A synchronized snapshot API that atomically captures active window, active Safari tab/DOM inspection, active project, and recent pendant turn ID.; A cross-surface fusion prompt/cache with provenance so the answer cites which surface supplied each fact.; A confirmation-bound handoff that converts the selected next action into /execute or browser command without losing the snapshot correlation.

### "“Before you do that, prove that you are acting on the page and file I mean; if the browser, screen, and task history disagree, tell me exactly what conflicts instead of guessing.” Then, after I say “yes,” execute and verify the same target is still in focus."
- **useful because:** Today the system can read a browser page, inspect Mac state, and execute actions, but it has no owner-facing identity check that binds those observations to one target. A stale Safari tab, a changed URL, or a similarly named local file can produce a confidently wrong action. This capability would make the hive mind trustworthy for consequential everyday work without reducing its maximum access: it detects disagreement, explains it briefly through the pendant, and proceeds when the owner resolves it.
- **path:** pendant → relay-realtime → mac-vision → mac-planner → browser-extension → dashboard
- **model tier:** Cheap deterministic matching first (tab ID/URL/title, window/app identity, file inode/hash, job/session ID); use the realtime model only to phrase a short conflict report and interpret the owner's resolution.
- **latency:** Target proof in 1–2 seconds; re-check immediately before dispatch and within 1 second after completion.
- **cost:** ~$0.001–$0.01 per action; deterministic identity checks dominate latency, with model cost only for ambiguous conflicts.
- **security:** Do not send raw page contents or file contents merely to establish identity. Use URL, tab/window IDs, titles, hashes, and redacted metadata; treat a changed authenticated page as a conflict rather than silently refreshing or reusing stale evidence. Keep the proof bundle locally auditable.
- **missing:** A first-class target identity/proof object shared by browser commands, Mac actions, and pendant turns, with observedAt timestamps and expiry.; Mac-side foreground-window and file identity capture (bundle ID, window ID, path/inode/hash) exposed alongside machine context.; Browser-side atomic tab identity plus DOM/content hash at both inspection and action time; current inspections can be empty even when a browser receipt exists.; An execution preflight/postflight hook that compares the proof object and records a verified-target result without turning maximum-access execution into a blocking policy.

### "“Undo the last thing you changed, everywhere.” Reverse the browser mutation and the related Mac file or app change as one operation, and tell me if any part cannot be safely restored."
- **useful because:** The owner can already undo a narrow subset of Mac actions, but a real task often crosses an authenticated webpage and local files. A browser form submission, downloaded artifact, renamed file, or edited document currently has no coherent cross-surface rollback. This would give the pendant a practical safety net after autonomous work without imposing approval gates before it runs.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic compensating-action engine for known mutations; realtime model only to explain irreversible portions and ask which partial rollback the owner wants.
- **latency:** A rollback plan should be spoken within 2 seconds; execute reversible steps within 5 seconds, with verification after each surface.
- **cost:** ~$0.002–$0.02 per rollback; mostly deterministic storage and verification, with model cost only for ambiguous mappings.
- **security:** Snapshots may contain authenticated form data and private files. Encrypt local snapshots, apply short retention and field redaction, never store passwords or payment secrets, and clearly report irreversible effects such as sent messages or external submissions.
- **missing:** A cross-surface mutation bundle recording pre-state and compensating action for browser commands as well as Mac actions.; Browser primitives for restoring form values/navigation or issuing an application-specific undo, plus local file snapshot/version integration.; A dependency-aware rollback planner that reverses browser and Mac steps in safe order and marks partial failure explicitly.; Pendant-accessible lookup of the last completed mutation bundle, with retention and privacy controls.


## What it asked for

_Nothing._
