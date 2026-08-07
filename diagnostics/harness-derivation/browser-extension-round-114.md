# Harness derivation — browser-extension — round 114

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser bridge health** — Safari is not currently registered/online. Live /browser/status reports only offline home-chrome, 11 pending commands, while /browser/sessions retains three stale tabs (including time.is and selenium web-form). The Mac bridge itself is online.
  - evidence: GET /browser/status 200: online=false, devices=[home-chrome offline], pendingCommands=11; GET /browser/sessions 200: stale tab records; GET /ops/status 200: macBridgeOnline=true.

## Capabilities it proposed

### "“Save this page for me as a reminder” (or “turn the important date on the page into a reminder”)."
- **useful because:** Only the browser has the owner’s authenticated page and only the Mac can create a durable native reminder; the pendant provides the in-the-moment trigger. This turns a logged-in webpage into an actionable reminder without copying URLs or exposing page contents to a public search service.
- **path:** browser-extension → mac-planner → relay-realtime → unified
- **model tier:** Use the realtime model only to resolve the short spoken intent and confirmation; use a cheaper background text model to extract candidate title/date from the browser excerpt. Browser extension reads the active tab, Mac creates the reminder, relay returns a concise spoken receipt.
- **latency:** Target 5–10 seconds end to end: 1–2 seconds for page extraction, 2–6 seconds for parsing and native reminder creation. If extraction or date is ambiguous, return candidates rather than guessing.
- **cost:** About $0.005–$0.03 per invocation, dominated by background extraction; realtime usage is limited to the short utterance and result.
- **security:** Page text may contain private work/financial/health data. Send only a bounded, user-selected excerpt and URL to the local Mac parser by default; never upload the whole page to relay. Creating a reminder is reversible but should speak back the exact title/date/list before committing when extraction is ambiguous. Do not submit forms or send page data elsewhere.
- **missing:** A browser action that returns active-tab URL/title plus bounded semantic text selection in one typed result; A local extraction pipeline that identifies dates and preserves source citation; A cross-surface handoff linking browser session identity to POST /reminders and a spoken receipt

### "“Remember this private page detail for later” — for example, the return deadline, tracking number, policy limit, or appointment date currently visible in my logged-in browser."
- **useful because:** Today a fact behind an existing browser login disappears when the tab closes, and public web search cannot see it. This would let the owner capture one useful fact into their personal memory without manually copying it, then ask the pendant about it later even when the browser is closed.
- **path:** browser-extension → mac-planner → relay-realtime → unified → faculty-perception → faculty-judgement
- **model tier:** Use the realtime tier only for the short spoken capture request and immediate response. Run local extraction, normalization, deduplication, and expiry classification on the Mac with a cheaper background model; use the relay only to synchronize an encrypted memory reference when the Mac is unavailable.
- **latency:** Capture should complete in 3–8 seconds. Later recall should answer in under 2 seconds if the Mac/relay memory index is warm. If the page has multiple plausible facts, return a compact candidate list instead of silently choosing.
- **cost:** Approximately $0.003–$0.02 per capture, dominated by local/background extraction; routine recalls should be near-zero model cost using indexed structured facts.
- **security:** The source page may contain highly sensitive personal or work information. Extract only the requested fact and a short citation, never the full DOM; keep raw text and cookies on the Mac/browser boundary. Store an encrypted structured fact with source URL, captured time, confidence, and expiry; relay synchronization should contain ciphertext or a capability reference, not plaintext. Do not capture passwords, payment credentials, or session tokens, and clearly identify the source when recalling a fact.
- **missing:** A browser-extension command for owner-selected text or a bounded semantic extraction anchored to the active tab; A local private-fact schema with provenance, confidence, expiration, correction, and deletion semantics; A memory index shared between Mac and relay that can answer pendant queries without replicating raw page content; A cross-surface capture receipt and later citation mechanism


## Changes it proposed to its own stack

### `browser-harness` — Add health-aware browser command dispatch: every queued command carries an extension/device lease and session tab identity; when heartbeat goes offline or tab identity is stale, immediately mark the command unavailable (no 45s wait), quarantine it by session, coalesce duplicate reads/navigations, and expose a reconnect/resume operation that replays only safe idempotent reads after a fresh heartbeat. Purge or explicitly label the 11 currently pending commands rather than letting them execute against a later unrelated tab.
- **owner gets:** The pendant will stop hanging after Safari closes or sleeps, and reconnecting Safari will not accidentally run old clicks/types or navigate to the wrong page. Reading can resume safely while mutations remain visibly pending for the owner.
- effort: Medium: browserBridge queue state machine, heartbeat lease validation, session identity checks, duplicate coalescing, and dashboard/receipt states; add failure/reconnect tests.  ·  risk: A heartbeat race could incorrectly quarantine a command or lose a safe read. Recover by retaining quarantined payloads with expiry and an explicit replay endpoint; never replay browser_type/click/select/submit automatically.
- cost: Negligible API cost; small local JSON/state overhead (<100 KB).  ·  latency: Offline failure returns in <1 s instead of a 45 s timeout; online commands unchanged.
- security: Improves safety by preventing stale commands from reaching a future logged-in tab. Keep URL/tab metadata and quarantined mutation payloads local; redact typed text from receipts.


## What it asked for

_Nothing._
