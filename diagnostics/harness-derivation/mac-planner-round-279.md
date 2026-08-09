# Harness derivation — mac-planner — round 279

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“When I press the bookmark button before I walk away, save my work exactly where it is and leave me a short spoken handoff for later.”"
- **useful because:** The pendant becomes a physical ‘I am leaving this context’ signal. The Mac captures open work before a laptop sleep, crash, or location change; the owner can later ask the relay what was left unfinished without reconstructing tabs and documents from memory. This is a true pendant–Mac–relay workflow, not another desktop save shortcut.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Use the realtime model only to acknowledge the button and answer a later handoff question; use a cheaper background model to summarize staged metadata. The Mac performs deterministic capture and atomic staging.
- **latency:** Button acknowledgement under 500 ms; capture and staging within 10 s; spoken handoff available after the transaction receipt arrives.
- **cost:** About $0.01–$0.04 per handoff for a small background summary; Mac and storage dominate, not model tokens.
- **security:** Document names, app names, browser URLs, and possibly unsaved text leave the Mac only if the owner enables content capture. Default to metadata and hashes, redact query strings, and never upload document bodies without an explicit policy setting. Do not close apps or overwrite files automatically.
- **missing:** A real USB/device-edge event or relay event that tells the Mac the bookmark happened while the pendant is attached (today’s button behavior is firmware-local and LTE is unregistered).; Per-application unsaved-document identity and safe read APIs; current host observation reports apps and tabs but not dirty buffers.; A durable handoff record/query route on the relay; workbench contexts can stage artifacts but are not yet a user-facing spoken handoff store.

### "“Turn this authenticated web page into a trustworthy brief I can keep: quote the relevant facts, show where each came from, and save it locally without sending anything or changing the site.”"
- **useful because:** Authenticated browser sessions contain information the relay cannot reach, while the Mac can create a durable local artifact. This gives the owner a citation-preserving answer instead of an uncited spoken paraphrase, useful for invoices, policies, travel pages, and research that must be checked later.
- **path:** browser-extension → mac-planner → relay → dashboard
- **model tier:** Use a cheaper background model for extraction, deduplication, and citation formatting; invoke realtime only when the owner asks a spoken follow-up. Browser and Mac operations remain deterministic.
- **latency:** Snapshot in 2 s, extraction in 10–30 s depending on page size, then open the resulting Markdown/PDF locally.
- **cost:** Roughly $0.02–$0.10 per page depending on extracted text length; browser transfer and local file writing dominate latency.
- **security:** Page contents may contain credentials, health, financial, or private work data. Never transmit passwords, form values, cookies, or hidden DOM fields. Show the URL, timestamp, selected excerpts, and a redaction report; default to local-only output. No submit/click mutation is permitted in this mode.
- **missing:** A browser bridge operation that returns the accessibility tree or reader text with stable element/source offsets, not only the current tab identity.; A provenance format and local verifier that binds each quote to URL, timestamp, and content hash.; An owner-configurable classification policy for which authenticated domains may be summarized unattended.

### "“After you do that on my Mac, prove what changed and tell me if it actually worked—not just that the command ran.”"
- **useful because:** Today a plan can execute while the owner is away, yet a successful transport receipt is not proof that the file, app, browser, or shortcut reached its intended state. A postcondition verifier would catch partial writes, wrong-window actions, stale browser tabs, and app failures, then give the pendant a concise truthful result with a retry or recovery path.
- **path:** relay → mac-planner → mac-vision → pendant → dashboard
- **model tier:** Use deterministic checks first (file hashes, app/window presence, browser URL/title, shortcut result). Use the inexpensive vision model only when a visual postcondition is unavoidable; reserve realtime for spoken explanation.
- **latency:** Add 1–3 s for deterministic verification and up to 8 s for a visual check. Never claim success before the check or timeout is explicit.
- **cost:** Usually <$0.01 because most checks are local; occasional vision verification costs about $0.01–$0.05. The main cost is one extra observe round trip.
- **security:** Verification can expose filenames, URLs, and screen content to the relay. Return structured pass/fail plus minimal redacted evidence by default; retain full screenshots only when the owner requests debugging. Verification must not silently retry destructive actions.
- **missing:** A typed postcondition schema attached to each planned action (expected app, URL, file hash, shortcut result, or UI state).; A read-only semantic UI/document inspector that can identify the target control or resulting state; current ui_snapshot is available but not a stable semantic contract.; A receipt join key shared by POST /execute, observation, and the job ledger so a later answer can distinguish a verified success from an attempted action.

