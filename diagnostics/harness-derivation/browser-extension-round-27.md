# Harness derivation — browser-extension — round 27

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser_enqueue_command_impl** — The newly granted browser enqueue wrapper is still an unimplemented stub; even a harmless list_tabs request returns an implementation error, so authenticated browser work cannot currently be dispatched through this agent.
  - evidence: Called browser_enqueue_command_impl with command=list_tabs and empty deviceId; response: 'This tool was granted a schema but has no implementation yet. Report what you would have done with it.'

## Capabilities it proposed

### "“I’m looking at this—read the important parts and tell me what I should do.”"
- **useful because:** It turns the owner’s current private Safari context into a pendant-sized, cited answer without requiring them to copy URLs, identify tabs, or expose an entire logged-in page. The browser reads only on explicit voice request, then Mac/relay condense and retain a reviewable receipt.
- **path:** pendant → relay → browser → mac-bridge → dashboard
- **model tier:** Realtime for intent confirmation and the short spoken summary; a cheaper background model for long-page extraction, normalization, and citation packaging. Public cross-checks use web_search rather than the authenticated browser.
- **latency:** Acknowledge intent immediately; fresh tab resolution under 1 second, then 2–5 seconds for extraction and spoken answer. If the page is large, return a short first answer and continue citation packaging in background.
- **cost:** Usually one low-token realtime turn plus one cheap extraction/summarization call; roughly cents or less per request, dominated by authenticated-page text size. Metadata-only tab events cost effectively nothing.
- **security:** The page may contain credentials, health, financial, or work data. Send only the explicitly requested tab/selection, redact secrets, retain snippets and hashes briefly, bind results to the Safari session/tab, and show source URL/title. Never click, submit, send, or purchase as part of read; any follow-up mutation is a separate action.
- **missing:** A working browser enqueue implementation—the granted wrappers currently return an implementation error; Safari focus/navigation event protocol and zero-tab bootstrap behavior; Selection-aware extraction with redaction and short-lived provenance receipts; Pendant intent routing for deictic phrases ('this', 'here', 'the page')

### "“Save this page for my commute.”"
- **useful because:** The owner can turn a private logged-in page they are viewing into a small, spoken, offline queue without emailing themselves links, leaving a browser tab open, or asking the system to monitor the page. The pendant button or voice marks the current page; the browser captures the relevant content, the Mac produces a concise audio brief, and the relay syncs it to the pendant for playback later.
- **path:** browser → mac-bridge → relay → pendant → dashboard
- **model tier:** Use a cheap background model for extraction, cleanup, and audio preparation; use realtime only to acknowledge the clip and report when it is ready. No expensive model is needed for routine pages.
- **latency:** Acknowledge the clip in under 1 second; capture and queue it within 5 seconds. Audio preparation may continue in the background, with a notification when available. Playback must work offline after sync.
- **cost:** One inexpensive extraction/summarization call per clip plus speech synthesis; approximately a few cents for a normal article, dominated by page length and audio generation. Metadata-only clips should cost near zero.
- **security:** Authenticated pages may contain sensitive work, financial, or health information. Require an explicit button press or spoken command, capture only the current page and any selected region, redact credentials and hidden fields, encrypt the queue, expire items by default, and show title/source/retention in the dashboard. Never capture pages marked private or transmit content when the owner has paused browser sharing.
- **missing:** An authenticated browser clip command that captures the current tab or selected DOM region with provenance; A Mac-side encrypted clip store and background summarizer/audio generator; Relay-to-pendant queue synchronization with resumable transfer and offline playback; Pendant controls for save, skip, delete, and retention status; A privacy indicator and per-site capture policy in the dashboard


## Changes it proposed to its own stack

### `browser-harness` — Add an event-driven active-tab context channel and self-healing browser bootstrap. Safari extension emits a signed, minimal tab-focus event (tabId, origin/title, timestamp, optional user-selected text only) on focus/navigation, with page body withheld by default. Relay voice intents such as “read this page” resolve that tab and enqueue extraction; if no tab exists, the extension opens/attaches a tab and returns a typed 'ready' event. Persist short-lived context in the Mac workbench with provenance, redaction markers, and an explicit stale timeout; do not turn this into continuous page polling.
- **owner gets:** The owner can say “what am I looking at?” or “read this” from the pendant while already browsing, instead of fighting failed list-tabs/browser-page-access commands. It uses the browser’s private login, keeps the spoken answer short and sourced, and avoids uploading whole pages or silently watching them.
- effort: Medium: extension focus/navigation hooks and event POST, relay event schema and tab resolver, browser queue correlation, Mac workbench receipt and stale/error UI; add integration tests for zero-tab bootstrap and Safari restart.  ·  risk: Tab titles and selected text can contain secrets; minimize payload, redact obvious credentials, encrypt in transit, retain for minutes, and provide a pause/private-tab toggle. Focus events can be noisy or stale; debounce and require a fresh tab receipt before extraction. If bridge is offline, say so and retain no queued page content.
- cost: Low API cost: metadata events are local/relay bookkeeping; one extraction call only when asked. Small D1/R2 receipt storage; no continuous page-body transfer.  ·  latency: Focus event under one poll interval; on-demand read typically adds one extension round trip (~1–3 s), with no cost when the owner does not ask.
- security: Improves least-data handling versus sending full pages by default, but introduces a new metadata path. Scope events to the registered Safari device, bind tab IDs to session leases, redact selected text unless explicitly requested, and expose an always-visible pause indicator.
- depends on: A functioning browser command enqueue implementation (all currently granted enqueue wrappers still return an implementation error); Safari extension event hook and authenticated POST endpoint; Existing request-id/tab-affinity/result receipt work (chg-14accc01)


## What it asked for

_Nothing._
