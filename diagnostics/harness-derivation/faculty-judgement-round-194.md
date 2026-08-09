# Harness derivation — faculty-judgement — round 194

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Give me one brief that contains only what changed since I last successfully heard it, merge duplicate scheduled briefs, and tell me if anything could not be verified.”"
- **useful because:** The owner currently has two daily 07:00 briefs plus a 07:30 brief and no guarantee that a generated audio artifact was actually played. This would make the pendant a dependable memory of what the owner has already heard, not another source of repeated noise. It works across relay scheduling, Mac/browser evidence, and the physical delivery ACK.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Background model gathers and ranks deltas; realtime model is used only for a short spoken handoff or owner follow-up. Deterministic dedupe and delivery-state checks run without a model.
- **latency:** Under 10 seconds to prepare after scheduled trigger; spoken start under 1 second once the artifact is available. If a source is offline, say so rather than waiting indefinitely.
- **cost:** Roughly $0.01–$0.05 per brief depending on source volume; model summarization dominates, while dedupe, provenance, and ACK reconciliation are negligible.
- **security:** Only source-linked summaries leave the Mac; raw mail/page text stays local unless the existing policy permits it. A missing playback_finished ACK must never be treated as heard. Sensitive items are queued or described generically until the owner’s disclosure policy says otherwise.
- **missing:** A durable cross-surface identity linking routine run, briefing item, audio artifact, and playback ACK (the current IDs are unrelated); A writer from the Mac bridge into fleet memory or a durable heard-item index; An owner-set policy for whether an item counts as heard at playback_started or playback_finished; A routine migration/deduplication UI that proposes which of the duplicate scheduled briefings to disable

### "“When the pendant or Mac comes back online, give me a compact handoff: what was attempted, what actually reached me, what is still pending, and what I should do next.”"
- **useful because:** A dropped link currently makes generated work look indistinguishable from delivered work. This gives the owner a truthful recovery moment after offline periods, joining relay jobs, Mac receipts, browser results, and pendant playback events into one short, actionable answer instead of replaying everything.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** A cheap deterministic reconciler assembles status and suppresses duplicates; a slower background model turns the verified rows into a three-sentence spoken handoff. Realtime is reserved for questions about one row.
- **latency:** Status should be available within 2 seconds of reconnect; narration within 5 seconds. Never block reconnect on a slow source.
- **cost:** About $0.005–$0.02 per reconnect handoff; most runs need no model call if only receipts and ACK state changed.
- **security:** The pendant receives opaque IDs, short labels, and failure classes—not page contents, credentials, or raw mail. External actions remain pending unless their receipt and policy verdict both show completion. The owner can ask for provenance for any row.
- **missing:** A real relay-job/Mac-job foreign-key mapping instead of telemetry-only localJobId; A durable offline-reconnect trigger and last-seen cursor for each surface; A single read model combining job receipts with authenticated pendant delivery ACKs; A policy for how much failure detail may be spoken in public

### "“Before you carry out anything that has gone stale, tell me exactly what changed, what remains safe, and ask only for the smallest confirmation needed.”"
- **useful because:** A prepared Mac/browser action can silently become wrong while the owner is away: a page may change, a deadline may pass, or a browser session may disappear. This turns stale-plan detection into an owner-facing judgement rather than a backend rejection, preserving the useful work while preventing an obsolete action from being executed.
- **path:** mac → browser → relay → pendant → dashboard
- **model tier:** Deterministic policy and typed revalidation decide whether the plan is still valid; a small background model explains changed fields in plain language. Realtime is used only if the owner asks a follow-up.
- **latency:** Revalidation under 2 seconds for local state and 5 seconds with browser round-trip. The owner should hear a concise reason before any mutation, not after failure.
- **cost:** Usually under $0.01; model explanation is optional and dominates cost.
- **security:** Revalidation must be read-only and least-privilege. Sensitive snippets remain excluded by default. Any external or irreversible action still requires the physical transaction approval latch and explicit policy verdict; stale plans fail closed.
- **missing:** Typed change projections for each plan source (only changed fields plus provenance); A durable plan-to-source snapshot and expiry visible to the owner; A common decision record consumed identically by relay, Mac, browser, and pendant; A route that binds the revalidation result to the existing approval handoff rather than leaving approval Mac-local

