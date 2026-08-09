# Harness derivation — relay-realtime — round 272

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "What’s going on with my Mac right now?"
- **useful because:** Quick status checks are a perfect pendant use: battery, wifi, and frontmost app help the owner decide whether to continue a task without touching the Mac.
- **path:** relay → mac-bridge
- **model tier:** Realtime, because the owner is waiting for an answer.
- **latency:** Under a second for cached/fast paths; otherwise as fast as the Mac can respond.
- **cost:** Very low; one status call per request.
- **security:** Status is personal. Don’t over-collect; fetch only the fields asked for.
- **missing:** 

### "Find the best way to do this, even if it means using my browser or multiple apps."
- **useful because:** This uses the hive mind: the relay captures the intent, the Mac planner executes, and the browser/OS surfaces do the fiddly work. It’s useful when the owner can’t predict the steps.
- **path:** relay → mac-bridge → browser → ios
- **model tier:** Realtime to capture intent, then mac-planner for the multi-step workflow.
- **latency:** Seconds to plan, longer for execution; keep the spoken confirmation short.
- **cost:** Moderate; planning and multi-surface actions dominate.
- **security:** May touch authenticated sessions and send messages. Use receipts and confirmations for high-impact actions.
- **missing:** 

### "“I’m away from my Mac. Find the cheapest nonstop flight that fits my constraints, use my logged-in browser only for the final comparison, and tell me the best option with the exact tradeoffs.”"
- **useful because:** This would turn the worn pendant into a trustworthy remote research agent: the relay captures constraints conversationally, the Mac planner searches broadly, and the authenticated browser session is used only where public tools cannot reach. The owner gets a decision-ready answer without manually shuttling links between devices.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Realtime for constraint capture and a one-sentence clarification; mac-planner/background tier for search and comparison; browser harness only for authenticated pages; realtime again for the final spoken synthesis.
- **latency:** Acknowledge in under 1 second; 10–60 seconds for public search and logged-in comparison; push a concise result when complete, with a dashboard evidence trail.
- **cost:** Roughly $0.03–$0.20 per request depending on planner iterations and page extraction; browser calls and planner context dominate, not the short voice turns.
- **security:** Search constraints and any authenticated page excerpts leave the pendant for relay/Mac processing. Never expose credentials to the model; retain only cited result snippets and URLs; require explicit confirmation before booking or purchasing.
- **missing:** A durable cross-surface research job that can combine web_search/read_web_page with the owner's authenticated browser session; A result schema containing normalized options, constraints satisfied/violated, citations, and confidence; A relay completion path that can deliver the result after the voice turn without making the owner poll

### "“When I say ‘quiet mode,’ make the whole hive private: stop speaking sensitive details, mute or lock the Mac/browser surfaces, and keep only a short confirmation on the pendant. When I say ‘resume,’ restore the previous state.”"
- **useful because:** The owner can wear the device in public or around other people and change the privacy posture in one spoken command. It coordinates the pendant, relay, Mac audio/display, and browser rather than relying on one surface's local mute switch.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Realtime intent recognition and immediate acknowledgement; deterministic Mac/browser state capture and restoration; no expensive model after the state transition.
- **latency:** Acknowledge and begin enforcement in under 500 ms; complete surface changes within 2 seconds; if a surface is offline, state exactly which one remains unprotected.
- **cost:** Usually below $0.01 per toggle; cost is dominated by one state snapshot and a few Mac/browser actions, not inference.
- **security:** The privacy mode must fail closed for spoken content: if relay cannot verify a surface's state, it must not claim privacy. Store a signed pre-toggle snapshot, never log sensitive transcript text in the confirmation, and make resume restore only the states this command changed.
- **missing:** A first-class privacy posture record spanning pendant, relay, Mac audio/notifications, and browser tabs; Atomic or compensating state transitions with per-surface acknowledgement and an offline-safe pendant indicator; A redacted status/result contract so the relay can confirm protection without repeating secrets

