# Harness derivation — relay-realtime — round 251

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Handle this while I’m away: take the item I’m looking at in Safari, send it to the right person, and tell me exactly what happened.” The pendant should resolve “this” to the currently selected page or text, identify the recipient from my scoped contacts/context, perform the send on the authenticated browser or Mac, and speak a concise receipt; if the recipient or artifact is ambiguous, ask one focused question instead of guessing."
- **useful because:** Today the wearable, browser session, and Mac each know different halves of the task. This makes a natural reference like “this” actionable from the pendant even when the owner is not at the screen, while preserving truthful reporting about what was actually sent.
- **path:** pendant → relay → browser → mac-planner → mac-vision → dashboard
- **model tier:** Realtime relay for reference resolution and one clarification; mac-planner for orchestration; mac-vision only when DOM/extension metadata is insufficient; cheap background verifier for the post-send receipt.
- **latency:** Acknowledge in under 1 s; resolve and execute in 5–20 s; speak only after a concrete receipt or a clarification is available.
- **cost:** Roughly $0.01–$0.08 per invocation; cost is dominated by planner/vision turns, not the short realtime exchange.
- **security:** The browser must return a narrow artifact handle (URL, title, selected text, origin, timestamp), not an unrestricted page dump. Sending mail/messages is externally visible, so the owner’s existing destructive-action policy must still govern it; never claim success from a click without a delivery receipt. Sensitive selected text must stay scoped to the voice/mac/browser surfaces and expire quickly.
- **missing:** A browser-extension event that publishes the active selection/page artifact with a short-lived capability token; A relay-side reference resolver joining that token to the utterance and session memory; A receipt schema that distinguishes submitted, delivered, and failed sends; A Mac/browser handoff that can execute against the captured artifact after the owner leaves the screen

### "“I’m leaving now—make me a handoff.” The system should inspect the Mac’s active work and authenticated browser tabs, identify unsaved drafts, half-completed jobs, and decisions waiting on me, save a resumable handoff with links and provenance, and tell me only the top blockers over the pendant. When I return, “resume my handoff” should reopen the relevant apps/pages and continue from the saved checkpoint."
- **useful because:** A wearable is most valuable at the moment the owner walks away: it can prevent lost context without requiring an end-of-day ritual. The result is a durable, truthful transition between physical presence at the Mac and being away from it.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime relay handles the short command and summary; a cheaper background planner inventories and ranks unfinished work; mac-vision is used only for visual unsaved-state evidence.
- **latency:** Speak an acknowledgement immediately; produce the handoff in 10–30 s, with a short spoken summary and a dashboard detail view.
- **cost:** About $0.02–$0.12 per handoff, dominated by Mac/browser inspection and optional vision; resuming a handoff costs only the planner/action turns required.
- **security:** Draft contents and private tabs must remain on the owner’s surfaces unless explicitly included. Every item needs source, timestamp, confidence, and a reason it was classified unfinished; never infer that a destructive dialog or unsaved document is safe to close. Handoff records should expire or be deleted on request.
- **missing:** A Mac/browser snapshot contract for active documents, dirty state, current selection, and pending dialogs; A resumable handoff record with item-level provenance and confidence, rather than a free-form summary; An owner-away trigger and a return/resume trigger exposed to the pendant; A safe reopen/resume action that restores context without silently submitting or closing anything

### "“Do this, but don’t collide with anything already running.” Before acting, the pendant should know about active Mac, browser, and relay jobs; detect when two requests touch the same file, tab, account, or external object; serialize or merge compatible work; and tell me in one sentence whether it started, joined, or deferred the request. If a conflict appears mid-run, pause at the smallest safe boundary and report the competing job and evidence."
- **useful because:** Today separate requests can race because the owner may issue them from the pendant while an earlier Mac or browser job is still running. Conflict-aware execution prevents overwritten drafts, duplicate submissions, and contradictory calendar or file changes without forcing the owner to remember every outstanding task.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension → dashboard
- **model tier:** Realtime relay performs fast intent classification and speaks the disposition; a cheaper planner builds resource claims and compatibility checks; execution remains on the existing Mac/browser agents.
- **latency:** Disposition in under 2 s; conflict analysis in under 5 s; no extra spoken turn when requests are clearly independent.
- **cost:** Approximately $0.01–$0.06 per request, mostly planner analysis; substantially cheaper than recovering from a duplicate external action.
- **security:** Claims must be advisory and observable, not an excuse to hide work or impose a new confirmation gate. Resource identifiers should be hashed or minimally scoped in logs. External mutations need idempotency keys and receipts so a retry cannot send twice. The owner’s maximum-access policy remains intact.
- **missing:** A shared live resource-claim registry for jobs and sessions; Action metadata declaring read/write resources and idempotency keys; A scheduler/arbiter that can queue, merge, or pause jobs at safe boundaries; Cross-surface cancellation and conflict events delivered to the pendant; A receipt view that explains the competing evidence in owner language


## What it asked for

_Nothing._
