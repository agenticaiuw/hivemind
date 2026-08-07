# Harness derivation — faculty-action — round 79

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live action reachability** — Mac bridge and relay are online, but Browser Bridge is offline with 7 pending commands. Mac agent reports accessibility and screen-recording ungranted, computer-use loop disabled; AppleScript automation grants are present. Any authenticated browser action or GUI verification is currently blocked until the extension reconnects, and GUI-only actions remain blocked by owner TCC.
  - evidence: GET /ops/status at 2026-08-07T12:59Z: browser.online=false, pendingCommands=7, accessibility.trusted=false, screenRecording.granted=false, relay.reachable=true; GET /browser/status confirms same.

## Capabilities it proposed

### "“After you do it, prove that it actually happened—check the resulting app, page, or device state, and tell me if the proof is missing or contradicts the plan.”"
- **useful because:** Execution receipts currently report what the harness attempted, not whether the outside world accepted it. A mail send can be rejected, a browser click can hit the wrong tab, a reminder can fail silently, and a dropped pendant link can hide the result. This capability closes the action loop with independent postcondition evidence and an honest UNKNOWN state instead of claiming success.
- **path:** faculty-judgement supplies typed postconditions and acceptable evidence before execution → mac-planner observes resulting Calendar/Mail/Finder/Notes state through granted AppleScript or high-level Mac routes → browser-extension re-reads the bound authenticated tab and captures URL/title/selected text or DOM evidence → relay compares observations against the planned postcondition, records contradictions and timestamps, and only then marks DONE → relay-realtime speaks success, failure, or unverifiable outcome on the pendant; unified can expose the evidence and offer retry/undo
- **model tier:** Use deterministic checks and a small background model for semantic matching of evidence to postconditions; use realtime only to explain the verified result during live conversation.
- **latency:** Add 1–3 seconds for local Mac checks and up to 10 seconds for a browser re-read. If a surface is offline, report PENDING/UNKNOWN and verify automatically on reconnect.
- **cost:** About $0.002–$0.03 per verification, mostly browser/Mac round trips; model use is limited to ambiguous semantic comparisons.
- **security:** Evidence must be scoped to the exact app/tab/session and redact secrets. Never treat an agent receipt alone as proof. For irreversible effects, require positive evidence or explicitly tell the owner that confirmation is unavailable; do not automatically retry non-idempotent actions.
- **missing:** first-class postcondition schema with evidence predicates and UNKNOWN outcome; Mac and browser verification adapters tied to action IDs and tab/session affinity; reconciliation route that stores before/after evidence and contradiction reasons; pendant-facing status that distinguishes attempted, verified, failed, and unverifiable

### "“If this becomes urgent, keep trying every way to reach me until I acknowledge it—and show me when and where I acknowledged it.”"
- **useful because:** Today the mind can schedule work and speak through the pendant, but it cannot guarantee that a time-critical decision reaches the owner across a dropped wearable link, sleeping Mac, or unavailable browser. This is an escalation contract, not a one-shot notification: it continues across relay, pendant, and Mac fallback until there is a real acknowledgment, then records a trustworthy delivery and acknowledgment history.
- **path:** faculty-judgement creates an alert policy with urgency, deadline, quiet-hours exception, escalation order, and acknowledgment phrase/button → relay remains the durable coordinator and schedules retries while the Mac is asleep or disconnected → pendant receives a local alert, repeats it with bounded backoff, and records a physical button/voice acknowledgment offline → mac-planner uses granted AppleScript/notifications as a fallback when the pendant is unavailable → relay reconciles duplicate deliveries, stops all escalation on one valid acknowledgment, and exposes a concise receipt to unified and relay-realtime
- **model tier:** Use deterministic scheduling, delivery, deduplication, and acknowledgment validation; use the background tier only to summarize the receipt or classify an ambiguous spoken acknowledgment. Realtime is reserved for the live alert conversation.
- **latency:** Relay should begin escalation within 1 second of the trigger. Pendant alert delivery target is under 2 seconds when connected; fallback retries continue for the configured deadline. Reconciliation after reconnect should complete within 30 seconds.
- **cost:** About $0.001–$0.02 per alert, dominated by speech/audio delivery and retry traffic; deterministic coordination avoids planner calls.
- **security:** Alerts may expose sensitive content on a shared Mac or in public spaces, so support redacted previews and a private wake phrase. Require explicit policy approval before contacting third parties. Store delivery metadata and acknowledgment proof, not raw microphone audio.
- **missing:** durable multi-channel escalation policy and timer state in the relay; pendant firmware alert/retry/acknowledgment state that survives a dropped link; common delivery-attempt and acknowledgment proof schema across pendant and Mac; deduplication and cancellation when multiple channels reconnect


