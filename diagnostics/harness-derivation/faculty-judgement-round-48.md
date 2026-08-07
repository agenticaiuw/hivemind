# Harness derivation — faculty-judgement — round 48

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Learn how much freedom I want: handle routine, reversible things without bothering me, but ask at the right boundary—and show me when you think my boundary should change.”"
- **useful because:** Today every cross-surface job either interrupts for approval or risks acting with the wrong authority. A personal autonomy policy turns the hive into a trustworthy delegate: it uses reversibility, money, audience, uncertainty, and deadline pressure to decide whether to act, queue, or ask. The pendant can capture a spoken policy in the moment; the relay keeps it available; Mac/browser supply impact and execute; judgement explains the boundary. The policy can learn from explicit approve/edit/reject outcomes, but never silently expand authority.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision → unified → faculty-judgement → faculty-action
- **model tier:** Use the cheap background model to classify risk, reversibility, audience, and policy matches; use realtime only to explain a boundary during a live voice interaction. Escalate ambiguous/high-stakes cases to the judgement model.
- **latency:** Routine classification under 500 ms and no interruption; a live boundary explanation under 2 s. Policy-learning summaries can run hourly or overnight.
- **cost:** Usually <$0.01 per job using a small classifier and cached typed context; realtime cost only for escalations. Dominant cost is context retrieval, so send compact action facts and policy clauses rather than full histories.
- **security:** Policies are sensitive behavioral data and must remain owner-scoped. Never infer permission from silence or from one approval; require explicit confirmation to broaden a rule. External messages, purchases, legal/health actions, credential changes, and irreversible operations retain hard approval gates. Show the exact policy clause, evidence, and predicted impact whenever acting autonomously; keep a revocable audit trail.
- **missing:** A typed autonomy-policy store with versioning, scope (surface/account/action), risk dimensions, expiry, and explicit deny rules; A deterministic policy evaluator shared by relay, Mac, browser, and pendant offline queue; Outcome feedback events (approve/edit/reject/undo) and a review UI that proposes—but does not apply—policy changes; A cross-surface risk/reversibility/audience classifier and a safe fallback when required surfaces are offline

### "“Let me approve a plan once with conditions—if the price, wording, recipient, and deadline stay within these limits, finish it; otherwise pause and ask me.”"
- **useful because:** An approval today is a snapshot, but real transactions change while they are being prepared: prices move, pages refresh, recipients change, and a deadline can pass. The owner should be able to delegate a bounded conditional commitment instead of either micromanaging every step or granting an unsafe blanket permission. The browser watches the authenticated source and gathers fresh evidence; Mac prepares and executes; the relay keeps the escrow alive; the pendant gives a spoken status and an immediate cancel gesture even when the owner is away. If any condition becomes false, the plan freezes rather than improvising.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a cheap deterministic constraint evaluator for every step and a small background model only to normalize natural-language conditions into a reviewable schema. Use the realtime model only when the pendant must explain a violated condition or resolve an ambiguity live.
- **latency:** Condition checks should be sub-second for already-available page/state evidence; refreshes can take seconds. Never wait on a model for the safety decision. A violation alert should reach the pendant within 2 seconds when online.
- **cost:** Typically <$0.01 per step with deterministic checks and compact browser extracts; authenticated refreshes and long-running monitoring dominate cost, not generation. Expired escrows should stop polling.
- **security:** This is delegated authority, so conditions must be shown in plain language and as exact machine predicates before approval. Default-deny on missing evidence, stale tabs, changed account, ambiguous recipient, or parser failure. Bind approval to action scope, account, maximum spend, content hash/template, and expiry; require a fresh explicit confirmation for any condition broadening. Store sensitive evidence locally or encrypted, and provide pendant emergency revoke.
- **missing:** A durable conditional-commitment/escrow object with immutable approved predicates, expiry, and step receipts; A browser freshness and semantic-diff service that can prove the observed values still satisfy predicates; A cross-surface cancel/revoke signal with delivery acknowledgment and safe handling when offline; A constraint compiler and human-readable preview that cannot silently weaken or reinterpret conditions; A transaction executor that revalidates predicates immediately before every irreversible step


