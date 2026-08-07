# Harness derivation — mac-terminal — round 90

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac execution readiness and recovery** — At 2026-08-07T13:03Z the local agent and relay are reachable, but agent ready=false because Accessibility and Screen Recording are not granted; computer-use loop is disabled, browser extension is offline with 7 pending commands, and journal reports 120 retained jobs / 146 actions / 16 failed / 0 undoable / 112 unattributed tier.
  - evidence: GET /ops/status and GET /journal returned these live values.

## Capabilities it proposed

### "“If my Mac or browser connection is unhealthy, keep my request moving where it can, tell me what could not run, and retry the missing Mac steps when it recovers.”"
- **useful because:** Today the relay is reachable while the Mac reports not-ready (Accessibility and Screen Recording are missing), the browser extension is offline with 7 queued commands, and recent browser navigations spent about 45 seconds timing out. The owner should get useful public/reasoning work immediately instead of a silent failure, plus a precise recovery rather than manually repeating the whole request.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic health/circuit-breaker and retry planner first; gpt-4.1-mini in background for summarizing partial results and deciding safe retry ordering; realtime only to narrate a short status when the owner is waiting.
- **latency:** Health preflight under 300 ms from cached heartbeats; immediate partial result in 2–5 s; recovery retries are background and should not block the pendant conversation. Browser commands must expire or be revalidated before replay, not blindly drain the stale queue.
- **cost:** Usually near-zero for preflight, queue, and routing; roughly 2k–4k input tokens per failed multi-step request when a background model summarizes partial completion. Realtime cost occurs only for the spoken interruption/status.
- **security:** Health telemetry stays local/relay metadata; private browser page contents never go to the public fallback. A retry must bind to the original tab/session, verify URL and a fresh page fingerprint, and omit irreversible actions unless the owner explicitly asks again. The owner permits unrestricted Mac execution, so this is observability/recovery rather than a new gate.
- **missing:** A single preflight contract combining relay heartbeat, Mac readiness/permission state, browser online state, and pending-command age; Circuit-breaker states and per-step capability requirements (Mac shell, GUI, authenticated browser, public web); Stale-command quarantine with idempotency-aware replay and page/session revalidation; A durable partial-result/retry plan linking relay job IDs to local job receipts and pendant notifications

### "“When something failed, tell me whether it is safe to retry, what already happened, and retry only the missing pieces.”"
- **useful because:** The current receipts can say an action failed and whether it is undoable, but they do not provide a durable, owner-facing retry decision for a partially completed multi-surface goal. This matters because the job store shows 77 write actions, 16 failures, and zero undoable actions; blindly repeating a request could duplicate work.
- **path:** pendant → relay-realtime → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic receipt/effect analysis for known action types; background gpt-4.1-mini only to summarize an ambiguous partial state; realtime only when the owner asks aloud.
- **latency:** Under 1 s for known receipt chains; under 5 s for an ambiguous cross-surface summary. Retry execution remains asynchronous and reports progress through the pendant.
- **cost:** Near-zero for typed receipt analysis; 1k–3k background input tokens only when effects cannot be reconciled deterministically.
- **security:** Do not infer success from a timeout. Require fresh before-state evidence for browser and filesystem operations, preserve private page data on the local path, and present a concise list of potentially duplicated effects before any replay. This adds explanation and recovery, not an approval gate.
- **missing:** Effect-aware retry planner that understands completed, failed, timed-out, and unknown actions; Cross-surface receipt graph joining relay request, local job, browser command, and evidence capsule IDs; Owner-readable duplicate-risk and retry-scope response, with a dry-run replay preview; Persistent retention of the minimal receipts needed after the 120-job rolling store evicts old jobs

