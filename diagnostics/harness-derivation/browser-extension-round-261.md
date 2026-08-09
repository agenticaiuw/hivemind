# Harness derivation — browser-extension — round 261

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser live state** — Safari extension is online with one active tab: YouTube video Max Hodak: Average Is Not Good Enough, tabId 52; POST /execute browser_list_tabs succeeds and browser actions are operational through the route.
  - evidence: POST /execute {actions:[{type:'browser_list_tabs'}]} returned status 200, tabCount 1, tabId 52, active=true.

## Capabilities it proposed

### "“What am I looking at? Ask the page: is this claim supported, and give me the two facts that matter.”"
- **useful because:** The browser is the only body with the owner's authenticated context, while the pendant is the only body available while his hands and eyes are occupied. A voice request should bind to the currently active Safari tab, extract just the relevant page evidence, and answer without forcing him to copy a URL or expose page text to other surfaces. This is the single most useful browser capability: authenticated, context-aware answers on demand.
- **path:** browser → relay → pendant
- **model tier:** Use the realtime model only for the short spoken exchange; use the cheaper local planner/browser extraction path to read the active tab and select evidence, then send a compact claim/evidence capsule to realtime.
- **latency:** 3–6 seconds end to end for a normal page; a visible “still reading” alert after 4 seconds and a hard 20-second timeout.
- **cost:** One small local-agent action plus a compact realtime turn, typically far cheaper than sending the page body; cost is dominated by the spoken response, not extraction.
- **security:** The page may contain secrets. Send only the minimum quoted evidence, never raw HTML or screenshots; apply existing browser redaction and 24-hour, 200-character browser-fact limits, and persist nothing unless the owner explicitly asks. Bind to the active tab at request time so a later tab cannot be confused with the spoken context. No irreversible browser action is involved.
- **missing:** A stable active-tab/current-page action in the browser harness (the live POST /execute path works, but the granted wrapper is ambiguous);; A relay intent that carries a short spoken question plus tab-bound browser evidence;; An explicit empty per-origin policy UI/configuration, populated only when the owner chooses origins.

### "“On this logged-in page, what changed since the last time you checked it? Show me only changed facts, with links back to the exact sections.”"
- **useful because:** A normal page read answers what is present now; this answers what matters over time without requiring a permanent watcher. It lets the owner revisit a dashboard, statement, or account page after an arbitrary interval and get a compact, evidence-linked delta while the browser remains the only place authenticated content is visible.
- **path:** browser → mac-planner → relay → pendant
- **model tier:** Use local extraction and stable section fingerprints first. Use a cheaper background model to normalize changed sections; reserve realtime for the final spoken delta and a follow-up question.
- **latency:** 5–10 seconds for a typical page, with a 30-second timeout for a large dashboard.
- **cost:** Low-to-moderate: extraction and hashing are local; model cost is proportional to changed sections, not the whole page. Realtime is one short answer.
- **security:** Store only redacted section claims and hashes under the existing browser TTL, never page HTML or screenshots. Keep the baseline keyed to host, URL pattern, and section identity; expose provenance links and let the owner delete the baseline. Require explicit per-origin configuration, shipped empty.
- **missing:** A baseline/delta endpoint for browser findings that records section fingerprints without retaining page text;; A page-section locator that can produce stable anchors/URLs for evidence;; A user-facing way to request or clear a baseline from the pendant/relay.

### "“I can’t find the control on this page—where is it, and can you point it out without clicking?”"
- **useful because:** The owner can be looking at a dense authenticated web app while using the pendant hands-free. Browser text extraction often omits canvas controls or spatial relationships; a browser snapshot plus vision can identify the requested control, describe its location relative to the viewport, and optionally highlight it without performing the action.
- **path:** browser → mac-vision → relay → pendant
- **model tier:** Use the cheap vision loop for screenshot localization and the local planner for selector validation. Use realtime only to speak the short location answer.
- **latency:** 2–5 seconds for a normal page; never click as part of this request.
- **cost:** Low: one screenshot and a small vision inference; a brief realtime turn if spoken.
- **security:** The screenshot can contain authenticated data. Keep it in-memory, redact known secrets before any model handoff, do not persist it, and expose a strict read-only action set. The owner explicitly asked for pointing, not clicking.
- **missing:** A browser_snapshot result path that can be passed to mac-vision with tab/viewport coordinates;; A non-mutating highlight overlay or returned rectangle that Safari can render;; A relay intent for spatial references such as “top-right” and “next to the Save control.”

