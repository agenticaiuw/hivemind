# Harness derivation — relay-realtime — round 53

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I say “do this later” or “queue that for my Mac,” capture it, plan it, and tell me when it’s done—even if my Mac is asleep right now."
- **useful because:** The owner can speak in the moment and trust the system to carry the task to completion without babysitting, which is exactly what a worn assistant should make feel effortless.
- **path:** pendant → relay → mac-bridge → mac-planner → faculty-action
- **model tier:** Realtime relay for fast capture and confirmation; cheaper planner/action models for planning and execution once the Mac is reachable.
- **latency:** Capture/ack under a second; execution can be minutes later depending on Mac availability; status updates should be instant once job state changes are known.
- **cost:** Low per utterance at relay; dominant cost is planning/execution runs on Mac plus storage/queue operations for persistence.
- **security:** Tasks may include sensitive content. Persist only what’s needed to execute; encrypt at rest; avoid leaking details in spoken summaries; never claim completion without verified status.
- **missing:** A durable job runner/queue that persists tasks across relay restarts; A retry/availability strategy to hand work to the Mac when it comes online; A unified status stream so relay can report progress without polling every turn

### "When I start something on my pendant and it needs my Mac or a signed-in browser, keep the task alive across the handoff: tell me exactly what is waiting, notice when the Mac/browser becomes available again, and continue from the last verified step without making me repeat myself. If a step fails, explain the specific recovery choice over the pendant and let one button press choose it."
- **useful because:** Today a spoken request is effectively tied to the moment and surface that received it. The owner is usually away from the Mac, so work that encounters an offline Mac, expired browser tab, or transient failure either stops silently or forces a complete restart. This would make the wearable a dependable front door for work spanning the pendant, always-on relay, Mac executor, and authenticated browser.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime relay handles only the short spoken status, failure explanation, and button-choice dialogue. A cheaper background model in the relay summarizes verified state and ranks recovery options; mac-planner plans resumed Mac work; browser-extension executes only against the original tab/session; mac-vision is used when visual state must be re-established.
- **latency:** Immediate acknowledgement in under 1 second. Availability/presence changes and retries may take seconds in the background. Recovery dialogue should speak within 2 seconds of a detected failure; no repeated full plan unless verification shows state was lost.
- **cost:** Roughly one realtime turn for the initial acknowledgement and one for each failure/recovery dialogue; background state summaries are inexpensive and dominate only for long-running tasks. Mac/browser execution and telemetry are the larger non-model costs, not repeated voice context.
- **security:** Persist only a task id, minimal action state, and opaque browser/session references; never copy page secrets into relay prompts or speech. Resume must require verified session/tab identity and an idempotency key so reconnects cannot duplicate mutations. The owner has chosen maximum access and no confirmation gates, but destructive or externally visible actions still need explicit status and an undoable receipt. A lost pendant link must pause rather than guess.
- **missing:** A durable cross-surface task state machine with verified checkpoints and idempotency keys; Worker Cron/Durable Object alarms or an equivalent always-on retry/presence watcher; Mac presence and browser-extension availability events, not just point-in-time status; A relay-to-pendant status/choice protocol supporting spoken failure options plus one-button selection; Resume endpoints in mac-planner and browser-extension that accept a checkpoint and return typed verification; A compact owner-visible task timeline in the dashboard with pause, abandon, and inspect controls

### "If my Mac and browser disagree about whether a task happened, ask me one short, evidence-backed question on the pendant instead of guessing: say what each surface verified, offer the two likely interpretations, and after I choose reconcile the records and continue or undo the right branch."
- **useful because:** Cross-surface automation can otherwise duplicate purchases, messages, edits, or submissions when one node completed an action but another missed its receipt. The owner cannot inspect both surfaces while wearing the pendant. A focused discrepancy dialogue turns an invisible distributed-systems failure into a quick decision, preserving continuity without requiring the owner to restart or manually compare screens.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Faculty-perception/mac-vision and the browser extension provide typed, timestamped observations; a background model correlates them and generates the smallest set of competing explanations. Realtime is used only to state the discrepancy and capture the owner's choice. Faculty-judgement selects reconciliation/undo semantics, and faculty-action executes the chosen branch.
- **latency:** Detect discrepancies asynchronously within a few seconds of conflicting receipts. Speak one concise question in under 2 seconds after detection. Correlation can take longer for large histories, but must not block unrelated voice conversation.
- **cost:** Low background-model cost per conflict, with realtime cost only when owner intervention is actually needed. Storage and event correlation dominate; no continuous vision or full-page prompt should be sent to the realtime tier.
- **security:** Evidence must be redacted before speech and prompts: disclose titles, domains, and action types, not credentials, message bodies, or tokens. Every observation needs source, timestamp, and confidence; never reconcile based on stale presence alone. Undo must be scoped to the exact action receipt, and the unresolved state must remain visible in the dashboard until closed.
- **missing:** A shared append-only observation ledger joining Mac, browser, relay, and pendant event ids; Typed semantic receipts that distinguish attempted, verified, and merely inferred outcomes; A conflict detector that handles delayed and duplicate events with causal ordering; A small pendant response grammar for choosing among two or three interpretations; Reconciliation/undo APIs that operate on an exact receipt rather than a latest-action heuristic; Dashboard UI for unresolved cross-surface discrepancies and their evidence


## Changes it proposed to its own stack

### `integration` — Add a durable job runner with retry and backoff, plus a persistent queue that the relay writes to and the Mac agent drains when online. Include job receipts and a status API that the relay can read cheaply to inform the owner.
- **owner gets:** They can ask for something once and get reliable follow-through, even when the Mac is asleep or connectivity is flaky.
- effort: High: requires new storage, worker logic, retry semantics, and coordination with Mac agent.  ·  risk: Duplicates or partial execution if idempotency isn’t handled; recover with action receipts, idempotent action keys, and an undo path for reversible operations.
- cost: Moderate. Storage and worker time add ongoing cost; planning/execution remains the dominant compute cost.  ·  latency: Small added latency at capture time; big reliability improvement overall.
- security: Queue contents are sensitive. Encrypt at rest, restrict access, and minimize logged content.
- depends on: Clarify job identity and idempotency keys across relay and Mac actions; A status API/stream that can be read without waking the Mac unnecessarily


## What it asked for

_Nothing._
## Its own summary

Discovered the current toolset and grants, confirmed relay_job_status is available and suitable for reporting previously queued work. Proposed a genuinely new cross-device capability: reliable deferred execution from a spoken request, and a concrete integration change: a durable job runner/queue with retries and a cheap status path for the relay.

**Biggest unknown:** There is still no confirmed durable scheduler/queue implementation or unified status stream; without those, “do it later” cannot be trusted. Also, the new tools relay_route_intent and server_browser_actions appear listed as granted but were not describable here, so their exact runtime availability/protocol remains unclear.

