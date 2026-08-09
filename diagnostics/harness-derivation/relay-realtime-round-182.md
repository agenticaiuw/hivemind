# Harness derivation — relay-realtime — round 182

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If I stop mid-command, recover gracefully: ask one smart follow-up, suggest the top two likely intents, and keep context minimal.”"
- **useful because:** Voice is messy. This improves reliability without forcing the owner to repeat everything, and it reduces context cost by keeping only a tiny, explicit state.
- **path:** relay-realtime → mac-planner → browser-extension
- **model tier:** Realtime for quick clarification; mac-planner only after intent is disambiguated.
- **latency:** Clarification under 700ms; escalation to Mac only when needed.
- **cost:** Very low. It avoids expensive work by preventing misroutes and unnecessary planning runs.
- **security:** Do not infer sensitive data. If the utterance could trigger data access, require confirmation before reading private content.
- **missing:** A resolvable intent-routing tool or a small enum-based intent schema shared across relay and Mac; A policy for what minimal context can be cached across turns without re-sending full transcripts

### "“Undo the last thing you did across my Mac and browser.” The pendant should identify the most recent completed mutation, tell me exactly what will be restored, and on my spoken command carry out the inverse (including browser-session changes) with a receipt."
- **useful because:** A voice assistant that can act but cannot reliably undo is dangerous in daily use. This gives the owner a practical recovery path while away from the Mac, rather than making them reconstruct which app or tab changed.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension → dashboard
- **model tier:** Realtime only for identifying the referenced action and speaking the concise diff; a background/cheaper planner computes and validates inverse actions from stored receipts.
- **latency:** Under 2 seconds to announce the candidate mutation; under 10 seconds to compute the inverse; execution may take as long as the underlying Mac/browser action.
- **cost:** Roughly $0.01–$0.05 per undo, dominated by planner context and any screenshot/page inspection; simple receipt lookup is negligible.
- **security:** Inverse actions can themselves be destructive or impossible after external state changes. The relay must show the original and proposed inverse, refuse to claim success without post-state evidence, and expire/mark receipts when their target no longer matches. No third-party data needs to leave the Mac/browser beyond existing action context.
- **missing:** A mutation receipt schema containing pre-state fingerprints and an inverse or inverse-planning inputs; A persistent per-owner action ledger with ordering and expiry; Mac/browser executors that can verify preconditions and return post-state evidence; A spoken confirmation protocol for this specifically requested undo operation

### "“Make me a handoff packet for this task.” While I am away, the pendant should capture my goal, the relay should collect the relevant authenticated browser page and Mac files, and the Mac planner should produce a compact packet containing the current facts, unresolved choices, proposed next actions, and exact links/paths so I can resume by voice later."
- **useful because:** Today a voice request and the machine’s transient context are easily separated. A durable, source-linked handoff turns an interrupted thought into something the owner can resume without reopening apps, remembering tabs, or repeating discovery.
- **path:** pendant → relay → mac-planner → browser-extension → mac-terminal → dashboard
- **model tier:** Realtime extracts the goal and asks at most one clarification. A cheaper background model performs source collection, deduplication, and packet drafting; realtime only reads the final short summary.
- **latency:** Acknowledge capture in under 1 second; packet draft within 30–90 seconds when Mac and browser are online; allow partial packet delivery if one surface is unavailable.
- **cost:** About $0.03–$0.15 per packet, dominated by page/file extraction and summarization; storing the compact packet is inexpensive.
- **security:** Authenticated pages and local files must stay on their owning surface or be explicitly scoped; packet entries need source labels, timestamps, and stale markers. Never paraphrase inaccessible content as if collected. The owner should be able to delete a packet from the pendant or dashboard.
- **missing:** A cross-surface capture session that binds one spoken goal to Mac and browser collection; A source-linked packet data model with freshness and partial-completion fields; A relay endpoint to retrieve and stream packets to the pendant after the voice turn; A Mac-side collector for selected files and current app state

