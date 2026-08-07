# Harness derivation — mac-terminal — round 51

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac execution preflight** — Live ops status reports fullControlMode=true and unrestricted planner, but mac readiness is false because Accessibility and Screen Recording are not granted. Browser bridge is offline with 3 pending commands; a browser_navigate attempt waited ~45 seconds before failing. Relay and mac bridge are reachable.
  - evidence: GET /ops/status HTTP 200 payload at 2026-08-07T10:56Z; GET /jobs shows failed browser_navigate receipt with durationMs 45180 and offline reason.

## Capabilities it proposed

### "“Reconcile this logged-in webpage with the matching files on my Mac and tell me exactly what conflicts, is missing, or is stale; prepare a clean correction plan but change nothing.”"
- **useful because:** Today the owner can have the browser or Mac inspect one source at a time, but cannot safely compare private web records against local documents as one evidence-backed task. This would catch mismatched invoices, application forms, schedules, and project exports without silently editing either source.
- **path:** pendant → browser → mac-planner → mac-vision → relay → dashboard
- **model tier:** Use background for extraction, normalization, and pairwise comparison; escalate to planner only for ambiguous identity matching or contradictory evidence. Realtime should only handle the spoken request and concise result.
- **latency:** Initial answer in 10–30 seconds for a small set (up to 10 files/tabs); larger sets continue asynchronously and leave a dashboard workbench plus a short pendant summary.
- **cost:** Roughly $0.02–$0.15 per small reconciliation, dominated by private-page/file extraction and comparison tokens; deterministic hashing and metadata matching should avoid model calls for obvious matches.
- **security:** This joins two sensitive stores, so the relay must receive only opaque job IDs and redacted normalized fields; raw authenticated page text and local file contents stay on the Mac/browser bridge where possible. Every claim needs source URL or file path, timestamp, and quoted evidence. Preparing a correction plan must never write, upload, email, or submit without a separate owner request.
- **missing:** A local reconciliation worker that can read selected Mac files and authenticated browser tabs into a common typed schema; Stable cross-surface provenance IDs and field-level evidence links; A user-selectable scope picker for which tabs/files may be compared, with sensitive-file exclusions; A conflict report/workbench UI and an offline-safe pending result queue


## Changes it proposed to its own stack

### `integration` — Add a cross-surface capability preflight and failure-recovery broker, without restricting FULL_CONTROL_MODE. Before dispatch, query cached liveness/permission state for Mac, browser bridge, relay, and any requested app; attach a short-lived preflight snapshot to the job. If a target is unavailable, fail fast with a typed reason (offline, permission missing, stale session, or timeout) instead of waiting ~45 seconds, and select only an explicitly safe alternate: public-page reads can fall back to relay/read_web_page, while private authenticated work is parked as a durable retry bound to the same tab/session. On reconnection, retry only failed, idempotent steps and reconcile receipts so the owner never gets duplicate actions. Surface a single spoken explanation plus a dashboard diagnostic link.
- **owner gets:** The pendant can say immediately whether something is blocked by the Mac or browser, and still get public answers when the private browser is asleep. Long waits and mysterious failures disappear, while private work resumes later instead of being lost or accidentally repeated.
- effort: Medium: shared preflight schema and 10–15 typed failure states; health-cache hooks in planner/execute; idempotency-aware retry queue; relay fallback adapter; dashboard and spoken receipt changes. No permission gate or capability reduction.  ·  risk: A stale health snapshot could misroute a job, and an overly broad fallback could expose data to the relay. Enforce source classification: authenticated content never falls back to public/relay paths; require session affinity for retries; expire snapshots quickly; preserve failed receipts and provide an explicit discard operation.
- cost: Small background health probes and a few hundred tokens of structured metadata per job; avoids wasting expensive planner calls and 45-second failed browser attempts. Relay fallback incurs normal read/API cost only when selected.  ·  latency: Adds roughly 50–150 ms for cached preflight; removes tens of seconds from known-offline failures. Reconnection retries are asynchronous.
- security: Improves security observability without adding gates. Private tab/session identifiers remain local and are never sent to public fallback; typed provenance records where each result came from.
- depends on: A durable job/retry store (the existing browser runner backlog is still open); A functioning browser heartbeat endpoint/extension polling loop; Implementations for the newly granted read-only Mac diagnostics tools; Shared action idempotency keys and receipt reconciliation


## What it asked for

_Nothing._
## Its own summary

Discovered live readiness gaps: Mac agent is in unrestricted FULL_CONTROL_MODE but reports ready=false because Accessibility and Screen Recording are missing; browser bridge is offline with 3 pending commands. A browser navigation actually waited 45.2s before failing, despite the failure being known. Relay and Mac bridge are reachable. I recorded this and proposed a new cross-surface preflight/failure-recovery broker that fails fast, preserves private-session affinity, falls back only for public reads, and retries idempotently without adding gates.

**Biggest unknown:** The newly granted Mac diagnostic interfaces all return 'no implementation yet', so I cannot independently verify host state or local-agent health through them. I also still need the browser-extension heartbeat/reconnect behavior and durable retry/idempotency contract to implement the proposed recovery path.

