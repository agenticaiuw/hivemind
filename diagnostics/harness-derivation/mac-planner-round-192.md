# Harness derivation — mac-planner — round 192

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-accessibility-state** — The live Mac agent currently reports Accessibility trusted, Screen Recording true, synthesized input events posting successfully, secure input false, and UI actions will reach the screen. AI Pendant Agent is foreground-capable even though Claude is the foreground app. This is a changed live fact relative to the earlier denied/grant context.
  - evidence: mac_readonly_inspect operation running_apps resolved to GET /observe at 2026-08-08T02:29:04.962Z and returned accessibility.trusted=true, screenRecording=true, eventsPost=true, inputReachability.status=verified.

## Capabilities it proposed

### "When I say “finish this across my computer,” carry out the spoken task in the right authenticated browser tab and Mac app, then tell me exactly what changed and show me a proof receipt; if one critical detail is missing, ask only for that detail."
- **useful because:** Today the system can plan Mac actions and browser commands, but the owner has to trust that a multi-surface task actually finished. A single spoken request should become a coordinated browser+desktop transaction with a concise, auditable result instead of silent partial completion.
- **path:** pendant → relay → browser → mac-bridge → dashboard
- **model tier:** Use realtime only to capture intent and ask a single clarification; use a cheaper background planner to decompose and verify the workflow. Browser and Mac harnesses execute, while relay persists the receipt and pendant speaks the result.
- **latency:** Initial acknowledgement under 1 second; execution 5–30 seconds depending on browser and app; final receipt immediately after both surfaces report completion.
- **cost:** One short realtime turn plus one background planning/verification call; roughly $0.01–$0.08 depending on task length. Browser/Mac I/O dominates latency, not tokens.
- **security:** Authenticated page contents and local filenames may leave the device to the relay unless redacted. The owner must configure which domains/apps may run unattended; destructive sends/deletes need an explicit policy entry. Every step, touched resource, before/after hash or URL/title, and failure is retained in the receipt.
- **missing:** A cross-surface transaction coordinator that can correlate browser command IDs and Mac action/job receipts, detect partial completion, and retry idempotently.; Browser result payloads with stable before/after evidence and an operation idempotency key.; Owner-configured action policy that is actually consulted by FULL_CONTROL_MODE.

### "Undo the last thing you did across my Mac and browser, and tell me what could not be safely reversed."
- **useful because:** Current receipts can say what happened, but a failed multi-surface task can leave half a document, a moved file, and a changed web form. A spoken cross-surface undo would turn the system from an irreversible automation hazard into something the owner can recover from without hunting through apps.
- **path:** pendant → relay → browser → mac-bridge → dashboard
- **model tier:** Use a deterministic inverse-action planner over the recorded receipt; invoke realtime only if the inverse is ambiguous or an external side effect (send/purchase/delete) cannot be reversed. No model is needed for ordinary file staging, draft edits, or navigation rollback.
- **latency:** Receipt lookup and reversals in under 5 seconds for local/browser-state changes; external irreversible effects are reported immediately rather than pretending success.
- **cost:** Usually no model call; one cheap classifier/inverse lookup. Cost is dominated by browser/Mac operations and retention of before-state metadata.
- **security:** Undo metadata can contain private page text, filenames, and form values, so encrypt and redact it. Never fabricate reversal: distinguish reverted, partially reverted, and irreversible. The owner must define whether browser history/navigation, drafts, file moves, and app edits are eligible; sent messages and purchases remain non-reversible.
- **missing:** A shared inverse-operation ledger joining browser command IDs, Mac job receipts, and workbench transaction receipts.; Browser-side compensating actions and before-state snapshots for supported form/document operations.; A bounded retention policy and dashboard showing exactly which inverse steps will run.

### "Research this for me, using both public sources and the sites I’m already signed into; save a cited decision memo on my Mac, and give me a 30-second spoken answer with the unresolved disagreements."
- **useful because:** Public web search alone misses the owner’s private dashboards and subscriptions, while browser automation alone does not produce a durable, cited artifact. This combines the relay’s research synthesis, authenticated browser sessions, and a local Mac memo so the owner gets both an answer now and something auditable later.
- **path:** pendant → relay → browser → mac-bridge → dashboard
- **model tier:** Use a cheaper background research model for retrieval, deduplication, and citation extraction; use realtime only to clarify the question or speak the final short answer. Keep private authenticated-page extraction scoped to the requested domains.
- **latency:** Acknowledge in under 1 second; return a spoken provisional answer in 20–60 seconds; finish the cited memo in under 3 minutes, with progress available on the dashboard.
- **cost:** One background retrieval/synthesis job plus optional realtime speech, roughly $0.03–$0.20 depending on source count. Browser fetches and page rendering dominate time.
- **security:** Private subscription pages and account-specific data must stay scoped to the job and be redacted before any broad model call. Never mix sources across owners or silently quote paywalled content. The memo should include URLs, access time, confidence, and claims that could not be verified; saving locally is a write and must follow the owner’s policy.
- **missing:** A research coordinator that can request bounded extracts from authenticated browser tabs and combine them with public web_search results.; A citation-preserving artifact writer that emits Markdown/PDF with source spans and hashes, not just a prose summary.; Browser command support for extracting structured text from the current authenticated page without exposing passwords or unrelated tabs.

