# Harness derivation — relay-realtime — round 224

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If my Mac is asleep, queue the request and handle it when it wakes."
- **useful because:** The owner is often away from the Mac. Queuing makes voice commands dependable instead of brittle.
- **path:** relay → mac-bridge → mac-planner
- **model tier:** Realtime to capture intent; cheaper background to hold and retry.
- **latency:** Immediate acknowledgement; execution when the Mac is available.
- **cost:** Moderate: durable queue storage plus retry logic; minimal per attempt.
- **security:** Queued commands are powerful. Keep an audit trail and allow cancellation. Confirm destructive actions.
- **missing:** Durable job queue at relay; Wake detection and retry policy; Cancel/undo path for queued jobs

### "When I say “leave this here and let me pick it up later,” have the pendant save the exact work handoff—what I was trying to do, the relevant Mac app state, browser tabs and drafts, and unresolved choices—then let me say “resume my last handoff” from anywhere and restore or reopen it on the Mac."
- **useful because:** The owner can walk away from the Mac without losing the thread of work. A spoken handoff is more useful than a generic reminder because it preserves the actionable state and gives the Mac enough context to continue rather than merely reopening an app.
- **path:** pendant → relay → mac-planner → browser-extension → mac-terminal → dashboard
- **model tier:** Use realtime only to capture and confirm the short handoff; use the cheaper background planner to normalize the goal and reconstruct state. The Mac planner restores apps and files, while the browser facet snapshots and reopens authenticated tab state without exporting secrets.
- **latency:** Capture and acknowledge in under 2 seconds; restoration may take 10–30 seconds and must produce a completion or needs-attention alert.
- **cost:** About $0.01–$0.05 per handoff/resume, dominated by planner context and optional screenshot/state summarization; routine acknowledgements should be local or relay-only.
- **security:** Handoff records can contain private tab URLs, drafts, and screen text. Keep browser credentials in the browser session, store only encrypted references and minimum excerpts, expire handoffs by default, and require an explicit spoken target before restoring or editing anything.
- **missing:** A first-class handoff record containing goal, app/window identifiers, browser tab/session references, draft hashes, and unresolved decisions; Mac and browser snapshot adapters plus an idempotent restore operation; A pendant command and relay route that can retrieve the owner’s latest handoff across sessions

### "When the pendant misses or mangles something, let me ask “why did that happen?” and have the system diagnose the whole path: inspect the pendant’s audio counters and link health, correlate the relay voice run and Mac/bridge logs, run a short hardware probe over USB, and tell me the measured cause and the one fix it recommends—or apply a reversible fix if I say “fix it.”"
- **useful because:** Today a silent failure looks like the AI ignoring the owner. This would turn the worn device and its attached Mac from a black box into a self-diagnosing instrument, reducing debugging from a code investigation to one spoken question and preserving evidence from the exact failed utterance.
- **path:** pendant → relay → mac-terminal → mac-planner → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** Realtime should only explain the already-collected measurements. A cheaper diagnostic worker should correlate logs and run deterministic probes; use the expensive model only when measurements conflict or the owner asks for a natural explanation.
- **latency:** Return basic counters in 2 seconds; a full USB/log correlation in under 20 seconds. Never claim a fix until a post-fix probe verifies it.
- **cost:** Roughly $0.005–$0.03 per diagnosis; most work is local shell and serial I/O, with model cost only for correlation and speech.
- **security:** Diagnostics include transcripts, audio timing, serial identifiers, and local paths. Keep raw audio local and send counters/hashes by default; USB repair commands must be allowlisted, reversible, logged, and followed by measured verification.
- **missing:** A unified voice-run correlation ID carried into pendant, bridge, relay, and Mac logs; Read-only serial diagnostic commands and a hardware probe action in the Mac agent; A diagnosis schema that records hypothesis, measurements, confidence, and post-fix verification rather than a free-form answer

### "Let me say “watch my pendant project tonight; wake me only if it regresses.” The relay should run the project’s real tests on the Mac and inspect authenticated CI or issue pages when available, compare failures with the last known-good run, and send the pendant one short alert containing the first actionable regression and a link or command to reproduce it."
- **useful because:** The owner cannot keep a terminal open or babysit a build while away. A regression-only sentinel turns the always-worn pendant into an overnight engineering safety net instead of a device that can only answer while the owner is actively talking.
- **path:** pendant → relay → mac-terminal → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic test commands and diffing in a background worker; use a small model only to cluster a new failure against prior receipts and phrase the alert. Realtime is needed only when the owner asks a follow-up.
- **latency:** Register in under 3 seconds; each check may take several minutes, but the owner should receive a push within 15 seconds of a confirmed regression. No alert for a clean or unchanged failure.
- **cost:** Low when clean (shell/test execution plus storage); approximately $0.01–$0.10 per changed failure depending on log length and CI-page summarization.
- **security:** Test logs can expose source, tokens, and private issue text. Run only owner-selected commands, redact secrets before relay storage, keep authenticated browser content on the Mac/browser surface, and make the watch visibly cancellable from the pendant or dashboard.
- **missing:** A durable recurring worker that remains alive while the owner is away and survives relay restarts; A per-watch baseline and semantic failure-diff store, including suppression of repeated known failures; A real Mac test-runner action with bounded resource use and a completion callback into the existing pendant inbox/push path


## Changes it proposed to its own stack

### `integration` — Introduce a relay-side durable queue for requests when the Mac is offline, with replay on reconnect, plus cancellation/undo and an audit trail visible via jobs endpoints.
- **owner gets:** Voice commands become dependable even when the Mac is asleep or out of reach. The owner gets confidence that requests will run.
- effort: High: queue storage, retry policy, idempotency keys, reconciliation on reconnect.  ·  risk: High: could duplicate actions or run out of order; mitigate with idempotency, receipts, and explicit ordering.
- cost: Moderate ongoing storage and retry traffic.  ·  latency: Immediate acknowledgement; deferred execution latency depends on reconnect.
- security: Queued actions are sensitive; require confirmation for destructive actions and keep receipts/undo.
- depends on: relay capability manifest; job status receipts; mac reconnect events


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities: (1) durable cross-device work handoffs that capture actionable Mac/browser state and restore it later from the pendant; (2) spoken, evidence-backed diagnosis of a failed utterance across pendant, bridge, relay, and Mac, with verified reversible repair; and (3) an overnight regression sentinel that runs the project’s tests while the owner is away and pushes only new actionable failures. The main missing pieces are durable handoff/state references, a unified diagnostic correlation and serial probe schema, and a restart-surviving recurring worker with baseline diffing and push delivery. Existing plan/execute, watches/routines, receipts, browser, ops, and pipeline routes are the building blocks.

**Biggest unknown:** Whether the existing workbench, watches, and routines implementations already expose enough persistence and callback semantics to support these without new routes; discovery is unavailable this round, so I have treated the stated missing pieces as implementation gaps rather than asserting they are absent.

