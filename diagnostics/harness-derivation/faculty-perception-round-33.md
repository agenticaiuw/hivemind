# Harness derivation — faculty-perception — round 33

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-control-reachability** — At 2026-08-07T10:39:06Z the Mac local agent reports full-control mode and token configured, but Accessibility is not trusted, screen recording is not granted, and input probe failed. It explicitly warns UI actions may report success while doing nothing; UI clicks/typing cannot be trusted until AI Pendant Agent is granted Accessibility.
  - evidence: GET /observe HTTP 200: accessibility.trusted=false, eventsPost=false, screenRecording=false, inputReachability.status=failed, consequence says receipts for ui_click/ui_menu/type_text/press_keys cannot be trusted.
- **browser-reachability** — The browser extension home-chrome is offline at 2026-08-07T10:39Z with no active tab/window URL, while the Mac agent reports 3 durable browser sessions/tabs and 3 pending browser commands. Browser actions cannot currently be verified through the extension.
  - evidence: GET /observe and GET /ops/status: browser online=false, home-chrome tabId/windowId null; pendingCommands=3; durable sessions list includes default, probe-form2, probe-form.
- **relay-connectivity** — At 2026-08-07T10:39Z the Mac bridge and cloud relay are reachable/online. Relay advertises pendant pipeline telemetry, pendant speech, persistent agent state, and durable audio; relay voice model is gpt-realtime-2.1 and Mac TTS fallback is 24 kHz PCM.
  - evidence: GET /ops/status: relay.reachable=true, relay payload macBridgeOnline=true, capabilities pendantPipelineTelemetry/pendantSpeech/persistentAgentState/durableAudio=true.
- **machine-timezone** — The Mac machine-context currently reports timezone America/New_York.
  - evidence: GET /machine-context HTTP 200, machine.timezone=America/New_York at 2026-08-07T10:39Z.

## Capabilities it proposed

### "“Did that actually happen?”"
- **useful because:** Today the Mac can return a successful receipt even when synthesized UI input never reaches the screen, and browser commands can sit queued while the extension is offline. This capability would answer with independent postcondition evidence—not a receipt—using Mac observation, browser tab state, relay/job state, and (when relevant) pendant pipeline telemetry. It would say verified, contradicted, or not observable, with the exact reason and next diagnostic step.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use realtime only for the short spoken verdict; use a cheaper background model (or deterministic checks) to collect and reconcile postcondition evidence.
- **latency:** Spoken acknowledgement in under 1 s; evidence reconciliation within 5 s for Mac/relay, up to 20 s if waiting for browser heartbeat or pendant delivery.
- **cost:** Low: deterministic endpoint reads dominate; a small background summarizer only when multiple evidence sources conflict. Realtime cost is limited to the brief verdict.
- **security:** Evidence must be scoped to the specific job/session and redact private page contents. Never claim success from an executor receipt alone. Browser evidence requires the authenticated extension; pending or stale commands remain unverified. Any action to retry, resend, or alter state requires separate owner confirmation.
- **missing:** A first-class postcondition verifier that binds an action's expected state to independently observed facts across /observe, browser results, jobs, and pipeline telemetry.; Typed tri-state evidence contract (verified/contradicted/unobservable) with freshness and source timestamps exposed to relay and pendant.; A safe browser-queue reconciliation policy for stale commands when the extension returns online.

### "“If I asked for something while you were offline, tell me exactly what happened when everything reconnects—and resolve any duplicate or conflicting work before doing more.”"
- **useful because:** A worn device can accept a command while disconnected, while the Mac or relay may independently receive, retry, or partially execute the same intent. Today the owner can receive late replies and receipts but cannot reliably know whether two copies ran, which one won, or whether an offline pendant instruction is still pending. This would produce one causal timeline across pendant storage, relay jobs, Mac execution, and browser state; quarantine duplicates; and present a conflict for the owner instead of silently repeating side effects.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic event correlation and idempotency checks first; use a cheaper background model only to summarize the reconciled timeline. Reserve realtime for the short spoken reconnect summary.
- **latency:** On reconnect, acknowledge the reconciled state to the pendant within 2 seconds; complete cross-surface correlation within 10 seconds. Never delay local offline capture waiting for the cloud.
- **cost:** Low API cost: event joins, hashes, and idempotency keys dominate; background summarization is small and infrequent.
- **security:** The system must not infer that two similar natural-language requests are duplicates without a stable intent/action key. Side effects remain quarantined until conflict resolution; private browser content stays on the Mac and only hashes/status/timestamps leave it. The owner must confirm any choice that could cause another irreversible action.
- **missing:** A durable causal event log shared by pendant, relay, Mac, and browser, with monotonic device sequence numbers and reconnect watermarks.; End-to-end idempotency keys that survive offline capture, relay retries, Mac job creation, and browser command delivery.; A conflict/quarantine state machine and owner-facing reconciliation UI/audio, including explicit acknowledgement and replay rules.; Pendant firmware support for storing the originating request key and surfacing a compact unresolved-conflict alert offline.


