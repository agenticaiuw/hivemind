# Harness derivation — relay-realtime — round 231

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "While I’m talking, keep track of what I meant, and if it’s ambiguous, ask a quick clarification instead of doing the wrong thing."
- **useful because:** Prevents costly mistakes and keeps the conversation smooth. It makes the pendant feel like a smart assistant, not a command parser.
- **path:** relay → mac-bridge → mac-planner
- **model tier:** Realtime for detection and clarification; mac-planner for execution after intent is clear.
- **latency:** Clarification question must arrive within about a second to feel natural.
- **cost:** Moderate: intent parsing is cheap; the expensive part is context carry and conversation length, which should be minimized.
- **security:** Do not invent details; ask before acting. If destructive actions are implied, confirm explicitly.
- **missing:** A reliable intent-to-actions bridge without inventing a protocol (relay_route_intent is unresolved); Better shared context projection into the live prompt to reduce token cost and ambiguity

### "“Pause the thing you’re doing on my Mac, keep any safe progress, and switch it to this new goal.”"
- **useful because:** A delegated workflow is currently a one-way handoff: the owner cannot redirect it from the wearable without starting a competing job. This would make the pendant a genuine control surface for work already in flight, preserving completed artifacts while preventing stale instructions from continuing.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Relay-realtime classifies the short control utterance; a deterministic job controller pauses/cancels safely, and mac-planner replans from the checkpoint. Use the realtime model only to resolve which active job “it” means.
- **latency:** Acknowledge pause in under 1 s and stop issuing new actions within 2 s; replan after the new goal is captured.
- **cost:** About $0.005–$0.03 per redirect, mostly one planner call; pause/cancel itself should be non-model work.
- **security:** Stopping must be idempotent and leave a receipt of the last action. The controller must distinguish a paused job from one that already committed an irreversible external effect, and must never replay browser clicks or shell commands after resume.
- **missing:** A job-control state machine with pause, cancel, supersede, and checkpoint semantics; A pendant command path that targets active jobs and resolves pronouns against the owner’s active-job list; Planner support for resumable checkpoints and an explicit artifact/side-effect ledger

### "“Undo the last thing you did for me.”"
- **useful because:** After a voice-initiated Mac/browser workflow, the owner currently has to remember which app or site changed and repair it manually. A cross-surface undo would turn mistakes into recoverable events: identify the exact recent action, perform its inverse where possible, and say plainly what could not be reversed.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use a deterministic receipt index to identify the latest owner-requested mutation; mac-planner generates a compensating plan, while browser-extension or Mac actions execute it. Relay-realtime only speaks the result or asks which action if several are equally recent.
- **latency:** Identify and acknowledge the target under 1 s; reversible local changes complete within 5 s. External-service compensation may become an asynchronous job with a spoken pending notice.
- **cost:** $0.01–$0.06 per undo, dominated by compensation planning and browser inspection; receipt lookup and local reversals are negligible.
- **security:** Undo must never pretend that deletion, sending, or third-party effects are reversible. Each compensation needs an audit link to the original receipt, idempotency protection, and an explicit spoken distinction between fully undone, partially compensated, and impossible.
- **missing:** A normalized inverse-operation registry for Mac and browser action types; Receipt records that include before-state or enough information to construct a compensating action; A compensation executor with idempotency and partial-failure reporting

### "“Show me on my Mac exactly what you found when I asked from the pendant.”"
- **useful because:** The owner is often away from the Mac when asking, then returns to a computer with only a spoken summary and no way to inspect the evidence. This would turn a voice result into a handoff: reopen the relevant browser pages, files, and action receipts in a labeled workspace so the owner can verify rather than trust a compressed sentence.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Relay-realtime records the request; a background handoff worker gathers the job’s evidence and mac-planner arranges it. No expensive realtime reasoning is needed except a short spoken acknowledgement.
- **latency:** Speak acknowledgement immediately; prepare the Mac workspace within 10 s for ordinary results, or notify the pendant when a large evidence bundle is ready.
- **cost:** About $0.005–$0.03 per handoff, mainly extraction and one planner call; opening already-known URLs/files is cheap.
- **security:** Do not expose sensitive page contents on a shared display without an explicit owner request. Workspace links must be scoped to the originating job, avoid leaking credentials, and clearly label stale or inferred evidence versus source material.
- **missing:** A job-scoped evidence bundle containing source URLs, screenshots/text excerpts, files, and action receipts; A Mac handoff action that creates a temporary labeled workspace without disturbing unrelated work; A relay event that tells the pendant when the visual handoff is ready


## What it asked for

_Nothing._
## Its own summary

Recorded three non-identical capabilities: wearable control to pause/supersede an active Mac/browser job, cross-surface undo with compensating actions and receipts, and a pendant-to-Mac visual evidence handoff. The first proposed clarification flow was rejected as already present, so I did not count or restate it. These require durable job control/checkpoints, inverse-operation and before-state receipts, and job-scoped evidence/workspace handoff respectively.

**Biggest unknown:** Whether the unobserved /ops/history route already contains enough structured action history to support any of these; the recorder flagged it as the only named piece not established by the current inventory.

