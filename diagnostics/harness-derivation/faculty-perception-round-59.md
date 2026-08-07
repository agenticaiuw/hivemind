# Harness derivation — faculty-perception — round 59

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-observation** — At 2026-08-07T12:08:30Z, /observe reports foreground Claude (com.anthropic.claudefordesktop), 16 running apps, and AI Pendant Agent PID 25245. Accessibility and Screen Recording are not trusted for the running com.aipendant.agent binary; synthesized UI events are rejected, and UI receipts cannot be trusted. AppleScript automation grants are present for System Events, Finder, Calendar, Mail, Notes, Messages, Safari, Chrome and others.
  - evidence: GET /observe HTTP 200 at 2026-08-07T12:08:30.296Z
- **browser-state** — At 2026-08-07T12:08:30Z, browser extension home-chrome is online but has no attached tab/window metadata and 5 pending commands. /observe lists 3 durable sessions, including default at https://time.is/UTC last used 06:26Z and two probe forms last used 05:40Z.
  - evidence: GET /browser/status and GET /observe HTTP 200 at 2026-08-07T12:08:30Z
- **audio-pipeline** — The live pipeline contains a completed Mac TTS response rendered as 24,000 Hz mono s16le PCM: 75,734 bytes, 1,578 ms, no clipping. A separate realtime input job recorded 937,500 bytes at 15,625 Hz mono and uploaded successfully, so output is verified at 24 kHz while input remains observed at 15.625 kHz.
  - evidence: GET /pipeline HTTP 200; events pipe_evt_d9e30c71... and pipe_evt_b716e091...
- **timezone-consistency** — The owner projection states timezone America/Chicago, while live GET /machine-context reports machine timezone America/New_York. Any scheduled spoken time or date must treat timezone as unresolved rather than silently using machine timezone.
  - evidence: discover:owner remembered timezone America/Chicago; GET /machine-context HTTP 200 reports timezone America/New_York

## Capabilities it proposed

### "“Is everything actually connected and trustworthy right now—and if not, what can still safely be done?”"
- **useful because:** The system currently reports browser online and jobs successful even when the browser has five queued commands, no attached tab metadata, and Mac UI receipts are known false because Accessibility is untrusted. A perception-first answer would distinguish reachable, stale, and deceptive state before judgement or action relies on it, and would flag the owner-vs-machine timezone conflict for scheduled work. It only speaks a compact health verdict; it does not execute anything.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background; deterministic evidence aggregation first, with a cheap text model only to compress the cited findings. Realtime is unnecessary unless the owner asks during a live voice turn.
- **latency:** 1–3 seconds for parallel reads; pendant should receive a short verdict first, with a detailed cited report available asynchronously.
- **cost:** Usually near-zero model cost when rule-based; under $0.01 when a small summarizer is needed. Dominant cost is context-free status requests, not inference.
- **security:** Expose only capability/health metadata, never page contents, tokens, or secret captured facts. Treat /observe accessibility.trusted=false as a hard warning: do not claim UI actions succeeded. Browser/account inspection still requires the existing logged-in-session policy; no mutation is performed.
- **missing:** A typed cross-surface perception snapshot schema with freshness/age, trust level, and safe-operation classes; A relay route that merges Mac /observe, /ops/status, /browser/status, /pipeline, and durable job state; A pendant spoken status command and dashboard view that cite which observation caused each warning

### "“I lost connection—resume the unfinished thing from exactly where you stopped, and tell me what changed while I was away.”"
- **useful because:** A durable job can finish after the owner leaves, but today's evidence shows pipeline runs can remain processing, the pendant can surface held offline alerts, and browser commands can sit pending without an attached tab. The owner needs one continuity operation that reconstructs the last safe checkpoint across relay, Mac job receipts, browser session state, and pendant delivery—without repeating completed steps or pretending a UI action succeeded.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background cheap model for checkpoint summarization and reconciliation; deterministic state machine for step identity, idempotency, and resume eligibility. Realtime only announces the short result when the pendant reconnects.
- **latency:** On reconnect, a terse checkpoint should arrive within 2 seconds; full reconciliation can continue in the background for 10–30 seconds.
- **cost:** Typically <$0.01 per resume using a small model; durable state reads and browser/Mac probes dominate, not inference.
- **security:** Never replay irreversible steps automatically. Require confirmation for sends, purchases, deletes, or submissions. Bind checkpoints to job ID, browser tab/session ID, and an idempotency key; invalidate checkpoints when authentication or page identity changes. Mark any UI receipt untrusted while /observe accessibility.trusted=false. Keep private page text local to the Mac/browser and send only hashes, statuses, and requested excerpts to relay.
- **missing:** A durable checkpoint protocol shared by relay jobs, Mac jobs, and browser commands; Per-step idempotency keys and explicit resumable/non-resumable classification in receipts; A continuity event stream with delivery and acknowledgement state for pendant offline buffering; A reconciliation endpoint that compares last checkpoint, current job receipts, browser session/tab identity, and pipeline events

