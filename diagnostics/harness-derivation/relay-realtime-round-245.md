# Harness derivation — relay-realtime — round 245

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I say something like “handle the Outlook thing,” figure out what I meant and route it to the right place without me naming the tool."
- **useful because:** The owner talks naturally. The system should turn that into the correct action type and destination without exposing internal tool names.
- **path:** relay → mac-bridge → mac-planner
- **model tier:** Realtime to classify intent fast, then planner tier to expand into actions.
- **latency:** Under a second to confirm the interpretation; planning can take a few seconds.
- **cost:** Low per request; dominated by planning and execution on the Mac.
- **security:** Misrouting is the risk. The relay should confirm high-impact interpretations and require explicit confirmation for destructive operations.
- **missing:** A real implemented routing tool or schema-to-action bridge (relay_route_intent is unresolved); Integration with the existing plan/execute action vocabulary to avoid free-form intents

### "Remember what we’re working on right now and keep future turns focused on that, without me repeating context every time."
- **useful because:** Reduces friction and cost: the owner shouldn’t pay for the same context every turn, and the assistant stays on-task.
- **path:** relay → mac-bridge
- **model tier:** Realtime uses a compact projection head; heavier retrieval happens on the Mac when needed.
- **latency:** No noticeable delay; must be under a second.
- **cost:** Saves tokens per turn by sending a stable, small context head; costs are occasional projection reads.
- **security:** Projection must honor sensitivity and scope rules; only relevant facts for the current surface and task should be included.
- **missing:** Wire the existing memory projection into the live conversation context builder; A task label from the relay for better relevance scoring

### "When I tap the pendant and say “bookmark this,” capture exactly what I was doing on the Mac and browser, then later let me say “take me back to that” and restore the relevant app, tab, document, selection, and a one-sentence reason."
- **useful because:** A physical tap is a reliable interruption boundary. The owner could leave the desk, return hours later, and recover the precise work context rather than remembering which window, tab, or text mattered. This is more useful than a note because it restores state across the Mac and authenticated browser.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Realtime only for the two short utterances; a cheaper background planner should assemble and restore the context, with mac-vision used only when the active UI needs visual interpretation.
- **latency:** Bookmark acknowledgement under 2 seconds; capture under 10 seconds; restore under 15 seconds, with a spoken fallback if a tab or app is no longer available.
- **cost:** Roughly $0.01–$0.08 per bookmark/restore, dominated by one vision snapshot and planner context; most bookmarks need no large model call.
- **security:** The snapshot may include authenticated pages, clipboard text, and window contents. Encrypt the bookmark, retain it for a user-selected TTL, redact passwords/credit-card fields, and never speak captured sensitive text unless explicitly requested.
- **missing:** A first-class cross-surface bookmark record containing app/document/tab identity, selection, screenshot reference, transcript, and provenance; Mac actions to capture active window, caret/selection, and browser tab identity in one atomic snapshot; A restore planner that validates targets before changing the Mac and reports what could not be restored; Pendant utterance routing for bookmark/create versus restore/reopen

### "When I say “what did I leave unfinished?”, search my recent voice sessions, Mac jobs, browser work, and saved task facts, rank the unfinished threads, and let me say “continue the second one” to resume the exact next step."
- **useful because:** The owner should not have to remember whether an abandoned intention lived in a voice memo, a failed Mac action, or a logged-in browser tab. A single spoken backlog turns scattered partial work into actionable continuity and is especially valuable when the pendant is worn away from the desk.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Use a cheap background summarizer/ranker over structured job and memory records; realtime only reads the short ranked list and routes the chosen continuation.
- **latency:** Ranked answer in under 4 seconds; continuation starts within 10 seconds after selection.
- **cost:** About $0.01–$0.05 per query, mostly context retrieval and a small ranking call; continuation costs the normal planner/browser execution budget.
- **security:** Only surface records scoped to the owner and current surface; do not read arbitrary browser content merely to build the list. Show provenance (“from yesterday’s Mac job”) and allow deletion of a thread from the pendant.
- **missing:** A unified unfinished-thread index joining voice runs, jobs, receipts, browser findings, and task facts without duplicating their source data; Thread identity and deduplication across retries and handoffs; A continuation endpoint that rehydrates a selected thread into the correct Mac/browser agent with stale-state checks; A compact spoken disambiguation format and pendant-side selection gesture

### "When you do something for me, let me ask “why did you choose that?” and hear a short, honest explanation that separates what the system observed, what it inferred, what it changed, and what remains uncertain—across the Mac, browser, and relay."
- **useful because:** A single completion receipt says what happened, but not whether the decision was based on a page observation, an owner preference, or a guess. This would let the owner audit an action from the pendant without reopening the Mac, catch mistaken assumptions, and correct the underlying preference rather than merely undoing one result.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Record structured observation/decision/action provenance during execution; use a cheap summarizer for the explanation and realtime only for the spoken answer. Escalate to vision or planner logs only when the owner asks for detail.
- **latency:** A short explanation in under 3 seconds from cached provenance; detailed reconstruction under 15 seconds.
- **cost:** Under $0.01 for a cached short explanation; $0.03–$0.15 when reconstructing multiple agent traces or page evidence.
- **security:** Explanations can quote private page text or commands. Redact secrets and limit the default to actor, evidence class, confidence, and outcome; expose raw evidence only after an explicit request and enforce the same owner/session scope as the source job.
- **missing:** A causality/provenance record linking perception evidence, judgement, selected action, and observed result across agents; A stable spoken reference to the last action or a selected job from the pendant; A redaction and confidence policy that distinguishes observed facts from model rationale; A route that gathers the linked Mac, browser, and relay records into a compact explanation


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities: (1) a cross-surface work bookmark that captures Mac/browser state and restores it later, (2) a unified unfinished-thread spoken backlog that resumes selected work, and (3) source-grounded explanations of what the agents observed, inferred, changed, and still do not know. The blocked-task question/answer channel was proposed but rejected as an existing backlog item, so it was not counted. The first needs an atomic state snapshot and restore planner; the second needs a unified thread index and continuation endpoint; the third needs linked provenance across perception, judgement, action, and result records.

**Biggest unknown:** Whether the existing /ops/history and voice-run records already expose enough structured provenance and active-window identity to implement the recorded ideas, or whether those fields must be added at their source.

