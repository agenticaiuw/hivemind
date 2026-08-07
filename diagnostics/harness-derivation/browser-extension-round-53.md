# Harness derivation — browser-extension — round 53

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser bridge** — As of this round, /browser/status reports both registered browser devices offline and 3 pending commands; no tab/session is available. The Mac bridge itself is online, but its required Accessibility and Screen Recording permissions are missing, so browser recovery may need the extension/Safari rather than computer-use.
  - evidence: GET /browser/status HTTP 200 and GET /ops/status HTTP 200 live responses

## Capabilities it proposed

### "“Read this private page to me, but remember only the decisions and dates I explicitly ask you to keep.”"
- **useful because:** The browser is the only node that can see the owner's authenticated page, while the pendant is the only node that can deliver a hands-free spoken digest. This gives the owner an ephemeral private-page reading mode with deliberate memory boundaries instead of leaking page content into durable context.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard-ux
- **model tier:** Use a cheap extraction/summarization model for page chunks and a fast realtime model only for the pendant conversation; use local TTS/audio queue for replay rather than spending realtime tokens.
- **latency:** Start speaking within 3 seconds of extraction; continue chunked playback while later sections are summarized. Stop immediately if the browser session disappears.
- **cost:** Low to moderate per invocation; dominated by page extraction and summary tokens, with local TTS preferred. No cost for memory unless the owner explicitly saves a fact.
- **security:** Page text must stay ephemeral, be redacted before relay logging, and be deleted after playback/session TTL. Any request to save a decision/date becomes a separate, spoken confirmation plus a cited memory item; never infer permission from 'remember only' without the explicit item.
- **missing:** A streaming private-page extraction contract from browser-extension to relay with chunk IDs and sensitivity labels; An ephemeral audio queue that can accept browser chunks and expire them automatically; An explicit pendant phrase/button for 'save that' which captures only the last cited fact, not the page; Dashboard UI showing what was read, what was discarded, and what (if anything) was saved

### "“While I browse, quietly understand the private page I’m on and speak up only when you spot a deadline, fee, contradiction, or decision I might miss.”"
- **useful because:** Today the owner must stop and explicitly ask the assistant to inspect each authenticated page. This would make the pendant a real-time second set of eyes over private web sessions: it could notice a hidden renewal term, changed total, conflicting date, or required action while the owner is already reading, without narrating every page or sending anything.
- **path:** browser-extension → relay-realtime → pendant → dashboard-ux
- **model tier:** A local extension-side extractor should detect page structure and candidate risk signals cheaply; a background text model should rank and explain candidates. Use the realtime model only when a high-confidence alert needs immediate spoken delivery.
- **latency:** DOM/semantic candidate detection under 300 ms after navigation or meaningful mutation; speak a concise alert within 2 seconds for high-confidence findings. Debounce scrolling and repeated mutations.
- **cost:** Low during ordinary browsing if extraction, hashing, and thresholding run locally; model cost is incurred only for changed regions or candidate alerts. Audio cost is dominated by occasional TTS, not continuous transcription.
- **security:** Private page text must remain local until a candidate region is explicitly selected for analysis, then be sent as the smallest necessary excerpt with URL, account, and sensitive-field redaction. Never announce secrets or expose page contents to the dashboard by default. Provide an always-visible pause switch and a per-site exclusion list.
- **missing:** A Safari extension event stream for navigation and meaningful DOM-region mutations, not just request/response polling; A local semantic-risk detector for deadlines, money, contradictions, and required decisions; A relay protocol for deduplicated candidate excerpts with sensitivity labels and confidence; Pendant alert interruption policy, mute/pause controls, and a dashboard showing the exact cited region after each alert


## Changes it proposed to its own stack

### `browser-harness` — Add an explicit browser-command lease and reconciliation protocol. Every queued browser command gets createdAt, expiresAt, tab/session fingerprint, and a monotonic attempt number. When the extension disappears, the queue marks commands suspended rather than leaving them pending; on reconnect it returns a typed reconciliation (expired, tab changed, safe-to-retry, or requires re-read) and automatically discards expired read results. The dashboard and pendant should say exactly which commands were not run, while idempotent reads may be retried only against the same tab/session fingerprint.
- **owner gets:** The current browser bridge can strand commands when Safari goes offline (there are already three pending now), then potentially replay an old click or type after the owner reconnects. This makes browser automation predictable: no surprise stale interaction, no silent loss, and a clear 'nothing happened' answer.
- effort: Medium: queue schema/state machine, heartbeat-driven reconciliation, extension result metadata, dashboard status, and tests for disconnect/reconnect/tab replacement.  ·  risk: A conservative lease may expire a long page read and require retry; recovery is explicit retry from the dashboard or pendant. Never auto-retry mutation actions; preserve their payload only as encrypted-at-rest pending state until expiry.
- cost: Negligible API cost; small D1/local JSON metadata and one heartbeat update per command.  ·  latency: No added latency while online; reconnect adds one reconciliation round trip before safe reads resume.
- security: Reduces replay risk and prevents actions targeting a new tab. Do not log typed text or page contents in reconciliation metadata; use hashes and sensitivity labels.
- depends on: browser extension heartbeat must expose a stable device/tab/session fingerprint; existing browser request IDs/result receipts


## What it asked for

_Nothing._
