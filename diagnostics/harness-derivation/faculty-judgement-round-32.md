# Harness derivation — faculty-judgement — round 32

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Before I commit to this, check what I'm overlooking and give me the safest next step."
- **useful because:** The owner currently gets isolated answers from the Mac, browser, and pendant. This would reconcile live private-page facts, local files/calendar, queued jobs, and the owner's spoken intent into a short decision card: contradictions, hidden dependencies, deadline, irreversible effects, and one recommended next step. It prevents acting on stale or incomplete context without making the owner manually gather it.
- **path:** pendant captures the spoken proposal and can ask one narrowly targeted clarification → relay persists the decision card, evidence references, expiry, and later resume prompt → mac-planner reads relevant local notes/calendar/files and pending Mac receipts → browser-extension reads up to the already-open authenticated tabs, with tab/URL/source citations → faculty-perception normalizes facts and freshness; faculty-judgement ranks conflicts and consequences; faculty-action executes only the approved reversible step
- **model tier:** Use a cheaper background model for evidence collection and normalization; use the realtime tier only for the spoken clarification and final 1–2 sentence recommendation. Escalate to the expensive tier when sources materially disagree or the action is consequential.
- **latency:** Initial spoken acknowledgement under 1 second; evidence sweep 5–20 seconds in background. If the owner is waiting, return a provisional card with explicit unknowns, then update the pendant when the sweep completes.
- **cost:** Roughly $0.01–$0.08 per ordinary sweep depending on tab count and extracted text; most cost is browser/Mac context and conflict adjudication, not the short spoken response.
- **security:** Private browser content and local files leave their surfaces only as minimally scoped, cited fields. Never include secrets in the decision card. Treat purchases, deletion, sending, publishing, or external commitments as confirmation-required; show the exact proposed change and evidence before action.
- **missing:** A cross-surface impact scan primitive that accepts an intent and returns scoped evidence, conflicts, freshness, and affected commitments; A durable decision-card schema with expiry and source citations shared by relay, Mac, and browser; ActionProof postconditions and verification wired into faculty-action; A pendant affordance to say 'hold', 'approve this step', or 'resume' offline/after a dropped link

### "If I say yes to this, what will it cost me—and what would have to move?"
- **useful because:** The owner can currently inspect individual calendars, messages, and pages, but cannot safely model the consequences of a proposed commitment before making it. This would produce a time-and-attention impact simulation from their actual commitments: overlaps, travel and preparation time, deadlines displaced, follow-up obligations, and the smallest set of changes needed. It is a decision aid, not an action, so it helps them avoid overcommitting without silently changing anything.
- **path:** pendant captures the hypothetical and can read the answer aloud privately → relay stores the scenario, assumptions, expiry, and a resumable result → mac-planner inspects calendar, local task/notes, reminders, and existing job commitments → browser-extension reads relevant authenticated reservation, work, or account pages with citations → faculty-perception builds a dated commitment graph; faculty-judgement simulates alternatives and distinguishes facts from assumptions; faculty-action remains dormant unless the owner later approves a specific change
- **model tier:** Use a background economical model for extraction, normalization, and schedule arithmetic; use the realtime tier only to clarify an ambiguous hypothetical and summarize the result. Reserve the expensive judgement pass for competing scenarios or high-stakes commitments.
- **latency:** A preliminary answer in 2 seconds from known local state, followed by a complete 10–30 second cross-surface simulation. The pendant should say which sources are still being checked rather than blocking silently.
- **cost:** Approximately $0.02–$0.12 per scenario; browser extraction and long-lived context dominate, while most arithmetic and formatting can be deterministic and cheap.
- **security:** Only fetch sources relevant to the hypothetical and keep private-page content on the relay as redacted structured facts. Never contact anyone, move a calendar event, book travel, or disclose the scenario without explicit confirmation. Show assumptions, confidence, and the exact commitments affected.
- **missing:** A durable commitment graph that represents time, travel, preparation, dependencies, attention budget, and follow-up obligations across Mac, browser, and relay; A scenario/sandbox engine that can clone the graph, apply hypothetical changes, and compute conflicts without mutating real state; Cross-surface authenticated extraction with provenance and freshness, including reservation and task semantics; A compact pendant interaction for choosing among scenarios or correcting an assumption


