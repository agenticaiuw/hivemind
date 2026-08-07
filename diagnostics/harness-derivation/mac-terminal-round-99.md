# Harness derivation — mac-terminal — round 99

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-ui-reachability** — Mac agent reports ready:false: Accessibility is not trusted for the running AI Pendant Agent binary, input probe failed, and ui_click/type_text/press_keys may report success while doing nothing; browser extension is offline with 9 pending commands. /observe exposes this, but action execution does not appear to enforce or surface a preflight outcome.
  - evidence: GET /ops/status at 2026-08-07T13:34Z: accessibility.trusted=false, requiredMissing=[], ready=false, browser.online=false pendingCommands=9. GET /observe: uiActionsWillReachTheScreen=false and consequence says UI receipts cannot be trusted.

## Capabilities it proposed

### "“If you lose connection while doing that, keep the work safe: resume only while my request is still fresh, and tell me exactly whether it finished, was abandoned, or needs me.”"
- **useful because:** Today the Mac reports nine pending browser commands while the extension is offline, and prior browser jobs waited ~45 seconds before failing. A durable job that blindly resumes can duplicate a click after the owner's intent has changed; a job that simply dies loses useful work. The owner needs a cross-node lease: relay persistence, Mac execution, browser session identity, and a wearable status/expiry conversation.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use the realtime model only for the initial short voice clarification and final spoken status; use a cheaper background model for step planning, state reconciliation, and summarizing receipts.
- **latency:** Acknowledge immediately (<1 s), persist a resumable job in <2 s, then work asynchronously. Reconnect recovery can take seconds; never keep the voice turn open for browser timeouts.
- **cost:** Low per invocation: one short realtime turn plus background planner calls only on retries/reconciliation; storage and heartbeat traffic dominate, not inference.
- **security:** The lease must bind to the original request, authenticated browser session/tab, and a freshness deadline. Never replay non-idempotent shell/UI/browser mutations after expiry; retain encrypted hashes and redacted receipts, and ask the owner again when the lease expires. The relay must not expose private page content to the pendant unless requested.
- **missing:** A cross-surface job lease with intent version, expiry/quiet-hours policy, and cancellation tombstones; Relay-to-Mac durable resume protocol that survives duplicate delivery and reconnects; Browser command acknowledgement carrying session/tab identity and idempotency key; Pendant status events for resumed/abandoned/needs-owner states

### "“Make the computer-control connection usable again, and stay with me until you know it really works.”"
- **useful because:** The owner cannot reliably have GUI work done today: the running AI Pendant Agent is not the binary trusted by Accessibility, synthesized events are rejected, and receipts can claim success while nothing reaches the screen. The useful missing experience is not another action history—it is a cross-node repair session. The pendant should explain the exact problem, the Mac should open the right System Settings pane and run a harmless reachability test, the relay should preserve the repair checklist if the agent restarts, and the pendant should announce only after a post-repair probe succeeds.
- **path:** pendant → relay → mac-planner → dashboard-ux
- **model tier:** Realtime only for the owner's short conversational guidance and final confirmation; use a cheap background model to map the observed permission error to a deterministic repair checklist and summarize verification.
- **latency:** Speak the diagnosis immediately from the existing observation (<1 second), open the relevant settings pane within a few seconds, and finish the verification loop within 30 seconds of the owner granting permission. Persist progress across disconnects.
- **cost:** Low: mostly deterministic Mac probes and one background summary; no browser page content or vision upload is needed. Cost is dominated by occasional background inference, not the realtime turn.
- **security:** The repair flow must never claim it can grant macOS permissions itself. It may open System Settings and run a zero-delta/input reachability probe, but the owner performs the permission grant. Do not transmit screen contents, keystrokes, or private app data to the relay; store only permission state, binary identity, timestamps, and probe result. Require an explicit owner gesture before opening settings if initiated remotely.
- **missing:** A deterministic permission-remediation state machine keyed by host binary identity and permission type; Deep-link/open-and-return handling for macOS Privacy & Security panes; A post-grant reachability test whose result is bound to the actual executing agent binary; Relay-persisted repair-session state and pendant progress/failure events


## Changes it proposed to its own stack

### `mac-harness` — Add a reachability-aware execution envelope around every Mac action. Before dispatch, snapshot /observe-derived facts (Accessibility/input reachability, screen recording, secure input, browser heartbeat, foreground app, session/tab identity); annotate the job with the selected route and an explicit `mayNotReach` warning, but never block in FULL_CONTROL_MODE. After dispatch, run a bounded, action-specific verification (browser command result/DOM change, app/window state, file existence/hash, volume state, or a second observation) and set receipt status to `verified`, `completed-unverified`, or `failed-to-reach` instead of treating the host API's return as success. For browser commands, automatically requeue with exponential backoff only when the extension is offline/stale, and collapse duplicate pending commands by idempotency key. Expose preflight, verification, retry history, and the exact fallback route in GET /jobs/:jobId, /jobs/:jobId/receipts, /observe, and the dashboard.
- **owner gets:** The pendant can honestly say “I changed it,” “I could not reach the screen,” or “it may have changed but I cannot verify,” rather than claiming success while Accessibility is pointed at the wrong binary or Safari is not polling. Long tasks recover after a transient browser disconnect without duplicate clicks, and the owner gets a useful explanation instead of a silent 45-second timeout.
- effort: Medium: central execution wrapper plus per-action verifiers, idempotency/retry state, dashboard fields, and tests against the existing browser/job/receipt paths. No model change required.  ·  risk: Verification may be inconclusive or misclassify a legitimate change; preserve raw host result and allow the job to remain completed-unverified. Retries must be limited to operations marked idempotent and use request/action keys; never replay arbitrary shell or irreversible UI actions automatically. This adds latency for verification, bounded by ~1–3 seconds for local checks and existing browser timeout for browser recovery.
- cost: Negligible API cost; small local CPU/IO. Saves expensive model turns by returning structured failure causes and avoiding repeated blind attempts.  ·  latency: Adds ~0.1–1 s for local preflight and verification; browser retries are asynchronous and do not hold the voice turn open. Fast-path read-only shell can skip verification when its exit code and captured stdout are sufficient.
- security: No new authorization or restrictions; FULL_CONTROL_MODE and unrestricted shell remain. Receipts gain sensitive metadata (paths, URLs, foreground app), so redact secrets and retain only hashes/snippets in the dashboard/log export.


## What it asked for

_Nothing._
## Its own summary

Fresh discovery found a concrete live defect: /ops/status says the agent is not ready, /observe says Accessibility events are rejected by the running binary and UI actions may report success while doing nothing; browser is offline with 9 queued commands. I recorded this and proposed a non-blocking, reachability-aware verification envelope. I also proposed a cross-surface freshness lease so relay/Mac/browser jobs resume only while the owner's intent is valid, rather than replaying stale commands. I do not need another diagnostic grant this round; what is still needed is implementation of the lease/verification wiring between the existing routes, plus correcting Accessibility permission for the actual AI Pendant Agent binary.

**Biggest unknown:** Whether the owner wants the current browser queue (9 pending commands) discarded, replayed after the extension reconnects, or marked abandoned; no mutation was performed.

