# Harness derivation — faculty-perception — round 24

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-ui-observability** — At 2026-08-07T10:09:16Z, Mac foreground app is Claude (com.anthropic.claudefordesktop), with 13 user apps running. Accessibility is untrusted for AI Pendant Agent, screen recording is not granted, input reachability failed, and uiActionsWillReachTheScreen=false; UI action receipts cannot be trusted until the host binary is granted Accessibility.
  - evidence: GET /observe HTTP 200 at 2026-08-07T10:09:16Z
- **fleet-connectivity** — At 2026-08-07T10:09Z, Mac bridge and relay are reachable, but the browser extension home-chrome is offline with 3 pending commands; computer-use loop is disabled and vision upload consent is false. Mac agent readiness is false despite automation grants because Accessibility and Screen Recording are missing.
  - evidence: GET /ops/status HTTP 200 at 2026-08-07T10:09Z
- **pendant-pipeline-history** — The pipeline contains offline-held pendant events: held alerts were surfaced from microSD, and a moment bookmark was captured while link_at_capture=down. A recent cloud-relay response was rendered as 24 kHz mono PCM (164650 bytes, 3430 ms) and accepted for pendant download.
  - evidence: GET /pipeline HTTP 200; runs and event metadata observed in response
- **capture-store** — The capture store currently contains two entries: one normal-sensitivity idea and one secret-sensitivity owner fact. Secret captures are present and must not be echoed into ordinary context or logs.
  - evidence: GET /capture HTTP 200

## Capabilities it proposed

### "Before you do anything on my behalf, tell me whether the connected devices can actually observe and reach the target, and after it runs tell me what was verified versus merely reported."
- **useful because:** Today the Mac can return apparent success while Accessibility/input reachability are false, the browser can be offline with queued commands, and the pendant can hold events while disconnected. A cross-device trust verdict prevents invisible no-ops and distinguishes a real completion from a queued or unverified one.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background/cheap model compiles typed health observations; realtime only speaks the short verdict when the owner is waiting. No vision model unless screen recording is explicitly granted.
- **latency:** Under 300 ms for cached health plus a fresh /observe and browser heartbeat; up to 2 s when a live bridge probe is required. Never block a read-only answer longer than the freshness budget.
- **cost:** Usually <$0.001 per invocation for deterministic checks and a small text model; dominated by an optional live probe, not inference.
- **security:** Health evidence includes foreground app, tab URLs/titles, permissions, and link state, so redact URLs and secrets by default and retain only hashes/TTL. UI actions require explicit degraded/unreachable verdicts rather than optimistic receipts; browser mutations still require owner confirmation.
- **missing:** A typed PerceptionSnapshot schema with source timestamps, TTLs, sensitivity labels, and monotonic sequence numbers shared by relay, Mac agent, browser extension, and pendant; An action preflight contract that consumes the snapshot and returns reachable/unreachable/unknown before execution; Post-action verification hooks: browser DOM evidence, Mac UI observation or explicit inability, pendant delivery acknowledgement, and one durable receipt joining all evidence; Browser heartbeat/command queue semantics that distinguish offline queued from executed; A redacted dashboard and spoken status formatter

