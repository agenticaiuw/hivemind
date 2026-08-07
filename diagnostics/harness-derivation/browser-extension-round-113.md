# Harness derivation — browser-extension — round 113

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-extension live health** — At 2026-08-07T14:46Z the browser bridge is offline with 11 pending commands; only home-chrome is registered and offline. The persisted browser session file still lists three Safari tabs, so session presence is stale and must not be treated as live availability.
  - evidence: GET /browser/status returned online:false, home-chrome only, pendingCommands:11; GET /browser/sessions returned default/probe-form/probe-form2 with old tab IDs and lastUsedAt around 06:26Z.

## Capabilities it proposed

### "“Research this for me across my private browser tabs, my Mac files, and the public web; reconcile the answers and leave me a sourced brief without changing anything.”"
- **useful because:** No single node can answer this reliably: Safari can see authenticated material, the Mac can search local documents, and the relay can fetch public sources while the pendant gives one concise answer. Contradictions and stale private pages are surfaced instead of silently blended.
- **path:** pendant → browser-extension → mac-planner → mac-terminal → relay-realtime → dashboard
- **model tier:** Use a cheaper background text model for retrieval, normalization, and citation reconciliation; reserve realtime only to clarify the request and read the finished brief aloud.
- **latency:** A few seconds to acknowledge on the pendant; roughly 20–60 seconds for parallel collection and reconciliation, with partial results if one surface is offline.
- **cost:** Usually low: parallel local/browser extraction and relay web retrieval dominate; one background synthesis call, with no realtime model spent on the long research pass.
- **security:** Private page text and local file snippets must stay in the authenticated Mac/relay job context and be labeled by source and sensitivity; public sources must never be allowed to write into private sites. Read-only by default, no form submission or message sending. Show URLs/file paths, timestamps, and quoted evidence in the brief.
- **missing:** A durable cross-origin research job that fans out to authenticated browser origins, local file search, and public web retrieval; A common evidence capsule schema with source sensitivity, freshness, quote/hash, and contradiction links; A synthesis route that accepts heterogeneous evidence and emits a cited brief plus partial-failure status; A user-visible research workbench on the Mac/dashboard and a pendant audio summary

### "“Remember the useful facts from the private webpages I show you, so later I can ask the pendant ‘what did that page say?’—even after Safari is closed—and show me the exact source when I need to verify it.”"
- **useful because:** Today a logged-in browser page is effectively ephemeral: once the tab closes or the bridge disconnects, the owner cannot ask the pendant about a fact they previously saw without reopening the site. This gives them durable, source-grounded recall without retaining an indiscriminate transcript or depending on a live browser session.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Use a background text model at capture time to extract claims, entities, and short supporting quotes; use the cheaper retrieval model for later pendant questions. Use realtime only for the spoken interaction and never for bulk indexing.
- **latency:** Capture should complete within a few seconds after a page read; a pendant answer should begin within 1–2 seconds and provide the citation shortly afterward.
- **cost:** Low per page: extraction and embedding/indexing dominate, with small retrieval-and-answer calls later. Storage cost is primarily compact claim records and hashes rather than screenshots or full HTML.
- **security:** Private-page claims need per-source sensitivity labels, encryption at rest, retention/expiry, and an owner-visible delete control. Store minimal quoted evidence, not passwords, form fields, or entire pages. A later answer must distinguish cached historical evidence from current live data and offer to reopen the page for verification; no browser mutation is implied.
- **missing:** A private-page memory index that stores claim-level records with URL, tab/session provenance, capture time, freshness/expiry, and evidence quote/hash; A redaction and sensitivity pass that excludes credentials, hidden fields, and irreversible-form contents before persistence; A pendant query route that retrieves those claims and returns both a concise spoken answer and a dashboard citation bundle; Per-source deletion, export, and revocation semantics spanning the Mac store and relay cache


## Changes it proposed to its own stack

### `browser-harness` — Add a heartbeat-aware browser command circuit breaker and stale-session reconciler. Before dispatch, bind each command to a device heartbeat generation (extensionId, lastSeenAt, tabId/windowId); if the device is offline or the session's tab has not been observed in the latest heartbeat, quarantine the command as `awaiting_browser`, coalesce duplicate idempotency keys, and stop retrying it. On reconnect, revalidate tabs and replay only commands whose target still exists; expire the rest with a typed reason and preserve the original request/evidence. Expose queue counts by live, quarantined, coalesced, and expired state so the planner can tell the owner what is waiting rather than reporting repeated failures.
- **owner gets:** The owner will not get ten identical failed browser attempts or a false impression that a logged-in tab is still available. When Safari reconnects, useful work resumes against a verified tab; when it does not, the pendant can plainly say the browser is offline and what was preserved.
- effort: Moderate: extend browserBridge lease/dispatch state, browserSessions reconciliation, heartbeat generation tracking, and journal/dashboard summaries; add restart and reconnect tests.  ·  risk: A tab could disappear between heartbeat and dispatch, or a command could be quarantined longer than desired. Recover by revalidation immediately before replay, explicit manual retry, and retaining the original command payload; no action is silently discarded.
- cost: Negligible API cost; fewer failed 45-second waits and duplicate extension calls. Small local JSON/D1 state increase for queue state and heartbeat generations.  ·  latency: Offline requests return a fast queued/quarantined status instead of blocking 45 seconds; reconnect adds one heartbeat/tab validation before replay.
- security: Improves isolation by never replaying a command into an unverified tab/window or a newly attached browser device; payloads remain local and authenticated.
- depends on: chg-14accc01's existing request IDs/idempotency keys and browser session affinity; POST /browser/heartbeat and GET /browser/status; chg-16bc5dee's durable browser job runner (for persistence/replay)

### `browser-harness` — Add a client-side private-page capture boundary in the Safari extension: before any authenticated DOM text, screenshot, or form state leaves Safari, classify and redact credential-like values, hidden inputs, payment/account identifiers, and unrelated page regions; emit a compact signed evidence packet containing only the selected region, source URL, timestamp, and redaction manifest. Let the owner inspect and revoke individual packets from the dashboard, and propagate revocation to relay caches and derived claim indexes.
- **owner gets:** The owner can use browser-based memory and cross-device answers without having whole private pages, passwords, or unrelated personal data copied into the AI system. They get useful citations while retaining practical control over exactly what survives.
- effort: High: extension-side DOM/visual region classification, packet signing, redaction tests across real sites, encrypted storage, and revocation propagation through Mac, relay, and dashboard.  ·  risk: Over-redaction could omit a fact; under-redaction could leak sensitive data. Recover with visible redaction previews, conservative defaults, packet-level deletion, and a local-only fallback that refuses upload when classification is uncertain.
- cost: Moderate implementation and small storage overhead for manifests/signatures; lower downstream model and storage cost because packets are compact. No recurring cost beyond normal extraction/indexing.  ·  latency: Adds roughly 100–500 ms for DOM classification and packet construction on ordinary pages; visual pages may add more processing before an answer is returned.
- security: Substantially reduces private-data exposure and creates tamper-evident provenance. Requires careful key management and must never expose signing keys to page JavaScript.
- depends on: The browser extension's existing authenticated page extraction path; A durable evidence/claim index for retained packets; Dashboard controls for packet inspection and deletion; Relay cache invalidation and Mac-local storage synchronization


## What it asked for

_Nothing._
