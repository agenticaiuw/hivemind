# Harness derivation — mac-terminal — round 266

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “resume that” into the pendant, continue the interrupted task from the last safe boundary—whether it was a Mac shell step, a browser session, or an iPhone action—and tell me exactly what will be retried before doing it."
- **useful because:** Today a dropped link, Mac restart, or browser timeout leaves the owner guessing whether repeating will duplicate an email, purchase, edit, or download. A single spoken resume command would turn the pendant into a trustworthy continuation point, using the Mac ledger, browser session state, and relay durability together rather than making the owner reconstruct the task.
- **path:** pendant → relay → mac-planner → browser-harness → iOS → dashboard
- **model tier:** background for journal reconstruction and duplicate-risk analysis; realtime only for the short spoken explanation and confirmation
- **latency:** Under 2 seconds to report the last safe boundary; 5–15 seconds to reconstruct a browser or Mac continuation. Never silently re-run an uncertain side effect.
- **cost:** About $0.01–$0.05 per resume, dominated by a small reasoning call over the journal and any browser snapshot; most status reads should be local and free.
- **security:** The relay must send only the selected job's journal, not unrelated history or secrets. Browser cookies remain in the extension. Re-running irreversible actions requires an explicit spoken confirmation; read-only and idempotent steps can continue automatically. The result must say 'unknown' when the prior step's commit state is ambiguous.
- **missing:** A durable job-to-ledger join and closed ledger on every /execute; Boot-time reconciliation of processing jobs and interrupted ledgers; Per-action commit markers and idempotency keys shared by Mac, browser, iOS, and relay; A planner that can classify a step as safe-to-retry, already-completed, or ambiguous; A pendant/relay request carrying the original task id and resume cursor

### "If I say “stop” or press the pendant's second button, halt the task currently running on my Mac, browser, or mirrored iPhone, then tell me whether it actually stopped, what step was in flight, and what partial changes remain."
- **useful because:** A cloud voice request can outlive the conversation that created it. The current cancel path only sets a cooperative signal, cannot kill a running shell, and can leave a browser or phone action underway. A physical stop that is acknowledged by the executing surface gives the owner a real brake instead of a reassuring but false cancellation message.
- **path:** pendant → relay → mac-planner → browser-harness → iOS → dashboard
- **model tier:** Realtime for recognizing the short stop command and returning the acknowledgement; no LLM needed to propagate the cancellation or verify process state
- **latency:** Dispatch in under 250 ms; show 'stop requested' immediately, then report verified stopped/uncertain within 2 seconds. Never claim stopped until the Mac/browser/iOS surface returns a terminal acknowledgement.
- **cost:** Near-zero model cost for the control path; at most $0.001 for a concise spoken status if interpretation is needed.
- **security:** Only the active task bound to the pendant session may be stopped; a stale replayed stop must not affect a later task. The relay must authenticate a monotonic task sequence and reject duplicate or old stops. Partial side effects and sensitive command text should be summarized, not spoken aloud in public.
- **missing:** A real cancellation signal passed into child processes (AbortSignal/kill process group) instead of only checking between steps; Browser and iOS action cancellation plus a terminal acknowledgement protocol; A pendant-side physical stop event with durable task sequence, distinct from recording/end-call semantics; Relay fan-out that races cancellation to every surface and reconciles their acknowledgements; A journal entry for stop-requested, stopped, could-not-stop, and partial-state evidence

### "After you finish a task, say “show me the changes” and give me a compact before/after report across my Mac files, browser page, and mirrored iPhone—what was created, edited, sent, navigated, or left uncertain—with a link or undo action for each reversible change."
- **useful because:** A completion message is not evidence. The owner needs to know whether a document was actually saved, which browser fields changed, whether an iPhone action landed, and what remains uncertain without opening every app. A cross-surface diff is something no Mac-only or browser-only agent can provide.
- **path:** pendant → relay → mac-planner → browser-harness → iOS → dashboard
- **model tier:** Background model to normalize structured before/after records and write the summary; realtime only to answer the spoken follow-up and read a short result
- **latency:** Initial structured change list within 2 seconds of completion; deeper file/page comparison within 10 seconds. Never infer a change from intent when the surface did not return post-state evidence.
- **cost:** $0.01–$0.04 per report, mainly for summarizing many structured diffs; hashes, receipts, browser provenance, and iOS action results are local/low-cost.
- **security:** Do not upload file contents, page text, screenshots, or phone notifications by default—send names, hashes, field labels, URLs, and redacted values. Sensitive changes must be visible only on the local dashboard, with the pendant speaking a redacted summary. Undo must use the existing authenticated surface and preserve the original evidence.
- **missing:** A per-task before-state snapshot and post-state snapshot shared by Mac, browser, and iOS; Structured browser field-change and navigation receipts rather than only command completion; iOS action postconditions and screenshot/hash comparison through the Mac mirror; A cross-surface diff schema with sensitivity labels, provenance, and reversible undo handles; A dashboard view and pendant speech formatter that distinguish changed, unchanged, and unknown

