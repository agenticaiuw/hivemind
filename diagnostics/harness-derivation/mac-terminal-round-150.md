# Harness derivation — mac-terminal — round 150

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What changed on my Mac while I was away, and is anything waiting for me?”"
- **useful because:** The owner currently gets point-in-time machine context, not a trustworthy explanation of unattended change. A return-home spoken digest would combine active apps, Mac jobs, browser sessions, project state, and failures into only the items requiring attention—without opening a microphone or making them reconstruct a day from logs.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background for periodic sampling and summarization; realtime only when the pendant asks for the digest
- **latency:** Sampling is incremental (under 1 s each wake); spoken answer should begin within 2 s and finish within 10 s.
- **cost:** Low: mostly local structured facts and a small background summarization prompt; dominant cost is one compact model call per requested digest, not continuous audio.
- **security:** All raw window titles, URLs, project names, and job output remain on the Mac unless the owner explicitly asks for a spoken/cloud summary. Authenticated browser content must be reduced to titles/statuses by default, with an explicit request for page text. Never infer completion from stale jobs.
- **missing:** A Mac-side change journal that records foreground app/project/browser tab transitions and job receipts as compact events; A relay endpoint to request a since-cursor digest and persist the cursor across pendant reconnects; A browser adapter that exposes tab identity and coarse status-change events without exporting page bodies; A user-visible retention/forget control for the local timeline

### "“Run the long task now, keep working if I close the lid, and tell me only when it reaches a real milestone or needs me.”"
- **useful because:** Today a Mac action is a one-shot sequential job with weak cancellation and no retry/reconciliation. This would make the pendant a dependable remote operator: dispatch from a button/voice turn, let the relay retain intent, resume after a Mac-agent restart, and receive truthful milestone/failure notices rather than a dead silent job.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** background model for milestone extraction and retry decisions; realtime only for the initial spoken confirmation and exception conversation
- **latency:** Dispatch acknowledgement under 1 s locally; milestone notices within 5 s of a completed step; no need to keep a realtime model alive during execution.
- **cost:** Low-to-moderate: local execution dominates; one cheap summarization call per milestone or failure. Durable relay polling is the main operational cost.
- **security:** The owner explicitly wants maximum Mac access and no gates, so this is not an approval design. Preserve exact command, cwd, timeout, exit code, stdout/stderr, and transformed action in an append-only receipt; send only milestone summaries to the relay. Never retry non-idempotent actions automatically; label them and stop. Pendant must show queued/running/stale/failed without inventing completion.
- **missing:** A durable relay-backed work queue with leases and idempotency keys; Exec-based cancellation using AbortSignal plus captured exit code/pid; Boot reconciliation that marks processing jobs interrupted and offers ledger resume rather than leaving them running forever; A step classifier that can distinguish safe-to-retry from side-effecting shell actions; A pendant notification path for milestone payloads over the existing USB/LTE transport

### "“Tell me why the project stopped being green, and open the exact files and issue pages I need to fix it.”"
- **useful because:** A developer can ask this while walking away from the keyboard. The Mac can run the repository's tests and inspect git; the browser can read the authenticated CI/issue session; the relay correlates timestamps and preserves the investigation; the pendant returns a short diagnosis and the Mac opens the evidence. No single surface has both local failure details and authenticated team context.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background model for correlation and concise diagnosis; realtime only for follow-up questions after the evidence bundle is ready
- **latency:** Start collecting evidence immediately; first spoken result in 8–15 s, with a dashboard evidence bundle streaming as each source finishes.
- **cost:** Moderate: local test/git commands are cheap; one compact reasoning call over failure excerpts and browser status. Keep full logs local and send bounded excerpts/hashes.
- **security:** Repository contents, CI pages, and issue text may be sensitive. Default to local correlation and redact secrets/paths before relay upload. Opening files/pages is reversible; changing code, commenting, or rerunning deployment must remain an explicit separate request. Treat browser session state as read-only.
- **missing:** A typed Mac diagnostic recipe that runs bounded test/git/status probes and returns structured failures, not just flattened shell text; A browser read adapter for authenticated CI checks and issue pages keyed by commit/branch; A correlation service that joins local commit/test timestamps to browser CI runs with confidence and cites every claim; A single evidence bundle route usable by both dashboard and spoken relay reply

