# Harness derivation — mac-planner — round 113

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac/browser live state** — Mac local agent is reachable and relay bridge online, but browser extension is offline with 9 pending commands; computer-use loop disabled, Accessibility and Screen Recording ungranted. Newly granted mac_read_sources and mac_readonly_inspect are schemas without implementations, so they cannot yet read Calendar/Mail or inspect running apps/tabs.
  - evidence: GET /ops/snapshot returned 200: relay macBridgeOnline=true, browser online=false/pendingCommands=9, accessibility trusted=false, screenRecording granted=false, computerUse loopEnabled=false; direct calls to both newly granted tools returned 'schema but has no implementation yet'.

## Capabilities it proposed

### "If the browser is disconnected, keep my request moving: use public web access where safe, queue private-account work until Safari reconnects, and tell me exactly what is waiting instead of silently failing."
- **useful because:** Today a spoken request can spend 45 seconds timing out and leave nine opaque browser commands pending. The owner should get useful public findings immediately, while authenticated work is preserved and resumed rather than retried dangerously or lost.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use the realtime tier only to acknowledge and classify the request; use a cheaper background model for extraction, deduplication, retry scheduling, and the reconnect digest.
- **latency:** Acknowledge within 2 seconds; public fallback results within 15 seconds; private queue status immediately and resume after a heartbeat, with exponential backoff rather than 45-second blocking attempts.
- **cost:** Low per request: one short realtime turn plus background extraction; dominant cost is public-page fetch/extraction, not the health checks or queue reconciliation.
- **security:** Never send authenticated URLs, cookies, or page content to the public fallback. Classify each step as public or private before dispatch; private steps remain on the Mac/Safari bridge. Require explicit confirmation before any queued irreversible action executes after reconnect. Surface stale/duplicate command IDs and receipts.
- **missing:** A durable dispatcher that partitions a plan into public and authenticated steps and chooses Cloudflare/public versus Safari/private execution; A reconnect reconciler that marks the existing 9 pending commands stale or resumable by idempotency key and emits one concise digest; Working implementations for mac_read_sources and mac_readonly_inspect, or equivalent read-only local routes; Browser extension heartbeat/polling restored on the owner's Safari/Chrome

### "When my meeting ends, make me a private follow-up pack: collect the notes and files I touched, summarize decisions and open questions, identify promised follow-ups from my Mail and calendar context, and leave drafts/reminders for me to review—never send anything."
- **useful because:** The owner loses the transition between conversation and execution. A wearable-triggered, Mac-grounded closeout would turn scattered notes, files, and email into a reviewable next-step list without requiring them to remember to ask.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use a background text model after the meeting for extraction and deduplication; use realtime only if the pendant needs to announce that the pack is ready or ask one short clarification.
- **latency:** Detect the end within 2 minutes of the calendar event; produce a first pack in 60 seconds, then enrich it asynchronously. Keep all proposed sends/edits in review state.
- **cost:** One bounded background summarization per meeting plus cheap local reads; cost dominated by the amount of selected note/mail text, capped before upload.
- **security:** Only inspect apps/files/tabs touched during the meeting window and explicitly allowed sources; redact unrelated mail and secrets. Keep drafts local, show source links/snippets and confidence, and require confirmation before creating external mutations or sending messages.
- **missing:** A meeting-window provenance collector that records touched files, active app/tab metadata, and note destinations without screen recording; A post-meeting extraction pipeline joining Calendar/Mail/local notes/browser citations with strict time and source bounds; A review-pack artifact and pendant notification path, with deduplicated reminders and draft replies

