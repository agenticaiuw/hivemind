# Harness derivation — browser-extension — round 47

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-command reliability** — As of live probe, browser status reports online=false, Safari absent, stale home-chrome only, and pendingCommands=3; ops/status repeats the same state. Routes expose poll/result/delete but no watchdog or lease reconciliation endpoint.
  - evidence: GET /browser/status HTTP 200: online false, home-chrome lastSeenAt stale, pendingCommands 3. GET /ops/status HTTP 200: browserExtension online false and same pendingCommands 3. GET /routes discovery lists browser poll/result/delete but no watchdog route.

## Capabilities it proposed

### "Keep my browser tasks from silently hanging: if Safari disconnects, recover safe reads automatically and tell me exactly what did not run."
- **useful because:** Authenticated browser work is uniquely dependent on the extension. Today commands can remain pending while the extension is offline (fresh live state: pendingCommands=3), leaving the owner unsure whether a page was read or an action happened. A relay/Mac/extension/pendant watchdog can distinguish safe reads from mutations, recover only idempotent work, and provide an audible, cited failure receipt.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard-ux
- **model tier:** Use deterministic relay/Mac watchdog logic and a cheap background model only to summarize failed/retried command receipts; reserve realtime for the pendant alert.
- **latency:** Heartbeat detection 10–20 s; command expiry 30–45 s (matching current browser result wait); safe retry within 1 minute. Pendant alert should be under 2 s after the watchdog classifies a stranded command.
- **cost:** Near-zero model cost for detection/retry; roughly $0.001–$0.01 only when a background model compresses a multi-command receipt. Dominant cost is persistent heartbeat/status traffic and implementation time.
- **security:** Never retry browser_click/type/select/press-key or form submission automatically. Retry only browser_navigate/read/snapshot/wait when the command declares an idempotent target and the original tab/session affinity is still valid. Store URLs, selectors, and extracted text only in local receipts unless the owner explicitly asks for relay sync. Pendant should say the domain/title, not page contents. Recovery and expiry receipts must be visible in dashboard and queryable by command id.
- **missing:** Extension heartbeat must include a monotonic session/connection id and tab identity, and reconnect promptly after Safari sleeps.; Mac browser bridge needs a watchdog that leases commands, expires stranded leases, classifies idempotent versus mutating actions, and records retry lineage.; Relay needs a small durable browser-watch state/alert channel so it can notify the pendant when the Mac is unreachable.; Dashboard needs a pending/expired/retried timeline with an explicit 'not executed' versus 'execution unknown' state.; Pendant needs a concise offline-browser alert and a way to request the latest receipt.

### "Let me ask my pendant questions about whatever authenticated Safari page I am currently looking at, and have it find the answer or open the relevant section without me dictating a URL."
- **useful because:** The browser is the only node that can see the owner's logged-in pages, while the pendant is the only node available when their hands and eyes are busy. Today those surfaces cannot act as one continuous conversation. This would turn a private web session into a hands-free, low-friction assistant without exposing the whole page or requiring the owner to copy links.
- **path:** browser-extension → relay-realtime → mac-planner → pendant → dashboard-ux
- **model tier:** Realtime model handles the short spoken question and answer. The browser bridge performs deterministic extraction and safe reveal/scroll actions; use a cheaper background model only for long-page semantic indexing.
- **latency:** Initial answer from visible DOM within 1–2 seconds; an expand/find-and-read operation within 3 seconds. Never wait on a full-page crawl before answering from visible content.
- **cost:** About $0.005–$0.03 per spoken exchange, dominated by realtime audio/model tokens; deterministic DOM extraction and scroll/click actions are negligible. Long-page indexing should be opt-in and background-priced.
- **security:** Send only the active tab's selected/visible semantic text by default, with domain and title, not cookies or raw page state. Keep extraction local until the user asks a question. Do not click links that navigate away, submit forms, send messages, or purchase without an explicit separate request. Show the active domain/title in the pendant response and log citations locally for audit.
- **missing:** A browser-extension event stream for active-tab changes, selection, visible DOM, and accessibility-tree updates—not just command polling.; A low-latency relay route binding one pendant conversation to one browser tab/session with strict tab affinity.; Mac/browser actions that can locate text, expand disclosure widgets, and return bounded cited excerpts as one atomic read operation.; Pendant response metadata for source domain/title and a short 'I could not access that section' state.; A privacy-preserving local redaction/classification layer for obvious secrets and payment fields before text reaches the realtime model.


## Changes it proposed to its own stack

### `browser-harness` — Add a durable browser-command lease/watchdog: each queued command gets issuedAt, leaseUntil, extensionConnectionId, tabId, actionClass, and retryOf. A Mac timer reconciles leases with /browser/status; on expiry it marks mutating commands execution_unknown (never replays), retries at most once for idempotent navigate/read/snapshot, and emits a signed receipt. On extension heartbeat, stale commands are not blindly replayed; the dashboard offers explicit discard/retry.
- **owner gets:** A disconnected Safari will no longer make the owner guess whether a logged-in page was read or a click occurred. Safe reads recover, while risky actions are honestly reported as unknown instead of duplicated.
- effort: Medium: browserBridge.js lease schema and reconciliation loop, extension heartbeat connection identity, receipt/dashboard rendering, and tests for sleep/reconnect races.  ·  risk: A navigation/read retry may observe changed content; label it as a retry and include timestamp. The main safety risk is duplicate mutation, prevented by never auto-retrying mutation classes. If the watchdog crashes, existing timeout behavior remains and commands can be manually discarded.
- cost: No meaningful API cost; a lightweight timer and a few persisted receipt fields. Small local storage growth per command.  ·  latency: Adds no foreground latency; expiry detection runs every 10–15 seconds and safe retries add up to one extension round trip.
- security: Keep page text and selectors local by default; use opaque command ids in relay alerts. Connection and tab ids prevent replaying a command into a newly opened unrelated tab.
- depends on: Extension heartbeat reconnect/session identity; Durable browser result receipts; Relay-to-pendant alert path; Dashboard command timeline


## What it asked for

_Nothing._
