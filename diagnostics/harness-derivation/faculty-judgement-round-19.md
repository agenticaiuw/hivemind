# Harness derivation — faculty-judgement — round 19

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If this takes a while, keep going—but stop and ask me if the facts or my intention changed before you do anything consequential.”"
- **useful because:** Long-running work currently risks resuming against a changed page, price, deadline, or owner intention. This creates a single owner-facing continuity contract: the pendant captures the original goal, the relay versions it and records assumptions, the Mac/browser re-check reality after interruptions, and the pendant asks one short question only when a material change or ambiguity is detected. It is safer than blindly resuming and less annoying than re-confirming every step.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-action → unified
- **model tier:** Background/cheap model continuously compares compact evidence and intent versions; realtime model is used only for the brief spoken clarification and final receipt.
- **latency:** No added latency for ordinary steps. After an outage or meaningful page/state change, 1–3 seconds to compute a diff; clarification is one spoken turn. Consequential execution waits indefinitely for the owner's answer.
- **cost:** About $0.005–$0.03 per resumed job, dominated by background semantic comparison; near-zero for stable jobs because hashes and typed fields avoid re-sending full pages.
- **security:** Private page content remains on the Mac/browser bridge; relay stores redacted intent, field hashes, provenance, and sensitivity labels rather than raw secrets. Sending, deleting, purchasing, or submitting always requires explicit confirmation. The system must never infer that silence means approval.
- **missing:** Durable job runner and result stream with jobId/step cursor; Typed intent-version and assumption ledger shared by relay, Mac, and browser; Material-change policy for prices, dates, recipients, permissions, and destructive actions; Owner-facing readiness snapshot and a small clarification/response protocol; Idempotency and evidence reconciliation at the action boundary

### "“When your sources disagree, don't guess—tell me the conflict in one sentence, let me choose which source to trust, and remember that choice for this situation.”"
- **useful because:** Today a relay, Mac, and logged-in browser can each hold partial or contradictory truth (for example, a stale calendar tab versus a refreshed account page). The owner cannot reliably see that disagreement; a smooth summary can turn uncertainty into a wrong action. This gives them an explicit, low-friction way to adjudicate reality and have the decision follow the task across devices without teaching the system a dangerous global preference.
- **path:** faculty-perception → relay-realtime → mac-planner → browser-extension → pendant → faculty-action → unified
- **model tier:** Cheap background model clusters and compares typed observations; realtime model speaks only the conflict and records the owner's choice. Use the expensive tier only when the conflict is genuinely ambiguous or safety-critical.
- **latency:** No delay when sources agree. On disagreement, produce a 1–2 sentence spoken conflict within 2 seconds and pause only the affected action; unrelated work continues. The owner's choice should take one voice turn or button press.
- **cost:** Roughly $0.01–$0.05 per conflict, dominated by semantic normalization; ordinary agreeing observations use hashes/typed fields and cost almost nothing.
- **security:** Show provenance without leaking private page contents aloud in public settings; the pendant should say source names and redacted values, with full evidence available on the Mac. Choices are scoped to job/entity/time and expire by default—never silently become a universal trust ranking. Sending, deleting, purchasing, or submitting still requires explicit confirmation.
- **missing:** A typed cross-node observation and contradiction schema with provenance, timestamps, freshness, and scope; A relay-held conflict record and signed owner adjudication that Mac/browser/action agents can consume; A pendant interaction supporting a short two-option answer and private/full-detail escalation; A policy engine that blocks only the disputed action while allowing independent steps to proceed; A durable event stream so the adjudication survives reconnects and browser/Mac restarts


## Changes it proposed to its own stack

