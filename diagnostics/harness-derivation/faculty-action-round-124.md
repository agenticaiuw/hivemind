# Harness derivation — faculty-action — round 124

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I press the pendant button, save what I’m looking at as a thought: capture the active Mac app and open browser tab context, classify it as a note, reminder, or idea, and give me a one-sentence spoken acknowledgment. Never send or delete anything."
- **useful because:** A physical, zero-friction way to remember the exact thing that prompted a thought; the Mac supplies context, the browser supplies the page, and the pendant supplies intentional capture even when the owner cannot type.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background for classification; realtime only for the acknowledgment
- **latency:** acknowledgment within 2 seconds; context enrichment within 10 seconds
- **cost:** ~$0.002–$0.01 per capture; classification dominates
- **security:** Active URL/title and selected context may leave the Mac; redact secrets and exclude password/payment fields. Creating reminders is allowed; anything outbound requires confirmation.
- **missing:** pendant button event bridge over current USB serial/LTE protocol; Mac endpoint to snapshot active app and browser tab with provenance; small capture classifier and deduplication policy; spoken-ack audio handoff to the pendant

### "Put me back in the middle of my last unfinished task. Reopen the exact files and private browser tabs involved, summarize the last successful and failed steps, and ask me for only the next decision you cannot make."
- **useful because:** After interruptions, the owner regains working context in one spoken request instead of hunting through tabs, files, logs, and failed jobs; it uses the pendant for intent, the Mac for state, and the browser for private session reattachment.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** background planner; realtime only to ask the one blocking question
- **latency:** restore visible workspace within 8 seconds; summary within 3 seconds after state loads
- **cost:** ~$0.01–$0.05 per restore; context compilation and browser inspection dominate
- **security:** Must not expose private page contents in relay logs; retain tab/session identifiers and local evidence only. Reopening is reversible; edits, sends, or submissions always stop for confirmation.
- **missing:** a resumable task bundle linking journal entries, files, tabs, and receipts; browser session reattachment with exact tab identity; Mac action to restore a workspace atomically and report partial failures; a compact cross-surface state summary

### "If I walk away while you are carrying out a reversible task, pause cleanly; when I reconnect the pendant, tell me what completed, what is still pending, and offer to continue from the next safe step."
- **useful because:** A dropped pendant link or leaving the Mac no longer produces an ambiguous half-finished action. The wearable is the owner's physical presence signal, while the relay, Mac, and browser preserve and explain safe continuation.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** cheap background state machine; realtime only for reconnection summary
- **latency:** pause within 1 second of link loss; reconnection status in 3 seconds
- **cost:** ~$0.001–$0.01 per task transition; storage and polling dominate, not model tokens
- **security:** Only pause/resume predeclared reversible steps; never resume sends, purchases, deletions, or submissions without fresh confirmation. Link presence is not identity alone; bind to authenticated device session.
- **missing:** device link-presence events over USB now and LTE later; step-level checkpoints and idempotent cancellation/resume semantics; a relay state machine that converts disconnect into pause and reconnect into a review; Mac/browser adapters that report completed versus attempted steps

### "Teach the system a task by doing it once while I narrate. Record the Mac and private-browser steps, identify which values are parameters, and turn it into a reusable routine that I can invoke later from the pendant without repeating the walkthrough."
- **useful because:** The owner gets personal automation for workflows unique to them, without writing scripts or exposing private sessions to a developer. The wearable starts the lesson or replay, the Mac and browser observe/act, and the relay stores only the reusable recipe.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background model for recipe extraction and parameter labeling; realtime only for spoken prompts
- **latency:** lesson feedback under 2 seconds; routine generation under 30 seconds
- **cost:** ~$0.03–$0.15 per taught routine; trace summarization dominates
- **security:** Do not record passwords, tokens, keystrokes in secret fields, or page contents by default. Replay must be preview-only until explicitly enabled; sending, deleting, purchasing, or submitting always requires confirmation.
- **missing:** cross-surface action trace recorder with sensitive-field suppression; recipe compiler that turns traces into parameterized, idempotent steps; routine test-run and versioning with rollback; pendant trigger for selecting and invoking a routine

### "Before I leave for an appointment, make me a private departure packet: verify the route and timing, gather the relevant meeting files and logged-in page details, put everything in one local folder, and give me a short spoken checklist. Do not contact anyone or change calendar events."
- **useful because:** It turns scattered Mac files, private browser information, and time-sensitive travel context into something usable while walking out the door; no single surface can assemble all three with current-session access.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background planner and extraction model; realtime only for the final spoken checklist
- **latency:** under 60 seconds for a normal meeting packet
- **cost:** ~$0.02–$0.10; private-page extraction and route lookup dominate
- **security:** Keep the packet local by default; avoid storing page secrets or precise location history beyond the requested trip. Never message attendees or modify calendar without confirmation.
- **missing:** calendar-to-browser-to-files entity resolver; local packet assembler with citations and expiry; route/time lookup that respects owner timezone and departure constraints; spoken checklist/audio queue delivery

