# Harness derivation — browser-extension — round 221

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser status** — Safari on MacIntel is online with two tabs; active tabId 3186198 is a YouTube video page. Direct POST /execute browser_read_page succeeded and returned an evidence capsule; pendingCommands was 0.
  - evidence: GET /browser/status at 2026-08-09T00:12:25Z and POST /execute browser_read_page tabId 3186198 returned title/content/provenance.

## Capabilities it proposed

### ""Turn the page I'm reading into a decision brief I can act on.""
- **useful because:** The browser is the only body that can read an authenticated page; the Mac can turn that reading into a durable, editable artifact; the relay can compress it for speech; and the pendant can deliver the conclusion without making the owner reopen the page. It converts private web context into an actionable brief rather than merely reading text aloud.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a cheaper background model for extraction and structured brief drafting; reserve realtime only for the owner's follow-up question and spoken delivery.
- **latency:** 30–90 seconds for extraction, corroboration, and a draft; under 2 seconds for a follow-up spoken answer from the stored brief.
- **cost:** Roughly one background model call plus optional web-search calls; typically cents, with realtime cost only if the owner asks a follow-up. Dominant cost is page context, so send extracted claims and evidence capsule rather than HTML.
- **security:** The browser session may expose private content. Read only the explicitly addressed tab, redact secrets, retain claims and provenance rather than page text, and create a draft artifact—not an outbound message or external submission. Use the existing 24-hour browser TTL and 200-character value cap. An empty per-origin policy must remain inspectable until the owner supplies origins/categories.
- **missing:** A first-class browser job that packages page claims into a brief and writes it to a Mac note/file; Owner-supplied per-origin read/extract/redact/never-store configuration (ship empty); Pendant delivery hook for a generated brief, beyond the existing alert inbox

### ""Diagnose the error page I'm looking at and tell me the safest fix.""
- **useful because:** This joins the browser's private authenticated context with the Mac's local reality: the browser supplies the exact error and account context, while the Mac can inspect logs, network state, or app versions without asking the owner to copy/paste. The relay can explain uncertainty and the pendant can speak a short, safe next step. Neither browser nor Mac alone can connect the page symptom to the local cause.
- **path:** browser-extension → mac-terminal → mac-planner → relay-realtime → pendant
- **model tier:** Use a background model for page/error extraction and local-diagnostic synthesis; use realtime only to answer the owner's follow-up and speak the final bounded recommendation.
- **latency:** 5–20 seconds for read plus local diagnostics; under 2 seconds for follow-up questions.
- **cost:** One compact model call after extracting the error plus low-cost local diagnostics; cents per diagnosis. The dominant context cost is avoided by passing a short error block and command receipts, not the whole page.
- **security:** Do not transmit credentials, cookies, or full page bodies. Restrict the browser read to the addressed tab and redact tokens. Local diagnostics may reveal filesystem paths or host details; include only relevant lines. Any fix that mutates files, permissions, or accounts must be presented as a plan first, never silently executed.
- **missing:** A shared diagnostic envelope carrying browser evidence capsules and Mac command receipts into one model context; A browser action that extracts error/stack text while excluding nearby secrets; A Mac diagnostic policy that can run read-only checks selected from the extracted error

### ""Save this authenticated page as a citation card I can ask about months from now, and tell me when it is stale.""
- **useful because:** Browser findings intentionally expire after 24 hours, which is correct for ambient page reads but loses deliberate research. This gives the owner an explicit, durable unit: a short claim, source URL, observed date, and revalidation rule—not a copied page. The Mac can keep the card in the owner's notes/project, the browser can reopen the source when needed, and the pendant can announce that a cited claim changed.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a cheap background model to extract and normalize a few claims; use realtime only when the owner asks about a card or receives a change alert.
- **latency:** 5–15 seconds to create a card; revalidation can run in the background and need not block conversation.
- **cost:** One small extraction call per card and one small call per revalidation; usually pennies. Cost is bounded by a claim whitelist, not page length.
- **security:** This is opt-in persistence of private web-derived facts. Store only owner-selected claims, URL, host, timestamp, content hash, and evidence capsule metadata; never HTML, screenshots, cookies, or page text. Default to private/local storage, allow revoke/delete, and require the owner to choose retention duration. Do not infer that a source change means the claim is false—surface changed/unchanged/unavailable with evidence.
- **missing:** A durable citation-card store separate from short-lived browser findings; A revalidation scheduler that reopens a source only when its card is due; A pendant spoken-status event for changed or unavailable citations; Owner-configurable retention and per-origin rules, initially empty

