# Harness derivation — mac-terminal — round 107

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac action reachability and truthful execution** — At 2026-08-07T14:02Z the Mac agent is full-control but not ready: Accessibility trusted=false, eventsPost=false, screenRecording=false, inputReachability failed; /observe explicitly warns UI actions report success while doing nothing. Browser extension is offline with 9 pending commands. /journal totals 120 retained jobs, 146 actions, 18 failed, 0 undoable, and 112 unattributed tier receipts.
  - evidence: Authenticated GET /ops/status, GET /observe, GET /journal, and GET /routing in round 107.

## Capabilities it proposed

### "When I tell you to do something on my computer, use whatever route can actually reach it, and tell me plainly if it was completed, partially done, or impossible—never say success when the Mac or browser could not receive the action."
- **useful because:** The current Mac agent can produce false success receipts: live observation shows Accessibility is not trusted and synthesized UI events are rejected, while browser commands are queued with the extension offline. A pendant-to-relay-to-Mac planner can preflight reachability, choose shell/AppleScript/browser/UI appropriately, and return a spoken, evidence-backed outcome instead of silently claiming completion.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Use deterministic readiness checks and receipt reconciliation first; use background gpt-4.1-mini to summarize multi-step outcomes; reserve realtime gpt-realtime-2.1 for the spoken explanation and only escalate ambiguous recovery decisions to planner gpt-5.6-luna.
- **latency:** Under 1 second for /ops/status + /observe + /browser/status preflight; 2–4 seconds for deterministic or shell fallback; up to 10 seconds for a multi-step recovery. Speak an immediate 'unable to reach UI/browser' status when a route is offline, then continue only through an explicitly viable route.
- **cost:** Typically near-zero model cost for preflight and typed receipt reconciliation; roughly 2k–4k input tokens on gpt-4.1-mini only for a complicated multi-action summary, with realtime used for the short final voice response.
- **security:** Readiness telemetry includes foreground app, running apps, browser URLs/titles, permission state, and command outcomes; keep it local to the Mac/relay and send only the minimum status needed. FULL_CONTROL_MODE remains unrestricted as the owner requires—this is observability and truthful reporting, not a new gate. Shell fallbacks can mutate permanently, so receipts must label undoability and capture stdout/stderr, exit status, and evidence.
- **missing:** A preflight contract that maps action classes to reachability facts (Accessibility/input, Screen Recording, browser heartbeat, active tab/session).; Executor-side verification that a UI action caused an observable state change rather than trusting an API return value.; A planner fallback matrix (AppleScript/shell/browser/UI) and a terminal outcome enum: completed, completed-with-fallback, queued-offline, failed, or blocked-by-host-permission.; A relay/dashboard timeline that joins the pendant request, chosen route, preflight snapshot, action receipts, and final spoken result.

### "Make computer control work again, and walk me through whatever my Mac needs—then verify it actually works before trying the task again."
- **useful because:** Today the Mac agent can detect that Accessibility is granted to the wrong binary, but the owner receives no end-to-end repair flow; UI actions can appear successful while doing nothing. This would turn an opaque broken setup into a guided, verified recovery: the pendant explains the one fix needed, the Mac opens the exact System Settings destination, and a no-op reachability probe confirms the repair before any real action is attempted.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → dashboard-ux
- **model tier:** Deterministic Mac diagnostics and a fixed repair state machine do the work; use the realtime model only to speak the next instruction and answer questions. Use a cheaper background model to summarize persistent failures; no planner-tier call is needed unless the permission UI differs across macOS versions.
- **latency:** Detect in under 1 second, open the relevant settings page within 2 seconds, and verify within 5 seconds of the owner completing the step. If the owner is away, leave a durable repair task and resume when the Mac bridge reconnects.
- **cost:** Near-zero model cost for diagnosis, launch, and probe; at most a short background summary (about 1k–2k input tokens) for an unusual OS error. No hardware cost.
- **security:** Permission state and host identity remain on the Mac; relay receives only a coarse repair status and no screen image unless the owner explicitly enables it. Opening System Settings is reversible, but changing permissions remains visibly owner-controlled by macOS. Never claim repair from the settings-page launch alone; require the input reachability probe.
- **missing:** A version-aware permission-repair state machine that distinguishes the running AI Pendant Agent binary from stale or differently signed Accessibility grants.; A typed action to open the exact Privacy & Security > Accessibility destination and return a deep-link/open result.; A post-repair reachability probe whose result is bound to the same executable identity used for real UI events.; A resumable pendant-to-Mac repair job with spoken instructions, timeout, reconnect handling, and a final verified receipt.


## Changes it proposed to its own stack

