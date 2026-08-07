# Harness derivation — faculty-judgement — round 99

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“When I walk into a meeting, get me ready; while I’m there, remember the loose ends; when I leave, turn them into a clean follow-up queue.”"
- **useful because:** This closes the meeting lifecycle rather than producing a one-time brief: a long press or double-press on the pendant marks entry/exit, the relay combines Calendar, the active Mac project, and already-authenticated browser tabs into a short cited/audio prep, then the pendant captures spoken follow-ups even when LTE drops. On exit, the Mac reconciles captured items against the meeting and drafts reminders/notes, showing provenance and asking before any external send.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use the realtime model only for the live spoken interaction and capture confirmation; use mac-planner/background jobs for Calendar/browser research, reconciliation, and audio generation.
- **latency:** Entry acknowledgement under 1 second; prep brief within 20 seconds or stream the first items; offline capture immediate; exit reconciliation within 60 seconds after the Mac is reachable.
- **cost:** About $0.01–$0.08 per meeting depending on transcript length and browser research; most work should be background Mac calls, not realtime tokens.
- **security:** Calendar titles, private tab contents, and spoken notes leave the pendant only to the authenticated relay/Mac. Keep meeting data scoped to its event, expire raw audio quickly, cite every extracted fact, and require confirmation before sending mail or creating externally visible artifacts.
- **missing:** A durable meeting session object linking entry/exit gestures, event identity, active project, captured utterances, and final follow-up state.; A pendant gesture recognizer and offline encrypted capture queue that distinguishes meeting start/stop from ordinary conversation.; A reconciliation worker that deduplicates captured commitments against Calendar/Mail/Notes and produces a reviewable queue.; A cross-surface preflight that refuses to claim browser/calendar context when the bridge is offline.

### "“Let me bring another person into a private AI-assisted conversation safely: make consent and recording state obvious, help us understand each other in real time, and give both of us control over what summary survives.”"
- **useful because:** Today the pendant can speak with its owner, but it cannot safely serve a shared conversation. This would let the owner use it in a doctor visit, repair appointment, interview, or difficult conversation without secretly turning a private exchange into permanent memory. The other participant gets an explicit join/consent signal, a temporary session, optional live translation or clarification, and a review screen before any transcript or summary is retained.
- **path:** pendant → relay-realtime → mac-planner → dashboard-ux
- **model tier:** Use realtime only for low-latency speech recognition, translation, and clarification. Use a cheaper background model on the Mac for the post-conversation summary and redaction; never send the full recording to the background tier unless both participants approve.
- **latency:** Consent-state changes and mute confirmation under 500 ms; translation/clarification under 1.5 seconds; post-session review packet within 30 seconds.
- **cost:** Approximately $0.03–$0.25 per ten-minute conversation, dominated by realtime audio and optional translation; summary/redaction is comparatively inexpensive background work.
- **security:** This is highly sensitive third-party data. The pendant must visibly and audibly indicate listening, provide a hardware mute/stop path, refuse capture until the second participant consents, and encrypt a session-scoped stream. Default retention is zero: only an explicitly approved redacted summary may leave the temporary session. Never use private browser or Calendar context in a shared session unless the owner separately unlocks it.
- **missing:** A two-party consent handshake with signed session membership and jurisdiction-aware recording rules.; A pendant-visible shared-session state with a local mute/stop latch that survives link loss.; A relay mode that keeps shared audio isolated from the owner's long-term memory and supports optional translation.; A Mac/dashboard review surface where both participants can approve, redact, or delete summary items before persistence.; A retention/deletion primitive that can prove the raw audio and unapproved transcript were destroyed.


## Changes it proposed to its own stack

### `integration` — Add a Meeting Session Coordinator between gesture/event ingestion and existing research/briefing/reminder routes. It creates one immutable session ID on entry, resolves the matching Calendar event, snapshots the active project and reachable browser evidence, appends pendant utterances as timestamped provisional items (including offline batches), then closes the session on exit and emits a deduplicated review queue with source links and confidence. Every downstream job must reference that session ID; if a source is unavailable it records 'not observed' rather than silently substituting stale context.
- **owner gets:** The owner can use one tiny pendant gesture at the door and receive a coherent before/during/after meeting record instead of disconnected briefs, captures, and reminders that they must manually join.
- effort: Medium-high: event schema, matching rules, offline merge/idempotency, coordinator state machine, and adapters around the existing research, capture, briefing, and reminder routes.  ·  risk: Wrong Calendar matching or duplicate follow-ups could erode trust. Mitigate with a visible candidate event list when ambiguous, immutable provenance, idempotency keys, and a review-only closeout; all external sends remain confirmation-gated.
- cost: Low API cost: mostly short structured records and one background reconciliation call; storage is a few KB per meeting plus optional short-lived audio.  ·  latency: Entry is immediate; prep starts asynchronously; closeout can complete within a minute after connectivity, while the owner gets an immediate 'captured, pending reconciliation' acknowledgement.
- security: Session-scoped access prevents unrelated private tabs or meetings leaking into the brief. Raw utterances and browser extracts need TTLs and deletion controls; dashboard must show which sources were actually reachable.
- depends on: A durable session/event schema and idempotent append endpoint; A device-local gesture/capture queue (button patterns, offline timestamps); A browser/calendar availability preflight and explicit stale-source marker; Existing /capture, /research, /briefing, /reminders, /projects/active, and /pipeline/events adapters


## What it asked for

_Nothing._
## Its own summary

Round 99 discovery found no newly exposed item in the granted category; the live fleet remains Mac bridge online, browser offline, and the pendant is still the nRF9160 prototype (15,625-Hz capture, 24-kHz playback, 87% single-core duplex load). I added two new, non-duplicate design items: a Meeting Session Coordinator that joins entry gesture, cited prep, offline follow-ups, and exit reconciliation; and the concrete dependencies needed to make that trustworthy. I still need a durable session/event schema with idempotent offline merge, a device-local meeting gesture/capture queue, source-health preflight with explicit stale/unavailable markers, and an end-to-end negotiated audio contract/product hardware path rather than another codec patch.

**Biggest unknown:** Whether the orchestrator's newly acted-on requests are actually deployed in this environment: discover:granted reports zero, and no new device-local or reconciliation tool is visible. The next useful check is deployment/status evidence for those grants, not another permission request.

