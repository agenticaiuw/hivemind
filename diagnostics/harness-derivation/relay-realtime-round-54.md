# Harness derivation — relay-realtime — round 54

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "What happened to that thing I asked you to do? If it failed, try a safe fallback and tell me what you’re doing."
- **useful because:** When the owner is away from the Mac, they shouldn’t have to guess whether a request ran, stalled, or failed. This gives a quick spoken answer, then a recovery path without making them babysit the system.
- **path:** pendant → relay → mac-bridge → mac-harness
- **model tier:** Realtime only for the spoken status. A cheaper planner model on the Mac should handle fallback planning and execution.
- **latency:** Fast status: under a second when the relay already has job state. If a fallback is needed, the relay hands off and the Mac may take several seconds; the owner hears a short acknowledgment.
- **cost:** Low for status reads (relay_job_status). Higher when invoking mac_delegate because planning dominates; execution cost depends on the actions.
- **security:** Status reveals task names and outcomes; keep spoken output verbatim from relay_job_status. Fallback execution must remain reversible by default and avoid high-impact changes without explicit intent.
- **missing:** A reliable, describable routing tool to send intent labels from relay to Mac without inventing protocol details; A shared vocabulary for task categories and fallback strategies (status-only, retry, alternative app)

### "“Handle this while I’m away. If anything is ambiguous, investigate across my Mac and already-signed-in browser, ask me at most one focused question through the pendant, then finish and tell me exactly what you decided and why.”"
- **useful because:** Today the pendant must either guess from a short utterance or hand off a goal without a durable, cross-surface clarification loop. This would let the owner delegate real work while walking, preserve their browser sessions, avoid interfering with active Mac work, and spend their attention only on the single uncertainty that truly blocks completion.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** Realtime handles only the initial utterance and any one-question exchange; a cheaper background planner/perception model investigates and drafts alternatives, while faculty-judgement selects the minimum necessary clarification and faculty-action executes the selected reversible plan.
- **latency:** Immediate acknowledgment in under 2 seconds; investigation may run asynchronously for minutes. The owner can continue walking and receive a brief spoken question or completion receipt whenever the durable job reaches that state.
- **cost:** One short realtime turn for intake and, only if needed, one for the clarification; background model calls dominate and should be batched over Mac/browser observations. Small durable-state and dashboard costs are negligible compared with repeated full-context realtime calls.
- **security:** Mac and authenticated browser content leave their devices to the relay/model only as scoped evidence; redact secrets and unrelated tabs. The job must bind the answer to the exact pending question, expire stale observations, and expose an audit trail. Reversible actions can follow owner policy without confirmation; destructive or external communication should be surfaced as a proposed action rather than silently inferred.
- **missing:** A durable cross-surface job state machine with explicit blocked_on_owner_question and resumed states; A pendant notification/answer protocol that can deliver one short question and correlate a button/voice response; A unified evidence bundle with freshness, source, and redaction metadata across Mac and browser; An ambiguity evaluator that is constrained to one highest-value question and can safely abandon stale jobs; Cross-surface completion receipts that explain the decision, not merely list low-level actions; Presence/interference checks so Mac work pauses when it would disrupt active owner work

### "“I got interrupted. From the work I had open before the interruption, tell me what I was doing and resume the next safe step—without losing or overwriting anything.”"
- **useful because:** A worn assistant should preserve continuity when the owner is away from the Mac, not merely execute isolated commands. The Mac can see applications and files, the browser can see authenticated task context, and the relay can reach the owner, but today those observations are not joined into an interruption checkpoint with a resumable next step.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → mac-terminal → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a cheap background model to summarize recent app/browser/action traces into a checkpoint; use realtime only to answer the owner’s spoken request and narrate the short result. Use a stronger judgement pass only when several work threads are plausible.
- **latency:** A spoken orientation in 2–4 seconds from the latest checkpoint; reconstruction of stale or multiple threads can take up to a minute. Resume actions should report progress asynchronously rather than hold the voice turn open.
- **cost:** Low recurring cost if checkpoints are incremental and compact; occasional summarization dominates. Realtime context stays to the owner’s request plus a checkpoint id instead of retransmitting full histories.
- **security:** Checkpoint data may contain private document names, messages, and URLs; encrypt it, scope retention, and omit secrets and page contents unless needed. Never infer that an unfinished send/payment/delete is safe to resume; classify those as pending and leave them untouched. Provide an exact source-linked explanation and an undoable action receipt.
- **missing:** A local Mac/browser checkpoint collector that records active work threads and recent reversible actions rather than just current window state; A durable interruption marker and compact encrypted checkpoint store on the relay; Cross-surface thread identity linking a Mac project, browser tabs, terminal commands, and pendant conversation; A resume planner that selects only the next reversible step and detects stale/conflicting state; A user-facing “pause/checkpoint/resume” lifecycle and spoken checkpoint identifiers


## Changes it proposed to its own stack

### `model-routing` — Add a canonical, versioned intent schema and registry shared between relay and mac-planner (and browser harness). The relay emits intent labels and minimal context; downstream agents map them to planners/actions. Include a “status-only” class and a “fallback allowed” flag.
- **owner gets:** Their voice request gets routed predictably and explainably. When something fails, the system can try alternatives without misinterpreting the request.
- effort: Medium: schema design, registry, backward compatibility, and instrumentation; moderate refactor to adopt it.  ·  risk: Misrouting if the mapping is wrong. Mitigation: versioned intents, audit logs, and safe default to status-only when confidence is low.
- cost: Low per call; the cost is mainly development and some extra logging.  ·  latency: Slight overhead for validation, negligible compared to planning/execution.
- security: Reduced risk of arbitrary free-form routing; clearer boundaries between read-only, reversible, and high-impact intents.


## What it asked for

_Nothing._
## Its own summary

Discovered current shipped tools and newly granted items. relay_job_status is live and well-specified. Two named tools in the granted list (relay_route_intent, server_browser_actions) appear as granted but are not discoverable/describable in the tool registry this round. Proposed a new owner-facing capability: status check with safe fallback, and a routing change: a canonical intent schema to avoid protocol drift and enable reliable recovery.

**Biggest unknown:** Why relay_route_intent and server_browser_actions are marked granted but not actually available for describe/use through the tool registry; what is the correct way to route intents from relay to mac-planner without inventing protocol details.

