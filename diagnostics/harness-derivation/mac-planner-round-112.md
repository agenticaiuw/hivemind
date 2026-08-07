# Harness derivation — mac-planner — round 112

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Park this and help me resume it later.” On a pendant tap or spoken command, save the current work context; when I say “resume the thing I parked,” restore the relevant Mac apps, browser tabs, project, and a one-sentence spoken recap without reopening secrets unnecessarily."
- **useful because:** The owner can leave a task mid-stream—meeting, commute, interruption—and return without reconstructing what was open or why. This is genuinely cross-surface: the pendant supplies the low-friction trigger, the relay persists the capsule while the Mac sleeps, the browser supplies authenticated tab identity, and the Mac reopens only the chosen context.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the realtime tier only to recognize the short park/resume utterance and speak the recap; use a cheaper background model to normalize the capsule, rank relevant tabs/apps, and redact volatile or sensitive fields.
- **latency:** Park acknowledgement under 2 seconds; resume acknowledgement under 2 seconds, with Mac/browser restoration continuing asynchronously and a completion receipt within 15 seconds.
- **cost:** About $0.001–$0.01 per park/resume depending on whether summarization is needed; most work is local metadata and durable storage, not model tokens.
- **security:** Store app names, URLs, project id, and short user-approved notes—not page bodies or passwords by default. Encrypt capsules, give each a TTL, mark authenticated tabs as private, and provide 'forget parked context'. Never submit forms or send mail during restore; destructive or external actions remain confirmation-required.
- **missing:** A durable resume-capsule schema linking /observe state, browser session/tab identity, active project, and a user note; A relay job that survives Mac disconnects and returns a typed restoration receipt; A Mac restore planner that can reopen apps/URLs via mac_run_actions while preserving the owner's current foreground app; A browser reattachment operation that validates extension heartbeat/tab affinity before acting; Pendant trigger and offline acknowledgement for park/resume

### "“Use my work account for this, but do not expose or copy my credentials.” Let me securely authorize one specific task from the pendant, have the browser use the already-open signed-in session, and receive a proof that the action used the intended account and changed only the approved fields."
- **useful because:** Today the system can see that a browser session exists, but it cannot give the owner a strong, understandable guarantee about which account, tab, or scope an action used. This would make private-account automation trustworthy without ever moving passwords or session cookies through the relay.
- **path:** pendant → relay → browser → mac-bridge → dashboard
- **model tier:** Use the realtime model only to resolve the owner's short authorization utterance and read back the account/display name. Use deterministic local code for capability-token issuance, tab binding, field-diff verification, and receipts; use a cheaper background model only to summarize the final proof in plain language.
- **latency:** Authorization and account read-back under 2 seconds; preflight proof under 5 seconds; final field-diff receipt within 10 seconds after the browser reports completion.
- **cost:** Near-zero model cost for most invocations; a small deterministic token/receipt record per task. Optional summarization costs under $0.005 per completed task.
- **security:** The relay must never receive cookies, passwords, page bodies beyond the approved fields, or reusable bearer tokens. Issue a one-task, short-lived capability bound to account identifier, extension device, tab/session id, action hash, and expiry; require a physical pendant confirmation for account-scoped mutations. On mismatch, stop and report rather than guessing. Store only redacted before/after hashes plus user-visible labels, with revocation and audit history.
- **missing:** A cryptographic pairing and attestation protocol between pendant, relay, Mac agent, and browser extension; A browser-side account identity primitive that can report the origin and signed-in display identity without exposing cookies; A preflight capability-token endpoint binding one action plan to one tab/session and expiry; A deterministic before/after field-diff verifier and proof receipt schema; A pendant confirmation UX for displaying or speaking the target account and approved scope


## Changes it proposed to its own stack

