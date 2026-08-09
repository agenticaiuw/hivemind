# Harness derivation — mac-terminal — round 271

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-system status** — The Mac bridge and Safari browser extension are online and Accessibility/Screen Recording/automation permissions are ready; the nRF9160 pendant is still offline from the device inventory. The requested bounded USB serial diagnostic cannot run because no serial capability is implemented, despite both ports being physically connected.
  - evidence: GET /ops/snapshot returned fullControlMode=true, relay reachable, macBridgeOnline=true, browser online, permissions.ready=true; discover(devices) listed nrf9160-pendant offline; mac_usb_serial_diagnostics returned unresolved with no serial/USB/tty inventory capability.

## Capabilities it proposed

### ""Do this from the pendant, and keep going if the Mac or browser drops: when it's finished, tell me what happened.""
- **useful because:** This would be the system's most useful everyday capability: one spoken request becomes a durable, exactly-once task spanning the worn device, always-awake relay, Mac executor, and authenticated browser. The owner does not have to repeat a task after sleep, Wi-Fi loss, a crashed local agent, or a browser reconnect; the pendant reports queued, running, completed, or failed truthfully.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** gpt-realtime-2.1 only for the initial short intent capture and final spoken status; use deterministic routing and a cheaper background/planner model for decomposition, retries, and summarization.
- **latency:** Acknowledge on the pendant within 1 second; start work within 5 seconds of Mac/browser reconnect; completion can take minutes, with push status rather than keeping a voice turn open.
- **cost:** Roughly one realtime turn for capture plus one background planner call per task; dominant cost is the planner context and any browser page reads, not relay storage or status pushes.
- **security:** The relay must store only a task envelope and opaque references, not browser page contents or secrets. Authenticated browser actions remain on the Mac extension. Mutating Mac/browser steps stay under the owner's existing maximum-access policy, but the task receipt must record the exact step and result so a later retry cannot silently repeat an irreversible action.
- **missing:** A relay durable-task envelope with owner-scoped idempotency key, dependency state, retry schedule, and completion push; Mac boot reconciliation that converts orphaned processing jobs into resumable/failed states and joins each job to its action ledger; Browser command replay that rejects stale command IDs and reports a final compact result to the relay; Pendant-side rendering of a multi-hour queued/running state beyond the existing last-action beacon

### ""Watch this authenticated page for a meaningful change, and only interrupt me when it changes; then make the reminder or Mac action I asked for.""
- **useful because:** The owner can delegate a condition instead of repeatedly checking a logged-in site. The browser is the only node that can see the authenticated page, the relay is the only node that can keep watching while the Mac sleeps, and the Mac is the node that can create a native reminder or perform the requested local follow-up. It turns a private browser session into a useful, low-noise personal sensor.
- **path:** browser → relay → mac-bridge → dashboard → pendant
- **model tier:** Use deterministic DOM/structured-diff checks and a cheap background model only to classify whether a changed region is materially relevant; reserve realtime for the one spoken alert.
- **latency:** Poll or receive page-watch events every 5–15 minutes, classify within 10 seconds, and speak the alert within 3 seconds of relay delivery. No open conversation is required.
- **cost:** Small recurring browser/relay traffic; one cheap classification call only on a changed page, plus one native Mac action. Cost is dominated by page reads, so hash and diff structured fields before sending text to a model.
- **security:** Keep cookies and page bodies on the browser/Mac. Persist only host, URL, selector/field locator, baseline hash, and a redacted evidence capsule. Require an explicit per-watch expiry and never use a change in an arbitrary page as authorization to send messages, buy, delete, or publish.
- **missing:** A durable relay page-watch scheduler that can target the browser session while the Mac agent is offline; A structured browser watch/diff operation (field locator, baseline, threshold, expiry) rather than repeated full-page reads; A relay-to-Mac event route that creates a reminder or queues a typed local action with evidence attached; Pendant notification payloads that include the changed fact and source age, not merely an action status

### ""I’m at my desk with the pendant plugged in—use it as my microphone and speaker right now, even though it has no LTE registration.""
- **useful because:** This makes the hardware useful today rather than waiting for cellular provisioning. The nRF9160 supplies the worn button and microphone path, the Mac supplies network/model access, and the ESP32 audio bridge supplies bench playback; the owner can test the real interaction loop and use the pendant at a desk with the relay unavailable.
- **path:** pendant → mac-bridge → relay → dashboard
- **model tier:** No expensive model is needed for transport negotiation; use the existing realtime voice model only once audio is flowing, with deterministic framing/ack handling on the Mac.
- **latency:** Button-to-stream acknowledgement under 250 ms; audio round-trip under 500 ms on USB; reconnect after unplug/replug under 3 seconds.
- **cost:** No per-use infrastructure cost beyond realtime audio inference. One engineering implementation and modest local logging; USB bandwidth and CPU are negligible.
- **security:** Treat USB as a local authenticated bench transport, not a product LTE path. Bind to the expected device serial identities, expose no relay credentials to firmware, and keep raw audio in memory unless the owner explicitly enables capture. Show a distinct tethered/offline state so the pendant never implies LTE continuity.
- **missing:** A real Mac USB serial reader/framer for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA (the granted diagnostic schema is unresolved because no serial capability exists); A local-agent route that bridges framed pendant audio to the existing POST /pipeline/audio and returns acknowledged playback frames; A dual-chip clock/sequence protocol with bounded buffering and a bench start/stop command; A user-visible tethered mode indicator separate from truthful_action_status_beacon's remote job state

