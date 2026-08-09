# Harness derivation — relay-realtime — round 199

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Summarize what I was doing on my Mac and what changed since I last asked."
- **useful because:** Gives the owner a quick, spoken situational awareness of ongoing work without needing a screen.
- **path:** mac-bridge → relay → pendant
- **model tier:** Cheaper background tier to assemble the summary; realtime to speak it.
- **latency:** 1-3 seconds for a short spoken summary.
- **cost:** Moderate; depends on reading job logs and receipts.
- **security:** May reveal sensitive content from apps. Provide a brief summary and avoid reading raw documents unless explicitly asked.
- **missing:** A concise, user-sized summary generator that uses receipts/journal; A stable mapping from job outputs to user-facing summaries

### "“I’m looking at something on my Mac or in a logged-in browser. Tell me exactly what matters, then carry out the safe next step.” The pendant should capture the current visual context, have the Mac/browser agent interpret it with the user’s spoken constraint, act when appropriate, and report what changed and what remains uncertain."
- **useful because:** Today the owner must separately describe what is on a screen and issue a second command; the wearable cannot see the thing they are referring to. This makes the pendant a genuinely remote control for the owner’s current visual context while preserving a concise spoken interaction.
- **path:** pendant → relay-realtime → mac-vision → mac-planner → browser-extension
- **model tier:** Realtime relay handles the short utterance and final spoken summary; mac-vision performs screenshot/UI grounding; mac-planner executes the small action sequence; browser-extension supplies authenticated page state when the target is in Safari.
- **latency:** 5–8 seconds for a first answer; up to 20 seconds for a multi-step action, with an immediate spoken acknowledgement if it runs longer.
- **cost:** Roughly $0.02–$0.10 per invocation; screenshot interpretation and any browser page extraction dominate, while the relay turn remains short.
- **security:** A screenshot and possibly authenticated page text leave the Mac for interpretation. Redact known secrets and exclude password fields by default; make destructive or externally visible actions explicit in the spoken plan, and return a receipt naming the app/page and action.
- **missing:** A Mac capture/vision endpoint that can atomically capture the foreground window and expose UI coordinates to mac-vision; A relay-to-Mac visual-context request carrying the spoken referent and a freshness timestamp; A browser bridge that returns the currently focused tab plus an inspectable DOM snapshot; A compact receipt format that the pendant can speak

### "“Make this a private handoff: move the thing I’m working on from the Mac/browser to my phone or pendant, and back later, without me explaining it again.” The system should package the current task, relevant files or links, exact position, and unresolved decision into a resumable handoff, then surface it through the wearable and restore it on another surface."
- **useful because:** The owner is often away from the Mac. Today context is stranded in an app, browser tab, or an interrupted voice turn. A durable, minimal handoff would let them leave mid-task and resume hands-free or on the Mac with the same state rather than reconstructing it.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** A cheap background model extracts a structured task capsule; realtime only speaks the capsule title and next decision. Mac-planner/browser-extension produce exact local/browser anchors and faculty-perception validates that they still exist on resume.
- **latency:** Under 4 seconds to create a capsule and speak confirmation; restoration may take 10 seconds and should provide progress asynchronously.
- **cost:** About $0.01–$0.05 per handoff; tokenized task metadata is cheap, while optional screenshot/file indexing dominates.
- **security:** Capsules may contain private file names, URLs, or snippets. Encrypt at rest, retain only the minimum selected artifacts, expire capsules by default, and never copy file contents to the relay when a local reference suffices. Restoring a browser session must not expose its contents in spoken audio around others.
- **missing:** A durable encrypted task-capsule store with owner-controlled expiry; Mac and browser adapters that record stable anchors (window, tab, document range, cursor/selection); A pendant/phone inbox verb that can announce and select capsules; Resume validation and conflict handling when a file, tab, or selection changed


## Changes it proposed to its own stack

### `relay` — Add a relay-visible capability manifest endpoint (e.g., GET /relay/capabilities) plus a typed, enum-based intent routing tool schema that resolves to real plan/execute action types, and a job status receipt feed sized for spoken output.
- **owner gets:** The relay can reliably tell what it can do and route requests without guessing. That reduces misroutes and lets the owner ask for complex actions with confidence.
- effort: Medium: define manifest, implement endpoint, align tooling schemas with existing action vocabulary.  ·  risk: Low to medium: schema mismatch could break routing; mitigate with versioning and a compatibility alias table.
- cost: Low ongoing; one extra endpoint and schema maintenance.  ·  latency: Improves routing speed by reducing retries and misroutes.
- security: Requires careful scoping to avoid exposing sensitive internals; publish capability names and versions, not secrets.