### `browser-harness` — Add a bridge-health lease and dead-letter watchdog, distinct from the command queue: treat a heartbeat with tabId/windowId null, missing browserName, or an old lastSeenAt as degraded even when online=true; stop claiming queued commands, mark the existing 9 pending commands as quarantined with their request IDs, and require a fresh tab-bound heartbeat epoch before replaying only idempotent reads. Surface a single repair action in the dashboard and a concise pendant notification.
- **owner gets:** Prevents a disconnected or reloaded browser extension from silently executing stale private-page commands later, while making the current 'online but no tab' state understandable and recoverable instead of leaving work hanging.
- effort: Medium: heartbeat validation, command lease/dead-letter state, replay classification, dashboard status, and a small relay notification adapter.  ·  risk: A false degraded state could delay a legitimate read; recover by accepting a fresh tab-bound heartbeat and allowing explicit replay from the dashboard. Never delete quarantined commands automatically; retain receipts and audit history.
- cost: Negligible API cost; a few D1/local JSON records per command and one periodic watchdog invocation.  ·  latency: Adds no delay to healthy commands; degraded detection occurs at heartbeat/lease expiry, with recovery in one heartbeat interval.
- security: Improves security by preventing stale commands from being applied to a different authenticated tab or account. Quarantined payloads should be redacted in dashboard/pendant views and retained under existing private-session policy.
- depends on: A heartbeat payload that includes a monotonically increasing bridge epoch and bound tab/window identity; Typed idempotency classification for browser commands (read-only versus mutation); A dead-letter/quarantine record and dashboard repair/replay control; An explicit relay notification route for degraded browser state

### `integration` — Introduce a four-party, one-task authorization envelope: the pendant signs an owner confirmation containing target origin/account label, normalized action hash, allowed field scope, expiry, and nonce; the relay forwards only that envelope; the Mac bridge asks the browser extension to attest the bound tab's origin and account label; execution receipts include matching hashes and a redacted before/after diff. Reject any tab, account, origin, or action mismatch and invalidate the nonce after one use.
- **owner gets:** They can safely say “use my work account for this” and know which signed-in account acted, without handing credentials to the AI or wondering whether a stale tab performed the wrong change.
- effort: High: protocol design, pendant signing/secure storage, browser extension account-identity attestation, Mac/relay verification, receipt schema, and recovery for browser reloads or clock skew.  ·  risk: Pairing loss or extension updates could invalidate authorization; recover with an explicit re-pair flow and never silently fall back to an unbound session. An account label could itself be sensitive, so redact it in relay logs and expose only a user-chosen alias.
- cost: Negligible per-task API cost; engineering and secure-key storage are the main cost. Requires a small key record on the pendant and short-lived records in relay/bridge storage.  ·  latency: Adds one local attestation round trip, typically 100–500 ms on a healthy link; no model latency on execution.
- security: Materially reduces confused-deputy and stale-tab risk while preserving the owner's maximum-access policy. It does not block ordinary unscoped local actions, only account-scoped browser work lacking a valid envelope.
- depends on: A pendant signing/key-storage primitive with rotation and recovery; Browser extension support for origin plus signed-in account identity attestation; Relay and Mac verification libraries with nonce replay protection; Redacted proof receipts and dashboard rendering


## What it asked for

_Nothing._
## Its own summary

Live discovery found the Mac agent healthy and relay-connected, but not execution-ready: Accessibility and Screen Recording are still false, so UI actions can report success without affecting the screen. Browser status is misleadingly online with no bound tab/window and 9 pending commands; durable sessions exist, while recent browser jobs timed out. I proposed (1) a cross-surface park/resume capsule and (2) a bridge-health lease/dead-letter watchdog to quarantine stale commands and replay only after a fresh tab-bound heartbeat.

**Biggest unknown:** Whether the browser extension can emit a real tab-bound heartbeat and epoch (rather than the current online/no-tab heartbeat); without that, private-page execution and safe recovery remain unreliable. The owner still needs to grant Accessibility/Screen Recording manually if vision/UI automation is wanted.

