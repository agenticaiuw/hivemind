# Harness derivation — mac-planner — round 32

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac_readonly_inspect implementation** — The newly granted mac_readonly_inspect schema is present, but every supported operation currently returns 'This tool was granted a schema but has no implementation yet.' It cannot provide running apps, browser tabs, foreground app, accessibility, or directory state this round.
  - evidence: Four parallel calls for running_apps, browser_tabs, foreground_app, and accessibility_enabled all returned the same implementation error.

## Capabilities it proposed

### "“Start handling this, but if I say stop—or I lose connection—pause every part safely and tell me exactly what already happened.”"
- **useful because:** Today a spoken request can fan out across the relay, Mac apps, and authenticated browser, but interruption can leave partial edits, open tabs, drafts, or queued jobs with no single truth about what completed. This gives the owner a reliable stop/resume boundary instead of guessing whether it is safe to continue.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the realtime model only to recognize the owner's stop/resume command and acknowledge immediately; use a cheaper background planner to execute and reconcile steps. Mac and browser workers emit receipts to the relay, which maintains the job's cancellation state and the dashboard renders the partial-result ledger.
- **latency:** Stop acknowledgement under 500 ms from the pendant; workers should reach a cancellation checkpoint within 2 s. Resume can take 2–5 s to reconcile receipts and inspect current tabs/files before continuing.
- **cost:** Low per stop/resume event: one short realtime turn plus background reconciliation; dominant cost is re-reading browser/Mac state after an interrupted or disconnected job, not the cancellation signal.
- **security:** The stop signal and job identity must be authenticated and replay-safe; a stale pendant command must not cancel a newer job. No data needs to leave the Mac beyond typed receipts and redacted result metadata. Never claim rollback: report irreversible mutations separately, and require explicit confirmation before resuming a job whose external side effects are unknown.
- **missing:** A cross-surface cancellation token propagated from relay to Mac and browser workers; Checkpoint contracts for mac_run_actions and browser jobs, including completed/in-flight/unknown states; A durable per-step receipt and reconciliation endpoint with idempotency keys; Pendant firmware/server handling for disconnect-triggered pause versus intentional completion; Dashboard view for partial effects, resumable checkpoints, and explicit resume/abandon

### "“Give me a physical privacy button: when I press it, stop all AI watching and automation everywhere, close or blur any AI-opened sensitive views, and tell me what was retained—without losing my unfinished work.”"
- **useful because:** The owner needs a trustworthy way to revoke observation across the pendant, relay, Mac, and authenticated browser at the moment a private conversation, password, or sensitive document appears. A software setting is hard to reach under pressure and cannot reliably stop already-running workers. This gives an immediate physical boundary while preserving resumable task state rather than silently abandoning it.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** No model is needed for the first safety action: pendant firmware emits a signed local privacy-stop event, and relay/clients enforce it deterministically. Use a cheap background model only afterward to summarize retained-versus-erased artifacts; never invoke the realtime model during the privacy transition.
- **latency:** Pendant acknowledgement under 200 ms locally; relay fan-out and worker halt within 1 second when connected. If disconnected, the pendant must still stop local capture/queueing immediately and apply the stop when the link returns.
- **cost:** Negligible per event; signed control messages and bounded deletion receipts dominate. Optional post-event audit summarization is a small background-model call.
- **security:** The stop event must be authenticated, monotonic, and impossible for a browser page or model output to forge. Default behavior should be fail-closed: no new screenshots, DOM extraction, microphone/audio buffering, or desktop actions after the event. Erasure must distinguish deleted data from data already exported, and report unavoidable retained audit metadata honestly. The owner should be able to resume only with a deliberate physical gesture or spoken confirmation after the privacy state is visible.
- **missing:** A dedicated pendant button/gesture and firmware event with local fail-closed behavior; Relay-wide privacy lease propagated to Mac, browser extension, and queued jobs; Client-side kill switches for screenshots, DOM reads, audio, and action execution; A bounded retention/erasure ledger proving what was deleted, retained, or already transmitted; A visible and spoken privacy-state indicator plus explicit resume gesture


## Changes it proposed to its own stack

