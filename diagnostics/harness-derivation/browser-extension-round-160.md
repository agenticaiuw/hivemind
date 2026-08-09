# Harness derivation — browser-extension — round 160

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser live state and read path** — Safari extension is online with 9 tabs; active tab 1163292 is https://x.com/home. POST /execute with browser_read_page successfully returned live text plus evidence capsule evd_4ce9672bcda4, content hash, provenance, and receipt rcpt_f8bb9f3f-59f3-404f-9f9b-ece987855bac.
  - evidence: GET /browser/status at 2026-08-08T02:08:27Z and POST /execute browser_read_page at 2026-08-08T02:09:03Z

## Capabilities it proposed

### ""Check the authenticated tabs I have open, tell me what changed since yesterday, and put only urgent items on my pendant.""
- **useful because:** This is the highest-value browser capability: it turns private, already-open web sessions into a low-noise daily triage stream, while the pendant delivers urgent items even when the Mac is unattended. Unlike public search or Mail APIs, it can reach sites behind Safari logins.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** background for scheduled DOM extraction and change ranking; realtime only when the owner asks a follow-up
- **latency:** 2-5 seconds for an on-demand scan; scheduled scans can take 30-90 seconds and should not block conversation
- **cost:** Low: one extraction call per configured tab/origin plus a small ranking call; dominant cost is page text/context, reduced by storing normalized hashes and sending only diffs
- **security:** Page content leaves Safari and reaches the relay; ship with an empty per-origin rule set and require the owner to opt sites in. Store only redacted change summaries and URL/title/timestamp, never raw page text by default. Urgent alerts should be short and must respect a configurable may-speak taxonomy.
- **missing:** browser tab enumeration and DOM extraction must return stable tab IDs and origin metadata; per-origin extraction/redaction rules UI with empty default; durable page snapshots/diff store and scheduled browser poll jobs; pendant alert routing for ranked browser changes

### ""Open the form I was working on, show me exactly what is filled in, and save it as a draft I can approve from the pendant later—never submit it.""
- **useful because:** Authenticated forms are where browser access is uniquely valuable, but losing a half-completed form is costly. A durable draft capsule lets the Mac/browser prepare reversible work while the owner can inspect a concise diff and resume later from the wearable.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** background for field extraction and diff generation; realtime for the owner's spoken review
- **latency:** 3-8 seconds to capture a draft and produce a field summary; resume should be under 3 seconds
- **cost:** Low-to-moderate: DOM field metadata and values dominate context; redact secrets and transmit only changed fields where possible
- **security:** Form values may include financial, medical, or credentials. Per-origin and per-field rules must be explicit; default to local encrypted storage, no speech for sensitive fields, and an expiry. Submission remains an explicit separate operation outside this capability.
- **missing:** browser snapshot/field serialization with stable form identity; encrypted local draft vault and expiry; wearable-readable field diff with sensitive-value masking; reopen-and-rehydrate workflow that detects page/form version drift

### ""Read this private page to me, and whenever you quote it later, show me which tab and section the fact came from.""
- **useful because:** Authenticated-page answers currently risk becoming uncited summaries. A provenance capsule makes private browsing trustworthy: every extracted claim remains tied to the tab, URL, timestamp, DOM section, and a content hash so the owner can jump back and verify it.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** background for deterministic DOM segmentation, hashing, and claim indexing; realtime only to answer the owner's question from indexed sections
- **latency:** Initial indexing 2-6 seconds per page; spoken answers under 1 second when the page capsule is warm
- **cost:** Moderate one-time extraction, then cheap retrieval; costs are dominated by first-page text and can be bounded by section limits
- **security:** Do not persist raw private text by default. Keep redacted section hashes and short owner-requested excerpts with TTL; origin policy controls whether excerpts may be spoken. A stale capsule must be labeled stale rather than silently refreshed.
- **missing:** DOM section IDs and selection-aware extraction in the extension; claim-to-section index with timestamp/hash and TTL; citation payload understood by relay speech and a pendant tap-to-reopen event; explicit per-origin persistence/speech policy configuration

### ""I’m looking at something on my Mac—explain the current page, then put me back exactly where I was when you’re done.""
- **useful because:** The browser can now read a live page with tabId, windowId, URL, content hash, and a receipt, but the voice agent has no user-facing continuity contract. A context handoff lets the owner ask from the pendant without losing scroll position, tab, or a multi-tab workflow; it combines browser reach with wearable conversation in a way neither node can provide alone.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** realtime for the short explanation; deterministic local-agent capture/restore for tab, URL, scroll anchor, and focused element
- **latency:** Capture state immediately; answer in 2-4 seconds; restore in under 1 second after playback
- **cost:** Low: send a bounded page excerpt and state metadata, not the whole tab set; model cost is one short response
- **security:** The active tab may contain private data. Apply the owner's per-origin speech policy before excerpting; keep state local and expire it after the interaction. Restoration must validate URL/content hash so it does not overwrite a changed form or page.
- **missing:** extension actions to capture and restore scroll/focus/history state; a voice-session context token linking the current tab to the pendant request; bounded selection/viewport extraction instead of whole-page reads; stale-page/hash mismatch handling

