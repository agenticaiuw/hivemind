# Harness derivation — faculty-judgement — round 105

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **round-105-grants** — No new grants are exposed in the granted category this round; the live device inventory remains Mac bridge online, browser offline, no pendant registered.
  - evidence: discover(granted) returned an empty item list; prior device discovery in this round reports home-macbook-bridge online, home-chrome offline, cloudflare-contract-test offline.

## Capabilities it proposed

### "When I correct you—like changing a reminder time, shortening a briefing, or rejecting a browser draft—remember that preference and quietly apply it next time, while showing me what you learned and letting me forget it."
- **useful because:** The owner should not have to repeat stable judgments. This turns everyday corrections into bounded personalization without granting broad autonomy: the pendant captures the correction in the moment, the relay preserves it, and Mac/browser work uses it only when the situation matches.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → dashboard
- **model tier:** background for extracting and consolidating candidate preferences; realtime only to acknowledge the correction and speak the one-sentence explanation
- **latency:** Immediate acknowledgement under 500 ms; candidate preference write within 2 s; future application adds under 100 ms through a compact local projection
- **cost:** About $0.001–$0.01 per correction depending on whether consolidation needs a model; most reads are a small structured lookup, not an LLM call
- **security:** Preferences may expose routines, health, work, or communication style. Store sensitivity, provenance, confidence, scope, and expiry; never learn secrets or permissions from an action. Do not learn a destructive-action approval from a single correction. Show 'I learned X from Y' in the next spoken response and provide forget/edit controls; sensitive preferences require explicit confirmation.
- **missing:** A durable preference ledger separate from factual memory, with candidate→confirmed lifecycle, scope matching, expiry, provenance, and owner-visible delete/edit UI; A cross-surface event linking the owner's correction to the generated action/draft and its final edited value; A compact per-job preference projection so prompts do not resend the entire memory context

### "Before I say yes to something, let me ask, “What does this commitment cost me?” Have you inspect my calendar, active work, travel, and existing promises, then give me a short consequence forecast with conflicts, hidden preparation, and what I would have to drop—without contacting anyone or changing anything."
- **useful because:** Today the owner can ask for separate calendar, mail, browser, or Mac lookups, but cannot see the second-order cost of a commitment. This would protect their time and attention at the exact moment a decision is being made, turning scattered private facts into an honest tradeoff rather than another task list.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → faculty-perception → faculty-judgement → dashboard
- **model tier:** Background model gathers and normalizes evidence; the realtime model only asks one clarifying question if the commitment is ambiguous and speaks the final compact forecast.
- **latency:** A first forecast in 10–20 seconds, with progressive updates if authenticated pages are slow. The pendant should be able to say that evidence is incomplete rather than fabricate certainty.
- **cost:** Roughly $0.02–$0.10 per forecast, dominated by evidence extraction and synthesis; cached calendar and obligation facts should reduce repeated cost.
- **security:** This combines highly sensitive calendar, mail, travel, and logged-in work data into an inference about the owner's life. Keep raw page contents on the Mac/browser surfaces, send only extracted evidence and citations to the relay, redact unrelated people and secrets, and never infer permission to decline or send messages. It must be advisory only: no calendar edits, cancellations, or replies without a separate explicit request.
- **missing:** A cross-surface commitment-impact graph that relates proposed commitments to time blocks, travel, preparation work, deadlines, and existing promises; A private evidence-matching layer that can search authenticated Mac and browser sources without exporting raw page data; A forecast format with confidence, missing-evidence warnings, and explicit alternatives such as accept, defer, or accept-and-drop; A pendant interaction for naming the proposed commitment and paging through the short spoken tradeoff


## Changes it proposed to its own stack

### `memory` — Add a bounded preference ledger and compiler between action receipts and future jobs. On every owner edit/correction/rejection, record a candidate preference with subject, normalized rule, source event, before/after values, confidence, sensitivity, scope (surface/task/entity), TTL, and status (candidate/confirmed/expired/forgotten). Confirm low-risk repeated patterns automatically only after two independent occurrences; require explicit spoken confirmation for sensitive or autonomy-affecting rules. Emit a compact job-scoped projection and an owner-facing change/forget stream.
- **owner gets:** The pendant becomes easier to live with: changing one recurring behavior once prevents the same annoyance tomorrow, while the owner can see and erase exactly what was learned rather than wondering why the AI behaved differently.
- effort: Medium: event schema and D1/R2 persistence, projection endpoint, receipt/draft diff hooks, and a small dashboard view plus pendant acknowledgement.  ·  risk: A mistaken generalization could make future actions subtly wrong. Mitigate with narrow scopes, confidence thresholds, expiry, provenance shown before use, and never applying learned preferences to irreversible actions without the existing confirmation gate. Recover by disabling the preference or replaying the affected job from its receipt.
- cost: Negligible storage and lookup cost; occasional background consolidation model call (~$0.001–$0.01 per cluster). No additional pendant hardware.  ·  latency: Sub-100 ms structured lookup; asynchronous consolidation. No added latency to ordinary speech beyond a short local acknowledgement.
- security: Preference data can be sensitive and correlatable across surfaces. Encrypt at rest, classify sensitivity, redact secrets, enforce per-surface projection, and make deletion propagate to derived projections and audio briefs.
- depends on: An event linking owner edits/rejections to action receipts and browser before/after diffs; A durable typed context projection service (the existing context-service backlog items); Owner-visible preference review/forget controls

### `model-routing` — Add a counterfactual decision sandbox that forks the owner's current state without mutating calendars, tasks, browser sessions, or memory. It should accept a proposed commitment, resolve evidence locally on Mac/browser, calculate time and dependency deltas, and return cited tradeoff branches (accept, defer, accept-and-remove something else). Discard the fork after the response unless the owner explicitly saves it.
- **owner gets:** The owner gets a safe answer to “what happens if I agree?” rather than an irreversible action or a vague summary. They can explore consequences without polluting their real schedule or teaching the system a hypothetical as if it were true.
- effort: High: define a typed state snapshot and delta model, add local evidence extraction, implement branch computation and citation retention, and expose a compact spoken comparison plus dashboard detail.  ·  risk: The model may miss an obligation or overstate impact. Every output must label observed versus inferred facts, show freshness and missing sources, and refuse a confident forecast when evidence is insufficient. No branch may write to external systems; discard or undo the fork on timeout.
- cost: Moderate background-model cost per forecast, approximately $0.02–$0.08; storage is temporary and small. Reuse cached structured evidence where possible.  ·  latency: Adds several seconds for private-source collection; stream a provisional result from available evidence and revise it when slower browser evidence arrives.
- security: Raw private pages remain on their originating Mac/browser surface. Only minimal extracted facts and hashes cross the relay. Temporary forks receive automatic expiry and deletion; hypothetical data must never enter durable memory or notifications.
- depends on: A typed cross-surface state snapshot with provenance and freshness; Local Mac/browser extraction that can return structured facts rather than raw pages; A strict no-side-effects transaction boundary around planning and execution; Spoken and dashboard rendering for observed facts, inferences, and missing evidence


## What it asked for

_Nothing._