## Changes it proposed to its own stack

### `model-routing` — Add an uncertainty-escalation router for cross-surface decisions. A cheap extractor first returns typed claims with source, timestamp, sensitivity, confidence, and contradiction edges. Only claims that are stale, contradictory, safety-sensitive, or action-bearing are sent to faculty-judgement; uncontested informational claims stay on the cheaper tier. The final card must expose unresolved claims rather than silently averaging them.
- **owner gets:** The owner gets fast, concise answers for ordinary questions while important decisions receive real scrutiny. It also makes 'I don't know because these two sources disagree' visible instead of producing a confident but wrong action.
- effort: Medium: claim envelope, contradiction scoring, routing policy, and regression fixtures for stale browser versus local-calendar examples.  ·  risk: A cheap extractor can miss a contradiction and under-escalate. Recover by conservative thresholds, sampling/escalation audits, and mandatory escalation for external side effects or secrets; degradation falls back to no-action with an explicit unknown.
- cost: Reduces expensive-tier calls for uncontested work; adds small classifier/extraction cost. Net expected savings after instrumentation, with no new hardware cost.  ·  latency: Adds tens to hundreds of milliseconds for claim scoring; avoids waiting for the expensive tier unless needed. Consequential actions may take longer by design.
- security: Claims carry sensitivity labels and source boundaries; the router must not merge private browser and general context into a broader prompt than required. Contradiction logs should redact values and retain hashes/citations.
- depends on: Shared typed claim/context envelope; ActionProof postconditions for action-bearing claims; Cross-surface impact scan or equivalent scoped evidence collector

### `integration` — Create a non-mutating commitment-simulation service. It ingests provenance-tagged events from Mac, authenticated browser, and relay, converts them into a temporal dependency graph (including preparation, travel, response obligations, and estimated attention cost), and exposes scenario branches that can be compared and discarded. Every output must separate observed commitments from inferred costs and list the assumptions that would change the result.
- **owner gets:** They can ask about the consequences of saying yes before making a promise, instead of discovering collisions after the fact. The result is actionable without taking control away: a clear tradeoff and the smallest changes required, while their real calendar and accounts remain untouched.
- effort: Large: shared event ontology, authenticated extractors, temporal/dependency reasoning, scenario storage, and tests against partially missing or stale data.  ·  risk: Incomplete sources could make a scenario look safe. Mitigate with freshness thresholds, explicit unknowns, conservative travel/preparation buffers, and a refusal to call a scenario safe when critical commitments are missing. Scenario branches must be read-only and garbage-collected.
- cost: Moderate background inference and storage cost per scenario; deterministic graph calculations keep model spend low. No hardware cost required, though the pendant interaction benefits from a small local scenario cache.  ·  latency: Known-state previews can be near-immediate; complete cross-surface simulations take roughly 10–30 seconds and should stream progress rather than delay the spoken interaction.
- security: Private facts stay scoped by source and sensitivity. Scenario branches must not be treated as authorization to mutate source systems; discard sensitive hypothetical data on expiry and audit which sources contributed to each conclusion.
- depends on: A typed cross-surface event/commitment schema; Authenticated browser and Mac read adapters with provenance and freshness; Durable relay storage for scenario branches; A faculty-judgement contract that distinguishes facts, assumptions, and forecasts


## What it asked for

_Nothing._
## Its own summary

This round added a genuinely cross-surface capability: “Before I commit to this, check what I’m overlooking.” It gathers scoped evidence from the pendant’s spoken intent, authenticated browser tabs, Mac notes/calendar/files, and queued jobs; produces an expiring decision card with citations, contradictions, dependencies, freshness, irreversible effects, and one safest next step. I also proposed uncertainty-escalation routing so cheap extraction handles uncontested facts and faculty-judgement is reserved for conflicts or consequential actions. I told faculty-action to include target, machine-checkable postcondition, deadline, privacy class, reversibility, confirmation requirement, and before/after evidence in every ActionProof.

**Biggest unknown:** The capability still needs a real cross-surface impact-scan/evidence collector, a shared expiring decision-card schema, ActionProof verification wiring, and a pendant approve/hold/resume interaction. I still lack confirmation of the current cross-surface persistence and audio acceptance implementations; the owner’s requested 24 kHz end-to-end audio path remains an independent critical gap.

