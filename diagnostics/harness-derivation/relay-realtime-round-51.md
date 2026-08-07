# Harness derivation — relay-realtime — round 51

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Keep working on that long task after I walk away, and let me know what happened when it finishes."
- **useful because:** The owner is often away from the Mac. This lets a multi-step job continue across surfaces and then report back to the pendant without the owner babysitting it.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime only for acknowledgement and status playback; planning and execution on a cheaper planner tier; browser automation on browser harness when online; server browser run for public pages when Mac is offline.
- **latency:** Acknowledge in under a second; execution may take minutes. Status checks should be instant from relay records, and final notification should arrive as soon as completion is detected.
- **cost:** Low per status check (relay record read). The expensive part is cross-surface planning and browser automation, dominated by page reads/extraction and tool calls.
- **security:** Must not leak private content across surfaces. Keep provenance and citations, and only speak a pre-sized status message. Drafts must not be sent without explicit confirmation.
- **missing:** A durable job runner that can resume after disconnects; A completion notification path to the pendant (push or poll); A cross-surface action commit protocol with idempotency and postcondition verification; A typed context projection service to avoid resending large context each turn; Reliable browser session attachment with provenance-aware extraction

### "While you are carrying out a task on my Mac or in my browser, let me say 'stop', 'skip that', or 'instead do X' into the pendant and have the current work safely pause, incorporate my correction, and continue without starting over."
- **useful because:** The pendant is worn while the owner is away from the Mac, so a planned action can become wrong before it finishes. Today the owner must wait, issue a separate request, or risk an unattended task continuing with stale intent. A spoken mid-task correction makes the hive responsive to the owner's latest instruction rather than blindly completing an obsolete plan.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime handles only the short interruption classification and immediate spoken acknowledgement; mac-planner performs the slower replan, while mac-vision/browser-extension execute the revised steps. The relay remains the session coordinator.
- **latency:** Pendant must acknowledge stop/pause locally or through the relay within 500 ms; pause propagation within 2 s; revised plan can take 3–10 s. If the link is lost, the device records the interruption and the executor remains paused until a durable decision is available.
- **cost:** Roughly one realtime turn for the interruption plus one cheaper planner call only when the owner gives a redirect; ordinary task execution cost is unchanged. Dominant cost is the replan context and current-state evidence, not the short voice command.
- **security:** The interruption must bind to the active job/session and reject ambiguous 'stop' when no job is active. The spoken audio/transcript and current action state leave the pendant for interpretation. Pause must be fail-safe, idempotent, and preserve a receipt of what was already done; resuming or redirecting mutations should be logged, while the owner's stated maximum-access policy means no confirmation gate is required.
- **missing:** A durable bidirectional control channel from pendant voice sessions to an in-flight job, including job-bound pause/cancel/redirect commands; Executor checkpoints that can halt between actions and report the exact last committed action; Planner API accepting a correction plus checkpoint/evidence and returning a replacement suffix rather than a fresh unrelated job; Browser-extension and Mac action runners must honor pause leases and avoid starting a queued action after a stop; Relay speech-state handling that distinguishes interruption commands from a new independent request; Dashboard timeline showing original intent, interruption, committed prefix, and revised suffix

### "Remember this exact way I completed the task, turn it into a named routine, and let me invoke that routine later by voice from the pendant across the same Mac and browser accounts."
- **useful because:** The owner repeatedly performs personal workflows that are too specific for a generic assistant. Today the hive can execute one-off goals but cannot turn a demonstrated successful Mac/browser sequence into a durable, editable shortcut that remains callable from the worn device. This would convert expertise demonstrated once into reliable daily leverage.
- **path:** pendant → relay → mac-vision → browser-extension → mac-planner → dashboard
- **model tier:** mac-vision and the browser extension capture structured semantic steps during the demonstration; a cheaper background planner generalizes and parameterizes them. Realtime only names, confirms, or invokes the routine and should not summarize the whole trace.
- **latency:** Capture must add less than 100 ms per observed action. Routine creation may take 5–15 s after the demonstration. Invocation should acknowledge within 500 ms and begin execution within 2 s, with parameter questions asked through the pendant only when genuinely missing.
- **cost:** One background planner call per routine creation and a small planner call per invocation when parameters or UI drift require adaptation. Storage and action receipts dominate long-term cost; routine invocation otherwise costs the same as the underlying Mac/browser work.
- **security:** The trace may contain private page contents, typed text, URLs, and account identifiers, so sensitive fields must be redacted or represented as runtime slots rather than persisted. Routines must be scoped to the owner's device/account, versioned, revocable, and report exactly which steps ran. The owner permits maximum access, so this needs transparency and recovery rather than an approval gate.
- **missing:** A cross-surface demonstration recorder that converts Mac and browser events into semantic actions while excluding passwords and secrets; A durable routine registry with names, parameters, device/account scope, versions, disable/delete, and provenance; A planner compiler that turns a trace into a parameterized routine and can adapt it when the UI changes; A pendant-to-routine invocation and parameter-slot protocol; Replay support in Mac and browser executors with per-step checkpoints, receipts, and safe recovery after drift; Dashboard UI to review, edit, test, and revoke recorded routines

