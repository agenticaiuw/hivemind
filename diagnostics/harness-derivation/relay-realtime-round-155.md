# Harness derivation — relay-realtime — round 155

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Mark this moment.” Have the pendant capture a short audio excerpt and, if the Mac is reachable, attach the active screen/browser state; later let me ask “what did I mark at lunch?” and get a time-ordered, source-cited answer."
- **useful because:** The owner can preserve fleeting ideas, decisions, and things visible on a screen without opening an app or remembering to take notes. The worn button/audio path supplies the moment, the Mac supplies inaccessible visual context, and the relay makes the record retrievable when the owner is away.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime model handles the immediate marker acknowledgment and entity/time normalization; a cheaper background model performs transcription, screen/browser summarization, indexing, and later retrieval.
- **latency:** Acknowledge the mark in under 500 ms; capture can complete asynchronously within 10 seconds. Retrieval should return a spoken answer in 2–4 seconds.
- **cost:** About $0.01–$0.05 per marked minute plus a few cents per retrieval, dominated by audio transcription and optional screen image/OCR processing.
- **security:** Audio and screenshots may contain private material and leave the device to the relay. Encrypt records, retain only an owner-configured window, visibly indicate capture with the LED, and never capture continuously—only on explicit button/voice trigger.
- **missing:** A pendant event/audio upload endpoint that accepts a bounded clip; A Mac snapshot endpoint returning active-window metadata and an optionally user-enabled screenshot; An encrypted episodic index with time/source citations and deletion; A joiner that correlates pendant timestamps with Mac/browser state

### "“I’m leaving—give me a handoff.” The pendant should ask the Mac and browser for a fresh departure snapshot: unsaved work, running long jobs, active calls, private tabs, and anything that will need attention when I return, then speak a prioritized 20-second checklist."
- **useful because:** Today the owner can walk away from the Mac without knowing whether work is still running or a call/document is exposed. This turns the worn device into a reliable boundary between physical presence and unattended-machine state, using each node’s unique reach.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime model conducts the short spoken exchange and compresses results; cheaper background classification extracts unsaved/risky/long-running state from structured Mac and browser reports.
- **latency:** Snapshot collection under 3 seconds and spoken summary under 8 seconds; stale or unavailable surfaces must be explicitly named rather than silently omitted.
- **cost:** Usually under $0.02 per invocation; most cost is one short realtime turn, with no screenshot processing unless a state is ambiguous.
- **security:** The report can reveal sensitive tabs and documents over audio. Require the pendant’s physical trigger or explicit wake phrase, redact titles by default, support a private LED/vibration-only mode, and discard the snapshot after delivery unless the owner saves it.
- **missing:** A single authenticated departure-snapshot contract spanning Mac and browser; Mac inspection of unsaved documents, active calls, and process/job state with freshness timestamps; Browser extension report of tabs with sensitivity labels and pending downloads; A relay aggregator that distinguishes offline, stale, and confirmed-clear states

### "“Check this before I send it.” Without changing anything, have the pendant inspect the focused draft on the Mac or browser, compare recipients, attachments, links, and claims against the surrounding document/context, and speak only concrete risks and a one-sentence suggested fix."
- **useful because:** A wearable can catch the expensive mistake at the last second even when the owner is not staring at the screen. The browser session knows authenticated recipients and attachments, the Mac knows the focused app/document, and the relay provides a fast spoken second opinion without taking over or silently sending.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime model performs intent recognition and delivers the concise risk summary; a cheaper structured/background model extracts draft, recipient, attachment, and link facts and runs deterministic checks before the realtime explanation.
- **latency:** Collect evidence in 2 seconds and answer in under 5 seconds for ordinary drafts; if evidence is stale or inaccessible, say so instead of guessing.
- **cost:** Roughly $0.02–$0.08 per review, dominated by secure draft extraction and one realtime response; deterministic checks should avoid unnecessary model calls.
- **security:** Drafts, recipients, and attachments are highly sensitive. Keep raw content on the Mac/extension where possible, send only hashes/extracted facts to the relay, encrypt any temporary payload, never auto-send or edit, and visibly state which surfaces were actually inspected.
- **missing:** A read-only focused-draft adapter for common Mac apps and browser compose surfaces; A browser-extension inspection API for recipient/attachment/link metadata with session affinity; Deterministic checks for wrong recipient, external domain, secret/token patterns, broken links, and attachment mismatch; A provenance-bearing relay response that reports inspected timestamps and unavailable surfaces

### "“Can I merge this?” From the focused repository and current diff, have the Mac run the relevant tests and inspect the actual changed files, then have the relay speak a short merge-readiness report: failing evidence first, behavior risks second, and exact commands or files behind each claim."
- **useful because:** The owner can get a trustworthy engineering checkpoint while away from the keyboard instead of relying on a green-looking editor or memory. The Mac has the repository and test runtime; the relay and pendant make the result available during a walk; the report is grounded in executable evidence rather than a generic code opinion.
- **path:** pendant → relay → mac-planner → mac-terminal → mac-vision → dashboard
- **model tier:** Use a cheaper background planner for repository/test discovery and deterministic diff/test collection; reserve realtime for interpreting the collected evidence and speaking the compact result.
- **latency:** Start immediately, provide an audible 'testing started' acknowledgment within 500 ms, and deliver a first result within 30 seconds; long suites should return incremental completed/failed counts rather than blocking.
- **cost:** Typically $0.03–$0.15 per review, dominated by test execution and a short synthesis; no screenshot cost unless the focused diff is only visible in a GUI.
- **security:** Source code and test output may contain secrets or proprietary data. Keep execution on the Mac, redact credentials and unrelated files, include exact evidence paths and timestamps, and never merge, push, or mutate the repository without a separate explicit command.
- **missing:** A Mac-terminal job endpoint that runs a bounded test plan and streams typed progress; Repository/diff identity and clean-worktree checks in the result; A relay job-to-pendant progress and completion channel; A synthesis format that separates observed test evidence from model risk judgments


## What it asked for

_Nothing._
## Its own summary

Recorded four owner-facing capabilities: explicit pendant “mark this moment” capture with Mac/browser provenance; a spoken departure handoff for unattended Mac/browser state; read-only pre-send risk review of focused drafts; and evidence-backed voice merge-readiness checks from the repository. The haptic hardware idea was correctly rejected as already present in the backlog, so I did not rephrase it. What remains needed is implementation of the cross-surface joins: bounded pendant capture and event delivery, fresh Mac/browser snapshot adapters, encrypted cited episodic indexing, a provenance-aware pre-send inspection path, and a streamed Mac test/job channel that can report progress and completion back to the wearable.

**Biggest unknown:** Whether the existing Mac/browser routes expose enough focused-window, draft, repository-diff, and test-progress data to implement these joins without adding new local-agent adapters; I did not perform further discovery per instruction.

