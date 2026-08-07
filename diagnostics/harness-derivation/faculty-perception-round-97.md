# Harness derivation — faculty-perception — round 97

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/browser perception at round 97** — At 2026-08-07T14:19Z, home-macbook-bridge is online and relay reachable, but browser extension home-chrome is offline with 10 pending commands. /observe exposes three durable browser sessions with stable session IDs and tab/window IDs plus URL/title/lastUsedAt, but /browser/inspections is empty and no content hash/freshness assertion exists. Mac UI perception is not trustworthy: Accessibility trusted=false, Screen Recording=false, inputReachability=failed; foreground app is Claude (pid 55646).
  - evidence: GET /ops/status, GET /observe, GET /browser/status, GET /browser/sessions, GET /browser/inspections all returned HTTP 200 on 2026-08-07T14:19Z.

## Capabilities it proposed

### "Before you act, tell me what is actually true right now across my Mac, browser, relay, and pendant—and distinguish observed facts, stale evidence, and things you cannot verify."
- **useful because:** Prevents the system from treating queued browser commands, stale tabs, simulated pendant telemetry, or GUI receipts as current reality. It gives the owner an honest operational picture and gives action-gating a machine-readable basis for refusing unsafe assumptions.
- **path:** relay-realtime → mac-planner → browser-extension → mac-vision → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Background/cheap model compiles structured observations; realtime is used only when the owner asks by voice. No expensive model is needed for timestamps, heartbeats, IDs, and hashes; escalate to a stronger model only to reconcile contradictions.
- **latency:** Under 2 seconds for a cached snapshot; up to 10 seconds when requesting fresh browser heartbeat and Mac observation. If a surface is offline, return immediately with its last-seen age rather than waiting.
- **cost:** Usually negligible (route calls and hashing); occasional small model call for contradiction explanation. Dominant cost is only when summarizing many heterogeneous observations.
- **security:** Private tab URLs/titles and device identifiers remain in the local relay/agent projection; page contents must not leave the Mac unless explicitly requested. Never claim a GUI action succeeded from an untrusted receipt. Require confirmation for any action whose precondition is stale, missing, or contradictory.
- **missing:** A durable perception-snapshot schema with per-fact observedAt, expiresAt, source, identity, confidence, and optional content hash; Browser heartbeat reconciliation that clears or quarantines the 10 pending commands when home-chrome reconnects; Content-level browser inspection/hash endpoint; current /browser/inspections is empty and /observe has metadata only; A real pendant registration and delivery acknowledgement; current pendant-shaped pipeline records are historical, not live; A contradiction policy consumed by faculty-judgement/action (unknown is not false, and stale is not current)

### "When you tell me something about my world, let me ask “why do you believe that?” and get an evidence chain: the exact device/session observation, when it was seen, what was inferred, what was not observed, and which alternative explanations remain."
- **useful because:** Today the owner cannot audit the boundary between a live observation, stale telemetry, and an agent inference. A provenance challenge would make the system trustworthy: instead of merely hearing a conclusion, they could inspect the basis and catch a dead browser, historical pendant event, or unverified GUI receipt before relying on it.
- **path:** faculty-perception → faculty-judgement → relay-realtime → mac-planner → browser-extension → mac-vision → faculty-action
- **model tier:** Use deterministic structured records for the evidence chain and a cheap text model only to explain it in plain language. Reserve the realtime tier for speaking the explanation when asked through the voice path.
- **latency:** Return the structured chain in under 1 second from stored observations; allow up to 5 seconds for bounded revalidation of the relevant surface. If revalidation cannot happen, say so rather than silently refreshing or inventing evidence.
- **cost:** Low: hashes, timestamps, IDs, and relationship traversal dominate; a short explanation is a small background-model call. No page content needs to be sent to a model unless the owner explicitly asks for interpretation.
- **security:** Evidence may contain private URLs, tab titles, calendar/mail metadata, or device identifiers. Keep raw observations local to the owning surface, expose redacted snippets and hashes by default, and require explicit confirmation before revealing authenticated page content. Never present an inference as an observation.
- **missing:** A durable assertion ledger linking every user-visible claim to source observations and inference steps; A typed distinction between observed, derived, assumed, stale, contradicted, and unknown; Stable evidence references across relay, Mac jobs, browser sessions, and pipeline events; A user-facing voice/dashboard query that retrieves the chain for the immediately preceding claim; Retention and redaction rules for private evidence and expired assertions


## Changes it proposed to its own stack

### `integration` — Add a perception lease/contradiction layer between observation routes and action planning. Each observation gets a signed lease containing source identity (Mac PID/bundle, browser session+tab+window, relay device), observedAt, maxAge by fact type, and content/metadata hash when available. Before planning or executing, compare the lease to a fresh /observe, /browser/status or heartbeat, /browser/sessions, and relay/pipeline state; mark facts current, stale, contradicted, or unverifiable. A stale or contradicted lease must downgrade the plan to read-only or request confirmation. Persist the decision and evidence IDs in the job receipt.
- **owner gets:** The owner stops hearing confident claims based on a dead browser extension, old tabs, or a GUI action that only returned a false success. They get a clear reason for every pause: what changed, how old the evidence is, and what must reconnect before continuing.
- effort: Medium: shared schema, TTL policy, hash calculation, and planner/action middleware; tests for offline/reconnect/race conditions.  ·  risk: Overly short TTLs could make harmless tasks feel blocked; recover by using fact-specific TTLs and an explicit refresh attempt. Clock skew or reconnect races could create false contradictions; use server receipt time and monotonic sequence numbers where available.
- cost: Negligible storage/CPU for hashes and leases; no additional model call in the common path.  ·  latency: Normally one local validation pass; at most one bounded refresh round trip when a lease is near expiry.
- security: Improves safety by preventing stale/private data from being acted on. Lease records must redact page content and avoid exporting authenticated URLs beyond the local agent/relay trust boundary.
- depends on: Browser heartbeat/queue reconciliation for home-chrome; A live pendant registry and delivery acknowledgements; Browser content inspection or normalized page hash endpoint; Faculty-judgement/action middleware that actually honors a refused or downgraded lease


## What it asked for

_Nothing._
