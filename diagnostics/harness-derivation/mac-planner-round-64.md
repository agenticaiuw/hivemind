# Harness derivation — mac-planner — round 64

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-planner live execution readiness** — Relay and Mac bridge are online, but browser extension is offline with 3 pending commands; Accessibility and Screen Recording are not granted, so computer-use vision/UI control is not ready. AppleScript automation domains are cached as granted, but the Mac agent reports ready=false. The newly granted mac_readonly_inspect tool has no implementation and returns an implementation error for all operations.
  - evidence: GET /ops/status returned fullControlMode=true, browser online=false/pendingCommands=3, accessibility.trusted=false, screenRecording.granted=false, ready=false; mac_readonly_inspect operations returned 'This tool was granted a schema but has no implementation yet.'

## Capabilities it proposed

### "“Handle this, and leave me proof of what you did.”"
- **useful because:** Today a request can fail because the browser is offline or Mac permissions are missing, and the owner has to repeat it without knowing which step actually happened. This would turn one spoken request into a resumable, cross-surface job: inspect the pendant context and current Mac/browser state, do only the reversible work, preserve before/after evidence, and speak a truthful one-sentence receipt. If a surface disappears, the relay keeps the checkpoint and resumes later instead of claiming success or losing the request.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the realtime tier only to capture the utterance and deliver the short receipt; use a cheaper background model for plan decomposition, evidence reconciliation, and retry classification.
- **latency:** Acknowledge on the pendant in under 1 second; first state inspection in 3–5 seconds; background execution can continue for minutes. On failure or offline surfaces, speak “paused at step N” immediately and resume when the device heartbeat returns.
- **cost:** Roughly $0.01–$0.05 per ordinary job, dominated by background model calls and any screenshot/page extraction; realtime cost is limited to two short utterances. Storage is small JSON receipts plus selected evidence snippets.
- **security:** Private browser pages and local UI state leave the Mac only as redacted evidence; secrets and full page bodies stay local. Never send mail, delete files, purchase, or submit forms without the owner’s existing confirmation policy. Each step needs an idempotency key and a visible target so retries cannot duplicate mutations.
- **missing:** A durable cross-surface checkpoint schema shared by relay, Mac executor, and browser session runner; Heartbeat-triggered resume with idempotency and explicit paused/blocked states; A local evidence bundle writer under ~/AI-Pendant-Workspace with redaction and retention controls; Dashboard and spoken receipt support for step-level outcomes, not just one final job status

### "“Bookmark this moment.”"
- **useful because:** The owner often encounters something worth returning to while wearing the pendant, but today there is no reliable bridge from that physical moment to the exact digital context on the Mac. A deliberate pendant button press would create a private, timestamped bookmark: optionally attach the owner’s short spoken label, capture the foreground app and the currently selected browser tab when available, and leave one linked note in ~/AI-Pendant-Workspace. Later they could ask “show me the moments I bookmarked about the contract” and get the original context rather than trying to reconstruct it from memory.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use firmware for the immediate button event and timestamp; use the relay’s cheaper background tier to normalize the label and classify it; use Mac/browser surfaces only for explicitly requested, foreground-context metadata. Realtime is unnecessary except for an optional short label transcription.
- **latency:** The pendant should acknowledge the bookmark locally in under 150 ms and survive a dropped link. Sync and Mac context capture can complete within 10 seconds when connected, or reconcile later without losing the event.
- **cost:** Typically below $0.005 per bookmark; dominated by optional speech transcription. Text-only bookmarks are essentially storage and transport cost. A compact event plus metadata should be under a few kilobytes.
- **security:** No passive microphone or continuous screen capture. Capture only after the physical bookmark action, with a configurable policy for whether the active URL/title is allowed. Keep page contents and sensitive URLs redacted or local; never capture passwords, form fields, or private page bodies by default. Provide local delete/export of each bookmark.
- **missing:** A pendant firmware bookmark event with a monotonic timestamp and offline queue; Relay ingestion and deduplication for bookmark events across reconnects; A Mac context snapshot endpoint that returns only foreground app and safe browser metadata; A linked local-note/index format and dashboard search for bookmark labels, timestamps, and source provenance


## Changes it proposed to its own stack

### `browser-harness` — Add a live capability preflight and fast-fail/queue path before browser_* execution. The Mac agent already reports browser online=false with 3 pending commands, while a failed navigate currently spends ~45 seconds before returning an error. On every browser job, bind it to the heartbeat/device, check extension freshness and tab/session availability, then either execute, enqueue durably with a paused receipt, or immediately report “blocked: browser bridge offline”; when heartbeat returns, resume idempotently and attach the result to the original job. Keep local Mac actions independent so a mixed job can continue its non-browser steps.
- **owner gets:** The owner stops waiting through long false starts and does not have to repeat browser requests. A spoken request can make progress on the Mac while the private browser portion waits safely, with one truthful completion receipt instead of scattered failures.
- effort: Medium: shared preflight contract in browserBridge/browserSessions, durable queue state and heartbeat resume, plus planner handling for mixed-step jobs and dashboard status.  ·  risk: A stale heartbeat could cause a job to resume against the wrong tab or duplicate a mutation. Require extensionId plus tab/session affinity, idempotency keys, and a fresh tab metadata check; if affinity changed, remain paused rather than guessing. Recovery is cancel/retry from the original checkpoint.
- cost: Negligible API cost; one lightweight heartbeat/status read per browser job and a small D1/local JSON queue.  ·  latency: Offline requests return in under 1 second instead of timing out after ~45 seconds; online jobs add only one status check.
- security: Improves safety by preventing actions from being sent into an unknown browser session. Private page contents remain on the browser/Mac path; queue metadata should contain only opaque session IDs and redacted intent.
- depends on: A durable browser job runner and command queue; Heartbeat events from the browser extension; The cross-surface checkpoint/idempotency schema proposed above


## What it asked for

_Nothing._
## Its own summary

Recorded a new capability: a deliberate pendant “Bookmark this moment” event that works offline, optionally accepts a short spoken label, and later links the timestamp to safe foreground Mac/browser context without passive recording. This is not in the existing backlog and requires new firmware, relay ingestion, context capture, and searchable local notes.

**Biggest unknown:** The exact pendant button/event interface and available offline flash budget for a durable bookmark queue.

