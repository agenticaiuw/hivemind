# Harness derivation — relay-realtime — round 228

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I lost the thread—show me the exact things I started but did not finish, what state each is in, and let me resume one by voice.”"
- **useful because:** A job can finish while the owner is away, fail after a Mac disconnect, or pause in a browser form, but today there is no owner-facing, cross-surface recovery view that joins those states into actionable spoken resume cards. This prevents abandoned half-completed work and avoids making the owner repeat context.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** A cheap background summarizer builds resume cards from receipts, handoffs, browser state, and memory; realtime only reads the selected card and routes the explicit resume utterance.
- **latency:** The inventory may refresh asynchronously; selecting and reading a card should respond in under 2 seconds.
- **cost:** Under $0.01 per refresh when mostly structured metadata; occasional summarization dominates.
- **security:** Cards must distinguish observed state from inference, redact authenticated URLs/form values, expire sensitive browser state, and never claim a task is complete without a receipt. Resuming must use the recorded job revision rather than replaying an old action list.
- **missing:** A cross-surface unfinished-work index with explicit states: paused, failed, awaiting owner, stale, and complete-with-unread-result; A redacted resume-card schema and ranking policy; A resume endpoint that rehydrates the correct Mac/browser context safely; Pendant inbox presentation for cards longer than one spoken sentence

### "“When I point my attention at something on my Mac or in my signed-in browser, let me say ‘take care of this’ and have you use the visible item—not a guessed search result—as the source of truth.”"
- **useful because:** The owner currently has to describe a screen or manually bridge a browser page into voice. A coordinated attention handoff would let the worn pendant supply intent while Mac vision identifies the focused window and browser extension supplies the authenticated DOM, then return a concise spoken result. This is useful precisely when the owner is moving between desk and room and cannot narrate UI details.
- **path:** pendant → relay → mac-vision → mac-planner → browser-extension
- **model tier:** A low-cost vision/DOM grounding pass identifies the focused target; realtime interprets the short utterance and confirms only when grounding is ambiguous; planner executes the resulting structured action.
- **latency:** Grounding preview under 3 seconds; spoken acknowledgement under 1 second; execution asynchronous for multi-step work.
- **cost:** Roughly $0.01–$0.08 per invocation, dominated by a screenshot or vision pass; DOM-only pages should be near the low end.
- **security:** Screenshots and DOM extracts may contain secrets and should stay on the Mac/browser bridge unless a redacted excerpt is necessary. Bind the action to a target hash and foreground-window timestamp so a later click cannot affect a different page. Never silently use a background tab when the visible target is unavailable.
- **missing:** A live focused-target snapshot contract from mac-vision and the browser extension; Cross-surface target identity and freshness hashes; A relay utterance flow that can ask ‘which of these two?’ with spoken disambiguation; Result receipts that include the target evidence used

### "“Why did you do that, and what did you actually see? Read me the short evidence trail for the last action, including anything you were uncertain about.”"
- **useful because:** Receipts can record an outcome, but the owner cannot currently interrogate the causal evidence behind a Mac or browser action from the pendant. A provenance replay would make remote automation legible: the owner hears the target observed, the action taken, the result, and any uncertainty, rather than trusting an unexplained success sentence.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Structured event aggregation and a cheap summarizer do the work; realtime only answers the spoken follow-up and reads a compact, evidence-linked explanation.
- **latency:** First sentence under 2 seconds from a recent receipt; fetching older evidence may take 5 seconds.
- **cost:** Usually below $0.01 because the source is structured receipts; vision evidence summarization is the dominant occasional cost.
- **security:** Evidence must be redacted before leaving the Mac/browser, with secrets and full page text excluded by default. Every claim must link to a timestamped observation or receipt and distinguish observed facts from planner rationale. Expired evidence should be reported as unavailable, never reconstructed as fact.
- **missing:** A normalized action-evidence event schema shared by Mac, browser, and relay; Redacted screenshot/DOM provenance references with retention and expiry; A spoken query over the event graph keyed by job, time, and action; A dashboard timeline for inspecting the same evidence with links to raw local artifacts


## Changes it proposed to its own stack

### `context` — Replace the live voice prompt's legacy working-project and long-term-memory blocks with the existing surface/task-aware projectContext projection, while preserving a short stable preference/permission prefix and recording which projected facts were used by each turn. Add an A/B measurement on prompt bytes, latency, and follow-up resolution before deleting the legacy path.
- **owner gets:** The pendant would answer faster and with fewer stale or irrelevant details, while still remembering the owner’s actual preferences and the current task. Follow-up phrases such as “send it to him” would use the relevant projected context instead of forcing the expensive realtime model to reread a large unrelated memory block.
- effort: Small-to-medium server change: thread surface and utterance task into conversationContext.js, call projectContext, add regression tests and one production metric.  ·  risk: A fact may be omitted or scoped incorrectly, causing a less helpful answer. Recover with a fallback to the legacy block when projection reports low confidence or dropped required entities, and compare A/B transcripts before making it default.
- cost: Reduces context-token spend materially (measured projection saves about 222 tokens/turn, roughly 59% of the prior block); no new external API cost.  ·  latency: Likely lower prompt assembly and model latency; projection itself is local and should be sub-millisecond to low milliseconds.
- security: Improves least-context behavior by honoring voice/mac/browser surface scopes; sensitive facts remain excluded unless the existing reveal policy permits them.
- depends on: Existing GET /memory/projection?surface=&task=&budgetTokens=&revealSensitive=&includeWeb= route; conversationContext.js live prompt integration point; A/B transcript and token measurement


## What it asked for

_Nothing._
