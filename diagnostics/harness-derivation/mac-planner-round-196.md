# Harness derivation — mac-planner — round 196

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-accessibility-live** — The live Mac agent now has Accessibility and Screen Recording trusted for AI Pendant Agent, synthesized input verified, secure input false, and UI actions expected to reach the screen. This overturns the older blocked assumption; the current foreground app is Claude and browser sessions include X plus two stale probe tabs.
  - evidence: mac_readonly_inspect(operation=running_apps) resolved to GET /observe at 2026-08-08T02:42:37.986Z and returned accessibility.trusted=true, eventsPost=true, screenRecording=true, inputReachability.status=verified.

## Capabilities it proposed

### "After you do something on my Mac for me, tell me exactly what changed and let me say "undo that" when it is genuinely reversible. If it cannot be safely undone, say so instead of pretending."
- **useful because:** FULL_CONTROL_MODE currently executes actions without a gate and many actions are permanent. A spoken, resource-specific result and undo path would make automation trustworthy while preserving the owner's chosen maximum access. It is useful precisely when the owner is away from the screen.
- **path:** relay-realtime → mac-planner → mac-vision → browser → pendant → dashboard
- **model tier:** Realtime for the short receipt and voice disambiguation; deterministic local code for inverse actions; background model only for grouping several receipts.
- **latency:** Receipt within 1 second of action completion; undo dispatch within 2 seconds after a clear voice command; no model call for known inverse operations.
- **cost:** Very low per action: structured receipt plus optional one realtime turn. Storage is a bounded local/relay ledger; cost is dominated by spoken response generation.
- **security:** Never claim undoability without an inverse and verified post-state. Do not retain page contents or keystrokes in receipts; hash/redact sensitive paths and URLs. Deletes, sends, purchases, and arbitrary shell commands remain explicitly non-undoable and should be reported as such.
- **missing:** A typed inverse catalog and pre/post state capture for mac_run_actions and browser actions; A receipt join between POST /execute, GET /jobs/:jobId/receipts, and browser command results; A pendant voice command resolver for selecting one of several recent reversible actions

### "While I am on a call, quietly watch the browser page and Mac work I asked you to monitor. If something materially changes, put one evidence-backed update in my pendant inbox; do not interrupt me, and let me ask for the source or open it afterward."
- **useful because:** Polling authenticated browser sessions and desktop jobs is valuable but unsolicited speech during a call is disruptive. This creates a bounded, evidence-backed change feed: the relay detects deltas, the Mac/browser retain the source, and the pendant surfaces only a short alert when the owner chooses.
- **path:** browser → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Cheap background model for deduplication and materiality ranking; realtime only when the owner requests a spoken explanation.
- **latency:** Poll on the watch's configured cadence; inbox insertion under 5 seconds after a confirmed delta; playback only on an owner button press or explicit voice request.
- **cost:** Low to moderate: browser polling and compact DOM/hash diffs dominate; model cost is limited to changed snippets and can be avoided for simple field changes.
- **security:** Authenticated page content leaves the browser only as minimal redacted diffs. Watches need per-site scope, expiry, pause, and an audit trail. Never auto-submit or purchase; opening a source is an explicit action.
- **missing:** A material-change detector that compares browser and Mac evidence without uploading whole pages; A unified watch-to-pendant inbox record with source citation and expiry; A call-state/quiet policy signal shared by relay and pendant

### "Turn what we just discussed into a handoff pack on my Mac: a concise brief, decisions, open questions, source links, and next actions in separate files, then open the folder so I can send it to someone."
- **useful because:** The owner often needs a usable artifact, not a spoken recap. This joins relay conversation context with authenticated browser evidence and bounded Calendar/Mail reads, then atomically stages a coherent folder on the Mac instead of scattering edits across apps.
- **path:** relay-realtime → mac-planner → browser → mac_read_sources → mac_workbench_transaction → pendant → dashboard
- **model tier:** Background/cheap model drafts and extracts structure; realtime only for a spoken completion confirmation or clarification. Deterministic transaction code writes the final files.
- **latency:** Under 10 seconds for a short conversation and already-captured sources; longer research is asynchronous with a job receipt. Never open or send externally without an explicit owner command.
- **cost:** Low to moderate: one background summarization call plus small source snippets; Mac workbench dominates no API cost. Limit source text and use hashes/URLs where possible.
- **security:** Default to local-only files and redact mail bodies, tokens, and personal data. Include provenance and generation time in each file. Opening is safe; sending, uploading, or sharing the folder requires a separate explicit action. Atomic staging prevents half-written handoffs.
- **missing:** A relay API that exposes the current conversation's structured decisions and citations to the Mac planner; A source-bounded pack template with redaction and provenance fields; A receipt that links the generated pack, source versions, and any later send action

### "Make this safe to share. From whatever document, browser page, or app I am looking at, produce a redacted copy that preserves the useful facts, show me exactly what was removed, and leave the original untouched until I explicitly send the cleaned version."
- **useful because:** People routinely need to share a screen or document while accidentally exposing tokens, private mail, customer data, or unrelated tabs. The pendant provides an immediate command, the Mac can inspect and duplicate the actual artifact, and the browser can resolve the authenticated source; the owner gets a shareable result without manually hunting for secrets.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser → dashboard
- **model tier:** A background model performs bounded redaction and classification; realtime only handles the owner's short command and reports the result. Deterministic file duplication, diffing, and send/open actions remain local.
- **latency:** Under 8 seconds for a text document or page under 100 KB; larger artifacts become an asynchronous job with a pendant receipt. Never send automatically.
- **cost:** Moderate: redaction inference over extracted text is the dominant API cost; local hashing, copying, and diff generation are cheap. Screenshots/PDFs require OCR or an on-device parser to avoid uploading raw pixels.
- **security:** Raw content must stay on the Mac/browser unless the owner explicitly opts into cloud redaction. Use layered deterministic detectors for credentials, personal data, and hidden metadata, then model-assisted review. Preserve an encrypted local original, disclose every removal, and require explicit confirmation for any outbound share.
- **missing:** A Mac/browser artifact extraction and redaction service that can handle the foreground document, web DOM, PDF, image, and metadata without relying on cursor-driven scraping; A verifiable redaction report with before/after hashes and a machine-readable removal list; An owner-configurable local-vs-cloud privacy policy and a typed send/share action with a final preview


## What it asked for

_Nothing._
## Its own summary

Three new owner-facing capabilities were recorded: (1) spoken, evidence-backed receipts with a truthful “undo that” path for reversible Mac/browser actions; (2) quiet, source-cited material-change alerts from browser watches and Mac jobs, delivered through the pendant inbox without interrupting calls; and (3) a conversation-to-handoff-pack workflow that atomically creates a brief, decisions, open questions, links, and next actions on the Mac. I also verified and recorded that Accessibility, Screen Recording, and synthesized input are now live for AI Pendant Agent. My first bookmark-context proposal was correctly rejected as an existing capability, so I did not count or rephrase it.

**Biggest unknown:** The missing semantic join is still the key blocker: a durable correlation between a pendant bookmark or relay event and a redacted Mac/browser document context, plus a typed selected-text/document-identity snapshot. Existing host observation reports apps and tabs, but not enough semantic UI context to safely cite or reopen the exact work item. I still need that capability (or an explicit route/schema for it), and a relay endpoint exposing structured conversation decisions/citations for handoff packs.

