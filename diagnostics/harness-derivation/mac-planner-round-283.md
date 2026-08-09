# Harness derivation — mac-planner — round 283

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac accessibility and screen recording readiness** — The live Mac agent now reports Accessibility trusted, synthesized input verified, Screen Recording granted, secure input inactive, and no missing automation permissions. AI Pendant Agent can reach the screen; this supersedes the older denied-status finding.
  - evidence: GET /ops/status at 2026-08-09T02:14:22Z: permissions.accessibility.trusted=true, screenRecording.granted=true, inputReachability.status=verified, automation.requiredMissing=[]; GET /observe independently reports uiActionsWillReachTheScreen=true.

## Capabilities it proposed

### "“Remember this in context — the page, app, and project I’m looking at — and turn it into something I can act on later.”"
- **useful because:** A short button press or spoken memo would stop being an orphaned timestamp. The relay would bind the capture to the live Safari tab, foreground Mac app, active project, and nearby calendar context, then produce a searchable note with a concrete next action. This is the highest-value everyday bridge: fleeting thoughts become attached to the thing that caused them, without making the owner narrate URLs or filenames.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime only for the spoken capture and entity extraction; a cheaper background model resolves project identity, deduplicates against existing notes, and drafts the next action.
- **latency:** Acknowledge on the pendant in under 300 ms; bind the context in under 5 s; background enrichment under 60 s. If the Mac or browser is offline, retain the capture and attach context when they return.
- **cost:** About $0.005–$0.03 per capture depending on audio length; most cost is speech transcription and background entity linking, not the realtime turn.
- **security:** The capture may contain private speech and page titles/URLs. Send only redacted snippets and stable local identifiers to the relay; keep raw audio local and expire it after transcription. Never copy password fields or page bodies. Creating a note is low-risk under the owner's stated policy, but external sharing is not allowed without confirmation.
- **missing:** A cross-surface context-binding route that accepts a pendant bookmark/voice memo plus Mac/browser observation and returns a durable linked artifact; A local semantic read for selected text/document identity (the currently pending mac_semantic_context_read request); Relay support for linking offline_moment_bookmark and offline voice memos to a project/action rather than only storing independent events

### "“Ask me on the pendant before you send, delete, buy, or publish anything consequential, then do it and prove what happened.”"
- **useful because:** The owner can keep maximum automation without trusting a fragile browser prompt or a foreground Mac window. The relay prepares the exact operation, the pendant shows a short spoken summary and uses its physical button for a deliberate out-of-band commit, and the Mac/browser executes only that prepared operation. A receipt with the target, before/after evidence, and undo path closes the loop.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime for the short confirmation conversation; deterministic server logic for token issuance, expiry, idempotency, and receipt validation. No expensive model is needed to decide whether a previously approved plan matches.
- **latency:** Prepare in under 2 s, speak confirmation in under 1 s, and execute within 3 s of the button press. Tokens expire after 60 s and are single-use.
- **cost:** Under $0.01 per action; the dominant cost is a short realtime prompt, while signing, matching, and receipt storage are negligible.
- **security:** A confirmation must bind to an exact normalized URL/app/resource, action arguments, account/session, and hash of the prepared plan; a changed page or stale browser tab must invalidate it. Do not speak or log secrets. Sending mail, deletion, purchases, and external publication require this path; drafts, local notes, and reversible navigation do not. The current FULL_CONTROL_MODE bypasses actionRisk, so this must be enforced at the relay-to-Mac execution boundary rather than merely classified in the UI.
- **missing:** A relay-issued, single-use action capability token accepted by POST /execute and browser commands; A pre-execution plan hash and post-execution receipt schema that records target, result, and evidence and can be joined to the action ledger; A pendant confirmation transport that is distinct from ordinary speech and cannot be replayed after link loss

### "“Set up everything I need for this task, and when I’m done, put my Mac and browser back exactly as they were.”"
- **useful because:** The owner can delegate disruptive context switching without losing their current work. The system would snapshot open browser sessions/tabs, foreground app, relevant file state, and a reversible action plan; stage the requested workspace; then restore the prior state on a pendant button press, spoken command, or expiry. If the Mac crashes, the relay keeps the manifest and resumes or restores idempotently instead of guessing.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** A cheap planner creates the workspace manifest from deterministic observations; realtime is only needed if the owner describes the task conversationally. Restoration and deduplication must be deterministic, not model-generated.
- **latency:** Snapshot under 2 s, setup under 10 s for a bounded task, restore under 10 s. A transaction can remain open for hours, with a visible expiry and an explicit 'leave as-is' option.
- **cost:** Typically below $0.01; model cost is only for translating a vague task into a bounded plan. Storage is a small manifest plus file hashes.
- **security:** Do not snapshot passwords, private page bodies, secure-input fields, or raw screen images by default. File restoration must use atomic staging and hashes, and never silently overwrite changes made after setup. Deleting or moving user files still follows the owner's destructive-action policy. Browser restoration must be scoped to the exact session and tab IDs, not merely URLs.
- **missing:** A cross-surface snapshot/restore manifest covering browser tabs, app/window identity, and selected workspace files; A browser command to open/close/reorder tabs and restore session affinity atomically; A transaction coordinator that joins mac_workbench_transaction receipts with browser and Mac action receipts and detects owner changes before rollback

