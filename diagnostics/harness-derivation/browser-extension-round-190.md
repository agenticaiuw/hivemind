# Harness derivation — browser-extension — round 190

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-live-state** — Safari extension is online with 2 tabs; active tab is YouTube at https://www.youtube.com, tabId 1419527, and there are no pending commands.
  - evidence: GET /browser/status returned online=true, tabCount=2, tabId=1419527, tabUrl=https://www.youtube.com, pendingCommands=0 at round 190.

## Capabilities it proposed

### "“Tell me what on my authenticated tabs changed since I last looked, rank it by consequence, and let me open the one I choose.”"
- **useful because:** This turns scattered logged-in web sessions into one actionable inbox: the owner hears only meaningful changes and can drill into the exact authenticated page without manually hunting through tabs. Unlike public search, it uses Safari's existing sessions; unlike a static daily briefing, it is event-driven and can cover any origins the owner configures.
- **path:** browser-extension → relay-realtime → mac-planner → relay-realtime
- **model tier:** Background model performs scheduled/local DOM diffs and ranking; realtime is used only for the owner's spoken query and the final short response.
- **latency:** Change detection can run every 15–60 minutes in the background; spoken query should answer in under 3 seconds, with page navigation/extraction streamed within 10 seconds.
- **cost:** Low per check if DOM hashing and extraction are local; roughly one background summarization call per changed page, with realtime tokens only for the final interaction. Cost is dominated by changed-page summarization, not polling.
- **security:** Ship an empty per-origin configuration and retention policy; never assume which sites or categories are safe. Keep raw page text in Safari/local agent only, send redacted diffs and provenance, encrypt stored fingerprints, and expose an inspectable deletion control. Opening a page is reversible; submitting or sending anything remains outside this capability.
- **missing:** A durable per-origin watch registry tied to Safari tab/session identity; Local DOM fingerprint/diff extraction with selector-level redaction before relay upload; A background scheduler and cross-device change cursor; Owner-supplied origin/category rules (initially empty); A pendant alert payload that includes watch ID and drill-down action

### "“Fill out this form from the documents and messages on my Mac, show me exactly what will be submitted, and leave it ready for my review.”"
- **useful because:** The browser can reach the authenticated form while the Mac can reach local files, Mail, and Calendar; neither surface alone can safely and accurately assemble the complete answer. The owner gets a finished, reviewable form instead of copying facts between windows, while the irreversible submit remains visibly under their control.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → relay-realtime
- **model tier:** A cheaper background/local planner gathers candidate fields and provenance; realtime is reserved for resolving ambiguity in a spoken interaction and producing the final review summary.
- **latency:** Small forms in 5–15 seconds; multi-page forms up to 60 seconds with progress updates. Never wait on a model while holding an irreversible submit action.
- **cost:** One extraction/planning call plus optional field-level verification; typically low single-digit cents, dominated by OCR/long document context for unusual forms.
- **security:** The owner must provide empty-to-start origin and category rules for what may be read or persisted. Keep source snippets local, attach provenance to every filled field, redact secrets by default in the spoken summary, and never click submit/send/purchase. Detect hidden fields and cross-origin redirects; show the exact serialized payload before the final action.
- **missing:** A browser form-model/extraction action that can identify fields, labels, and validation errors; Mac-side local-source connector returning cited snippets rather than whole documents; A reversible draft state keyed to tab and form fingerprint; A review artifact rendered both in Safari and as a concise pendant speech/card; Cross-surface provenance and conflict resolution

### "“Explain the text I’m looking at in Safari, in plain language, and remember only the question—not the page.”"
- **useful because:** A spoken question from the pendant is paired with the owner's live Safari selection or viewport, so the owner can interrogate private content hands-free without dictating URLs or copying sensitive text. The answer can be short and conversational, while the raw page never becomes long-lived memory.
- **path:** browser-extension → relay-realtime → mac-vision → relay-realtime
- **model tier:** Realtime handles the short question and answer; a local browser extractor supplies only the selected/visible DOM region, and a cheaper model can pre-clean boilerplate when the region is large.
- **latency:** Selection capture under 500 ms; spoken answer in 2–4 seconds. If extraction fails, say so rather than uploading the whole page.
- **cost:** Small realtime request per question, generally a few cents or less; cost scales with selected text length, capped locally before model submission.
- **security:** Default to selection-only, ephemeral transfer with origin/title metadata optional and raw text excluded from retention. The per-origin policy must explicitly control whether content may be spoken, and categories marked never-speak must be blocked locally. Do not infer or store sensitive categories; provide a physical cancel/barge-in path on the pendant.
- **missing:** Extension support for active selection/viewport extraction and a page-scoped request ID; A relay route binding a pendant utterance to the most recent Safari selection; Local length limits and redaction before model upload; A no-retention answer mode with auditable receipt; A clear spoken fallback when Safari has no active tab or selection

