# Harness derivation — mac-planner — round 58

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-reachability-2026-08-07T10:41** — Mac bridge is online but not execution-ready: Accessibility trusted=false due to grant mismatch (com.aipendant.agent), screenRecording=false, input reachability failed, and ui actions would report success without reaching the screen. Browser extension is offline with 3 pending commands. Recent browser jobs failed and have linked failure receipts; no repair/retry receipt exists.
  - evidence: GET /observe and GET /ops/status at 2026-08-07T10:40:58Z; GET /jobs shows failed browser_navigate receipts.

## Capabilities it proposed

### "When I press and hold the pendant, hide sensitive work everywhere immediately; when I release and authenticate again, restore exactly what I was doing."
- **useful because:** The owner gets a physical, dependable privacy reflex: a visitor, shared screen, or unexpected recording can be handled without finding the Mac or speaking aloud. Restoring the prior tabs, windows, and paused voice state avoids losing work while ensuring private content does not remain exposed.
- **path:** pendant → relay-realtime → mac-vision → browser-extension → mac-planner
- **model tier:** Realtime only for the pendant command and acknowledgement; deterministic local handlers perform the lock/redaction and restoration, with no model call for the emergency path.
- **latency:** Local pendant event to Mac/browser privacy action under 1 second when connected; relay fallback acknowledgement under 2 seconds. Restoration can take up to 5 seconds and must report any surface that could not be restored.
- **cost:** Near-zero per use; a small realtime event/ack payload dominates, with no vision or text generation. Engineering cost is a coordinated state journal and platform-specific privacy controls.
- **security:** The hide operation must be fail-closed and work without microphone or speech. The pendant should send only a signed event, not screen contents. Mac should lock or cover the display and suspend synthesized input; the browser extension should replace authenticated page content with a local blank/lock view and cancel queued commands. Persist an encrypted, short-lived restoration manifest containing window/tab identifiers and paused-job IDs, never page text or passwords. Resume requires a deliberate pendant gesture plus Mac-unlock/biometric confirmation; if the link drops, local Mac and browser watchdogs retain the hidden state rather than exposing content.
- **missing:** A pendant firmware emergency privacy event with reliable delivery and local retry; A Mac privacy-controller service that can instantly lock/blank the display and freeze planner/vision execution, then restore a verified window state; A browser-extension privacy curtain that hides authenticated DOM and cancels or pauses pending commands without destroying sessions; Relay support for signed privacy-state fan-out and encrypted, expiring restoration manifests; A cross-surface state machine and test harness proving hide completion and safe recovery under link loss, app crashes, and partial restoration


## Changes it proposed to its own stack

### `integration` — Add a cross-surface reachability watchdog and repair handshake. Before any UI/browser plan, the relay asks the Mac bridge for a signed preflight containing host fingerprint, Accessibility/Input Monitoring/Screen Recording state, foreground app, and browser-extension heartbeat. If stale or mismatched, do not execute deceptive UI steps: persist the plan, notify the pendant with a short offline-safe repair prompt, and have the Mac open the exact System Settings Privacy pane (or extension enablement page). After the owner repairs it, the bridge must heartbeat with the new fingerprint and run a zero-delta input plus no-op target probe; only then release the queued plan. Failed attempts and repair/retry receipts should be linked to the original job, with a TTL and explicit 'not run' status.
- **owner gets:** Today a desktop action can report success while doing nothing because macOS granted Accessibility to a different binary; browser work can also sit behind an offline extension. This makes the pendant trustworthy: it tells the owner exactly what is broken, preserves the request while they fix it, and resumes only after verified reachability instead of silently losing work or claiming completion.
- effort: Medium: Mac bridge preflight/verification and System Settings deep links, relay queue state and receipt linkage, pendant notification/retry message, plus tests for binary updates and extension reconnects.  ·  risk: A queued plan could resume after the owner forgot its context; expire plans after a short TTL, summarize the exact pending actions, and require the existing owner policy's normal execution semantics (no new approval gate). If verification is flaky, mark not-run rather than execute blindly. System Settings URLs vary by macOS version, so retain a manual fallback prompt.
- cost: Negligible API cost (small JSON preflight/heartbeat); modest local implementation/storage for queue and receipts. No new cloud data beyond hashes, status, and job metadata.  ·  latency: ~100–300 ms preflight when healthy; repair path is human-time. Avoids 45-second browser failures and false-success retries.
- security: Improves security by binding authorization to the currently running signed host identity and refusing unverified synthesized input; do not upload screen contents. Store only permission state/fingerprint and redact app/window details in relay logs.
- depends on: Implement the granted mac_readonly_inspect backend (currently schema exists but returns 'no implementation'); Add a Mac action preflight/verification endpoint or equivalent bridge RPC; Relay durable pending-plan and receipt linkage; Pendant notification/audio queue for repair prompts


## What it asked for

_Nothing._
## Its own summary

Fresh live checks confirm the Mac bridge is online but not actually reachable for UI execution: Accessibility is false due to a binary/grant mismatch, Screen Recording is false, input probe failed, and browser extension is offline with three pending commands. Recent browser attempts have failure receipts only; no repair/retry receipt exists. I informed faculty-action and recorded the finding. I proposed a new cross-surface reachability watchdog/repair handshake that queues work, guides repair via pendant/Mac, verifies reachability, and resumes with linked receipts.

**Biggest unknown:** Whether the owner can currently repair macOS Privacy permissions for the AI Pendant Agent and re-enable the browser bridge; the granted mac_readonly_inspect interface still has no backend implementation, so I cannot independently verify UI state beyond /observe.