### `relay` — Add a durable distributed job lease and cancellation protocol. Every multi-surface job gets a cryptographically random generation, lease expiry, and monotonic step sequence. Mac and browser workers heartbeat at checkpoints and append typed receipts (started, completed, skipped, in-flight, unknown). A pendant stop or link-loss policy changes the lease to PAUSED; workers refuse new steps, finish only their current safe atomic operation, and append a final receipt. Resume first reconciles receipts against live Mac/browser state, then continues only from an idempotent checkpoint. Preserve a tombstone so delayed workers cannot mutate an abandoned generation.
- **owner gets:** The owner can interrupt automation without wondering whether it kept typing or submitting after they walked away, and can resume later without duplicated calendar edits, files, or web forms. They get a truthful list of what happened, what may still be in flight, and what needs manual inspection.
- effort: Medium-high: relay state machine and storage, worker SDK changes in Mac and browser harnesses, disconnect semantics on pendant, and a small dashboard/voice status surface. Requires fault-injection tests for dropped links, duplicate receipts, app crashes, and delayed packets.  ·  risk: A worker may crash after performing a mutation but before its receipt, so reconciliation must classify the step as unknown rather than replaying it blindly. Lease expiry can pause legitimate long operations; use explicit atomic-operation windows and bounded grace periods. Recovery is abandon-plus-manual-review when state cannot be proven.
- cost: Small durable relay storage and heartbeat traffic; background model calls only on resume reconciliation or unknown steps. No meaningful pendant power increase if pause is a server-side lease event.  ·  latency: Negligible during normal execution (small receipt/heartbeat overhead); stop acknowledgement is immediate, while safe pause and resume reconciliation take roughly 1–5 seconds depending on open apps/tabs.
- security: Improves containment by preventing stale or replayed workers from acting after stop/abandon. Receipts should contain hashes and redacted metadata by default, with sensitive page content retained only locally unless the owner requests it.
- depends on: Existing request IDs/tab affinity/idempotency work for browser jobs; Mac action result receipts and a typed step identity in mac_run_actions; Relay job persistence and a defined disconnect policy; A read-only Mac/browser reconciliation inspection path

### `hardware` — Add a dedicated, physically recessed privacy-shutter button to the pendant, backed by a hardware-latched privacy state rather than a model-interpreted gesture. Pressing it cuts microphone/audio buffering and marks the device unable to enqueue new sensor data until a deliberate long-press resume. On reconnect it sends a signed, monotonic privacy epoch to the relay, which fans that epoch to Mac and browser workers; any worker with an older epoch must refuse reads, screenshots, DOM extraction, or actions. Store only the epoch and a compact local event receipt in flash.
- **owner gets:** The owner gets a clear, dependable way to make the whole system stop looking or acting when privacy suddenly matters—even if the network or model is unavailable—and can later verify whether anything was retained before resuming.
- effort: High: pendant PCB/button and firmware changes, relay epoch enforcement, browser-extension and Mac worker kill switches, plus retention-audit UI and failure-injection testing across disconnects and process crashes.  ·  risk: A false press can interrupt useful work; resume remains easy but deliberate. Hardware failure must default to privacy-off for capture and actions, while preserving ordinary device controls. A client that ignores the epoch is a security defect, so relay and dashboard need heartbeat attestation and visible noncompliance reporting.
- cost: Roughly a few dollars BOM and negligible idle power; a hardware latch may add a few microamps. Runtime API cost is negligible except optional background audit summarization.  ·  latency: Local shutoff is sub-200 ms; connected clients should halt within about one second, with offline clients enforcing the latch immediately.
- security: Strongly improves privacy containment by making revocation physical, signed, monotonic, and fail-closed. Do not upload raw retained content for the audit; send only hashes, classes, timestamps, and deletion status.
- depends on: Pendant firmware event channel and local persistence; Relay-wide epoch/lease enforcement; Mac and browser worker cancellation hooks; Durable retention and deletion receipts


## What it asked for

_Nothing._
## Its own summary

Round 32 produced a new cross-surface capability: interruption-safe automation. A spoken “stop,” pendant disconnect, or explicit abandon pauses the relay job lease, prevents stale Mac/browser workers from starting further steps, records completed/in-flight/unknown effects, and supports receipt-based resume without duplicate mutations. I also proposed the relay lease/cancellation protocol with generation IDs, monotonic steps, heartbeats, typed receipts, tombstones, and reconciliation. I verified that the newly granted mac_readonly_inspect interface is not implemented: all four inspection operations failed identically, so current-state reconciliation cannot yet be built or tested.

**Biggest unknown:** Whether the Mac and browser executors already emit durable per-step idempotency receipts and can stop between atomic operations; the missing read-only inspection implementation prevents validating that against live apps, tabs, and files. Still needed from the system: implement mac_readonly_inspect, expose worker cancellation/checkpoint hooks, and define the pendant disconnect policy (pause versus abandon).

