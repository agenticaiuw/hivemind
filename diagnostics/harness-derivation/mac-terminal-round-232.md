# Harness derivation — mac-terminal — round 232

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Continue the task that failed last night from the exact step that is still safe, and ask me only if the next step could duplicate an irreversible action."
- **useful because:** Today a failed multi-action job leaves the owner to reconstruct what happened. This turns the durable ledger into a practical spoken recovery workflow: the pendant can recover a half-finished Mac/browser task without blindly repeating side effects.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision
- **model tier:** background for ledger inspection and deterministic resume planning; realtime only for the short wearable question when an ambiguous side effect is encountered
- **latency:** Immediate acknowledgement under 1 second; inspect and resume in 2-10 seconds per frontier; one question only at each ambiguity
- **cost:** Usually one cheap background planner call (roughly 10k input tokens today because context is oversized); deterministic ledger replay should be near-zero model cost
- **security:** The ledger must expose pre/post state and idempotency keys but never shell environment secrets. The owner must explicitly answer a wearable question before a step marked non-replay-safe; safe reads can proceed unattended.
- **missing:** Boot-time conversion of orphaned processing jobs into recoverable interrupted jobs; orchestrator must close ledgers and attach planMeta.jobId; A resume planner that treats action receipts and idempotency keys as the frontier, not merely rerunning the original action list; A compact relay endpoint that turns one ambiguity into a pendant question and routes the answer back to the waiting job

### "Handle this while I am away, and interrupt me on the pendant only if you are blocked, need a choice, or the deadline is at risk."
- **useful because:** Long Mac/browser work currently either finishes silently or fails into a log. The owner gets a useful third mode: leave a goal, walk away, and receive a concise, actionable wearable interruption only when human judgment is actually needed.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision
- **model tier:** background planner for work and deadline forecasting; realtime model only to compress a block into a yes/no or two-choice spoken prompt
- **latency:** Dispatch acknowledgement under 1 second; background progress checks every 30-60 seconds; wearable prompt within 3 seconds of detecting a block
- **cost:** One cheap planner pass at dispatch plus low-cost deterministic polling; realtime cost only for rare blocked prompts, likely under 1k completion tokens each
- **security:** Never speak page contents or secrets in an unsolicited prompt; give host/app, blocked reason, and redacted choices only. Browser actions that submit, send, purchase, or delete remain explicitly labeled in the prompt. Expire unanswered prompts rather than guessing.
- **missing:** A durable goal/deadline record separate from the transient job record; Mac progress and blocked-state events with a predicted deadline miss, not just completed/failed; Relay wake-and-queue delivery for a blocked prompt while the Mac remains online; Pendant response protocol carrying a short choice token back to the waiting Mac/browser job

### "Use the page and window I was looking at earlier, not the one open now, and pick up where I left off."
- **useful because:** The owner's intent often refers to a vanished tab or prior moment. A wearable should recover that referent from the Mac's recent browser/session trail instead of forcing the owner to remember a title, URL, or project name.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision
- **model tier:** Deterministic search over recent browser sessions, captures, jobs, and context graph first; background model resolves ambiguous references; realtime only asks the owner to choose between two candidate pages
- **latency:** Return two candidates in under 2 seconds; resolve a clear referent and begin work in under 5 seconds; ask one concise wearable disambiguation when needed
- **cost:** Near-zero for indexed lookup; one small background call only for ambiguous natural-language references, far cheaper than sending the whole browsing history to realtime
- **security:** Search only the owner's local authenticated session metadata. Do not read page bodies until the selected candidate is confirmed; display host/title/time and redact sensitive URL query strings in the spoken choice.
- **missing:** A local time-indexed index of tab metadata, captures, and browser session transitions; A stable context bookmark/reference that points to a historical tab state without inventing a new physical marker; Browser extension support for restoring or focusing a historical tab and reporting whether it still has a live session; A compact relay query/result protocol for wearable disambiguation

### "Don't just tell me the browser action ran—check that the intended result is actually true, and tell me what is still wrong."
- **useful because:** A click receipt is not an outcome. A form can reject a field, a download can be partial, or a page can silently remain unchanged. The owner needs end-to-end verification across the authenticated browser and the Mac, delivered as a concise wearable answer.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision
- **model tier:** Deterministic postcondition checks first using DOM/state queries and local file inspection; background model interprets ambiguous evidence; realtime only summarizes the verified result to the pendant
- **latency:** Verification within 2 seconds for structured pages and 5 seconds for visual/canvas pages; wearable answer under 1 second after evidence is collected
- **cost:** Usually no additional model call; one cheap background interpretation only when structured evidence conflicts, with realtime reserved for the final short response
- **security:** Read only the minimum resulting state needed to prove the claim. Never repeat private page contents over audio. Treat a missing or ambiguous postcondition as 'unverified', never as success; preserve source URL and timestamp for audit.
- **missing:** A typed postcondition specification attached to browser and Mac actions; A verifier that can query DOM, download completeness, filesystem state, or visual state after execution; A result object distinguishing executed, verified, disproved, and unknown; Relay delivery of verification evidence rather than only action completion

