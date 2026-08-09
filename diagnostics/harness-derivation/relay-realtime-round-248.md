# Harness derivation — relay-realtime — round 248

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "What’s happening with the thing I asked earlier?"
- **useful because:** Owners forget exact wording. A status concierge that can resolve vague references reduces frustration and prevents duplicate requests.
- **path:** relay-realtime → relay job records
- **model tier:** realtime for quick conversational clarification; no Mac trip when possible
- **latency:** Under a second for already-recorded jobs, since it reads relay records.
- **cost:** Very low. One job lookup and a short spoken reply.
- **security:** Must not claim success unless the job state says so. Speak the returned status verbatim to avoid hallucinating outcomes.
- **missing:** 

### "If my Mac isn’t reachable, try through the bridge or tell me what’s blocked."
- **useful because:** The owner is often away from the Mac. A graceful fallback makes the system feel dependable instead of brittle.
- **path:** relay-realtime → mac-planner → bridge
- **model tier:** realtime to decide quickly; background for retries or alternate paths
- **latency:** Fast detection (a couple seconds). If fallback is possible, hand off and notify.
- **cost:** Low. The cost is in attempted handoffs and a status update.
- **security:** Avoid repeated retries that leak behavior patterns or spam logs. Avoid doing destructive actions without confirmation, regardless of path.
- **missing:** A documented relay-visible path to the bridge when the Mac is unavailable; Clear routing rules for what can be executed via bridge versus Mac

### "“What am I looking at, and what should I do next?” — while I am away from my Mac, inspect my active Mac app and authenticated browser tab, reconcile the relevant local and web evidence, and tell me one concise next step with links and confidence."
- **useful because:** This is the highest-value everyday interaction: the pendant supplies the owner’s intent and voice, the Mac supplies private local context, the browser supplies sessions the relay cannot possess, and the relay turns the result into an immediate spoken decision rather than making the owner explain which window matters. It is genuinely cross-surface and preserves provenance instead of guessing from one screen.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Use relay-realtime only for intent capture and the final short answer; use mac-vision/mac-planner and the browser harness for extraction, then a cheaper synthesis pass for evidence reconciliation.
- **latency:** Acknowledge in under 1 second; gather context in 5–15 seconds; speak a provisional answer immediately if one source is slow, then deliver one queued correction when complete.
- **cost:** Roughly $0.01–$0.06 per invocation depending on whether vision and browser extraction are needed; latency and token cost are dominated by screenshots/page text, not the spoken turn.
- **security:** Private screen, authenticated pages, and local files leave their owning devices only to the relay/model path. Every cited claim must retain source URL/app and timestamp; redact secrets and never infer that a page is authoritative merely because it is logged in. No destructive action is taken from this request.
- **missing:** A coordinator that can request parallel, read-only snapshots from Mac and browser, join them by the owner’s spoken task, and return provenance plus confidence; Stable authoritative browser-tab targeting (the current default can return the wrong tab); A compact evidence-fusion result schema consumed by the spoken relay

### "“Before you do that, what private data will leave my devices, where will it go, and what will be retained?” Give me a spoken data-flow preview for the exact Mac/browser action I just requested, then let me say “go ahead” or “change it.”"
- **useful because:** The owner has granted broad access, but broad access without visibility makes the wearable impossible to trust. This gives a real person an understandable explanation of the concrete files, page text, audio, and destinations involved in a pending action—without forcing them to inspect logs on a Mac. It is an informational preview, not a generic permission gate.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Relay-realtime classifies the immediate request and speaks a short preview; a cheaper background pass derives the data-flow manifest from the planned actions and receipts. Use the low-latency model again only for the owner’s follow-up choice.
- **latency:** Preview in 2–4 seconds for a short action list; up to 10 seconds for a multi-app plan. The owner should hear the action intent immediately while the manifest is assembled.
- **cost:** About $0.005–$0.03 per request; dominated by inspecting planned argv, file paths, browser extraction fields, and receipt metadata rather than generation.
- **security:** The preview itself must not quote secrets it is warning about. It should identify classes and destinations (for example, “text from your authenticated payroll page to the relay”), retain a tamper-evident plan hash, and distinguish planned from actually transmitted data. The owner’s “go ahead” is a transparency choice, not an added blanket policy restriction.
- **missing:** A data-flow manifest emitted by every Mac and browser action before execution; A relay endpoint that binds the spoken approval to a plan hash and later compares it with the execution receipt; Redaction and classification of sensitive fields across screenshots, page text, files, and audio