### "“Remember this as a reusable way of working: whenever I ask for a client update, gather the latest project facts, draft a short email in my editor, and leave it ready for me to review—but never send it.”"
- **useful because:** The owner gets a personalized command that compounds over time instead of repeating a multi-step workflow. The pendant supplies the trigger while the relay retrieves only relevant memory, the Mac gathers current material and drafts, and the browser can add context from an authenticated project page. The safety boundary is useful: preparation is automatic, sending remains impossible by construction.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Realtime to capture and confirm the reusable recipe; background planner to execute each invocation; cheap deterministic memory projection and action validation; realtime only for the spoken result.
- **latency:** Recipe creation under 3 seconds; invocation acknowledgement under 1 second and draft completion within 30 seconds; push a completion alert if the owner walks away.
- **cost:** About $0.02–$0.10 per invocation depending on browser/planner steps; memory retrieval is cheap, while authenticated page extraction and drafting dominate.
- **security:** Persist the recipe as a structured template, not unrestricted prompt text. Scope facts by surface/task, redact secrets, and enforce a hard no-send terminal action. Show source links and the draft location in the dashboard; deletion must remove both recipe and derived sensitive artifacts.
- **missing:** A user-facing routine/recipe layer that stores parameterized multi-surface workflows rather than only fixed schedules; Binding from a spoken alias to a validated plan with current memory projection and browser findings; A no-send draft artifact contract and completion receipt that the Mac and relay both honor

### "“I’m leaving now. Keep working on the task I just started, and if it finishes, tell me the result; if it needs a decision, ask me one precise question on the pendant. I should also be able to say ‘cancel that’ or ‘undo the last change’ from anywhere.”"
- **useful because:** The owner can physically walk away without abandoning work or babysitting a browser. This is more than a completion ping: the relay becomes a durable control surface for an active Mac/browser job, translating only actionable blockers into a short voice exchange and exposing cancellation/undo when available.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Realtime for the initial handoff, blocker question, and cancel/undo intent; background planner and deterministic job monitor for execution; no expensive model while merely waiting.
- **latency:** Immediate acknowledgement under 1 second; blocker alerts within 5 seconds of detection; cancellation request acknowledged under 2 seconds; final summary delivered asynchronously.
- **cost:** About $0.01–$0.08 per delegated task outside the planner's normal execution cost; monitoring is mostly polling/event infrastructure, with inference only on blocker summaries.
- **security:** A spoken cancel/undo must be bound to the owner's active session and job identity, not a vague historical reference. Do not claim completion without a receipt; if undo is unavailable, say so and preserve the exact failure state. Pending questions must expire rather than silently authorizing a mutation.
- **missing:** A durable voice-owned job lease linking a pendant session to one or more Mac/browser jobs; A blocker protocol that pauses safely, asks one constrained question, and resumes with the answer; Real asynchronous delivery from job state changes to the pendant, plus authenticated cancel/undo resolution for spoken references

### "“Tell me what changed in my work since yesterday, but only after checking the project page in my logged-in browser and the local files on my Mac. Cite each change, flag contradictions, and say what I should do next.”"
- **useful because:** This gives the owner a single spoken situation report assembled from sources that no one node can reach alone: authenticated browser state, local Mac files, and the relay's remembered project context. Contradiction detection prevents a polished but false summary, which is especially valuable when the owner is away from the screen.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Background planner gathers and normalizes sources; a judgement tier compares claims and ranks next actions; realtime only asks for scope and speaks the short result.
- **latency:** Acknowledge immediately; deliver within 30–90 seconds; provide a dashboard evidence view while the pendant speaks only the top changes and contradictions.
- **cost:** Approximately $0.05–$0.25 per report; Mac file inspection, authenticated browser extraction, and claim comparison dominate.
- **security:** Limit file paths and browser pages to the named project; preserve source URLs and file timestamps; do not read unrelated mail or secrets. Mark stale/blocked sources explicitly and never infer ‘no change’ from an unavailable surface.
- **missing:** A cross-surface snapshot job with a shared cutoff time and source freshness metadata; A normalized claim/evidence format and contradiction detector spanning browser text and Mac artifacts; A spoken compression policy that retains uncertainty and cites evidence in the dashboard


## What it asked for

_Nothing._
## Its own summary

Recorded four owner-facing proposals: cross-surface authenticated research with tradeoffs, a coordinated whole-hive privacy posture, reusable spoken workflows that produce drafts without sending, and a durable walk-away job lease with blocker questions/cancel/undo. Also recorded a cross-surface evidence report that compares authenticated browser state with local Mac artifacts and flags contradictions. The strongest immediate value is walk-away control: the owner can leave the desk while retaining truthful, voice-level control over work. The required changes are durable job ownership, blocker/resume semantics, evidence normalization, and real asynchronous delivery to the pendant—not another local action wrapper.

**Biggest unknown:** Whether the existing job_completion_watch and relay_event_push paths are actually wired end-to-end to a live pendant, and whether /workbench/contexts can provide source snapshots suitable for cross-surface evidence comparison. The proposal recorder accepted these as missing or unverified rather than assuming they exist.