### "Take whatever I’m currently looking at on my Mac or in the active browser tab, and send it where I say — for example, “send this article to my notes,” “turn this selected paragraph into a reminder,” or “share this file with Alex.”"
- **useful because:** The owner should not have to copy URLs, hunt for the selected text, or explain which window “this” means. The pendant supplies intent while the Mac establishes the exact foreground selection and the browser supplies authenticated context. This is a genuinely cross-node reference-resolution capability, not another generic automation macro.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use realtime only to resolve the spoken destination and ambiguity. A small deterministic resolver obtains the active app, window, selection, URL, and file identity; a cheaper planner performs the requested transformation and dispatch.
- **latency:** Resolve “this” in under 1 second and confirm the target before any external send; complete local note/reminder actions within 5 seconds, with browser sharing actions reported when the site responds.
- **cost:** Usually one short realtime turn and one cheap classification call, approximately $0.005–$0.04. Mac/browser inspection and destination APIs dominate latency.
- **security:** The active selection may contain secrets, credentials, or third-party personal data. Capture only the selected text or explicitly targeted file, redact passwords and secure-input fields, and show the exact source and destination in the spoken/dashboard receipt. Sending or sharing must be governed by an owner policy entry and must not silently broaden from selection to whole-page contents.
- **missing:** A resolved Mac inspection operation for selected_text, window_identity, and document_path with stable source identifiers.; A browser extraction command that returns the active tab’s selected text and canonical URL without scraping unrelated tabs.; A typed source-reference object passed through relay planning so “this” cannot drift between inspection and execution.; Destination adapters for Notes, Reminders, email drafts, and authenticated browser share forms.

### "For anything you tell me, let me ask “why?” and get the exact calendar event, email, browser page, or Mac file that caused the answer, including what was inferred versus directly observed."
- **useful because:** A spoken assistant becomes trustworthy when the owner can inspect the basis of an answer instead of accepting an opaque summary. This is especially valuable while walking: the pendant can speak a two-sentence provenance explanation, while the Mac dashboard opens the precise source and timestamp.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** No realtime model is needed to assemble provenance. Store structured source spans and inference labels during the original background job; use realtime only to summarize the trace aloud when asked.
- **latency:** Spoken “why?” response in under 2 seconds from the stored trace; opening the source on the Mac within 3 seconds.
- **cost:** Negligible incremental model cost if provenance is captured during the original request. Storage and bounded source-span retention dominate.
- **security:** Provenance can expose private mail, page contents, filenames, and other people’s data. Store redacted spans and source identifiers, enforce per-source retention, and refuse to read a source aloud when the owner’s privacy latch or secure-input state prohibits it.
- **missing:** A provenance envelope required on every briefing, research, plan, and spoken response.; Stable source-span identifiers for Calendar/Mail, browser tabs, and local files that survive refreshes and edits.; A relay query that can retrieve and redact the trace for a pendant-sized spoken explanation.; Dashboard UI that highlights observed facts, inferred claims, and stale sources separately.

### "Show me everything you sent or changed on my behalf today, grouped by recipient and app, with the exact final text or file and whether it was actually delivered."
- **useful because:** The owner currently has to search Mail, browser history, reminders, and local files separately to know what the assistant did. A single outbound ledger makes delegated work accountable and catches a mistaken or duplicated send before it becomes a surprise.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic event aggregation and hashes; no expensive model is required. Use realtime only to answer a spoken filter such as “only messages to work” or “what changed after lunch.”
- **latency:** Answer common queries from the ledger in under 2 seconds; source inspection or delivery verification may take up to 10 seconds.
- **cost:** Near-zero model cost; bounded encrypted event storage and occasional browser/Mac verification are the main costs.
- **security:** Outbound text, recipients, filenames, and destinations are highly sensitive. Encrypt the ledger locally, redact bodies by default on the pendant, support per-app retention, and clearly distinguish drafted, queued, submitted, and confirmed-delivered states. Never infer delivery merely from a click receipt.
- **missing:** A normalized outbound-event schema spanning Mac actions, browser commands, reminders, notes, and relay messages.; Delivery-state callbacks from Mail and authenticated browser forms rather than only UI action success.; A retention/redaction policy and dashboard filters by time, recipient, app, and confidence.; A compact pendant query/summary path for voice-only audit questions.


## What it asked for

_Nothing._