### "“Compare the two authenticated pages I have open and tell me why their numbers disagree; cite each source and do not change either page.”"
- **useful because:** Many of the owner's hardest web questions are relational, not single-page lookups: an invoice versus a vendor portal, a benefits statement versus an account dashboard, or two versions of a contract. Today the browser tier can read a page, but it cannot safely align claims across authenticated origins and explain a discrepancy. This gives the owner an evidence-backed answer while preserving both sessions untouched.
- **path:** browser → mac-planner → mac-vision → relay → pendant
- **model tier:** Use the local planner for tab selection, extraction, normalization, and arithmetic. Use a cheaper reasoning model for claim alignment. Use realtime only to deliver the concise spoken conclusion and answer follow-ups.
- **latency:** 8–15 seconds for two ordinary pages; up to 45 seconds for large authenticated dashboards, with incremental progress spoken after the first page is captured.
- **cost:** Moderate: two page reads and a small structured comparison; realtime cost is limited to the final answer, not the page contents.
- **security:** Keep origins and sessions isolated during extraction; never merge raw page text into persistent memory. Pass only the minimum redacted claims and provenance URLs to reasoning. Persist no result unless explicitly requested, and preserve source-specific citations so a claim from one origin cannot silently be attributed to another. Use the existing empty per-origin policy rather than inventing an allowlist.
- **missing:** A multi-tab browser query primitive that reads a specified set of existing tabs without navigation or mutation; A claim-normalization and discrepancy engine that retains source identity and confidence for every compared field; A spoken response format that can identify source A/source B and let the owner request a browser jump to one citation

### "“Is this page safe to share with my team? Find secrets and personal details, explain what would leak, and prepare a redacted copy without sending it.”"
- **useful because:** The owner can inspect a private authenticated page and need to turn it into a safe status update, bug report, or support request. Today the browser can read content, but it cannot produce a trustworthy, reviewable redaction preview that preserves useful context while preventing accidental disclosure. A pendant-readable risk summary plus a draft artifact is valuable even when no message is sent.
- **path:** browser → mac-vision → mac-planner → relay → pendant
- **model tier:** Use deterministic local redaction for credentials, tokens, email addresses, account numbers, and obvious identifiers. Use the cheaper vision/reasoning tier to classify ambiguous sensitive passages. Use realtime only for the short spoken risk summary; never send raw page text to realtime.
- **latency:** 5–12 seconds for a page-sized document; return a draft preview and risk count before any export.
- **cost:** Low-to-moderate: local scanning dominates; model inference is only for ambiguous regions. No realtime turn is needed unless the owner requests spoken output.
- **security:** The original stays in Safari and is never uploaded as a persistent artifact. Redacted output is held ephemerally until the owner explicitly saves or copies it. Show every replacement and its reason, preserve source location, and never claim that automated redaction guarantees safety. No send/share action is performed by this capability.
- **missing:** A browser-to-local-agent extraction path that returns text and screenshots with region offsets; A deterministic, inspectable secret/PII classifier with a redaction preview format; An ephemeral draft/export surface that requires a separate owner request before copying or saving

### "“Pause this private web task and let me resume it tomorrow exactly where I left off, even if Safari closes; keep only the steps and fields, not the page contents.”"
- **useful because:** Authenticated web work is fragile: a laptop sleep, tab close, or dropped link currently loses the owner's place and forces him to reconstruct the task. A privacy-minimizing task capsule would preserve the workflow state—origin, safe selectors, completed steps, and unsent field intentions—without retaining page text or credentials, then rehydrate it into the owner's existing Safari session later.
- **path:** browser → mac-planner → relay → pendant
- **model tier:** Use the local planner to serialize and validate workflow state. Use a cheap background model only to normalize human-readable step labels. Realtime is unnecessary except for a short pendant confirmation when pausing or resuming.
- **latency:** Pause under 2 seconds; resume and verify the page in 5–15 seconds. If the page changed, stop at a review state rather than guessing.
- **cost:** Low: mostly structured local state and browser actions; model use is optional and limited to labels.
- **security:** Never store passwords, cookies, page bodies, screenshots, or sensitive field values. Store only an encrypted, expiring task capsule with origin, tab identity, selectors, and redacted field metadata. On resume, re-read the live page and invalidate stale selectors. The capsule must be inspectable and deletable, and resume must stop before any irreversible submit.
- **missing:** An encrypted browser-task capsule store with expiry and explicit deletion; A browser session rehydration protocol that validates origin, tab state, and selector freshness before acting; A way to mark field intents as safe-to-replay versus requiring fresh owner review


## What it asked for

_Nothing._
