# Harness derivation — faculty-action — round 39

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **reachability** — Mac bridge is online and full-control mode is enabled, but fresh /observe proves synthesized input cannot reach the screen because Accessibility is granted to a different binary; /ops/status reports ready=false. Browser bridge is offline with 3 pending commands. Therefore UI/browser action receipts must be treated as non-execution until fresh proofs transition.
  - evidence: GET /observe at 2026-08-07T10:51:53.909Z: inputReachability.status=failed, eventsPost=false, uiActionsWillReachTheScreen=false; GET /ops/status: accessibility.trusted=false, screenRecording.granted=false, browserExtension.online=false, pendingCommands=3.

## Capabilities it proposed

### "“If something you need to do is blocked, tell me exactly what is unreachable, keep the approved work safe, and resume it automatically once I fix the Mac or browser.”"
- **useful because:** Today the system can claim success while Accessibility events do nothing and browser commands queue behind an offline extension. The owner needs one trustworthy explanation on the pendant, not a misleading receipt or a lost task. This is genuinely cross-surface: the pendant delivers the blocker and receives a local confirmation, the Mac diagnoses/repairs its reachability, the browser bridge reattaches queued tabs, and the relay holds the resumable job.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the realtime tier only to explain the immediate blocker and ask a short local confirmation; use a cheap background worker for queue reconciliation, permission/extension health polling, and replay eligibility.
- **latency:** Immediate blocker speech under 2 seconds; health polling every 10–30 seconds while a job is held; automatic resume within 5 seconds of a verified reachability transition.
- **cost:** Usually <$0.01 per blocked job: polling and state transitions are local/relay work; realtime cost is only one short spoken explanation. No vision/model call unless the owner explicitly authorizes GUI repair.
- **security:** Never infer reachability from a successful API receipt. Require fresh inputReachability and browser-heartbeat evidence, bind the held job to its original tab/session and idempotency key, and require explicit approval before changing permissions, enabling an extension, or replaying an irreversible step. Do not upload screenshots or private page content for diagnosis.
- **missing:** A typed reachability contract emitted by Mac with freshness, binary identity, and proof that synthesized input reached the target; A durable blocked-job state machine spanning relay, Mac jobs, and browser commands (hold, repair-needed, revalidate, resume, expire); A browser heartbeat/command acknowledgement that drains or safely invalidates the existing three pending commands; A pendant-facing short status/confirmation protocol for blocker, repair instructions, and resume/abort; An OS-permission repair path or owner-guided deep link; the agent must remain fail-closed when Accessibility/Screen Recording are absent

### "“If I long-press the pendant, immediately freeze every pending action everywhere, even if the Mac or browser is unreachable, then tell me what was stopped and let me release only the safe ones.”"
- **useful because:** The owner currently has no guaranteed physical override when a queued Mac/browser action is stale, duplicated, or has lost reachability. A pendant-local kill switch gives them control at the one place they always have, while the relay, Mac agent, and browser reconcile the stop when links return. It is not merely an undo receipt: it prevents actions that have not started and marks in-flight work for cancellation across all surfaces.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** No model for the stop path: pendant firmware and relay use a signed emergency-stop event. Use a cheap background model only to summarize the resulting action inventory; realtime is optional for the spoken acknowledgment.
- **latency:** Pendant LED/haptic acknowledgment locally under 100 ms; relay freeze under 1 second when connected; offline stop is durable on the pendant and applied before any queued replay after reconnection.
- **cost:** Near-zero model/API cost for stop and reconciliation; small relay storage for a monotonic stop epoch and per-job cancellation markers.
- **security:** Long-press must be physically deliberate, authenticated to the owner’s paired relay, monotonic, and resistant to replay. It must not claim to reverse an already completed external side effect. On reconnect, every worker checks the stop epoch before starting a step; release requires a fresh deliberate owner confirmation, with irreversible actions never silently resumed.
- **missing:** A pendant-firmware emergency-stop event and durable monotonic stop epoch that survives dropped LTE; Relay-wide cancellation fence checked by Mac jobs, browser commands, and scheduled workers; Mac/browser adapters that distinguish queued, started, and completed work and acknowledge the fence; A dashboard/pendant inventory of frozen jobs with selective release and explicit expiry


## Changes it proposed to its own stack

### `integration` — Implement a cross-surface Reachability Contract and blocked-job coordinator. Mac emits signed, expiring proofs for input posting (host bundle + executable identity + probe result), screen capture, and browser heartbeat/tab ownership. The relay stores an approved job as held when any required proof is absent, while the Mac/browser layers stop claiming success and attach a machine-readable blocker. A repair transition (owner-guided permission deep link or extension-open instruction) causes re-probe; only a fresh proof matching the original session/tab and idempotency key permits replay. Irreversible steps remain approval-gated and are never auto-replayed.
- **owner gets:** The owner stops hearing “done” when nothing happened, and a dropped browser extension or mismatched macOS grant no longer loses a multi-step task. They get a clear pendant explanation, can fix one thing, and the exact safe portion resumes without duplicate sends or clicks.
- effort: Medium-high: shared schema and state machine in relay/Mac agent, browser heartbeat changes, pendant status events, dashboard diagnostics, and failure/replay tests across offline transitions.  ·  risk: A stale or incorrectly scoped proof could permit an action on the wrong tab or binary; mitigate with short TTLs, tab/session binding, nonce probes, fail-closed defaults, and manual approval for writes. Recovery is to expire the held job and present its plan rather than replay.
- cost: Negligible relay/D1 storage and local polling; one short realtime explanation when blocked. Engineering cost is the main cost.  ·  latency: Adds one local probe/heartbeat round (typically <1 s) before action execution; held jobs resume within a few seconds after proof transition.
- security: Improves security by making identity and reachability explicit; no permission is silently granted and no private page data leaves the Mac for diagnosis.
- depends on: Mac inputReachability proof API; browser heartbeat with command/session acknowledgements; durable relay-to-Mac job state and idempotency keys; pendant blocked/resume event protocol


## What it asked for

_Nothing._
## Its own summary

Fresh discovery found a still-unfilled cross-surface gap: the Mac bridge reports full control, yet /observe proves its exact com.aipendant.agent binary cannot post input, and the browser bridge is offline with three pending commands. I recorded this and proposed a Reachability Contract plus durable blocked-job coordinator: signed short-lived proofs, fail-closed receipts, pendant blocker speech, owner-guided repair, and idempotent resume only after a fresh Mac/browser proof. I also proposed the owner-facing capability to safely hold and automatically resume approved work. What remains needed operationally is not another model: the owner must grant Accessibility and Screen Recording to the exact running AI Pendant Agent binary and bring the browser bridge online; implementation still needs the typed proof/state-machine/heartbeat protocols.

**Biggest unknown:** Whether the owner can grant permissions to the exact app-bundle identity (rather than the currently different binary) and whether Safari/Chrome can be made to poll the browser bridge; until then all GUI/browser actions remain unreachable and must not be trusted.

