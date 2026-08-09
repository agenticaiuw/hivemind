# Harness derivation — mac-planner — round 204

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Save this page for later when I say so or press the pendant bookmark button."
- **useful because:** Preserves the active browser page as a durable, deduplicated research card with a one-sentence spoken confirmation, unlike a timestamp-only moment bookmark.
- **path:** pendant → relay → browser → mac-planner
- **model tier:** Cheap background summarizer; realtime only for the brief confirmation.
- **latency:** Confirmation under 2 seconds; card completion under 15 seconds.
- **cost:** About one short-context model call, dominated by page extraction.
- **security:** Capture only active URL/title/selection and bounded readable text; never submit forms. Exclude secrets and require explicit command for broad page capture.
- **missing:** Deterministic browser-tab/page-selection inspection; mac_serial_exchange for fully pendant-initiated USB testing

### "Something just failed—make me a reproducible incident packet."
- **useful because:** Combines pendant diagnostics, Mac state, browser context, and relay receipts into one timestamped, hashed artifact instead of an invented explanation or UART-only fragment.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** No model for collection; cheap summarizer only after facts are collected.
- **latency:** Packet in 5 seconds; spoken summary in another 5–10 seconds.
- **cost:** Near-zero collection cost plus one small summarization call.
- **security:** Redact tokens, passwords, page bodies, and microphone/audio payloads by default; include exact observed errors and job IDs only.
- **missing:** mac_serial_exchange; Explicit configurable log-redaction policy

### "Brief me on this page later and put the spoken version on my pendant."
- **useful because:** Creates a cited, time-stamped Markdown brief and offline-playable audio from the page currently open in Safari, without requiring the owner to reopen it.
- **path:** browser → relay → mac-planner → pendant
- **model tier:** Background/cheap model; realtime only for an interrupting follow-up.
- **latency:** Immediate acknowledgement; final brief within 30 seconds.
- **cost:** One moderate summarization call, dominated by extracted page tokens.
- **security:** Preserve canonical URL, capture time, and content hash; bounded extraction; do not access authenticated pages unless the active browser session explicitly supplies them.
- **missing:** Deterministic browser-tab inspection; Page-content size/truncation contract; Relay route accepting cited document and emitting Markdown plus pendant audio

### "Turn what I have open in VS Code and the browser into a tested change, then tell me exactly what changed."
- **useful because:** The owner can move from intention to a verified repository change without manually ferrying context between editor, documentation tabs, relay planning, and the Mac executor. It returns a concrete diff, test evidence, and a spoken result rather than merely suggesting code.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Background coding model for repository analysis and tests; realtime only for the short spoken acknowledgement.
- **latency:** Acknowledge within 2 seconds; first plan within 20 seconds; completion bounded by a 5-minute job.
- **cost:** One medium coding call plus test/runtime cost; context extraction dominates, not speech.
- **security:** Only send explicitly selected workspace paths and inspected browser documents; never include unrelated tabs, secrets, or source files. Keep mutations staged and provide a complete diff and test receipt.
- **missing:** A cross-surface context bundle that joins VS Code files, selected browser documents, and pendant request identity; A bounded test executor with streamed receipts; An explicit staged-change handoff from relay to mac workbench

### "Keep working on this while I am away, and give me one spoken result when it is genuinely finished."
- **useful because:** A long task could survive the owner leaving the Mac, a dropped pendant link, or a retry without producing duplicate files or half-applied work. The owner gets a single durable completion/failure result instead of repeatedly checking several surfaces.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Cheap background worker for polling and retries; use the expensive realtime tier only if the owner interrupts with a question.
- **latency:** Immediate acceptance; retries and progress can take minutes or hours; final notification within one delivery window after completion.
- **cost:** Low model cost during waiting; execution and browser session time dominate.
- **security:** Persist only a job manifest and redacted receipts. Never silently send messages, delete files, purchase, or publish changes; those operations remain explicit owner commands.
- **missing:** A durable cross-node job lease with resumable checkpoints; A single completion-notification contract that targets the pendant inbox and Mac receipt; A scheduler that can rehydrate browser and Mac work after process restart

### "When I ask about something on my Mac, answer from the exact current artifact and show me where each claim came from."
- **useful because:** The owner would get grounded answers about the current editor document, browser page, or local file rather than a generic answer based on stale conversation context. Each claim would link to a file range, page section, or observed UI element, making spoken answers trustworthy and auditable.
- **path:** pendant → relay → mac-planner → browser
- **model tier:** Small extraction model for local structure; stronger model only for synthesis across multiple artifacts.
- **latency:** Spoken answer in under 10 seconds for one artifact; under 30 seconds for a multi-artifact question.
- **cost:** Small-to-medium context call; local extraction and redaction reduce token cost.
- **security:** Default to on-device extraction and send only relevant excerpts. Redact passwords, tokens, hidden browser fields, and unrelated windows. Do not infer access from a visible URL alone.
- **missing:** Semantic document identity and selected-text extraction from the Mac; Structured browser DOM/section provenance rather than screenshot or URL alone; A spoken citation format that maps claims back to local paths and page anchors


## What it asked for

_Nothing._