### "Watch this web transaction until it reaches the condition I specified, and if it changes before completion, pause and tell me instead of letting it drift."
- **useful because:** Many browser tasks are not one action: prices, availability, approval pages, and confirmation states can change between steps. The owner needs a conditional transaction that remains supervised after the initial click, rather than a fragile one-shot automation.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision
- **model tier:** Deterministic watcher for the specified condition and bounded polling; background planner for state transitions; realtime only for a concise exception or choice on the pendant
- **latency:** Initial setup under 5 seconds; polling cadence configurable from 10 seconds to 5 minutes; exception reaches the pendant within 3 seconds
- **cost:** Mostly deterministic browser polling and relay storage; background model only on an unrecognized state transition, so substantially cheaper than continuous realtime vision
- **security:** The owner specifies the allowed condition and expiry. Never continue after a material change, authentication challenge, or timeout. Keep credentials and page contents local to the browser session; speak only a redacted state summary.
- **missing:** A durable conditional-task primitive with expiry, allowed transitions, and an explicit stop state; Browser watchers that compare structured and visual state over time and emit a typed transition; A relay-held wakeup and exception queue that survives Mac sleep or browser reconnect; A pendant response that can select pause, abandon, or resume the same transaction

### "While I am busy, collect interruptions into a short digest, but wake me immediately for anything that could expire, cost money, expose private data, or block the task."
- **useful because:** A wearable that reports every progress event becomes unusable, while silence hides the one decision that matters. The owner needs interruption triage spanning Mac jobs and authenticated browser work, with urgency based on consequences rather than arrival order.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision
- **model tier:** Deterministic classification for known job states, deadlines, spend/privacy markers, and quiet-window policy; background model clusters and summarizes deferred events; realtime only for genuinely urgent wakeups
- **latency:** Urgent event delivered within 3 seconds; ordinary events batched at the owner's chosen interval; digest generation under 5 seconds
- **cost:** Low: event classification and batching are deterministic; one background summarization call per digest, with no realtime usage for routine updates
- **security:** Urgency rules and quiet windows are owner-controlled and persisted locally. Do not infer sensitive categories from page text unless necessary; redact event details in the queue. Expire stale notifications and never wake for an unverified claim.
- **missing:** A shared event severity taxonomy across Mac jobs, browser watchers, and relay events; A durable interruption policy with quiet windows, escalation deadlines, and digest cadence; Relay-side deduplication and batching keyed by task and state transition; Pendant firmware support for urgent-vs-deferred notification modes beyond the current last-action beacon


## Changes it proposed to its own stack

### `mac-harness` — Add an immutable execution provenance envelope to every Mac action, especially run_shell rewrites: preserve the planner's original action, the normalized action actually dispatched (including tkinter/overlay and research-CLI substitutions), resolved cwd, redacted environment fingerprint, pid, start/finish/duration, exit code or signal, stdout/stderr digests plus bounded excerpts, and one correlation ID shared by job, ledger, journal, and relay delivery. Expose a read-only 'explain this action' view that can be requested from the pendant.
- **owner gets:** When the Mac says a task failed, the owner can finally hear what really ran and whether it changed anything, instead of trusting a misleading command string or a generic 'Failed' message. It also makes a spoken 'what happened to that?' answer precise after the owner has left the desk.
- effort: Medium: wrap exec/execFile result handling, capture process metadata without retaining secrets, persist the envelope in the existing receipt stores, and add correlation joins plus a concise explanation formatter.  ·  risk: Capturing too much output or environment could leak secrets; hash and redact by key, cap excerpts, and retain only digests by default. Rewrites must remain behaviorally identical. If metadata capture fails, execution still proceeds and marks the envelope partial.
- cost: Negligible runtime/storage overhead per action; no additional model call for ordinary execution. One small background summarizer only when the owner asks for a natural-language explanation.  ·  latency: Under roughly 10 ms bookkeeping per shell action; no extra network round trip on the hot path.
- security: Improves auditability while reducing secret exposure: environment values are never persisted, only allowlisted names and a keyed fingerprint. The read-only explanation must redact paths, tokens, and page contents.
- depends on: A stable jobId-to-ledger correlation field (planMeta.jobId currently stays null); A closeLedger call at the end of ordinary orchestrator execution; Capture child exit status/signal and pid in the run_shell executor; A read-only explanation route/tool that can be called by relay-realtime


## What it asked for

_Nothing._
