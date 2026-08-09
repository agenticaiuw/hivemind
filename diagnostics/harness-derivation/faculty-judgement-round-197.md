# Harness derivation — faculty-judgement — round 197

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Did you actually get that briefing, or did it only finish on the server?” Give me one truthful answer for the exact spoken item, including whether it was generated, downloaded, started, finished, interrupted, or never delivered."
- **useful because:** Today a completed pipeline/job can be mistaken for a heard message. This would close the most important trust gap in a wearable: distinguish server success from the owner's actual receipt, and say what recovery is possible without replaying an already-heard item.
- **path:** relay → pendant → dashboard
- **model tier:** background for receipt aggregation; realtime only for the one-sentence spoken answer
- **latency:** Under 500 ms when delivery events are already uploaded; under 3 s if the relay must reconcile recent job receipts.
- **cost:** Usually <$0.001 per query; dominated by no model call, with a small model fallback only for ambiguous human phrasing.
- **security:** Expose artifact IDs and timestamps, not audio or transcript, to the dashboard/relay. Require provenance-backed event IDs and deduplicate offline replays. A missing ACK must be reported as unknown, never inferred as heard.
- **missing:** A production read endpoint joining relay job/pipeline receipts to record_pendant_delivery_event events by artifact and session; A durable per-item delivery state projection and a dashboard/voice formatter; Pendant firmware upload wiring for the already-accepted audio_delivery_ack_queue

### "“If I ask you to do this tomorrow, what exactly would you be allowed to do, what would need my approval, and what could you not do because a surface is offline?” Show me the decision before doing anything."
- **useful because:** The owner should be able to inspect the boundary of agency before trusting it. This turns hidden routing and approval behavior into a concrete preview: reachable surfaces, matched autonomy rules, reversibility, required confirmation, and explicit offline blockers. It is especially valuable when Mac, browser, relay, and pendant disagree about what is possible.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** background for compiling the natural-language request into a typed candidate; deterministic policy and preflight for the actual verdict
- **latency:** 1–2 s for a normal request; no mutation and no waiting on an offline surface.
- **cost:** <$0.002 per preview; most calls use deterministic evaluators, with model cost only for ambiguous intent parsing.
- **security:** Preview must not enqueue, click, send, or reserve anything. Redact secrets from the explanation. Show evidence references and policy rule names, and mark stale capability reports with their age. Any transition from preview to execution must use a fresh revalidation and an owner confirmation for external or destructive effects.
- **missing:** A durable preview object with expiry and an explicit bind from preview to later execution; One response contract that combines cross-surface preflight, autonomy verdict, stale-plan revalidation, and provenance references; A dashboard/voice presentation that distinguishes ACT, PREPARE, QUEUE, ASK, and BLOCK without pretending BLOCK is failure

### "“When you say tomorrow at 9, tell me which clock you used and what you still do not know about where I am.” Resolve every date spoken or scheduled across the Mac, relay, browser, and pendant, and ask only when the clocks genuinely conflict."
- **useful because:** A wearable can be physically with the owner while the Mac's timezone is merely the machine's location, and the pendant currently has no trustworthy timezone at all. Silent conversion can create missed meetings or reminders at the wrong hour. This gives every temporal decision an honest clock, provenance, and a small disambiguation question rather than a confident guess.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** deterministic timezone/offset comparison and date parser; realtime model only to phrase the single clarification question
- **latency:** Under 300 ms for an unambiguous request; under 2 s when browser/calendar evidence must be gathered.
- **cost:** <$0.001 per request; no model call for standard ISO dates and offsets.
- **security:** Do not infer physical location from IP, browser locale, or calendar venue. Treat the pendant's zoneless clock as unknown. Show source and capture time for each offset, and require confirmation before creating a reminder/event when two plausible instants remain.
- **missing:** A typed temporal-context object that distinguishes machine timezone, owner-declared timezone, event timezone, and unknown pendant clock; A read-only cross-surface comparison covering Mac zone, browser/session locale where available, relay timestamps, and explicit owner preference; A scheduler write guard that refuses ambiguous local times instead of borrowing America/New_York

