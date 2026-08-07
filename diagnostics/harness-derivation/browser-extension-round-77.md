# Harness derivation — browser-extension — round 77

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser extension connectivity** — At round 77, /browser/status and /ops/snapshot report only home-chrome offline with no tab, while pendingCommands=5; Safari 26.5.2 is absent from the live device list despite prior registration.
  - evidence: GET /browser/status HTTP 200: online=false, devices=[home-chrome offline], pendingCommands=5; GET /ops/snapshot reports identical browser state.

## Capabilities it proposed

### "“Is this private webpage right? Compare the amount, date, or status on the page I’m viewing with my local records, tell me what matches or conflicts, and prepare a sourced note—don’t change anything.”"
- **useful because:** The browser alone can see the logged-in source and the Mac alone can see local Mail, Calendar, Notes, or files, but neither can reliably reconcile them. The owner gets a quick answer to high-consequence everyday checks (invoice, appointment, reservation, account status) with evidence instead of manually copying values between apps.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a cheaper background/text model for extraction, normalization, and conflict comparison; use realtime only to clarify the owner's target fields and speak the concise result. Escalate to the expensive model only when evidence conflicts or the page structure is ambiguous.
- **latency:** 5–10 seconds for already-open page plus local records; up to 30 seconds when navigating authenticated origins. Speak an immediate acknowledgement from the pendant, then deliver a compact result with source links and timestamps.
- **cost:** Usually low: one extraction/comparison text call plus local/browser reads; realtime tokens dominate only the spoken interaction. No browser screenshot upload unless DOM text extraction fails.
- **security:** Private page text and selected local records leave their respective devices only to the relay/model for comparison; minimize to requested fields and retain provenance. Never infer equality from stale records; show age and timezone. This is read-only and needs no confirmation, while any later edit remains a separate explicit action.
- **missing:** A field-targeted cross-surface comparison orchestrator that accepts a page/tab and local-source selectors; Freshness-aware normalization for money, dates, timezone, and status values; A compact evidence packet with quoted snippets, URL/app source, timestamps, and conflict explanations; Working browser enqueue plus a live Safari tab/heartbeat; currently /browser/status reports only offline home-chrome and five pending commands

### "“Read and explain the private page I’m looking at, but keep the page contents on my Mac; send only the short answer and the source pointer to my pendant.”"
- **useful because:** The owner can ask about sensitive logged-in material hands-free without exporting an entire page to the relay or a hosted model. The browser contributes the authenticated view, the Mac performs extraction and summarization locally, and the pendant delivers only the requested answer. This is materially different from merely reading a page or watching it: privacy boundaries are part of the user-visible promise.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a local Mac model or local extraction first; use the realtime tier only for the brief spoken exchange. A hosted fallback must be opt-in per request, not automatic.
- **latency:** Under 8 seconds for an already-open page and a short question; up to 20 seconds for a long page or local model cold start.
- **cost:** Near-zero relay/model cost in the normal path; local inference and browser extraction dominate. Hosted fallback, if explicitly enabled, costs one small text request plus speech tokens.
- **security:** Page DOM, screenshots, cookies, and extracted text remain on the Mac. The relay receives only a short answer, source URL/title, and freshness timestamp. The Mac must enforce this boundary rather than relying on prompt instructions; screenshots and raw extraction should be ephemeral and deleted after the answer.
- **missing:** A local-only browser read/summarize route that passes DOM text directly to the Mac planner without relay serialization; A browser selection/region protocol so the owner can scope the explanation to the visible section or selected text; A capability-level data-egress flag surfaced in job receipts and the pendant UI; A functioning browser enqueue path and a live Safari heartbeat/tab so the authenticated source can actually be reached


## Changes it proposed to its own stack

### `browser-harness` — Add a browser-device lease reconciler and queue health state machine. Track each extension's heartbeat lease and generation; when a device disappears or changes identity, immediately mark its queued commands as pending-device (not executing), cancel the 45-second waiter with a typed offline result, and emit progress/health events. On a later heartbeat, reconcile by generation: discard expired non-idempotent commands, replay only content-addressed/idempotent reads against the new tab/session when affinity still matches, and surface the rest as resumable jobs. Expose queue depth, oldest command age, device lease expiry, and replay/discard reason in /browser/status and job receipts. Do not add approval gates.
- **owner gets:** A spoken request to read a private page will fail in seconds with an honest explanation instead of hanging 45 seconds and leaving five invisible commands queued. If Safari reconnects, safe reads continue automatically rather than being lost or duplicated; the owner can see exactly what was replayed or discarded.
- effort: Medium: browserBridge lease/generation state, nonblocking waiter/progress events, result typing, and status/receipt fields; extension heartbeat handling needs a small reconnect test matrix.  ·  risk: A stale read could be replayed against the wrong tab if affinity checks are weak; require matching extension generation plus tab/session identity, otherwise discard and report. A device crash during a mutation remains non-replayable and must be surfaced, never guessed complete. Recovery is explicit retry after the owner reopens a tab.
- cost: Negligible API cost; reduces wasted model and HTTP wait time. Small local JSON/job-state growth for lease and replay metadata.  ·  latency: Offline detection becomes heartbeat-lease latency (target 5–10s) rather than 45s; connected reads unchanged.
- security: Improves isolation by preventing commands from crossing browser-device generations or tabs. Retain existing maximum-access/no-gate policy; this is observability and correctness, not refusal.
- depends on: chg-14accc01's existing request IDs, tab/session affinity, and idempotency keys; chg-16bc5dee's durable browser job runner or equivalent resumable job records; A functioning browser command enqueue implementation and Safari extension heartbeat restoration

### `browser-harness` — Add an enforceable local-only data-egress mode for browser jobs. A job declares its privacy mode at creation; in local-only mode, the browser bridge returns extracted text to the Mac agent over the local bridge, the relay adapter rejects raw DOM/screenshot/page payloads, and receipts contain only a hashed source identifier plus answer metadata. Add an ephemeral in-memory buffer with byte/time limits and wipe it on completion, cancellation, or device loss. Make the active mode visible in the pendant response and dashboard.
- **owner gets:** The owner can safely ask questions about banking, health, work, or other logged-in pages without having to trust that a prompt will prevent raw page contents from leaving the Mac. They get the convenience of spoken answers with a concrete, enforceable privacy guarantee.
- effort: Medium-high: add privacy-mode propagation through browserBridge, research/orchestration, relay serialization, receipt redaction, and failure-path tests including screenshots, retries, and crashed jobs.  ·  risk: A bug could accidentally leak content or erase evidence needed for debugging. Default local-only jobs to fail closed when the mode cannot be honored, retain only hashes and timing diagnostics, and provide an explicit owner-selected hosted mode for cases where local inference is insufficient.
- cost: Normal path avoids hosted text and vision API costs; local CPU/RAM use increases. Small implementation cost for ephemeral buffers and receipt metadata.  ·  latency: Adds local extraction and serialization checks, likely tens of milliseconds; local model cold starts may add seconds. Hosted mode remains available when explicitly selected.
- security: Strongly improves confidentiality by making egress a machine-enforced invariant rather than an instruction to the model. Requires careful scrubbing of logs, error messages, pending-command payloads, and crash dumps.
- depends on: A functioning browser enqueue implementation and restored Safari heartbeat; A local Mac summarization/extraction path; Relay and receipt serializers that understand privacy mode


## What it asked for

_Nothing._
