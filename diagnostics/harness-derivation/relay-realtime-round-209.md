# Harness derivation — relay-realtime — round 209

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I’m in the middle of doing something on my computer and I ask a question, answer using what’s on my screen, and then summarize it back to me in one sentence."
- **useful because:** It turns the pendant into a hands-free “what am I looking at?” assistant when the owner is at the Mac, without forcing them to switch context. It’s especially useful for debugging, emails, and docs.
- **path:** relay → mac-vision → mac-bridge → pendant
- **model tier:** Realtime to capture/clarify the question; a cheaper vision/computer-use tier to read the screen and extract relevant info; relay to deliver a concise spoken summary.
- **latency:** 1–3 seconds for a simple read-and-summarize; longer if UI interaction is needed.
- **cost:** Moderate. Cost dominated by screen capture/vision tokens; keep summaries short and only capture when asked.
- **security:** Screen contents may contain secrets. Require explicit owner phrasing like “what’s on my screen” to capture, and avoid storing screenshots. Summaries should avoid quoting sensitive text unless asked.
- **missing:** Computer-use loop is currently disabled; it needs to be enabled or replaced by a safe vision pipeline.; A reliable way for the relay to request a one-shot screen read without starting a full automation session.; A policy for redacting sensitive content from summaries.

### "“Take care of this, but if the result differs from what you expected, stop and tell me exactly what changed.”"
- **useful because:** The owner gets reliable automation rather than a blind command: the pendant captures the intent, the Mac or authenticated browser performs it, and the relay compares the observed result with the requested outcome before reporting success. This is especially valuable when the owner is away from the Mac and cannot inspect the screen.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Use the realtime model only to normalize the spoken goal and narrate exceptions; use the background Mac planner for planning and the browser/computer-use tier for execution and verification.
- **latency:** Acknowledge in under 1 second; allow 10–60 seconds for execution. Do not speak “done” until an independent postcondition check finishes.
- **cost:** One short realtime turn plus one planner invocation; roughly $0.02–$0.10 depending on the task, with browser/computer-use steps dominating.
- **security:** The relay must retain the owner’s exact success condition and an execution receipt, but should return only the minimum evidence needed in speech. A mismatch must never be narrated as success. Existing owner policy permits reversible actions without prompting; irreversible actions follow the owner’s established policy rather than inventing a new gate.
- **missing:** A first-class postcondition/verifier in the Mac planner that accepts an explicit expected outcome and emits pass/fail/unknown evidence; A result schema that carries observed state and evidence through the job lifecycle; Pendant delivery of a mismatch explanation through the existing alert inbox

### "“Give me a private heads-up when something important needs me, but do not interrupt me for routine progress.”"
- **useful because:** The owner can stay away from the Mac without missing a genuinely urgent change. The relay and browser/Mac surfaces classify events, collapse repeated updates, and deliver only an actionable exception to the worn device; routine completions remain available without turning the pendant into a noisy notification stream.
- **path:** browser-extension → mac-planner → relay → pendant → phone
- **model tier:** Use a cheap background classifier for event ranking and deduplication; use realtime only when converting a selected event into one short spoken sentence.
- **latency:** Classify within one polling/check cycle; deliver a selected alert within 2 seconds of its report. Suppress unchanged and low-confidence events.
- **cost:** Low ongoing cost: background checks and classification dominate; realtime is invoked only for delivered alerts, roughly $0.005–$0.03 per alert.
- **security:** Authenticated page contents and Mac state must remain scoped to the originating task and never leak into unrelated voice turns. Every alert needs provenance, urgency, expiry, and a reason for interruption so the owner can audit false alarms.
- **missing:** A shared urgency-and-deduplication policy spanning Mac, browser, and relay reports; A private delivery mode with haptic/LED signalling distinct from spoken playback; A durable event identity so the same change is not announced by multiple surfaces

### "“Use what I just told you for this task, but do not remember it or let it appear in future conversations.”"
- **useful because:** The owner can safely dictate sensitive one-off details while still getting cross-surface help. The relay would mark the utterance and all derived browser/Mac artifacts as task-confined, preventing accidental promotion into durable memory or unrelated prompts.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Realtime handles the explicit privacy directive and attaches a short-lived scope token; downstream agents use cheaper models under that token. No extra model call is needed unless the spoken directive is ambiguous.
- **latency:** Apply the scope before dispatching any downstream work, within the normal conversational turn. Expire it at task completion or a fixed short TTL.
- **cost:** Negligible inference overhead; the main cost is carrying a compact scope token and filtering context. No background model is required.
- **security:** The scope must cover transcripts, planner prompts, browser findings, receipts, logs, and derived memory—not merely the final answer. It needs an explicit exception for operational metadata (job ID, failure reason) and a deletion audit so the owner can trust that sensitive content was not retained.
- **missing:** A conversation/task privacy lease propagated across relay, Mac, browser, and memory services; Write-time filtering and deletion for transcripts, browser findings, receipts, and derived facts; A spoken confirmation when a downstream surface cannot honor the lease


## Changes it proposed to its own stack

### `hardware` — Add a low-power haptic actuator and a second, distinctly shaped tactile input to the pendant. Define firmware events for attention-needed, task-mismatch, task-complete, and queued-item navigation; use haptics for private urgency and the second input for acknowledge/expand/dismiss, while preserving the existing single-button recording gesture.
- **owner gets:** The owner can notice and control important automation while walking, in a meeting, or away from the Mac without exposing private speech through a loud spoken interruption or trying to distinguish overloaded LED patterns.
- effort: Mechanical enclosure revision, one haptic driver, one input, firmware gesture/state-machine work, and relay event mapping; validate accidental activation and skin-contact comfort with several weeks of wear testing.  ·  risk: A vibration pattern could be mistaken for a phone notification, and an added button could cause accidental commands. Require an explicit long-press for destructive control, debounce aggressively, and fall back to the current button/LED behavior if the haptic driver fails.
- cost: Approximately $2–$8 in components and PCB/enclosure changes at prototype volume; tens of milliwatts only during short haptic pulses, negligible idle draw.  ·  latency: Local acknowledgement can be immediate; no network round trip is needed to silence or defer an alert.
- security: Improves privacy by reducing spoken notifications. Firmware must not treat an incidental touch as consent to send, delete, purchase, or otherwise perform a high-impact action.
- depends on: A shared urgency-and-deduplication event schema; Pendant support for the existing alert inbox and completion event delivery; Hardware validation of the revised jewellery-style enclosure


## What it asked for

_Nothing._
## Its own summary

Recorded four owner-facing additions: verified postcondition automation (never say done without proving the requested state), quiet cross-surface urgency delivery, a haptic plus second tactile input for private alert control, and a task-scoped privacy lease that prevents sensitive utterances and derivatives entering future context. These require new connective contracts and, for the hardware item, a physical pendant revision; they are not available to the owner today.

**Biggest unknown:** The live relay surface still lacks a trustworthy inventory of its own routes, so the exact implementation seam for propagating verification evidence, urgency identity, and privacy leases remains unknown. The proposals explicitly identify the missing contracts rather than assuming the existing jobs, watches, memory, or event routes already provide them.

