# Harness derivation — mac-planner — round 227

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Finish this for me.” (I say the task once on the pendant; use whatever is on my Mac and in my authenticated browser, do the reversible parts, and tell me exactly what happened.)"
- **useful because:** This would be the system's defining capability: an utterance becomes a grounded, resumable desktop result rather than advice. The pendant supplies intent while worn, the relay keeps orchestration alive, Mac/browser provide private reach, and the owner gets a receipt even if a link or app fails.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision
- **model tier:** Realtime only for the short intent capture and progress/error speech; a cheaper background planner grounds the request against /machine-context, /context-graph and live browser state, then the Mac planner executes the bounded plan.
- **latency:** Acknowledge on the pendant in under 1 s; inspect and present a plan in 3–8 s; execute reversible steps in under 30 s where possible. Long work becomes a tracked job with a spoken completion alert, not a blocked conversation.
- **cost:** Roughly $0.01–$0.05 per invocation depending on planner context; the expensive tier is used only for the utterance and final explanation. Browser/Mac inspection and receipts dominate wall time, not tokens.
- **security:** Private page text and local context must stay in the relay's redacted projection unless explicitly needed. The action policy slot is currently empty under FULL_CONTROL_MODE, so this must default to preview and stop on any policy entry not explicitly enabled by the owner; do not assume current bypass is consent. Require an explicit owner command to cross from preflight to mutation, and return touched resources plus receipt IDs.
- **missing:** A cross-surface intent envelope carrying utterance, context snapshot hash, plan version, and idempotency key; A server coordinator that joins browser command results, Mac action receipts, and pendant progress events into one job; A policy-aware transition from mac_action_preflight to mac_run_actions/mac_workbench_transaction; A compact pendant progress/error protocol and final spoken receipt

### "“Do this when the Mac is ready—on Wi‑Fi, plugged in, and not in a meeting—and let me know when it’s done.”"
- **useful because:** The owner can delegate expensive or disruptive work without babysitting a laptop. The relay can wait overnight, the Mac contributes real power/network/foreground state, Calendar contributes meeting exclusion, and the pendant receives one completion or exception instead of repeated prompts.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Background/scheduled model for eligibility checks and job planning; realtime is unnecessary except for the initial acknowledgment and final short notification.
- **latency:** Acknowledge immediately, poll conditions every 5–15 minutes, and start within two minutes of eligibility. No model call when the condition hash has not changed; completion notification within 30 seconds of the Mac receipt.
- **cost:** Under $0.005 for most invocations; mostly cheap state polling. A larger planner call occurs only when eligibility changes or a job fails.
- **security:** Calendar titles, Wi‑Fi identifiers, and power state are sensitive and should be reduced to booleans plus a time window. Never run while a policy entry is absent; keep the exact command and resource list in the job receipt. A network transition must not duplicate a mutation, so every run needs an idempotency key and a durable terminal state.
- **missing:** A condition-triggered routine primitive (power/network/meeting predicates, debounce, and expiry) rather than time-only routines; Read-only Mac power/Wi‑Fi state exposed to the coordinator with stable snapshots; A durable lease so only one Mac worker starts an eligible job; Pendant notification that distinguishes started, deferred, completed, and expired

### "“Give me a private change report: what I changed or completed since yesterday, what is still open, and show me the exact files, messages, and browser work you used.”"
- **useful because:** Today the system can execute actions and report individual jobs, but the owner cannot reconstruct a trustworthy day-level narrative across surfaces. A signed, source-linked change report would turn scattered Mac receipts, browser outcomes, mail/calendar, and pendant bookmarks into an auditable answer without requiring him to remember where work happened.
- **path:** relay → mac-planner → browser-extension → pendant → dashboard
- **model tier:** Cheap background summarizer over structured events; use realtime only if the owner asks follow-up questions while wearing the pendant. The model should never infer completion from prose when a receipt or source event is absent.
- **latency:** Generate in 5–15 seconds for a 24-hour window; stream an initial count in under 2 seconds and fetch details on demand. Retain raw event hashes, not full page bodies, unless the owner explicitly asks to inspect one.
- **cost:** About $0.005–$0.02 per report; event normalization and local file metadata dominate, with summarization on a small structured projection.
- **security:** This is a high-sensitivity cross-source view. Default to redacted subjects/paths and require an explicit expansion for message bodies, authenticated URLs, or file contents. Treat browser claims as provisional until a command result exists; clearly label inferred versus receipt-backed completion. Allow deletion of the report projection without deleting source records.
- **missing:** A Mac activity journal for file create/move/delete and app actions that includes timestamps, resource hashes, and job IDs; A browser event ledger for navigation, form submission, and result status without storing secrets; A cross-surface event schema linking pendant bookmarks and voice jobs to Mac/browser receipts; A read-only report endpoint with time range, source filters, redaction level, and provenance links