### "“That task may have half-finished. Don’t retry blindly—tell me what actually changed, what remains, and offer the smallest safe repair.”"
- **useful because:** Today a failed Mac/browser job can leave real partial effects while the owner sees only success or failure. The owner needs a semantic repair plan, not a duplicate retry that might send twice, buy twice, or overwrite a good result. This is a new capability: reconstructing the postcondition from receipts and current observations, then selecting a compensating action.
- **path:** relay → mac → browser → dashboard → pendant
- **model tier:** background model to interpret the intended postcondition; deterministic receipt/state diff and autonomy policy for the repair decision; realtime only for the short spoken summary
- **latency:** 2–5 s for a repairable task; immediately report “state unknown—do not retry” when evidence is insufficient.
- **cost:** <$0.01 per incident; model cost is only for ambiguous postcondition extraction, while diffs and policy checks are local.
- **security:** Never automatically compensate an irreversible or externally visible effect. Show each observed change and its source, quarantine duplicate-send/buy/delete classes, require physical confirmation for any external repair, and preserve the original receipt chain.
- **missing:** A typed postcondition contract for each action step; A read-after-write verifier for Mac and authenticated browser state; A compensating-action planner that is separate from blind retry and binds repairs to the original job

### "“What information about me left this machine this week, where did it go, and what exact purpose did it serve?” Give me a compact, source-linked disclosure receipt I can revoke or export."
- **useful because:** The current redaction and origin checks can block some secrets, but the owner cannot audit the actual disclosures across relay prompts, TTS, browser extraction, and Mac actions. A disclosure ledger makes privacy observable after the fact: destination, data class, minimized digest, purpose, policy rule, and whether the recipient acknowledged it. It also exposes accidental paths that bypass the one briefing redaction gate.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** deterministic event collection and aggregation; background model only to group receipts into owner-readable purposes
- **latency:** No foreground cost for writes; dashboard query under 1 s for a week of receipts; spoken answer under 3 s.
- **cost:** <$0.002 per weekly summary; storage is bounded digests and metadata, not copied content.
- **security:** The ledger itself is highly sensitive. Keep raw content out, hash or classify payloads locally, encrypt at rest, restrict spoken output to destination and category unless the owner explicitly opens details, and make deletion/revocation produce a durable tombstone rather than pretending historical transmission can be undone.
- **missing:** A mandatory outbound-disclosure event emitted by every prompt, TTS, browser-result, and external-action boundary; A shared destination/data-class/purpose schema and retention policy; A dashboard route for disclosure history, export, and scoped revocation requests

### "“Ask Alex to handle the part I can’t, but reveal only what Alex needs, show me the exact draft first, and bring back their answer without treating it as fact.”"
- **useful because:** The system can act across the owner’s tools, but it cannot safely delegate a bounded piece of work to another person while preserving least disclosure, consent, and provenance. This would turn a vague request into a human handoff: a scoped brief, an owner-approved outbound draft, a reply channel, and a clear distinction between the other person’s claim and verified state.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** background model for scope minimization and draft composition; deterministic disclosure policy and autonomy checks; realtime only to confirm the owner’s intent
- **latency:** Draft in under 5 s; no outbound message until explicit approval; reconcile replies asynchronously and surface only when attention policy permits.
- **cost:** <$0.02 per delegation, dominated by draft/reply summarization; no cost while awaiting a response.
- **security:** Never infer a recipient or send from a spoken ambiguous name. Show recipient, exact fields, attached sources, and expiry. Strip secrets by default, label every reply as unverified third-party input, and require confirmation before any resulting external action. Persist only the task brief and provenance, not unnecessary private conversation.
- **missing:** A durable human-delegation object with scope, recipient, expiry, allowed disclosures, and reply state; A draft-only outbound adapter for the owner’s chosen channel plus inbound reply capture; A policy that treats third-party replies as evidence requiring verification, not instructions

