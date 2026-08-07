# Harness derivation — relay-realtime — round 31

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Keep working on that task after I step away, and tell me exactly what happened when it’s done."
- **useful because:** The owner can start something from the pendant, then go live their life. They get a clear, trustworthy completion report without babysitting the Mac or keeping the session open.
- **path:** relay → mac-bridge → browser → dashboard
- **model tier:** Realtime only for the brief spoken acknowledgement; planning and execution should use a cheaper planner model on the Mac and browser harness.
- **latency:** Under a second to acknowledge. Minutes to hours for execution is fine as long as status is trackable and completion is announced reliably.
- **cost:** Low per invocation at the relay; dominant cost is downstream planning/execution and any authenticated browser work.
- **security:** Authenticated sessions and extracted data must be scoped to the task, logged with provenance, and never used for unrelated goals. Completion reports should quote sources, not raw secrets.
- **missing:** Durable job runner that persists across relay restarts; Unified job status and receipts across Mac and browser steps; Notification path to the pendant when the relay is not actively in a voice run; Typed context service to avoid resending large context every turn

### "While I’m away from my Mac, let me say ‘handle this’ and then interrupt, redirect, or ask for the exact status of that task from the pendant; have the Mac/browser continue from the last verified checkpoint and tell me what actually happened."
- **useful because:** Today a spoken delegation is effectively fire-and-forget: the owner cannot maintain a live, trustworthy conversation with work happening on an unattended Mac or in an authenticated browser. This would make the pendant a real remote control for multi-step work, not merely a voice inbox, while preserving factual boundaries between planned, attempted, and completed actions.
- **path:** pendant → relay → mac-bridge → mac-planner → browser → dashboard
- **model tier:** Use relay-realtime only for intent capture, concise status, interruption, and clarification. Use the slower mac-planner for planning and checkpoint recovery; use mac-vision/browser harness only for the concrete UI steps. Use a cheap background model for summarizing receipts when the owner asks for a briefing.
- **latency:** Acknowledge and create a task session in under 500 ms; interruption/cancel must reach the active worker within 2 seconds when online. Checkpoint updates may arrive asynchronously, with a spoken milestone under 3 seconds after each meaningful state change.
- **cost:** About one realtime turn for each owner utterance, plus planner tokens per checkpoint/replan; roughly 1–3x the cost of a normal delegation depending on interruptions. Most status fan-out should be event payloads, not repeated full conversation context.
- **security:** The relay must authenticate the pendant task session and bind browser work to its existing tab/session identity. Do not claim success from intent or a click receipt: each checkpoint needs an observed result and timestamp. Cancellation must be idempotent, and an interrupted action must be marked unknown if its outcome cannot be observed. Task summaries should redact page contents and secrets by default; require explicit owner wording before transmitting sensitive extracted data over voice. Dashboard audit history should show every plan, redirect, cancellation, and receipt.
- **missing:** A durable task-session and checkpoint protocol shared by relay, mac-planner, mac-vision, and browser bridge, including idempotency keys and explicit states (planned, running, waiting, redirected, cancelled, succeeded, failed, unknown).; Server push from workers to the relay/pendant, with compact spoken milestone events and reconnect/replay support.; A pendant command grammar for addressing the active task (status, pause, cancel, redirect, continue) without requiring the owner to repeat a job id.; Planner support for resuming from the last verified checkpoint rather than replanning from the original goal, and for safely handling an owner redirect.; Browser/Mac execution hooks that can stop between actions and emit typed observed-result receipts.; A dashboard timeline that exposes the same task session and makes unknown outcomes conspicuous.

### "If a browser task reaches a login challenge, CAPTCHA, device approval, or other step only I can complete, ask me on the pendant with the minimum safe description, let me answer or approve by voice/button, and resume the exact browser task without making me walk to the Mac."
- **useful because:** Authenticated browser sessions are where the owner’s reach is strongest but also where unattended automation stops today. A wearable-mediated human checkpoint would let useful work continue while the owner is away, without handing credentials or unrestricted challenge data to the model.
- **path:** browser → mac-bridge → relay → pendant → dashboard
- **model tier:** Use browser/mac harnesses to detect and suspend at a challenge. Use relay-realtime only to explain the challenge category and collect the owner’s deliberate response. Use deterministic protocol handling—not a language model—to pass an approval or one-time response back to the browser; use a cheap background model only to summarize the completed task.
- **latency:** Challenge notification under 2 seconds after detection; owner response acknowledged immediately and browser resume within 3 seconds. Expire an unanswered challenge rather than holding an automation session indefinitely.
- **cost:** A few realtime turns only when a challenge occurs; negligible model cost for the normal path. Engineering/storage cost is dominated by secure short-lived challenge state and browser-session recovery.
- **security:** Never read or speak passwords, full OTPs, recovery codes, or CAPTCHA image contents unless the owner explicitly requests that exact interaction. Prefer a single-use pendant button confirmation for approvals and encrypted entry for codes. Bind the response to browser session, origin, tab, task id, and a nonce; reject replay and expire quickly. Clearly distinguish ‘approve’, ‘deny’, and ‘enter code’. Record category, origin, and outcome, not secret values. The owner must be able to cancel from the pendant.
- **missing:** A browser-bridge challenge detector and pause/resume API with origin, tab, task, nonce, and expiry binding.; An authenticated, encrypted pendant-to-browser response channel supporting button approval and optional speech-to-text code entry without persistence.; Relay push events and a compact spoken challenge vocabulary, plus reconnect/replay behavior.; Mac/browser harness rules for preserving the exact session and refusing to continue if origin or page identity changes.; Dashboard audit records that prove which challenge was approved without storing its secret.


