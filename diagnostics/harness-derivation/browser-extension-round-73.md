# Harness derivation — browser-extension — round 73

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser command queue liveness** — GET /browser/status reports only offline home-chrome with 5 pending commands; GET /browser/poll returns browser_fc12217f... navigate command claimed by home-chrome at 12:26:24 with attempts=6, while /browser/sessions contains stale Safari tab records. The queue can retain/retry work on an offline device and misroute commands.
  - evidence: GET /browser/status and GET /browser/poll responses on 2026-08-07

## Capabilities it proposed

### "“What am I looking at?” (or “save this for later”) while a page is open on my Mac."
- **useful because:** The pendant can turn an unstructured moment at the screen into an immediate, cited answer or a saved follow-up without the owner copying a URL or describing the page. Safari supplies authenticated page content, the Mac ties it to the active tab and can save an artifact, and the relay returns a short spoken response.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision
- **model tier:** Realtime model only for the short intent/response turn; use a cheaper background model for page extraction, citation normalization, and optional saved-note indexing.
- **latency:** Acknowledge from the pendant within 300 ms, extract the active page within 5 s, and speak a concise answer within 8 s. If the page is unavailable, say so immediately rather than waiting for a timeout.
- **cost:** About one realtime turn plus 1–3k extracted page tokens; roughly $0.01–$0.05 depending on model and page size. Cost is dominated by sending page text, so cap extraction and omit unchanged boilerplate.
- **security:** Authenticated page text is sensitive and must stay within the existing browser-to-Mac/relay path, with source URL/title and extraction timestamp attached. Do not include passwords or hidden form values. “Save this” can create a local note, but sending, submitting, purchasing, or sharing remains outside this capability.
- **missing:** A reliable active-tab command path and device-aware queue recovery (current enqueue wrappers are still unimplemented and the live queue has commands claimed by offline home-chrome); A pendant event carrying the spoken intent plus correlation ID to the browser session; A small page-to-brief artifact store with citations and optional local-note export

### "“Put this page in context.” While I’m on any logged-in Safari page, use the text I’m viewing to find the relevant local files, notes, and calendar items on my Mac, then give me a short spoken explanation of how they relate and leave a cited context card beside the page."
- **useful because:** Today the browser can see the private page and the Mac can see local material, but neither can join those two contexts from a single natural request. This would answer the owner’s real question—why this page matters to me—without copying text, searching folders manually, or losing the source provenance.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-terminal → mac-vision
- **model tier:** Use the realtime tier only to interpret the short voice request and deliver the answer; use a cheaper background model for entity extraction, local-file/calendar retrieval, deduplication, and citation linking.
- **latency:** Acknowledge in under 500 ms; capture the active page and selected/visible text in 3 seconds; retrieve and rank local context in 8 seconds; speak the answer in under 12 seconds. Leave the durable context card asynchronously if indexing takes longer.
- **cost:** Approximately $0.02–$0.08 per invocation, dominated by page text plus retrieved local snippets sent to the summarizer; cap both inputs and hash previously seen page regions to avoid repeat cost.
- **security:** This joins two sensitive domains, so raw page contents and local snippets must remain on the owner’s Mac whenever possible; the relay should receive only the minimum extracted passages needed for speech. Never upload passwords, hidden form fields, or unrelated files. The context card must record URL, timestamp, file paths, and quoted evidence, and default to local-only storage.
- **missing:** An extension operation that returns the active tab’s visible/selected text with stable DOM anchors and page fingerprint, rather than only generic page extraction; A Mac-side retrieval adapter that searches local Notes, files, and Calendar and returns bounded snippets with provenance; A cross-surface correlation protocol linking the pendant utterance, browser capture, Mac retrieval, and final context card; A local context-card renderer or sidecar writer that can place the result beside the active page without sending or submitting anything


## Changes it proposed to its own stack

### `browser-harness` — Add device-aware lease fencing and dead-command recovery to the browser bridge: commands carry target device plus lease token/expiry; heartbeat liveness is checked before claim; a command claimed by an offline or silent device is automatically returned to the queue (or marked unavailable) after a short lease, with bounded retry and an operator-visible reason. Never deliver a command intended for Safari to the unreporting home-chrome registration. Reconcile stale browser sessions against current heartbeats and expose queue age/device/lease in status.
- **owner gets:** A browser request will either reach the owner's real logged-in Safari or fail clearly instead of hanging for 45 seconds, being silently claimed by a dead device, or leaking work to the wrong browser registration. Returning later can safely resume queued work.
- effort: Moderate: extend browserBridge command schema and poll/claim transaction, add heartbeat-based lease sweeper and status fields, plus integration tests for offline-device claims and Safari reconnect.  ·  risk: A transient Safari disconnect could cause a command to be requeued and executed twice unless idempotency keys and result deduplication are enforced. Recovery: lease token fencing, idempotent command IDs, and explicit terminal status after retry budget.
- cost: Negligible API cost; one lightweight lease sweep per minute or on poll/heartbeat. No new hardware cost.  ·  latency: Adds at most a heartbeat/liveness check (milliseconds); avoids the current 45-second timeout and repeated dead-device retries.
- security: Improves isolation by preventing cross-device command delivery and stale-session use. Device IDs and lease metadata remain server-side; no page contents leave the existing bridge.
- depends on: Existing browser command request IDs/idempotency and tab/session affinity (chg-14accc01); Browser heartbeat/status endpoints; Durable browser job runner (chg-16bc5dee)


## What it asked for

_Nothing._
## Its own summary

Discovered a live queue defect: Safari is no longer online, only the never-used home-chrome registration is offline, yet five commands remain pending and one navigate command has been claimed by home-chrome six times. Browser sessions are stale Safari records. I recorded this and proposed device-aware lease fencing, liveness recovery, and wrong-device isolation. I also proposed a genuinely cross-surface “What am I looking at?” pendant workflow that reads the active authenticated Safari page and answers/saves it with citations.

**Biggest unknown:** The browser enqueue implementation is still unavailable: all granted enqueue wrappers return an implementation error. I still need a functioning POST /execute-to-extension path (or working enqueue tool), a reliable Safari heartbeat/tab presence, and confirmation of the exact active-tab event/correlation contract before I can perform a real authenticated-page task. I do not need more owner preference context this round.

