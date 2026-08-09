# Harness derivation — unified — round 191

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I press the pendant's bookmark button and say “continue this at my desk,” carry the exact conversational/task context to my Mac, reopen the relevant workspace and browser tabs, and tell me what was already completed versus what still needs me."
- **useful because:** A physical moment marker becomes a real cross-device continuation instead of a timestamp: the owner can leave a thought while away and resume at the desk without repeating themselves or accidentally redoing an action.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Use deterministic event binding and the background tier to package context; use the expensive realtime tier only for the short spoken confirmation and ambiguity resolution.
- **latency:** Acknowledge the button locally in under 100 ms; relay receipt under 2 s when online; desk restoration within 10 s after the Mac is reachable.
- **cost:** About $0.01–$0.05 per continuation, dominated by one context-summary/background model call; deterministic marker and handoff are negligible.
- **security:** Transmit only the selected task nonce, transcript excerpt and opaque workspace references, not ambient audio. Browser restoration must be read-only until the owner explicitly approves an action; show the exact tabs and files being reopened.
- **missing:** A marker payload amendment carrying task/conversation nonce and monotonic event ID; A durable relay-to-Mac context handoff endpoint that binds one marker to one workbench context; Mac/browser restoration that reports postconditions and does not silently execute queued actions

### "Before I rely on a reply, say “prove the path” and have the pendant run a bounded end-to-end audio/link check, then tell me in one sentence whether my next reply will be heard, with the measured reason if not."
- **useful because:** The owner gets an actionable answer to the only question that matters during a conversation—whether speech will arrive—rather than a misleading connected indicator. It uses the shipped 24 kHz path and catches simultaneous loss before a long response is spoken.
- **path:** pendant → relay-realtime → mac-planner → mac-vision
- **model tier:** Use deterministic diagnostics and fault counters; use realtime only to phrase the compact result and choose a safe profile already defined by the congestion guard.
- **latency:** Local button acknowledgement under 100 ms; active probe and verdict within 2 s; never block ordinary conversation unless explicitly requested.
- **cost:** Near-zero model cost for a deterministic probe; at most $0.01 for spoken explanation.
- **security:** Probe payloads must be synthetic and contain no microphone content. Do not persist test audio; return only counters, profile and verdict. A degraded verdict may recommend the shipped fallback but must not silently change an owner-approved call mode.
- **missing:** A callable, bounded fixture trigger on the pendant/bridge that correlates uplink, relay and downlink sequence IDs; A compact authenticated result receipt consumable by the pendant; Policy tying the result to duplex_audio_congestion_guard without making diagnostics run on every turn

### "Stop giving me four separate morning interruptions: combine routines that overlap into one spoken brief, run each source once, and tell me which calendar, mail, file, battery and research items were included or skipped."
- **useful because:** The owner already has multiple daily routines at the same time, including overlapping morning briefs. This turns competing scheduled jobs into one predictable handoff instead of duplicate speech and duplicate browser/Mac work.
- **path:** relay-realtime → mac-planner → browser-extension → pendant
- **model tier:** Use deterministic schedule overlap and source deduplication; use the background tier to summarize the merged results, with realtime only for the final short spoken delivery.
- **latency:** Detect conflicts at routine creation and at scheduler startup; merged execution should begin within one schedule tick and deliver a single result within 30 s of the slowest source.
- **cost:** Usually lower than today because duplicate source reads disappear; roughly $0.01–$0.05 for one merged summary.
- **security:** Preserve each routine's permissions and destructive-action confirmation independently. Do not merge a routine that would send mail, delete files or submit a form into an auto-running brief. Expose a source-by-source inclusion receipt.
- **missing:** A scheduler conflict graph that groups routines by firing window and source intent; A merge plan and owner-visible override for routines that should remain separate; One spoken/audio delivery receipt listing source results and failures

### "Give me a five-minute “help me finish this” session: after I physically authorize a stated goal on the pendant, let the Mac and bound browser tabs take only the declared class of actions under a spend/time/file budget, stop at the first scope violation, and tell me exactly what changed when the session expires."
- **useful because:** Today approval is attached to individual staged actions, while a real task often needs a short chain across a browser, Mac files and a spoken interaction. This gives the owner useful delegation without handing the system an unbounded bearer token or requiring repeated confirmations for every harmless step.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard-ux
- **model tier:** Use deterministic scope, budget, expiry and policy enforcement; use the planner tier to decompose the stated goal and realtime only for the pendant readback and stop reason.
- **latency:** Physical authorization receipt under 2 s; each action starts within 3 s; hard expiry and revocation take effect within one action boundary, never mid-write.
- **cost:** About $0.03–$0.15 per session, dominated by planning and the final change summary; enforcement and receipts are negligible.
- **security:** The session must be bound to exact app/tab/path capabilities, a plan digest, an expiry, action count and resource budgets. Browser credentials and form secrets never enter the pendant. Any send, purchase, delete, or off-machine action remains separately blocked. Scope violations fail closed and produce a signed receipt.
- **missing:** A capability-token/session record distinct from the existing one-shot transaction approval; Executor middleware that enforces path/tab/action/resource budgets before every Mac or browser action; A durable cross-surface session ledger with revocation, expiry and a human-readable diff of changes


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities: a pendant-to-desk continuation capsule, a routine-overlap merger for the owner's duplicate morning schedules, and an explicit on-demand end-to-end audio-path verdict. The extracted-fact transparency idea was correctly rejected as already covered, and the audio proposal was accepted as connective work rather than a new primitive.

**Biggest unknown:** Whether the workbench handoff routes (/workbench/contexts, /workbench/jobs/:jobId/handoff, /workbench/contexts/:contextId) truly exist in the live route inventory. I still need a targeted route description plus the scheduler's routine-grouping semantics before implementation can be scoped honestly.

