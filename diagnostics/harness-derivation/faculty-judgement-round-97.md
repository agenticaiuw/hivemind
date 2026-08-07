# Harness derivation — faculty-judgement — round 97

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Before I commit to this, can I realistically keep the promise?"
- **useful because:** The pendant catches an intended promise while it is still tentative, checks the owner's actual calendar, existing obligations, travel and relevant logged-in threads, and returns one honest answer: feasible, feasible if moved/delegated, or likely to slip. It can place a private hold or draft a follow-up, but never contacts anyone or makes a commitment without approval. This prevents the wearable from merely recording obligations after they become failures.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime model extracts the tentative promise and asks at most one clarifying question; a cheaper background planner gathers calendar/mail/browser evidence and computes time/effort slack; realtime returns the short spoken judgment once the packet is ready.
- **latency:** Immediate acknowledgement in under 1 second; evidence-backed answer in 10–30 seconds. If private browser access is offline, say so and return a clearly marked partial judgment rather than guessing.
- **cost:** Roughly $0.01–$0.05 per check, dominated by background reasoning and private-page extraction; routine calendar-only checks should be near the low end.
- **security:** Promise text, calendar, mail, and authenticated-page excerpts leave the Mac only as an encrypted, minimized evidence packet. Default to private local storage, redact names/content in spoken output, and require confirmation before creating holds, reminders, drafts, or any external action. Never infer a promise from ambient audio without a wake-word or explicit 'check this'.
- **missing:** A durable commitment/obligation object with source utterance, confidence, due window, effort estimate, owner approval state, and expiry; A cross-surface impact scan that can compare the proposed promise with calendar, reminders, active jobs, and authenticated browser evidence; A decision packet that records evidence freshness and partial/blocked status for the pendant response; A postcondition verifier so any created hold or reminder is independently checked rather than trusted from an action receipt

### "If I do this, what else will it affect?"
- **useful because:** Before changing a meeting, deleting a file, accepting an offer, or committing to a plan, the hive builds a read-only counterfactual: downstream calendar collisions, travel slack, reminders, active Mac jobs, browser-account dependencies, and people who would need a draft notice. It distinguishes observed consequences from assumptions and lets the owner choose a safer alternative before anything changes.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime handles the short intent and returns a one-sentence headline; a cheaper background planner gathers evidence and computes alternatives. Escalate to the expensive model only when evidence conflicts or the consequence graph is ambiguous.
- **latency:** Headline acknowledgement under 1 second; complete impact packet in 15–45 seconds. If a surface is offline, label that branch unknown and do not present it as safe.
- **cost:** About $0.02–$0.08 per analysis, dominated by multi-source extraction and conflict reconciliation; no cost for branches that can be answered from fresh local state.
- **security:** Read-only by default. Send minimized identifiers and snippets, not whole mail or page contents. Authenticated browser evidence stays on the Mac/bridge where possible. Any mutation (reschedule, send, delete, purchase) requires the existing explicit confirmation gate and must show before/after effects.
- **missing:** A typed counterfactual/impact graph linking calendar events, reminders, files, jobs, and browser entities with provenance and freshness; A read-only cross-surface preflight that can query all reachable surfaces and return unknowns explicitly; A conflict/assumption classifier so inferred effects cannot be confused with observed ones; An owner-facing decision slate that fits in one spoken headline plus drill-down evidence

### "Should I say yes to this?"
- **useful because:** The hive should help the owner judge a request before reflexively accepting it—not merely whether there is an empty calendar slot. It extracts the actual ask from a message, browser page, or spoken conversation, compares the time and hidden follow-up cost with the owner's stated priorities and existing commitments, identifies pressure or ambiguity, and offers three honest responses: accept, ask a clarifying question, or decline. It must explain the recommendation in terms the owner can challenge, and prepare a reply without sending it.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use the realtime model only to capture the request and return the short recommendation; use a cheaper background model for message/page extraction, effort estimation, and comparison against the owner's priorities. Escalate only when the request is ambiguous or socially sensitive.
- **latency:** A provisional spoken answer in 2 seconds; sourced recommendation in 15–40 seconds. If the relevant account or preference data is unavailable, say 'I can’t judge that part' rather than inventing confidence.
- **cost:** Approximately $0.02–$0.07 per request, mostly background extraction and reasoning; local calendar-only requests should be substantially cheaper.
- **security:** Private messages and browser pages must be minimized to the specific request, with sensitive relationship or health content excluded from spoken output by default. No reply is sent, acceptance is recorded, or calendar time is reserved without explicit approval. Store the owner's preference model locally or encrypted, with per-source disclosure controls.
- **missing:** A durable values-and-boundaries profile that the owner can inspect, correct, and scope by relationship or type of request; A hidden-cost estimator for preparation, travel, emotional labor, and recurring follow-up—not just event duration; A provenance-rich recommendation packet separating quoted request facts, inferred effort, and value judgments; A reply composer that produces accept/clarify/decline drafts while preserving the owner's voice and never auto-sends


