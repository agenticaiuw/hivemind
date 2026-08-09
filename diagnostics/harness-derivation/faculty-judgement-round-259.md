# Harness derivation — faculty-judgement — round 259

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What changed since I last checked?” Give me a short, trustworthy delta across my browser, mail, calendar/reminders, files, and pendant—not a fresh dump."
- **useful because:** The owner repeatedly needs orientation, not another full briefing. It turns scattered watches, triage runs, job receipts, and device ACKs into one source-linked change report, while explicitly saying when a source was unreadable or stale.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Background model for diff clustering and wording; realtime only for the owner's follow-up question. Deterministic source freshness and deduplication run without a model.
- **latency:** Under 3 seconds when baselines are current; up to 10 seconds for a requested full delta. Spoken output is one sentence plus an optional queued detail.
- **cost:** Low: one background summarization call only when there are new deltas; dominant cost is source reads, not tokens.
- **security:** Never treat absence as no change when Calendar/EventKit or Browser is unreadable. Store hashes and small provenance pointers by default, not raw mail/page text. Sensitive deltas are queued rather than spoken unless the owner policy allows them.
- **missing:** Durable per-source baseline/ack cursor with freshness and permission provenance; Adapters that normalize mail/calendar/browser/files/pendant events into a common delta record; A dashboard and pendant command for advancing or restoring an anchor

### "“Tell me where my attention is leaking.” Find repeated failed, abandoned, or retried work across the Mac, browser, routines, and pendant, then suggest one concrete fix—not a productivity score."
- **useful because:** The system already records retries, stale jobs, browser lease failures, audio interruptions, and routine errors, but the owner gets no synthesis. This finds real friction (for example, a job stranded after a Mac or extension disconnect) and offers a reversible repair or a reviewable bug draft.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Cheap scheduled/background classifier over typed receipts and diagnostics; realtime model only explains a selected incident.
- **latency:** Scheduled scan under 15 seconds; spoken answer under 2 seconds from a prepared result.
- **cost:** Very low: mostly local aggregation; occasional background clustering call dominates.
- **security:** Analyze metadata and error codes first; redact page contents and mail subjects. Never auto-retry destructive or external actions. Every recommendation must pass autonomy_policy_evaluate and show evidence refs.
- **missing:** A durable friction episode schema joining relay job IDs, Mac/browser IDs, action receipts, and pendant delivery events; A scheduled collector that consumes existing receipts and diagnostics without inventing success; Owner-facing repair cards with one-click reversible fixes and suppression

### "“Can you keep this thread alive until it is actually done?” Turn a spoken intention into a small, observable outcome with a deadline, check progress across the right surfaces, and tell me only when it is done, blocked, or needs me."
- **useful because:** The owner can currently create jobs, watches, reminders, and drafts, but none share a semantic outcome. This is the missing life-level behavior: the pendant remembers what ‘done’ means, the relay coordinates, the Mac/browser verify reality, and the owner is not nagged by intermediate noise.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Realtime model extracts the initial intention once; background model and deterministic checks monitor it. Do not spend realtime tokens on every poll.
- **latency:** Initial capture under 2 seconds; checks run on schedules or source events; completion notification under 5 seconds of verified evidence.
- **cost:** Moderate initial extraction, then low background cost. Source polling and browser reads dominate, not generation.
- **security:** Default to read-only verification and a 14-day expiry. Mutations, messages, purchases, and deletion require explicit physical approval. A blocked state must be honest about missing permissions, stale browser sessions, or contradictory evidence; never infer completion from a queued job.
- **missing:** A durable outcome object with success predicates, deadline, source bindings, and state transitions; Typed progress adapters for jobs, browser watches, reminders, mail, and delivery ACKs; A completion/blocked event path into attention_arbitrate and a reviewable owner UI; Cross-surface correlation IDs; current IDs only meet in unindexed telemetry

### "“Before I say yes, show me the likely cost to future-me.” For a proposed commitment, simulate its effects on time, existing obligations, privacy, and attention, then present the smallest safe version or a clear tradeoff."
- **useful because:** The owner currently gets execution and reminders, but not a judgment that connects a new promise to the life it will displace. This is a decision aid, not an automatic planner: it makes hidden opportunity costs visible before they become obligations.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** A background model builds a few bounded scenarios from structured state; realtime is used only to discuss the selected tradeoff. Deterministic checks enforce deadlines, conflicts, permissions, and spending limits.
- **latency:** Initial answer within 5 seconds; deeper alternatives can arrive as a queued briefing. No interruption unless the owner explicitly asks.
- **cost:** Moderate per explicit invocation; the expensive part is scenario synthesis, while calendar/job/reminder reads remain local and cheap.
- **security:** Use abstract facts and time blocks by default, not raw message contents. Never contact anyone or create an obligation during simulation. External actions require the existing policy and physical approval path. Every forecast must distinguish observed facts from assumptions.
- **missing:** A typed commitment/opportunity-cost model that can represent displacement without creating a second task ledger; A bounded scenario evaluator with explicit assumptions and confidence intervals; A provenance-backed comparison view showing which facts drove each predicted cost; Owner-set preferences for what tradeoffs matter (time, money, privacy, recovery, relationships)