### ""Before I click accept on this private webpage, tell me exactly what obligations, renewals, data sharing, and cancellation limits I'm agreeing to—and keep a record of the evidence.""
- **useful because:** Today the browser can read a page and other tiers can summarize it, but the owner cannot get a structured consequence analysis that follows links or expandable terms inside an authenticated flow, distinguishes stated facts from interpretation, and preserves a reviewable evidence trail before acceptance. This is especially valuable for subscriptions, employment portals, financial settings, and privacy controls where the important consequence is scattered across several pages.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a background reasoning model for multi-page extraction, obligation classification, and contradiction checking; use realtime only to answer the owner's spoken follow-up. Do not use the expensive tier for crawling or normalization.
- **latency:** 20–60 seconds for a bounded pre-acceptance analysis; under 2 seconds for follow-up questions. The owner should hear a short verdict while the full evidence ledger remains on the Mac.
- **cost:** A few small background model calls plus browser reads; roughly cents to low tens of cents depending on linked terms pages. The dominant cost is linked-page context, bounded by a maximum page/link budget and claim deduplication.
- **security:** Authenticated pages may expose financial, employment, or health information. Read only the current flow and explicitly followed same-origin terms; never submit, accept, or alter fields. Store claims, URLs, timestamps, and evidence hashes—not page HTML, screenshots, credentials, or full text. Mark every item as explicit text, inferred consequence, or unresolved ambiguity. A spoken alert must avoid sensitive values unless the owner asks. The evidence ledger must be deletable and expire by owner policy.
- **missing:** A browser-side bounded link/accordion traversal action that remains in the current authenticated session; A consequence schema for renewals, fees, permissions, data sharing, cancellation, and dispute terms; A claim ledger that records supporting evidence and contradiction status per obligation; A pre-acceptance UI/audio handoff that shows the owner the exact control that would be clicked without clicking it; Owner-provided per-origin and per-category retention rules, initially empty

### ""Build me a dispute packet for this order: compare the merchant page with my local receipt and correspondence, identify the contradiction, and draft the claim without sending it.""
- **useful because:** The owner currently has to manually reconcile a logged-in merchant page, local files or mail, and the wording of a dispute form. This capability would produce a fact-checked packet with a timeline, conflicting amounts or promises, source links, and a ready-to-review draft while stopping before submission. It uses the browser session for evidence no other node can access and the Mac for the owner's local records.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant
- **model tier:** Use a background model for document alignment, timeline construction, and draft generation; use realtime only to explain the contradiction or read the proposed claim aloud.
- **latency:** 1–3 minutes for a packet assembled from bounded sources; under 2 seconds to answer a question about a cited fact.
- **cost:** Several compact extraction/alignment calls, generally low tens of cents. Cost is dominated by local-document and page context, controlled by extracting only relevant fields and retaining provenance pointers.
- **security:** Orders, payment details, and correspondence are sensitive. Read only the selected merchant page and explicitly selected local sources; redact account numbers and payment tokens. Preserve fact-level evidence and hashes, not raw documents in the model context or long-term browser memory. Drafts must be visibly marked unsent; no submit, send, upload, or purchase action is allowed in this capability.
- **missing:** A source-selection protocol joining one browser session to explicitly selected local files/mail; A timeline and contradiction engine with field-level provenance; A draft packet format that can be reviewed on the Mac and summarized over the pendant; A submission boundary that exposes the exact final payload and target before any future send

### ""Make this authenticated dashboard usable by voice: tell me its sections, let me jump to a named control, explain the focused field, and dictate a value without submitting anything.""
- **useful because:** Plain page extraction gives the owner a wall of text and current browser commands are not a reliable semantic navigation layer. This would turn private, complex dashboards into a spoken map: landmarks, labels, required state, validation feedback, and an exact focused control. The pendant supplies hands-free speech and button interruption, while Safari performs only the reversible navigation or fill the owner requested.
- **path:** browser-extension → pendant → relay-realtime → mac-planner
- **model tier:** Use a small/cheap model to build an accessibility tree and resolve labels; use realtime for low-latency voice interaction and focus changes. Escalate only ambiguous controls to the larger planner.
- **latency:** Initial page map in 2–5 seconds; named-control focus and explanation under 1 second; dictated field fill under 2 seconds. Submission is outside the capability.
- **cost:** One compact accessibility-tree extraction per page and small realtime turns; low cents per interaction. Sending a semantic tree instead of page HTML keeps context cost bounded.
- **security:** The tree can contain private labels and values. Redact secrets and values by default, keep it in memory for the session, and persist nothing unless explicitly requested. Never infer that a focused control is safe to activate; distinguish navigation, fill, and submit. If a page uses deceptive labels or cross-origin frames, announce uncertainty rather than silently acting.
- **missing:** Extension support for semantic accessibility-tree extraction and stable element identifiers; A browser focus/describe operation distinct from click and raw text extraction; Pendant speech-to-command and barge-in routing for field-by-field interaction; A strict non-submit action profile for this voice mode


## What it asked for

_Nothing._