### "“Give me a 20-minute focus window for this task.” Temporarily capture my current Mac and browser state, silence only distracting notifications/tabs, keep the task materials open, and restore exactly what changed when I say “done” or the window expires."
- **useful because:** A worn pendant is the one interface available when the owner decides to focus, while the Mac and browser are the things that actually interrupt them. This turns a spoken intention into a bounded, reversible mode rather than a vague reminder. The state snapshot and restoration matter: the owner can trust that asking for focus will not destroy their working set.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Relay-realtime handles the short command and completion phrase. A cheaper deterministic coordinator snapshots state, applies reversible actions, watches the timer, and restores it; use a planning model only for choosing what counts as distracting when the owner did not specify it.
- **latency:** Acknowledge immediately; enter focus in under 5 seconds; restore within 2 seconds of “done” and within 10 seconds of expiry. No model call should be required for restoration.
- **cost:** About $0.002–$0.02 per session; most work is local state capture and action execution, with generation needed only for ambiguous task or distraction selection.
- **security:** Never close or overwrite unsaved work. Store a local encrypted snapshot of only changed app/window/tab/notification state, with an expiry and explicit recovery if the Mac is offline. Browser authenticated content need not leave the Mac; the relay should receive only action receipts and the owner’s chosen task label.
- **missing:** A durable, expiring focus-session record containing pre-state, applied mutations, owner label, and restoration status; Mac/browser reversible primitives for notification focus, tab visibility, and exact state restore; A relay-side timer/expiry worker and a pendant completion event that survives the voice session

### "“What did you actually get done since yesterday, and what is still unresolved?” Build a truthful spoken retrospective from relay jobs, Mac action receipts, browser results, and my voice requests, separating completed work, failed work, and things that were only planned."
- **useful because:** Today the owner has to remember which requests were spoken, which were handed to the Mac, and which actually succeeded. A wearable retrospective turns the hive’s scattered execution history into an honest answer while away from the desk; distinguishing planned, attempted, and completed prevents the most damaging kind of assistant failure—a confident false completion.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use a cheap background summarizer over structured receipts and history; relay-realtime should only answer the short spoken query and read the final bounded summary. Escalate to a stronger model only when receipts conflict or the owner asks for detail.
- **latency:** Speak “I’m checking your last day” in under 1 second; return a 3–5 item summary in 3–8 seconds; offer drill-down by item without regenerating the entire retrospective.
- **cost:** About $0.003–$0.02 per invocation; structured history retrieval dominates little, while summarization cost scales with the number of jobs and receipts.
- **security:** Do not include page contents, file contents, or sensitive command arguments in the spoken default—only task labels, outcome, timestamp, and destination. Preserve links and receipt IDs for an explicit detailed request, and mark missing telemetry as unknown rather than successful.
- **missing:** A normalized cross-surface activity ledger joining voice runs, plans, executions, browser command results, and undo receipts by correlation ID; Outcome semantics that distinguish planned, running, completed, failed, cancelled, and unknown; A compact retrospective route with time window, surface filters, and spoken/detail response modes


## What it asked for

_Nothing._
## Its own summary

Recorded three new owner-facing capabilities: (1) a cross-surface “what am I looking at?” evidence fusion answer with provenance, (2) a reversible spoken focus window that snapshots/restores Mac and browser state, and (3) a truthful cross-surface retrospective separating planned, completed, failed, and unknown work. Also recorded a data-flow preview capability that explains what private data an action will transmit before execution. The existing memory-projection wiring proposal was correctly rejected as already in the backlog, so I did not rephrase it.

**Biggest unknown:** The missing coordinator contracts are still unspecified: authoritative browser-tab identity, cross-surface evidence and activity schemas, reversible Mac/browser state snapshots, and durable timer/restoration semantics. Those—not another model prompt—are what must change for the owner to have these capabilities.

