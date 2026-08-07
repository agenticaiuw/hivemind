# Harness derivation — browser-extension — round 15

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser command execution** — The granted browser_enqueue_command_implemented tool is still an unimplemented stub, so I cannot dispatch navigate/read/click commands even though browser status/context says Safari can bootstrap a tab via browser_navigate.
  - evidence: Tool call returned: 'This tool was granted a schema but has no implementation yet. Report what you would have done with it.' Direct probe /browser/status and /execute also returned fetch failed.

## Capabilities it proposed

### "Watch the authenticated pages I choose, detect meaningful changes, and leave me a concise, sourced briefing with suggested next steps—without sending or submitting anything."
- **useful because:** This turns the browser's unique access to logged-in portals into persistent value: the owner wakes to changes in work dashboards, ticket queues, benefits portals, or travel reservations rather than repeatedly checking them. Evidence and exact page snippets make the result auditable.
- **path:** browser → relay → dashboard
- **model tier:** A scheduled/background browser worker uses a cheap model for DOM diff normalization and priority ranking; realtime is used only if the owner asks follow-up questions by voice. A stronger model is invoked only for ambiguous changes.
- **latency:** Polling can be minutes to hours; a changed page should produce a ledger artifact within 1–3 minutes. Voice follow-up should feel realtime.
- **cost:** Low per watch: browser navigation/extraction dominates wall time; cheap model gets only normalized diffs, not whole pages. Roughly cents per daily watch depending on page size; cache stable DOM and redact unchanged sections.
- **security:** Authenticated content leaves Safari and enters the relay/ledger, so encrypt artifacts, minimize retention, and allow per-watch domain/field exclusions. Never auto-submit forms, send messages, or purchase; present proposed actions and exact payload for explicit confirmation. Beware pages that render a false change due to timestamps or ads.
- **missing:** A durable browser watch scheduler with per-watch cadence and state; DOM-aware diffing that ignores volatile elements and preserves citations; Shared task-ledger artifact schema consumed by Mac and relay; Encrypted, owner-visible retention and redaction controls

### "When I ask about something on a logged-in site, have several agents inspect it in parallel, reconcile their findings, and give me an evidence-backed answer or a prepared (not sent) action."
- **useful because:** Authenticated pages often contain fragmented information across dashboards, messages, and documents. Parallel browser extraction plus Mac-side computation can answer questions that a single page read cannot, while preserving the owner's control over consequential actions.
- **path:** browser → mac-bridge → relay → dashboard
- **model tier:** Use a cheap planner to decompose the question and cheap extractors for each page; use a stronger synthesis model only on the compact evidence set. Realtime handles only the spoken clarification and final response.
- **latency:** Parallel reads should complete in 10–30 seconds when sessions are valid; synthesis in another few seconds. If a page is slow, return partial results with explicit gaps rather than blocking indefinitely.
- **cost:** Lower than serial full-page prompting: parallel browser reads and cached normalized evidence, with synthesis seeing citations and diffs only. Typical request should be cents-scale, dominated by model input if pages are not aggressively reduced.
- **security:** The decomposition must not leak credentials or broaden scope beyond requested domains. Evidence can contain private data; encrypt it and expire it. For prepared actions, show target, exact fields, and side effects; do not submit/send/purchase without an explicit confirmation. Treat prompt injection in page text as untrusted data, never instructions.
- **missing:** Cross-surface job fan-out/fan-in orchestration; Browser evidence objects with URL, timestamp, region, and content hash; Prompt-injection-resistant extraction boundary; Owner-facing review UI for prepared actions

