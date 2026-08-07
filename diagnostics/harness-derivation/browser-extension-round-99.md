# Harness derivation — browser-extension — round 99

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser availability** — The browser backend currently has no live extension: /browser/status reports online:false for home-chrome, no Safari device entry, and 9 pending commands; persisted sessions point to stale tabs last used hours ago. Treat reads/actions as unavailable until heartbeat returns, and do not claim a private-page result.
  - evidence: GET /browser/status HTTP 200: {online:false, devices:[home-chrome offline, tabId:null], pendingCommands:9}; GET /browser/sessions HTTP 200: three stale sessions with lastUsedAt 06:26 or earlier; GET /browser/inspections HTTP 200: inspections:[]

## Capabilities it proposed

### "“Read this private page in Safari, turn the important details into a short reminder or audio note, and deliver it to my pendant at the right time—without sending or submitting anything on the site.”"
- **useful because:** This joins the one place that can see authenticated browser content with the always-awake relay and wearable output. It lets the owner convert a logged-in itinerary, prescription instruction, appointment page, or support deadline into an actionable reminder without exposing the page to public search or requiring the Mac to stay awake.
- **path:** browser-extension → mac-planner → relay-realtime → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use the cheap background tier for extraction, normalization, scheduling, and audio preparation; use realtime only if the owner asks follow-up questions by voice. Escalate to the expensive tier only for ambiguous dates, conflicting page fields, or safety-sensitive interpretation.
- **latency:** Private-page read and draft in 5–15 seconds while Safari is online; reminder scheduling and audio generation can complete asynchronously. If Safari is offline, report that plainly and retain no fabricated result.
- **cost:** Usually one short background extraction plus optional TTS/audio generation; roughly low cents per request, dominated by page-text context and audio synthesis. Realtime cost is avoided unless conversation is active.
- **security:** Only selected page excerpts and the requested reminder fields leave Safari; preserve URL, tab, timestamp, and evidence snippet for audit, with short retention. Do not submit forms, send messages, or alter the source page. Calendar/reminder creation and pendant playback are reversible but should be clearly described before execution; never infer medication or financial advice beyond quoted text.
- **missing:** A durable browser job runner and result stream (chg-16bc5dee remains open); A scheduler/audio handoff that accepts browser evidence and emits a pendant queue item with provenance; An online Safari heartbeat and stale-command recovery; current GET /browser/status reports offline with 9 pending commands; A unified evidence object linking browser extraction, reminder, and audio artifact

### "“From my pendant, answer a question about the private page I’m looking at in Safari, but send only the minimal answer back—never the page or my login data to the relay, and forget the answer after I hear it.”"
- **useful because:** Today the browser is the only surface that can see the owner’s authenticated page, while the pendant is the only surface available when the owner is away from the Mac. This would let the owner ask about a live private page hands-free without copying page contents into chat history or a long-lived server record. It is a genuinely different privacy property from ordinary browser extraction: a one-shot, end-to-end, least-information answer channel.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a small local/browser extraction model on the Mac for page grounding and answer compression; use realtime only to transcribe the pendant question and speak the returned answer. Escalate to the expensive tier only when the page evidence is ambiguous.
- **latency:** 5–10 seconds while Safari is online; return an explicit unavailable result within 2 seconds if the browser lease is dead. The answer should be discarded after playback or a short timeout.
- **cost:** Low cents per request, dominated by a compact local extraction and optional realtime speech; no full-page relay prompt or persistent audio artifact.
- **security:** The relay must route an opaque request and encrypted response, not receive DOM/text. Safari extension and Mac agent need an ephemeral session key, origin/tab binding, nonce, expiry, and replay protection. The Mac should return a short answer plus an evidence hash, while raw evidence remains local and is deleted after completion. Never perform clicks, typing, submissions, purchases, or messages through this read-only capability.
- **missing:** A browser-to-pendant ephemeral encrypted channel with per-request key agreement and explicit zero-retention semantics; A local Mac answerer that grounds only against the bound active tab and enforces a response-size limit; A Safari heartbeat/lease and active-tab binding API; the current browser state can be offline and stale; Relay plumbing that transports ciphertext without logging decrypted content; A typed response contract distinguishing answered, ambiguous, unavailable, and expired requests


