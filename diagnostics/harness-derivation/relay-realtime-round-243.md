# Harness derivation — relay-realtime — round 243

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Test the pendant connection and audio path right now.”"
- **useful because:** When something sounds off, the owner needs a one-shot diagnostic they can run without opening a laptop. It’s immediate confidence, not a spreadsheet.
- **path:** pendant → bridge → relay → mac-bridge
- **model tier:** Realtime to guide the user; the actual test routine should run on-device and/or on the Mac without LLM involvement.
- **latency:** Fast: a few seconds for loopback checks; longer if a recording needs analysis.
- **cost:** Low. Mostly device and bridge operations; minimal model tokens.
- **security:** Diagnostics should not capture or store user speech beyond what’s needed for the test; no routine SD writes.
- **missing:** A callable diagnostic endpoint for the bridge/pendant path (today it’s only indirectly testable).; A standard report format that can be spoken and also logged for later analysis.

### "When I ask “where was I?”, tell me exactly what I was doing on my Mac and in my browser, what is unfinished, and give me a one-sentence way back into it through the pendant."
- **useful because:** A worn assistant should restore the owner’s working context without requiring them to remember which app, tab, or job held it. This is a cross-node reconstruction, not merely a history list: live Mac state, authenticated browser state, outstanding jobs, and durable task memory are reconciled into a spoken answer.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use the realtime model only to clarify the spoken request and speak the compact result; use faculty-perception or a background planner to rank and reconcile state, because the owner is waiting for a short answer rather than a long computer-use loop.
- **latency:** Under 4 seconds for the first spoken sentence; continue collecting state in the background for up to 15 seconds and replace the answer only if confidence materially improves.
- **cost:** Roughly one realtime turn plus one cheap synthesis turn; the dominant cost is browser and Mac state collection, not tokens.
- **security:** Browser titles, document names, and window contents can be sensitive. Send only extracted task candidates to the relay, redact page text by default, and require an explicit “show me the details” follow-up before reading private content aloud.
- **missing:** A single state snapshot API that joins live Mac windows, browser tabs, active jobs, and task memory with timestamps; A reconciliation/ranking worker that marks evidence as current, stale, or conflicting; A spoken disambiguation response when two work contexts are equally plausible

### "Let me say “hold this thought” while away from my Mac, then later say “continue that” and have the system reopen the exact working context, quote the last saved thought, and ask only the one missing question before acting."
- **useful because:** This turns a fleeting wearable utterance into a resumable handoff rather than a dead-end memo. The owner can leave a meeting or walk away from the desk and return to a precise, bounded continuation with the relevant browser page, Mac app, and pending intent restored.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime handles capture confirmation and the later one-question clarification. A background planner extracts a compact continuation record and resolves it against Mac/browser state when the owner returns.
- **latency:** Acknowledge capture in under 1 second; on resume, speak the proposed context in under 3 seconds, then wait for confirmation before any mutation.
- **cost:** One short realtime exchange at capture and one at resume; background extraction is a low-cost model. State snapshots and browser inspection dominate operational cost.
- **security:** Continuation records may contain secrets or sensitive page titles. Store a minimal encrypted record with expiry, never store raw audio after transcription, and require confirmation for reopening or acting on a different account/session than the original.
- **missing:** A first-class continuation record with source anchors, expiry, and confidence; Mac and browser commands to restore a recorded app/window/tab context without replaying destructive actions; A conflict resolver for stale or changed pages

### "Tell me “what can I safely do right now?” and have the pendant answer using my current Mac activity, browser session, audio state, and pending jobs—then offer one useful action that will not interrupt work already in progress."
- **useful because:** The owner should not have to know whether an action belongs to the Mac, browser, relay, or a queued job. This creates a truthful availability view for a worn device: it distinguishes idle, busy, disconnected, stale, and safe-to-interrupt, and converts that into one actionable suggestion.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Faculty-perception gathers and classifies state; a cheap planner selects a reversible suggestion; realtime only asks a clarification or speaks the result. The computer-use loop is not needed unless the owner accepts the suggestion.
- **latency:** First answer in 2–3 seconds from cached state; refresh uncertain sources within 8 seconds and say explicitly when a source is stale.
- **cost:** Low per invocation if state snapshots are cached; occasional Mac/browser probes and one small synthesis call are the main costs.
- **security:** The answer itself may reveal private work titles or browser sessions. Speak app-level categories by default, keep content redacted, and make detailed disclosure a separate request. Do not infer that disconnected means safe.
- **missing:** A shared freshness-aware availability schema across relay, Mac, browser, and jobs; A non-interference classifier that understands active calls, presentations, audio playback, and unsaved work; A cache with explicit stale/error states rather than silently treating missing data as idle

