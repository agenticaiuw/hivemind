# Harness derivation — mac-planner — round 54

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-readiness** — Live Mac ops status is degraded: fullControlMode=true and relay/mac bridge online, but accessibility trusted=false (detail: Enable Accessibility for AI Pendant Agent), screenRecording granted=false, computer-use loop disabled, browser extension online=false with home-chrome only and pendingCommands=3. The newly granted mac_readonly_inspect and mac_read_sources tools currently return 'schema but has no implementation yet'.
  - evidence: GET /ops/status HTTP 200 at 2026-08-07T10:30Z; parallel calls to mac_readonly_inspect and mac_read_sources returned implementation errors.

## Capabilities it proposed

### "Make my Mac ready for automation, and tell me when it is working."
- **useful because:** Today the relay is reachable and full-control is enabled, but the Mac agent reports accessibility and screen-recording permissions missing, so GUI plans silently cannot run; the browser bridge is also offline with three pending commands. A single spoken request should diagnose readiness, open only the exact System Settings panes, guide the owner from the pendant, re-check, and leave a durable receipt instead of making them debug permissions or lose a queued task.
- **path:** pendant → relay → mac-bridge → dashboard → browser
- **model tier:** background for diagnosis and state comparison; realtime only for the short spoken guidance loop
- **latency:** Initial diagnosis under 2 seconds; each permission re-check under 1 second; no polling more often than every 5 seconds; queued browser work remains paused until a positive heartbeat and is resumed only when its step is idempotent.
- **cost:** About $0.01–$0.05 per setup invocation, dominated by the background model only when interpreting unfamiliar permission errors; most checks are local HTTP/state reads. No audio upload beyond the owner's spoken command.
- **security:** Do not request or infer passwords, screen contents, or browser page data. Open System Settings locally and report exact missing grants; never auto-toggle security permissions. Preserve existing maximum-access execution policy, but mark pending browser mutations as paused and never replay them after reconnect without an idempotency key. Require explicit owner confirmation only for enabling permissions in macOS UI if macOS presents one.
- **missing:** A local readiness endpoint that returns typed blockers (accessibility, screen recording, automation grants, browser heartbeat freshness) and remediation deep links.; A pendant/relay job state for waiting_on_owner with a short spoken instruction and durable timeout.; A reconnect reconciler that classifies pending browser commands as idempotent read vs mutation and resumes only the former automatically.; A small dashboard card showing blocker, last check, and the exact next step.

### "Make sure this actually gets done: keep the commitment with me, notice whether I completed it across my Mac and logged-in browser, and nudge me on the pendant only if it is still unfinished."
- **useful because:** Today the system can create reminders or perform a desktop job, but it cannot close the loop between a spoken commitment, observable evidence of completion across multiple surfaces, and proportionate follow-up. The owner should not have to remember to check whether a draft was sent, a document was saved, or a portal task was completed; the system should distinguish 'done', 'blocked', and 'no evidence' and stop nudging as soon as it is satisfied.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use a cheap background model for commitment parsing, evidence matching, and scheduled checks; use realtime only for the initial spoken capture and an escalation conversation when the owner responds.
- **latency:** Capture under 2 seconds. Evidence checks on a configurable cadence (for example 15 minutes during an attention window), with no more than one spoken nudge per escalation level. Completion should suppress future nudges within 2 seconds of verified evidence.
- **cost:** Roughly $0.005–$0.03 per commitment per day, dominated by background semantic matching; local file/app/browser metadata checks should be free. Audio costs are limited to brief nudges and replies.
- **security:** Default to metadata and explicit evidence selectors, not continuous screen/audio recording. Browser evidence must be scoped to named tabs and redact secrets. Never infer completion from a page merely being open; require a typed success predicate or owner confirmation. A nudge can reveal sensitive task names, so support a discreet vibration/short code mode on the pendant. Expiry and cancellation must be easy and durable.
- **missing:** A first-class commitment object with owner language, success predicates, evidence sources, due window, escalation policy, privacy class, and cancellation state.; A cross-surface evidence evaluator that can consume Mac receipts/files/calendar state and browser typed results without scraping arbitrary pages.; A relay scheduler and durable state machine for pending, evidenced_done, blocked, overdue, snoozed, and cancelled, with deduplication across reconnects.; A pendant delivery mode for discreet escalation and a dashboard showing the evidence that caused completion or the reason it remains unresolved.


