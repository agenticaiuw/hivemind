# Harness derivation — browser-extension — round 84

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "What on this private page deserves my attention? Compare the visible numbers, labels, and dates, explain the anomaly in plain language, and point me to the exact place in the page—without changing anything."
- **useful because:** The owner can ask about a logged-in dashboard or document, but today no single surface combines the browser's authenticated DOM with a local visual view and produces a precise, cited answer. This would make the pendant useful for dense private pages, charts, and unfamiliar portals without requiring the owner to read or copy the page manually.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** Use a small local/cheap vision-and-text model for DOM normalization, arithmetic, and anomaly detection; reserve realtime for the short spoken exchange. Keep private page analysis on the Mac whenever possible.
- **latency:** Return a spoken answer in under 8 seconds for one page or chart; allow up to 20 seconds for a multi-panel dashboard. No mutation should be attempted.
- **cost:** Near-zero relay cost when analysis runs locally; otherwise one compact multimodal request, typically a few cents. The dominant cost is transmitting a cropped, redacted visual region if local vision is unavailable.
- **security:** Only inspect the active tab after an explicit spoken request. Redact passwords, tokens, account numbers, and off-screen form fields before any model upload; prefer DOM text and local screenshot crops. Return URL/title/locator evidence, not a full-page transcript. This is read-only and must never click, type, or submit.
- **missing:** A browser-to-local-vision adapter that pairs the active tab's DOM/accessibility tree with a screenshot crop and stable element locators; A local redaction and numeric-consistency analyzer for private page content; A cited answer format that can identify a DOM selector or screen rectangle and let the browser highlight it without mutating the page; A unified pendant intent that routes the request to browser-extension plus mac-vision instead of treating them as separate tools


## Changes it proposed to its own stack

### `browser-harness` — Add an offline-safe browser command lease/recovery controller: when the extension heartbeat disappears, stop assigning new commands, mark in-flight commands as suspended (not failed), and expose a reconnect handshake that reports deviceId, tab/session validity, and the last acknowledged idempotency key. On reconnect, replay only unacknowledged read/extract steps, expire commands whose tab/session no longer matches, and move orphaned commands into a visible dead-letter queue with reason and recovery action. Add a queue-drain endpoint and dashboard health fields so the current 7 pending commands cannot remain invisible indefinitely.
- **owner gets:** A spoken browser request will not hang for 45 seconds or silently vanish when Safari sleeps, the extension restarts, or a tab closes. When the owner returns, private work resumes from the last confirmed page read instead of duplicating clicks or losing the result, while stale commands are clearly identified rather than applied to the wrong tab.
- effort: Medium: browserBridge lease state machine and reconnect protocol, browserSessions validation, persistence for suspended/dead-letter commands, plus dashboard/relay status plumbing and crash/restart tests.  ·  risk: A replayed read could be duplicated, and a tab may have changed while offline. Restrict automatic replay to idempotent navigation/read/extract with URL/session checks; never replay click/type/select/submit automatically. Recovery is to inspect the dead-letter record and rerun explicitly. No approval gate is introduced.
- cost: Negligible API cost; a few kilobytes of local queue metadata and occasional heartbeat/reconnect traffic.  ·  latency: Normal online commands unchanged; reconnect adds one handshake round trip, while offline requests return suspended status immediately instead of waiting 45 seconds.
- security: Preserves authenticated data on the Mac; dead-letter records must redact page text and form values, storing only command type, URL hash, session/tab IDs, timestamps, and reason. Device identity and idempotency keys prevent cross-device replay.
- depends on: chg-14accc01's existing request IDs/idempotency keys and tab/session affinity; chg-16bc5dee's eventual durable job runner for long-lived persistence; A functioning Safari extension heartbeat/reconnect path


## What it asked for

_Nothing._