### "“Give me a private weekly mirror of how I actually lived.” Summarize patterns in attention, unfinished intentions, interruptions, and recovery—using local aggregates—then let me correct the story or erase a pattern."
- **useful because:** The system reacts to individual events but cannot help the owner notice recurring causes: which commitments repeatedly slip, when interruptions cluster, or whether the pendant is being used as intended. A private mirror supports better choices without turning behavior into a score or surveillance feed.
- **path:** pendant → relay → mac → dashboard
- **model tier:** Cheap background aggregation over typed local events, followed by a small synthesis model. Realtime is unnecessary except for an owner follow-up such as “why do you think that?”
- **latency:** Weekly generation under 20 seconds; spoken summary under 90 words. Detail is dashboard-only and on demand.
- **cost:** Low: local aggregation dominates, with one small background synthesis call per reporting period.
- **security:** Keep raw audio, page text, mail bodies, and credentials out of the mirror. Store only owner-approved aggregate dimensions with a short retention period. Every statement needs an evidence range and an easy correction/erase action; never infer health, personality, or protected traits.
- **missing:** An owner-visible aggregate event vocabulary spanning attention, intention, interruption, recovery, and delivery; A local-only rollup store with retention and deletion semantics; A correction mechanism that records “this interpretation is wrong” without silently rewriting source history; A presentation mode that refuses to speak sensitive patterns aloud

### "“When I am unavailable, leave the right kind of explanation—not just a failure.” For a blocked task or missed commitment, produce a compact handoff stating what was attempted, what is known, what is uncertain, and the safest next owner action."
- **useful because:** Today a failed job, stale browser session, or missing permission leaves the owner to reconstruct the situation from logs. A truthful handoff preserves agency across sleep, travel, crashes, and changing attention without pretending that queued work succeeded.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic receipt assembly first; a cheap background model compresses it into owner language. Realtime only answers follow-up questions.
- **latency:** Available immediately when a task becomes blocked; spoken form under 2 seconds and one sentence, with detail queued.
- **cost:** Low: receipt assembly is local; generation is a small background call only for non-template explanations.
- **security:** Handoffs must carry sensitivity labels and avoid raw page/mail content by default. Never disclose a third party's private data to another recipient. Do not retry or mutate while composing the handoff. Include provenance and an expiry so an old explanation cannot be mistaken for current state.
- **missing:** A durable blocked-state record with attempted steps, evidence refs, uncertainty, and next-safe-action fields; A cross-surface correlation key joining relay jobs, Mac actions, browser commands, and pendant delivery ACKs; A lifecycle that expires or supersedes handoffs when the underlying state changes; A policy-controlled spoken/text destination selector


## Changes it proposed to its own stack

### `context` — Introduce a signed freshness contract for every cross-surface observation and judgement: source_id, observed_at, valid_until, permission_state, redaction_state, and evidence_refs. The relay refuses to collapse stale or unreadable observations into 'clear'; Mac/browser/pendant attach the contract to receipts, attention events, and spoken brief items. A single owner-visible 'why this is stale/blocked' view replaces silent fallback.
- **owner gets:** The owner stops hearing confident lies such as 'your calendar is clear' when EventKit returned an unauthorized empty list, or 'done' when audio was merely generated. They get a brief answer that says what was actually checked, when, and what could not be verified.
- effort: Medium-high: shared schema, adapters in briefing/triage/jobs/pipeline, and enforcement at speech and action boundaries. No new hardware required.  ·  risk: Existing callers may break when they must handle unknown/stale instead of empty. Recover by dual-writing contracts, logging violations, and failing closed only for high-impact decisions before expanding enforcement.
- cost: Negligible storage and token overhead; avoids expensive realtime explanations by carrying compact evidence references.  ·  latency: Milliseconds for deterministic checks; at most one extra source read when a contract is expired.
- security: Improves least-privilege and disclosure: spoken content can be blocked based on both sensitivity and recipient freshness/provenance. Contracts contain IDs and timestamps, not raw secrets.
- depends on: Define owner-configurable interruption and disclosure policies rather than hard-code them; Add relay-job to Mac/browser job correlation (currently only unindexed telemetry); Use the existing briefingTriage empty-pair corroboration for EventKit and preserve unreadable as a first-class state


## What it asked for

_Nothing._
