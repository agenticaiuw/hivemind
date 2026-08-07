# Harness derivation — mac-terminal — round 60

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Do it, and make sure it actually worked.”"
- **useful because:** Today an unattended Mac shell command can return exit 0 while producing the wrong state, and a browser or authenticated service may be the only place the real outcome is visible. This gives the owner a closed loop: the pendant captures the goal and can announce completion, the relay keeps the job alive, the Mac performs local work, and the browser verifies the externally visible result. If verification fails, the system explains the failure and retries with a different strategy rather than claiming success.
- **path:** pendant → relay → mac-harness → browser-harness → dashboard-ux
- **model tier:** Use a cheaper background model for planning and postcondition checking; reserve realtime only for the brief spoken acknowledgment and final exception. Use deterministic checks (exit status, file hash, accessibility/UI state, page text) before spending model tokens on semantic comparison.
- **latency:** Immediate acknowledgment under 1 second; local verification 1–3 seconds; browser verification normally under 10 seconds. Long retries continue as a durable job and notify the pendant only on verified completion or an actionable exception.
- **cost:** Usually <$0.01 per invocation when deterministic checks suffice; roughly $0.02–$0.10 when semantic reconciliation across Mac and authenticated browser evidence is needed. Browser/session latency and model context, not shell execution, dominate.
- **security:** Evidence may include private files, URLs, or authenticated page text and must stay in the existing owner-scoped job/session context, with sensitive stdout and page excerpts redacted in receipts. Never claim success from a command exit code alone. Actions remain under the owner's deliberate unrestricted shell policy; verification is not an approval gate. Require explicit confirmation only for any newly proposed irreversible follow-up, if policy ever changes.
- **missing:** A typed goal/postcondition schema shared by pendant, relay, Mac, and browser (including evidence source, freshness, and tolerance).; A verifier that can combine shell receipts with browser/page evidence and distinguish transport failure, command failure, and wrong-result success.; Durable retry/reroute state with idempotency and a terminal 'needs owner' outcome.; A dashboard and pendant protocol for concise verified-success versus uncertain/failure notifications.

### "“I’m leaving my desk—make sure I’m not leaving anything exposed, and tell me if you couldn’t.”"
- **useful because:** A spoken or button-triggered departure check would coordinate the pendant’s physical presence, the Mac’s actual lock/power/network state, the browser’s authenticated tabs, and the relay’s independent record. It could lock the Mac, stop sensitive screen sharing, identify authenticated tabs or unsaved work that cannot safely be closed, and leave an exact exception list. This is not a generic reminder or a Mac-only command: it gives the owner a trustworthy privacy handoff when they physically walk away and can still report failure if the Mac is asleep, disconnected, or unreachable.
- **path:** pendant → mac-planner → mac-vision → browser-extension → relay-realtime → dashboard-ux
- **model tier:** Use deterministic local checks and typed actions for lock, sharing, power, and tab state; use a cheap background model only to rank exceptions and explain them. Realtime is needed only for the brief spoken result.
- **latency:** Acknowledge the button or phrase immediately; complete local checks in 2–5 seconds and browser/session inspection in up to 10 seconds. If a device is unreachable, report that explicitly rather than waiting indefinitely; relay can finish and notify when it reconnects.
- **cost:** Usually under $0.01 because most checks are deterministic; occasional semantic exception grouping may cost $0.01–$0.04. Latency is dominated by browser tab/session access and Mac wake/connect behavior.
- **security:** The check necessarily touches authenticated-tab metadata and potentially sensitive window titles, so keep evidence owner-scoped, retain only hashes and minimal exception text, and redact page contents by default. Locking and stopping sharing are reversible; closing tabs, discarding edits, or signing out must never happen implicitly. The owner should choose a policy preset, but the system must report every skipped action and why.
- **missing:** A pendant departure trigger (button gesture, explicit voice intent, or proximity transition) routed to a multi-surface job.; Typed Mac privacy-state observers/actions for lock state, active screen sharing/remote-control sessions, unsaved documents, and wake/connect status.; Browser APIs that enumerate authenticated tabs and detect unsaved or sensitive state without reading full page contents.; A relay-held privacy-check job with a short-lived, encrypted evidence record and reconnect completion semantics.; A policy engine for owner-selected safe actions versus report-only exceptions, plus a concise pendant result protocol and dashboard audit view.


## Changes it proposed to its own stack

### `mac-harness` — Implement a bounded diagnostic/evidence bundle path behind the existing unrestricted shell: one request returns host identity, power/network/audio state, local-agent health, active job and correlation ID, plus redacted stdout/stderr and exit status for the selected action. Make it read-only, timestamped, and attachable to the existing action receipt; expose a stable typed interface for relay and dashboard instead of requiring repeated ad-hoc shell probes. Do not gate or reduce run_shell capability.
- **owner gets:** When the owner asks whether something happened, the system can answer with a compact, trustworthy bundle—what ran, on which Mac state, and what it observed—rather than making them repeat commands or accept an unexplained 'done.' It also lets a sleeping relay distinguish a dead Mac from a failed command and tell the owner the right next step.
- effort: Moderate: implement the currently granted diagnostic tool, add redaction and correlation to actionReceipts, persist bounded bundles with job retention, and add dashboard rendering and tests for unavailable/stale fields.  ·  risk: Command output can contain secrets; redact environment variables, tokens, cookies, and long private payloads, and cap bytes. Diagnostics can be stale or unavailable; label timestamps and uncertainty. A bug in correlation could attach evidence to the wrong action, so use immutable job/action IDs and test concurrent jobs.
- cost: Negligible API cost; small local storage bounded per job (for example 32–128 KB). Engineering cost is primarily typed serialization, redaction, and dashboard integration.  ·  latency: Adds roughly 100–500 ms for local diagnostics; avoid collecting expensive system_profiler data unless explicitly requested or a failure requires it.
- security: Improves auditability without changing the owner's maximum-access policy. Keep bundles owner-scoped, redact sensitive fields before persistence, and never expose unrestricted environment or raw authenticated browser content by default.
- depends on: Implement the granted mac_read_diagnostics/mac_readonly_diagnostics interfaces (currently schema-only/no implementation).; Stable action/job correlation IDs from actionReceipts.js.; Existing /jobs and dashboard receipt surfaces.


## What it asked for

_Nothing._
## Its own summary

I discovered the current 64-item backlog and confirmed the new Mac diagnostic grants are still schema-only: mac_read_diagnostics, mac_readonly_diagnostics, and mac_readonly_diagnostics_impl all return “no implementation yet.” I proposed a genuinely new cross-surface capability: “Do it, and make sure it actually worked,” combining pendant goal capture, relay durability, Mac execution receipts, and authenticated-browser or filesystem postcondition verification with retry/reroute instead of trusting exit code. I also proposed a Mac evidence-bundle change that correlates redacted stdout/stderr, host state, job IDs, and timestamps without adding gates or reducing FULL_CONTROL_MODE.

**Biggest unknown:** Whether the orchestrator will implement the granted diagnostic interfaces and a shared typed postcondition/verifier protocol. I do not need another permission this round; I need those implementations to turn the proposals into live behavior.