### `integration` — Introduce a durable, cross-surface notification spine: a relay Durable Object (or equivalent) that tracks job subscriptions, stores minimal state, and delivers completion notifications to pendant/phone inboxes when they reconnect.
- **owner gets:** They can start tasks and confidently get results later, even across disconnects, without re-asking.
- effort: High: needs storage, subscription API, reconnect logic, and delivery semantics.  ·  risk: Medium: duplicate or missed notifications; mitigate with idempotent receipts and expiry.
- cost: Moderate: storage and a small amount of always-on compute.  ·  latency: Completion delivery depends on reconnect; acknowledgement stays fast.
- security: Must enforce per-owner isolation and avoid leaking job metadata; store only what needs to be spoken.

### `interaction` — Add a two-channel spoken interaction protocol for the relay: every downstream request first emits a 1-sentence intent echo with a compact correlation token, then the final answer includes a machine-verifiable freshness/source/result class. The pendant should let a second press say “repeat source,” “stop,” or “that’s not what I meant,” and the relay should cancel or correct the active Mac/browser job rather than starting a new unrelated turn.
- **owner gets:** The owner can currently lose track of whether the pendant heard the right referent, especially while away from the Mac. This would make remote actions recoverable in conversation: fewer silent wrong actions, clear distinction between current state and stale completion, and a fast way to abort without reaching for the Mac.
- effort: Medium: relay session state and correlation tokens, cancellation propagation to Mac jobs, a small firmware gesture/state addition, and spoken receipt rendering.  ·  risk: A dropped cancellation could leave a downstream action running; the relay must say cancellation is requested versus confirmed and use existing job undo/cancel paths where available. Recovery is a final status event and the existing inbox for offline delivery.
- cost: Negligible per-turn storage; one extra short TTS sentence can add roughly $0.001–$0.01 and modest audio latency.  ·  latency: Adds about 300–700 ms for the intent echo, but prevents much costlier retries and wrong actions.
- security: Correlation tokens must be unguessable and scoped to the owner’s session; spoken source labels should avoid leaking sensitive URLs or file names.
- depends on: A real relay job cancellation/abort propagation path; A durable per-session correlation record; A firmware gesture that distinguishes interrupt/cancel from ordinary playback

### `integration` — Ship a first-class USB-tethered operating mode: when the nRF9160 and ESP32 are attached to the Mac, a signed local bridge should carry the same press/audio/reply protocol as LTE, expose connection quality and device identity to the relay, and fail back cleanly to the existing offline outbox when the cable is removed. The mode must be selectable per session, not silently masquerade as LTE.
- **owner gets:** The real pendant is physically testable on the owner’s desk today, but it cannot currently behave like the worn product because it is not relay-registered over LTE. This would let the owner use and debug the actual button, microphone, speaker, LED, and 24 kHz path immediately, then walk away without losing queued work.
- effort: Medium-high: USB serial framing/authentication on the Mac, a local-to-relay WebSocket or HTTPS bridge, device registration/lease handling, and firmware transport selection with reconnect tests.  ·  risk: A stale cable bridge could report the pendant as online when it is not. Use explicit transport identity, heartbeats, monotonic sequence numbers, and replay-safe acknowledgements; on failure, preserve the existing upload-failure-only SD behavior and offline memo queue.
- cost: No per-invocation model cost beyond normal voice turns; negligible power change while tethered. Engineering cost is in the serial bridge and integration tests.  ·  latency: Should reduce desk-mode round-trip latency by roughly 50–150 ms by avoiding LTE, while LTE behavior remains unchanged.
- security: The local bridge becomes a powerful bearer of microphone audio and relay credentials. Pair it with a device key, bind it to the owner’s Mac session, use encrypted localhost transport, and refuse arbitrary serial clients.
- depends on: A real pendant registration/lease route on the relay; A Mac USB serial bridge for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A transport-neutral audio/session protocol shared by LTE and USB; Integration tests for cable removal during capture, upload, and downlink playback


## What it asked for

_Nothing._