### "Give me a spoken privacy freeze: immediately stop all active Mac/browser work, revoke the relay's live session leases, and tell me what was paused; later let me say 'resume my work' to restore only the explicitly selected jobs."
- **useful because:** Because the pendant is always with the owner while the Mac may be unattended, the owner needs an emergency boundary that follows them rather than requiring access to the Mac or dashboard. Today there is no single owner-controlled command that atomically freezes every surface and makes the resulting state legible. This is useful during travel, a sensitive meeting, a lost pendant, or suspected misrouting.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** The freeze phrase should use a tiny deterministic classifier (and ideally a physical button chord) rather than the expensive realtime model. Realtime can explain the resulting state. Background reconciliation can enumerate jobs and verify leases without consuming the low-latency tier.
- **latency:** Local pendant trigger and relay lease revocation under 1 s; Mac/browser runners must stop before their next action and report within 3 s. Reconciliation and resume can take several seconds and must never silently restart work.
- **cost:** Negligible per freeze; periodic lease heartbeats and one reconciliation call dominate. Resume may require a planner call for jobs whose state changed while frozen.
- **security:** This is intentionally a high-authority owner control, so it needs authenticated device identity, replay protection, durable audit records, and an offline-safe local trigger. It must distinguish freeze from resume, preserve already-completed receipts, and avoid deleting evidence. Spoken status must not read sensitive page data aloud unless explicitly requested. If the relay is unreachable, the pendant should retain the freeze intent and apply it when connectivity returns; a firmware emergency flag may be needed.
- **missing:** A cross-surface lease/revocation registry with a global owner freeze epoch; Mac and browser executors that check the freeze epoch before every action and heartbeat their lease; Authenticated pendant emergency trigger with offline persistence and replay-resistant uplink; Relay reconciliation that inventories paused, completed, and unknown jobs and produces a terse voice-safe report; Explicit per-job resume protocol that requires fresh state inspection after a freeze; Dashboard privacy-state indicator and audit/export controls


## Changes it proposed to its own stack

### `relay` — Add durable relay checkpoints and completion subscriptions: when a plan is handed off, persist a compact job manifest and a list of completion signals (Mac job receipt, browser run result, perception postcondition). Provide a status stream that can be spoken verbatim on the pendant and a small notification queue for the next reconnect.
- **owner gets:** They can ask for something, walk away, and later hear exactly what happened without re-asking or keeping the Mac awake.
- effort: Medium-high: requires a storage-backed job ledger, a notification queue, and integration with downstream receipts. Needs coordination with mac-bridge and browser harness.  ·  risk: Duplicate work or false completion if signals are miswired. Mitigate with idempotency keys, leases, and postcondition verification.
- cost: Storage reads/writes per job; minimal compute. Main cost is downstream automation calls.  ·  latency: Adds negligible overhead to acknowledgement; improves status check latency because relay can answer without contacting devices.
- security: Stores summaries and references; must enforce retention limits and avoid storing sensitive payloads. Encrypt at rest if supported.
- depends on: Cross-surface Action Commit Protocol with explicit prepare/commit and postcondition verification; Typed context projection to avoid resending large context blobs

### `browser-harness` — Implement a dual-path browser runner: authenticated Safari bridge when Mac is online, and Cloudflare Browser Run for public pages when it is not. Use a shared step model (navigate/read/extract/click) with provenance, typed results, and an idempotency key per request.
- **owner gets:** The system can still gather public information and summarize it even when the Mac is offline, while keeping private account work on the Mac.
- effort: High: needs a shared action schema, result typing, provenance, and a durable command queue.  ·  risk: Automation drift and unintended clicks. Reduce risk with typed actions, explicit irreversible checkpoints, and read-first workflows.
- cost: Higher cost for browser automation; dominated by page loads and extraction. Relay should avoid doing this inline.  ·  latency: Long-running; should run off the realtime tier. Relay only acknowledges and reports status.
- security: Public pages can run on server browser; private pages must remain on the Mac bridge to avoid credential leakage.
- depends on: Reliable browser command queue with request IDs and session affinity; Durable job runner; Provenance-aware extraction records


## What it asked for

_Nothing._
## Its own summary

Recorded three new cross-surface capabilities: spoken mid-flight pause/redirect with checkpointed replanning; demonstration-to-routine recording and later pendant invocation; and an authenticated pendant privacy freeze/resume control spanning relay, Mac, and browser. Each names the missing protocols, persistence, executor behavior, and firmware/server changes rather than assuming current wiring.

**Biggest unknown:** Which existing job and executor state model should become the canonical source for implementing the pause/redirect and global-freeze leases; I did not perform further discovery per instruction.

