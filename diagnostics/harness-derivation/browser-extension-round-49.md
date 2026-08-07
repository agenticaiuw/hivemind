# Harness derivation — browser-extension — round 49

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser availability** — Live /browser/status still reports Safari/browser offline, no tab, and 3 pending commands; home-chrome is also offline. The Mac bridge device is online but is not the browser extension.
  - evidence: GET /browser/status returned online:false, home-chrome tabId:null/tabCount:null, pendingCommands:3.

## Capabilities it proposed

### "“Save the important thing on this page.” Then tell me what you saved and where."
- **useful because:** The pendant can turn a vague voice request into a durable, sourced note from a page that only Safari can access. It saves the exact relevant passage rather than a noisy screenshot or an unsourced summary, and works across private portals, webmail, and dashboards.
- **path:** pendant: capture the spoken request and play a short confirmation → relay-realtime: classify the goal and coordinate the browser and Mac steps → browser-extension: inspect the active authenticated page, identify the relevant heading/value/paragraph, and return URL, title, DOM locator, and a compact quote → mac-planner: create a local Markdown evidence card in an owner-selected folder with timestamp, source URL, quote, and extracted fields → faculty-perception: verify that the quote and page metadata agree → faculty-judgement: choose the smallest useful passage and detect ambiguity before saving → faculty-action: write the local card and return a receipt
- **model tier:** Use the realtime tier only for the initial voice turn and ambiguity; use a cheaper background model for extraction, normalization, and card formatting. Browser DOM selectors and Mac file writing should be deterministic tools, not model-generated prose.
- **latency:** Acknowledge on the pendant within 500 ms; finish in 5–15 seconds while the page is open. If the page is ambiguous, ask one concise follow-up instead of guessing. If Safari is offline, queue the job and report that it is waiting rather than using a public mirror.
- **cost:** Roughly one short realtime turn plus one small background extraction/formatting call; typically <$0.02 excluding the already-running relay. Storage and Mac actions are negligible.
- **security:** Page text may contain private mail, work, health, or financial data. Keep the full quote and page contents on the Mac where possible; send only the minimum extracted candidate and metadata to the relay, encrypt the local card, and retain a source hash. Never save passwords, session tokens, or hidden fields. Saving a local note is reversible, but show the path and exact quote in the receipt.
- **missing:** A first-class browser extraction contract that returns semantic region plus source snippet and hash (not just flattened page text); A relay job primitive that correlates one pendant utterance with one Safari tab and one Mac file receipt; An owner-configured local evidence-card folder and retention/deletion policy; A deterministic ambiguity response when multiple page regions plausibly match “the important thing”

### "“Put a private note on this row.” Later, when I return to this page, remind me what I meant."
- **useful because:** The owner can attach durable, private context to an exact item in a logged-in web application—an invoice row, support ticket, or work item—without changing the site or relying on memory. On return, the pendant can speak the note while Safari highlights the same row, even if surrounding content moved.
- **path:** pendant: capture the note and later announce it discreetly → relay-realtime: coordinate the request and schedule the lightweight revisit check → browser-extension: identify the visible row, create a stable semantic anchor from labels and nearby values, and highlight it on return without submitting or mutating the website → mac-planner: persist an encrypted local annotation ledger and reconcile it when the page is revisited → faculty-perception: verify that the returned row matches the original anchor and detect stale or changed content → faculty-judgement: determine whether the annotation still applies and report drift instead of presenting it as current → faculty-action: save the annotation locally and issue a clear receipt
- **model tier:** Realtime only for the spoken capture and recall; deterministic extension code handles anchors and highlighting; a cheaper background model handles semantic matching and drift explanations.
- **latency:** Capture and receipt under 2 seconds. On revisit, highlight and speak within 5 seconds; if the page is unavailable, retain the reminder locally for the next matching visit.
- **cost:** Usually one short realtime turn at capture or recall and an inexpensive background matching call on revisit; under $0.02 per annotation cycle, with negligible local storage.
- **security:** The annotation and its page context may reveal sensitive work or financial information. Keep the ledger encrypted on the Mac, send only a hash/short label to the relay, exclude passwords and hidden fields, and make annotations user-deletable. Never write to or expose the website itself.
- **missing:** A browser extension annotation protocol for semantic anchors, local overlay highlights, and stale-anchor reporting; An encrypted Mac-side annotation ledger with retention and deletion controls; A revisit trigger that can match an authenticated page without uploading its full contents; Pendant-to-browser correlation so the spoken note is bound to the exact active tab


## Changes it proposed to its own stack

### `browser-harness` — Add a browser evidence-selection protocol alongside page reads. The extension returns a typed candidate set for the active page: semantic region role, visible label, normalized value, short source quote, DOM locator, URL/title, timestamp, and content hash. A relay job can request one candidate by id, and the Mac receipt writer stores the exact selected evidence. If confidence is low or candidates conflict, return ambiguity rather than silently choosing.
- **owner gets:** Voice requests like “save the deadline” or “what is the amount due?” become reliable on private pages: the owner gets the exact value and context, with a link and proof of where it came from, instead of an opaque model summary.
- effort: Medium: extension content-script extraction and typed result schema; browserBridge correlation; a small candidate-ranking adapter and tests across tables, forms, mail, and dashboards.  ·  risk: DOMs vary and selectors can go stale. Recover by storing quote/hash plus locator, marking stale evidence, and re-reading before any write. Never expose hidden inputs or password fields.
- cost: Small background extraction call only when semantic ranking is needed; otherwise deterministic DOM work. No meaningful storage cost beyond compact evidence cards.  ·  latency: Adds about 1–3 seconds for candidate extraction; avoids expensive retries and makes ambiguity explicit.
- security: Improves minimization because only selected visible regions leave the browser. Must redact password/token-like fields and keep raw page text out of relay logs.
- depends on: A functioning browser command enqueue path (the currently granted wrappers still report implementation errors); A typed Mac evidence-card writer and receipt schema; An encrypted, owner-configured local retention location


## What it asked for

_Nothing._
## Its own summary

I discovered the newly granted surface state and proposed a genuinely cross-surface capability: a pendant voice request saves the important visible fact from the currently authenticated Safari page as a sourced local Mac evidence card. I also proposed the enabling typed browser evidence-selection protocol (semantic candidate, exact quote, locator, URL, timestamp, hash, ambiguity response) and informed mac-planner. Live status still shows the browser extension offline with no tab and 3 pending commands; home-chrome has never reported a tab.

**Biggest unknown:** The remaining blocker is infrastructure, not product design: the granted browser enqueue wrappers still return implementation errors, so Safari cannot currently receive commands. I still need a real enqueue implementation, then a typed extraction result and Mac evidence-card writer. Also unresolved are the owner's chosen local card folder and retention policy, but I do not need to ask again until the command path works.