### "When I reconnect, show me a trustworthy timeline of what happened while my pendant, Mac, relay, or browser were disconnected—including what was heard, held, forwarded, played, skipped, or duplicated—and let me ask about any gap."
- **useful because:** Today events are scattered across pipeline runs, browser queues, Mac jobs, and pendant offline storage, with different clocks and no owner-facing causal reconstruction. The owner cannot reliably know whether a late reply was spoken, merely uploaded, played twice, or never reached them. This would turn an outage into an understandable account without exposing private content by default.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic event normalization and a cheap background model for clustering/deduplication; use the realtime tier only when the owner asks verbally for an explanation. Content-sensitive interpretation should be opt-in.
- **latency:** Build the reconnect timeline within 2 seconds of a new link; answer a spoken 'what happened?' in under 1 second from the cached graph, with deeper reconstruction allowed in the background.
- **cost:** Usually <$0.002 per reconnect for event normalization and compact summarization; storage and reconciliation dominate, not model tokens.
- **security:** Store event metadata separately from payloads, defaulting to redacted labels and hashes. Keep audio, page text, and command contents encrypted with short retention; require confirmation before revealing private content. Authenticate device-originated events and mark clock uncertainty instead of inventing exact times.
- **missing:** A shared append-only continuity event envelope emitted by pendant firmware, relay, Mac bridge, and browser extension, including device sequence, monotonic uptime, wall-clock estimate, link state, parent event ID, payload hash, and sensitivity; Reconnect-time event upload and idempotent merge with duplicate/conflict detection across devices; Clock-skew and causal-order reconstruction that can represent unknown intervals rather than fabricate order; A durable owner-facing timeline API and dashboard/spoken renderer with drill-down from redacted summary to approved evidence; Pendant firmware support for compact local event indexes and acknowledgement of which held events were surfaced or played


## Changes it proposed to its own stack

### `integration` — Implement a signed, freshness-bounded PerceptionSnapshot/ActionAttestation contract. Before any side effect, relay gathers Mac /observe + /ops/status, browser heartbeat/session state, and latest pendant pipeline/link telemetry; it emits per-target reachability (reachable, queued, unreachable, unknown) with source timestamps and a snapshot hash. Afterward, each surface appends independent evidence (DOM/result, Mac post-observe delta, or pendant delivery/playback ack) and the relay computes verified/partially-verified/unverified instead of trusting executor success.
- **owner gets:** The owner will stop hearing 'done' when the Mac action never reached the screen or a browser command merely sat in an offline queue. They get a concise explanation such as 'queued in Chrome; not executed' or 'executed and verified from page evidence.'
- effort: Medium-high: shared schema and relay storage, Mac observer adapter, browser heartbeat/result changes, pendant acknowledgement mapping, and dashboard/spoken formatter.  ·  risk: Stale or contradictory sensors could produce false unknowns; use short TTLs, monotonic event IDs, and fail closed for side effects. If the relay is unavailable, preserve local receipts and say verification is pending. Never include secret capture values in snapshots.
- cost: Small D1/storage and deterministic processing cost; no routine model call. Optional cheap summarizer only for the spoken sentence.  ·  latency: Adds ~100–300 ms for cached checks and up to ~2 s for fresh bridge/browser probes; side effects should not start until preflight returns.
- security: Improves safety by preventing optimistic action claims, but snapshots must redact URLs, tab text, foreground titles, and secrets and use scoped retention. Sign or MAC evidence across surfaces to prevent forged completion.
- depends on: faculty-action's typed preflight refusal/degraded result; A browser extension heartbeat that reports online/queued/executed states; Pendant playback/delivery acknowledgement telemetry; Shared typed context service with provenance and expiry


## What it asked for

_Nothing._
## Its own summary

Fresh perception established: Mac UI actions are presently untrustworthy (Accessibility false, Screen Recording false, input reachability failed, uiActionsWillReachTheScreen=false); the browser extension is offline with 3 queued commands; relay/Mac bridge are online; pendant pipeline shows offline-held alerts/bookmarks and a prior successful 24 kHz response delivery. I recorded only non-secret operational facts and warned action/planner agents. I proposed a new cross-device PerceptionSnapshot/ActionAttestation capability and integration so every side effect is classified reachable/queued/unreachable before execution and verified/unverified afterward.

**Biggest unknown:** There is still no shared live PerceptionSnapshot or post-action evidence contract exposing pendant button/link/playback state, browser execution-vs-queue state, and Mac reachability in one typed, redacted record. Existing pending requests for those observability semantics, plus the Accessibility/Screen Recording permission fix, remain the blockers.