### "When a task hits a login, permission, CAPTCHA, ambiguous form, or other human-only step, tell me exactly what you need on the pendant, pause safely, and continue automatically after I resolve it on the Mac or browser—without restarting earlier steps."
- **useful because:** Today a browser or Mac workflow either stalls silently or makes the owner repeat the whole task after handling the one human decision. A wearable prompt plus a durable pause cursor lets the owner resolve only the exception and preserves the work already done, across the relay, logged-in browser session, and Mac executor.
- **path:** pendant → relay → mac-planner → browser-harness → iOS → dashboard
- **model tier:** Realtime only for the short, private request and acknowledgement; background model for classifying the exception and rebuilding a continuation plan from structured state
- **latency:** Notify the owner within 1 second of a blocked human step; resume within 3 seconds after the browser/Mac acknowledgement. Wait indefinitely without spending model calls while the owner is away.
- **cost:** Typically $0.005–$0.02 per exception, mostly one concise classification and continuation summary; idle waiting is free.
- **security:** Never ask the relay to transmit passwords, MFA codes, CAPTCHA images, or private page contents. The browser extension handles credentials locally. The pendant should speak only the action needed (“approve the dialog on Safari”), and the dashboard shows details. Bind the response to the paused task and reject late acknowledgements.
- **missing:** A first-class paused-for-owner state and durable continuation cursor in the job/ledger model; Browser and Mac events for permission dialogs, login completion, CAPTCHA completion, and window focus; A browser-extension callback that reports only completion and a redacted reason; Relay push to the pendant plus a private local dashboard prompt; Continuation planning that proves prior side effects and does not replay them

### "When I say “undo what you just did,” reverse the last completed multi-device task wherever possible—Mac files and settings, browser edits, and mirrored-iPhone changes—in reverse dependency order, then tell me which parts were undone and which are irreversible."
- **useful because:** Today undo is fragmented: the Mac has partial action-specific undo, while browser and iPhone work have no shared rollback. The owner cannot safely recover from a completed task that touched several surfaces without manually reconstructing every change. A single spoken rollback command would make experimentation and delegation much less risky.
- **path:** pendant → relay → mac-planner → browser-harness → iOS → dashboard
- **model tier:** Background model to construct and validate a rollback plan from structured receipts; realtime only to recognize the short command and report the final rollback result
- **latency:** Acknowledge the target task in under 1 second; begin rollback within 2 seconds; report each surface's result as it settles. Never claim a rollback succeeded without post-state evidence.
- **cost:** $0.01–$0.05 per rollback plan, dominated by dependency analysis and summarization; deterministic inverse actions and state checks should be local.
- **security:** Rollback must be bound to the owner's authenticated session and an exact task id, not merely the latest global job. Deleting or reverting data is itself consequential, so the system must retain a recovery snapshot and clearly mark irreversible effects such as sent messages or external purchases. Sensitive file/page contents stay on their owning surface.
- **missing:** Cross-surface inverse-action contracts for Mac, browser, and iOS, including pre-state snapshots and post-rollback verification; A dependency-aware rollback planner that reverses actions in safe order and handles partial failure; Browser edit undo records and iOS mirror action receipts with stable target identifiers; A durable rollback snapshot store with retention and recovery after relay or Mac restart; A pendant command binding to the completed task id, plus a truthful per-surface rollback status protocol

### "After I complete a task once, let me say “make that repeatable,” and turn the verified Mac/browser/iPhone action sequence into a parameterized routine that asks only for the values that change, previews its effects, and runs on my schedule or from the pendant."
- **useful because:** The owner can demonstrate a workflow once instead of repeatedly explaining it to an agent. Existing routines can be scheduled, but they do not learn a successful multi-surface sequence with its provenance, variable fields, and recovery behavior. This would convert real work into a reusable personal capability without requiring the owner to write automation.
- **path:** pendant → relay → mac-planner → browser-harness → iOS → dashboard
- **model tier:** Background model to extract stable steps, parameters, and safety invariants from completed receipts; realtime only for naming the routine and answering a short parameter prompt
- **latency:** Draft the routine within 10 seconds after the request; parameter collection under 3 seconds per turn; scheduled runs should use the cheaper background path and report completion asynchronously.
- **cost:** $0.02–$0.10 to synthesize and validate a routine once; subsequent runs are mostly deterministic and low-cost, with model use only when a page or UI has changed.
- **security:** Do not persist passwords, MFA values, session cookies, or raw sensitive page contents as routine parameters. Store selectors and redacted field semantics, require re-authentication locally, and make destructive or external-send steps explicitly visible in the preview. A routine must retain source receipts so the owner can disable it if the site changes.
- **missing:** A routine synthesizer that extracts stable actions versus per-run parameters from Mac, browser, and iOS receipts; Versioned browser selectors and iOS target identities with drift detection; A routine preview that shows external side effects and a dry-run result before scheduling; Parameter vault integration that keeps secrets on the owning surface; A cross-surface routine runner with step-level evidence, retry policy, and failure handoff to the pendant