### ""Compare the private pages I already have open—mail, calendar, and account dashboards—and tell me when they disagree about the same real-world event.""
- **useful because:** Today each surface is read independently. A cross-session discrepancy detector could catch mismatched delivery dates, meetings that moved without a calendar update, duplicate charges, or an account warning hidden in one tab. This is a genuinely multi-node capability: Safari supplies authenticated evidence, the Mac correlates it, the relay explains the conflict, and the pendant surfaces only the exception.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** background model for periodic entity extraction and contradiction ranking; realtime only when the owner asks about a specific conflict
- **latency:** Scheduled correlation within 2 minutes of a tab update; a focused question answered within 5 seconds
- **cost:** Moderate: extraction is bounded to enrolled pages and normalized entities; the dominant cost is comparing changed entities, not replaying full page text
- **security:** Cross-origin correlation is more sensitive than reading one page. Require explicit enrollment of each origin and category, keep raw text on the Mac when possible, persist only redacted entities/conflicts with short TTL, and never speak sensitive values unless explicitly allowed.
- **missing:** cross-tab entity extraction with origin labels; conflict/temporal reasoning over normalized entities; local encrypted correlation store with TTL; pendant alert payload for a conflict plus links back to the source tabs

### ""Turn the private article or dashboard I’m viewing into a clean note in my workspace, preserving only the sections I asked for and leaving out secrets and tracking junk.""
- **useful because:** The browser can see pages behind logins, while the Mac can write to the owner's workspace. This would convert a page that cannot be reached by ordinary web search into a durable, useful local artifact without saving an indiscriminate transcript. The owner gets a cited, redacted note rather than having to copy-paste manually.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime
- **model tier:** background model for section selection, cleanup, and concise citation; deterministic local code for writing the file
- **latency:** 5-15 seconds for a normal article or dashboard; no need to occupy the realtime voice path
- **cost:** Low-to-moderate: one bounded page extraction and summarization; local file creation is negligible
- **security:** The resulting note is durable and may outlive the browser session. Default to a preview in memory, redact configured sensitive categories, record origin and capture time, and require the owner to choose the destination and retention class. Do not include cookies, hidden fields, or unrelated tabs.
- **missing:** selection/section-aware browser extraction; redaction and citation formatter for local Markdown; workspace note writer with retention metadata; a spoken or pendant-readable preview before persistence

### ""If Safari disappears or my Mac sleeps halfway through a browser task, remember exactly what was safe to do and continue when it comes back—without repeating anything.""
- **useful because:** A browser task currently depends on a live extension poll and can lose continuity during sleep, network changes, or a Safari restart. A resumable transaction journal would make long private workflows dependable: it records completed reads and reversible edits, validates the page before continuing, and reports a concise recovery state through the pendant.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** background/deterministic worker for journal replay and page-state validation; realtime only to explain a recovery conflict
- **latency:** Resume within 10 seconds after Safari heartbeat recovery; conflict explanation under 3 seconds
- **cost:** Low model cost; most work is local journal validation and browser polling. Context is sent only for the next unfinished step.
- **security:** A stale journal must never replay against a different account, tab, origin, or changed form. Bind entries to extension device, tab, origin, URL pattern, and content hash; expire journals and scrub field values. The owner should receive a recovery alert when continuation is impossible.
- **missing:** durable browser action journal with idempotency keys; heartbeat-triggered resume worker; page/form precondition checks and recovery branching; pendant notification for paused or safely resumed work

### ""Explain the chart or canvas in the private dashboard I’m looking at, including the trend and the exact point I should care about.""
- **useful because:** Text extraction cannot reliably represent canvas-rendered charts, maps, or virtualized dashboards. Combining Safari’s authenticated tab with Mac vision and the relay would let the owner understand private visual data hands-free instead of taking screenshots or manually reading axes and legends.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** realtime vision model only for the bounded chart viewport; background model for optional trend extraction and comparison over time
- **latency:** 3-7 seconds for one viewport; under 15 seconds for a multi-chart dashboard
- **cost:** Moderate: image tokens dominate, so crop to the chart and send only the visible viewport plus accessibility metadata
- **security:** Charts can expose financial, health, or work data. Require per-origin visual-read permission, do not retain screenshots by default, and speak only the requested metric. A content hash and chart title can be retained without the image.
- **missing:** browser command to capture a bounded viewport or chart element; vision-to-structured-series extraction with uncertainty; chart-specific provenance (axis, legend, viewport, timestamp); pendant-friendly short answer and optional repeat-on-uncertainty behavior


## What it asked for

_Nothing._