### "“Show me everything the AI has read or changed in my private browser sessions this week, grouped by site, and erase any item I choose.”"
- **useful because:** The owner currently has no single, trustworthy way to answer what private web data crossed the browser/relay boundary or what actions occurred. A spoken, inspectable ledger would make the system safe enough for daily use: it exposes page reads, extracted regions, drafts, and mutations with timestamps and lets the owner delete retained artifacts rather than relying on hidden logs.
- **path:** browser-extension → mac-planner → relay-realtime → unified → relay-realtime
- **model tier:** Background processing builds a compact event index; realtime is used only to answer the owner's query and navigate the ledger. No expensive model is needed for ordinary event recording.
- **latency:** Ledger entries should appear within seconds of an action; a weekly spoken summary should respond in under 5 seconds, with pagination for detail.
- **cost:** Very low model cost: mostly structured event storage and filtering. A summary call is occasional and small; storage/indexing dominates operational cost.
- **security:** The ledger itself is sensitive. Keep raw page text out of it by default; store origin, purpose, selector/region hash, action type, retention decision, and cryptographic receipt. Require explicit owner configuration before retaining content, support per-entry deletion and complete purge, and never speak secrets in a summary unless the owner asks for the specific entry.
- **missing:** A cross-surface immutable-then-deletable event schema for browser reads and mutations; A local encrypted ledger with content TTLs and deletion receipts; Relay queries for origin/time/action/purpose filters; Pendant-friendly pagination and a physical stop/delete interaction; Instrumentation in the extension and local agent for every browser command and result

### "“Compare this private offer with my calendar, saved documents, and previous messages; tell me the tradeoffs and prepare the next three actions, but do not act yet.”"
- **useful because:** The browser holds the offer and terms behind the owner's login, while the Mac holds the practical constraints and history. Combining them produces a decision brief grounded in the owner's actual commitments rather than generic advice, and turns the result into concrete prepared actions without silently sending or purchasing anything.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → relay-realtime
- **model tier:** A background model extracts facts and conflicts from each source; a stronger model is invoked only for the final tradeoff reasoning, with realtime reserved for the spoken question and concise answer.
- **latency:** Initial extraction in 10–30 seconds; final answer in under 5 seconds after sources are ready. Long jobs should provide a pendant progress alert and resumable result.
- **cost:** Moderate per invocation because private terms plus local history can be lengthy; reduce cost with local fact extraction, deduplication, and cached source fingerprints. The reasoning pass is the dominant cost.
- **security:** Source selection and retention must be explicit per origin and category, starting empty. Keep citations and raw snippets local where possible, redact credentials and unrelated messages, and clearly separate sourced facts from model inferences. Preparing an action is allowed; sending, accepting, buying, or scheduling requires a separate owner step.
- **missing:** A cross-surface source bundle with provenance and conflict tracking; A fact extraction layer that can cite exact browser regions and Mac artifacts; A decision/constraint model rather than a generic summary prompt; A resumable action-plan object with previews and expiry; Owner-configured source and retention rules

### "“If I lose my pendant or say ‘lock my browser,’ immediately stop AI access to my authenticated Safari sessions, cancel queued work, and tell me what was revoked when I recover it.”"
- **useful because:** The browser is the only node carrying live authenticated sessions, so compromise or loss of the pendant creates a unique risk. A physical or spoken panic action would cut off queued browser work and invalidate the AI's session affinity quickly, then provide a recovery report instead of leaving the owner unsure whether a command was still pending.
- **path:** browser-extension → relay-realtime → mac-planner → relay-realtime → unified
- **model tier:** Deterministic local/relay control path; no model is required for the lock. Realtime may narrate the recovery report, but security action must not depend on inference.
- **latency:** Lock propagation under 2 seconds while connected; the extension should fail closed for new commands during a link outage and reconcile revocations on reconnect.
- **cost:** Negligible model cost; implementation cost is in extension/session invalidation and durable command-state reconciliation.
- **security:** The trigger must be authenticated by the pendant's physical interaction or an already-authenticated voice session, with replay-resistant tokens. Locking should cancel queued commands, stop result uploads, clear ephemeral page context, and optionally close only AI-owned tabs—not destroy the owner's unrelated browsing. Recovery must show exactly which commands completed, were canceled, or need inspection.
- **missing:** A pendant-to-relay panic/lock event that works offline and queues until delivery; Extension-side command quarantine and session-token revocation; A durable cross-surface cancellation barrier checked before poll and result submission; Recovery receipts distinguishing completed, canceled, and unknown commands; Owner-configurable scope (AI tabs only versus all authenticated tabs)


## Changes it proposed to its own stack

### `browser-harness` — Add a page-scoped ephemeral context channel: the Safari extension reports active tab ID, origin, title, selected text, and a bounded visible DOM fragment on request; the local agent redacts it using existing origin rules, assigns a one-time context ID, and deletes both fragment and result after the answer receipt expires. Expose explicit states (no tab, no selection, extraction failed) instead of silently falling back to full-page upload.
- **owner gets:** The owner can ask the pendant about exactly what is on screen without reading URLs aloud, copying private text, or having the system retain a page. It makes authenticated browsing feel conversational while minimizing accidental disclosure.
- effort: Medium: extension content-script capture, local-agent redaction/TTL store, and one relay correlation route; test across Safari pages with shadow DOM and iframes.  ·  risk: Selection can contain secrets or cross-origin text; origin policy and a strict byte/token cap limit exposure. If capture fails, return a clear spoken failure. Recovery is simply retry or use the existing full-page workflow explicitly.
- cost: Negligible storage; one short-lived context record per question. Model cost decreases versus full-page extraction because payloads are bounded.  ·  latency: Adds under 500 ms locally; should reduce end-to-end latency by avoiding full-page transfer.
- security: Improves least-data handling, but requires careful extension isolation and deletion verification; context IDs must be unguessable and single-use.
- depends on: Owner-supplied per-origin read/speak/retention configuration; A relay endpoint to correlate the pendant utterance with the Safari context ID; Existing local-agent redaction and browser session machinery


## What it asked for

_Nothing._
