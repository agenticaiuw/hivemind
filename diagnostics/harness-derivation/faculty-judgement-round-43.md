# Harness derivation — faculty-judgement — round 43

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If you can do this within these limits, just handle it; otherwise ask me.” For example: “Rebook my flight to arrive before six, under $300, and use the same airline if possible.”"
- **useful because:** Today the owner must remain in the loop for every multi-step task, or grant an unsafe blanket permission. A bounded delegation contract lets them express the outcome, budget, deadline, acceptable substitutions, and forbidden actions once. The pendant captures it in the moment; browser and Mac gather and act; the owner is interrupted only when a constraint is ambiguous or would be exceeded, with a final receipt and undo where possible.
- **path:** pendant → relay → browser → mac-bridge → dashboard
- **model tier:** Use the realtime tier only to turn the spoken request into a short, read-back contract and to handle an exception conversation. Use a cheaper background model for option search, constraint checking, and receipt summarization; deterministic policy code, not a model, decides whether an action is inside the contract.
- **latency:** Read-back in under 3 seconds. Background research can take minutes. If a valid option is found, execute without another interruption; if not, deliver one concise exception prompt on the pendant and leave the job resumable.
- **cost:** About $0.01–$0.08 per ordinary delegation, dominated by authenticated page extraction and one background reasoning pass; realtime cost occurs only at initial read-back or exception.
- **security:** The contract must be explicit about spend ceiling, data scope, expiration, allowed vendors/accounts, and irreversible actions. Never infer permission from a vague phrase. Require a spoken/button confirmation for purchases, sending messages, or exposing sensitive data unless the owner explicitly included that action and a ceiling in the contract. Store only a hashed contract plus provenance; browser credentials remain in the browser, and every mutation gets before/after evidence and an undo/rollback attempt.
- **missing:** A typed delegation-contract schema with hard predicates (amount, date, vendor, destination, account, action class) and an expiration.; A policy evaluator shared by relay, browser, and Mac that can fail closed and emit a human-readable reason.; A durable exception/resume queue that can wake the pendant without losing the contract or search evidence.; A simulation/preview endpoint that shows the exact actions that would occur before the owner opts into autonomous execution.

### "“Before I commit to this, show me what saying yes will cost.” For an invitation, appointment, purchase, or deadline, compare the real alternatives and tell me the likely schedule, travel, money, preparation, and privacy consequences—without changing anything."
- **useful because:** The owner currently gets reminders and task execution, but not a trustworthy counterfactual of the life consequences before a decision. This would turn scattered calendar entries, authenticated reservations, mail, files, and current Mac state into an evidence-backed choice: what collides, what preparation is required, what can be canceled, what the worst case costs, and what remains unknown. The pendant gives a short spoken answer while the Mac/browser workbench keeps the detailed evidence for review.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic temporal, financial, travel, and conflict calculations first. A background model can summarize scenarios and identify missing evidence; reserve realtime only for the owner's spoken question and a follow-up clarification. Never let a language model silently invent a consequence or treat a soft preference as a hard fact.
- **latency:** A spoken triage answer in under 5 seconds from cached context; a complete comparison in under 2 minutes. If authenticated pages are unavailable, say exactly which scenario inputs are stale rather than pretending the result is current.
- **cost:** Roughly $0.02–$0.15 per comparison, dominated by authenticated page reads and optional travel/price lookups; most arithmetic and unchanged facts are cached and incur no model cost.
- **security:** This crosses highly sensitive calendar, mail, travel, financial, and possibly health data. Keep raw records on their owning surface, pass only extracted facts with source, timestamp, sensitivity, and confidence, and show citations for every claimed consequence. The feature is read-only by default; cancellation, acceptance, purchase, or sending a message still requires a separate explicit action and confirmation.
- **missing:** A counterfactual scenario model that can fork a proposed commitment without mutating the real calendar or accounts.; Cross-surface fact extraction for duration, travel time, cost, preparation, cancellation terms, and privacy/data exposure, with freshness and uncertainty attached.; A consequence graph that distinguishes hard collisions from soft tradeoffs and supports “if I decline,” “if I delay,” and “if I delegate” branches.; A pendant response format for uncertainty: concise spoken conclusion plus a button/voice path to hear the top three assumptions and open the cited workbench.