## Changes it proposed to its own stack

### `browser-harness` — Add a reconnect quarantine for queued browser commands: every command gets an enqueue timestamp, bridge-session fingerprint, and intent risk class. When the extension returns after being offline, expired or session-mismatched commands remain held; the relay produces a compact review packet showing what would have run, why it was held, and whether the page changed. Only an explicit owner approval or a newly compiled idempotent plan may release a held command. Revalidate page identity and expected preconditions immediately before replay.
- **owner gets:** A command spoken yesterday cannot unexpectedly act on a different tab or stale page when Chrome reconnects. The owner gets a clear recovery choice instead of silent replay or lost work.
- effort: Medium: queue metadata, reconnect state machine, page/session revalidation, and pendant/dashboard review; can be implemented without Accessibility or Screen Recording.  ·  risk: A legitimate long-running read may be held or expire. Recovery is safe replay after revalidation, with read-only commands eligible for an owner-configured longer TTL. Never replay irreversible actions automatically.
- cost: Negligible API cost; one short revalidation request per held command. Small durable queue metadata increase.  ·  latency: Adds roughly 1–5 seconds before replay while session and page identity are checked.
- security: Improves safety by binding commands to a browser session and preventing cross-session execution; review packets must omit page secrets and include only hashes/snippets needed to identify drift.
- depends on: Existing browser command queue with request IDs/idempotency keys and typed results; A durable browser session/bridge status record; Owner-configured TTL and approval policy for held commands

### `memory` — Add an owner-controlled boundary profile, distinct from factual memory: inspectable rules and soft preferences such as protected evenings, acceptable response delay, kinds of favors the owner wants to decline, relationship-specific limits, and how much uncertainty should trigger a question. Each rule carries scope, origin, confidence, expiry, and an easy spoken correction. The planner must show which rule drove a recommendation rather than silently optimizing for inferred values.
- **owner gets:** The assistant can help the owner protect time and relationships according to their actual standards, while remaining corrigible when those standards change. It stops 'helpful' automation from deciding what the owner ought to value.
- effort: Medium: schema, encrypted storage, editor/review UI, retrieval policy, and planner integration.  ·  risk: A stale or overgeneralized boundary could produce an embarrassing decline or missed opportunity. Mitigate with expiry, scope restrictions, quoted rationale, and defaulting to a clarifying question when confidence is low.
- cost: Tiny storage cost; modest model-token increase only when a relevant request is evaluated.  ·  latency: Negligible for cached profile retrieval; up to a few seconds when resolving conflicting scoped rules.
- security: High sensitivity: keep profile encrypted, never expose it to external sites, and require explicit owner confirmation before using a sensitive boundary in a draft or action.
- depends on: A durable provenance-aware context service; A reviewable decision packet with evidence versus inference labels; Existing confirmation gates for external actions


## What it asked for

_Nothing._
## Its own summary

This round I added two genuinely owner-facing gaps beyond the backlog: (1) “Before I commit to this, can I realistically keep the promise?”—a tentative spoken promise is checked against calendar, obligations, travel, active work, and private browser evidence, with no external action without approval; (2) “If I do this, what else will it affect?”—a read-only counterfactual impact graph that surfaces downstream collisions, unknowns, and safer alternatives before a change. I also proposed browser reconnect quarantine so stale or session-mismatched commands cannot silently replay after Chrome returns.

**Biggest unknown:** The missing connective primitives are still not implemented: durable commitment/obligation entities, cross-surface impact/preflight graphs, explicit freshness/unknown semantics, and a compact decision-slate/approval surface. I should not re-request the already-pending tools; those are the concrete work still needed.