### "“Rehearse this whole workflow with me, using fake values and no external side effects, then tell me exactly where the real run could still fail.”"
- **useful because:** A preview lists intended effects, but it does not let the owner experience a multi-surface workflow or expose brittle assumptions before committing. A rehearsal mode would run the planner, browser navigation, field mapping, policy checks, and pendant interaction against a local/synthetic sandbox, then produce a gap report. This is especially useful for unfamiliar forms, recurring jobs, and accessibility-sensitive flows.
- **path:** dashboard → mac → browser → relay → pendant
- **model tier:** background model for scenario generation and failure explanation; deterministic sandbox adapters and autonomy policy for execution; realtime model only for interactive coaching
- **latency:** 5–15 s for a short workflow; longer workflows stream checkpoints and never touch production endpoints.
- **cost:** <$0.03 per rehearsal, primarily model-generated synthetic fixtures; browser and Mac work runs locally.
- **security:** Sandbox adapters must fail closed if a production origin or real account is reached. Synthetic credentials and targets must be unmistakable, network writes must be denied, and screenshots/transcripts must be retained only with explicit owner request. The report must never imply rehearsal proves production success.
- **missing:** A dry-run adapter contract for every Mac/browser action, including deterministic synthetic page fixtures; A network and side-effect firewall that proves the rehearsal target is non-production; A rehearsal transcript/checkpoint format that can be compared with a later real run


## Changes it proposed to its own stack

### `context` — Make every scheduled-time record carry an explicit clock provenance tuple: instant, displayed local time, zone source (owner-declared, Mac system, event-provided, or unknown), capturedAt, and ambiguity status. Reject writes with unknown/ambiguous zone unless the owner confirms; render the source in receipts and spoken confirmations. Keep the pendant clock zoneless rather than borrowing the Mac zone.
- **owner gets:** The owner stops receiving reminders that sound precise but were silently shifted by the wrong machine or device clock. When the system asks a question, it can say exactly why: “I have 9:00 New York from the Mac, but no owner location.”
- effort: Medium: shared schema, parser/write guards, migrations for routines/reminders, and tests across relay/Mac/browser.  ·  risk: Existing routines may lack provenance and become review-required rather than firing; recover by treating legacy records as Mac-system time with an explicit legacy warning and offering one-time confirmation.
- cost: Negligible storage and API cost; no extra model spend.  ·  latency: <10 ms deterministic validation; at most one clarification turn for ambiguous requests.
- security: Reduces accidental disclosure through wrong-time actions; no location inference and no new sensitive data collection.
- depends on: owner-declared timezone must be a separate value from America/New_York Mac system zone; A typed cross-surface temporal context and scheduler write guard; Read paths for existing reminder/routine records


## What it asked for

_Nothing._
## Its own summary

Round 197 produced three new owner-facing capabilities and one stack change. The highest-value proposal is a pre-action agency preview: before tomorrow’s request is acted on, the owner sees which surfaces are reachable, what autonomy rule matches, whether it is ACT/PREPARE/QUEUE/ASK/BLOCK, what is stale, and what confirmation is required. I also proposed truthful heard-vs-generated delivery status, and timezone-provenance-aware scheduling that refuses to borrow the Mac zone for the pendant or owner. I added a concrete context-layer change to persist clock provenance and ambiguity on every scheduled-time record.

**Biggest unknown:** The owner’s timezone fact conflicts with the authoritative Mac timezone: memory says America/Chicago, while routine policy says America/New_York and the pendant has no zone. I still need the owner to distinguish their personal timezone from the Mac’s routine timezone before any system can safely resolve local times. I also need live implementation confirmation for the newly granted cross-surface tools before claiming their routes are actually mounted.