### "Package everything I need to hand a project to another person: collect the relevant local files, notes, calendar commitments, and logged-in browser facts, remove secrets and personal data, and create a reviewable local handoff folder with a checklist. Do not share it or send it."
- **useful because:** The owner can delegate or transfer a project without manually searching four silos and accidentally leaking credentials. The Mac gathers local artifacts, the browser contributes authenticated facts, the relay coordinates, and the owner reviews one concrete folder.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background extraction and redaction model; realtime only to summarize what is ready for review
- **latency:** under 2 minutes for a normal project; always show progress and partial completion
- **cost:** ~$0.05–$0.30; document extraction and redaction dominate
- **security:** Default local-only output. Secret detection must fail closed, preserve originals untouched, and show every excluded artifact and redaction. Sharing or sending requires separate confirmation.
- **missing:** cross-source project artifact resolver; secret/PII redaction with human-review manifest; deterministic local handoff-folder writer and checksums; browser evidence export that strips session credentials and volatile personal fields


## Changes it proposed to its own stack

### `integration` — Add a Context Capture Broker between the pendant event stream, Mac machine-context, browser session inspection, and /capture. On one debounced intentional button event, it snapshots active app/tab metadata, applies URL/secret redaction locally, writes a provenance-linked capture record, and emits one spoken acknowledgment; do not make the classifier itself responsible for device or browser polling.
- **owner gets:** One button reliably remembers the exact moment and page that triggered a thought, rather than producing an unhelpful standalone note.
- effort: Medium: event schema, Mac/browser snapshot adapters, redaction, and capture transaction tests.  ·  risk: A stale tab or duplicate button event could attach wrong context; use sequence IDs, timestamps, and a visible 'context unavailable' acknowledgment rather than guessing.
- cost: Negligible storage; one cheap classification call only when needed.  ·  latency: Local snapshot under 500 ms; acknowledgment under 2 seconds.
- security: Sensitive URL/query/title data is redacted before relay persistence; raw context remains local unless explicitly requested.
- depends on: pendant button event transport; active-app and browser-tab snapshot endpoints; capture record accepting provenance

### `integration` — Introduce a Resumable Task Bundle manifest that atomically records task goal, exact file paths, browser session/tab IDs, completed step receipts, pending reversible steps, and a single blocked decision. Add a restore coordinator that reopens only those resources and returns a typed partial-restore report; this is a new cross-surface object, not another job queue.
- **owner gets:** The owner can resume interrupted work instantly and see what really happened without replaying steps or reconstructing context from logs.
- effort: High: manifest schema, journal/receipt adapters, browser reattachment, Mac workspace restore, and failure-injection tests.  ·  risk: Stale tabs or changed files could cause unsafe replay; restore must be read/open-only and mark every mismatch for review.
- cost: Small local/relay metadata footprint; background model call for concise summary.  ·  latency: Typically 5–10 seconds due to opening apps and private tabs.
- security: Keep page contents and file snippets on the Mac; relay stores opaque IDs, hashes, and minimal summaries.
- depends on: stable job step receipts; browser tab/session identity; Mac open-file/workspace action

### `relay` — Add a Presence-Scoped Execution Controller: consume authenticated pendant link up/down events, checkpoint the current reversible step before disconnect, transition the task to paused (never failed), and on reconnect produce a completion/pending diff requiring an explicit continue command. It must distinguish USB-attached development presence from future LTE presence.
- **owner gets:** Walking away or losing signal cannot leave the owner wondering whether a task half-ran; returning to the pendant yields an honest, actionable state.
- effort: High: device presence protocol, checkpoint contract across Mac/browser adapters, relay state machine, reconnect diff, and tests for disconnect at every step boundary.  ·  risk: A false disconnect could pause unnecessarily; debounce link changes and never infer authorization solely from presence. Irreversible actions remain excluded or require fresh approval.
- cost: Low persistent state and event traffic; no model call for transitions, cheap model only for the spoken diff.  ·  latency: Pause in under 1 second; reconnect report in under 3 seconds.
- security: Presence is a safety signal, not identity; bind to authenticated session and avoid sending private task data over unauthenticated reconnects.
- depends on: pendant USB/LTE authenticated presence events; idempotent step checkpoints; Mac/browser adapters exposing attempted/completed status

### `model-routing` — Add an action-risk compiler that converts a natural-language goal into a typed cross-surface execution graph before any tool call: read-only, reversible-local, externally-visible, destructive, and ambiguous nodes; route each node to the cheapest capable surface/model and stop exactly at the first policy boundary with a concrete preview.
- **owner gets:** The owner can state outcomes instead of micromanaging devices, while the system avoids both reckless execution and needless high-cost model calls.
- effort: High: typed graph schema, policy evaluator, surface capability registry, partial-plan previews, and adversarial tests across Mac/browser/relay actions.  ·  risk: Misclassification could skip confirmation or unnecessarily block useful work; default unknown actions to pause and show the exact intended effect.
- cost: Usually lowers cost by using background planning and deterministic adapters; adds small graph-compilation overhead.  ·  latency: Adds 0.5–2 seconds before execution, offset by parallel read-only steps.
- security: Creates an auditable record of data leaving the device and why each action was permitted; sensitive arguments remain local until approval.
- depends on: typed action schemas for Mac and browser; authoritative owner policy projection; precondition and side-effect metadata on every adapter; receipt graph linking plan nodes to outcomes


## What it asked for

_Nothing._
