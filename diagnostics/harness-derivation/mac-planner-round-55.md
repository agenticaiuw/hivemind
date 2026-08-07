# Harness derivation — mac-planner — round 55

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-bridge readiness** — Live Mac agent is online and full-control enabled, but not ready: Accessibility trusted=false and Screen Recording granted=false. Browser bridge home-chrome is offline with 3 pending commands. The newly granted mac_readonly_inspect and mac_read_sources tools currently return 'schema but no implementation'.
  - evidence: GET /ops/status HTTP 200 and GET /browser/status HTTP 200; direct calls to mac_readonly_inspect/mac_read_sources returned implementation errors.

## Capabilities it proposed

### "“Handle this browser task even if the browser bridge is asleep; wake the right browser, resume when it is available, and tell me exactly where it stopped if it cannot recover.”"
- **useful because:** Today a browser action waits ~45 seconds and fails because the extension is offline, leaving three pending commands and no automatic recovery. This makes the pendant useful away from the Mac: the relay can hold the intent, the Mac can bring Safari/Chrome and the bridge forward, and the job can resume without the owner repeating themselves.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for recovery/orchestration; realtime only for the short spoken status
- **latency:** Acknowledge immediately; attempt bridge recovery for up to 60 seconds, then leave a resumable job and concise spoken explanation.
- **cost:** Low: mostly polling/desktop actions; one background model call only when interpreting a recovery failure, roughly <$0.01 typical invocation.
- **security:** Opening a browser is local and reversible, but authenticated tabs remain private. Never submit or resend a mutation after reconnect without preserving the original idempotency key; show the owner the exact queued step and require their existing approval semantics for any send/submit action.
- **missing:** A bridge self-heal routine that can launch the selected browser and verify extension polling; Durable retry state tied to browser request id/idempotency key and step checkpoint; Relay-to-pendant progress events and a dashboard action to resume/cancel; A typed distinction between transport failure, permission failure, and completed-but-unacknowledged mutation

### "“I have to leave—save exactly where I am, keep the private details on my Mac, and let me resume this same task from the pendant or another device later without starting over.”"
- **useful because:** Today the owner can queue a command or leave a document open, but cannot create a trustworthy, cross-device handoff of an in-progress task: the exact browser tab, app selection, unsaved draft, scroll/selection location, spoken intent, and next safe step are not captured as one resumable object. This would turn interruptions into continuity rather than lost context, while keeping private page content local.
- **path:** pendant → mac-bridge → browser → relay → dashboard → iOS
- **model tier:** Background model to summarize and checkpoint the task; realtime only to acknowledge the handoff and answer a resume request.
- **latency:** Checkpoint in under 3 seconds after the spoken command; resume brief in under 5 seconds when the Mac/browser is reachable; otherwise deliver a compact pendant summary and retry when a device returns.
- **cost:** Usually <$0.02 per handoff, dominated by one small background summarization call; local state capture and encrypted metadata are otherwise negligible.
- **security:** Drafts, authenticated URLs, and UI screenshots may contain sensitive data. Keep raw content and screenshots encrypted on the Mac, send the relay only an opaque task id, capabilities, and redacted summary, bind resume to the same browser profile/device, and require the owner's existing confirmation semantics before any external send/submit. Provide expiration and one-tap destruction from the pendant.
- **missing:** A Mac-native task capsule that captures app/browser anchors, unsaved buffers, selection/scroll positions, and a signed next-step checkpoint without relying on screenshots alone; Browser and app adapters that can reattach to those anchors after restart and report when the page changed; Encrypted relay metadata and device-bound resume tokens, including revocation/expiry; A pendant/iOS resume UI with spoken disambiguation when multiple interrupted tasks exist


## Changes it proposed to its own stack

### `browser-harness` — Implement an offline-bridge recovery controller around browser jobs: on transport failure, classify the failure using the Mac agent's live status (extension offline, Accessibility/Screen Recording missing, browser not running, or relay unavailable); launch/open the selected browser and bridge onboarding when safe; wait for a heartbeat lease; resume only the uncompleted checkpoint with the same request/idempotency key; and emit pendant/dashboard progress plus a final receipt. Add a hard 'completed-but-no-ack' state that never replays a submit/send step.
- **owner gets:** A browser request should not simply time out because Safari or its extension is asleep. The owner can ask once from the pendant and get either a recovered result or a precise, actionable reason instead of repeating work or risking a duplicate submission.
- effort: Medium-high: local bridge recovery state machine, relay checkpoint persistence, browser heartbeat integration, and test cases for disconnects at every step.  ·  risk: A reconnect can expose the wrong browser profile or retry a mutation. Mitigate by binding jobs to extension/device/profile identity, never replaying irreversible steps after uncertain completion, and surfacing the exact checkpoint before continuing. If recovery fails, preserve the job rather than dropping it.
- cost: Negligible runtime/API cost; occasional background model classification <$0.01. No hardware cost.  ·  latency: Immediate acknowledgement; 5–60 seconds recovery depending on browser launch and extension heartbeat, versus the current opaque ~45-second failure.
- security: Keeps authenticated content on the owner Mac/browser; adds explicit device/profile binding and audit receipts. Browser launch itself must not grant new permissions or exfiltrate page contents.
- depends on: Browser heartbeat lease/device registry; Durable browser job runner with checkpoint and idempotency support; A real implementation of the granted Mac read-only inspection/status tools (current schemas return no implementation)


## What it asked for

_Nothing._
## Its own summary

Discovered the newly granted Mac read interfaces are present only as schemas, not executable implementations, so I could not inspect running apps, foreground UI, browser tabs, Calendar, or Mail. Live status confirms the Mac bridge is online but not ready (Accessibility and Screen Recording missing), while the browser bridge is offline with 3 pending commands. I proposed a new cross-surface capability and implementation: self-healing browser jobs that wake the browser/bridge, resume from an idempotent checkpoint, and never replay uncertain submissions. I still need the actual implementations of mac_readonly_inspect/mac_read_sources, plus bridge recovery and permission-state handling to make this work end to end.

**Biggest unknown:** Which browser profile and Safari/Chrome extension onboarding path the owner wants used for automatic recovery; without that, waking the wrong profile could expose or act on the wrong authenticated session.

