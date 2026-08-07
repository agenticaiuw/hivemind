# Harness derivation — mac-planner — round 75

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac bridge and browser readiness** — As of 2026-08-07T11:45Z the Mac bridge is online but not ready: Accessibility trusted=false and Screen Recording granted=false. Browser extension home-chrome is offline with 5 pending commands. /jobs contains a current processing execute job with no actions and a prior browser_navigate failure caused by offline extension.
  - evidence: GET /ops/status, GET /browser/status, and GET /jobs returned these states.

## Capabilities it proposed

### "“Save my current work so I can pick it up later.” Then, when I say “resume my saved work,” bring back the right browser tabs and Mac files and give me a short spoken orientation."
- **useful because:** This creates a real cross-device pause/resume primitive: the pendant is the always-available command surface, the Mac contributes foreground app/files, the browser contributes authenticated tab state, and the relay preserves a compact, cited capsule. It is more useful than a generic history because it restores the working set and explains what was unfinished.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the realtime model only for the spoken save/resume conversation and final short orientation. Use a cheaper background model to normalize the capsule, deduplicate tabs/files, and generate the resume brief.
- **latency:** Save acknowledgement under 2 seconds; background capsule construction under 10 seconds. Resume should restore reversible tabs/files in under 8 seconds, then speak a 20–30 second orientation.
- **cost:** Roughly $0.01–$0.05 per save/resume depending on transcript and page text; most cost is background summarization, not the realtime acknowledgement. Storage is small JSON plus hashes, unless the owner explicitly includes page excerpts.
- **security:** Authenticated URLs, filenames, and snippets are sensitive. Keep the capsule encrypted/owner-scoped, default to metadata and source hashes rather than full page bodies, expire capsules, and never submit forms or send messages during restore. Opening a saved tab or file is reversible; any mutation must remain an explicit separate command.
- **missing:** A first-class cross-surface work-capsule schema with provenance, TTL, and sensitivity labels; Read-only Mac snapshot implementation (foreground app, open files, browser tabs, selected directory metadata); Browser session/tab reattachment and restore endpoint with idempotency; Pendant command/event wiring for save and resume plus a compact spoken result; A restore planner that distinguishes open/read actions from mutations and emits receipts

### "“Privacy mode.” When I enter a meeting or shared space, immediately hide sensitive Mac windows, pause authenticated browser work, and stop private spoken output; when I say “resume privately,” restore the exact working state and give me the missed updates discreetly through the pendant."
- **useful because:** The owner can use the system in real life without accidentally exposing mail, account pages, filenames, or spoken reminders to people nearby. It is a coordinated physical-world mode: the pendant is the low-friction trigger and private output channel, the Mac hides local state, the browser pauses authenticated work, and the relay queues only the minimum missed notifications. No current single surface can provide this consistently.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the realtime model only to interpret the short privacy/resume command and confirm state. Use deterministic local rules for hiding/pausing and a cheap background model to rank missed updates for the later private digest.
- **latency:** Enter privacy mode in under 1 second for the pendant acknowledgement and under 3 seconds for Mac/browser state changes. Resume acknowledgement under 2 seconds; digest generation may take up to 10 seconds.
- **cost:** Usually under $0.01 per transition; most work is local state capture and deterministic routing. Background summarization costs roughly $0.01–$0.03 only when missed updates need ranking.
- **security:** The mode state, hidden-window list, authenticated tab identifiers, and queued notifications are sensitive. Keep detailed state local and owner-scoped, encrypt relay metadata, expire queued digests, suppress all TTS except a neutral confirmation, and never navigate, submit, or send while paused. Restoration must be idempotent and produce receipts.
- **missing:** A pendant privacy-mode command/event, including a physical-button fallback that works if speech is inappropriate; A local Mac privacy controller that records and restores window visibility, foreground app, audio route, and notification suppression without losing unsaved work; A browser pause/resume protocol that freezes queued commands and preserves authenticated tab/session affinity; Relay-level quiet-mode state with expiry, missed-event queue, and private digest delivery; A cross-surface state machine and crash-safe restore journal


## Changes it proposed to its own stack

### `relay` — Add a failure-aware reconciliation loop that joins relay pipeline events, Mac /jobs state, /journal action receipts, and browser heartbeat/session state by requestId. It should classify each unfinished job as progressing, completed-with-missing-receipt, failed-retryable, failed-permanent, or unreachable; issue at most one idempotent retry for retryable read/open steps; and publish a concise owner-facing outcome with the exact last successful step and next recovery option. Do not add blocking approval gates.
- **owner gets:** When the owner asks the hive to do something and walks away, they get a trustworthy answer instead of a vague 'processing' or silent failure. If the browser disappears or the Mac bridge loses permission, the system can say precisely what happened and recover harmless steps automatically.
- effort: Medium: correlation schema, watchdog worker, retry classification, and dashboard/pendant status rendering; action adapters must emit requestId and step receipts consistently.  ·  risk: A bad retry classifier could repeat a mutation. Restrict automatic retries to explicitly read-only or idempotent open/inspect steps, and mark all other steps unresolved for the owner. Recover by stopping reconciliation and preserving raw receipts.
- cost: Low background compute and storage; roughly <$0.01 per watched job. No realtime model call unless a final spoken explanation is requested.  ·  latency: Adds a 5–15 second stale-job detection interval; no impact on the first action response.
- security: Correlating browser URLs, filenames, and action history increases metadata sensitivity. Store only IDs/status/source hashes in the relay, keep detailed snippets local where possible, and enforce owner-scoped access.
- depends on: Consistent requestId/stepId propagation across /pipeline, /jobs, browser heartbeat, and Mac action receipts; A durable background scheduler/worker (not a realtime turn); Typed action result metadata identifying read-only/idempotent steps


## What it asked for

_Nothing._