### "“Read me the important parts of this private page, but never say sensitive details aloud if my headphones are not actually connected.”"
- **useful because:** Today the system can access authenticated browser pages and can send audio, but it cannot prove that a sensitive response is taking a private route. This capability would let the owner use the pendant in public without accidentally speaking passwords, medical data, one-time codes, or private work text through the wrong output device. It combines browser-held sessions, Mac audio state, the ESP32 bridge, relay policy, and the pendant's truthful link state; no single node can establish all of that.
- **path:** browser-extension → mac-planner → mac-vision → relay → pendant → dashboard
- **model tier:** Realtime for the short request and route decision; background model for extracting a sensitivity-labeled summary from the page. Do not send raw page content to the realtime model unless the owner explicitly requests verbatim reading.
- **latency:** Route decision and a safe acknowledgement under 1 s; summary within 5–10 s. If privacy state is unknown, immediately say that it cannot safely read the details and offer a redacted visual result.
- **cost:** Low-to-moderate: one extraction call per request; audio/device checks and redaction are local. The dominant cost is summarizing page text, not transport.
- **security:** Default-deny for sensitive spoken output when headphone connection, Bluetooth route, or device identity is unknown or stale. Classify page spans (credentials, codes, financial/health identifiers) and redact before synthesis. Keep raw page text local to the browser/Mac; relay receives only the minimum labeled summary. Require an explicit owner override for verbatim sensitive reading and record the chosen route.
- **missing:** A cryptographically bound audio-route attestation from the ESP32/Mac bridge, including headphone identity and freshness; Browser extraction that returns sensitivity spans and citations without exporting the whole page by default; A relay policy decision that joins content sensitivity, transport state, and owner preferences; A pendant acknowledgement pattern for private-safe, redacted, and blocked output states


## Changes it proposed to its own stack

### `mac-harness` — Upgrade run_shell execution from exec(string) to an internally structured command record while preserving FULL_CONTROL_MODE: capture original and rewritten action, resolved cwd, sanitized environment fingerprint (never secret values), pid, started/finished timestamps, numeric exit code/signal, timeout reason, bounded stdout/stderr tails, and a stable action/job join. Write the receipt before and after dispatch so a crash leaves an honest in-flight record.
- **owner gets:** When the owner asks “did it run, what failed, and can I continue?”, the answer will be factual instead of a flattened “Failed: …”. It also makes the pendant's running/stale/error beacon truthful and makes expensive reruns avoidable.
- effort: Medium: computerControl/executor receipt schema, job/ledger join, output retention policy, and migration tests for command rewrites and timeout paths.  ·  risk: Receipt code must never alter shell semantics. A crash between pre/post writes could show unknown rather than false success; recover by marking unknown and exposing the raw job record. Secret redaction errors are possible, so store environment names plus a keyed fingerprint, not values.
- cost: Negligible disk and CPU; bounded output storage may add tens of KB per job, within the existing ring stores.  ·  latency: Under 10 ms per shell step for bookkeeping; no meaningful command latency change.
- security: Improves auditability without adding gates or shrinking access. Explicitly prevents AGENT_TOKEN/LLM keys from entering receipts while retaining enough provenance to debug.
- depends on: Keep FULL_CONTROL_MODE and unrestricted command capability per owner policy; Fix the orchestrator to close its action ledger and populate planMeta.jobId; Define a bounded receipt retention/eviction rule

