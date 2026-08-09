# Harness derivation — faculty-judgement — round 237

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **action-risk-policy** — For faculty-action coordination, classify R0 read-only/local observation, R1 reversible local mutation, R2 external side effect or sensitive disclosure, R3 irreversible/destructive/spend/commit. Unknown or moving motion permits R0 only by default; stillness never counts as consent. R1 needs an independently approved plan and verified undo; R2/R3 require deliberate physical approval.
  - evidence: Judgement policy sent to faculty-action in Round 237; grounded in existing autonomy_policy_evaluate and physical_transaction_approval_latch constraints.

## Capabilities it proposed

### "“Did that actually happen, everywhere it was supposed to—and if not, fix only what is missing?”"
- **useful because:** Receipts currently prove server acceptance or Mac execution, not the owner's intended outcome. This would verify the postcondition across relay, Mac, browser, and pendant delivery, distinguish partial success from failure, and offer a reversible repair instead of falsely saying done. It is the single most useful missing behavior: trustworthy completion of real-life requests.
- **path:** relay → mac → browser → pendant
- **model tier:** Background model for invariant extraction and repair planning; realtime only for the concise spoken result. Deterministic checks should run without an LLM.
- **latency:** Initial verification 2–5 seconds across surfaces; repair planning under 10 seconds; never delay the owner's immediate acknowledgement—say “checking outcome” first.
- **cost:** Roughly $0.005–$0.03 per verification when model interpretation is needed; most checks are local route calls and cost near zero. Browser/Mac round trips dominate latency.
- **security:** Verify only declared postconditions, never infer success from a screenshot alone, and redact sensitive state in spoken output. Repairs require autonomy_policy_evaluate and physical approval for external or irreversible effects. Persist a source-linked outcome record, not page bodies or audio.
- **missing:** A typed postcondition/invariant schema attached to each plan before execution; A durable relay-job ↔ Mac/browser action join key (currently only telemetry localJobId); Read-only state adapters for each effect (calendar/reminders and some browser outcomes are incomplete); A repair planner that can emit a minimal diff and route it through existing undo/approval gates

### "“Before you act, show me whether the plan is still about what I asked for—not just whether the buttons still work.”"
- **useful because:** A plan can remain technically executable while its meaning drifts: a changed recipient, page, price, deadline, or file can turn a once-approved action into the wrong action. This semantic scope sentinel compares the original request, prepared steps, current observations, and intended audience, then blocks or asks only when the meaning changed.
- **path:** relay → mac → browser → pendant
- **model tier:** Cheap deterministic field/rule comparison first; use the background model only to extract a typed intent and explain a detected semantic delta. Realtime speaks the short ask/decision.
- **latency:** Under 1 second for digest and field checks; up to 4 seconds for model-assisted ambiguity. No mutation until the verdict is available.
- **cost:** Usually under $0.01 per recheck; model cost only for ambiguous natural-language intent or changed entities. Browser snapshot and Mac reads dominate.
- **security:** Never expose private snippets in the relay verdict by default. Compare hashes, entity IDs, amounts, domains, recipients, and deadlines; reveal changed text only on the local dashboard. A changed external audience, spend, or destructive effect must fail closed and require fresh physical consent.
- **missing:** A durable typed intent digest with owner-visible fields and semantic version; Adapters that extract stable recipient/amount/domain/deadline fields from every Mac/browser action; A cross-surface plan join key and signed observation snapshot; A policy rule distinguishing harmless presentation drift from meaning-changing drift

