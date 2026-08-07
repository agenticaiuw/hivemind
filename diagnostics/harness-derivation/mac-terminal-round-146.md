# Harness derivation — mac-terminal — round 146

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Save this research trail so I can pick it up tomorrow—even if the browser tabs change.”"
- **useful because:** A spoken request should create a durable, human-readable case packet from the current authenticated tabs: page titles, quoted passages, timestamps, source URLs, and the owner's short voice note. It should remain available when tabs are closed, be resumable from the pendant, and detect which sources changed later. This is more durable than a one-off page brief and does not require the owner to organize files manually.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-terminal → dashboard
- **model tier:** Use a cheap background text model for extraction, deduplication, and change summaries; realtime only confirms the packet name and reads a short result.
- **latency:** Acknowledge in 2 seconds; capture 3–4 tabs and write the packet in under 15 seconds; later change scan under 30 seconds. Pendant playback should start within 1 second from cached text.
- **cost:** About $0.01–$0.06 per capture, dominated by page text; hash and store raw excerpts locally so repeat scans send only diffs.
- **security:** The packet may contain private authenticated content. Store encrypted-at-rest on the Mac, disclose source domains in the pendant response, redact obvious secrets, and require confirmation before sharing/exporting. Keep immutable source timestamps and hashes so generated claims cannot silently become stale.
- **missing:** A durable evidence-packet format and local encrypted store with source hashes, excerpt provenance, and owner voice-note metadata; A browser command to snapshot several already-open tabs plus authenticated page text without navigating away; A scheduled or on-demand diff scanner that re-reads only changed sources and reports meaningful changes; A pendant command to list, resume, and speak packet summaries while offline from the relay

### "“I’m about to unplug the Mac—keep listening for short notes and quietly file them, then bring me a concise catch-up when I reconnect.”"
- **useful because:** This turns the physically tethered prototype into something wearable today: the nRF9160 button/LED can delimit short offline notes while the Mac disappears, the pendant flash stores them, and reconnecting over USB lets the Mac transcribe, timestamp, deduplicate, and deliver a prioritized catch-up through the relay. It preserves the owner's thoughts across the exact interruption that currently loses work, rather than pretending LTE registration exists.
- **path:** pendant → mac-terminal → relay-realtime → dashboard
- **model tier:** No model while offline; use a cheap background transcription/summarization model after USB reconnection. Realtime is only for the spoken catch-up.
- **latency:** Button-to-record under 100 ms offline; reconnect import under 10 seconds for 10 notes; catch-up under 20 seconds and interruptible.
- **cost:** About $0.01–$0.05 per reconnect batch, dominated by transcription; local WAV/PCM should be downsampled and deleted after verified transcription.
- **security:** Notes can contain private speech. Encrypt pendant flash records if feasible, otherwise erase immediately after an authenticated USB transfer; show an LED code for storage-full and transfer success, never claim cloud delivery until relay receipt. Require explicit opt-in before syncing notes beyond the Mac.
- **missing:** Firmware ring-buffer note recorder using the existing full-duplex I2S and one button, with flash-backed records and a truthful LED protocol; A USB serial framing and resume protocol with checksums, duplicate suppression, and erase-after-receipt semantics; Mac reconnect watcher that imports and transcribes notes without opening the microphone; A relay endpoint and dashboard view for batch status and spoken prioritized catch-up

### "“I’m going into a meeting—make the computer quiet, keep anything urgent for me, and catch me up when I press the pendant afterward.”"
- **useful because:** A single spoken command should create a temporary attention boundary across every surface: the Mac enters a reversible Focus/audio state, the browser stops nonessential prompts while preserving authenticated work, the relay classifies incoming jobs and queues only urgent interruptions, and the pendant’s next press exits the boundary and speaks a compact digest. Today these surfaces can mute or summarize independently, but they cannot share one start/stop boundary or guarantee that deferred work is not lost.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → dashboard
- **model tier:** Use realtime for the two short spoken interactions; use a cheap background model to classify queued events and produce the post-meeting digest.
- **latency:** Start acknowledgement under 2 seconds; Mac/browser quieting under 5 seconds; restore under 5 seconds; post-meeting digest ready within 15 seconds of the button press.
- **cost:** Approximately $0.005–$0.04 per meeting, mostly digest classification and summarization; ordinary queued events should be handled by deterministic rules.
- **security:** The classifier may see private mail, browser titles, and job text. Keep raw content local where possible, send only minimal excerpts to the relay, and make the meeting boundary explicit with a visible dashboard indicator and pendant LED state. Restoration must preserve the exact pre-meeting volume, Focus, tabs, and pending jobs; never discard deferred work.
- **missing:** A temporary cross-surface attention-boundary state machine with start, active, interrupted, and restored states; Mac actions to snapshot/restore Focus, volume, and notification-related state without relying on untrusted UI receipts; Browser extension support for suppressing or queueing nonessential commands while retaining authenticated sessions; Relay event classification and a durable urgent/deferred queue keyed to the boundary; A pendant LED/button protocol that reports active, urgent-pending, and restored states


