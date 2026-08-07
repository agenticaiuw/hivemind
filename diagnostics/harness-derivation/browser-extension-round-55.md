# Harness derivation — browser-extension — round 55

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser bridge state** — GET /browser/status currently reports Safari/home-chrome offline and 3 pending commands, while GET /browser/sessions still contains a default Safari tab at https://time.is/UTC plus two probe sessions. The control-plane heartbeat and session store are inconsistent.
  - evidence: probe_http GET /browser/status returned online:false, pendingCommands:3; probe_http GET /browser/sessions returned three persisted sessions including tabId 320512.

## Capabilities it proposed

### "When I say “save this page for later,” capture the relevant logged-in page I’m looking at, give me a short spoken reminder on the pendant, and bring the exact evidence back when I ask about it—even if my Mac was asleep."
- **useful because:** This turns the browser’s unique access to private sessions into a durable, conversational memory. The owner gets a small, sourced reminder instead of losing a tab, while avoiding repeated login navigation and avoiding any mutation of the site.
- **path:** browser-extension → mac-planner → relay-realtime → unified
- **model tier:** Use a cheap background model to select and compress page evidence; use realtime only for the owner’s spoken save/follow-up and a small summary. The browser extension supplies the private DOM; Mac-planner binds it to context; relay stores the expiring capsule and routes the pendant query.
- **latency:** Acknowledge the save in under 2 seconds with title and expiry; capture can finish within 10 seconds. A later pendant query should return the cached evidence in under 3 seconds, or explicitly say the capsule expired and offer to reopen the page.
- **cost:** Roughly $0.005–$0.03 per save/query depending on page length; browser bridge and storage dominate operational cost, while the cheap summarization call dominates API cost. No relay-browser minutes are needed for an already-open private Safari tab.
- **security:** The capsule may contain private authenticated text. Encrypt at rest, bind it to the owner, retain only a configurable TTL (default 7 days), redact secrets/credit-card-like fields before model submission, and never include cookies or raw DOM by default. Reopening a page must not submit, send, purchase, or change anything; show the source URL, capture time, and an evidence excerpt when answering.
- **missing:** A browser capsule schema and encrypted TTL store shared by relay and Mac-planner; A browser action that captures the active tab plus stable URL/title/selected text and a bounded semantic excerpt; A pendant notification/lookup route and unified query resolver that can retrieve a capsule by spoken reference; A durable browser job runner/result stream so capture survives a Mac or extension restart; A live Safari extension heartbeat (currently browser status reports offline)

### "While I browse, let me ask the pendant “what on this page matters?” or “what changed from the tab I just left?” and get a concise answer grounded in the current logged-in tab, without stopping to copy or share the page."
- **useful because:** Today the browser is a private island: the owner can see the page, while the pendant conversation cannot continuously understand the tab they are actively using. This would make the wearable a hands-free second channel for private web work, including comparisons across tabs that only the extension can access.
- **path:** browser-extension → relay-realtime → mac-planner → unified
- **model tier:** Use a small/cheap model for DOM landmark extraction, visible-region diffs, and page compression; reserve realtime for the owner’s spoken question and answer. mac-planner should resolve project/person context and select which tab evidence is relevant, not receive whole pages by default.
- **latency:** Stream a compact page landmark update within 1–2 seconds after navigation or a meaningful DOM change; answer a spoken question in under 3 seconds. Fall back to an explicit “page is still loading” rather than blocking the conversation.
- **cost:** About $0.001–$0.01 per question and modest relay storage/egress; incremental visible-text hashes are cheaper than repeated full-page model calls. The main cost is extension-side extraction and maintaining a short-lived tab context.
- **security:** Only the active tab and explicitly compared tabs may be included; do not transmit cookies, hidden DOM, passwords, payment fields, or full-page text by default. Encrypt the short-lived context, expire it quickly, show the page title/domain in the spoken answer, and provide a physical pendant action to clear the current browser context. Never click, type, or submit as a consequence of an informational question.
- **missing:** An extension event stream for active-tab navigation, focus, and visible-content changes (not just a poll/result command queue); A low-latency relay channel that associates spoken turns with an owner-scoped tab context and drops stale updates; A bounded visible-region/landmark extractor with secret-field redaction and cross-tab diffing; A unified resolver that can ask mac-planner for project context without exposing the raw authenticated page; A reliable Safari heartbeat and command/result path so the current tab context is actually available


## Changes it proposed to its own stack

