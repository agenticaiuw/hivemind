# Harness derivation — relay-realtime — round 161

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Track that task for me and tell me when it finishes, even if I stop talking.”"
- **useful because:** This is the single most useful thing: the owner can start something and walk away. The system handles the waiting and delivers the outcome when it matters.
- **path:** relay → mac-bridge → browser → pendant
- **model tier:** Realtime to acknowledge and hand off; cheaper background tier to monitor and summarize; relay delivers the notification.
- **latency:** Under a second to confirm tracking. Completion notification is asynchronous.
- **cost:** Low per invocation. Main cost is backend monitoring and notification delivery; status checks should be lightweight.
- **security:** Completion messages may contain sensitive task details. Only send short, user-facing summaries, and avoid leaking contents beyond what the owner would hear anyway.
- **missing:** A real relay_event_push implementation (currently a schema without implementation); A background scheduler or job watcher (cron/alarm or durable object) to monitor job completion without an open voice session; A typed notification path to the pendant/phone inbox

### "“Tell me what’s going on with my computer right now and whether it’s safe to proceed.”"
- **useful because:** A fast status check prevents confusion and accidental overlap with ongoing work. It’s a safety net when the owner is away from the Mac.
- **path:** relay → mac-bridge
- **model tier:** Realtime to ask and summarize; mac status tool provides the facts.
- **latency:** 1–2 seconds for a concise spoken summary.
- **cost:** Very low. One status call and a brief summary.
- **security:** Status may reveal sensitive app names or documents; default to minimal detail unless asked for specifics.
- **missing:** Reliable routing from relay to get_mac_status via a confirmed, implemented intent route (today intent routing is not implemented as a tool)

### "“Summarize what I was working on across my tabs and documents, and tell me the next best step.”"
- **useful because:** This turns scattered context into a coherent plan. It’s especially helpful when returning to work after a break or switching tasks mid-day.
- **path:** browser → mac-bridge → relay
- **model tier:** Cheaper planner for synthesis; relay for conversational delivery; browser/Mac for collecting context.
- **latency:** A few seconds depending on content size; must be interruptible and able to deliver a short version first.
- **cost:** Moderate. Reading multiple tabs/documents and synthesizing is the main cost; should be cached when possible.
- **security:** May touch sensitive content. Use least privilege and avoid reading more than necessary; provide citations to what was read.
- **missing:** A durable, typed cross-surface context snapshot format with citations; A unified read pipeline that can merge browser tab summaries with Mac file/app context

### "When I say “resume my work,” reconstruct exactly where I left off across my Mac apps, open browser tabs, and the last pendant conversation, then tell me the single next step and offer to do it."
- **useful because:** The owner can leave the Mac, return hours later, and recover the actual interrupted task rather than receiving a generic machine status or manually searching tabs and notes. The pendant supplies intent and continuity; the Mac and browser supply observable state.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use relay-realtime only to interpret the short request and speak the result; use a cheaper background planner to build a structured interruption checkpoint, with mac-vision only when app state cannot be read through the normal Mac harness.
- **latency:** Acknowledge immediately; first spoken reconstruction within 8 seconds, with later details delivered as a queued alert if needed.
- **cost:** Roughly one small planner invocation plus local observation calls; dominant cost is context extraction and summarization, not audio transport.
- **security:** The checkpoint may contain private document titles, URLs, and text. Keep raw content on the Mac where possible, send only selected excerpts and hashes to the relay, and never expose a private checkpoint aloud unless the owner explicitly asks for it while wearing the paired pendant.
- **missing:** A durable interruption-checkpoint ledger on the Mac/relay with timestamps, active-app and browser-tab provenance, task hypotheses, and confidence; A Mac observer that captures a bounded, user-visible work snapshot without disturbing the foreground app; A resume protocol that returns one cited next action and can invalidate stale checkpoints

### "When I press the pendant and say “bookmark this,” attach that spoken note to a synchronized snapshot of the Mac's active document and authenticated browser tabs, so I can later say “show me the bookmarks from that project” and recover the exact moment."
- **useful because:** A voice memo alone loses the screen context that made it meaningful. This gives the owner a durable, searchable bridge between something they noticed while away or walking around and the precise work state they were looking at.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime handles the short utterance and immediate acknowledgement. A background worker captures and indexes the bounded Mac/browser snapshot, using a smaller embedding or lexical index rather than the realtime model.
- **latency:** Acknowledge in under 1 second; capture confirmation within 5 seconds. Retrieval should speak the top match within 3 seconds.
- **cost:** Low per bookmark: one transcription plus local metadata extraction; optional embedding/indexing is the dominant API cost if enabled.
- **security:** Authenticated URLs and document titles are sensitive. Store the raw snapshot locally on the Mac, retain only encrypted metadata and a short owner-selected excerpt in the relay, and require the pendant's paired session for spoken retrieval.
- **missing:** A consent-bounded snapshot endpoint that records the active app/document and up to four already-open browser tabs at the instant of the press; A durable cross-surface bookmark record linking audio/transcript, timestamp, app/document identity, tab IDs, and project labels; A retrieval API that can cite the original local artifact and gracefully report when it has moved or disappeared

### "Let me start a task on the pendant, walk up to my Mac, and say “continue here”; move the live conversation and its unresolved references to the Mac without making me repeat the request, then let me finish by voice or keyboard."
- **useful because:** The wearable is best while mobile and the Mac is best for long answers and visual work. Today the owner must either keep talking to the pendant or restate the task at the computer; this makes the hive feel like one session moving between bodies.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime owns the short-lived conversational state and handoff acknowledgement. The Mac planner handles the longer continuation; mac-vision and browser-extension are invoked only if the unresolved task needs visual interaction.
- **latency:** Detect the paired Mac and acknowledge handoff within 2 seconds; restore the transcript and unresolved references within 5 seconds. Never block the owner's local Mac input while transferring.
- **cost:** One compact state serialization and one continuation call; token cost is controlled by sending a structured summary plus only the last few turns, not the entire conversation.
- **security:** A handoff could expose a private transcript on an unattended Mac. Require an explicit spoken “continue here” plus paired-device presence, show a visible handoff indicator, expire the transfer state after 60 seconds, and encrypt it in transit and at rest.
- **missing:** A real-time session-handoff channel between the relay and the local Mac agent with presence/expiry semantics; A portable conversation-state format containing unresolved entities, pending actions, cited browser tabs, and cancellation state; A Mac-side continuation surface that can accept the handoff without stealing focus or executing pending actions twice


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities: resumable work reconstruction, context-linked voice bookmarks, and live pendant-to-Mac conversation handoff. The common missing pieces are durable cross-surface state, bounded local observation, and an expiring authenticated handoff protocol—not another generic action route. The recorder flagged each as adjacent to existing ideas, so future work should differentiate by implementing the missing state semantics rather than proposing more variants.

**Biggest unknown:** Whether the existing relay already has an undocumented session-transfer or checkpoint route; discovery was explicitly unavailable this round, so I could not verify that before recording the proposals.

