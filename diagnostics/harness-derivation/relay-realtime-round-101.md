# Harness derivation — relay-realtime — round 101

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “handle this for me and tell me when it’s done,” route it to the right place, keep tabs on it, and notify me on the pendant when it finishes or needs my input."
- **useful because:** This turns the pendant into a reliable assistant, not just a voice remote. The owner can speak once, walk away, and still get closure without babysitting a Mac or browser session.
- **path:** relay → mac-bridge → browser → pendant
- **model tier:** Realtime at the relay for intent capture; cheaper planner/judgement model on the Mac for multi-step work; lightweight status polling in a background worker if available.
- **latency:** Under a second to acknowledge. Completion notification can arrive later; it should not block the conversation.
- **cost:** Low per utterance at the relay. Most cost is in downstream planning/execution and periodic status checks, which should be batched and rate-limited.
- **security:** Must avoid leaking task details across sessions. Notifications should reveal only what’s necessary. High-impact actions should remain observable and reversible where possible, but not gated.
- **missing:** relay_route_intent implementation; relay_job_status implementation for queued jobs and references; a durable job runner and status store (or equivalent) to track long-running work; a notification path from relay to pendant for completion/needs-attention events

### "While I’m away from my Mac, let me start a multi-step task by voice, have the Mac/browser work until it reaches a genuine ambiguity, then ask me exactly one concise clarification on the pendant and resume the same task when I answer (or let me cancel with the button)."
- **useful because:** Today delegation either completes without interaction or leaves an opaque job. This would make unattended work safe and practical: the owner can resolve an ambiguity from anywhere without reopening the Mac, while preserving the original browser session, action history, and context rather than starting over.
- **path:** relay-realtime → pendant → mac-planner → mac-vision → browser-extension → relay
- **model tier:** Use relay-realtime only to classify the spoken reply and phrase the short question; use mac-planner for planning and mac-vision/browser-extension for execution. No model should poll or remain in a realtime turn while waiting.
- **latency:** Immediate acknowledgement under 1 second; clarification delivery on the next available checkpoint; resume within a few seconds of the owner's spoken answer or button cancellation.
- **cost:** One short realtime turn for the question and one for the answer, plus the existing planner/vision calls; the dominant cost is the resumed planner context, which should be a compact checkpoint rather than the full transcript.
- **security:** The question must contain only the minimum non-secret ambiguity (never read passwords or tokens aloud). Persist a redacted checkpoint and bind replies/cancel to the owner, job, and expiry; do not execute after a stale answer. Browser and Mac mutations remain recorded in existing receipts.
- **missing:** A durable job checkpoint/state machine with WAITING_FOR_OWNER, RESUMING, CANCELLED, and EXPIRED states; A relay-to-pendant notification and answer channel for pending questions, including a button-to-cancel event; A typed clarification record carrying options, redacted evidence, jobId, and checkpoint version; Resume logic that rehydrates only the checkpoint and preserves Mac/browser session affinity; A timeout/recovery policy for unanswered questions and a receipt showing the question, answer, and resumed actions

### "If I ask you to do something and my Mac is asleep or unreachable, try the safe browser-side path instead; if both paths recover, reconcile them so the action happens once and tell me which path succeeded."
- **useful because:** The pendant is worn away from the Mac, so today reachability silently determines whether an otherwise valid request works. A durable, idempotent failover would make the system dependable in travel, sleep, and intermittent LTE conditions without asking the owner to repeat a request or risking duplicate sends.
- **path:** relay-realtime → relay → mac-planner → browser-extension → browser → pendant
- **model tier:** Use a cheap deterministic router and idempotency ledger; use relay-realtime only for the spoken acknowledgement/result. Use mac-planner or browser automation only after capability selection, not for deciding failover.
- **latency:** Acknowledge immediately; probe path health in under 2 seconds, then run the selected path. If recovery/reconciliation is needed, report asynchronously rather than holding the voice turn.
- **cost:** Negligible routing/storage cost; normal downstream Mac or browser automation cost. Reconciliation may add one verification call, which is cheaper than duplicate side effects.
- **security:** Only actions explicitly classified as idempotent or safely verifiable may fail over automatically. Bind a stable owner/job/action id across both paths, redact payloads in the ledger, expire entries, and never replay irreversible mutations merely because a receipt was lost.
- **missing:** A shared capability/health registry for Mac, browser relay, and pendant links; An exactly-once action envelope with idempotency key, intent hash, target surface, and lease; A prepare/commit or verify protocol for Mac and browser actions, including an UNKNOWN outcome; A reconciliation worker that resolves UNKNOWN without replaying unsafe mutations; A spoken result that distinguishes completed, failed, and unknown states