### "“Move this conversation to my Mac without making me repeat myself—open the right work context there, and keep the pendant as my remote.”"
- **useful because:** Today the pendant, relay, Mac agent, and browser each know fragments of the current interaction, but there is no owner-visible, atomic transfer of the live conversational state. The owner must repeat the goal and manually recover the relevant tabs or job. A true handoff would preserve the partial transcript, unresolved question, cited evidence, current job/checkpoint, and confirmation policy, then let the Mac take over while the pendant remains the notification and approval channel.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime only for the short spoken handoff acknowledgement. A cheaper background model should compress the transcript into a typed handoff packet; deterministic routing should select the Mac session and browser context.
- **latency:** Acknowledge on the pendant in under 500 ms; deliver the handoff packet and open the selected Mac context within 3 seconds. If browser attachment or Mac reachability is unavailable, retain the packet and explain that no transfer occurred.
- **cost:** Usually <$0.01 per handoff with a small summarizer; the dominant cost is not model inference but durable packet storage and optional browser context restoration.
- **security:** Do not transmit unrelated microphone history or private page contents. Scope the packet to the active turn, selected source tabs, and explicitly relevant job records; encrypt it in relay storage and expire it after handoff completion. Opening a page is reversible, but sending, purchasing, deleting, or submitting remains a separate confirmation on the pendant. Include an explicit “Mac UI untrusted” state when Accessibility is unavailable rather than claiming the context was opened.
- **missing:** A versioned handoff-packet schema containing transcript span, intent, evidence references, unresolved slots, selected session/tab IDs, job/checkpoint IDs, and policy state; An atomic relay transfer protocol with acknowledgement, expiry, and exactly-once ownership transition between pendant and Mac; Mac and browser handlers that restore context without replaying actions, plus a pendant control to return ownership; A spoken/dashboard indication distinguishing packet delivered, context restored, and action actually performed


## Changes it proposed to its own stack

### `mac-harness` — Make action receipts evidence-aware: before and after any ui_click, ui_menu, type_text, or press_keys step, attach the latest /observe accessibility/inputReachability snapshot and set receipt status to blocked_or_unverified when trusted=false or uiActionsWillReachTheScreen=false. Where a declared AppleScript equivalent exists, offer it as a separate verified route; never label the original UI step successful merely because the call returned. Add a dashboard banner and relay-visible machine-readable trust field.
- **owner gets:** The owner stops hearing “done” when nothing reached the screen. On this Mac, the running AI Pendant Agent is explicitly rejecting synthesized events, yet receipts can still report success. This turns an invisible failure into an honest explanation and often preserves progress through already-granted AppleScript automation.
- effort: Medium: central receipt middleware, observation snapshot attachment, action capability metadata, and tests for stale permission changes. No owner-side code changes beyond the existing agent update.  ·  risk: Some previously successful-looking UI jobs will become unverified or blocked, which is intentionally safer. Recover by retrying through AppleScript or after the owner grants permissions. Avoid stale snapshots with a short freshness TTL and a post-action probe.
- cost: Negligible API cost; a few local status reads per UI action and small receipt storage increase.  ·  latency: Adds roughly 50–200 ms per action for local observation; AppleScript fallback may be faster than failed UI interaction.
- security: Improves security by preventing false claims and by making permission state explicit. Observation metadata contains no page contents; keep it out of spoken responses unless relevant.
- depends on: A typed action capability map identifying AppleScript-safe alternatives; Existing GET /observe and /ops/status routes; Receipt/undo infrastructure from chg-5fc73ce3

### `interaction` — Add a shared interruptibility lease across pendant, relay, Mac, and browser: the owner can say or press a button to enter a timed “do not interrupt,” “safety-critical only,” or “bring me everything” state. Every queued alert, routine result, browser change, and Mac job completion is classified against that lease, held durably with priority and expiry, then delivered once with a reason and the original source. The lease must survive link loss and resolve conflicts by newest explicit owner action, not whichever node last happened to reconnect.
- **owner gets:** The owner gets control over when this hive may break their attention. A pendant alert, browser watch, scheduled briefing, or completed Mac job will no longer arrive at an arbitrary time—or disappear while offline. They can trust that quiet means intentionally quiet and that held items will be surfaced later in priority order.
- effort: Medium-to-high: shared state model in relay, local pendant cache, Mac/browser adapters, priority classifier, expiry/acknowledgement UI, and tests for reconnect races and clock disagreement.  ·  risk: A low-priority item could be delayed too long, or a safety-critical classification could be wrong. Recover with a local pendant override, a visible held-count indicator, conservative defaults for safety events, and an audit trail showing why each item was held or delivered.
- cost: Low ongoing API cost if priority rules run deterministically; occasional cheap classification model call for ambiguous notifications. Small flash/RAM and relay D1 storage increase.  ·  latency: Immediate local button state (<100 ms); delivery after lease expiry or owner override within a normal relay round trip (roughly 1–3 seconds).
- security: Reduces accidental disclosure in public settings by suppressing spoken private content until the owner explicitly resumes. The lease metadata may leave the pendant, but alert content should remain encrypted and scoped to the intended surface.
- depends on: A durable relay-side event/alert record with priority, source, expiry, and acknowledgement; Pendant-local persistence for the current lease and held-alert count; A single authoritative time policy or monotonic lease durations to handle the observed Chicago/New York timezone conflict; Adapters for existing pipeline, jobs, browser-watch, and routine results


## What it asked for

_Nothing._
## Its own summary

Round 59 established four live facts: Mac UI automation is not trustworthy for the running AI Pendant Agent binary; browser extension is online but has five pending commands and no attached tab metadata; 24 kHz mono PCM output is verified while realtime input is still observed at 15.625 kHz; and owner timezone (America/Chicago) conflicts with machine timezone (America/New_York). I recorded all four findings. I proposed (1) a cross-surface “is everything genuinely reachable?” perception verdict, (2) interruption resume with checkpoint reconciliation across pendant/relay/Mac/browser, and (3) receipt middleware that refuses to call UI actions successful when observation says events cannot reach the screen.

**Biggest unknown:** I still cannot establish pendant-local telemetry or the authoritative 24 kHz implementation state, nor the retention/acknowledgement semantics for offline continuity events. The authoritative timezone also remains unresolved. These were already requested and should not be re-requested this round; until supplied, time-sensitive speech and reconnect/resume claims must remain explicitly qualified.