### `browser-harness` — Add a private evidence-capsule protocol: browser_capture_capsule targets a tab/session and returns a bounded, normalized excerpt with URL, title, capture timestamp, selected DOM locators, content hash, and sensitivity labels. Mac-planner stores only the redacted excerpt plus a pointer to an encrypted relay object with TTL; relay exposes owner-scoped capsule lookup and push notification. On follow-up, the resolver first answers from the capsule, then optionally queues a read-only revalidation against the same Safari session and marks stale fields instead of silently refreshing.
- **owner gets:** The owner can say “save this” once and later ask about it from the pendant without hunting through tabs or repeating a private login. Answers remain tied to what was actually seen and clearly distinguish captured facts from current facts.
- effort: Medium-high: capsule schema/storage, DOM extraction and redaction, owner-scoped encryption/TTL, notification and voice lookup wiring, and a restart-safe browser job integration.  ·  risk: Over-redaction can make a capsule useless; under-redaction can retain sensitive account data. Use bounded excerpts, explicit sensitivity labels, short default TTL, deletion by voice/dashboard, and a stale marker. If the Safari session disappears, return the stored evidence rather than attempting a public fallback.
- cost: Small storage and relay invocation cost; one cheap summarizer call per capsule. Revalidation costs a Safari command only when requested, avoiding routine browser polling.  ·  latency: Save acknowledgement is immediate while extraction completes asynchronously; cached lookup is faster than reopening Safari. Revalidation adds up to the browser bridge timeout.
- security: Improves security versus retaining full pages by minimizing and expiring data, but introduces a sensitive relay object. Encrypt capsules with an owner key, keep plaintext out of logs, and audit every lookup with source and expiry.
- depends on: A live Safari extension heartbeat and working browser command enqueue path; The still-missing durable browser job runner/result stream (chg-16bc5dee); An owner-authenticated relay object store and pendant push/lookup route

### `browser-harness` — Add an owner-scoped live-tab context channel separate from the command queue. Safari emits debounced events for active-tab changes, navigation completion, visible accessibility-tree landmarks, and user selection; a local redactor removes password/payment/hidden fields, computes content-region hashes, and sends only bounded deltas to relay. The relay maintains a short TTL context keyed by voice session and tab identity, supports a two-tab diff request, and invalidates context on tab switch, logout indicators, or timeout.
- **owner gets:** The pendant can answer questions about what the owner is looking at right now, and compare adjacent private tabs, without the owner reading text aloud or handing over control of the browser.
- effort: High: extension event instrumentation, accessibility-tree/visible-region extraction, redaction tests, low-latency relay routing, tab identity lifecycle, and voice-session integration.  ·  risk: A DOM/accessibility change could leak sensitive content or create noisy updates. Ship denylisted field types, visible-only defaults, strict byte/rate limits, explicit tab/domain indicators, short expiry, and a clear-context button; if the stream fails, the voice agent must say it cannot see the current tab rather than infer.
- cost: Low-to-moderate relay and model cost; deltas and hashes substantially reduce tokens versus full-page snapshots. Extension and relay engineering are the dominant cost.  ·  latency: Adds a small event-to-relay path (target under 1 second); question answers become faster because current context is already warm. Initial extraction may take 1–2 seconds on complex pages.
- security: Creates a new live channel for private authenticated data, so it needs owner/session binding, encryption in transit and at rest, no durable raw-page logs, per-domain opt-out, and automatic purge on tab switch or timeout.
- depends on: A functioning Safari extension heartbeat and browser result path; A relay realtime context stream keyed to the pendant voice session; A tested visible-content redaction and bounded accessibility-tree extractor; Unified/mac-planner routing that can request tab diffs without broadening page access


## What it asked for

_Nothing._
## Its own summary

Discovered a new cross-surface capability beyond the existing page-watch/workbench proposals: expiring private evidence capsules. Saying “save this page for later” captures a bounded, redacted excerpt from the logged-in Safari tab, stores it encrypted with a TTL through the relay, gives a spoken pendant acknowledgement, and later answers from cited cached evidence or performs an explicit read-only revalidation. Proposed both the owner capability and browser-harness implementation, and notified mac-planner. Live checks found a control-plane inconsistency: /browser/status says offline with 3 pending commands, while /browser/sessions still has a default Safari tab and two probe sessions.

**Biggest unknown:** Whether the real Safari extension is actually able to poll and return commands now; the status/session contradiction needs an end-to-end heartbeat plus one harmless browser capture before capsule work can be validated. Still needed: working enqueue/heartbeat, durable browser job runner/result stream, owner-scoped encrypted TTL storage, and pendant lookup/push wiring.