### "Keep a private commitments ledger for me: whenever I promise or accept a follow-up in a meeting, email, or logged-in web conversation, record who, what, and when; reconcile it against my Calendar, Mail, files, and browser activity; and remind me only when a commitment still lacks evidence of completion."
- **useful because:** The owner can generate summaries and reminders today, but cannot reliably close the loop between a promise and proof that it happened. This prevents forgotten follow-ups without flooding them with duplicate task alerts.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use a background text model for extracting candidate commitments and matching completion evidence; use the realtime tier only for a short pendant notification when a high-confidence deadline is approaching.
- **latency:** Capture candidates within 5 minutes of a source becoming available; reconcile hourly and on Calendar/Mail/browser events; notification under 2 seconds once a high-confidence unresolved item crosses its reminder threshold.
- **cost:** Low-to-moderate background cost, dominated by periodic classification of new Mail and authenticated-page deltas; use hashes and incremental source cursors so unchanged content is not resent.
- **security:** Commitments can expose relationships and sensitive work. Store structured facts with source pointers and confidence rather than full content; keep private-page text on the Mac; never infer completion from a draft or page view alone; require confirmation before sending a follow-up or changing a due date.
- **missing:** A durable commitment schema with owner, counterparty, due window, source citation, confidence, status, and evidence links; Incremental event/cursor adapters for Calendar, Mail, local files/notes, and authenticated browser watches; A cross-surface entity resolver that can tell that 'send Alex the deck' in Mail and a file upload in the browser refer to the same commitment; A deduplicating reminder policy and dashboard review/edit controls, plus pendant delivery acknowledgements


## Changes it proposed to its own stack

### `browser-harness` — Add a privacy-aware circuit breaker and queue reconciler between the existing browser routes: before dispatch, label each step public or authenticated; when /browser/status is offline, immediately divert only public steps to /research, persist private steps with idempotency keys and a resumable cursor, stop retry storms, and publish one pendant-readable state transition. On heartbeat, reconcile pending command IDs against job receipts, expire commands whose tab/session is stale, and resume only read-only steps automatically; keep mutations paused for explicit owner review.
- **owner gets:** A disconnected extension should not make the owner wait, lose work, or accidentally replay a form submission. They receive partial useful results now and a clear, trustworthy list of private work waiting for Safari.
- effort: Medium: dispatcher state machine, step classification, durable queue schema, receipt reconciliation, and tests for offline/online transitions.  ·  risk: Misclassification could leak a private URL to public research or leave a safe read stuck. Default unknown to private, retain original step, and provide an inspectable queue with manual retry/cancel. Idempotency prevents duplicate mutations.
- cost: Negligible API cost for health checks; modest D1/local storage growth for cursors, classifications, and receipts.  ·  latency: Removes current ~45-second browser timeout from the voice path; adds sub-second classification and background reconciliation.
- security: Improves security by making private-by-default routing explicit and preventing authenticated payloads from reaching public fallback; mutation replay remains paused.
- depends on: chg-16bc5dee durable browser job runner; chg-14accc01 request IDs/idempotency/tab affinity; browser extension heartbeat implementation; working read-only Mac source/inspection tools


## What it asked for

_Nothing._
## Its own summary

Established live state: the Mac agent and relay are reachable, but the browser bridge is offline with 9 pending commands; a browser navigation already consumed ~45 seconds and failed. Accessibility/Screen Recording remain unavailable, and the newly granted mac_read_sources/mac_readonly_inspect tools are schema-only stubs. Recorded a concrete privacy-aware browser circuit-breaker/reconciler (public fallback, private queue, idempotent resume) and a new post-meeting follow-up-pack capability joining pendant trigger, Calendar/Mail/local Mac context, browser citations, and review-only drafts/reminders. Still needed: implement the two read-only Mac adapters; restore the browser extension heartbeat/poll loop; and build the durable privacy partition/receipt reconciler. Owner action remains needed to enable Safari/Chrome bridge and, if desired, TCC permissions.

**Biggest unknown:** Whether the browser bridge is merely not polling because Safari/Chrome is closed/disabled, or is blocked by a persistent dialog/page; without a real browser heartbeat and implemented local inspection, I cannot safely distinguish those cases or inspect the owner's current tabs.