## Changes it proposed to its own stack

### `browser-harness` — Add reconnect quarantine for pending browser commands: every queued command gets an expiry, session/tab fingerprint, and intended effect class; when the extension reconnects, do not replay stale or write/submit commands automatically. Move them to a reviewable queue, revalidate the tab/session fingerprint, and let the relay ask the pendant whether to discard, refresh evidence, or resume. Read-only idempotent commands may be auto-replayed only within a short TTL and unchanged session.
- **owner gets:** The browser is currently offline with seven pending commands. Without quarantine, reconnecting can cause old clicks, typing, or submissions to run against a changed tab and produce an action the owner no longer intended. The owner gets safe recovery instead of surprise browser mutations.
- effort: Medium: extend browser command persistence/schema, add reconnect reconciliation and dashboard/pendant status, and test stale, duplicate, and tab-changed cases.  ·  risk: A command may remain pending until the owner reviews it; that is safer than replay. Recovery is explicit discard or re-plan. Read-only commands can expire harmlessly.
- cost: Negligible storage and model cost; one deterministic reconciliation per reconnect.  ·  latency: Adds under 1 second for queue inspection; owner confirmation adds human latency only for stale/irreversible work.
- security: Improves safety by binding commands to session/tab fingerprints and preventing stale authenticated actions. Do not persist page contents beyond existing evidence retention.
- depends on: browser bridge reconnect/heartbeat path; typed effect class and idempotency metadata on browser commands; owner-visible pending-command review via existing jobs/receipts or dashboard

### `firmware` — Add a persistent, resumable alert envelope protocol to the pendant: relay-delivered alerts are stored with alertId, urgency, expiry, redacted display/audio payload, retry schedule, and acknowledgment nonce. The firmware renders and repeats active alerts without server contact, queues an acknowledgment event durably, and uploads it exactly once after reconnect; duplicate envelopes are idempotent and expired alerts are visibly marked rather than silently discarded.
- **owner gets:** An urgent alert will not vanish because the pendant briefly loses Wi‑Fi or the relay is restarting. The owner can acknowledge it on the device and later see proof that the acknowledgment reached the system, instead of wondering whether a critical reminder was delivered.
- effort: Medium firmware and relay protocol work, plus power-loss/reconnect tests and a small dashboard status view.  ·  risk: Persistent alerts could annoy the owner or survive after they are no longer relevant; enforce expiry, bounded repetition, quiet-hours policy, and a physical dismiss action. If flash writes fail, keep the alert in RAM and report unacknowledged rather than claiming durability.
- cost: Negligible API cost. Small flash journal and under roughly 8 KB RAM for a bounded active-alert queue; modest battery use while repeating audio/LED.  ·  latency: Local rendering is immediate; reconnect acknowledgment delivery is bounded by the next network opportunity.
- security: Use per-alert authenticated envelopes and nonces; persist only redacted payloads and metadata, never raw conversation audio. Acknowledgment proves device interaction, not identity of a third party holding it.
- depends on: relay alert envelope and escalation scheduler; pendant/server acknowledgment event schema; owner-configurable urgency, expiry, and quiet-hours policy


## What it asked for

_Nothing._
## Its own summary

Discovered and recorded two concrete action gaps. (1) Postcondition verification: receipts prove dispatch, not that Mail/Calendar/browser/device state actually changed; add DONE/FAILED/UNKNOWN evidence reconciliation across Mac, authenticated browser, relay, and pendant. (2) Browser reconnect quarantine: the live system has 7 pending browser commands while the extension is offline; stale or tab-mismatched write/submit commands must not replay automatically. Fresh status: relay and Mac bridge online; browser offline; Accessibility and Screen Recording still absent, while AppleScript grants are present.

**Biggest unknown:** The durable browser job runner and cross-surface saga are still unimplemented, and there is no verified owner approval/checkpoint protocol or postcondition schema. I still need those implementation pieces; the owner must manually grant TCC permissions if GUI/screen verification is required.

