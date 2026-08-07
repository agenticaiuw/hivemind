# Harness derivation — faculty-judgement — round 9

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Only interrupt me when something truly matters; otherwise keep a quiet queue and tell me at the right time.”"
- **useful because:** The owner currently has several daily routines, browser watches, long-running Mac jobs, and a pendant that can reach them anywhere, but no shared decision about when an alert deserves an interruption. This would merge duplicate findings, weigh deadline and consequence, respect quiet hours, and escalate only when waiting is likely to cost them something. The owner gets fewer noisy briefings and does not miss the one item that actually matters.
- **path:** browser-extension reads the owner's authenticated pages and produces sourced change events without exporting page contents → mac-planner/mac-terminal correlate calendar deadlines, running jobs, files, and failed or blocked work → relay stores a compact urgency queue and applies quiet hours, deduplication, sensitivity, and escalation policy → pendant/relay-realtime speaks a single short interruption when the threshold is crossed; otherwise it announces the next digest at a natural interaction → dashboard or Mac workbench shows why an item was escalated, what evidence supports it, and snooze/resolve controls
- **model tier:** Use a cheap background model for extraction, clustering, deadline and consequence scoring; reserve gpt-realtime for the actual short spoken interruption. Use the expensive judgement model only when evidence conflicts or an escalation would cause a meaningful interruption.
- **latency:** Background events can settle within 1–5 minutes. A high-confidence urgent event should reach the pendant within 10 seconds; routine items can wait for the next scheduled digest. The spoken alert must be one short sentence with an optional follow-up.
- **cost:** Roughly $0.01–$0.08 per day for normal event classification and digesting, dominated by authenticated-page extraction and repeated context. Urgent voice delivery adds only a small realtime turn. Avoid sending full page contents repeatedly by retaining hashes, snippets, source URLs, and expiry times.
- **security:** Private mail, calendar, and page contents should remain on the Mac/browser bridge; the relay should receive only the minimum normalized event, sensitivity label, deadline, and evidence pointer. Never speak secrets aloud by default. Escalation must not send mail, submit forms, delete files, or buy anything; those remain confirmation-gated. The owner must be able to inspect, mute, snooze, correct, and delete every queued event.
- **missing:** A durable cross-surface event schema with provenance, expiry, sensitivity, and idempotency; A shared urgency policy/queue service with quiet hours, deduplication, escalation and snooze state; A pendant notification/queue protocol that survives a dropped voice session; A small dashboard/workbench for explaining and correcting escalation decisions

### "“While I’m away, carry this through within the limits I set—and stop, ask, or hand it back whenever the situation exceeds those limits.”"
- **useful because:** Today the owner must either remain in the conversation or grant a dangerously broad instruction. This would let them delegate a real goal across private browser sessions, Mac applications, and the always-awake relay with explicit bounds: allowed sites, budget, deadline, reversible actions, people it may contact, and conditions requiring approval. The pendant is the portable consent and hand-back channel, not merely a microphone. The owner returns to a trustworthy result, a stopped-at-boundary task, or a concise request for the one missing decision.
- **path:** pendant captures the owner's spoken delegation and provides local button/voice approval, cancellation, and emergency stop → relay mints short-lived, scoped delegation capabilities, tracks heartbeats and expiry, and routes questions or completion notices → mac-planner/mac-terminal execute bounded file, research, and application work under the issued capability and preserve a step-by-step receipt → browser-extension operates only in explicitly allowed authenticated tabs/sites, with field-level and action-level policy checks → faculty-perception verifies current page/task state and detects when the requested bounds no longer match reality → faculty-action performs only permitted reversible work and pauses before any boundary-crossing action
- **model tier:** Use a cheaper background model for routine planning, policy matching, and progress summaries. Use the expensive judgement model only for ambiguity or a proposed boundary change. Use realtime solely for the brief live question, approval, or hand-back message.
- **latency:** Delegated work can run asynchronously. A boundary violation or approval question should reach the pendant within 10 seconds; normal progress can wait for completion or a scheduled digest.
- **cost:** Approximately $0.02–$0.20 per delegation, dominated by browser/Mac execution and occasional ambiguity resolution; most steps should use deterministic policy checks and a cheaper model. No full private page or file corpus needs to be resent to the relay.
- **security:** This is high-impact delegation and must default to deny. Capabilities need audience/device binding, short expiry, one-time nonces for irreversible steps, a spend limit, domain/app allowlists, data egress rules, and revocation from the pendant. Mail sending, purchases, deletion, account/security changes, and external uploads always pause for explicit confirmation. Every action needs before/after evidence and a tamper-evident receipt; private content should remain on the Mac/browser bridge except for the minimum needed to ask or report.
- **missing:** A capability-token and policy-enforcement layer shared by relay, Mac, and browser; A durable delegation state machine with heartbeat, pause, revoke, expiry, and hand-back semantics; A pendant-local emergency stop and approval protocol that works through intermittent connectivity; A provenance-rich execution receipt that can be replayed and audited across surfaces