### "“Save what I’m looking at right now for me, with enough evidence that I can trust it later, and let me pick it back up from the pendant without reopening the page.”"
- **useful because:** Today the browser can inspect or capture a page and the Mac can run jobs, but there is no owner-facing handoff object that preserves the exact authenticated tab state, a compact local evidence bundle, the owner’s spoken note, and a resumable follow-up across devices. This would turn an ephemeral browsing moment into a reliable personal queue without sending private page contents through the relay.
- **path:** browser-extension → mac-planner → relay → pendant → dashboard
- **model tier:** Deterministic capture and provenance first; background gpt-4.1-mini optionally labels and compresses the evidence; realtime only reads a short queued item or records the owner’s note.
- **latency:** Capture acknowledgement under 2 seconds; evidence packaging under 10 seconds; pendant playback starts from a compact summary while the full bundle remains local.
- **cost:** Near-zero for tab metadata, DOM excerpt hashing, local encrypted storage, and queueing; about 1k–3k background input tokens only when the owner asks for a generated summary.
- **security:** Authenticated page text, screenshots, cookies, and URLs stay on the Mac/browser side; the relay carries only an opaque item ID, short owner note, status, and optionally a redacted summary. Bind the bundle to tab/session identity, show source URL and capture time, and expire or delete it on request.
- **missing:** A first-class cross-device handoff object linking browser tab/session, local evidence files, spoken note, and resumable follow-up state; Local encrypted evidence bundles with content hashes and DOM/screenshot provenance, separate from the rolling job store; Relay APIs for opaque handoff IDs, pendant queue/playback, and later resume requests; A browser command that freezes a coherent page snapshot (metadata, selected content, screenshot, and page fingerprint) atomically


## Changes it proposed to its own stack

### `model-routing` — Add an execution-aware router that compiles a request into typed subgoals (local status, Mac shell/action, authenticated browser, public research, narration), consults live /ops/status and /browser/status before planning, and routes each subgoal independently. Cache deterministic Mac diagnostics and fail fast on an offline browser instead of spending a 45-second browser timeout; retain the full planner only for ambiguous joins. Attach the routing tier, subgoal ID, and outcome to every job receipt so the current 112 unattributed actions become attributable.
- **owner gets:** The pendant answers faster and more reliably: a browser outage no longer stalls unrelated Mac work, repeated battery/Wi-Fi questions do not pay planner tokens, and the owner receives one coherent answer from whatever parts actually worked.
- effort: Medium: define subgoal schema, health capability matrix, planner handoff, and receipt propagation across relay and local agent; add replay tests for partial failure.  ·  risk: A compiler could split a task incorrectly or report a partial answer as complete. Recover by preserving the original goal, requiring a join step to mark completion, and falling back to the existing planner when confidence is low. No action is blocked; this only changes planning and observability.
- cost: Reduces planner calls and repeated timeout retries; expected savings are material given the observed 28,971 planner-tier tokens across 3 requests and 16 failed actions. Small deterministic CPU/storage overhead.  ·  latency: Health check <300 ms; independent subgoals can run concurrently. Failed browser work returns in seconds rather than ~45 seconds, while complex tasks may add a short join step.
- security: Private tab data remains in the browser/local path; only typed status and provenance cross the relay. Existing unrestricted Mac execution policy remains unchanged.
- depends on: A shared subgoal/job schema across relay and local agent; Capability requirements and health preflight described in the recovery proposal; Receipt attribution for every action and routing tier


## What it asked for

_Nothing._
## Its own summary

Live discovery found a concrete reliability gap: relay and local agent are reachable, but Mac readiness is false (Accessibility and Screen Recording missing), browser bridge is offline with 7 queued commands, and recent browser navigations repeatedly consumed ~45 seconds before failing. Journal shows 120 retained jobs, 146 actions, 16 failures, zero undoable actions, and 112 actions without routing attribution. I recorded this finding and proposed (1) an execution-aware subgoal router that uses health preflight, parallelizes independent Mac/browser work, fails fast, and attributes every receipt, and (2) a cross-surface effect-aware retry explanation that distinguishes completed/failed/unknown work before replay. These preserve the owner's maximum-access/no-gates policy.

**Biggest unknown:** The implementation contracts between relay request IDs, local job IDs, browser command IDs, and evidence capsules are still not exposed as one shared schema. I still need that contract (or an implementation of it), plus stale-queue expiry/revalidation semantics; I do not need more permissions or another shell tool this round.

