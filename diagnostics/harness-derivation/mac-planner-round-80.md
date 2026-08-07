# Harness derivation — mac-planner — round 80

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-browser execution readiness** — Mac bridge is online and FULL_CONTROL_MODE is enabled, but local agent reports ready=false because Accessibility is not trusted and Screen Recording is not granted; browser extension home-chrome is offline with 5 pending commands. Computer-use loop is disabled and vision upload consent is false.
  - evidence: GET /ops/status returned HTTP 200 at 2026-08-07; payload agent.permissions.accessibility.trusted=false, screenRecording.granted=false, browserExtension.online=false, pendingCommands=5, computerUse.loopEnabled=false.

## Capabilities it proposed

### "If I tell you to handle something in Safari and then my laptop or Wi‑Fi drops, keep the task safe: prepare what you can, pause if the page/session changed, and tell me from the pendant exactly what is waiting before anything is submitted."
- **useful because:** Today a disconnected bridge leaves pending browser commands and no trustworthy way to know whether they are still aimed at the same page. This gives the owner continuity without replaying stale actions or losing the prepared work.
- **path:** pendant: receives a concise paused/resumed status and can request resume or discard → relay: owns the durable job, lease expiry, idempotency, and notification when the Mac/browser reconnects → mac-planner: reattaches the Mac bridge, captures fresh local evidence, and writes a receipt → browser-extension: reattaches the authenticated tab, verifies URL/title/semantic fingerprint, and prepares or resumes only against the current tab → dashboard: shows quarantined reason, evidence timestamps, and resume/discard controls
- **model tier:** Use the slower background model for extraction/reconciliation and the realtime tier only for the pendant's live explanation or resume command.
- **latency:** Immediate acknowledgement in under 2 seconds; after reconnect, fresh tab verification in under 5 seconds. No waiting voice turn should block on a long browser job.
- **cost:** Low per invocation: mostly relay storage and browser/Mac local actions; one cheap background extraction pass on reconnect. Realtime tokens are limited to status wording.
- **security:** Never replay an expired lease or a command bound to a changed tab/session. Page content stays on the authenticated browser/Mac path where possible; the relay stores hashes, IDs, timestamps, and minimal excerpts. Resume of an irreversible submit should remain a separately visible action, consistent with the owner's no-gate policy but with explicit evidence.
- **missing:** A shared lease/quarantine protocol across relay, Mac bridge, and browser extension; Browser reconnect and tab fingerprint verification; Pendant notification vocabulary and resume/discard intents; Dashboard view for quarantined jobs

### "I have to go—save my place everywhere and bring me back to exactly what I was doing when I return."
- **useful because:** A normal bookmark or job status loses the owner's intent, unsaved draft, tab relationships, and the reason the next step mattered. This would create one interruption checkpoint across the pendant, Mac, and authenticated browser, then restore a concise, evidence-backed continuation later without reopening the wrong work.
- **path:** pendant: one button or spoken command creates the checkpoint and later announces the recovery brief → mac-planner: records foreground app, open windows/documents, local draft locations, and reversible restoration actions → browser-extension: records the authenticated tab set, active tab, scroll/form state, and a redacted semantic snapshot without exporting secrets → relay: stores the encrypted checkpoint, links it to a resumable session, and delivers a reminder or recovery brief when the Mac is available again → dashboard: lets the owner inspect, edit, expire, or delete the checkpoint before restoration
- **model tier:** Use a cheap background model to compress the checkpoint and infer the next concrete step; use realtime only when the pendant is actively asking the owner what to restore.
- **latency:** Acknowledge the checkpoint in under 1 second, finish capture in under 5 seconds, and deliver a recovery brief in under 10 seconds after the owner returns. Restoration must be incremental so the owner can start before every detail is loaded.
- **cost:** Low to moderate: local capture dominates latency, relay storage is small, and one background summarization call per checkpoint is sufficient. Realtime usage is limited to the spoken trigger and recovery interaction.
- **security:** Checkpoint data can include private browser pages and unsaved text. Keep raw content on the Mac/browser where possible, send only encrypted/redacted excerpts and hashes to the relay, encrypt at rest, expire by default, and make deletion immediate. Never auto-submit forms or send messages during restoration; restore drafts and tabs only.
- **missing:** A cross-surface checkpoint schema with intent, app/window identity, tab/session identity, evidence timestamps, and expiry; Implemented read-only Mac/UI-state inspection and browser tab/form/scroll capture; A local encrypted vault for unsaved drafts and a relay pointer for recovery; Pendant checkpoint/resume events and notification delivery; Crash-safe restore plans with per-step receipts and explicit exclusion of irreversible actions