## Changes it proposed to its own stack

### `browser-harness` — Add an offline-queue reconciler and command lease dashboard. When the Safari extension goes offline, mark all unacknowledged browser commands as paused—not runnable—after their lease expires; classify each as safe-to-retry, stale-read, or unsafe-to-replay, discard duplicate content-addressed commands, and expose resume/cancel/retry with the original tab/session affinity and evidence. On reconnect, send only explicitly resumable commands and return a typed reconciliation report to the planner.
- **owner gets:** The owner will not get a surprise click or form fill after Safari has been disconnected for hours, and a private-page task can recover cleanly instead of hanging or silently disappearing. They can see exactly what paused, what was safely retried, and what needs a fresh look.
- effort: Medium: browserBridge lease state machine, persistent queue metadata, reconnect reconciliation endpoint/UI, and planner result schema; add fault-injection tests for disconnect/reconnect and duplicate polls.  ·  risk: A command could be incorrectly classified as retryable and act on changed page state. Recovery: default unknown actions to paused, require a fresh page snapshot before any mutation, preserve the existing maximum-access/no-gate policy by making this observability and stale-state handling rather than an approval gate.
- cost: Negligible API cost; small local JSON/D1 metadata growth, bounded by retention. No new hardware cost.  ·  latency: Adds milliseconds to normal enqueue; reconnect may spend one extra read/snapshot before resuming. Prevents 45-second hangs by returning paused status immediately.
- security: Improves safety and auditability: stale commands are not replayed blindly; retain only command hashes, session/tab IDs, and typed status, not page secrets.
- depends on: A live Safari heartbeat/reconnect path (currently GET /browser/status reports offline); The durable browser job runner and result stream from chg-16bc5dee; The existing request IDs/idempotency and journal work from chg-14accc01

### `integration` — Add a page-identity attestation protocol between Safari and the pendant request path. For each read-only question, Safari signs a short-lived tuple of extension installation key, tabId, top-level origin, URL hash, DOM snapshot hash, and monotonic sequence; the Mac planner refuses to answer unless the attestation matches the tab lease and the response includes the same evidence hash. Rotate the ephemeral request key after every answer and expose only an opaque receipt to the relay.
- **owner gets:** The owner can trust that a spoken answer came from the page currently open in their Safari—not a stale tab, another window, or a replayed command—without handing the relay a copy of their private page. This is especially valuable for banking, healthcare, travel, and work portals where a plausible answer from the wrong page is worse than no answer.
- effort: Medium-high: extension signing/key storage, Mac verification library, tab-change hooks, nonce/sequence persistence, and integration tests for reloads, redirects, duplicate polls, and Safari restarts.  ·  risk: A tab reload or extension update could invalidate an otherwise valid request and make the feature report unavailable. Recover by requiring a fresh read-only attestation, never silently falling back to an unbound tab, and retaining a local diagnostic receipt without page text.
- cost: Negligible per-request API cost and storage; modest engineering cost. No new recurring service dependency.  ·  latency: Adds one local signing and verification round trip plus a snapshot hash, generally under 200 ms; avoids expensive retries and wrong-tab answers.
- security: Strongly improves origin/tab binding, replay resistance, and minimization. Private DOM and answer plaintext stay on the Mac/pendant path; the relay sees only encrypted payload metadata and an opaque receipt.
- depends on: A functioning Safari extension heartbeat and tab-change event stream; A local ephemeral-key store in the Mac agent; The pendant/relay transport supporting opaque encrypted request and response bodies; The browser job/request IDs already present in the local browser bridge


## What it asked for

_Nothing._
## Its own summary

Discovered the live browser state: Safari is not currently registered/online; only the never-used home-chrome device appears offline, with 9 pending commands. Persisted browser sessions are stale and inspections are empty, so authenticated reads must not be claimed right now. I recorded this finding, informed mac-planner, and proposed two new pieces: (1) a cross-surface private-page-to-pendant reminder/audio workflow, and (2) an offline queue reconciler that pauses and classifies stale commands, preventing blind replay after reconnect.

**Biggest unknown:** Whether the real Safari extension is still running and can be made to heartbeat again; until that is restored, the missing durable browser runner/result stream and reconnect reconciliation cannot be validated end to end.

