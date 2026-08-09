# Harness derivation — browser-extension — round 152

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "I'm looking at a web page—answer my next question using the relevant section of this page, and quote where you found it."
- **useful because:** This turns the one surface that can see the owner's logged-in pages into a real voice companion: the owner can ask about a benefits portal, private dashboard, or document without copying text or exposing it to another service. It should use the active tab and, when available, the browser's selection/viewport so 'this' has a precise meaning.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Realtime for the spoken question and short answer; a cheaper background extractor can locate the cited passage before the realtime response when the page is large.
- **latency:** Under 4 seconds for an already-open tab; extraction is local through the browser bridge and should not wait on a cloud page fetch.
- **cost:** Usually one short realtime turn plus a small extraction call, roughly $0.01–$0.05; page text, not screenshots, dominates context size.
- **security:** Page content and the question leave the Mac only to the relay/model. Default to ephemeral extraction, origin policy redaction, and never persist the page. The answer must include origin/title and a quoted span so the owner can detect stale or wrong-tab context.
- **missing:** A reliable active-tab/selection read action (the current extension inventory has browser_list_tabs and browser_read_page but no stable active-tab or selection primitive); A request correlation path from pendant speech to a specific tab and viewport/selection snapshot; A compact citation payload in browser results

### "Fill out this web form from my local documents and calendar, read me exactly what will be submitted, and leave it unsubmitted for my review."
- **useful because:** Authenticated forms are a high-friction task where the browser, Mac, and pendant each have indispensable reach: Safari owns the session and fields, the Mac can retrieve local PDFs/calendar facts, and the pendant can give a hands-free review. The owner gets a completed draft without risking an accidental send or purchase.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → pendant
- **model tier:** Use a cheaper background planner/OCR pass for local-document field matching and a realtime turn only to resolve ambiguity and speak the final field-by-field review.
- **latency:** 30–90 seconds depending on document lookup; pause at any ambiguous field and never silently guess.
- **cost:** About $0.03–$0.15 per form, dominated by OCR/field text and the final review; no screenshot needs to leave the Mac if local extraction works.
- **security:** The browser session and local documents are highly sensitive. Apply per-origin and category policies, keep extracted values in the local job only, redact values from logs, and show every populated field plus source before typing. Submission is explicitly excluded; if the site autosaves drafts, warn the owner.
- **missing:** A browser form model that returns field labels, types, current values, and stable selectors; A local-only document/calendar fact extractor with source references; A typed draft-fill result that can be undone and a pendant-friendly review sequence; A cross-surface ambiguity callback so the owner can answer one field at a time

### "Keep watching this authenticated page and tell me on my pendant when the specific condition I named becomes true—such as an appointment opening, a status changing, or a deadline moving—without storing the page contents."
- **useful because:** The owner can delegate a private, time-sensitive web state to the always-awake relay while Safari remains the only place able to see it. A semantic condition is more useful than a generic notification: it avoids interrupting for cosmetic changes and can still reach the owner offline through the pendant's alert inbox.
- **path:** browser-extension → relay-realtime → mac-planner → pendant → faculty-perception → faculty-judgement
- **model tier:** Use a cheap scheduled/local comparator for repeated checks; invoke the realtime model only when a meaningful transition needs a concise spoken explanation.
- **latency:** Check interval chosen by the owner, from one minute to daily; alert within one interval plus a few seconds. Stop or back off on login expiry and site rate limits.
- **cost:** Low ongoing cost if DOM hashes/selectors and local rules handle unchanged pages; roughly $0.001–$0.02 per check, with model cost only on change.
- **security:** Keep DOM snapshots and before/after text on the Mac, send only a redacted transition summary, and honor empty-by-default per-origin storage rules. Never auto-submit, book, or purchase. Surface login expiry as an error rather than repeatedly retrying credentials.
- **missing:** A durable watch scheduler that can wake the browser bridge and retain a watch across relay restarts; A declarative condition language over selected DOM fields plus a local semantic diff fallback; A redacted transition receipt with old/new values and timestamp; Integration with the accepted offline_alert_inbox skill and an owner-visible pause/delete control