## Changes it proposed to its own stack

### `integration` — Add a cross-surface Delegation Contract service. At capture, normalize spoken intent into typed constraints and read it back. Issue a signed, expiring contract ID to relay, browser, and Mac. Each proposed action must present its source evidence, predicted side effects, and a deterministic policy verdict (allowed, needs confirmation, or refused). Persist a resumable exception state and a compact receipt; revoke the contract on owner command or expiry.
- **owner gets:** The owner can hand off a bounded real-world task while walking away without either micromanaging every click or giving the assistant open-ended authority. They hear only the one decision that genuinely falls outside their stated limits.
- effort: Medium-high: schema and evaluator, adapters in browser/Mac action runners, pendant read-back/interrupt path, durable state and dashboard preview, plus adversarial tests for ambiguous constraints and replay.  ·  risk: A parser could misunderstand a spoken limit, or a stale contract could authorize an unwanted action. Recover by mandatory read-back, short TTL, idempotency keys, fail-closed evaluation, pre-action recheck, and immediate revoke/undo controls. If any surface disappears, pause rather than downgrade to a different account or action.
- cost: Low ongoing API cost: mostly deterministic evaluation and background models; roughly $0.01–$0.08 per delegation. Storage is small typed JSON plus evidence references.  ·  latency: Adds 1–3 seconds for read-back and policy compilation; no added latency to background search beyond one deterministic check per action.
- security: Improves security by replacing broad trust with least-privilege, expiring, auditable authority. Sensitive values should remain on their owning surface; the relay sees predicates and receipt references, not credentials or full page contents.
- depends on: A durable cross-surface job/receipt primitive; Typed context/provenance projection so constraints cite fresh evidence; Browser and Mac action gates that can return a refusal instead of executing; A pendant-local interruption/read-back path


## What it asked for

### `t16-iybw` (tool) — delegation_contract_compile_and_check
- why: Bounded delegation is the new owner-facing capability proposed this round. It needs a deterministic, shared service to compile a spoken request into explicit constraints and check each planned action before any browser or Mac mutation; without this, the feature would rely on unsafe model judgment.

```json
{
  "type": "object",
  "required": [
    "mode",
    "request_or_contract",
    "action"
  ],
  "properties": {
    "mode": {
      "type": "string",
      "enum": [
        "compile",
        "check",
        "revoke"
      ]
    },
    "request_or_contract": {
      "type": "string",
      "description": "For compile: owner's transcribed request. For check/revoke: signed contract JSON or contract ID."
    },
    "action": {
      "type": "object",
      "description": "For check: proposed action with target surface, account scope, amount, data classes, reversibility, and evidence references."
    },
    "contract_id": {
      "type": "string"
    },
    "now": {
      "type": "string",
      "description": "ISO timestamp used for expiry and freshness checks."
    }
  }
}
```

## Its own summary

Proposed a genuinely new bounded Delegation Contract capability: the owner can say “handle this within these limits,” with the pendant doing read-back, relay holding an expiring signed contract, browser/Mac gathering and acting, deterministic policy checks before every mutation, and a resumable exception/receipt path. Also proposed the cross-surface contract service and queued a precise compile/check/revoke tool request. Still needed: the contract evaluator/schema, adapters in browser and Mac action gates, durable exception/resume state, and a pendant-local read-back/revoke path. I do not need another owner preference or broad context request to define this design.

**Biggest unknown:** Whether the existing action/receipt primitives can fail closed and expose enough structured metadata (spend, account, data class, reversibility, evidence freshness) for deterministic contract checks; if not, those adapters are the critical prerequisite.