### "“Try both approaches and show me the difference; don’t change my real files or submit anything until I choose.”"
- **useful because:** The owner can explore consequential work without trusting the first plan: for example, compare two document structures, two travel/cart options, or two browser workflows while the Mac and authenticated browser remain private. The system would return concrete diffs and a recommendation, then apply only the selected branch. This is a capability neither the pendant, Mac, browser, nor relay can provide alone today.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** A cheaper background planner creates and evaluates branches; realtime is used only for the spoken request and the short choice conversation. Vision/browser work runs only where page state requires it.
- **latency:** Acknowledge in under 1 s, create isolated branches in under 5 s, and stream each branch's progress. Small comparisons should complete in 30–60 s; long branches become resumable jobs with an expiry.
- **cost:** Approximately $0.02–$0.10 per comparison, dominated by duplicated browser/Mac execution and vision calls; structured diffing should remain local and cheap.
- **security:** Branches must be isolated from the real filesystem, authenticated browser session, clipboard, network submissions, and notifications. Default all external side effects to mocked or staged operations. Redact secrets in branch logs, cryptographically bind the displayed diff to the exact branch artifacts, expire abandoned branches, and require an explicit spoken or dashboard selection before merge.
- **missing:** A branch/sandbox primitive for Mac files and browser sessions with copy-on-write snapshots; A side-effect simulator or submission firewall that can prove a branch did not send, purchase, delete, or publish; A normalized artifact-diff format covering files, UI state, form fields, and browser outcomes; A merge/apply operation that revalidates the chosen branch against changed live state and reports conflicts; Pendant and dashboard controls for comparing branches and selecting exactly one

### "“Before I send or publish this, check the text, attachments, recipient, and destination for secrets, wrong-person mistakes, and accidental disclosure; tell me what you found without changing anything.”"
- **useful because:** A wearable can catch the last-second mistake when the owner is moving quickly, while the browser and Mac can inspect the actual draft, attachment, recipient, and destination that the relay cannot reach. It is more useful than generic content moderation because it checks the concrete send boundary and explains the evidence before submission.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision
- **model tier:** Background model for deterministic secret/entity checks and attachment inspection; realtime only for the owner’s spoken request and concise findings. Escalate ambiguous recipient or policy matches to the stronger model, never silently approve them.
- **latency:** Return a first risk list in 2 seconds for text-only drafts and 5–15 seconds with attachments or a rendered page. Never hold a browser form open indefinitely; expire the inspection after the draft or recipient changes.
- **cost:** About $0.005–$0.04 per check, mostly local hashing/OCR and occasional vision; send-time checks should not need the expensive realtime tier.
- **security:** The auditor itself sees highly sensitive drafts and attachments. Keep content on the Mac/browser where possible, send only redacted findings upstream, hash rather than retain files, and bind the result to recipient, destination, and draft hashes. A positive result must not auto-send; an owner confirmation must be required and invalidated on any edit.
- **missing:** A read-only draft/attachment inspection primitive for Mail, browser forms, and local files; A destination/recipient identity resolver that handles aliases and authenticated account context; A configurable secret and disclosure policy with owner-defined entities and allowed destinations; A hash-bound send gate that can invalidate stale approval and report the exact checked payload

### "“Package everything I need to hand this project to someone else: the relevant files, links, decisions, and next actions, with secrets removed and a manifest of what you omitted.”"
- **useful because:** The owner could hand off work in minutes instead of hunting through Finder, private browser tabs, mail, and spoken notes. The result is a reviewable folder/archive with provenance and explicit omissions, so it is useful even when the recipient is outside this system.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Background model assembles and summarizes the packet from structured sources; use the stronger model only for resolving ambiguous relevance or writing the final executive summary. Realtime is unnecessary except for the request and completion notice.
- **latency:** Produce a manifest and preview in 10 seconds, then build the packet in under 2 minutes for a normal project. The owner can inspect or cancel while large files are being staged.
- **cost:** Approximately $0.01–$0.08, dominated by local file scanning, attachment extraction, and optional browser rendering; summarization is a small portion.
- **security:** This operation crosses the highest-risk boundary: private mail, authenticated pages, and local files become a portable artifact. Default to a redacted preview, exclude credentials/cookies/tokens and unrelated personal data, show every included source and omission, write atomically to a dedicated folder, and require explicit confirmation before opening or sharing it. Keep the original sources untouched.
- **missing:** A relevance-linked project export planner spanning files, Mail/Calendar, browser sessions, and pendant bookmarks; A deterministic secret/PII scrubber for filenames, document text, images, and links; A provenance manifest with source hashes, timestamps, redaction reasons, and omitted-item counts; An atomic export/share boundary with expiry and deletion controls


## What it asked for

_Nothing._
## Its own summary

Discovered the live route/tool/device inventory and produced three new cross-surface capabilities. The highest-value is “Finish this for me”: one pendant utterance grounded in Mac/browser state, preflighted, executed, and returned with a receipt. The other two are condition-triggered Mac work (wait for Wi‑Fi, power, and meeting-free state) and an evidence-backed cross-surface change report. All three explicitly account for privacy, idempotency, and the currently empty FULL_CONTROL policy seam.

**Biggest unknown:** The coordinator still lacks a proven event envelope joining pendant intent/bookmarks, browser results, Mac receipts, and durable job state. I still need that orchestration layer, condition-triggered routine support, and provenance/event ledgers; the owner must also explicitly configure which Mac/browser action classes may run unattended. Current Safari and Mac bridge are online, but LTE pendant registration remains unavailable.