### "Turn this long authenticated web process into a resumable checklist: gather and verify the information it needs from my Mac, complete only the next safe step, and when I come back days later resume at the exact page and field without making me start over."
- **useful because:** Today the browser agent can act in a session, but the owner cannot delegate a multi-day process without losing place, source provenance, or the distinction between verified and guessed fields. This would make painful applications, renewals, claims, and account setup into an interrupted workflow the owner can continue from the pendant or Mac, while still stopping before irreversible submission.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → pendant → faculty-perception → faculty-judgement → faculty-action
- **model tier:** A background planner builds the field/checkpoint graph and matches local sources; realtime is used only for ambiguity resolution and a short spoken checkpoint briefing.
- **latency:** Initial decomposition 1–3 minutes; each resume under 10 seconds if the session is alive, or under a minute to restore/navigation-check the page. Never silently advance when the DOM or policy has changed.
- **cost:** Approximately $0.05–$0.30 per workflow setup and a few cents per resumed checkpoint; local DOM/state snapshots and document matching dominate context, not speech.
- **security:** Persist only encrypted checkpoint metadata, field hashes, source references, and origin—not raw page text or secrets by default. Detect changed terms, expired sessions, and changed totals as hard pauses. The owner can inspect, revoke, or delete the workflow; submission, payment, signing, and sending remain explicit terminal steps.
- **missing:** A durable browser workflow store with encrypted checkpoint graphs, DOM fingerprints, and tab/session restoration across Safari restarts; A browser action that can reopen a checkpoint and verify the expected field before typing, rather than relying on a stale selector; Local source provenance records linking each populated value to a document/calendar item and verification timestamp; Pendant commands for resume, skip, explain, pause, and delete plus a compact checkpoint receipt; A change detector that invalidates downstream checkpoints when a site changes its questions or terms

### "After you use a logged-in web page, show me a plain-language privacy receipt: which site and fields were read, which model saw them, what was retained, and let me erase that page's contribution without deleting the rest of my work."
- **useful because:** Private browser access is uniquely powerful but currently opaque. The owner should be able to use it confidently without guessing whether a whole page, a password field, or a temporary excerpt crossed the relay, and should be able to clean up one site's contribution after the task. This is transparency and selective deletion, not an approval gate that blocks useful work.
- **path:** browser-extension → relay-realtime → mac-planner → pendant → dashboard-ux → faculty-judgement
- **model tier:** Generate the receipt locally from typed browser events; use a cheap model only to phrase it for speech. No expensive model is needed to decide what was read or retained.
- **latency:** Receipt available with the task result, under 500 ms extra; deletion should complete within seconds and return a verifiable tombstone.
- **cost:** Negligible inference cost; a small local event ledger and dashboard storage are the main cost.
- **security:** Receipts must contain field categories and hashes, not secret values or page text. The ledger itself is sensitive and must be encrypted locally, origin-scoped, exportable, and deletion-complete across browser cache, relay context, jobs, logs, and derived summaries. Do not claim deletion until every store acknowledges it.
- **missing:** Typed browser read/type events carrying origin, selector category, redaction result, and retention class; A cross-store lineage ledger connecting browser results to model prompts, jobs, spoken output, and derived artifacts; An origin-scoped erase endpoint that propagates to Mac jobs, relay context, and dashboard cache; A pendant command and dashboard view for receipt, retention, and selective deletion


## Changes it proposed to its own stack

### `browser-harness` — Add a single browser command `browser_context_snapshot` implemented in the Safari extension that atomically returns active tab id, origin/title, URL, selected text, viewport text, and a short DOM locator map; include a monotonically increasing page revision and reject stale writes. Expose it through the existing /execute -> poll/result bridge, with local redaction before the result leaves Safari.
- **owner gets:** The owner can say “what does this section mean?” or “fill this from what I’m looking at” and get an answer grounded in the tab actually in front of them, rather than accidentally querying a background tab or an old page. It also makes private-page monitoring precise without uploading whole pages.
- effort: Medium: Safari extension command, content-script extraction, result schema, and /execute action registration; test on dynamic pages and multiple tabs.  ·  risk: Selection/DOM extraction can miss canvas-rendered content or expose a password field. Exclude input[type=password], redact known secrets locally, label confidence, and fall back to an explicit tab id. If the extension is offline, report unavailable rather than using stale context.
- cost: Negligible API cost; reduces token cost by sending the selected/visible region instead of full page. No hardware cost.  ·  latency: Adds roughly 100–500 ms locally; avoids a second browser round trip and reduces model latency.
- security: Improves security by constraining extraction to the active tab and redacting before relay, but introduces a new privileged content-script path that needs origin policy tests.
- depends on: A resolved browser_read_page/browser_context_snapshot action in the live capability manifest; Existing POST /execute browser bridge and Safari extension v1.2.0; Per-origin redaction rules from local-agent/httpPolicy.js and redaction.js


## What it asked for

_Nothing._
## Its own summary

Round 152 produced three distinct browser capabilities: voice Q&A grounded in the active authenticated page; cross-surface form drafting from Safari plus local Mac documents/calendar with field-by-field review and no submission; and semantic condition watches on private pages delivering only meaningful transitions to the pendant's offline alert inbox. I also proposed a Safari browser_context_snapshot primitive to make active-tab/selection grounding reliable and local-redacted. What I still need is not another wrapper: a live resolved browser_read_page/context action, atomic active-tab/selection extraction, durable watch scheduling/comparison, and the owner’s per-origin/category policy configuration. Safari is now online with 9 tabs, so these can be tested immediately.

**Biggest unknown:** Whether the live backend already has an unobserved durable watch scheduler or active-tab/selection action; the route inventory shows /watches but its semantics are not yet described, and the enqueue wrappers remain ambiguous/stubbed.