### "“Show me two or three plausible versions of tomorrow if I choose each option, using my real commitments and pending work, but do not change anything.”"
- **useful because:** The owner can receive a plan or execute an action, but cannot see the second-order shape of a choice across calendar obligations, browser work, reminders, and existing routines. A counterfactual rehearsal would let them decide deliberately before committing, especially when the obvious next action creates hidden conflicts.
- **path:** relay → mac → browser → dashboard → pendant
- **model tier:** A background model generates candidate futures from a deterministic snapshot; deterministic checks identify calendar/time/resource collisions; realtime only reads the selected comparison aloud.
- **latency:** 30–60 seconds for three scenarios, with a progress update after the snapshot. No mutation or notification should wait on the model.
- **cost:** $0.03–$0.15 per rehearsal; scenario generation and conflict explanation dominate.
- **security:** Rehearsal is read-only. Raw authenticated-page content and private mail stay on the Mac unless explicitly included. Every predicted consequence must be labeled inference versus observed fact; no scenario may silently create reminders, send messages, or submit forms.
- **missing:** A versioned cross-surface snapshot that can be replayed consistently; A typed simulator for time, commitments, and pending browser/Mac jobs rather than only action previews; A way to distinguish observed constraints from model-generated consequences in the spoken result; An owner policy for which hypothetical data may be sent to a model provider

### "“For an important question, have independent judges inspect the same evidence, show me where they disagree, and refuse to collapse disagreement into one confident answer.”"
- **useful because:** Today the system can retrieve evidence and explain a provenance chain, but a single fluent judgement can hide ambiguity. Independent readings with an explicit disagreement report would be useful for purchases, travel changes, technical decisions, and anything where the owner would rather hear uncertainty than a polished mistake.
- **path:** relay → mac → browser → dashboard → pendant
- **model tier:** A cheap extraction pass builds a shared evidence bundle; two smaller background judges reason independently; the expensive realtime model is used only to summarize the disagreement when the owner asks. Deterministic rules reject unsupported claims.
- **latency:** 10–30 seconds for normal cases; immediate acknowledgement that review is underway. The pendant speaks a short verdict and offers the detailed disagreement on the dashboard.
- **cost:** $0.04–$0.25 per review, dominated by two independent model passes and any authenticated browser reads.
- **security:** All judges receive the same redacted, source-linked bundle, not arbitrary raw context. Secret or sensitive material is withheld by default. A disagreement must lower confidence and block external action until the owner confirms; source revocation must invalidate the bundle.
- **missing:** A durable immutable evidence-bundle identifier shared by all judges; A real production writer/mount for browser provenance and cross-check results; A calibrated disagreement/confidence schema rather than free-form prose; A policy hook that converts unresolved disagreement into an ASK decision before POST /execute

### "“When I lose access to a device or account, tell me exactly which of my pending jobs, memories, and approvals are exposed, stranded, or safely revoked, and walk me through recovery without revealing their contents.”"
- **useful because:** The owner currently has separate sessions, jobs, browser commands, memory, evidence, and device state, but no human-level account/device-loss response. A lost Mac session, expired browser bridge, or revoked pendant credential can leave work stranded or permissions unclear. This capability would make the hive survivable rather than merely functional while everything is online.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Deterministic inventory and revocation-impact computation first; a background model turns the result into a concise recovery checklist. Realtime is only for interactive confirmation of each recovery step.
- **latency:** Under 5 seconds for a local device-loss report; under 30 seconds for a full cross-surface inventory. Revocation itself must be immediate and fail closed.
- **cost:** Usually below $0.02; the expensive part is only optional explanation, not the inventory.
- **security:** The spoken response must contain identifiers and classes, never secrets or raw source text. Revocation must be scoped, idempotent, and physically confirmable for sensitive device actions. A stale or unreachable surface is reported as unknown, never as safe.
- **missing:** A relay-owned device/session registry with credential epochs and revocation propagation; A cross-store impact graph linking jobs, approvals, evidence, memory facts, browser sessions, and audio artifacts; A durable recovery case with step-by-step receipts and idempotency; A safe credential-rotation/reconnect protocol for the unregistered pendant path


## What it asked for

_Nothing._
## Its own summary

Round 194 produced three owner-visible capabilities: exact-once delta briefings grounded in playback completion, truthful reconnect handoffs, and fail-closed stale-plan explanations tied to approval. I still need owner policy decisions (actual personal timezone versus Mac routine zone, quiet hours, what content may be spoken, and emergency classes), plus implementation of durable cross-surface IDs, a heard-item index/fleet-memory writer, relay reconnect triggers, and approval-plan binding. The live reconciliation call itself resolved to POST /briefing without invoking it, so it is not yet evidence of a trustworthy unified state.

**Biggest unknown:** Whether the owner intends America/Chicago as their personal/current timezone while America/New_York remains authoritative only for Mac-local routines; this must not be guessed when scheduling or speaking a brief.

