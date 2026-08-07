# Harness derivation — mac-terminal — round 114

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac execution preflight health** — At 2026-08-07T14:30Z, /observe reports inputReachability failed and UI actions will reach nothing because Accessibility is not trusted for the running AI Pendant Agent binary; Screen Recording is also false. /ops/status reports browser extension offline with 10 pending commands and computer-use loop disabled. Recent browser_navigate failures consumed ~45 seconds each.
  - evidence: GET /observe, GET /ops/status, GET /jobs

## Capabilities it proposed

### "Why didn't that work?"
- **useful because:** When a computer task fails, the owner gets a concise, evidence-backed explanation instead of a generic error: which surface was selected, whether the bridge or permission was unavailable, how long it waited, what actually changed, and the safest alternative. This is especially valuable when GUI receipts say success but Accessibility means nothing reached the screen.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheap background/text model to summarize structured receipts; reserve realtime only for the spoken answer when the owner asks through the pendant.
- **latency:** Under 2 seconds from cached job/health data; at most one bounded local read if the relevant receipt is missing. Never rerun the failed action merely to diagnose it.
- **cost:** Usually <$0.01 per invocation; dominated by model summarization, with local observability reads negligible.
- **security:** Return only the owner's own job metadata and sanitized error details; redact command strings, URLs, page text, tokens, and file contents unless explicitly requested. Diagnosis must be read-only and must not imply that a failed or no-op action completed.
- **missing:** A stable failure-cause taxonomy linking receipt status, /observe health, bridge heartbeat, timeout, and permission state; A correlation ID from pendant request through relay job and Mac receipt; A compact dashboard/pendant rendering for health evidence and recommended next step

### "Find the current, canonical version of this thing across my Mac and logged-in browser, and tell me what conflicts."
- **useful because:** The owner often has the same document, order, reservation, or task in Downloads, an app, Safari, and an earlier pendant capture. Today each surface can inspect its own copy, but none can establish which one is authoritative. This would produce one answer with source links, timestamps, hashes or field-level differences, and an explicit uncertainty when the sources disagree—without silently editing or submitting anything.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheaper background model for extraction, normalization, and diffing; use the realtime tier only to answer the owner's spoken follow-up. Deterministic hashing and timestamp comparison should happen locally without a model.
- **latency:** 20–60 seconds for a bounded search of selected Mac folders/apps and up to four already-open authenticated tabs; stream progress to the pendant and stop early once one source is strongly authoritative.
- **cost:** Typically $0.01–$0.05, dominated by normalizing heterogeneous text; local hashes, metadata, and receipts are nearly free.
- **security:** Keep file contents and authenticated page text on the Mac/relay boundary, redact secrets from the spoken summary, and require explicit source selection before any later write. Never treat matching text as proof of authority when timestamps, ownership, or workflow state conflict.
- **missing:** A cross-surface canonicality resolver with source-specific authority rules (for example, submitted portal state over a local draft), field-level diffs, and confidence; Read-only Mac file/app adapters that return stable source IDs, modification times, and content hashes rather than opaque shell output; A privacy-preserving evidence bundle that can cite local paths and authenticated tabs without copying their full contents into long-lived memory


## Changes it proposed to its own stack

### `model-routing` — Add a low-cost, read-only capability preflight before planning or executing any Mac/browser action. Cache a short-lived health vector from /ops/status and /observe (shellReady, browserOnline/lastHeartbeat, accessibilityTrusted, screenRecording, visionConsent, pendingCommandCount). Route browser_* only when the extension is online and recently heartbeating; route GUI/vision only when Accessibility and Screen Recording are actually trusted; otherwise choose shell/AppleScript or return a truthful unavailable result immediately. Include the selected route and the health snapshot in the job receipt, and invalidate the cache on a failed action or bridge heartbeat timeout.
- **owner gets:** The pendant stops wasting nearly a minute on browser commands that cannot run and stops claiming GUI actions succeeded when macOS is silently ignoring them. When Safari is offline, it can tell you immediately or use a different path; when permissions are missing, it can say exactly which permission is needed.
- effort: Moderate: health-vector endpoint/cache, planner hook, route predicates, and receipt fields; no new model required.  ·  risk: A stale or incorrectly interpreted health snapshot could route to the wrong surface. Keep TTL short (5–10 seconds), recheck after failures, and fall back to the existing executor rather than blocking shell actions.
- cost: Negligible API cost; one local authenticated read per cache miss. Reduces expensive planner retries and 45-second browser timeouts.  ·  latency: Adds roughly 10–50 ms locally on cache miss and usually saves 45 seconds on known browser/GUI failures.
- security: Read-only status metadata stays local and is not uploaded; do not include URLs, page text, or screenshots in the health vector.

### `integration` — Create a cross-surface source-of-truth resolver between the existing Mac, browser, capture, research, and context-graph systems. It should accept a task object (entity type plus identifying fields), query bounded local and authenticated sources in parallel, normalize fields, compute local hashes and freshness, apply configurable authority rules, and emit a signed evidence bundle with per-field provenance and conflicts. Store only hashes, source references, and short-lived snippets; make the bundle consumable by pendant speech and dashboard review without copying private page/file contents into general memory.
- **owner gets:** They can ask for the current answer once instead of manually opening several copies and guessing which is stale. Conflicting dates, amounts, statuses, or versions become visible before the owner acts on the wrong one.
- effort: High: typed adapters for local files/apps and browser pages, normalization schemas, authority configuration, evidence-bundle persistence/expiry, and relay-to-pendant rendering.  ·  risk: An incorrect authority rule could label a stale source canonical. Start read-only, show all conflicts and confidence, allow per-entity overrides, and never perform a write based solely on the resolver.
- cost: Low recurring storage and hashing cost; roughly $0.01–$0.05 for model-assisted normalization when needed. Avoids resending full private contents on every turn.  ·  latency: Parallel bounded reads add 20–60 seconds for a search, but progress can stream and deterministic comparisons avoid extra model turns.
- security: Sensitive contents remain on-device or in an encrypted short-lived relay bundle; spoken output is redacted by default. Source IDs and hashes are safer than persisting raw documents.
- depends on: Stable correlation IDs across Mac jobs, browser commands, relay requests, and pendant turns; Read-only local source adapters that expose metadata and hashes; A typed authority/conflict schema and expiring evidence-bundle store


## What it asked for

_Nothing._
## Its own summary

Fresh live discovery completed. Mac agent is healthy and FULL_CONTROL_MODE remains intentionally unrestricted, but /observe shows Accessibility is not trusted for the actual AI Pendant Agent binary and synthesized UI events do nothing; Screen Recording is also absent, so computer-use is disabled/untruthful. Browser bridge is offline with 10 queued commands, and recent browser navigations spent about 45 seconds timing out. I recorded these findings, informed unified, proposed health-aware preflight routing, and proposed a cross-surface evidence-backed 'Why didn't that work?' diagnosis capability. What is still needed from the system is not another shell permission or gate: (1) grant Accessibility to /Users/evanliu/Applications/AI Pendant Agent.app and Screen Recording if GUI/vision is desired, (2) get the browser extension polling/heartbeat online and drain or reconcile its 10 pending commands, and (3) add correlation IDs and a failure-cause taxonomy so relay, Mac receipts, and pendant explanations agree. I will not re-request already queued permissions/tools.

**Biggest unknown:** Whether the owner intends to grant the host Accessibility/Screen Recording permissions and bring the browser extension online; without those, shell and AppleScript remain usable but GUI and authenticated browser automation cannot be truthfully offered.