### ""When I leave my Mac, protect my private browser and audio automatically; when I return, restore exactly what I was doing without making me sign in again.""
- **useful because:** A pendant that is physically with the owner can become a continuous presence key, unlike a browser extension or Mac alone. Walking away would pause microphone streaming, mute playback, hide or lock authenticated browser content, and stop queued screen actions; returning would restore the prior session and explain anything that happened while away. This protects the owner's private sessions without forcing them to remember another control.
- **path:** pendant → mac-bridge → browser → relay → dashboard
- **model tier:** Deterministic presence and policy logic; no LLM for lock/unlock. Use a background model only to summarize events that occurred during absence, and realtime only if the owner asks for that summary by voice.
- **latency:** Detect departure within 2 seconds and enforce local privacy actions within 1 second of detection. Resume within 3 seconds after authenticated return. The relay must fail closed locally if disconnected.
- **cost:** Negligible per-event model cost; engineering is dominated by a secure proximity protocol and browser/Mac restore testing. Optional absence summaries cost one small background call per absence interval.
- **security:** Presence must be cryptographically authenticated and resistant to replay or an attacker carrying a copied identifier. The Mac must enforce the privacy action locally even when relay access is lost. Never upload browser contents merely to decide presence. Returning should unlock only the owner's agent session, not bypass macOS login or website MFA.
- **missing:** A secure low-power proximity channel on the pendant (BLE/UWB or equivalent); current USB attachment is not a wearable presence signal; Mac local-agent hooks for screen privacy, audio mute, browser tab concealment, and interruption of in-flight computer-use actions; Browser extension commands to freeze and restore authenticated tab state without serializing cookies or page secrets; A signed pendant presence token with rotation, replay protection, and an explicit owner-configured fail-closed policy

### ""Forget everything from that conversation everywhere, including the relay, Mac logs, browser evidence, and audio—then prove it is gone.""
- **useful because:** The owner currently cannot reliably revoke one piece of personal context across all substrates. A single privacy command would find linked audio, transcripts, evidence capsules, browser provenance, relay state, job records, and derived memory, delete or cryptographically tombstone them, and return a deletion receipt with anything that could not be erased.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic record-linking and deletion; use a cheap background model only to identify semantically linked derived notes when explicit IDs are unavailable. Realtime is only for the spoken request and confirmation of the result.
- **latency:** Acknowledge scope within 2 seconds; revoke relay and browser visibility immediately; complete local garbage collection within 30 seconds for normal records, with a later completion notification for large audio artifacts.
- **cost:** Low model cost if records carry stable provenance IDs; storage/index work dominates. Avoid re-reading page contents by deleting through evidence and lineage references.
- **security:** Deletion must be authenticated by the pendant/owner session and must not erase unrelated records with similar text. Keep only a minimal non-content tombstone: request ID, time, scope, and deletion status. The receipt must distinguish physically erased data from backups or immutable provider logs that cannot be controlled.
- **missing:** A cross-surface provenance graph linking relay turns, audio chunks, transcripts, Mac jobs, browser evidence, memory findings, and derived summaries; Authenticated deletion endpoints on relay and Mac that accept a provenance scope and return item-level results; Browser-extension erasure for cached page snapshots, command results, and local spools; A cryptographic deletion receipt and retention scanner that can verify absence without returning the deleted content


## Changes it proposed to its own stack

### `mac-harness` — Make every /execute shell and computer job a recoverable execution record: capture child exit code/signal, pid, effective cwd, a redacted environment fingerprint, stdout/stderr byte counts and hashes, and the pre-rewrite submitted action alongside the dispatched action; assign planMeta.jobId on ledger creation, close the ledger in a finally block, pass the AbortSignal to the child process, and on boot reconcile processing jobs and open ledgers. Add an automatic retry classifier that retries only transport/timeouts and never repeats an action marked irreversible without an idempotency key.
- **owner gets:** When the owner asks the pendant to do something, a crash or timeout would stop being a mystery or a stuck 'running' badge. They would hear whether the command exited, was killed, or was interrupted, resume only the unfinished safe step, and avoid duplicate calendar/file/browser mutations after a Mac restart.
- effort: Medium-high: executor and job tracker changes, ledger lifecycle tests, child-process signal wiring, boot reconciliation, and per-action idempotency metadata. No new hardware is required.  ·  risk: A bad retry classification could duplicate an irreversible action; default unknown failures to no retry and expose a clear 'needs replay' state. Reconciliation must not claim a child completed when it died; mark it interrupted and require the existing owner policy for rerun.
- cost: Negligible storage increase within existing job/ledger caps; no model cost for capture or reconciliation. A cheap background classifier is optional and should not be used for basic exit-code logic.  ·  latency: No meaningful added latency on success; boot may spend under a second reconciling bounded records. Retry backoff can add delay only after a transient failure.
- security: Do not persist raw environment values: record variable names plus a hash and explicit redaction list. Never put AGENT_TOKEN, relay keys, or LLM keys in stdout receipts. The owner retains maximum access; this improves forensic truth rather than adding gates.
- depends on: A stable job↔ledger identifier in POST /execute planMeta; Child-process execution using AbortSignal; Ledger close in orchestrator finally path; A durable interrupted-job state and resume endpoint that distinguishes safe from irreversible actions


## What it asked for

_Nothing._