### `integration` — Add a USB-local pendant session to the Mac bridge: identify the nRF9160 and ESP32 serial devices by handshake (not volatile tty suffix), multiplex button/audio/status frames, and expose a local authenticated transport to the relay. When the pendant is worn but LTE is absent, route turns and action receipts over USB immediately; queue only when both USB and LTE are unavailable, and surface transport choice in every receipt.
- **owner gets:** The hardware is on the owner's desk today but currently behaves as if it does not exist because it is not relay-registered. This makes the actual pendant useful now: press it, get a response, dispatch a Mac action, and know whether the result travelled over USB or LTE.
- effort: Medium-high: serial framing/handshake, ESP32 audio bridge coordination, local-agent registration/heartbeat, reconnect state machine, and end-to-end tests with both real /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA devices.  ·  risk: USB unplug/replug and partial bridge failure can leave stale sessions. Use sequence numbers, bounded buffers, explicit link ownership, and the already accepted audio_link_truth_and_recovery plus truthful_action_status_beacon; never claim cloud delivery from a local write alone. Recover by dropping to queued-offline mode.
- cost: No new hardware; modest Mac CPU and serial bandwidth. LTE/data cost decreases when USB is available.  ·  latency: Button-to-Mac dispatch should be tens of milliseconds over USB rather than LTE round-trip; reconnect may take 0.5–2 s.
- security: Keep transport loopback-only and bind the device to the local agent by a challenge-response handshake; do not expose serial frames on LAN. USB access grants the same owner-authorized Mac capability, so log device identity and session IDs.
- depends on: A serial protocol implementation for both boards; Relay registration/session route that accepts a local transport claim; Mac bridge access to the live serial ports; Use existing pendant_store OUTBOX for crash-safe offline queueing

### `hardware` — Add a small, dedicated local notification/audio mixer in the Mac↔ESP32 bridge path: preserve the existing 44.1 kHz SBC A2DP source, but reserve a bounded low-latency notification lane that ducks music, plays a short action/status tone or speech cue, then restores the prior stream. Keep the queue in Mac memory and send only tiny PCM/SBC bursts so the ESP32 never allocates the known-dangerous 44 kB buffer.
- **owner gets:** Action results will reach the owner's ears even when they are not looking at the pendant LED or dashboard: “build failed”, “reply ready”, or “Mac disconnected” can interrupt music briefly and restore it cleanly. This turns remote work into a usable hands-free experience without opening the microphone.
- effort: Medium: Mac audio-session duck/restore, ESP32 bounded notification state machine, and tests for Bluetooth starvation, reconnect, and simultaneous spoken reply.  ·  risk: A2DP reconnect or a malformed burst could silence audio. Keep the existing stream as the source of truth, watchdog notification playback, and restore the prior stream after a bounded deadline; if unsafe, fall back to the single LED beacon and no audio injection.
- cost: No new component required for the prototype; low CPU/RAM overhead. A production board could add a small codec/mixer (~$3–8) if Mac-side mixing proves unreliable.  ·  latency: Status cue begins under 300 ms when headphones are connected; normal music resumes within 1–2 s.
- security: No microphone and no new network exposure. Spoken content should be classified as potentially sensitive; default to short status labels, not command output or browser page text.
- depends on: USB-local pendant session and transport identity; A Mac audio control path that can duck/restore the current output; truthful_action_status_beacon for the no-audio fallback; Respect ESP32 320 kB DRAM and avoid allocations near the documented 44 kB starvation threshold


## What it asked for

_Nothing._
## Its own summary

Round 150 produced three owner-facing capabilities: a return-home “what changed while I was away?” digest across Mac/browser/relay/pendant; durable long-task execution with truthful milestones, restart recovery, and no unsafe automatic retries; and a cross-node project regression investigator correlating local tests/git with authenticated CI/issues and opening cited evidence. I also proposed three concrete changes: structured shell provenance/exit receipts without gates, a USB-local pendant session using the two live serial devices, and a bounded ESP32/Mac notification-audio lane that ducks music and falls back to the existing LED truth beacon. The most immediate path is USB-local use: the hardware is physically present but still not relay-registered.

**Biggest unknown:** Whether the orchestrator's pending mac_usb_serial_diagnostics request will ever be granted; without it I cannot verify the live serial handshake, framing, or whether the ESP32 and nRF9160 ports are currently open. I still need the actual serial protocol/registration contract and a relay endpoint for a USB-local session.

