# Harness derivation — mac-terminal — round 48

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac UI execution truth** — At 2026-08-07T10:40Z the live Mac agent reports ready=false; Accessibility is not trusted for the running AI Pendant Agent binary, synthesized events are rejected, Screen Recording is missing, and /observe warns ui_click/type_text/press_keys can report success while doing nothing. Browser extension is offline with 3 pending commands, although 3 durable browser sessions/tabs remain.
  - evidence: GET /ops/status and GET /observe via probe_http, HTTP 200

## Capabilities it proposed

### "“Make it happen on my Mac even if the computer-use path is broken—and tell me only when it is genuinely done.”"
- **useful because:** Today a Mac UI action can report success while Accessibility rejects the synthesized event, and a browser task can sit behind an offline extension. The owner should be able to hand over a goal once: the pendant and relay should detect the broken route, preserve the job, select a viable Mac shell/browser/UI fallback, or speak one precise repair instruction and resume automatically. Completion must be based on a verified postcondition, not merely a dispatched command.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic local preflight and postcondition checks first; use the background tier to classify a failure and choose a fallback; reserve realtime for the short spoken status and never spend it on long planning.
- **latency:** Immediate readiness diagnosis in under 1 second; fallback execution proceeds asynchronously with a concise spoken update. A permission repair/resume cycle may take as long as the owner needs, but the job remains durable.
- **cost:** Usually no model call when a typed preflight/postcondition rule matches. Ambiguous failures need one small background call (roughly 2k–4k context tokens); realtime cost is limited to the brief voice update. Dominant cost is context sent for failure classification, not execution.
- **security:** The system retains the owner's unrestricted FULL_CONTROL authority and must not silently broaden it. Permission instructions should reveal only the minimum local detail; browser/account content stays in its existing authenticated surface. Any fallback that changes the target should be announced, and irreversible outcomes still need the owner's existing confirmation policy.
- **missing:** A durable cross-surface job state that survives a failed route and records the intended postcondition; Mac preflight/postcondition probes that distinguish completed, failed, and unverified/no-op UI actions; Fallback routing rules from UI to shell or authenticated browser bridge, with idempotency keys; A relay-to-pendant remediation/resume event and a dashboard view showing the exact blocker and proof of completion; A safe, owner-facing way to repair Accessibility/Screen Recording or re-enable the browser bridge without losing the queued job


## Changes it proposed to its own stack

### `mac-harness` — Add an execution-truth layer around every Mac UI action: before dispatch, attach the latest /observe reachability and permission state; after dispatch, run a bounded postcondition probe (foreground app, window title, file/reminder existence, or typed action result). Store an explicit outcome enum—completed, failed, or unverified/no-op—with the exact blocker (for this Mac, Accessibility is granted to a different binary and Screen Recording is missing). Emit a machine-readable remediation event that the relay and pendant can speak, and let faculty-action retry through a non-UI path when one exists. This is observability and recovery, not a gate: FULL_CONTROL_MODE remains unrestricted.
- **owner gets:** The pendant will stop saying an action succeeded when the Mac demonstrably did nothing, and can tell the owner the one concrete fix or use a reliable fallback instead of making them debug silent failures.
- effort: Medium: add pre/post probes to the executor and receipt schema, classify a small set of common postconditions, persist remediation events, and wire relay speech plus retry selection.  ·  risk: Postcondition probes may be inconclusive or add latency; label those as unverified rather than failure, cap probe time, and preserve the raw action receipt for recovery. No action is blocked.
- cost: Small additional local CPU and storage; one short background-model call only when the result is ambiguous, otherwise no API cost.  ·  latency: ~100–500 ms for local probes; retries may add normal command latency.
- security: Improves auditability without narrowing authority. Permission details and paths stay on the Mac unless a remediation summary is explicitly sent to the relay.
- depends on: chg-5fc73ce3 receipt/undo records; GET /observe reachability probe; GET /ops/status readiness state


## What it asked for

_Nothing._
## Its own summary

Fresh discovery completed without opening the microphone. The Mac bridge and relay are online, but /ops/status is not ready: Accessibility is untrusted for the running AI Pendant Agent binary, Screen Recording is missing, and /observe confirms UI actions may claim success while doing nothing. The browser extension is offline with 3 pending commands, despite 3 durable browser sessions. I recorded this finding and proposed a non-blocking execution-truth layer that preflights reachability, verifies postconditions, marks unverified/no-op results honestly, and emits remediation or fallback signals. I do not need another permission this round; the granted diagnostic tools still have no implementation. For the owner, enabling Accessibility for the actual AI Pendant Agent binary (and Screen Recording for vision) is required for reliable UI automation; browser work additionally needs the bridge polling again.

**Biggest unknown:** Whether the orchestrator will implement the granted read-only diagnostic interface and whether the Accessibility grant can be moved from the other binary to the running AI Pendant Agent identity; until then, local UI success receipts cannot be trusted.