### "When I say “that wasn’t what I meant” after you act, let me describe the correction in plain language and have the hive repair the result from the action receipt instead of starting the whole task over."
- **useful because:** A wearable conversation is prone to short, underspecified commands. Today the owner must manually inspect what happened and explain the entire task again. Receipt-grounded repair would turn mistakes into a quick spoken correction, preserve useful completed work, and avoid duplicate browser/Mac side effects.
- **path:** pendant → relay-realtime → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Use a deterministic receipt lookup and action-diff first; use mac-planner for a compensating plan, and mac-vision/browser-extension only for the affected UI. Relay-realtime handles the brief correction dialogue and result.
- **latency:** Identify the referenced recent action in under 1 second; speak a repair summary quickly, then run the compensating actions asynchronously if they exceed a short voice turn.
- **cost:** One planner call over a compact receipt/diff, plus only the necessary downstream actions. This should cost materially less than replanning from the full conversation and state.
- **security:** The repair plan must be explicitly tied to a recent receipt and immutable action IDs. Keep the original and compensating receipts, detect already-undone actions, and clearly report when an effect cannot be reversed; do not infer destructive repairs from vague speech.
- **missing:** Natural-language reference resolution from spoken phrases such as “that” to a recent job/action receipt; A typed before/after state snapshot and compensating-action metadata for Mac and browser operations; A repair planner that consumes receipt diffs and emits a minimal patch plan; Cross-surface verification that the repaired state matches the owner's correction; A concise pendant dialogue for ambiguity and an audit trail linking original and repair


## Changes it proposed to its own stack

### `relay` — Publish a relay /capabilities inventory endpoint (or equivalent describe/discover responses) so this agent can see its own routes and delivery endpoints, including pendant notification endpoints, without guesswork.
- **owner gets:** Fewer blind spots means fewer failed actions and fewer repeated proposals. The assistant can reliably say what it can do right now, and route requests without probing random paths.
- effort: Medium. Mirror what the Mac does for /capabilities and wire it into the relay router build.  ·  risk: Low. The main risk is exposing too much detail; mitigate by returning only what the relay agent needs (names, parameters, auth requirements) and leaving secrets out.
- cost: Minimal runtime cost; small additional response payloads.  ·  latency: Negligible; one cheap read endpoint.
- security: Positive if scoped correctly; improves auditability and reduces accidental misuse.
- depends on: relay router metadata generation

### `relay` — Add a self-describing, authenticated relay manifest and live readiness feed: enumerate the relay's real routes, pendant ingress/egress, model versions, queue state, and downstream reachability with timestamps and machine-readable degradation reasons. Make the manifest consumable by the Mac planner and faculty agents before they choose a route, and expose a compact spoken-safe subset to relay-realtime.
- **owner gets:** The owner should not hear confident promises based on stale or invisible wiring. The hive would know whether a request can actually be delivered now, explain a failure honestly, and choose a reachable surface without the pendant conversation guessing.
- effort: Medium: generate the manifest from the live Worker router, add signed/versioned health snapshots and a small cross-agent cache, then add planner routing hooks and tests for stale data.  ·  risk: A stale or over-broad manifest could cause bad routing or leak internal topology. Use short TTLs, capability-level descriptions rather than secrets, fail closed to “unknown,” and keep the current direct routes as fallback.
- cost: Small Worker storage/CPU and one lightweight health read per routing decision; no additional model call when cached. No hardware cost.  ·  latency: A cached lookup adds near-zero latency; refreshes can happen asynchronously and must not block the voice response.
- security: Improves security observability but creates a topology surface; authenticate agents, omit credentials/session identifiers, sign snapshots, and log manifest access.
- depends on: A relay route that can publish its own live router inventory; A shared schema for capability readiness and freshness; Planner/router support for unknown and degraded capabilities


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing gaps: durable cross-surface failover with exactly-once reconciliation, receipt-grounded natural-language repair, and a signed self-describing relay readiness manifest. These require new connective state/protocols rather than assuming existing routes are sufficient.

**Biggest unknown:** The backlog may contain near-duplicates of the first two despite their distinct implementation boundaries; the relay manifest is the clearest independently established gap because this surface currently cannot inventory its own live router.

