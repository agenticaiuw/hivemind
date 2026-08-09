# Harness derivation — browser-extension — round 212

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-live-state** — Safari extension is online with 3 tabs: example.com, YouTube subscriptions, and an active authenticated ChatGPT conversation titled Hercules Mulligan Spy Tactics. POST /execute browser_list_tabs and browser_read_page both succeed now; browser page reads return evidence capsules and receipts.
  - evidence: POST /execute at 2026-08-08T23:21:25Z and 23:21:29Z returned status 200, tabCount 3, and page_text for chatgpt.com.

## Capabilities it proposed

### "“Look at the authenticated pages I already have open, tell me only what needs attention, and put the important items where I can hear them later.”"
- **useful because:** This turns the browser’s unique access into a useful daily outcome without inventing websites: inspect the owner’s current logged-in tabs, identify deadlines/requests/changes, speak a compact digest, and queue only urgent items in the pendant’s offline alert inbox. It works even after the Mac link drops and can create reminders for non-urgent follow-up.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Use a cheap background extraction/classification model for each page and a small realtime model only to answer a follow-up or produce the final spoken digest; do not send full page text to the realtime tier.
- **latency:** Under 10 seconds for 1–3 tabs; under 30 seconds for a larger tab set. The owner should hear an initial count quickly, then the digest.
- **cost:** Roughly $0.01–$0.08 per run depending on page length; browser extraction and short claim classification dominate, not speech.
- **security:** Read only the tabs the owner explicitly targets (or the active tab by default), redact secrets, retain claims rather than page bodies, and never submit forms. High-impact items should be phrased as proposed next steps, not silently acted on. Empty per-origin configuration remains the default until the owner supplies origins.
- **missing:** A browser job that runs read-only extraction across selected existing tabs and ranks actionability; A relay-to-pendant delivery adapter for offline_alert_inbox with urgency and expiry; A compact cross-surface result schema linking each claim to its browser evidence capsule; An owner-facing way to choose tabs/origins without hardcoding sites

### "“Start this form in my logged-in browser, ask me for only the missing answers through the pendant, save a resumable draft, and show me exactly what is filled before I submit.”"
- **useful because:** Forms are where browser access and a wearable complement each other: the owner can answer while away from the keyboard, the browser keeps the real session and site semantics, and the Mac stores a resumable draft. It removes repetitive transcription while preserving the owner’s control over the final irreversible click.
- **path:** browser-extension → relay-realtime → pendant → mac-planner → dashboard
- **model tier:** A cheap structured extraction model maps visible labels to fields; realtime is used only for the short conversational question/answer loop. A deterministic validator checks field types and reports missing/ambiguous values.
- **latency:** Ask one question at a time within 2 seconds; save after every answer within 3 seconds. Resume should survive a browser or Mac restart.
- **cost:** About $0.02–$0.10 per form, dominated by realtime turns for ambiguous answers; deterministic field mapping is cheap.
- **security:** Never read unrelated tabs; do not persist raw page text or audio; encrypt draft values locally and give each draft a TTL. Mask sensitive values in spoken confirmations. Stop before submit and present a field-by-field diff and destination URL. The owner’s maximum-access policy means this is not a refusal gate, just a deliberate stopping point.
- **missing:** A browser form model that exposes labeled fields, current values, validation errors, and a stable draft identifier; A durable encrypted draft store shared by Mac and browser session recovery; A pendant interaction for answering/confirming one field at a time without conflating it with button gestures; A deterministic pre-submit diff renderer in the dashboard

### "“When I mark a page while I’m reading, remember the exact spot and bring that authenticated page back later—even if Safari was closed—then tell me what I was looking at.”"
- **useful because:** A worn-device bookmark is the only reliable signal that the owner meant to keep something. Pairing it with the browser’s authenticated session lets the owner leave a task mid-stream and recover it days later without hunting through history. The pendant can speak the title, section, and a short owner-safe reminder while the Mac reopens the page only when available.
- **path:** pendant → browser-extension → mac-planner → relay-realtime → dashboard
- **model tier:** Use deterministic tab/session restoration and DOM anchors first. Use a cheap model only to compress the captured section into a short reminder; realtime is unnecessary unless the owner asks a follow-up.
- **latency:** Record a bookmark in under 500 ms locally and sync opportunistically. On resume, reopen within 5 seconds and report success/failure to the pendant.
- **cost:** Near-zero for restoration; under $0.01 for optional section compression. Storage and browser wake-up dominate, not model calls.
- **security:** Persist only URL, origin, title, DOM anchor, content hash, and a short redacted claim—not page HTML, screenshots, or credentials. If the session has expired, say so rather than attempting login. Make stale anchors visibly marked and offer the owner a re-read before speaking stored content.
- **missing:** A firmware/browser event bridge carrying offline_moment_bookmark with the current browser tab and section anchor; A browser session resurrection endpoint that can reopen a tab and locate an anchor after Safari restart; A compact bookmark record with TTL, content hash, and provenance, separate from browser findings; A resume command from pendant/relay to Mac that can wait for Safari online and report failure