### "“Keep me inside a daily risk budget, and tell me before my requests collectively cross it.”"
- **useful because:** Per-action approval misses accumulation: many individually reversible actions can collectively spend money, disclose information, send messages, or consume the owner's attention. A cross-surface budget would track external side effects, sensitive disclosures, irreversible operations, and interruption load, warn before a threshold, and let the owner set or revoke budgets without hiding policy in code.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Deterministic policy and ledger evaluation; background model only classifies an unstructured request into budget dimensions. Realtime handles the concise warning and asks for consent.
- **latency:** Under 300 ms for a policy check and ledger lookup; under 2 seconds if classification is needed. Budget status should be available offline on the pendant as a signed last-known summary.
- **cost:** Near-zero for deterministic checks; under $0.005 for occasional classification. Storage and route reads dominate, not model inference.
- **security:** Budgets must be owner-scoped, tamper-evident, and fail closed when accounting is unknown. Never count sensitive content itself in the relay ledger; store category, amount, destination class, policy version, and evidence references. Crossing a budget can warn or require physical consent, but never silently authorize an external side effect.
- **missing:** A durable cross-surface effect ledger with idempotent entries and reversal/void records; Owner-configurable budget dimensions, windows, and escalation rules (shipping conservative and visibly unset); A reliable relay/Mac/browser correlation ID and signed receipts for actual, not merely planned, effects; Pendant envelope support for compact budget status and offline fail-closed decisions

### "“Before you tell me something as fact, tell me whether it has gone stale—and automatically stop treating old assumptions as true.”"
- **useful because:** Today provenance can explain where a claim came from, but it does not make freshness a first-class property. A flight price, meeting status, delivery estimate, browser page, permission, or personal preference can remain confidently promptable after its validity window has passed. The owner should get claims with explicit freshness, decay, and retraction behavior: stale claims become questions or observations to refresh, never silent facts.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Deterministic freshness engine for timestamps, source-specific validity windows, and contradiction handling; background model only extracts the subject and expected validity from unstructured observations. Realtime speaks only the confidence/freshness summary.
- **latency:** Under 200 ms to evaluate an existing claim; under 3 seconds to refresh one source. Never block an urgent safety alert, but downgrade stale content and say that it is unverified.
- **cost:** Near-zero for decay and expiry checks. Occasional background extraction costs under $0.01 per new claim; source refreshes and browser/Mac reads dominate.
- **security:** Store claim metadata, hashes, source IDs, confidence, and validity windows rather than raw quotes in the relay. Stale must never mean deleted: preserve revocation and audit records. A stale or contradicted claim must not authorize an external action without fresh evidence and physical consent.
- **missing:** A typed claim lifecycle with observed_at, valid_until, freshness policy, contradiction, and retraction states; Source-specific freshness defaults for mail, calendar, browser pages, permissions, prices, and owner preferences; A writer and revocation cascade connecting evidence capsules to memory facts and context-graph copies; A pre-speech and pre-action freshness gate used by pendantSpeech, audioBrief, and execution planning

### "“What did you choose not to tell me today, and what would have made you tell me?”"
- **useful because:** The owner currently sees spoken and queued results, but not the important omissions created by suppression, stale evidence, uncertainty, privacy rules, or missing permissions. A bounded omission ledger would make silence inspectable: each withheld item has a reason, policy version, expiry, evidence reference, and a safe summary. This lets the owner correct bad suppression without requiring the system to interrupt them in real time.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Deterministic capture of suppression decisions and policy explanations; background model only clusters repetitive omissions into a daily digest. Realtime answers a specific “what did you hide?” query.
- **latency:** Decision logging under 100 ms; on-demand explanation under 2 seconds; daily digest generated in the background.
- **cost:** Near-zero for structured decision records; under $0.01 for an occasional clustering digest. Storage is bounded by retaining summaries and evidence references, not content.
- **security:** The ledger must not become a covert notification archive. Store redacted summaries, sensitivity class, source reference, policy rule, and expiry—not raw mail, page text, or secrets. Private omissions require local-dashboard-only detail; spoken responses reveal only category and reason unless explicitly requested.
- **missing:** A durable omission record schema and bounded retention policy; A mandatory hook from attention_arbitrate, autonomy_policy_evaluate, freshness gates, and permission failures; A local dashboard view and a safe spoken query surface; A distinction between intentionally suppressed, unavailable, stale, and never-observed items


## What it asked for

_Nothing._