### `context` — Add a cross-surface Intent Continuity Ledger. At plan creation, persist a compact signed intent record: goal, allowed side effects, deadlines, entities/recipients, numeric thresholds, assumptions, evidence hashes, owner-approved version, and expiry. Every resumed Mac/browser step submits a typed observation; the relay computes a material-diff classification (unchanged, safe drift, needs owner, expired), increments the intent version on spoken edits, and blocks faculty-action at the boundary for needs-owner/expired states. The pendant receives a single clarification card/audio prompt and records the answer as a new signed version.
- **owner gets:** A task that took ten minutes—or survived a sleep, Wi‑Fi loss, or browser restart—will not quietly act on yesterday's facts. The owner gets a concise question only when something genuinely changed, with an understandable explanation of what changed.
- effort: Medium-high: shared schema, relay persistence, Mac/browser observation adapters, diff policy, pendant prompt/answer plumbing, and end-to-end crash/retry tests.  ·  risk: False positives could interrupt harmless work; false negatives could allow stale actions. Recover with conservative defaults for consequential actions, explicit expiry, human-readable diffs, and replay tests using saved evidence. Ledger corruption must fail closed, not execute.
- cost: Small D1/R2 storage and one cheap comparison call per resumed or materially changing step; no model call for exact field/hash matches.  ·  latency: Negligible on stable steps; roughly 1–3 seconds when semantic comparison is needed, plus owner response time for a blocked consequential action.
- security: Improves safety by enforcing side-effect bounds and provenance. Store hashes/redacted values by default; encrypt sensitive observations and never expose browser secrets to the relay model.
- depends on: Durable browser job runner with jobId and retry cursor; Typed context projection with provenance/TTL; Cross-surface readiness and event persistence primitives; Explicit action receipts and idempotency keys

### `integration` — Create a Contradiction Broker between perception and action. Mac, authenticated browser, relay schedules, and pendant observations publish typed claims keyed by entity/field, each carrying source, observedAt, freshness, evidence pointer, and scope. The broker preserves competing claims instead of last-write-wins, computes a conflict card, and exposes an atomic adjudication endpoint whose result is scoped to the current job/entity and expiry. faculty-action must require a resolved claim for any affected consequential step; unrelated plan branches continue.
- **owner gets:** When two devices disagree, the owner sees exactly what is uncertain and can settle it once instead of receiving a confident but wrong answer—or being forced to restart the entire task.
- effort: High: claim schema and normalization, durable conflict state, provenance/evidence adapters on Mac and browser, pendant two-choice interaction, action-gate integration, reconnect/replay tests.  ·  risk: Over-reporting harmless timing differences could make the system noisy; under-reporting semantic conflicts is unsafe. Start with a narrow field allowlist (dates, amounts, recipients, availability, permissions), require freshness windows, and allow an explicit dismiss-with-scope action. If the broker is unavailable, consequential actions fail closed and read-only summaries identify the limitation.
- cost: Low storage and compute for typed claims; one cheap comparison per potentially conflicting field, with no expensive model call when normalized values match.  ·  latency: Zero on matching claims; approximately 1–2 seconds to normalize and render a conflict, then only the owner's response time for the affected branch.
- security: Evidence pointers and redacted claims cross the relay; raw authenticated content stays on the Mac/browser. Scoped, expiring adjudications prevent a choice about one invoice or date from becoming a global trust rule.
- depends on: Cross-surface event persistence; Typed provenance-aware context projection; Authenticated browser evidence extraction; Pendant clarification input and audio output; Faculty-action precondition enforcement


## What it asked for

### `t9-8axw` (tool) — intent_continuity_ledger
- why: Implement the proposed stale-intent guardian: persist a signed goal/version/assumption record and compare resumed Mac/browser observations before consequential actions.

```json
{
  "operation": "string enum: create, observe, classify, supersede, answer, get",
  "jobId": "string",
  "intentVersion": "string optional",
  "goal": "string optional",
  "allowedSideEffects": "array optional",
  "assumptions": "array of objects {key,value,source,expiresAt} optional",
  "observations": "array of objects {key,value,source,timestamp,sensitivity,evidenceHash} optional",
  "ownerAnswer": "string optional",
  "idempotencyKey": "string optional"
}
```

## Its own summary

Proposed a new cross-surface capability and context-layer change: Intent Continuity Ledger / stale-intent guardian. It versions the owner's goal and assumptions, compares resumed Mac/browser observations, and asks one concise pendant clarification only for material drift before consequential actions. Requested a precise intent_continuity_ledger tool.

**Biggest unknown:** The exact durable job/event primitives and owner interruption policy are still unavailable, so the schema and material-drift thresholds cannot yet be grounded in the live implementation.

