# Harness derivation — faculty-judgement — round 41

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Before you act, tell me whether you can actually reach the right device and whether the time zone is settled; if not, ask me one short question and wait. Never say something happened when it only looked like it did."
- **useful because:** The owner currently has a dangerous split between remembered America/Chicago and live Mac America/New_York, while Accessibility and Screen Recording are disabled and UI actions can falsely report success. This makes reminders, calendar work, and computer actions silently wrong. A single arbitration step turns uncertainty into an explicit, recoverable decision instead of a misleading completion.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** Cheap background classifier/rules for reachability, permission, timezone, and receipt validation; realtime model only speaks the one-line question or result. No expensive reasoning unless sources disagree after deterministic checks.
- **latency:** Under 300 ms for local state checks; at most one short spoken clarification. If the owner does not answer, hold the job with a durable pending reason and resume when resolved.
- **cost:** <$0.01 per invocation; dominated by one compact state snapshot and occasional clarification, not model tokens.
- **security:** Expose only capability states and timezone identifiers, not page contents or secrets. Never infer consent from silence. Require confirmation for destructive actions and for changing the canonical timezone. Keep an auditable source/timestamp trail for every preflight and receipt.
- **missing:** A shared preflight/arbitration contract consumed by every action surface; A durable pending-decision record that can resume jobs after the owner resolves timezone or permissions; Mac permission-state and browser-heartbeat events wired into receipt validation; A single canonical timezone setting with explicit owner resolution when memory and live OS disagree

### "When I travel or my devices disagree about time, ask whether I mean home time or where I am before creating anything, and remember that choice only for this task."
- **useful because:** A single remembered timezone is too blunt: the owner's calendar, reminders, flights, and spoken 'what time is it?' can legitimately use different zones. The pendant can notice context while the Mac provides its OS zone, and the relay can preserve a task-scoped choice without silently rewriting the owner's profile.
- **path:** pendant → relay-realtime → mac-planner → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Rules for IANA zone comparison and task type; cheap model only classifies ambiguous temporal language. Realtime speaks the clarification; background jobs use the stored task-scoped choice.
- **latency:** Under 200 ms when zones agree; one 5–8 word clarification when they do not. Never delay non-temporal work.
- **cost:** <$0.005 per temporal request; mostly deterministic state comparison.
- **security:** Store IANA zone and coarse source/time only, not continuous location. Location-derived zone requires explicit opt-in and should degrade to device zones. Changing the long-term home zone requires confirmation; task-scoped choices expire after completion or 24 hours.
- **missing:** Task-scoped temporal preference in the job journal; A safe source hierarchy (explicit utterance > calendar event zone > current OS zone > remembered home zone); Optional coarse location/timezone signal from the pendant or phone; Natural-language rendering that states the chosen zone in the receipt

### "If I’m in public or someone else may hear me, give me the useful answer without exposing private details: speak a safe summary on the pendant and put the exact names, amounts, links, or account content on my private Mac/browser screen. Let me say 'private' or 'say it all' to change the mode for this task."
- **useful because:** A wearable assistant is always available but its speaker is not a private channel. Today the owner must choose between silence and accidentally announcing mail, finances, health, or work information. This would let the pendant remain useful in meetings, transit, and shared rooms without making every request a privacy gamble.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** Deterministic sensitivity and output-routing rules first; a small background model classifies whether content contains private entities. Realtime is used only to produce the short spoken summary. Browser/Mac receives the detailed result through an authenticated local channel.
- **latency:** Safe spoken acknowledgement within 300 ms, with the detailed result appearing on the private screen within 2 seconds. If privacy context is uncertain, default to the safe summary rather than asking a long question.
- **cost:** Usually below $0.01 per request; classification and routing dominate, while the spoken summary may use the realtime tier.
- **security:** The system must never claim a room is private based on weak inference. Default to redaction for secrets, account identifiers, health data, and message contents; require an explicit 'say it all' override per task. Encrypt local delivery, avoid logging the redacted source in relay transcripts, and show the owner exactly where the full answer was placed.
- **missing:** A pendant privacy-mode control with tactile/audio confirmation and a task-scoped expiry; A shared sensitivity taxonomy and redaction renderer used by voice, Mac, and browser surfaces; Authenticated pendant-to-Mac private-display delivery with visible delivery status; Optional local signals for privacy context (manual mode first; proximity/earbud/phone signals later); Receipts that distinguish spoken-safe-summary delivery from full-detail delivery


## Changes it proposed to its own stack

### `integration` — Add a cross-surface Action Truth Envelope and preflight state machine. Every job receives a snapshot containing target surface reachability, permission probes, canonical timezone candidates, freshness, and required confirmation level. Actions may transition only from preflight_passed to executing; completion receipts must include observed evidence from the target (not the intent acknowledgement) and are marked trusted, untrusted, or unknown. A dropped bridge, failed Accessibility/Screen Recording probe, stale browser heartbeat, or timezone conflict routes to waiting_for_owner with a one-question pendant prompt. Resume uses the same idempotency key and appends evidence rather than overwriting the prior attempt.
- **owner gets:** The owner gets honest answers and safe recovery: no phantom Mac edits, no wrong-time reminders, and no need to remember whether a disconnected browser job really ran. Held work can continue after permissions, connectivity, or timezone are fixed.
- effort: Medium-high: shared schema and reducer, adapters in relay/mac/browser, permission probes, durable pending decisions, pendant prompt and dashboard explanation, plus failure-injection tests.  ·  risk: Some existing jobs will become visibly blocked instead of optimistically completing; recover by preserving the current permissive path only for explicitly local, observed operations and by offering resume/undo. Incorrect probes could over-block, so show source and age and allow an owner override with confirmation.
- cost: Negligible recurring API cost; roughly one compact state envelope per job. Engineering cost is integration and test coverage.  ·  latency: Adds roughly 100–300 ms for probes; avoids long wasted runs and false completion follow-ups.
- security: Improves security by preventing actions when permissions or target identity are unclear; envelope must redact URLs, account data, and secret page contents from spoken/dashboard logs.
- depends on: A durable cross-surface job/event journal; Mac Accessibility and Screen Recording status reporting; Browser heartbeat and session identity; Owner-confirmed canonical timezone resolution


## What it asked for

_Nothing._
## Its own summary

I added a new cross-hive Action Truth Envelope/preflight state machine: actions must prove target reachability and observed results, otherwise they become resumable waiting-for-owner jobs instead of false successes. I also proposed task-scoped timezone arbitration so home/current/event time can differ safely. I handed the required receipt fields to faculty-action and asked perception to publish freshness and source metadata.

**Biggest unknown:** The owner’s canonical timezone choice and whether Accessibility, Screen Recording, and the browser bridge will actually be authorized. Until those are resolved, Mac/browser completion receipts must remain untrusted and time-based actions should pause rather than guess.

