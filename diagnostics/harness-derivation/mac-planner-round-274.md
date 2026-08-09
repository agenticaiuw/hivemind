# Harness derivation — mac-planner — round 274

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-live-state-2026-08-09T01:51Z** — Mac bridge is online; AI Pendant Agent has Accessibility and Screen Recording, synthesized input posts successfully, Safari is foreground with four durable browser sessions (including USPS tracking and Google News), iPhone Mirroring is running, and the pendant itself has no relay telemetry.
  - evidence: mac_readonly_inspect(operation=running_apps) invoked GET /observe at 2026-08-09T01:51:47.900Z and returned accessibility.trusted=true, screenRecording=true, inputReachability.status=verified, browser.sessions=4, iPhone Mirroring in runningApps; faculty-perception independently reports pendant absent.

## Capabilities it proposed

### "“When I press the pendant bookmark, turn whatever I was looking at into one actionable follow-up: capture the Mac app/browser page, relate it to my calendar and recent mail, draft the task with a proposed due time, and read me the draft. Do not create or send anything until I say ‘do it’.”"
- **useful because:** Today a bookmark preserves a moment but leaves the owner to reconstruct why it mattered. This makes the physical gesture a reliable bridge from fleeting attention to a reviewable action, using the pendant, always-awake relay, Mac state, and browser session together.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** background for context joining and draft generation; realtime only for the short spoken acknowledgement and confirmation
- **latency:** Acknowledge the bookmark locally immediately; return a draft within 10 seconds. Calendar/mail reads and context collection can continue asynchronously.
- **cost:** About $0.01–$0.05 per capture depending on context size; model summarization dominates, while Mac/browser reads are local.
- **security:** The capture may expose the current URL, page title, mail snippets, and calendar context to the relay. Redact page bodies and message bodies by default, retain only the selected evidence and a short-lived encrypted draft, and require an explicit spoken confirmation before creating a task, reminder, or external change.
- **missing:** A real Mac semantic-context read returning foreground document identity, selected text, and active browser frame (the existing browser-tabs/host observation is insufficient); A durable capture correlation contract joining the pendant bookmark event, Mac observation, and generated draft; A task/reminder creation endpoint with an auditable confirmation receipt

### "“Run a complete pendant health check now, without recording me: exercise the synthetic audio fixture, verify the Mac-to-USB bench link, collect radio/codec counters, compare them with the last check, and tell me whether a real call is safe. If anything fails, leave a repair report I can hand to you later.”"
- **useful because:** The owner currently has to know firmware and serial procedures to distinguish a dead microphone, codec regression, or transport problem. This turns the physically connected pendant and bridge into a one-command, evidence-based readiness check and prevents a bad call from being discovered only after speaking.
- **path:** pendant → mac-planner → relay → dashboard
- **model tier:** background/cheap model for counter comparison and report writing; no realtime model unless the owner asks a spoken follow-up
- **latency:** Start within 2 seconds, finish a normal fixture run in under 30 seconds, and return a concise verdict plus a durable report.
- **cost:** Under $0.01 per run; almost all work is local serial I/O and report comparison.
- **security:** The fixture must use synthetic frames only and never open the microphone. Store raw logs locally with bounded retention; send aggregate counters and hashes to the relay, not PCM or arbitrary serial output. A repair action must remain a separate explicitly requested job.
- **missing:** A bounded, typed USB-serial bench procedure that can arm the accepted diagnostic fixture and read framed results with timeouts; A signed readiness schema and baseline store for codec, drop, underrun, and clock counters; A relay route that correlates the bench run, report, and pendant firmware version into one receipt

### "“Watch the important browser tasks I leave half-finished—forms, applications, bookings, and checkout pages—and tell me on the pendant if the session is about to expire, a required field becomes invalid, availability changes, or the price changes. Save a private resume card on my Mac, but never submit or purchase anything.”"
- **useful because:** A browser tab is not a durable task: sleep, session expiry, and changing inventory silently destroy work. This makes the browser's private session, the relay's monitoring, the Mac's local resume artifact, and the pendant's interruptible alert act as one safety net without granting it authority to submit.
- **path:** browser → relay → mac-planner → pendant → dashboard
- **model tier:** Cheap background model for change classification and deduplication; realtime only to phrase an alert if the owner asks what changed
- **latency:** Poll only explicitly enrolled tabs every 5–15 minutes; surface a high-confidence alert within one polling interval and write the resume card in under 3 seconds.
- **cost:** Roughly $0.01–$0.03 per monitored tab per day; browser snapshots and polling dominate, with model calls only on material diffs.
- **security:** Page contents and authenticated URLs remain sensitive. Enrollment must be per-tab, with domain and field redaction; never transmit passwords, payment fields, tokens, or full page bodies. Resume cards should be local and encrypted, alerts should contain only the changed label/value, and submission remains impossible in this capability.
- **missing:** A durable tab-enrollment and expiry policy rather than an ad-hoc browser command; A browser diff extractor that can identify invalid fields, session-expiry signals, price, and availability while redacting secrets; A pendant alert payload type that carries a resume-card identifier and expiry, not just free-form text