## Changes it proposed to its own stack

### `routines` — Add a cross-surface durable job system with scheduling primitives (cron-like cadence and single-run alarms). Jobs can target Mac planner, browser harness, or public web reads, and must persist status, receipts, and provenance. Include a notification mechanism that can queue a spoken summary for the next pendant connection.
- **owner gets:** This unlocks real “set it and forget it” workflows: watch pages, prep briefs overnight, and finish tasks after the owner walks away, then report back reliably.
- effort: High: requires storage schema, worker cron/alarm wiring, job lifecycle state machine, and integrations in Mac and browser harnesses.  ·  risk: Jobs could run at the wrong time or duplicate. Mitigate with idempotency keys, explicit schedules, and safe defaults; provide a kill switch and per-job visibility.
- cost: Moderate ongoing: storage reads/writes and occasional compute. Higher only for frequent browser automation.  ·  latency: Improves perceived latency by moving work off the critical voice path; acknowledgement remains fast.
- security: High sensitivity: authenticated sessions, extracted data, and action receipts must be access-controlled, encrypted at rest, and scoped per job.
- depends on: Persistent storage for jobs and receipts; Browser command queue with typed results (see chg-14accc01); Typed context service to keep payloads small

### `hardware` — Make the pendant’s single button a locally handled, fail-safe global halt control when held for a configurable interval (for example, 2 seconds): firmware immediately stops issuing new relay work, sends a signed emergency-stop event when LTE is available, and the relay propagates cancellation to Mac, browser, and any active task session. The LED gives unmistakable halted/acknowledged feedback; short press remains normal interaction. Add a cryptographic monotonic event counter so reconnects cannot replay an old halt or resume command.
- **owner gets:** If an unattended Mac or authenticated browser begins doing the wrong thing, the owner can stop the whole hive from wherever they are, even before they can formulate a spoken command or reach the computer. This is a physical escape hatch, not a routine approval gate, and is especially valuable because the pendant is worn while the Mac is unattended.
- effort: Firmware button-state machine and signed event persistence; relay fan-out and cancellation semantics across planner, Mac, and browser workers; a visible dashboard state; integration tests for LTE loss, reconnect, duplicate events, and an in-flight irreversible action. Resume should require an explicit spoken command or a new deliberate long press, never an automatic reconnect.  ·  risk: A false long press could pause legitimate work, so the gesture must be distinct and LED-confirmed; cancellation cannot undo an already-completed external mutation, which must be reported as unknown/complete. If LTE is unavailable, local halt state must persist and block queued work until the relay receives it. Recovery is an explicit resume with a fresh task/session nonce.
- cost: No per-use model cost. Firmware/storage work is small; relay and worker cancellation plumbing is moderate. Existing button/LED hardware can support it, so rough hardware cost is $0 and negligible power increase (brief LTE transmit and LED indication).  ·  latency: Immediate local LED/state response; remote halt typically bounded by LTE uplink plus relay fan-out, target under 2 seconds. It adds no latency to ordinary voice interactions.
- security: Improves safety if event signing, monotonic counters, and device authentication are enforced. The stop event should contain no page content or secrets. Do not expose a remote API that can silently clear the halted state.
- depends on: A shared task-session cancellation protocol with idempotent stop semantics across relay, Mac, browser, and planner.; Durable relay push/reconnect handling so a stop issued during connectivity loss is delivered before queued work resumes.; A firmware update path and persisted halt bit that survives reboot.

### `interaction` — Add a compact, stable pendant status vocabulary for remote work: the relay sends signed outcome/events and firmware renders them as distinct LED patterns (queued, waiting for owner, running, succeeded, failed, unknown, globally halted). A button press cycles the last few task summaries as pattern groups and requests a spoken detail only when the link is available; the relay keeps a tiny replayable status ring so a missed push is not lost.
- **owner gets:** The owner can tell at a glance—in a meeting, noisy street, or with audio muted—whether something delegated from the pendant finished, is waiting on them, or needs attention. It turns the only always-worn output channel into useful ambient feedback without requiring a phone screen.
- effort: Define a human-testable pattern grammar, implement firmware rendering and persistence, add relay event compression/replay, and add dashboard previews/accessibility documentation. Keep normal short-press behavior unambiguous and reserve long-press for the emergency halt.  ·  risk: LED patterns can be missed or misread; never treat them as proof of success, and make the spoken/dashboard receipt authoritative. Avoid flashing that attracts unwanted attention; include a quiet mode and bounded repetition. On stale connectivity, show ‘unknown/stale’ rather than the last success as current.
- cost: No model cost and no new hardware; small firmware and relay work. LED duty cycle should remain brief to avoid measurable battery impact.  ·  latency: Immediate for cached local state; push updates target sub-second after relay receipt. No impact on voice response latency.
- security: Patterns must not encode sensitive content, account names, or message previews—only coarse state and a non-sensitive sequence marker. Signed events prevent a stale or forged worker from presenting a false success.
- depends on: A durable task/event session with typed observed-result receipts and replay after reconnect.; Firmware update support and a documented button gesture partition shared with emergency stop.; Relay push delivery to the pendant and a persisted last-status ring.


## What it asked for

_Nothing._
## Its own summary

Recorded four new, cross-node additions: resumable interruptible remote task sessions; secure pendant-mediated browser challenge completion; a physical global emergency halt for unattended Mac/browser work; and privacy-preserving LED status feedback with replay. Each includes the missing protocol, firmware, push, and audit changes rather than assuming today’s wiring.

**Biggest unknown:** Whether any of these exact concepts already exist in the unseen backlog; I intentionally did not rediscover or restate backlog entries this round as instructed.

