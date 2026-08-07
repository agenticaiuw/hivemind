# Harness derivation — browser-extension — round 36

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-extension** — As of this round, /browser/status reports online=false, only an uninitialized home-chrome device, and pendingCommands=2; Safari is not represented despite the Mac bridge being online. Browser work cannot be truthfully claimed until extension heartbeat returns.
  - evidence: GET /browser/status at 2026-08-07T09:58Z response: online false; devices=[home-chrome tabId null tabCount null]; pendingCommands 2.

## Capabilities it proposed

### "When I’m looking at a logged-in webpage, let me say “save this for later” and later ask the pendant to find or reopen it, even if I’ve closed the tab."
- **useful because:** The browser is the only node that can see the owner’s authenticated pages, while the pendant is the only one always available. This creates a private, cross-device memory for useful pages (tickets, order details, forms, research) without requiring the owner to copy URLs or expose page contents to public search. It is distinct from change-watching: it captures an intentional moment and lets the owner retrieve it later.
- **path:** browser-extension → mac-planner → relay-realtime → relay-realtime → dashboard
- **model tier:** Use the realtime model only to interpret the short spoken save/find request and confirm the target. Use a cheaper background model on the Mac to extract a title, entities, key facts, and a compact summary from the authenticated page; the relay stores only an encrypted capsule and minimal searchable metadata. Browser reopens the original URL/session when requested.
- **latency:** Save: under 5 seconds after the extension is online; spoken confirmation can happen immediately with a pending state. Find: under 2 seconds for metadata search, then 5–10 seconds to reopen or reattach a tab. If Safari is offline, queue the capture/reopen and state clearly that it is pending rather than claiming success.
- **cost:** Roughly $0.002–$0.02 per save depending on page length and background extraction; find is usually <$0.001. Storage and indexing dominate long-term cost, not realtime inference.
- **security:** Authenticated page text can contain health, financial, work, or account data. Encrypt the capsule at rest with a device-bound key, keep it on the owner’s Mac by default, and send the relay only opaque IDs plus minimal encrypted data needed for pendant retrieval. Record source URL, tab ID, capture time, and a content hash; expire capsules by default (for example 30 days) with per-item delete. Never silently submit forms or follow an external action when reopening; show the page and stop.
- **missing:** A browser command that captures the active tab with bounded DOM text plus URL/title and returns a typed result (not only a screenshot).; A durable encrypted page-capsule store on the Mac with relay synchronization, TTL, deletion, and full-text/embedding search over locally decrypted content.; A pendant intent and result protocol for save/find/reopen, including pending/offline status and concise spoken confirmations.; Safari-extension reconnect handling: pending browser commands currently remain queued while status is offline, so the UI must surface stale/offline captures and retry safely with idempotency keys.

### "While I’m browsing, let me ask the pendant “What am I looking at?” or “Help me with this page,” and have it understand the current tab without me reading the URL or describing the page."
- **useful because:** Today the pendant and browser are effectively separate: the owner must manually explain which page is open before the system can help. A privacy-preserving active-tab handoff would make the wearable a true companion to the private browser session. It could identify the current page, summarize the relevant visible section, explain unfamiliar fields, or prepare next steps while leaving the browser in control.
- **path:** browser-extension → relay-realtime → mac-planner → dashboard
- **model tier:** The extension supplies active-tab metadata and, only after the spoken request, a bounded page extract. Use the realtime model to resolve the short request and answer conversationally; use a cheaper background model for long-page summarization or field explanation. The Mac planner coordinates tab identity and returns citations/locators to the browser.
- **latency:** Active-tab metadata should reach the relay in under 300 ms. A short visible-page answer should take 2–4 seconds; long extraction can continue asynchronously with a spoken 'I’m checking that page' status. If the extension is offline or the tab changed, state that explicitly and do not use stale context.
- **cost:** Metadata-only requests are negligible. A page explanation costs roughly $0.002–$0.02 depending on extracted text; the main cost is model input for long pages. No continuous page contents need to be uploaded.
- **security:** Do not stream page content continuously. Publish only an ephemeral tab identifier, origin, title, and timestamp; fetch authenticated text only in response to an explicit request. Mark sensitive origins and redact passwords, payment fields, tokens, and hidden inputs. Bind every answer to tab ID, URL, and capture time so a changed tab cannot be mistaken for the requested page. Keep extracts ephemeral unless the owner explicitly asks to save them.
- **missing:** A privacy-scoped active-tab context channel from Safari to the relay, with freshness and tab identity.; An on-demand bounded DOM extraction API that excludes secrets and hidden/form credential fields.; Cross-surface routing that binds the spoken request to the current browser tab and rejects stale captures.; A concise pendant response format with page citations or a Mac dashboard handoff for details.


## What it asked for

_Nothing._
