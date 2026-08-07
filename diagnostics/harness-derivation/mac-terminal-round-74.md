# Harness derivation — mac-terminal — round 74

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent readiness and browser reliability** — Live /ops/status reports version 0.5.0, fullControlMode=true, relay reachable and mac bridge online, but browser extension offline with 5 pending commands; Accessibility and Screen Recording are not granted, computer-use loop disabled, and agent ready=false despite requiredMissing=[]; /logs shows repeated browser failures taking ~45 seconds.
  - evidence: GET /ops/status and GET /logs probes in Round 74

## Capabilities it proposed

### "“Tell me which parts of my AI assistant were slow or unreliable today, what they cost, and automatically improve the routing for tomorrow without changing what actions it is allowed to take.”"
- **useful because:** Today the owner can see individual job receipts, but cannot get a trustworthy cross-surface reliability/cost diagnosis. The live data already shows a serious blind spot—112 of 120 jobs lack tier attribution—and repeated browser failures consume about 45 seconds each. A daily report would turn invisible waste into concrete improvements while preserving the owner's maximum-access policy.
- **path:** relay → mac-planner → browser-extension → pendant → dashboard
- **model tier:** background for aggregation and anomaly explanation; deterministic code for latency, failure, tier-attribution, and retry statistics; planner only if the owner asks for a natural-language investigation
- **latency:** Daily report under 10 seconds from cached journal data; interactive drill-down under 3 seconds. No low-latency voice model needed unless the owner asks verbally.
- **cost:** Near-zero model cost for the normal report because metrics and thresholds are deterministic; approximately 2k–4k input tokens to background model only when generating a concise explanation. Dominant cost is local aggregation, not inference.
- **security:** Keep command text, URLs, tab titles, and receipt evidence on the Mac by default; send the relay only aggregate counts, durations, failure classes, and model-token totals. Require explicit owner confirmation before applying any routing-policy change, and retain the previous policy for rollback.
- **missing:** A durable normalized event schema joining job receipts, journal entries, routing receipts, and browser heartbeat periods by request/job/action ID; A cost attribution fallback for jobs currently marked unattributed, with an explicit unknown bucket rather than fabricated prices; A deterministic policy simulator that can compare routing changes against the last 7 days before activation; A dashboard/pendant report and rollbackable routing-policy store

### "“When something fails, tell me in one sentence what stopped it, show me the evidence if I ask, and tell me the fastest safe way to continue—without making me repeat the whole request.”"
- **useful because:** The owner currently gets surface-specific errors such as “browser extension offline,” but not a causal explanation spanning relay, planner, Mac permissions, queue state, and browser heartbeat, nor a resumable continuation. This would convert a failed request into an actionable handoff instead of a dead end.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic causal-chain assembly and recovery classification first; background model for a short spoken explanation; planner only for genuinely ambiguous fallback choices.
- **latency:** Under 2 seconds for the first spoken diagnosis using existing receipts and status caches; evidence drill-down under 5 seconds. Resume should reuse the existing job/request ID rather than re-plan from scratch.
- **cost:** Usually no model call for diagnosis; under 1k background-model tokens for phrasing. Main cost is a durable causal event index and status sampling.
- **security:** Evidence may contain private URLs, text, or application names. Keep detailed capsules on the Mac and expose redacted summaries to the relay/pendant by default. Never infer that a failed write had no effect unless its receipt proves that; distinguish unknown outcome from confirmed no-op.
- **missing:** A durable causal chain linking request, routing decision, job, action receipt, browser heartbeat, permission snapshot, and terminal outcome; A resumable checkpoint format that records completed actions and explicitly excludes uncertain writes; A fallback registry describing alternatives by required surface and privacy boundary; A redaction layer for spoken relay summaries and owner-requested evidence


## Changes it proposed to its own stack

### `browser-harness` — Add a health-aware browser command circuit breaker and queue reconciler. Before dispatch, consult the extension heartbeat/status; if offline or heartbeat stale, fail locally within ~1 second with a structured OFFLINE_BRIDGE result instead of waiting ~45 seconds. Mark queued commands as blocked (not failed), coalesce identical retries by idempotency key, and automatically resume only after a fresh heartbeat. Include bridge last-seen age, pending-command count, and a single reconnect instruction in the receipt and relay/pendant notification.
- **owner gets:** Browser requests stop hanging for nearly a minute and repeatedly producing the same failure. The owner gets an immediate, truthful explanation and can fix Safari once; queued work is not silently lost and resumes when the bridge returns.
- effort: Medium: bridge heartbeat freshness check, queue state transition, retry coalescing, receipt fields, and relay notification.  ·  risk: A stale heartbeat could falsely declare the bridge offline; use a short grace period and allow an explicit force-retry. Reconciliation must preserve idempotency so a resumed write cannot run twice. Recovery is automatic on the next heartbeat.
- cost: Negligible API cost; saves planner and Mac-agent time otherwise spent on 45-second failed browser calls.  ·  latency: Offline detection under 1 second; online actions unchanged except for one heartbeat check.
- security: No new data leaves the Mac. Status metadata (extension id, last-seen time, pending count) may reach relay and should omit URLs/tabs unless already present in the action receipt.
- depends on: Existing browser heartbeat/status and durable command queue (chg-14accc01 / chg-16bc5dee); A queue state that distinguishes blocked/offline from failed; Relay/pendant delivery of structured job failure notifications

### `dashboard-ux` — Build a capability-readiness matrix fed by /ops/status, /browser/status, relay health, and pendant connectivity. Show each surface's usable operations (shell, AppleScript, browser, vision, audio) with live states, last-seen timestamps, missing macOS permissions, and the exact user action to restore them. Distinguish 'requiredMissing: []' from 'ready: false' and explain that Accessibility/Screen Recording are currently unavailable; do not block execution, just annotate receipts and proactively notify the pendant when a requested operation depends on an unavailable capability.
- **owner gets:** Today the agent reports ready=false while requiredMissing is empty, browser is offline, and vision consent/permissions are missing—an owner cannot tell whether a request failed because of the task or the machine. One glance or a spoken status answer would explain what to fix instead of repeated blind retries.
- effort: Medium: normalize status payloads, add operation-to-dependency mapping, dashboard cards, and a compact relay/pendant status event.  ·  risk: Permission details are sensitive and stale status could mislead; show timestamps and uncertainty, refresh on demand, and never claim a capability is usable without a successful probe.
- cost: No model cost; small local UI and status polling overhead.  ·  latency: Status checks are local and can be cached; no impact on normal action execution.
- security: Keep permission/status data local by default; relay only coarse states (browser offline, Mac unavailable) unless the owner asks for diagnostics.
- depends on: /ops/status and /browser/status read-only endpoints; Typed operation dependency registry for shell/browser/vision/audio; Dashboard and relay status-event support


## What it asked for

_Nothing._