## Changes it proposed to its own stack

### `integration` — Add GET /readiness and a durable readiness-watch record. It should normalize /ops/status into blocker codes, permission deep links, browser heartbeat age, pending command counts, and an overall state (ready, waiting_on_owner, offline, degraded). Add POST /readiness/recheck and emit state transitions to the relay/dashboard; never expose page contents or secrets.
- **owner gets:** The owner gets an honest answer—'automation is ready' or one precise fix—rather than an apparently successful voice command that cannot control the Mac or a browser queue that silently stalls.
- effort: Small-to-medium: local-agent endpoint and macOS permission probes, relay event schema, one dashboard card, and pendant phrasing; test transitions across reboot, permission denial, and browser reconnect.  ·  risk: Permission probes can be stale and the System Settings deep link may vary by macOS release. Fall back to a generic Privacy & Security URL and show the raw blocker. A crash must not alter queued commands.
- cost: Negligible API cost; local checks are free, with one background model call only for unfamiliar errors.  ·  latency: ~100–500 ms local check; dashboard/relay transition delivery under a few seconds.
- security: Improves least-information reporting: typed permission state instead of screenshots. Must keep tokens and account identifiers out of readiness payloads.
- depends on: macOS permission probe implementation (the granted readonly inspection tool currently has no backend implementation); browser heartbeat/device capability reporting; relay durable waiting_on_owner state

### `context` — Introduce a cross-surface commitment/evidence ledger rather than treating reminders and action receipts as separate records. Each commitment stores a normalized goal, success predicates, permitted evidence sources, due/quiet windows, escalation state, and immutable evidence references. Mac and browser agents publish typed evidence events (file hash, app operation receipt, calendar mutation, scoped page predicate); the relay evaluates predicates and emits exactly-once completion or escalation events to the pendant.
- **owner gets:** The owner gets reliable follow-through instead of either a reminder that keeps nagging after completion or an action receipt that says what the system did but not whether the real-world goal happened.
- effort: Medium-to-large: new relay schema/state machine, evidence adapters on Mac and browser, predicate evaluation tests, pendant notification states, and dashboard explanation of why a commitment is considered done or blocked.  ·  risk: False positives are the main risk. Start with explicit, high-confidence predicates and label 'no evidence' separately from 'not done'; retain a manual mark-done/undo path. Reconnect replay must be idempotent and stale evidence must expire.
- cost: Small D1/storage and event costs; background model use only for initial goal normalization or ambiguous evidence, not every poll.  ·  latency: Near-real-time for local receipts; scheduled browser checks add cadence latency. Completion suppression should be event-driven rather than waiting for the next reminder.
- security: Evidence references should contain hashes, app/tab identifiers, and redacted snippets—not raw mail, page bodies, or screenshots by default. Per-commitment privacy class controls which surface may inspect it.
- depends on: Typed Mac action receipts and browser results; Durable relay scheduler and exactly-once event handling; Pendant notification/quiet-mode protocol


## What it asked for

_Nothing._
## Its own summary

Discovered and recorded a concrete live blocker: relay and Mac bridge are online, but Accessibility and Screen Recording are missing; computer-use is disabled; Chrome bridge is offline with 3 pending commands. The newly granted readonly Mac/source tools exist in schema only and currently have no implementation. I proposed a cross-surface 'Make my Mac ready for automation' flow and the supporting typed /readiness endpoint with durable waiting-on-owner and safe browser-queue reconciliation. I also asked browser-extension to expose Safari heartbeat/registration distinctly from stale Chrome.

**Biggest unknown:** Whether macOS permission probes and Safari extension heartbeat can be implemented in this build; without them, readiness guidance and browser recovery cannot be verified end to end.