### "Prepare a browser transaction for me: gather the relevant logged-in data, fill the form or draft the message, show me exactly what will change with before/after evidence, and let me approve, edit, or discard it."
- **useful because:** This removes tedious form-filling while keeping the owner in control of irreversible actions. It also catches stale prices, wrong recipients, and hidden fields before anything is sent.
- **path:** browser → dashboard → relay → mac-bridge
- **model tier:** Cheap models extract fields and construct a structured draft; a stronger model validates cross-field consistency and summarizes risk only when needed. Realtime is reserved for spoken approval/editing.
- **latency:** Draft in 10–45 seconds depending on page complexity; preview updates after edits within a few seconds. Submission remains a separate explicit command.
- **cost:** Cents-scale for ordinary forms if the model sees field schemas and diffs rather than screenshots/full HTML. Browser interaction latency dominates; cache page state during the draft.
- **security:** Web pages may contain prompt injection and hidden fields. Treat all page content as untrusted, allow only user-requested target domains, expose every field/value and attachments in the preview, and refuse silent submission. Credentials and session tokens stay in Safari; redact sensitive values in logs. Confirmation must bind to the exact page hash and payload, invalidating if the page changes.
- **missing:** Structured form extraction and field-level before/after diff; Stable page hash plus stale-page invalidation; Dashboard review/edit/approve surface; Browser executor that can apply a reviewed payload atomically and return a receipt


## Changes it proposed to its own stack

### `browser-harness` — Build a first-class authenticated page-watch service: each watch stores URL/tab context, extraction selectors or semantic regions, a normalized baseline hash, volatile-field rules, cadence, and last successful session. On each run, capture a minimal diff with quoted evidence and provenance, publish it as an immutable artifact to the shared task ledger, and notify the relay only when a change crosses the owner's priority threshold. Add a recovery state when Safari has no tab or the session expires, rather than silently reporting no change.
- **owner gets:** The owner gets reliable monitoring of logged-in sites while asleep, with fewer false alarms and a clear audit trail. A disappeared Safari tab or expired login becomes an actionable alert instead of a missed deadline.
- effort: Medium-high: scheduler, browser bridge retries, DOM normalization, encrypted artifact storage, dashboard controls, and tests across Safari extension restarts.  ·  risk: Selectors can drift and create false negatives/positives; mitigate with semantic fallback extraction, baseline previews, and a visible 'watch degraded' state. A session-expiry screenshot or page content could be sensitive; encrypt, redact, and enforce retention.
- cost: Background extraction and cheap diff summarization cost modest API usage; storing only diffs is cheaper than full snapshots. Browser navigation remains the main latency/cost driver.  ·  latency: No impact on live voice. Change detection is eventual (target 1–3 minutes after a scheduled run); retries may take longer when Safari is asleep.
- security: Adds persistent access to logged-in pages. Encrypt watch configuration and artifacts, scope each watch to an explicit domain/path, and log every read. Keep mutation commands out of the watcher.
- depends on: Shared task ledger/artifact schema from mac-planner; Working browser command enqueue path and extension result delivery; Scheduler and encrypted retention/redaction controls

### `integration` — Define a cross-node Evidence Capsule protocol for browser results: immutable capsule ID, source URL/domain, capture time, tab/session identifier (pseudonymous), selected text/DOM region, content hash, redaction map, and confidence. Capsules are the only input exposed to synthesis and Mac actions; every derived summary/action receipt links back to capsule IDs. Add TTL and revocation so deleting a source removes downstream display while preserving an audit tombstone.
- **owner gets:** Answers become checkable instead of opaque: the owner can jump from a claim to the exact logged-in page excerpt, see when it was captured, and know whether a proposed Mac action used stale information.
- effort: Medium: shared schema, browser extraction changes, D1/R2 persistence, dashboard citation viewer, and propagation through Mac planner/action receipts.  ·  risk: Overly aggressive redaction can make evidence unusable; insufficient redaction can expose private data. Start with domain-specific sensitive-field rules, owner preview, and short default TTL. Hashes alone do not prove truth if the page is compromised, so preserve capture metadata and treat page text as untrusted.
- cost: Small storage and serialization overhead; compact excerpts and deduplication reduce model-token cost substantially versus resending pages.  ·  latency: Negligible on reads; citation indexing adds milliseconds to seconds. Synthesis gets smaller context and should be faster.
- security: Improves least-data sharing and auditability, but capsules become sensitive records. Encrypt at rest/in transit, restrict by owner and task, and never include cookies, tokens, or hidden form values.
- depends on: Shared task ledger/artifact handoff; Browser watch/read extraction returning stable regions; Dashboard citation and deletion controls


## What it asked for

_Nothing._