### "“Answer questions using my Mac, mail, calendar, files, and logged-in browser sessions, but keep the source material on the Mac—send only the minimum answer and proof back to the pendant.”"
- **useful because:** This would make the hive genuinely private and useful across surfaces: the owner could ask whether a commitment conflicts with a work portal deadline, which document supports a claim, or what needs attention without uploading an entire inbox, file, or authenticated page to the relay. Today each source is isolated and any cross-source reasoning either cannot reach the source or would require exporting raw content.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Run retrieval, filtering, and most reasoning locally with a cheaper background model. Use realtime only for the short spoken exchange. The relay should receive a compact answer, confidence, citations, and a provenance hash—not source text.
- **latency:** 2–5 seconds for calendar/mail/files; 10–30 seconds when an authenticated browser page must be read. The pendant should acknowledge immediately and speak only after the local evidence package is ready.
- **cost:** Typically $0.01–$0.08 per query, dominated by local extraction and any browser-page summarization; raw-data transfer costs should be near zero.
- **security:** The Mac must enforce source-specific redaction and domain policy locally. Browser cookies, passwords, hidden form fields, mail bodies, and unrelated files must never enter the relay request. The owner needs an inspectable evidence manifest showing exactly which sources, snippets, hashes, and timestamps influenced the answer. A query that cannot satisfy those rules should return “I can’t safely answer,” not fall back to broad export.
- **missing:** A local federated query broker that can combine mac_read_sources, filesystem metadata/content, and browser-session page text without passing raw source material through the relay.; A browser reader that returns bounded visible text plus stable citations while excluding credentials and hidden fields.; A signed, compact evidence-envelope protocol carrying answer, confidence, source identifiers, timestamps, and hashes.; A policy store the owner can configure per app, folder, mail account, and authenticated domain.

### "“When I make a promise out loud, remember it, watch for evidence that I completed it, and remind me only when it is genuinely at risk of being missed.”"
- **useful because:** The owner currently has to convert spoken commitments into reminders manually and cannot connect them to evidence spread across mail, calendar, files, and authenticated sites. This would turn a pendant moment into a private, time-bounded commitment with completion evidence and escalation—not another generic notification queue.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use a background model to extract the commitment, due date, and acceptable evidence. Use realtime only for immediate clarification or a short reminder. Deterministic watchers should handle calendar/mail/file/browser changes.
- **latency:** Capture acknowledgement under 1 second; commitment extraction within 15 seconds; evidence checks on schedule or on source changes; reminder delivery within 30 seconds of a risk threshold.
- **cost:** About $0.01–$0.06 per commitment plus inexpensive scheduled source checks. Browser and mail polling dominate operational cost.
- **security:** Commitments may contain sensitive people, projects, and deadlines. Store the smallest structured record, not the original audio by default; keep source excerpts local, redact unrelated correspondence, and require explicit opt-in for authenticated-domain monitoring. Never infer completion from a weak signal without showing the evidence.
- **missing:** A commitment ledger with due dates, evidence rules, expiry, and owner-controlled escalation policy.; A source-change watcher that can inspect only the relevant mail threads, calendar entries, files, and authenticated pages.; A local evidence matcher that can distinguish a real completion signal from a merely related mention.; A safe way to ask one clarifying question when the spoken promise lacks a due date or completion criterion.

### "“For anything you create or change for me, let me ask later why it exists, what I intended, and what sources or actions led to it.”"
- **useful because:** Files, notes, reminders, browser drafts, and shortcuts otherwise become unexplained residue. A cross-node intent lineage would let the owner recover the reasoning behind an artifact months later, distinguish their own work from automation, and safely continue or undo a half-finished task. This is more useful than a raw action log because it connects spoken intent, evidence, mutations, and outcome.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Record deterministic action and source identifiers locally; use a background model to compress them into a short causal explanation. Use realtime only when the owner asks “why is this here?” or “what was unfinished?”
- **latency:** Attach lineage metadata during each operation with negligible interactive delay; generate a human explanation in under 5 seconds.
- **cost:** About $0.005–$0.03 per artifact explanation. Storage and indexing dominate; source bodies need not be duplicated.
- **security:** Lineage can reveal sensitive intent even when the resulting file is innocuous. Encrypt the ledger locally, redact source excerpts by default, support per-folder/domain retention, and distinguish observed facts from model-generated explanations. Never claim an intent that was not recorded.
- **missing:** A durable, content-addressed intent-lineage store shared by relay jobs, Mac actions, browser commands, and pendant bookmarks.; A correlation identifier propagated from spoken request through plan, action, receipt, and resulting file/page/task.; Artifact watchers that can attach later edits or external completion evidence without claiming authorship for the owner.; A dashboard and pendant query path for inspecting, correcting, or deleting lineage records.


## What it asked for

_Nothing._