### "Keep private answers private: when I ask the pendant for sensitive information, decide whether it is safe to speak aloud from my current context; if not, send the answer to the least intrusive available surface and tell me only that it is ready."
- **useful because:** A wearable is inherently public. Without output-aware privacy, the assistant can disclose passwords, finances, health, or private messages to everyone nearby. This lets the owner use voice anywhere while preserving the convenience of a spoken answer for harmless information.
- **path:** pendant → relay → mac-planner → browser-extension → iOS → dashboard
- **model tier:** A low-cost policy model classifies sensitivity and chooses a delivery surface; realtime handles the request and speaks only a safe acknowledgement. The actual answer is rendered on the selected trusted surface.
- **latency:** Acknowledge within 2 seconds. Sensitive delivery may take up to 10 seconds if it must wait for a paired private surface; never stall the spoken interaction while probing every surface.
- **cost:** One small classification call plus whichever Mac/browser retrieval is needed; delivery rendering is cheap. Cost is dominated by source retrieval, not the privacy decision.
- **security:** This is security-critical: default to withholding rather than guessing, bind trusted surfaces to the owner, expire undelivered answers, avoid logging plaintext, and distinguish 'could not verify privacy' from 'safe.' The pendant must never read a secret merely because the owner asked while in public.
- **missing:** An output-sensitivity classifier with a closed set of delivery policies; Presence/proximity and acoustic privacy signals from the pendant and paired devices; Encrypted, single-use delivery envelopes for Mac, browser, phone, and dashboard; A confirmation-free but auditable policy for harmless versus sensitive speech

### "Give me a “one safe next move” whenever I am stuck: infer the smallest reversible action that advances the task from my current Mac/browser state, explain why it is next, and do it only after I say “go.”"
- **useful because:** The system becomes useful in moments of uncertainty rather than only when the owner already knows the command. It combines perception of the actual work state with judgement and a bounded action, while preserving the owner’s control over the decision.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Faculty-perception reads the current state, faculty-judgement proposes one reversible next move, and realtime presents it in one sentence. mac-planner or browser executes only after the owner’s explicit “go”; no expensive realtime reasoning is spent on execution.
- **latency:** Propose within 5 seconds; execution receipt within 8 seconds for a short action. If state is stale or conflicting, say so instead of fabricating a move.
- **cost:** One perception pass and one cheap planning pass per request, with Mac/browser inspection as the dominant variable cost; realtime output is short.
- **security:** The proposal must include the exact target and predicted effect, never silently mutate state, and attach a before/after receipt. Avoid proposing actions on unsaved or high-impact work without surfacing that fact.
- **missing:** A state-to-next-action evaluator that scores reversibility and expected progress; A compact spoken proposal schema with target, effect, and confidence; A precondition check and postcondition receipt spanning Mac and browser


## Changes it proposed to its own stack

### `integration` — Implement a job completion pipeline: when a Mac job reaches a terminal state, emit a relay event, queue a short alert (text/metadata) for delivery, and render audio only at delivery time — never store routine audio on SD.
- **owner gets:** They can start a task and walk away, then get a clear, timely update on the pendant without babysitting the job.
- effort: High. Needs relay event emission, a delivery queue, and integration with the existing alert inbox shape.  ·  risk: Duplicate or missing notifications if state transitions are mishandled. Use idempotent job receipts and retries.
- cost: Moderate build cost; low per-job runtime cost if event-driven.  ·  latency: Near real-time when event-driven; acceptable delay if fallback polling is used.
- security: Short messages reduce leakage; confirmation required for sensitive results.
- depends on: A reliable job state source (GET /jobs/:jobId) and a working event/watch implementation.

### `context` — Build a cross-surface evidence graph that records facts about the same task from pendant utterances, Mac observations, browser observations, and action receipts as timestamped claims with provenance, freshness, and contradictions; expose a task-scoped view to the realtime relay and downstream agents instead of passing unrelated raw context.
- **owner gets:** The owner gets answers grounded in what actually happened, even when the Mac, browser, and pendant disagree or one went offline. It prevents the assistant from confidently acting on yesterday’s tab, an old transcript, or a job that silently failed.
- effort: High: define claim identity and provenance, add adapters for each surface, implement freshness/conflict resolution, and integrate the task view into conversation context and action planning.  ·  risk: Bad entity matching could merge two projects or hide a real conflict. Keep original claims and provenance, expose uncertainty, and fall back to asking the owner rather than resolving high-impact conflicts automatically.
- cost: Moderate storage and a small background reconciliation model; lower realtime prompt cost once only task-relevant claims are injected.  ·  latency: Cached task views can be sub-second; a cold reconciliation adds 2–6 seconds and should produce an immediate stale/collecting acknowledgement.
- security: Provenance and sensitive fields need encryption and surface scoping. Do not replicate browser content to the relay unless the task explicitly requires it.
- depends on: Wire GET /memory/projection into conversationContext.js; Add adapters over GET /machine-context, GET /browser/inspect, GET /jobs/:jobId/receipts, and POST /execute receipts; Define surface-scoped redaction and claim retention rules


## What it asked for

_Nothing._
## Its own summary

Recorded six owner-facing capabilities and one stack change. The strongest missing experiences are (1) a privacy-aware answer that automatically chooses whether to speak or privately deliver sensitive information, (2) a single reversible next move proposed from live Mac/browser state, and (3) a cross-surface evidence graph that reconciles pendant, Mac, browser, memory, and receipts instead of trusting stale isolated context. I also recorded resumable work-context and current-availability experiences, while the recorder flagged those as close to existing handoff ideas; they should not be treated as distinct backlog items without a sharper boundary.

**Biggest unknown:** Whether the relay already has an unobserved private-delivery or presence signal and whether /state/:stateKey can provide enough surface-trust metadata. Those determine whether privacy-aware output is genuinely new wiring or requires new phone/presence capabilities.

