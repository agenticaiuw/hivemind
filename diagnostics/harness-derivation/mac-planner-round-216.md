# Harness derivation — mac-planner — round 216

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-accessibility-live** — AI Pendant Agent currently has Accessibility and Screen Recording trusted; synthesized input is verified reaching the screen, and Safari is foreground with three durable browser sessions. This changes the earlier blocked assumption for UI-based context capture.
  - evidence: mac_readonly_inspect(operation=running_apps) invoked GET /observe at 2026-08-08T04:53:30Z; response accessibility.trusted=true, screenRecording=true, eventsPost=true, inputReachability=verified.

## Capabilities it proposed

### "If my pendant audio path or modem test fails, diagnose it end to end and leave me a concise repair report with the exact evidence and next fix—without me opening a terminal."
- **useful because:** The owner currently has to correlate UART counters, fixture results, Mac USB state, and relay jobs by hand. This turns a silent wearable failure into an actionable report and a spoken alert, using the hardware that is physically attached today.
- **path:** pendant → mac-planner → relay-realtime → dashboard
- **model tier:** Background model for log normalization and report drafting; realtime only for the one-sentence spoken alert.
- **latency:** Run automatically on USB attach or a failed diagnostic, under 30 seconds for evidence collection and under 2 minutes for the report.
- **cost:** Usually <$0.01 per incident; most cost is a small background summarization call, not realtime audio.
- **security:** UART logs can contain identifiers and network metadata; redact device IDs before relay upload and keep raw logs in ~/AI-Pendant-Workspace. Never upload microphone PCM—the fixture is synthetic. Creating a patch or filing externally must require explicit confirmation.
- **missing:** A bounded Mac USB/UART diagnostic trigger-and-read capability (the current granted serial diagnostic is read-only and no typed serial route exists).; A relay incident schema that correlates fixture sequence numbers, Mac attachment state, and audio pipeline receipts into one report.; A local policy entry authorizing automatic report creation while keeping external filing and code changes confirm-gated.

### "When a browser action is ready to send, buy, publish, or delete, read me a one-sentence summary on the pendant and let my physical button be the approval that authorizes exactly that action once."
- **useful because:** The owner can read and click in the browser, but a browser session should not be able to turn an accidental click into an irreversible action. A physical press proves the owner is present without requiring them to find a confirmation dialog, while preserving unattended low-risk browsing.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** Realtime only to speak the compact action summary; deterministic policy and token matching handle authorization.
- **latency:** Summary within 2 seconds of staging; button approval should reach the browser in under 1 second and expire after 30 seconds.
- **cost:** A few cents per unusual high-impact action at most; routine reads use no model call.
- **security:** The approval token must be single-use, bound to a command hash, browser origin, account/session, and expiry. The relay must not accept a generic 'approve latest' token. The pendant should show an unmistakable LED state, and sending mail, deleting files, and buying remain explicit classes. Do not speak secrets or full payment details.
- **missing:** A relay-issued, single-use approval-token endpoint and browser result binding; existing browser_enqueue_command/result routes do not provide this physical-presence handshake.; Firmware integration that maps the existing moment/bookmark button edge to approval mode without confusing ordinary bookmarks.; An owner-configurable policy table naming which browser and Mac actions require this approval; the current FULL_CONTROL path has no active policy gate.

### "Save the useful claim from the page I am reading into my workspace as a cited note and a short audio card, with the source URL and a clear 'why this matters' sentence."
- **useful because:** The owner repeatedly asks to inspect pages but has no durable bridge from an authenticated browser session to the Mac workspace and pendant inbox. This converts transient browsing into a retrievable, listenable artifact without copying an entire page or exposing the session.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** Background model extracts and compresses the claim; realtime is used only if the owner asks for an immediate spoken confirmation.
- **latency:** Acknowledge immediately; create the note and audio card within 20 seconds.
- **cost:** <$0.02 per clip, dominated by extraction and speech synthesis; no cost for storing URL and selected text.
- **security:** Never send passwords, cookies, full page bodies, or hidden authenticated content by default. Require the browser extension to provide only the owner-selected text plus origin and title, redact query strings, and preserve the original URL locally. Do not auto-share or send the note.
- **missing:** A browser command for owner-selected text extraction with origin/title and explicit redaction metadata (current inspect is page-level, not a selection clip).; A relay artifact route that atomically stores note text, citation, and generated audio as one inbox item.; A Mac workspace writer that can append a cited markdown note and receipt without using arbitrary shell.

### "Find everything I already have open or drafted about a topic, deduplicate it, and leave me a short index showing each browser tab, local file, and the next action—without closing or changing anything."
- **useful because:** Work is split between authenticated browser sessions and ~/AI-Pendant-Workspace. A read-only cross-surface index gives the owner one map of an interrupted project instead of forcing them to search tabs and files separately.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background model for deduplication and next-action extraction; no realtime model unless the owner asks to hear the index.
- **latency:** Under 30 seconds for up to 20 tabs and 50 workspace files; return a spoken one-sentence completion notice.
- **cost:** <$0.02 per index, mostly background summarization; inspection and file listing are local.
- **security:** Keep authenticated page bodies local to the browser bridge; send only redacted titles, origins, snippets, and file names to the summarizer. Never modify or close tabs. File contents require explicit scope; default to names and headings.
- **missing:** A bounded cross-surface search primitive that joins browser tabs and workspace files by topic without exporting whole authenticated pages.; A structured index artifact format with stable references to tabs/files and freshness timestamps.; A relay query/notification route to deliver the finished index to the pendant inbox.

