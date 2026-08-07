# Harness derivation — browser-extension — round 60

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser liveness** — Direct GET /browser/status reports online=false for home-chrome with tabCount=null and 4 pending commands, while GET /browser/sessions still contains three sessions with historical tab IDs and URLs. This is historical session state, not proof Safari is currently reachable.
  - evidence: GET /browser/status at 2026-08-07T11:36Z returned online=false, lastSeen 11:34:33Z, pendingCommands=4; GET /browser/sessions returned default session tabId 320512 URL https://time.is/UTC and two probe sessions.

## Capabilities it proposed

### "When a logged-in page I care about changes in a way that may need me soon, interrupt me briefly on the pendant, open a sourced review card on my Mac, and let me say “later” or “handle it” without sending or submitting anything."
- **useful because:** Daily summaries are too late for a time-sensitive private account change. This combines the only authenticated browser reach with the always-carried pendant and Mac workspace, while keeping the irreversible step in review.
- **path:** browser-extension: capture the changed authenticated region and before/after evidence → relay-realtime: classify urgency and deliver a one-sentence spoken alert; receive acknowledge/snooze/handle intent → mac-planner: create a review card with URL, timestamp, diff, and proposed reversible next steps → pendant: tactile/audio alert and offline acknowledgement queue → dashboard: show active alerts, snoozes, and evidence links
- **model tier:** Use a cheap background model for page-diff normalization and urgency scoring; use realtime only to speak the alert and interpret the owner's short response.
- **latency:** Page checks can run on their existing cadence. Once a meaningful change is found, alert within 5 seconds; Mac review card within 10 seconds. Snooze/ack should work offline and sync later.
- **cost:** About $0.002–$0.02 per changed-page evaluation depending on extracted text; realtime cost is limited to actual alerts and short replies. Browser polling and storage dominate operational cost, not inference.
- **security:** Private page text and diffs leave Safari only to the local Mac agent/relay for processing; redact secrets and unrelated regions. Never auto-send, submit, purchase, delete, or change account state. The alert should expose only the minimum snippet until the owner asks for detail.
- **missing:** A durable alert object linking browser watch diff, Mac review card, and pendant acknowledgement; Urgency/quiet-hours policy with deduplication and snooze state; A working browser command enqueue implementation and reliable Safari heartbeat/session reconciliation; A pendant-to-relay acknowledgement event and Mac deep-link review card

### "When I say “what changed since I last looked?” while I have a logged-in page open, compare it with the last page state I personally saw, tell me the one meaningful change on the pendant, and highlight the exact changed section in Safari."
- **useful because:** This answers an immediate question about a private page without requiring a scheduled watch or a full briefing. The owner gets a concise spoken answer and a visual pointer to the evidence, even when the change is buried in a dashboard.
- **path:** browser-extension: capture the current authenticated DOM/viewport and apply a temporary highlight to the changed region → mac-planner: retain a compact owner-seen baseline keyed to site, account session, and page identity → relay-realtime: interpret the spoken request and speak the single meaningful difference → pendant: provide the short spoken result and an optional follow-up control such as “read it”
- **model tier:** Use a small background model or deterministic DOM/structured-data diff first; invoke the expensive realtime model only for the owner's spoken request and ambiguous summaries.
- **latency:** Return the spoken difference in 3–6 seconds and highlight the region in Safari before or immediately after the answer. Baseline capture should be asynchronous and not interrupt browsing.
- **cost:** Usually below $0.01 per request when structured DOM diffs are sufficient; model cost is dominated by occasional ambiguous page interpretation. Store hashes and selected snippets rather than screenshots by default.
- **security:** Keep the baseline local to the Mac where possible; never transmit unrelated page content. Bind baselines to the browser session and page origin, expire them, and avoid treating a changed login state or rotating timestamp as meaningful. This is read-only and must not click or submit anything.
- **missing:** An owner-seen baseline primitive distinct from scheduled page watches; DOM-region diff output with stable selectors and a temporary Safari highlight command; A pendant request/result correlation for short spoken follow-ups; Session-scoped privacy and expiration rules for authenticated page snapshots

### "Ask my logged-in site a question privately: have Safari extract only the answer from the relevant fields, speak it to me, and do not send the surrounding page or unrelated account data to the relay."
- **useful because:** The browser is uniquely able to reach private accounts, but sending whole pages to a server is unnecessary and uncomfortable. Field-scoped extraction would let the owner use private data conversationally while sharply reducing disclosure.
- **path:** pendant: capture the question and play the concise answer → relay-realtime: identify the target site/page and formulate an extraction request without receiving raw page content → browser-extension: locate the relevant authenticated fields locally and return only typed values plus provenance → mac-planner: maintain the local site schema, selector repair, and encrypted short-lived result cache → dashboard: show exactly which fields were released and allow the owner to revoke the cache
- **model tier:** Use a compact local/cheap extraction model on the Mac or extension for field selection; use realtime only for the spoken question and final response. Do not use the expensive model to process raw page text.
- **latency:** Answer in 3–8 seconds for known schemas; allow up to 15 seconds for first-time selector discovery. Cache only schema metadata, not page contents.
- **cost:** Near-zero inference cost for structured fields; occasional local model work and browser execution dominate. Relay token cost is limited to the question, typed answer, and source metadata.
- **security:** Raw authenticated DOM stays on the Mac/browser. Enforce origin, account-session, and field allowlists; redact secrets such as passwords and full payment numbers by default. Release only the requested value, a minimally identifying label, timestamp, and source URL. Require confirmation before any mutation, as today.
- **missing:** A browser-local extraction worker with a typed field/value response contract; Per-origin schemas and selector repair stored on the Mac; A relay protocol that can route questions without receiving raw page content; A visible release ledger and short-lived encrypted cache for extracted values


## Changes it proposed to its own stack

### `browser-harness` — Replace the contradictory browser liveness model with device leases plus session health. Safari heartbeats must register the real device identity, tab count, active tab, and last successful command; /browser/status must report per-device online state from a short lease, while browser sessions independently report reattachability. On reconnect, replay only idempotent pending reads, expire stale commands, and emit a typed recovery event rather than leaving pendingCommands stranded.
- **owner gets:** The owner should not be told browser access is ready when Safari is offline, nor lose a private-page task because the extension briefly disappeared. This makes authenticated reading dependable and prevents duplicate clicks or stale actions after reconnect.
- effort: Medium: update heartbeat/status schema, queue expiry and idempotency handling, session health checks, and add disconnect/reconnect tests against Safari 26.5.2.  ·  risk: A too-short lease could falsely mark Safari offline; use grace periods and visible degraded status. Replay must be limited to reads and navigations, never form submission or other mutations. Existing sessions may need one-time migration.
- cost: Negligible inference cost; small D1/local-agent state increase for leases and recovery events.  ·  latency: Heartbeat every 10–20 seconds adds minimal traffic; reconnect recovery adds at most one polling interval for safe reads.
- security: Improves safety by preventing stale private-page commands from replaying blindly. Preserve tab/session affinity and redact page contents from health telemetry.
- depends on: A functioning browser command enqueue path (the currently granted wrappers are still stubs); Safari extension heartbeat update to report its actual registered device instead of only home-chrome; Durable browser job runner or equivalent queue persistence


## What it asked for

_Nothing._