## Changes it proposed to its own stack

### `context` — Create a versioned Autonomy Policy Engine shared by relay, Mac, browser, and pendant. Compile plain-language owner rules into deterministic predicates over action class, reversibility, spend, audience, uncertainty, deadline, account, and current attention state. Return one of ACT, PREPARE, QUEUE, or ASK with the matched rule, evidence, expiry, and required confirmation. Record outcome feedback separately and generate proposed policy diffs for owner review; never self-amend permissions. Cache only signed, expiry-bounded rules on the pendant for offline queue decisions.
- **owner gets:** The owner gets consistent behavior instead of one surface asking while another acts, and can safely say “don’t interrupt me for harmless cleanup” without accidentally authorizing a sensitive external action. When disconnected, the pendant can still capture and classify intent without pretending it has authority to send.
- effort: Medium-high: policy schema/compiler, shared evaluator in relay and Mac agent, browser/action adapters, dashboard review flow, signed pendant cache, and adversarial tests for rule conflicts and stale policies.  ·  risk: A compiler bug could over-authorize actions or create surprising interruptions. Default-deny on parse failure, conflicts, stale signatures, missing evidence, or offline external side effects. Roll back by activating the previous policy version and drain queued actions through re-evaluation.
- cost: Small per-job classifier/evaluator cost (<$0.01 typical); engineering cost is substantial. Pendant storage is tiny (signed compact rules, likely <16 KB) and negligible power compared with radio/audio.  ·  latency: Local deterministic evaluation adds <50 ms; cross-surface evidence gathering may add 0.5–2 s only for borderline cases. Offline pendant capture remains immediate.
- security: High-value permission surface: require explicit owner confirmation to install or broaden policies, cryptographic versioning, scope-limited rules, deny precedence, and immutable audit records. Do not export raw conversational history when compiling rules.
- depends on: A durable cross-surface job/event identity and receipts; Action Lease/approval/provenance gates already being built; Typed context projection with freshness and sensitivity labels; Pendant offline handoff and local interruption primitives


## What it asked for

### `t17-1jsi` (tool) — autonomy_policy_evaluate
- why: A shared deterministic evaluator is needed so relay, Mac, browser, and pendant make the same ACT/PREPARE/QUEUE/ASK decision without asking the expensive model on every job. It must be fail-closed and expose matched rules for owner-facing explanations.

```json
{
  "type": "object",
  "required": [
    "action",
    "context"
  ],
  "properties": {
    "action": {
      "type": "object",
      "properties": {
        "kind": {
          "type": "string"
        },
        "target": {
          "type": "string"
        },
        "reversible": {
          "type": "boolean"
        },
        "external_side_effect": {
          "type": "boolean"
        },
        "spend_cents": {
          "type": "integer"
        },
        "audience": {
          "type": "string"
        },
        "deadline": {
          "type": "string"
        }
      }
    },
    "context": {
      "type": "object",
      "properties": {
        "surface": {
          "type": "string"
        },
        "attention_state": {
          "type": "string"
        },
        "confidence": {
          "type": "number"
        },
        "evidence_refs": {
          "type": "array"
        },
        "policy_version": {
          "type": "string"
        }
      }
    },
    "mode": {
      "type": "string",
      "enum": [
        "evaluate",
        "explain"
      ]
    }
  }
}
```

## Its own summary

This round I proposed a genuinely new owner capability: a learnable, fail-closed personal autonomy boundary spanning pendant, relay, Mac, browser, and action surfaces. It distinguishes ACT/PREPARE/QUEUE/ASK using reversibility, audience, spend, uncertainty, deadlines, and attention; learns only through explicit reviewed outcomes and never silently broadens authority. I also proposed the shared versioned Autonomy Policy Engine and requested the missing `autonomy_policy_evaluate` tool, with deterministic fail-closed output and matched-rule explanations.

**Biggest unknown:** The still-unresolved implementation dependencies are the durable cross-surface job/event identity, the exact Action Lease/approval/provenance primitives, typed context freshness/sensitivity fields, pendant offline handoff/interruption behavior, and the owner's interruption preferences. Those determine which policy decisions can safely execute versus queue or ask.