## Changes it proposed to its own stack

### `mac-harness` — Add a shell execution ledger that captures, for every run_shell action, the exact argv/command, resolved cwd, start/end monotonic timestamps, exit code, signal/timeout, bounded stdout/stderr with hashes for truncated output, environment and repository fingerprints, and a machine-generated side-effect class (read, reversible, or irreversible) without blocking execution. When a command fails, automatically retain a replay recipe and attach the nearest prior successful command and relevant stderr lines to the job/journal record; when it succeeds, emit artifact paths and a compensating-command hint where one can be inferred.
- **owner gets:** When the assistant says “I ran it,” the owner can see what actually ran, where, and whether it changed anything. A failed long command becomes recoverable instead of requiring the owner to reconstruct it, and future agents stop wasting turns rediscovering the project directory or repeating a dangerous partial command.
- effort: Medium: instrument computerControl.runShell and job/journal serializers, add bounded output storage and a small command classifier, then expose filtered records in the dashboard and relay status.  ·  risk: Capturing environment values can leak secrets and output can contain private data; allowlist/redact variable names, hash rather than store sensitive values, cap output, and keep records local by default. A bad classifier must remain advisory only. If ledger writing fails, execution still proceeds and the job records a degraded-observability flag.
- cost: Negligible model cost; roughly 1–5 MB/day of local logs depending on output caps, plus a small dashboard payload.  ·  latency: Under 10 ms per command for metadata; hashing large output can add tens of milliseconds, so hash streamed chunks and cap at a fixed size.
- security: Improves accountability but creates a concentrated sensitive log. Encrypt the ledger, redact secrets before persistence, and make relay uploads opt-in per job.
- depends on: Existing GET /jobs/:jobId/receipts and GET /journal/:jobId storage; Existing POST /execute run_shell path; A bounded local artifact directory and dashboard view for replay recipes

### `context` — Create a cross-surface task checkpoint that is written at meaningful transitions (pendant request, browser evidence captured, Mac command started/finished, USB link loss) and contains a compact state vector: owner goal, confirmed facts with timestamps, pending next action, blocked reason, artifact/job IDs, and a short model-generated continuation summary. On resume, project only the checkpoint plus newly changed evidence instead of replaying the entire conversation or raw logs. Expose explicit “resume the last task” and “what is blocked?” queries across relay, Mac, and dashboard.
- **owner gets:** The owner can stop halfway through a real task, close the lid or lose USB, and later say “continue” without explaining everything again. Responses become quicker and less repetitive, while stale observations are visibly separated from current facts.
- effort: Medium-high: define a versioned checkpoint schema, add transition hooks to relay pipeline, browser result handling, and Mac job lifecycle, then implement conflict resolution when two surfaces update the same task.  ·  risk: A compressed summary can omit a critical detail or preserve stale assumptions. Keep immutable source IDs/timestamps alongside every summary, mark checkpoints stale after a timeout or link loss, and fall back to raw records when confidence is low. Never treat a checkpoint as proof that an action succeeded.
- cost: Small local/relay storage increase; materially lowers repeated context tokens and therefore model cost on multi-turn tasks. One cheap summarization call per transition batch, not per event.  ·  latency: Adds at most tens of milliseconds to event persistence; resume is faster because projected context is smaller.
- security: Checkpoints may contain sensitive goals and page facts. Encrypt at rest, apply existing session scoping, and avoid copying raw authenticated page contents into the relay unless the owner has opted in.
- depends on: POST /pipeline/events and GET /pipeline/stream; GET /jobs and GET /journal/:jobId; Browser result/inspection records; Existing /context-graph and /capture storage


## What it asked for

_Nothing._
## Its own summary

Round 146 produced three non-duplicate additions: (1) a durable browser research-trail packet with source hashes, excerpts, voice note, and later change detection; (2) a cross-surface task checkpoint so “continue” survives tab changes, USB loss, and model turns without replaying expensive context; (3) an offline pendant note queue that records while the Mac is unplugged and imports/transcribes only after verified USB reconnect. I also submitted a shell observability ledger, though the recorder flagged it as close to existing execution-envelope work. A CI repair loop was rejected as already covered and was not rephrased.

**Biggest unknown:** The remaining blockers are implementation, not discovery: the USB serial protocol and firmware flash/ring-buffer format are unspecified; the browser snapshot/inspection contract does not yet expose durable multi-tab source hashes/diffs; and Mac Accessibility/Screen Recording remain false, so UI receipts are untrustworthy. I still need those three contracts (plus a decision on encrypted local storage and erase-after-receipt) before these can be run end-to-end.

