# Harness derivation — mac-planner — round 135

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-planner live reliability** — The newly granted mac_readonly_inspect tool is still schema-only and returns an implementation error. The live /observe route works: foreground app is Claude; Accessibility and Screen Recording are false for AI Pendant Agent; browser extension is offline with 10 pending commands. Browser failures currently consume about 45 seconds before reporting timeout/offline.
  - evidence: mac_readonly_inspect calls returned 'This tool was granted a schema but has no implementation yet'; GET /observe at 2026-08-07T14:35:42Z; GET /browser/status at 2026-08-07T14:35:42Z; GET /jobs showed browser_navigate failed after 45034 ms.

## Capabilities it proposed

### "“Pause here; when I say resume, put me back exactly where I was and remind me what I was doing.”"
- **useful because:** The pendant becomes a reliable interruption buffer: it records the Mac's foreground app, open work files, authenticated browser tabs, and the next calendar item, then later restores only the reversible parts and speaks a one-sentence orientation. No single node can do this: the pendant supplies the interruption trigger, the relay keeps the capsule while the owner is away, the Mac observes and restores desktop state, and the browser bridge preserves private tab/session context.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use Realtime only for the short pause/resume utterance and spoken confirmation; use a cheaper background model to label the captured context and rank the likely next action. Deterministic code should capture, diff, and restore state; no model should invent paths or URLs.
- **latency:** Pause acknowledgement under 1 second with a local/relay receipt; capsule completion within 3 seconds when Mac and browser are online. Resume should speak immediately from the stored capsule, then restore app/file/tab state in under 8 seconds. If the browser is offline, say so and restore the Mac portion instead of waiting 45 seconds for browser timeout.
- **cost:** About $0.001–$0.01 per pause/resume, dominated by the small background labeling call; routine pauses can be zero-model deterministic records. Storage is a few KB of redacted metadata per capsule plus optional short note, with configurable expiry.
- **security:** Capsules contain private app names, file paths, calendar titles, and authenticated tab URLs, so encrypt at rest, redact query parameters and page text by default, and expire after 7 days. Never capture passwords, form fields, clipboard contents, screenshots, or microphone audio. Restoring an app, file, or browser tab is reversible and can be automatic; sending, deleting, purchasing, or submitting anything remains outside restore and requires the owner's existing confirmation policy. Clearly label stale/offline browser state.
- **missing:** A durable capsule schema with provenance, TTL, redaction, and per-surface freshness; A pendant pause/resume event that survives a dropped link and queues a capsule identifier offline; A fast preflight that skips offline browser commands instead of waiting for their timeout; An implementation (not just schema) for read-only Mac inspection; until then, use the existing /observe route as the fallback

### "“Why didn’t that work? Diagnose the Mac and browser connection, tell me the one thing I need to fix, and keep trying once it’s fixed.”"
- **useful because:** Today the owner sees long browser timeouts, fake-success UI receipts, and opaque “failed” jobs. A spoken repair flight recorder would correlate the pendant request, relay pipeline, Mac reachability/TCC state, browser heartbeat, and job receipts; give one actionable diagnosis instead of a vague error; then automatically retry only the failed, non-destructive step after the relevant surface returns.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic rules for diagnosis and retry eligibility; use a cheap background model only to turn the evidence into one short spoken explanation. Realtime handles the owner's question and acknowledgement, not the investigation.
- **latency:** Initial diagnosis under 2 seconds from cached health state, with active probes capped at 3 seconds. Never wait on a browser command's 45-second timeout when /browser/status already says offline. After heartbeat recovery, retry within 5 seconds and report the original receipt plus the new receipt.
- **cost:** Usually zero model calls for rules; under $0.005 when narration needs summarization. Small durable records (health snapshots, job IDs, and error classes) can expire after 24 hours.
- **security:** Diagnostics may include app names, tab URLs, file paths, and TCC state. Keep raw details local and send the relay only an error class, timestamps, and redacted labels unless the owner asks for detail. Never retry send/delete/buy/submit actions; retry only idempotent reads and explicitly reversible opens. Do not attempt to grant Accessibility or Screen Recording—tell the owner the exact manual System Settings action required.
- **missing:** A correlation ID shared across pendant request, pipeline, browser command, and Mac job receipts; A failure classifier that distinguishes offline, timeout, TCC-untrusted UI, permission denial, and malformed plans; A retry ledger with idempotency keys and an explicit allowlist of safe retry types; A browser heartbeat recovery event and a Mac-side TCC remediation hint

### "“Finish this when I come back, but only if nothing important changed; otherwise tell me exactly what changed before touching anything.”"
- **useful because:** The owner gets safe continuity across interruptions without having to remember whether a draft, tab, or file changed. The system captures a proof of the relevant Mac file, foreground app, browser tab, and task intent; later the relay and pendant can detect a mismatch and explain it instead of blindly replaying stale actions. This is different from a durable job queue: it is state-conditional continuation with an explicit before/after explanation.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic hashes, timestamps, tab identity, and file metadata for the state proof. Use a cheap background model only to summarize the differences. Realtime is reserved for the brief spoken confirmation or alert.
- **latency:** Capture under 1 second. Resume validation under 2 seconds from Mac and browser health/state, with a hard 3-second timeout per surface. If a surface is offline, preserve the continuation and tell the owner which proof is unavailable rather than executing.
- **cost:** Near-zero API cost for metadata and hashes; under $0.005 only when a model summarizes meaningful differences. Each continuation proof should be under 10 KB and expire after an owner-selected period.
- **security:** Never hash or upload raw passwords, clipboard contents, form values, or page bodies by default. Keep file hashes and private URLs local; relay receives only opaque capsule IDs and redacted difference summaries. A mismatch must block continuation, not be treated as approval. Sending, deleting, purchasing, or submitting remains excluded and requires the existing owner confirmation policy.
- **missing:** A durable continuation record containing task intent, per-surface state proofs, expiry, and an idempotency key; Mac file/app proofs and browser DOM-region or semantic proofs that can be compared without exporting private content; A validator that atomically compares all proofs immediately before execution and emits structured diffs; A resume protocol from pendant to relay that can survive offline periods and distinguish stale, changed, and unavailable state


## What it asked for

_Nothing._
