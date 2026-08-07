# Harness derivation — faculty-judgement — round 15

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If that failed because something is disconnected, fix the connection if you can, then try again; otherwise leave me a one-sentence explanation and a ready-to-resume action.”"
- **useful because:** The owner has repeatedly asked for Gmail, GitHub, calendar, and browser access and received opaque failures. This turns a dead end into either a safe recovery or a durable handoff, without making them repeat context or guess which machine is broken.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use realtime only to acknowledge and ask for confirmation when needed; use the cheaper background planner for diagnosis/retry and the dashboard for a durable blocker card. The Mac planner inspects bridge health and local permissions, the browser harness checks extension/session state, and relay coordinates the result back to the pendant.
- **latency:** Speak an immediate acknowledgement in under 1 second; diagnose common failures in 5–15 seconds; if reauthorization or human input is needed, stop and present one concrete next step rather than looping.
- **cost:** Roughly $0.01–$0.06 per recovery attempt, dominated by planner/browser calls; health checks and typed error classification should be near-zero marginal cost.
- **security:** Never silently bypass permissions or reauthenticate. Reading private pages remains allowed under the owner's standing browser permission, but sending mail, deleting, purchasing, or submitting forms still requires confirmation. Store only an error class, attempted surfaces, and a resumable intent—not page contents or credentials. Ask before opening an external auth flow if it could expose account data.
- **missing:** A typed cross-surface error taxonomy with remediation recipes and safe retry limits; A durable intent-escrow record that preserves the original request, required confirmation state, and last failure; A browser/Mac health and authorization probe exposed to the relay; A dashboard/pendant response format for one-sentence blockers plus a resume action

### "“Keep an eye on whether today’s plan is still realistic. If a meeting, unfinished task, or new deadline makes it impossible, tell me what changed and give me the smallest useful replanning choice.”"
- **useful because:** A morning brief tells the owner what exists; it does not notice that the day has become impossible. This would reconcile calendar commitments, authenticated work pages, actual Mac activity, and the owner's spoken priorities, then interrupt only for a consequential conflict with an actionable choice.
- **path:** relay → mac-bridge → browser → pendant → dashboard
- **model tier:** Run scheduled and event-triggered reconciliation on a cheaper background model; reserve realtime for the short interruption and the owner's choice. Browser reads private calendar/task/work pages, Mac supplies local task/file state, relay maintains the plan graph, and the dashboard shows the evidence and alternatives.
- **latency:** Reconcile on calendar/account events or every 30–60 minutes while the Mac is active; deliver a 10-second spoken alert only for high-confidence conflicts. Replanning should finish within 30 seconds, otherwise leave a queued card.
- **cost:** About $0.02–$0.10 per daily plan, dominated by authenticated-page extraction and one planning pass; event deltas and unchanged-page hashes keep routine cost low.
- **security:** Read-only by default. Do not infer sensitive health, employment, or relationship facts from page content beyond what is needed for the plan. Never reschedule, message, or modify tasks without explicit confirmation. Pendant speech may be overheard, so speak only a generic alert and offer details on the Mac.
- **missing:** A typed personal-plan graph linking commitments, tasks, deadlines, dependencies, and confidence; Event/delta feeds from calendar, mail, task boards, and browser watches rather than repeated full-page polling; A local Mac activity signal that reports coarse progress without uploading raw screen contents; Quiet-hours, interruption-priority, and spoken-detail policy (already requested but not yet available)

### "“Handle this privately.”"
- **useful because:** Today the pendant, relay, Mac, and browser do not share a reliable way to keep sensitive results off an overheard voice channel. The owner should be able to start a task aloud and have the system automatically route private details to the Mac or browser, while the pendant says only a safe summary and offers a local continuation cue.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the realtime model only for the brief spoken acknowledgement and safe summary; use a cheaper planner to classify sensitivity, execute read-only browser/Mac work, and compose the private result. The relay enforces the output route rather than trusting the model’s wording.
- **latency:** A safe acknowledgement in under 1 second; route classification in under 2 seconds; private results can arrive asynchronously on the Mac/browser within 15 seconds. If the route cannot be verified, say nothing beyond that the result is waiting on the Mac.
- **cost:** Approximately $0.01–$0.05 per task, mostly planner and authenticated browser work; route checks and redaction are deterministic and negligible.
- **security:** Treat credentials, health, finances, private messages, and page contents as sensitive by default. Never read sensitive content aloud unless the owner explicitly overrides. Keep raw results on the Mac/browser where possible, send the relay only a redacted status, require confirmation before any external or irreversible action, and show an audit trail of where each datum was delivered.
- **missing:** A cross-surface sensitivity and delivery-policy protocol enforced outside the model; A trusted local-presence/attention signal from the Mac or pendant to distinguish an owner-only display from an overheard channel; Typed redaction and result-handoff primitives linking a relay job to a private Mac/browser panel; A user-visible policy editor for phrases such as “handle this privately,” plus a safe default when presence cannot be established


## What it asked for

### `t5-tkcm` (tool) — cross_surface_recovery
- why: The owner’s repeated Gmail/GitHub/calendar/browser failures currently collapse into opaque failure. This tool would let the judgement layer classify a failed intent, inspect safe local/browser health signals, and return a bounded remediation or resumable blocker without credentials or irreversible actions.

```json
{
  "type": "object",
  "required": [
    "intent_id",
    "original_request",
    "attempted_surfaces"
  ],
  "properties": {
    "intent_id": {
      "type": "string"
    },
    "original_request": {
      "type": "string"
    },
    "attempted_surfaces": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": [
          "pendant",
          "relay",
          "mac",
          "browser"
        ]
      }
    },
    "allow_reversible_repairs": {
      "type": "boolean"
    },
    "retry_budget": {
      "type": "integer",
      "minimum": 0,
      "maximum": 2
    }
  }
}
```

## Its own summary

Discovered the owner’s repeated opaque failures for Gmail/GitHub/calendar/browser and the current surfaces (LTE-M pendant, Mac bridge, browser, relay, D1/R2). Proposed two new owner-facing capabilities: bounded cross-surface failure recovery with a resumable one-sentence blocker, and event-driven plan-risk detection that interrupts only when the day becomes infeasible. Requested a precise cross_surface_recovery tool.

**Biggest unknown:** The actual harness-ledger priorities, interruption preferences/notification inventory, and persistence primitives remain unavailable this round; those determine which proposed capability should be built first and how safely it may interrupt.