### "“Carry out this multi-step request across my Mac and browser as one operation: if any step fails or the page changes underneath you, stop, preserve exactly what succeeded, undo only the reversible changes, and give me a repairable receipt instead of leaving half-finished work.”"
- **useful because:** The current system can execute desktop and browser actions, but a failure between surfaces can leave an app, file, and logged-in page in different states. The owner needs one understandable outcome—completed, safely paused, or recoverable—rather than reconstructing partial mutations by hand.
- **path:** relay → mac-planner → browser → dashboard
- **model tier:** Background model for plan decomposition and receipt explanation; realtime only for a low-latency spoken status update.
- **latency:** Preflight in under 2 seconds; execute ordinary bundles within the task's native duration; emit a failure/repair receipt immediately when a step diverges.
- **cost:** About $0.02–$0.08 per bundle, dominated by planning and verification snapshots; compensation is local execution rather than model cost.
- **security:** Cross-surface plans can touch authenticated pages and local files. Record a redacted resource manifest, never persist secrets or page bodies, and make compensation deterministic and auditable. External sends, purchases, and deletions must remain explicitly classified as non-compensatable operations.
- **missing:** A cross-surface transaction coordinator with checkpoints, idempotency keys, and compensation steps; Browser and Mac postcondition assertions that can detect an unexpected page or app state; A receipt format that reports committed, compensated, and unresolved steps separately

### "“When I put the pendant into privacy mode, make the whole hive forget the live context boundary: stop Mac and browser observation, cancel queued context reads, prevent new screenshots or page snapshots, and show me a local confirmation. When I release privacy mode, resume only with a fresh session—not with anything collected while I was private.”"
- **useful because:** A local privacy latch protects the pendant, but the owner can still have a Mac or browser worker observing independently. Privacy needs to propagate across every surface and have a verifiable cutoff, so the owner can trust the gesture even when the relay or Mac is busy.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** No expensive model is needed for enforcement; use realtime only to acknowledge state if the owner is speaking, and background processing only to reconcile receipts after resumption.
- **latency:** Pendant-side mute and local indication immediately; relay cancellation under 500 ms when connected; stale workers must be rejected by an epoch token even during a network partition.
- **cost:** Negligible per toggle; implementation is protocol/state work, not inference.
- **security:** Privacy state must fail closed locally and survive link loss. Pending snapshots, selected text, and page bodies must be deleted or cryptographically rendered unusable at the privacy boundary. A network outage must not delay entering or leaving local privacy mode.
- **missing:** A hive-wide privacy epoch propagated to relay, Mac, and browser workers; Cancellation and stale-result rejection in observation jobs; A verifiable privacy receipt proving which workers stopped and which queued artifacts were discarded

### "“Take care of this objective while I am away: keep checking the enrolled Mac/browser state until the condition is met, pause when the site asks for a human decision, and notify me on the pendant only when there is a meaningful change. Give the objective an expiry, a spend/action budget, and a one-sentence stop command that cancels every worker.”"
- **useful because:** Today a plan is mostly an immediate action or an opaque background job. The owner needs a bounded delegation that can survive sleep, retries, and a dropped pendant link without becoming an unattended agent with indefinite authority.
- **path:** relay → mac-planner → browser → pendant → dashboard
- **model tier:** Cheap background model for periodic state comparison and stop-condition evaluation; realtime only for concise pendant alerts and spoken cancellation.
- **latency:** Create the objective in under 3 seconds; poll only at its declared interval; propagate cancellation within one interval and reject late results immediately.
- **cost:** About $0.01–$0.10 per objective per day depending on polling frequency and page complexity; browser snapshots and model-based change classification dominate.
- **security:** Delegation must be scoped to named tabs/apps, domains, data classes, duration, and action budget. No enrollment of a new domain or external send without a fresh confirmation. Every poll and decision needs a redacted audit trail; expiration must revoke credentials/leases rather than merely stop the scheduler.
- **missing:** A first-class objective lease with owner, scope, expiry, budget, stop conditions, and cancellation epoch; A scheduler that can wake Mac/browser workers and deduplicate retries across relay restarts; A pendant/dashboard control that exposes active objectives and supports an unambiguous global stop command


## What it asked for

_Nothing._
## Its own summary

Recorded three capabilities beyond the backlog: cross-surface transactional execution with compensation, hive-wide privacy epoch propagation, and bounded long-running objective leases with cancellation and expiry.

**Biggest unknown:** Whether the relay already has an unobserved scheduler/lease primitive; this round's tools were unavailable for further discovery, so each proposal names the missing contract rather than assuming it exists.