### "When I ask what happened, show me a trustworthy timeline linking my spoken request to every browser/Mac action, resulting file, and receipt— including which step failed and what data was sent."
- **useful because:** Today receipts, browser commands, Mac actions, and pendant conversations are separate records. The owner cannot audit an outcome without reconstructing it by hand. A human-readable provenance timeline would make the hive explainable after an unexpected change, failed job, or privacy concern.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → dashboard
- **model tier:** Background model converts structured events into a concise explanation; deterministic IDs, hashes, and timestamps provide the evidence. Realtime is only for speaking the final summary.
- **latency:** Timeline query under 3 seconds; ingestion is asynchronous and must not delay actions.
- **cost:** <$0.01 per query; event correlation is storage/indexing work, not model work.
- **security:** Separate sensitive payloads from metadata; redact secrets and authenticated page bodies. Bind each event to a request/session and preserve hashes rather than copying content. The owner must be able to delete the content while retaining or deleting the audit metadata independently.
- **missing:** A hive-wide provenance envelope with request_id, surface, action hash, input/output references, and data-egress classification.; A query endpoint that joins relay jobs, browser commands, Mac receipts, and pendant delivery acknowledgements into a causal graph.; A dashboard/pendant presentation that distinguishes observed evidence from model-generated explanation.

### "Before carrying out a multi-surface task, give me a faithful rehearsal of the exact browser clicks, Mac file changes, messages, and costs; then let me run that unchanged plan later without the system silently replanning it."
- **useful because:** A Mac dry-run cannot currently predict browser side effects or prove that execution matches the preview. This would let the owner understand a consequential workflow once, preserve the approved plan, and detect drift in tabs, files, or account state before execution.
- **path:** relay-realtime → browser-extension → mac-planner → pendant → dashboard
- **model tier:** Deterministic planners and preflight classifiers do the rehearsal; a slower model may explain it in plain language. Realtime is not needed except for a spoken summary.
- **latency:** Preview in under 5 seconds for ordinary tasks; execution should start immediately when requested, with a plan hash check.
- **cost:** <$0.02 per preview, mostly model planning for ambiguous tasks; deterministic actions and hash checks dominate reliability, not spend.
- **security:** Preview must label estimates versus guaranteed effects and never claim a send/delete/purchase is reversible. Bind execution to an immutable plan hash, target origin, file paths, and expiry. If anything changes, return a new preview rather than silently adapting. This is an observability/consistency feature, not an invented approval policy.
- **missing:** Browser-side deterministic preflight that reports touched forms, navigation, downloads, and submission effects without submitting.; A cross-surface immutable plan manifest and executor that rejects drift between preview and execution.; A pendant-readable compact preview format for plans too large for one spoken sentence.

### "Before using a logged-in browser or sending anything from my Mac, tell me which account, workspace, and identity the action will use, and stop if it does not match the identity I named."
- **useful because:** Authenticated browser sessions and local accounts are powerful but opaque. A wrong tab, profile, or workspace can publish to the wrong organization even when every click technically succeeds. Identity attestation catches that class of mistake before the action, rather than after it appears in a receipt.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Deterministic account/profile discovery and origin matching; a small background model only explains ambiguous identity labels. Realtime can speak the compact identity before an action.
- **latency:** Identity result within 1 second for a staged action; cached attestations refresh on tab/profile change or every 5 minutes.
- **cost:** Near-zero for deterministic checks; <$0.005 when disambiguation needs a model.
- **security:** Never infer identity from page text alone. Use browser profile/session IDs, origin, selected account metadata, and Mac account/workspace identity; redact email addresses in logs unless needed. A mismatch should be explicit and recoverable, not silently switched. The owner chooses identity aliases and policy.
- **missing:** Browser bridge support for profile/account attestation and origin-bound session identity, not just URL/title inspection.; Mac identity/workspace attestation for Mail, Calendar, editor, and filesystem operations.; A shared identity declaration in the plan manifest, plus a relay route that reports mismatches to the pendant without leaking account details.


## What it asked for

_Nothing._
## Its own summary

Round 216 produced three new recorded capabilities: (1) physical pendant single-use approval for high-impact browser/Mac actions, bound to an exact command hash; (2) cited browser-claim clipping into a workspace note plus short audio card; (3) a read-only cross-surface project index joining open browser tabs and local drafts. A fourth UART incident-report idea was judged too close to an existing diagnostic-failure proposal and was not repeated. Live inspection also established that AI Pendant Agent now has Accessibility and Screen Recording, with synthesized input verified; Safari is foreground and three browser sessions are present.

**Biggest unknown:** The main remaining gaps are implementation contracts, not Mac permission: a typed physical-approval token route, browser selected-text extraction with redaction, a relay artifact/index schema, and a bounded USB/UART trigger/read path. mac_readonly_inspect(browser_tabs) is currently ambiguous between browser_inspect and browser_list_tabs, so browser-state capabilities need that resolver tie broken before they can be reliable.

