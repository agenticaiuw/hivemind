# Harness derivation — browser-extension — round 61

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-extension live availability** — Safari extension is currently offline (GET /browser/status online:false) with four pending commands; browser session records still reference three stale tabs, including time.is/UTC and test forms. A POST /execute browser_read_page request timed out after 20 seconds, confirming the queue cannot currently complete work.
  - evidence: GET /browser/status returned online:false and pendingCommands:4; GET /browser/sessions returned stale tab IDs; POST /execute with actions:[{type:browser_read_page,sessionId:default}] returned no response within 20s.

## Capabilities it proposed

### "“What does this page mean for me?” (or “compare these two numbers”) while I’m looking at a private Safari page."
- **useful because:** The pendant can answer about the exact authenticated page the owner is viewing without asking them to copy text, expose it publicly, or navigate away. It combines the pendant’s voice trigger, relay routing, Mac planning, and Safari’s logged-in DOM; citations and a compact spoken answer make it useful while walking or multitasking.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Realtime only for the short voice turn and clarification; a cheaper background model extracts/normalizes the page and compares values, with the realtime tier receiving only the evidence bundle and composing the spoken answer.
- **latency:** Target 3–6 seconds: 0.5s route, up to 2s browser snapshot/extraction, 1–3s evidence synthesis and speech. If Safari is unavailable, say so immediately rather than pretending the page was read.
- **cost:** Roughly $0.01–$0.05 per query depending on page size and whether synthesis needs a second pass; browser I/O and context tokens dominate, not the short voice response.
- **security:** Private DOM text, URL, and selected screenshot regions leave Safari for the relay/Mac pipeline; redact passwords, tokens, hidden inputs, and unrelated tabs. Do not execute clicks, navigation, or form submission from this capability. Show the source URL and quote/hash the relevant snippets in the answer; require no confirmation for read-only capture.
- **missing:** A working browser command enqueue implementation (all currently granted enqueue wrappers still return implementation errors).; A live Safari heartbeat/tab association; current /browser/status is offline with tabCount unavailable and four stale pending commands.; A first-class current-tab/session selector plus bounded extraction of the visible/selected region, rather than relying on stale session records.; A relay-to-browser request correlation and evidence envelope that can return citations to the voice turn.

### "“Let me ask about any logged-in webpage from my pendant, but prove to me afterward exactly what left Safari and automatically erase the captured page data when the answer is delivered.”"
- **useful because:** Today the browser can potentially read private pages, but the owner cannot obtain a trustworthy, human-readable privacy receipt or a guaranteed short-lived data path. This would make authenticated browser assistance safe enough for sensitive work: the owner gets an answer plus a verifiable record of the URL scope, DOM regions, redactions, hashes, retention deadline, and deletion result.
- **path:** pendant → browser-extension → mac-planner → relay-realtime
- **model tier:** Use a small background model for deterministic field classification and receipt generation; use realtime only to handle the owner’s spoken question and read the concise answer. Do not send raw page text to the realtime model unless the owner’s query requires it.
- **latency:** 4–8 seconds for the answer and an additional 1–2 seconds to seal the receipt and delete transient evidence. If deletion cannot be confirmed, explicitly report that instead of claiming success.
- **cost:** Approximately $0.01–$0.04 per invocation; browser capture and encrypted transient storage dominate, with model cost limited by a redacted evidence excerpt.
- **security:** The extension must classify and remove passwords, cookies, hidden inputs, payment fields, access tokens, and unrelated frames before upload. Keep raw DOM/screenshot only in encrypted, memory-bounded transient storage; bind each receipt to a request ID and content hash; expose deletion status without retaining page contents. This is read-only and must never click, type, or submit.
- **missing:** A content-security boundary inside the Safari extension that performs redaction before any browser result is posted.; A typed evidence/retention receipt format understood by the Mac planner and relay.; An ephemeral encrypted store with confirmed deletion and bounded failure recovery.; A pendant-visible or spoken receipt summary, including what was excluded and whether deletion succeeded.


## Changes it proposed to its own stack

### `browser-harness` — Add a browser-bridge liveness and recovery controller: distinguish extension offline, tabless, and command-stuck states; expire the four currently pending commands into a durable dead-letter record; reject new waits immediately when no heartbeat has arrived; and, on the next Safari heartbeat, replay only idempotent read commands with their original request/session IDs. Expose GET /browser/status fields lastHeartbeatAge, pendingByState, and recoveryAction so the planner can give an honest spoken status.
- **owner gets:** Private-page requests stop hanging for 20–45 seconds or silently using stale tabs. The owner hears “Safari is offline; I’ll retry when it returns” and gets the result automatically when Safari reconnects, instead of wondering whether a logged-in action happened.
- effort: Moderate: browserBridge state machine plus heartbeat bookkeeping, dead-letter persistence, and planner error mapping; add integration tests for offline→online and duplicate result delivery.  ·  risk: A replayed read can still observe a changed page, so attach capture time and mark it as a fresh observation. Never replay click/type/select/submit actions. If persistence is corrupt, clear only dead-letter metadata and leave the browser session store untouched.
- cost: Negligible API cost; small local JSON/SQLite growth bounded by retention (for example 100 records).  ·  latency: Fast failure in under 1 second while offline; normal online reads unchanged; reconnect replay adds one heartbeat interval.
- security: Dead-letter records must contain command type/session ID but not page text, form values, cookies, or screenshots; redact URLs where configured and delete records on retention expiry.
- depends on: A functioning extension command enqueue path, currently missing despite the granted wrappers.; The existing GET /browser/poll and POST /browser/result/:commandId protocol.; A heartbeat emitted by the real Safari extension with a stable device/session identity.


## What it asked for

_Nothing._
