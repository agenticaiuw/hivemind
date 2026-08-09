# Harness derivation — relay-realtime — round 234

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If my Mac is asleep or I’m away, tell me what’s going on with my system and whether a task can run right now."
- **useful because:** Prevents frustrating failures: the owner can decide to wake the Mac, plug in, or try a different approach before issuing commands.
- **path:** relay → mac-bridge → pendant
- **model tier:** Realtime for the quick spoken check; no background job needed.
- **latency:** A brief spoken answer within a second when possible; longer if a status probe is required.
- **cost:** Very low: a small status read and a short spoken response.
- **security:** Exposes device state (online/offline, battery, network). Keep it minimal and avoid sharing details beyond what the owner asked for.
- **missing:** A reliable relay-visible device status endpoint for pendant and bridge, beyond Mac agent context; Clear mapping from relay job status to ‘can run now’ readiness

### "Summarize what I was working on across my Mac and browser, and read the next important thing out loud."
- **useful because:** It turns the pendant into a quick daily navigator: what matters next, without a screen. This is only possible by combining browser session context, Mac project state, and the relay’s voice delivery.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** Cheaper planner for aggregation; realtime for the spoken summary.
- **latency:** A couple seconds for aggregation; then a short spoken summary.
- **cost:** Moderate: reading several sources and generating a short summary; reuse cached context when possible.
- **security:** Summaries may include sensitive content from mail, files, or pages. Use permissions and confirm before speaking anything potentially sensitive.
- **missing:** A unified cross-surface context projection wired into the live prompt path; Clear permissions for reading browser and Mac sources in one request; Policy for what can be spoken aloud in shared spaces

### "When I say “save this moment,” capture exactly what I’m doing on the Mac and in the browser so I can say “restore the moment from this morning” later."
- **useful because:** The owner can leave a task without losing the precise working state: focused app, windows, tabs, document/selection where available, and the spoken label are preserved as one recoverable checkpoint. This is more useful than a bookmark because it reconnects the worn device, the acting Mac, and authenticated browser state.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Realtime only for recognizing the short save/restore command; mac-planner and browser-extension do the capture/restore work asynchronously, with mac-vision inspecting UI when structured state is unavailable.
- **latency:** A save acknowledgement under 2 seconds; capture may take 5-15 seconds. Restore should speak a preview under 3 seconds and complete after explicit spoken selection if multiple checkpoints match.
- **cost:** About $0.01-$0.05 per save/restore depending on whether UI vision is needed; most structured Mac/browser captures should avoid the expensive vision tier.
- **security:** Checkpoint metadata may include private tab titles, document names, and authenticated URLs. Store encrypted, scope browser contents to the owner, never read page bodies unless requested, and require confirmation before restoring a state that would type, submit, or alter data.
- **missing:** A durable checkpoint schema and encrypted store joining Mac window state, browser tab/session identifiers, focused location, label, and timestamp; Mac actions to enumerate and restore windows/documents/selection rather than only opening apps/URLs; Browser extension support for serializing and restoring tab groups and session-bound page locations; A relay voice command resolver and checkpoint search/preview endpoint

### "If a task gets stuck while I’m away, ask me one clear question on the pendant, wait for my answer, and continue exactly where you stopped."
- **useful because:** Today an unattended Mac task either guesses, fails, or waits for a live conversation. This makes long computer/browser work genuinely usable while the owner is walking around: the relay turns ambiguity into a durable, answerable interruption rather than losing the task context.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision
- **model tier:** Use the cheaper planner/worker for execution and question generation; use realtime only to recognize the owner’s short answer and bind it to the waiting job.
- **latency:** Question generation within 10 seconds of a blocked step; pendant delivery within seconds when connected and retained until answered. Resume within 5 seconds after the answer reaches the Mac.
- **cost:** Roughly $0.02-$0.10 per blocked task, dominated by the planner context needed to summarize the ambiguity; no model call is needed while simply waiting.
- **security:** The question must expose only the minimum relevant choices, not page secrets or unrelated tabs. Bind answers to an opaque job/question nonce, expire stale questions, and never interpret an answer for a different job. The owner’s existing maximum-access policy still applies to execution.
- **missing:** A first-class WAITING_FOR_OWNER job state with a durable question record, allowed answer forms, expiry, and resume cursor; A relay-to-pendant interactive question delivery path and an answer upload path (the current inbox can surface alerts but cannot correlate a reply to a paused plan); Mac planner support for checkpointing tool state and resuming from a validated answer; A conflict policy for answers arriving after the Mac has already timed out or changed state

### "Before you upload or send something for me, tell me out loud what private details it contains and let me say “remove the phone number” or “send it” without opening the Mac."
- **useful because:** The owner gets a practical privacy checkpoint at the only moment that matters: immediately before data leaves a local file or authenticated browser. It combines Mac file access, browser session reach, relay reasoning, and the pendant’s hands-free approval; today those surfaces can act, but cannot produce a compact spoken disclosure-and-redaction loop.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Use a cheaper extraction/classification model for local candidate detection and a realtime turn only for the short spoken disclosure and owner’s redaction commands. Use the planner/browser tiers to apply edits and upload.
- **latency:** Initial disclosure in 3-8 seconds for a normal document; each redaction command acknowledged in under 2 seconds. Never submit until the owner’s explicit send instruction is bound to the exact content hash.
- **cost:** About $0.02-$0.15 per document, mostly OCR/structured extraction and any vision needed for PDFs or screenshots; text-only files are cheaper.
- **security:** The disclosure engine itself sees sensitive content, so processing should stay on the Mac whenever possible and send only entity labels/counts to the relay. Keep a content hash and immutable pre-send preview, redact locally, and prevent a stale spoken approval from authorizing changed content or a different recipient.
- **missing:** A Mac-local sensitive-entity extractor covering text, PDFs, images, and clipboard data; A relay protocol for a spoken disclosure card with content hash, recipient, destination, and field-level redaction commands; Browser and Mac actions that transform a staged copy, recalculate its hash, and submit only the approved version; A durable pending-send record so a dropped pendant link cannot silently turn approval into submission


## Changes it proposed to its own stack

### `model-routing` — Add a rule that the relay acknowledges commands, then hands long-running planning/aggregation to a cheaper model tier by default, retaining only the minimal state needed to answer quick spoken follow-ups.
- **owner gets:** Keeps the pendant responsive and reduces cost, without losing the thread of what was asked.
- effort: Medium: routing logic and state handoff; requires a minimal shared job reference.  ·  risk: Low to medium: follow-up questions could lose context; mitigate by storing job IDs and using status tools.
- cost: Reduces expensive realtime usage; more work runs on cheaper tiers.  ·  latency: Improves conversational responsiveness.
- security: Ensure job references don’t leak sensitive content.


## What it asked for

_Nothing._
## Its own summary

Recorded three new owner-facing capabilities. The strongest is durable clarification escrow: a long-running Mac/browser task can pause on a precise ambiguity, ask the worn owner one question, accept the answer later, and resume from a checkpoint. It needs a WAITING_FOR_OWNER job state, durable question/answer correlation, pendant delivery and answer upload, and planner resume cursors. Also recorded exact cross-surface work-state checkpoints, and a spoken pre-send privacy disclosure/redaction loop that hashes the approved content before submission. All three require new connective protocols rather than assuming current tools already provide them.

**Biggest unknown:** Whether the backlog already contains a near-duplicate of the pre-send disclosure/redaction loop; the recorder accepted it, but did not return a similarity warning.