### "“Start this workflow and keep it moving even after I stop talking; tell me only when it reaches a decision or is blocked.” The relay should checkpoint a multi-step goal, let the Mac and authenticated browser perform independent steps, resume after disconnects, and return a spoken escalation containing the exact blocker and the smallest choice I need to make."
- **useful because:** The owner is usually away from the Mac. Current jobs are effectively one handoff, so a dropped laptop, expired tab, or intermediate decision strands the task. Checkpointed execution makes the wearable useful for real work rather than only issuing single commands.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use a cheaper background planner for decomposition, retries, and checkpoint evaluation; use realtime only for the initial goal, terse progress/escalation, and the owner's answer to a blocker.
- **latency:** Immediate spoken acknowledgement; checkpoint updates within 5 seconds of each completed step; resume automatically after reconnect and tolerate hours of interruption.
- **cost:** Approximately $0.05–$0.30 per workflow, dominated by planner retries and browser/page context; idle waiting should use no model calls.
- **security:** A resumed workflow must never blindly repeat a mutation. Each step needs an idempotency key, observed preconditions, and a receipt. Browser credentials remain in the browser harness; only structured results and redacted evidence cross the relay. Escalations must distinguish blocked, failed, and complete.
- **missing:** A durable workflow/saga runner with checkpoints, retries, and reconnect recovery; Cloudflare Durable Object alarms or an equivalent background worker for resumption; Per-step idempotency and precondition receipts across Mac and browser; An event stream to the pendant for blocker/decision notifications; A shared workflow state view in the dashboard

### "“Why did you do that, and what did you actually see?” For any spoken answer or computer action, the pendant should be able to replay a short, time-ordered provenance trail: my utterance, the Mac/browser evidence consulted, the action taken, and what changed, with stale or missing evidence called out."
- **useful because:** When an answer is wrong or an action surprises the owner, ordinary chat history is not enough. A concise evidence trail lets them diagnose and correct the system while away from the Mac, instead of guessing whether the relay, browser session, or planner hallucinated.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime retrieves and compresses an existing provenance record; a cheaper background process normalizes event records and computes diffs. No expensive model call is needed to collect raw events.
- **latency:** First provenance sentence in under 2 seconds; full trail within 5 seconds. Raw records should be available in the dashboard for deeper inspection.
- **cost:** Under $0.02 per query when records already exist; storage and event normalization dominate rather than inference.
- **security:** Evidence can contain private mail, files, and authenticated pages. Keep raw payloads on the originating surface, expose redacted excerpts and hashes by default, enforce owner-scoped retention/deletion, and never invent a source when an event is absent.
- **missing:** A unified provenance event schema spanning voice, relay decisions, Mac actions, and browser observations; Stable correlation IDs linking one spoken turn to every downstream job and receipt; Redaction and retention controls for evidence excerpts; A relay query endpoint that can answer temporal questions over the event graph


## Changes it proposed to its own stack

### `relay` — Build a durable workflow coordinator that sits between /plan and /execute as a checkpointed saga: it stores the dependency graph, idempotency key, observed preconditions, result receipt, retry policy, and next runnable step; it resumes on Mac/browser reconnect and emits only decision-needed or terminal events to the existing pendant inbox.
- **owner gets:** A request does not die when the Mac sleeps or a browser tab disappears; the owner hears one truthful blocker or completion instead of repeatedly asking what happened.
- effort: High: Durable Object state machine, reconnect protocol in Mac/browser harnesses, idempotent action adapters, and integration tests for partial success and crash recovery.  ·  risk: A bad retry could duplicate an external mutation. Require precondition checks and idempotency at every mutation, quarantine ambiguous steps, and make recovery replayable from receipts.
- cost: Low idle cost; roughly $0.01–$0.10 per active workflow for state and occasional background planning, plus Durable Object/storage usage.  ·  latency: Adds tens to hundreds of milliseconds to each step for checkpoint writes; spoken acknowledgement remains immediate.
- security: Workflow state may reference private browser and Mac data. Encrypt or minimize payloads, retain source-local evidence, and scope each workflow to the owner/session.
- depends on: An event delivery implementation for POST /pipeline/events; Stable action receipts from /jobs/:jobId/receipts; A scheduler via Durable Object alarms or an equivalent background worker; Idempotency and precondition support in Mac and browser executors


## What it asked for

_Nothing._