## Changes it proposed to its own stack

### `integration` — Add a perception trust contract to every action receipt: before/after observation source, observedAt, freshness TTL, and trust state (verified, contradicted, unobservable). The orchestrator should preserve the action receipt but prevent higher layers from presenting it as completion when /observe reports failed input reachability or when browser extension heartbeat is stale. Relay should forward the compact verdict and source timestamps to the pendant.
- **owner gets:** The owner stops hearing “done” when nothing reached the screen or a browser command is still queued. They get an honest, actionable answer such as “submitted and confirmed,” “receipt says success but Mac input was unreachable,” or “waiting for Chrome to reconnect.”
- effort: Medium: typed schema and deterministic postcondition adapters for Mac, browser, relay pipeline; update dashboard and spoken-result rendering.  ·  risk: Some legitimate actions will be labeled unobservable when permissions or a device are temporarily unavailable. Recovery is to show the raw receipt, diagnostics, and allow an explicit retry only after the owner confirms.
- cost: Negligible API cost; mostly local endpoint reads and a few hundred bytes of metadata per job.  ·  latency: Adds roughly 100–500 ms for local verification; browser/pendant checks can remain asynchronous and update the receipt later.
- security: Improves safety by preventing unsupported success claims. Evidence should be redacted and scoped to job/session; do not transmit page content when only state metadata is needed.
- depends on: A typed postcondition verifier (new capability above); Relay support for compact evidence verdicts; Browser heartbeat/command queue timestamps

### `relay` — Build an append-only cross-surface causal ledger and reconnect reconciler. Each pendant capture, relay delivery, Mac job, browser command, and result receives an origin request ID, device sequence, attempt ID, parent ID, and observed state. On reconnect, the relay joins events by origin, marks duplicate attempts as quarantined rather than replaying them, and emits a compact conflict record to the pendant and dashboard. The Mac/browser must expose outcome hashes and timestamps without exporting private page contents.
- **owner gets:** After a dropped link, the owner gets one trustworthy account of what happened instead of duplicated reminders, repeated submissions, or an unexplained late response. They can choose once when two attempts disagree, without needing to inspect logs.
- effort: High: protocol changes across pendant firmware, relay D1 schema/worker, Mac job tracker, browser bridge, and dashboard/audio rendering; requires migration for existing jobs.  ·  risk: Incorrect correlation could quarantine legitimate separate requests or fail to quarantine duplicates. Start in observe-only mode, show proposed joins, then enable suppression for actions with stable idempotency keys; retain raw events and provide manual replay.
- cost: Small relay storage and egress increase for event metadata; no model cost for correlation, occasional cheap summarization only.  ·  latency: No impact while offline; reconnect reconciliation adds under 2 seconds for normal queues and asynchronous updates for large histories.
- security: Improves auditability but creates a cross-device metadata trail. Encrypt sensitive fields, minimize payloads to hashes/status, enforce per-owner authorization, and set retention/erasure controls.
- depends on: Stable end-to-end request and idempotency identifiers; Pendant offline queue metadata and conflict alert support; Mac/browser typed outcome hashes and timestamps


## What it asked for

### `p2-qsvr` (permission) — Grant macOS Accessibility and Screen Recording permissions to the exact running AI Pendant Agent binary (com.aipendant.agent at /Users/evanliu/Applications/AI Pendant Agent.app), then re-run the /observe input-reachability probe.
- why: Current observation proves UI actions may report success while doing nothing, and screen-based verification is unavailable. Without these permissions, perception cannot establish whether Mac GUI actions happened.
- risk it sees: Accessibility enables synthetic input and Screen Recording exposes the Mac display to the local agent; both should remain local, be visibly indicated by macOS, and be revocable in System Settings. Do not grant to a different helper binary or generic terminal process, because that would not make this agent's actions trustworthy.

## Its own summary

Fresh perception establishes: Mac/relay are online, but the exact AI Pendant Agent binary lacks Accessibility and Screen Recording; synthesized UI actions and their receipts are therefore untrustworthy. Chrome extension is offline with 3 pending commands, despite 3 durable browser sessions. Relay advertises durable audio/state and 24 kHz TTS. I recorded these facts, informed faculty-action of available/missing uncertainty fields, proposed a cross-surface “Did that actually happen?” capability and a typed verified/contradicted/unobservable evidence contract, and queued a request for the correct macOS permissions.

**Biggest unknown:** Whether the owner will grant Accessibility and Screen Recording to the exact AI Pendant Agent bundle; until then, no GUI action can be independently established, and browser work remains unverified until Chrome heartbeat returns.

