# Harness derivation — browser-extension — round 28

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser bridge liveness** — The browser bridge is currently offline despite the Mac and relay being online. /browser/status reports only the stale home-chrome registration, online=false, and 2 pending commands; /browser/sessions contains only old tabs from 2026-08-07. Do not treat those sessions as live authenticated Safari access.
  - evidence: GET /browser/status returned online=false with home-chrome tabId null and pendingCommands=2; GET /browser/sessions returned stale time.is and selenium/httpbin sessions; GET /ops/status reported browser online=false.

## Capabilities it proposed

### "“What am I looking at?” or “remember this page and remind me what it said later.”"
- **useful because:** This makes the private browser session a conversational extension of the pendant: the owner can get a concise answer about the authenticated page currently in front of them, then leave and continue by voice without reopening or explaining the context. It is meaningfully different from public web search because only Safari has the owner's logged-in page and session.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** Use the cheap browser extraction/normalization path first; mac-planner gpt-5.6-luna only for cross-page reasoning or follow-up planning; relay-realtime gpt-realtime-2.1 only to interpret the spoken request and speak the short answer. Persist a small page-handoff artifact in the relay or Mac store, not the full page by default.
- **latency:** 2–4 seconds for title/URL/selected readable text, under 8 seconds for a concise synthesis; offline bridge should say it cannot see the page rather than hallucinating. A later voice follow-up should resolve the handoff artifact in under 1 second before any new extraction.
- **cost:** Typically <$0.01 per request when extraction is deterministic and realtime only speaks; roughly $0.02–$0.08 when gpt-5.6-luna must reconcile a long or multi-tab page. Dominant costs are model synthesis and repeated page text, so cap extracted text and reuse the handoff artifact.
- **security:** The page may contain private financial, medical, or work data. Send only the selected readable region and URL metadata over the local bridge; redact password/input values and obvious secrets; never store a screenshot or full DOM unless explicitly requested. Reading and creating a local handoff are reversible and allowed by the owner; clicking, sending, submitting, or purchasing remains a separate action and must stop with an exact preview.
- **missing:** A browser command that targets the owner's active Safari tab and returns a typed, bounded extraction with URL/title/tabId and redaction metadata (the current bridge is offline and only stale sessions are listed).; A durable, expiring page-handoff store keyed to the pendant conversation, with source URL/tab/session, extracted snippet hashes, timestamp, and follow-up invalidation when the tab navigates.; Relay-to-Mac routing for a voice utterance that can resolve the handoff first, then invoke browser extraction, and return a one-sentence spoken result plus a citation/link on the Mac dashboard.; A bridge health/recovery path that detects stale heartbeats, wakes or prompts the Safari extension, and clears orphaned pending commands without replaying them.

### "“Read this page to me as I walk,” or “When I press the pendant button, read the paragraph I’m currently viewing and let me ask follow-up questions.”"
- **useful because:** The owner can consume private, logged-in browser content hands-free instead of copying text, taking screenshots, or losing their place. The browser contributes the exact viewport/selection, the pendant supplies a physical context cue and audio destination, and the relay keeps the conversation alive while the Mac remains unattended. This is a distinct multimodal handoff: it follows the owner's reading position rather than merely checking a page or producing a static summary.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** Use deterministic DOM/selection extraction and local text chunking by default; use a cheaper background text model only to clean headings or resolve page structure. Use realtime solely for low-latency spoken follow-ups and audio streaming, not for summarizing the whole document.
- **latency:** Button-to-first-audio under 1.5 seconds for a selected paragraph and under 3 seconds for the visible viewport. Continue in 10–20 second chunks with interruption support; a follow-up question should begin acknowledgment within 500 ms and answer within 3 seconds.
- **cost:** About $0.005–$0.03 per paragraph or viewport, dominated by speech generation; deterministic extraction and local chunking are nearly free. Reuse extracted chunks and avoid sending the entire DOM on every button press.
- **security:** Authenticated pages may contain confidential work, health, or financial information. Send only the current selection/viewport text, page title, URL, and a short-lived handoff token; exclude password fields, hidden DOM, cookies, and unrelated tabs. Store no audio or text beyond an expiring buffer unless the owner explicitly asks to save it. Reading is allowed without asking; any follow-up action such as clicking, sending, or submitting remains separate and must stop before the irreversible step.
- **missing:** A browser-extension event that reports the active tab's selection, viewport text, scroll position, and a stable page revision when the pendant button is pressed.; A low-latency relay audio queue that can stream extracted chunks to the pendant, interrupt playback, and resume at a paragraph boundary.; A short-lived cross-surface reading-session token linking pendant button events, the browser tab, and the Mac planner without exposing page contents in global prompt context.; A page-change/scroll reconciliation protocol so follow-up questions refer to the exact passage last heard rather than stale text.


## Changes it proposed to its own stack

### `browser-harness` — Add a browser-bridge liveness and recovery controller. Track per-device heartbeat age, extension version, tabCount, command lease, and pending-command age; mark a device stale after a bounded interval, cancel or quarantine orphaned commands, and expose a user-visible “reopen/enable Safari bridge” action. On the next heartbeat, reconcile command leases by idempotency key so a late result cannot execute twice. Retain stale authenticated sessions as metadata only, never claim they are live.
- **owner gets:** Browser requests will fail clearly and recoverably instead of hanging for 45 seconds or silently using yesterday's tab. The owner can resume a logged-in workflow after Safari sleeps, an extension restart, or a laptop wake without losing which page/task was in progress.
- effort: Medium: bridge state machine and lease persistence in the Mac agent, a small extension heartbeat/reconnect change, dashboard status card, and integration tests for sleep/restart/late-result races.  ·  risk: A command could be quarantined while the extension is merely slow, or a reconnect could surface an old tab. Use generous heartbeat grace, explicit stale states, command expiry, and require a fresh tab metadata heartbeat before dispatching mutations. Recovery is retrying the read; never auto-retry a high-impact action.
- cost: Negligible API cost; a few kilobytes of local state and one lightweight heartbeat per device interval. Engineering cost is primarily race-condition testing.  ·  latency: Healthy commands unchanged. Stale detection is immediate from heartbeat age; recovery adds at most one reconnect interval, while preventing the current 45-second timeout experience.
- security: Improves security by preventing commands from being delivered to an unknown/stale device and by avoiding replay after reconnect. Do not log page contents or cookies; persist only device and command metadata.
- depends on: An extension heartbeat that reports a stable device identifier and tab metadata; A typed command idempotency key/lease (can be implemented without blocking the owner's maximum-access policy); A dashboard or pendant error path that can tell the owner how to reopen the bridge


## What it asked for

_Nothing._