### "“Undo the changes I made across my Mac and browser since 2 PM, but leave anything I changed myself alone.”"
- **useful because:** Today undo is fragmented: browser history, app undo stacks, file moves, notes, reminders, and queued jobs do not share a common boundary. The owner needs a time-bounded, cross-surface rewind that identifies only AI-attributed mutations, previews the exact inverse operations, and restores the pre-change state without touching intervening human edits. This is a genuine safety net for delegation, not merely another confirmation prompt.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic event correlation and inverse generation; use a cheap model only to summarize the preview in plain language. Realtime is unnecessary unless the owner asks by voice and needs immediate acknowledgement.
- **latency:** Return a preview in under 3 seconds for the last hour; apply a bounded rewind in under 15 seconds. If any inverse cannot be proven safe, stop that item and report it rather than guessing.
- **cost:** Under $0.01 per rewind; storage and hashing dominate, not inference.
- **security:** Every mutation needs an actor, resource version, before/after hash, and inverse or explicit non-reversibility marker. Never reverse owner-authored edits, external sends, purchases, or deletions without a separate destructive confirmation. Secrets and page bodies stay local; the relay receives only resource identifiers and redacted operation summaries.
- **missing:** A unified append-only mutation journal shared by Mac execution, browser commands, reminders/notes, and relay jobs, with actor attribution distinguishing AI from the owner; Inverse operations with optimistic concurrency checks for files, app state, browser tabs, notes, and reminders; current job undo is too narrow and cannot span browser state; A preview/apply endpoint that accepts a time window and conflict policy, then emits one cross-surface receipt

### "“Fill out this form using my files and calendar, but keep passwords and sensitive fields hidden from the AI, and let me review the exact submission before it goes.”"
- **useful because:** The owner can complete tedious applications without handing the model unrestricted access to secrets. The browser extension supplies field structure and session state, the Mac reads only explicitly relevant local documents, and a local redaction/field-policy layer fills safe fields while leaving credentials and high-risk answers for the owner. The pendant can give a compact final review and commit signal even when the browser window is elsewhere.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** A low-cost model maps approved document facts to form labels; deterministic field policies enforce secret/high-impact exclusions. Realtime is only for the spoken review and final commit.
- **latency:** Field inventory in 3 s, draft completion in 15 s, final review under 10 s. Never submit automatically; the owner must see or hear the exact final field/value diff.
- **cost:** $0.01–$0.05 per form, dominated by document extraction and field mapping; secrets remain local and are not sent for inference.
- **security:** Each field needs a sensitivity class, source citation, confidence, and an allow/deny policy. Passwords, payment data, government identifiers, signatures, and free-text legal attestations are never model-filled. The browser must verify origin and account before accepting values, and submission requires a one-use confirmation bound to the final diff.
- **missing:** A browser field-inspection and typed-fill interface that returns labels/types/origins without exposing password values; A local redaction and provenance service joining mac_read_sources/file reads to individual form fields; A final-diff renderer that can be delivered to the pendant and cryptographically binds confirmation to the exact browser submission

### "“Package everything needed to hand this project to someone else, with sources and a checklist, but strip secrets and tell me exactly what will leave my Mac.”"
- **useful because:** Handoffs today are manual and unsafe: files, browser links, notes, and the reason for decisions live in different places. This would create a reproducible project bundle with provenance, redaction findings, unresolved dependencies, and a spoken/visual data-egress manifest. The owner can review it before it is copied or sent, and the recipient gets a usable handoff rather than a folder dump.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Cheap background extraction and summarization over locally selected files and page metadata; deterministic secret scanning, hashing, and manifest generation. Realtime only summarizes the final egress manifest on request.
- **latency:** Inventory under 10 s for a bounded project folder and current browser session; draft bundle under 60 s. No external upload until the owner confirms the manifest.
- **cost:** $0.02–$0.10 per bundle for extraction/summarization; local hashing and archive creation dominate wall time.
- **security:** Default to local staging. Scan for credentials, tokens, private keys, personal identifiers, and hidden metadata; quarantine rather than silently redact ambiguous content. Include source paths, hashes, and excluded-item reasons in a reviewable manifest. External sharing, email, and uploads remain explicit high-impact actions.
- **missing:** A project-bundle planner that joins active project state, local files, Notes, calendar context, and browser tab metadata into one manifest; A local secret/metadata scanner with deterministic redaction and an owner-visible egress report; An atomic archive-and-share handoff built on the existing workbench transaction and action receipts, with no upload before approval


## What it asked for

_Nothing._
## Its own summary

This round produced three distinct cross-node capabilities: (1) bind a pendant bookmark/voice memo to the exact live Mac/browser/project context and turn it into an actionable artifact; (2) use a single-use, plan-hash-bound pendant confirmation for consequential Mac/browser actions, with verified receipts; (3) transactionally snapshot and restore the owner’s browser/apps/files around a delegated workspace setup. I also verified a major environment change: Accessibility, Screen Recording, synthesized input, and all required Mac automation permissions are now live and healthy, so vision/UI execution is no longer blocked by TCC. I informed relay-realtime of the three proposals and their missing seams.

**Biggest unknown:** The live resolver cannot disambiguate mac_readonly_inspect(browser_tabs): action:browser_inspect, POST /browser/inspect, and action:browser_list_tabs tie, so I could not re-read browser tabs through that granted tool this round. The underlying /observe and /ops/status do show Safari online with two tabs. Still needed for the proposed work: a cross-surface transaction/token coordinator, browser tab snapshot/restore primitives, and a semantic selected-text/document identity read.

