# Harness derivation — relay-realtime — round 223

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Diagnose my pendant and file a bug report."
- **useful because:** This is the one-button path to trust: the owner gets a quick, accurate diagnosis and a ready-to-share report without digging through logs.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** relay for coordination, cheaper background model on Mac for log analysis
- **latency:** Under 3 seconds to confirm the test started; deeper analysis can continue in the background.
- **cost:** Low per invocation; most cost is log transfer and summarization on the Mac.
- **security:** Logs may contain sensitive metadata. Redact tokens, URLs, and personal content before filing. Ask before uploading large audio artifacts.
- **missing:** A structured diagnostic payload from pendant over USB; A relay-visible capability to create a durable bug report artifact

### "Show me what data you’re sending right now."
- **useful because:** A quick privacy audit builds confidence and helps the owner catch accidental leakage from browser or microphone paths.
- **path:** relay → mac-bridge → browser
- **model tier:** relay for narration, mac for enumerating active flows
- **latency:** 1-2 seconds for a concise spoken answer; detailed breakdown on Mac if requested.
- **cost:** Very low; mostly reading status endpoints.
- **security:** The audit itself must not expose secrets (like cookies). Provide categories and sources, not values.
- **missing:** A unified data-flow inventory across relay and Mac surfaces

### "Summarize what you heard and what you did, and leave me receipts."
- **useful because:** It closes the loop: owners can trust outcomes, revisit them later, and debug when something goes wrong.
- **path:** relay → mac-bridge → dashboard
- **model tier:** relay for concise spoken summary, mac for detailed receipts
- **latency:** Short spoken summary under 2 sentences; detailed receipts can render later.
- **cost:** Moderate; receipts and journal retrieval dominate.
- **security:** Receipts may include sensitive file paths or message content. Redact by default and reveal only on request.
- **missing:** A stable receipt format that maps voice intents to executed actions

### "“Go through this meeting with me. Listen for decisions and action items, keep a private running brief, and when it ends read me the three things I personally owe.”"
- **useful because:** The owner gets a wearable meeting sidecar without staring at the Mac: the pendant is the control and spoken output, the Mac supplies meeting audio and local apps, the authenticated browser supplies the meeting session, and the relay keeps the live loop responsive. It turns an hour of passive listening into an actionable spoken debrief.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Use relay-realtime only for button/voice control and urgent interruption; stream or chunk meeting audio to a cheaper background transcription/summarization model, with mac-vision/browser-extension extracting visible speaker and document context.
- **latency:** Button acknowledgement under 300 ms; urgent action-item cue under 2 s; final three-item brief within 30 s of the meeting ending.
- **cost:** Roughly $0.03–$0.20 per meeting hour depending on audio transcription; vision calls dominate when slides or shared documents change.
- **security:** Meeting audio, participant names, and shared documents leave the Mac only if the owner enables this mode. It must have an unmistakable recording LED/haptic state, a physical stop gesture, per-meeting retention expiry, and never send messages or create tasks without an explicit spoken or button confirmation.
- **missing:** Mac system-audio capture with a meeting-scoped consent boundary; Low-latency streaming transcription and diarization; Browser meeting-tab integration that can identify the active call and shared document; A relay session coordinator that merges audio, browser observations, and Mac context into one private brief; A durable, expiring meeting transcript/action-item record surfaced through the existing inbox rather than a new queue

### "“Find the right document in my authenticated browser and local project, compare the numbers to my calendar commitments, prepare the exact reply, and tell me the evidence before you send anything.”"
- **useful because:** This is the system's highest-value everyday action: it closes the loop from a spoken goal to a trustworthy decision across surfaces the owner cannot unify manually while walking. The owner hears not just a draft but the source trail, discrepancies, and what will happen next.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Relay-realtime handles clarification and a concise evidence readout. A slower planner performs the multi-step retrieval and comparison; a cheap extraction model normalizes tables and dates; a separate verifier checks every claim against captured source excerpts before preparation.
- **latency:** Acknowledge immediately, return a first answer in 10 s, and allow 1–3 minutes for a complex comparison. The owner can interrupt the spoken evidence and ask for only the discrepancy.
- **cost:** Approximately $0.05–$0.40 per request; browser/Mac vision and long-document extraction dominate, not the short relay turn.
- **security:** Authenticated pages and local files are combined into a sensitive evidence packet. Keep it relay-job scoped with field-level redaction and expiry, never expose unrelated browser tabs, and require a deliberate approve step immediately before sending or mutating anything. A failed verifier must say “not verified,” never fabricate confidence.
- **missing:** A cross-surface planner that can hand one goal to browser and Mac workers while preserving source identities; A normalized evidence packet format with quoted excerpts, timestamps, and claim-to-source links; A verifier pass that blocks an ungrounded draft from reaching /approve; Browser tab/document scoping and local-file scoping in the same job; Spoken, interruptible presentation of evidence and discrepancies on the pendant

### "“Keep an eye on my Mac and authenticated browser while I’m away. Interrupt my pendant only for something genuinely urgent; otherwise collect a short digest I can ask for later, and explain why you interrupted.”"
- **useful because:** The owner gets the benefit of an always-on assistant without turning the pendant into a noisy notification channel. It arbitrates across mail, calendar, browser changes, long-running Mac jobs, and the owner's current voice session, preserving attention while still surfacing a real emergency or deadline.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Use a cheap background classifier for event normalization and urgency scoring; use relay-realtime only to decide the immediate spoken interruption and to answer “why now?”. Escalate ambiguous or high-impact events to a stronger judgement model, not every notification.
- **latency:** Ingest events continuously; urgent interrupt within 2 s of a source event; nonurgent digest available on demand in under 3 s; never interrupt while the owner is speaking unless the event crosses a configured emergency threshold.
- **cost:** About $0.01–$0.08 per active day for event classification and compact digests; cost is driven by event volume and document extraction, so unchanged events should be deduplicated before model calls.
- **security:** This observes notifications and authenticated pages. It needs an explicit per-source allowlist, local redaction before relay upload, an audit trail showing the event and score that caused an interruption, and a physical mute/stop path. It must distinguish “could not check” from “nothing urgent” and must never silently suppress an already-promised deadline.
- **missing:** A unified event ingress from Mac notifications, browser watches, and relay jobs; A durable urgency policy with owner-tunable categories, quiet hours, and interruption budget; Presence/session state so the system knows when the owner is speaking, driving, or unavailable; A deduplicating event ledger that links repeated updates to one incident and records why it was escalated; A relay-to-pendant interrupt path that can preempt speech safely and preserve the interrupted response


## What it asked for

_Nothing._
## Its own summary

Recorded three new owner-facing capabilities: a consented meeting sidecar with spoken action-item debrief; cross-surface evidence-grounded research-to-reply across authenticated browser, local Mac files, and calendar; and an attention arbiter that interrupts the worn pendant only for genuinely urgent events while explaining why. The evidence-grounded cross-surface task is the single most useful: it unifies the surfaces no one node can access and verifies claims before action.

**Biggest unknown:** The exact live schemas and implementations of the observed /prepare, /approve, /watches, and pipeline-event routes remain only partially inventoried; the proposals explicitly mark the missing connective behavior rather than assuming those routes provide it.

