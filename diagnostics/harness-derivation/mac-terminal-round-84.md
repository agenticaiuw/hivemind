# Harness derivation — mac-terminal — round 84

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac/browser readiness** — At 2026-08-07T12:46Z the Mac agent and relay are reachable with FULL_CONTROL_MODE enabled, but browser extension home-chrome is offline with 6 pending commands; /ops reports accessibility and screen-recording permissions missing, and the agent marks permissions ready=false. A browser_navigate job waited ~45 seconds before failing with explicit offline error.
  - evidence: GET /ops/status and GET /ops/snapshot returned browser.online=false, pendingCommands=6, accessibility.trusted=false, screenRecording.granted=false; GET /jobs returned local_c8af... failed browser_navigate after 45048 ms.

## Capabilities it proposed

### "When the pendant notices a crash or I say “file this bug,” collect the relevant UART/device log, reproduce context, and leave a ready-to-review issue draft on my Mac with a short spoken summary—never submit it automatically."
- **useful because:** The owner's stated idea is a pendant that files its own bug reports. The pendant is the only node that can capture the immediate button/audio/device context; the Mac is the only node that can inspect the local repo and logs; the relay can preserve the report if the Mac disconnects; and the browser can optionally populate the authenticated issue tracker without sending. This turns an intermittent wearable failure into an actionable, sourced report instead of a vague memory.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic parsers and a cheap background model for log clustering and reproduction-summary prose; use realtime only for the immediate spoken acknowledgement. Escalate to the planner only when stack traces, repo state, and user narrative conflict.
- **latency:** Pendant acknowledgement under 300 ms and local ring-buffer snapshot immediately; relay receipt under 2 s; Mac collection and draft in 10–30 s. If the browser is offline, leave the draft locally and resume tracker population later.
- **cost:** Usually <$0.01 per report: most work is local parsing and background summarization; planner escalation and optional issue-tracker extraction dominate. Storage is a small compressed log bundle plus metadata per incident.
- **security:** UART logs may include tokens, Wi-Fi identifiers, transcripts, or private paths. Redact secrets and audio by default, hash/label sensitive fields, and show the exact bundle and issue body before any browser submission. Browser login/session data stays in the extension; the relay stores encrypted metadata and expires raw logs. Automatic filing should be limited to local draft creation, never send/publish.
- **missing:** A firmware ring buffer and crash marker that survives a dropped link and exports a bounded incident bundle; A relay incident-ingest endpoint with encrypted, expiring attachments and deduplication by device/firmware/time; A Mac log collector that correlates UART, local-agent job receipts, /journal/:jobId, git branch/commit, and machine health into one evidence capsule; A redaction and stack-trace clustering worker plus a draft writer that targets Markdown and optionally a browser issue form; Browser-side preview/fill integration that can populate but not submit an issue, with resume after extension heartbeat

### "When I double-press the pendant while I’m listening, bookmark the exact moment and later give me a searchable note with the surrounding transcript, audio clip, and any related Mac or browser context."
- **useful because:** People often hear an idea, instruction, or important detail while away from the keyboard and lose it before they can write it down. The pendant can mark the moment with no microphone session needing to stay open, the relay can preserve the audio event through a dropped Mac connection, and the Mac/browser can add nearby document, tab, or task context when available. The result is a precise, replayable memory rather than a vague dictated note.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use firmware and deterministic event capture for the bookmark; use a cheap background model for transcription, timestamp alignment, and context matching. Reserve realtime for an optional immediate acknowledgement, not processing.
- **latency:** Local bookmark acknowledgement under 200 ms; durable relay receipt under 2 s; searchable transcript and context enrichment within 30 s. If the Mac or browser is unavailable, preserve the clip and enrich it later.
- **cost:** A few cents or less per bookmark, dominated by transcription; deterministic capture and metadata are negligible. Storage is a bounded clip plus transcript and context pointers, with configurable expiration.
- **security:** The clip may contain private speech or third-party voices. Make capture explicit through the double-press, show an LED/haptic confirmation, encrypt in transit and at rest, redact likely secrets before indexing, and provide per-bookmark delete/export. Browser context must remain metadata-only unless the owner has an authenticated session; never silently capture continuous audio.
- **missing:** A firmware bookmark event with a precise monotonic timestamp and a bounded pre/post audio ring-buffer export; Relay storage and APIs for encrypted clip fragments, transcript alignment, retention, and later enrichment; Mac-side correlation of bookmark time with active application/document/window and local job history; Browser-side read-only context snapshot tied to the bookmark without requiring a new navigation; A dashboard/search view that joins audio, transcript, source context, and deletion controls


## Changes it proposed to its own stack

### `integration` — Add a non-blocking capability preflight and fail-fast dispatch contract across the Mac agent, browser bridge, and relay. Before a browser_* action is queued, read the existing /ops/status (or a cached heartbeat) and attach a capability snapshot: browser online/lastSeen, pending-command count, accessibility and screen-recording readiness, relay reachability, and an expected execution deadline. If the target is offline, do not spend the action timeout waiting: return a typed `unavailable` receipt immediately with the exact recovery instruction (for example, open Safari and enable/poll the AI Pendant Browser Bridge), retain the user's intent as a durable queued job only when the request was explicitly asynchronous, and re-check on heartbeat to resume it. The same snapshot should be embedded in /jobs, /journal, and spoken completion/failure summaries so the planner can choose shell, browser, or relay instead of blindly retrying.
- **owner gets:** Today a browser request can sit for roughly 45 seconds and then fail even though the Mac and relay are healthy; the owner gets no useful answer until the timeout. This makes the pendant respond immediately, choose another reachable surface when possible, and resume genuinely background work after the browser returns—without adding approval gates or reducing the owner's maximum-access policy.
- effort: Medium: shared health schema, dispatch middleware, heartbeat-triggered resumer, and typed receipt/UI rendering; no new model required.  ·  risk: A stale cached heartbeat could report a surface as available when it is not, or an intent could resume after the owner forgot it. Bound cache age, preserve idempotency keys, mark queued work clearly, and provide cancel/delete through existing job controls. Never claim an action ran from a preflight result.
- cost: Negligible API cost; saves failed planner/tool retries and ~45-second waits. Small local D1/job-store growth for health snapshots and queued intent metadata.  ·  latency: Healthy actions add a cheap local health lookup; unavailable browser actions return in milliseconds instead of timing out. Resumed jobs begin on the next bridge heartbeat.
- security: No new data access; health metadata should omit URLs/titles and expose only capability state. Existing unrestricted shell policy remains unchanged.
- depends on: A stable browser heartbeat/online contract in the existing /browser/heartbeat and /browser/status routes; Durable job lifecycle and idempotency semantics behind /jobs and /jobs/:jobId/cancel; A shared typed receipt schema consumed by /journal and dashboard


## What it asked for

_Nothing._
## Its own summary

Recorded a new cross-surface capability: a deliberate pendant double-press bookmarks the exact listening moment, preserves a bounded audio clip through the relay, and later joins transcript plus Mac/browser context into a searchable, replayable note. It requires firmware timestamp/ring-buffer support, encrypted relay clip storage, Mac/browser context correlation, and a review/deletion UI.

**Biggest unknown:** Whether any existing audio implementation already exposes a precise bookmark event and bounded pre/post clip export; discovery is unavailable this round, so that must be checked during implementation.