### `integration` — Wire a non-blocking execution preflight and verification envelope into every Mac/browser job. Before dispatch, snapshot /ops/status, /observe, and /browser/status; annotate each action with viable routes and host readiness. After dispatch, require route-specific evidence (exit code/stdout for shell, changed app/window or state query for UI, browser result/heartbeat for extension) and classify the job as completed, completed_with_fallback, queued_offline, failed, or host_unreachable. Persist the preflight and evidence references in the existing job receipt/journal, and have relay-realtime speak the concise result to the pendant. Do not gate or reduce FULL_CONTROL_MODE.
- **owner gets:** The owner gets an honest answer and useful fallback when a command cannot reach the Mac. Today /observe proves UI event calls can report success while doing nothing, and the browser has nine commands queued while offline; this change prevents lost time and makes unattended work recoverable.
- effort: Medium: shared preflight schema, executor hooks, route-specific postconditions, journal/dashboard rendering, and planner fallback rules.  ·  risk: Some legitimate actions have no observable postcondition and may be labeled uncertain; preserve raw receipts and allow a later status check. A stale preflight can race with permission or connectivity changes, so timestamp every snapshot and re-check after failures.
- cost: No new hardware or API spend. Deterministic checks add negligible CPU and under ~1k tokens only when a model must summarize an unusual failure.  ·  latency: Adds roughly 100–500 ms for local preflight and state verification; no extra LLM turn on ordinary shell actions.
- security: Telemetry may include active app and browser metadata; keep full snapshots local and project a minimal status to relay. Does not introduce approvals or restrict the owner's unrestricted shell policy.
- depends on: Existing /ops/status, /observe, /browser/status, /jobs/:jobId/receipts, and /journal/:jobId routes; A typed postcondition schema for shell, AppleScript/UI, and browser actions; Relay outcome event and dashboard rendering

### `hardware` — Add a low-power coin vibration motor and a dedicated charge/alert controller to the pendant, with firmware patterns for relay-connected, request accepted, completed, failed, and stale/offline states. Keep the LED as a redundant visual channel and expose a quiet-hours setting from the Mac dashboard.
- **owner gets:** The owner can know whether a remote Mac/browser task finished without looking at the pendant or hearing speech—especially while walking, in a meeting, or when the Mac is offline. This gives the wearable a reliable physical status channel that the current single-LED prototype cannot provide.
- effort: Low-to-medium hardware revision: motor, transistor/driver, PCB/enclosure revision, vibration patterns, battery characterization, and firmware event plumbing.  ·  risk: Vibration can be distracting or drain the small battery; cap pulse duration, provide quiet hours, and fall back to LED-only on low battery. Mechanical noise may be undesirable in meetings.
- cost: Approximately $1–$3 in components at prototype volume plus PCB/enclosure revision; brief pulses add negligible average draw but require battery validation.  ·  latency: No meaningful network or model latency; local notification begins as soon as the pendant receives the relay event.
- security: No new data leaves the device. Only compact outcome codes and timestamps are required; command contents remain off-device.
- depends on: A compact relay-to-pendant outcome event carrying request id, state, and timestamp; Firmware state machine for action outcomes and quiet-hours configuration; Battery telemetry and durable reconnect handling


## What it asked for

### `s15-cbhs` (skill) — truthful_action_status_beacon
- does: Displays the last known remote-action state on the pendant's single LED and button: brief pulse for dispatched, double pulse for completed, slow amber/error pattern for failed or host-unreachable, and a distinct queued-offline pattern. A short button press reads the state aloud when the link is available; if offline, it shows the locally cached state and request age.
- must be on-device because: The owner needs immediate, glanceable feedback while away from the Mac and this must remain useful through a dropped relay link. The pendant is the only surface physically attached to them; server/dashboard receipts cannot provide local confirmation.
- trigger: Relay pushes an outcome event; firmware starts a timeout after a request is acknowledged; button press requests a spoken status when connected; watchdog marks stale in-flight work after a bounded timeout.
- storage: Persist only the latest 4 action summaries in a small flash ring (request hash, enum, timestamp, retry flag), under 256 bytes; do not persist command text or page content.
- RAM budget: ~2–4 kB including event queue, LED state machine, and flash-buffer serialization—well below the 211,608 B application RAM budget. Must coexist with existing audio/modem buffers and avoid retaining LLM text.

## Its own summary

Fresh live discovery found a serious truthfulness gap: /observe reports Accessibility=false, synthesized UI events rejected, screen recording missing, and explicitly warns UI actions can report success while doing nothing; /ops/status shows the browser extension offline with 9 pending commands and agent ready=false. I recorded this, notified faculty-action, proposed a reachability/evidence execution envelope (without gates or reducing FULL_CONTROL_MODE), and queued a pendant LED status beacon so the wearer gets honest completion/failure feedback even when away from the Mac.

**Biggest unknown:** Implementation details remain: which route-specific postconditions can reliably verify shell, AppleScript/UI, and browser actions, and how the executor can persist the preflight/evidence envelope into existing receipts without duplicating the nearby backlog item. I do not need more read access this round; I need that contract implemented and a live Accessibility/browser-heartbeat recheck afterward.