### "Let me say “rehearse that” before a task, and have the system walk the real Mac, logged-in browser, and mirrored iPhone flow without committing changes, showing the exact fields, files, messages, and external effects it would touch before I choose to run it."
- **useful because:** Current planning and previews are mostly abstract; they cannot expose a changed selector, a wrong account, or an unexpected phone dialog without risking the real action. A cross-surface rehearsal lets the owner test unfamiliar automation against their actual sessions while keeping the side effects uncommitted.
- **path:** pendant → relay → mac-planner → browser-harness → iOS → dashboard
- **model tier:** Background model to compare the rehearsal trace with the intended task; realtime only to answer follow-up questions and read the compact impact summary
- **latency:** Start feedback within 1 second and produce a rehearsal trace within 10–30 seconds, depending on page and app load. Rehearsal must stop at any surface that cannot provide a non-committing mode instead of pretending.
- **cost:** $0.02–$0.10 per rehearsal, dominated by screenshots/DOM interpretation for UI-only steps; deterministic Mac reads and browser snapshots are inexpensive.
- **security:** A rehearsal must never type secrets, submit forms, send messages, purchase, delete, or alter clipboard/files. Browser and iOS surfaces need explicit dry-run adapters, and any unavoidable navigation must be labeled. Do not export page contents or phone data to the relay; retain a redacted local trace.
- **missing:** A true dry-run contract for every Mac, browser, and iOS action, including non-mutating substitutes for UI-only controls; Surface-level effect declarations and postcondition checks that detect accidental mutation; A rehearsal trace format with target identity, account, fields, files, URLs, and redacted values; A planner that refuses to rehearse when an action cannot be proven non-committing; Pendant/dashboard presentation of the trace and a run-from-this-rehearsal handoff


## Changes it proposed to its own stack

### `model-routing` — Add a deterministic, local control-intent fast path for the small set of pendant commands that must remain truthful under latency or relay loss: stop, resume, what is running, show changes, and repeat last result. It should resolve only an authenticated task sequence and dispatch the existing status/cancel/journal calls; fall through to the expensive model for anything ambiguous. Return a literal state vocabulary (requested, acknowledged, completed, failed, unknown) rather than generated reassurance, and cache the last safe spoken response on the pendant.
- **owner gets:** The owner gets an immediate, dependable answer while walking or when the cloud model is slow: “stop” is acted on now, and “what is running?” does not burn a full reasoning turn. The same path prevents the most dangerous failure—an eloquent model claiming completion when the Mac, browser, or relay is unreachable.
- effort: Medium: a signed intent grammar, monotonic task binding, relay and Mac dispatch adapters, and tests for stale/duplicate button and voice events. No new model training is needed.  ·  risk: A too-broad grammar could misinterpret ordinary conversation as a control command. Keep the trigger vocabulary intentionally narrow, require the current task sequence for action, and send uncertain phrases to normal conversation. The cached response can become stale, so always include its age and source.
- cost: Cuts model calls for frequent status/control turns to effectively zero; small local CPU and a few hundred bytes of pendant state.  ·  latency: Local recognition and relay dispatch target under 250 ms; cloud fallback retains current latency.
- security: A control command needs a per-session nonce and monotonic sequence to prevent replay from an old audio/button event. Do not cache command text or sensitive output on the pendant—only state enum, age, and opaque task id.
- depends on: truthful_action_status_beacon on the pendant; audio_link_truth_and_recovery for link truth; A durable task sequence shared by relay and Mac jobs; Terminal acknowledgement endpoints for Mac, browser, and iOS


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing capabilities and one accepted routing change: (1) spoken “resume that” with safe continuation across Mac/browser/iOS, (2) verified physical or spoken stop with truthful terminal acknowledgement, (3) “show me the changes” cross-surface before/after evidence, and (4) a local fast path for stop/resume/status/change commands. The most useful is resumable, exactly-once continuation: it turns dropped links and restarts from dangerous guesswork into a recoverable task. I also confirmed the newly granted USB serial diagnostic schema still has no live implementation; the Mac is online but the pendant is currently reported offline.

**Biggest unknown:** The remaining blocker is implementation truth at the execution boundary: no live serial reader tool, no durable job↔ledger join/closure, no process-group cancellation, and no post-state event contracts for browser/iOS. I still need a real bounded serial diagnostic route (or an allowlisted shell-backed implementation) and live confirmation of the pendant/ESP32 UART frames before claiming bench continuity.

