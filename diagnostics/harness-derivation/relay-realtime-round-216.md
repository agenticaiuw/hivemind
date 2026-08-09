# Harness derivation — relay-realtime — round 216

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Before anything consequential leaves my Mac, read back exactly who it will reach and what it contains; if the browser or app’s actual state differs from what I asked, stop and tell me the mismatch.”"
- **useful because:** This turns the pendant from a command microphone into a last-mile truth check. The relay hears the owner’s intended recipient, amount, attachment, or text; the Mac planner and browser extension inspect the rendered, authenticated UI immediately before submission; the owner hears a compact comparison rather than trusting a plan that may have drifted.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime relay only for extracting the owner’s constraints and speaking the verdict; a cheaper background planner performs the semantic comparison, while deterministic DOM/accessibility extraction supplies facts.
- **latency:** 3–8 seconds for an ordinary email/form; up to 15 seconds for a complex page. No model should narrate intermediate steps.
- **cost:** Roughly $0.01–$0.05 per check, dominated by one planner/comparison call; extraction and hashing are local and cheap.
- **security:** The comparison must inspect authenticated page content and may see secrets, but should send only the fields being checked to the relay and retain a redacted receipt. A mismatch must be surfaced, not silently normalized. This is an observational safety check, not an arbitrary confirmation gate.
- **missing:** A structured intent envelope carrying recipient/content/amount constraints from voice to the Mac planner; A browser/Mac pre-submit inspection action that returns normalized fields plus source locators; A semantic diff and redacted receipt route; A single spoken mismatch response that can leave the task paused without losing its browser session

### "“Keep this task alive while I walk away. If the Mac or browser reaches a genuinely ambiguous choice, ask me one short question on the pendant, wait for my answer, and continue from the exact checkpoint instead of starting over.”"
- **useful because:** Today a long delegated task can finish or fail, but an ambiguity discovered after the voice session has no natural conversational return path. This would let the owner leave the Mac, answer a single targeted question from anywhere, and preserve the authenticated browser session and already-completed work.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Background Mac planner handles the workflow; realtime relay handles only the short clarification exchange; a small durable state machine, not a model, owns checkpoint and correlation.
- **latency:** The initial handoff should be immediate; clarification delivery within seconds of the planner pausing. The task may remain suspended for hours without consuming model turns.
- **cost:** About $0.005–$0.03 per clarification, plus negligible durable-state storage; cost is dominated by the one short realtime turn.
- **security:** The question must identify the task and show only the minimum choices. Answers must be bound to a nonce/job checkpoint so a late answer cannot affect a newer task. Authenticated browser state stays on the Mac; the relay stores only the checkpoint and answer.
- **missing:** A durable WAITING_FOR_OWNER job state with checkpoint payload and expiry; A relay-to-pendant question inbox and answer endpoint distinct from completion alerts; Planner support for pausing and resuming at a named action boundary; A dashboard view of pending questions and expired checkpoints

### "“For the next hour, treat everything I say as private scratchpad: use it to act right now if I ask, but do not put the words, page contents, or result into memory, browser findings, transcripts used for later turns, or Mac logs.”"
- **useful because:** A worn microphone is present in intimate situations where durable memory is inappropriate. A spoken privacy mode would let the owner still control the Mac and authenticated browser while sharply limiting retention across every node, rather than relying on remembering which subsystem logs what.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime relay recognizes the mode and enforces it deterministically; downstream agents receive a short-lived capability token and do not need an expensive model to decide retention.
- **latency:** Mode activation and acknowledgement under one second; enforcement adds no meaningful task latency.
- **cost:** Negligible per invocation; storage deletion/audit is the dominant engineering cost, not inference.
- **security:** This must be fail-closed: if a downstream surface cannot honor the token, the relay must refuse to forward sensitive content and say so. Existing provider logs and OS-level telemetry need explicit redaction limits; the owner should see a dashboard receipt of what was intentionally discarded, without retaining the content itself.
- **missing:** An ephemeral-session/retention token understood by relay, Mac planner, browser extension, and memory service; A transcript and log redaction path covering voice runs, job receipts, browser findings, and planner prompts; A pendant gesture or spoken mode switch that remains active across a delegated job; A test harness proving no private payload reaches persistent memory or browser-finding routes


## What it asked for

_Nothing._