### "Go private for the next hour: keep helping me, but do not send anything from this task to the cloud, and tell me when a step cannot be done locally."
- **useful because:** The owner cannot currently express a temporary, task-scoped data boundary that all members of the hive honor together. This gives them useful local automation while making cloud-dependent steps visible instead of silently exporting page text, drafts, or audio.
- **path:** pendant: physical/spoken private-mode toggle, local indicator, and concise warnings when a requested operation exceeds the boundary → mac-planner: executes eligible reads, file work, Calendar/Mail access, and local app actions without relay upload; records a local-only receipt → browser-extension: applies a local-only extraction policy to selected tabs and blocks transmission of page content or screenshots to cloud workers → relay: issues a scoped privacy lease, refuses cloud model/storage use for matching jobs, and returns capability-unavailable results rather than downgrading silently → dashboard: shows the active scope, expiry countdown, blocked attempted egress, and a local export/delete control
- **model tier:** Use a local Mac model or deterministic routines for private-mode work; if no local model can satisfy the task, explain the limitation rather than invoking the realtime cloud model.
- **latency:** Mode activation under 1 second and enforced before the next action. Local actions retain normal latency; blocked cloud steps should be reported immediately.
- **cost:** Potentially lower API cost because cloud inference and relay storage are deliberately avoided. Engineering cost is in enforcement and testing, not per-use spend.
- **security:** A client-only flag is insufficient: relay, browser bridge, and Mac agent must cryptographically bind every job to the privacy lease and reject mismatched uploads. Define whether telemetry, receipts, and crash logs are metadata-only. Expire automatically, provide a visible confirmation on exit, and never claim private mode if a required local control is unavailable.
- **missing:** End-to-end privacy lease propagated from pendant to relay, Mac agent, and browser extension; Local model/routine capability registry and deterministic egress audit; A device-side private-mode indicator and offline-safe persistence; Relay and browser enforcement that rejects content-bearing requests outside the lease; Dashboard data-boundary status and audit view


## Changes it proposed to its own stack

### `integration` — Implement a reconnect-safe cross-surface execution lease and stale-command quarantine. When a plan originates from the pendant/relay, bind its job to a plan hash, browser tab/session (if any), Mac bridge instance, and short-lived nonce. The Mac bridge and browser extension may prepare/read and return evidence, but on reconnect they must first revalidate the lease and current tab URL/title/fingerprint; commands older than the lease or whose tab/session changed move to quarantined (not executed) with an explicit reason. Reconciliation should be idempotent by request ID, preserve receipts, and let the pendant ask to resume or discard. This is observability/reliability, not an approval gate, and must work with FULL_CONTROL_MODE owner policy.
- **owner gets:** If the laptop sleeps, Chrome restarts, or Wi‑Fi drops while you say “handle this,” the system will not silently apply an old command to a different page or duplicate a submission. When you come back, you get a clear “paused because the page changed” result and can resume from the pendant or Mac instead of reconstructing the task.
- effort: Medium: shared lease schema in relay D1, bridge reconnect handshake, browser extension reattachment/fingerprint check, quarantine state and dashboard/pendant status messages, plus crash/replay tests.  ·  risk: A legitimate long-running job may pause after expiry; recovery is explicit resume against fresh evidence. Network partitions can leave a job pending, but idempotency prevents duplicate execution. No mutation is blocked permanently; it is only held when identity/evidence is stale.
- cost: Negligible API cost; a few D1 reads/writes and small status payloads per reconnect. Engineering cost is primarily protocol and replay testing.  ·  latency: No added latency to ordinary connected reads; reconnect adds one handshake and evidence refresh, typically sub-second before resuming.
- security: Reduces confused-deputy and replay risk by binding actions to device/session/tab identity and freshness. Lease metadata should avoid storing page content beyond existing receipts and use nonce hashes rather than raw secrets.
- depends on: Browser command queue with request IDs/idempotency/tab affinity (chg-14accc01); Mac action receipts/undo records (chg-5fc73ce3); Relay durable jobs and /jobs status routes; Browser extension reconnect status currently reported by /browser/status and /browser/sessions


## What it asked for

_Nothing._
## Its own summary

Discovered the live blocker state and proposed a new reconnect-safe lease/quarantine protocol plus an owner-facing “pause safely and resume after reconnect” capability. The relay and Mac bridge are reachable, but the browser extension is offline with 5 pending commands; Accessibility and Screen Recording remain unavailable, so UI/vision execution is not ready. The granted mac_readonly_inspect interface is still present only as an unimplemented schema. No additional tool grant is needed for the protocol proposal; implementation and reconnect work are the missing pieces.

**Biggest unknown:** Whether the owner wants to enable Accessibility/Screen Recording and reconnect Chrome now; without those, I cannot verify or safely resume browser/UI work on the live Mac.

