# Harness derivation — relay-realtime — round 152

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Tell me what’s urgent across my stuff right now, and only the top three things."
- **useful because:** A daily “attention triage” saves time and reduces overwhelm, especially when the owner is on the move and can’t scan multiple apps.
- **path:** relay → mac-bridge → browser → dashboard
- **model tier:** relay for voice; mac-planner for local sources; browser harness for authenticated web; cheaper model for ranking and summarization.
- **latency:** Quick acknowledgment, then a brief spoken summary within a few seconds; deeper evidence available on the Mac.
- **cost:** Moderate; dominated by reading sources (calendar/mail/browser) and summarization.
- **security:** Needs strict source tagging and must show evidence on Mac. Should draft actions but not send or submit without explicit approval.
- **missing:** Reliable authenticated browser session access without the Mac; Unified review queue with evidence and drafts; Scheduler for periodic checks if run unattended

### "Prepare this form or message for me, show me exactly what will change, and wait for my go-ahead."
- **useful because:** This turns the assistant into a safe co-pilot: it can do the tedious parts and still keep the owner in control for irreversible steps.
- **path:** relay → browser → mac-bridge → dashboard
- **model tier:** mac-planner/browser for extraction and drafting; relay for spoken confirmation; cheaper model for diffing and summarizing changes.
- **latency:** Acknowledge fast; drafting may take longer. Final approval step must be explicit and reversible where possible.
- **cost:** Moderate; extraction and draft generation dominate, plus any browser automation.
- **security:** Never submit without approval. Keep sensitive fields minimized in spoken output; show full diff in a secure review surface.
- **missing:** Provenance-aware extraction and typed results from browser automation; Reliable command queue with irreversible-action checkpoints; UI for review and approval across devices

### "When I say “pause the hive,” stop every in-flight Mac and browser action immediately, preserve exactly where each task was, and resume when I say “continue” — even if I am away from the Mac."
- **useful because:** The owner can interrupt an unsafe, mistaken, or socially inconvenient action from the wearable instead of racing to the keyboard. This is a cross-surface primitive: the pendant supplies the urgent signal, the relay fans it out, and Mac/browser workers must cooperatively cancel and checkpoint work.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime model only classifies the short voice command; cancellation, checkpointing, and resume are deterministic worker behavior.
- **latency:** The stop signal should reach every worker in under 500 ms; resume can take a few seconds while workers restore checkpoints.
- **cost:** Negligible model cost for a command; engineering/storage cost is a durable cancellation token and per-action checkpoints, not inference.
- **security:** A false wake or speech recognition could interrupt work, so require the physical pendant button plus the spoken phrase for the global variant. Checkpoints must exclude secrets and never serialize browser credentials. Resume must be idempotent to avoid duplicate mutations.
- **missing:** relay-wide cancellation broadcast and durable run state; cooperative cancellation hooks in Mac planner/vision and browser extension; pendant button-plus-voice emergency command; idempotent checkpoint/resume protocol and owner-visible pause receipt

### "While I am at my desk, let me say “remember this page for me.” Later, away from the Mac, let me ask the pendant “what did that page say about the renewal date?” and get a cited answer without reopening the site or exposing my browser cookies."
- **useful because:** This turns authenticated browser access into a safe, portable memory rather than requiring the owner to be at the computer every time. The browser keeps the session and emits only an explicitly requested, expiring excerpt; the relay can answer from that sealed fact while the Mac is offline.
- **path:** pendant → browser-extension → mac-planner → relay → dashboard
- **model tier:** Use a cheaper background model to extract and normalize the explicitly selected page excerpt; use realtime only for the later short spoken lookup.
- **latency:** Capture confirmation under 2 seconds; an away-from-Mac lookup under 3 seconds if the sealed excerpt is local to the relay.
- **cost:** One small extraction call per saved excerpt and a small lookup call later; storage is a few KB per fact, dominated by model extraction rather than transport.
- **security:** Never copy cookies, DOM broadly, or unrestricted page text. Require an explicit spoken/button save, encrypt the excerpt, attach source URL, timestamp, scope, and expiry, and support immediate revoke. Sensitive fields should be redacted locally before upload.
- **missing:** browser-extension command to create a narrowly scoped signed excerpt; encrypted relay vault with expiry and revocation; citation-aware retrieval over owner-approved excerpts; pendant UX for naming, querying, and deleting saved facts

### "When I double-press the pendant and say “meeting mode,” make my Mac and browser go quiet, suppress non-urgent notifications, keep a tiny queue of what was deferred, and tell me through the pendant only if something meets my urgent rules; say “meeting over” to restore everything exactly."
- **useful because:** The owner can enter a meeting or focused conversation without touching the Mac. The wearable is the reliable physical context switch, the relay applies it even while the owner is away, and Mac/browser surfaces coordinate notification suppression and restoration instead of each behaving independently.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime handles the short mode command; deterministic policy and notification state snapshots do the work. A cheap background model may rank deferred items when the mode ends.
- **latency:** Mute/suppress actions should begin within 1 second; the end-of-mode digest can arrive within 10 seconds.
- **cost:** Near-zero realtime inference for mode changes; optional small background ranking call per meeting. Main cost is platform integration and encrypted state storage.
- **security:** The owner must be able to recover from a lost “meeting over” command. Persist a timeout and a visible dashboard override. Urgent rules must be explicit and local where possible; do not upload message contents merely to decide urgency.
- **missing:** pendant double-press and mode-state firmware event; Mac notification focus integration with complete pre-mode snapshot/restore; browser extension notification/audio suppression hooks; relay policy engine, deferred-event queue, timeout, and spoken urgent interrupt


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities. (1) A pendant-triggered global pause/resume with durable checkpoints and cooperative cancellation across Mac and browser workers; the owner can stop the hive while away. (2) Explicitly saved, narrowly scoped, expiring browser excerpts that the relay can answer from later without reopening the authenticated site or exporting cookies. (3) A physical pendant “meeting mode” that coordinates Mac/browser notification suppression, urgent-only interrupts, deferred-item queuing, timeout recovery, and exact restoration. The remaining needs are not more discovery: durable cross-worker cancellation/checkpoint state; a browser signed-excerpt vault with redaction, expiry, citation and revoke; and pendant mode events plus Mac/browser notification hooks and a relay urgency/deferred queue. Existing routes are building blocks, not complete owner experiences.

**Biggest unknown:** Whether any unobserved browser-extension or platform notification hooks already support signed excerpt export or exact notification-state restoration; the user explicitly prohibited further discovery this round, so these remain implementation questions rather than assumptions.