## Changes it proposed to its own stack

### `interaction` — Add an interruption arbiter between all producers and the pendant. It accepts typed event envelopes (source, owner impact, deadline, confidence, sensitivity, evidence pointer, dedupe key), computes an urgency class with a deterministic policy first and model fallback second, and emits one of queue, digest, ask-at-next-contact, or interrupt-now. Every decision gets a reason, expiry, snooze/resolve state, and a reversible audit record. Permit a two-stage escalation: silent Mac notification first, pendant interruption only if the event remains unresolved and crosses the owner's configured threshold.
- **owner gets:** The owner's attention becomes protected: repeated routine changes stop competing with real deadlines, while a blocked job or expiring appointment can still reach them when waiting would hurt. They can understand and correct why the system interrupted them rather than feeling managed by an opaque alert stream.
- effort: Medium: define the envelope and policy, implement durable queue and idempotent dedupe, connect browser/Mac/job producers, add relay push and pendant acknowledgement, then test with replayed event traces and quiet-hour cases.  ·  risk: A bad score could suppress something important or wake the owner unnecessarily. Recover with conservative defaults, deterministic hard rules for deadlines and safety, a visible 'show me everything' queue, expiry-based rechecks, and a pendant command to undo snooze/mute. If the arbiter is unavailable, producers retain events locally and the next digest reports the outage.
- cost: Low background-model cost because most decisions are rules or small classifications; likely under a few cents per day at current event volume. Storage is compact event metadata rather than page bodies.  ·  latency: Adds under a second for local/rule decisions and seconds for model fallback; urgent push target is under 10 seconds end to end.
- security: Reduces data exposure by passing normalized metadata and evidence pointers instead of private content. The queue must enforce sensitivity-aware speech, authenticated owner acknowledgement, and strict separation between notification and action permissions.
- depends on: durable cross-surface job/event persistence primitives; typed context projection with provenance and TTL; reliable relay-to-pendant push and acknowledgement; browser and Mac producers emitting idempotent event envelopes


## What it asked for

### `c3-j2yh` (context) — owner interruption preferences
- why: The proposed interruption arbiter needs safe defaults for quiet hours, what counts as urgent, and whether the pendant may speak notifications containing sensitive details. These preferences are not present in the owner projection.
- would change: I would set the arbiter's initial policy and avoid proposing unsafe defaults; without it I will require conservative, non-speaking notifications and escalate only hard deadlines or explicit owner-defined emergencies.

## Its own summary

Round 9 produced a new owner-facing capability: an interruption arbiter spanning browser, Mac jobs/calendar/files, relay, and pendant. It clusters and deduplicates events, respects quiet hours and sensitivity, queues ordinary items, and interrupts only when deadline/consequence warrants it. I also proposed the durable event-envelope, policy, escalation, audit, and pendant acknowledgement layer needed to make it real. I still need the durable cross-surface event/job primitives already requested, plus the owner's quiet-hour, urgency, and sensitive-speech preferences; I have queued that context request rather than guessing.

**Biggest unknown:** The owner's actual interruption policy: quiet hours, urgency threshold, and which categories may ever be spoken aloud.

