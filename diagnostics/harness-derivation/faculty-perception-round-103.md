# Harness derivation — faculty-perception — round 103

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac control readiness** — At 2026-08-07T14:40Z, Mac agent is online and relay reachable, but permissions.ready=false: Accessibility trusted=false, Screen Recording granted=false, inputReachability.status=failed, and ui actions are documented as reporting success while doing nothing. AppleScript automation grants are cached true for System Events, Finder, Reminders, Calendar, Mail, Notes, Messages, Safari, Chrome, Edge, Music, Preview, TextEdit, VS Code, Cursor, Terminal, Warp, iTerm, and System Settings.
  - evidence: GET /ops/snapshot and GET /observe responses at 2026-08-07T14:40:25Z
- **browser bridge availability** — Browser bridge is currently offline: home-chrome has no active tab/window, and 10 commands are pending. Browser actions cannot run until the extension is polling.
  - evidence: GET /browser/status and GET /ops/snapshot at 2026-08-07T14:40Z
- **pendant presence** — No physical pendant is registered/live; device discovery shows only online home-macbook-bridge, with home-chrome offline and cloudflare-contract-test mobile offline.
  - evidence: discover(devices) in round 103; GET /v1/devices/status returned 404
- **briefing freshness and grant contradiction** — Latest workday briefing generated 2026-08-07T11:30Z says calendar and mail were not read because they need Automation grants, while the live ops snapshot at 14:40Z reports Calendar and Mail automation grants true from cache; the briefing's permission note is stale or inconsistent and should not be treated as current.
  - evidence: GET /briefing/latest versus GET /ops/snapshot

## Capabilities it proposed

### "Before you read me a briefing or claim an action succeeded, tell me whether its evidence is current and whether the relevant Mac/browser surface is actually reachable."
- **useful because:** The live system currently has a stale briefing claiming Calendar/Mail permissions are missing while current ops says they are granted, and UI actions can report success while doing nothing. A cross-surface evidence check prevents confident but false spoken updates.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use deterministic freshness/reachability rules first; invoke a cheaper background model only to summarize conflicts. Reserve realtime for the owner's spoken request and concise explanation.
- **latency:** Under 300 ms for route reads and rule evaluation; under 2 s only if a conflict needs model summarization.
- **cost:** Near-zero for GET /briefing/latest, /ops/snapshot, /observe, /browser/status and local rules; occasional small text-model call for conflict wording.
- **security:** Permission state, foreground app, tab URLs, and action receipts leave the Mac only through existing authenticated relay routes. Do not expose URLs or app details unless relevant. Never convert a stale or unverified receipt into an action claim.
- **missing:** A shared evidence-envelope schema with observedAt, source route, TTL, and confidence; A pre-speech perception/judgement hook that can downgrade or block stale claims; A reconciliation rule for briefing permission notes versus live ops permission state

### "Let me ask, “What changed while I was away?” and get a time-bounded, source-cited account of changes across my Mac, browser sessions, relay-delivered messages, and (when I have one) the pendant—without pretending that an unobserved interval was unchanged."
- **useful because:** Today each surface can report its own current state, but nobody can reconstruct a trustworthy interval across surfaces. The owner needs to know whether a document, browser task, queued command, or spoken message changed while a device was disconnected, and which gaps are genuinely unknowable.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → unified → faculty-perception → faculty-judgement
- **model tier:** Use a deterministic event index and source-specific diffing first; use a slower inexpensive model only to turn the cited timeline into natural language. Realtime is only for the final conversational request.
- **latency:** A recent 30-minute query should return an initial cited timeline in under 2 seconds; archival reconstruction can run in the background and notify when complete.
- **cost:** Low recurring cost for local event indexing and compact hashes; occasional small summarization call. Storage, not inference, dominates: compact event metadata and selected before/after snapshots.
- **security:** This crosses highly sensitive browser, file, communication, and audio metadata. Keep raw page contents/audio local where possible, encrypt the event index, redact secrets, disclose blind intervals, and require confirmation before exposing private cross-surface details aloud.
- **missing:** A durable cross-surface event ledger with monotonic timestamps, source identity, connectivity intervals, and before/after hashes; Mac file/notification/calendar/mail change collectors with explicit retention and redaction policies; Browser session change events and relay delivery/acknowledgement events joined by a common correlation ID; Pendant presence and local-storage synchronization records when hardware exists; A query API that returns citations plus explicit unknown intervals rather than a prose-only answer


## Changes it proposed to its own stack

### `browser-harness` — Add a durable pending-command lease and reconciliation loop: every browser command gets an expiry, extension heartbeat binding, and terminal state (expired/replayed/cancelled). When the extension is offline, do not leave commands indefinitely pending; surface the count and safely expire or require explicit retry once the same session returns.
- **owner gets:** The owner will not wonder whether an old browser request is still going to happen later. Today 10 commands remain pending while the extension is offline, creating ambiguity and risk of delayed duplicate navigation or submission.
- effort: Moderate: persist leases and session affinity in browserSessions/browserBridge, add heartbeat reconciliation, dashboard status, and tests for offline/online transitions.  ·  risk: A command could expire just before the extension reconnects; recovery is explicit retry from a receipt-backed terminal record. Never auto-replay write actions; read-only actions may be offered for retry.
- cost: Negligible API cost; small local D1/JSON metadata per command.  ·  latency: No impact while online beyond one heartbeat check; reconnect reconciliation adds under 1 s.
- security: Reduces delayed-action risk. Preserve authenticated session IDs and do not log page content in lease records.
- depends on: Browser extension heartbeat must report a stable extension/session identity; A shared terminal command status and receipt schema; Dashboard/relay must expose expired versus awaiting-heartbeat clearly


## What it asked for

_Nothing._