### "“Compare the private pages I have open, tell me which option is better for my stated criteria, and cite exactly which tab supports each point.”"
- **useful because:** The browser can see several authenticated pages that public search cannot. Today the owner must manually copy information between tabs and remember which source said what. A provenance-preserving comparison would turn those private sessions into a decision aid while keeping the answer grounded in live page evidence rather than model memory.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Use a background model to extract a typed fact table from each selected tab and a stronger model only for the final comparison when criteria are ambiguous. Realtime should deliver the short spoken result, not process page bodies.
- **latency:** 15 seconds for two ordinary pages and 30 seconds for five; return an early ‘I found N comparable facts’ status while extraction continues.
- **cost:** Approximately $0.03–$0.20 per comparison, dominated by page extraction and the final reasoning pass; evidence hashes and tab metadata are negligible.
- **security:** Require explicit tab selection or a named browser session; never mix unrelated tabs by default. Keep page text ephemeral, retain only short claims plus evidence capsule IDs and URLs, and mark stale/conflicting values. Do not infer sensitive preferences from the pages; ask for criteria when absent.
- **missing:** A multi-tab browser job contract that accepts selected tab IDs and returns normalized claims with field-level provenance; A comparison planner that can distinguish factual conflicts from different scopes or timestamps; A spoken citation format that identifies the source tab without reading private URLs or page text aloud; A dashboard view showing the claim matrix and allowing the owner to correct criteria

### "“Find any dates, deadlines, locations, or booking numbers in the private pages I’m viewing, and offer to put only the commitments I choose onto my calendar with a link back to the source.”"
- **useful because:** Important commitments are scattered through authenticated confirmations and portals, where ordinary web search cannot reach. This would convert a page the owner already opened into a durable, actionable reminder without requiring him to retype details or trust an uncited model summary.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Use deterministic date/time/location parsing first, then a cheap model to resolve context such as ‘tomorrow’ or a departure timezone. Realtime only reads the selected commitment back and handles corrections.
- **latency:** Extract candidates in under 8 seconds; show a review list immediately. Calendar creation should complete within 3 seconds after selection.
- **cost:** Less than $0.03 per page set; parsing is local and the model is used only for ambiguous context resolution.
- **security:** Treat every candidate as untrusted until the owner selects it. Do not persist page bodies or booking credentials. Store only the chosen event, source origin, URL, evidence hash, and extraction timestamp. Avoid speaking booking numbers or addresses unless the owner asks for them.
- **missing:** A commitment extractor with timezone and recurrence handling across multiple page formats; A review/selection surface usable from the pendant as well as the dashboard; A calendar adapter that stores source provenance and can undo an event created from a page; Staleness checking that re-reads the source before a high-consequence reminder is spoken

### "“While I’m reading a private page, let me ask the pendant about the paragraph or field currently under my cursor, without reading the whole page aloud.”"
- **useful because:** Current browser reading treats a page as one large document. A focused-context channel would let the owner ask ‘what does this mean?’, ‘what date is that?’, or ‘is this required?’ while keeping the relevant paragraph/field in view, which is faster and far less privacy-exposing than sending the whole page to the model.
- **path:** browser-extension → relay-realtime → pendant → mac-planner → dashboard
- **model tier:** Extract the DOM node or accessibility subtree locally in the extension and send only that bounded context. Use a small model for direct explanation; reserve realtime for the owner’s follow-up conversation.
- **latency:** Under 2 seconds from button/voice request to context capture, and under 5 seconds to a spoken answer.
- **cost:** About $0.005–$0.04 per question; bounded context keeps token cost low. Extension-side DOM/accessibility extraction is the main engineering cost.
- **security:** The extension must explicitly indicate the captured region and redact password inputs, tokens, and hidden fields. Never silently broaden from focused context to the full page. Do not persist the excerpt by default; if the owner asks to save it, retain only a short claim with the existing browser provenance rules.
- **missing:** A functioning browser_read_focus_context action returning the focused DOM/accessibility subtree and selection range; A pendant/browser correlation token so the answer refers to the exact live tab and context, not a stale page read; A redaction and bounding policy for contenteditable, password, iframe, and shadow-DOM regions; A compact spoken response mode that can point back to the on-screen region


## What it asked for

_Nothing._
## Its own summary

Discovered and verified that Safari is now online with three tabs, including an authenticated ChatGPT page; POST /execute can successfully list tabs and read page text with evidence capsules. Recorded this and notified the hive. Proposed three new cross-surface capabilities: authenticated open-tab attention triage into the pendant inbox, voice-driven resumable form drafts that stop before submission, and wearable bookmarks that restore an authenticated page/section after Safari closes.

**Biggest unknown:** The owner still has not supplied the first authenticated origins or spoken/persistence categories, so browser automation should remain empty-config and owner-targeted rather than assume sites. Engineering still needs a browser job/extraction contract, resumable form state, and wearable bookmark-to-tab anchor plumbing; no additional browser grant is needed to begin experiments because /execute works.

