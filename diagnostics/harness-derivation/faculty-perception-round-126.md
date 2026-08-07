# Harness derivation — faculty-perception — round 126

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **current Mac input reachability** — At 2026-08-07T18:21:09Z the local agent is online and browser extension is online, but Accessibility is untrusted, Screen Recording is false, inputReachability is failed, and synthesized UI events cannot be trusted. AppleScript automation grants are present.
  - evidence: GET /ops/status and GET /observe returned accessibility.trusted=false, screenRecording=false, inputReachability.status=failed, uiActionsWillReachTheScreen=false, and automation grants.
- **current browser state** — Safari browser bridge is online with 3 sessions and 3 tabs; the heartbeat device reports a foreground tab titled 'Failed to open page' at example.com while durable sessions include Gmail inbox and two probe forms. No browser commands are pending.
  - evidence: GET /browser/status returned online=true, pendingCommands=0; GET /observe returned sessions=3 and the three durable tabs.
- **current pendant reality** — No live pendant registration is established by the relay/device discovery in this round. The pipeline contains historical nRF9160-origin events and a response accepted by the relay, but that is not proof of a currently connected pendant. The Mac bridge is online.
  - evidence: discover(devices) returned Safari and home-macbook-bridge online plus cloudflare-contract-test offline, with no pendant; GET /pipeline showed historical nrf9160 event and relay acceptance; GET /ops/status showed macBridgeOnline=true.

## Capabilities it proposed

### ""What is actually happening right now?" Give me one short, spoken situational snapshot: what app is in front, what my browser has open, whether the relay/Mac bridge/pendant are reachable, and whether anything I asked for is running or waiting. Mark each fact fresh, stale, or unknown, and call out contradictions instead of guessing."
- **useful because:** Today the system can report isolated status pages but cannot establish a trustworthy present-tense reality. This is the single most useful perception capability: it prevents the owner from believing a job completed when it is only queued, or believing the pendant is live when telemetry is historical.
- **path:** relay-realtime → mac-planner → browser-extension → faculty-perception → unified
- **model tier:** background for collection and reconciliation; realtime only to speak the final one-sentence snapshot
- **latency:** Under 3 seconds when the Mac bridge is online; under 8 seconds if browser heartbeat and relay status must be refreshed
- **cost:** <$0.01 typical; dominated by one small reconciliation call, not vision or audio generation
- **security:** Reads foreground app, browser tab metadata, job state, and connectivity only; never page contents by default. Private tab URLs/titles must be redacted unless the owner asks. Do not claim pendant presence from recorded pipeline history.
- **missing:** A typed perception snapshot endpoint that joins /observe, /ops/status, /browser/status, /pipeline, and relay device state with per-field timestamps; A reliable live pendant registry/delivery acknowledgement source

### ""Did that really work?" For my last request, independently verify the result across the machine, browser, relay, and audio delivery, then tell me exactly what is proven, what merely claimed success, and what still needs me."
- **useful because:** Existing receipts and pipeline events can say an action was accepted, while the real-world effect may be absent (for example a shell approval block or an audio response waiting for a nonexistent pendant). Cross-surface verification would make completion trustworthy rather than optimistic.
- **path:** faculty-perception → mac-planner → mac-vision → browser-extension → relay-realtime → faculty-action
- **model tier:** background reconciliation model; realtime only for the concise spoken result
- **latency:** 5 seconds for reversible local actions; up to 20 seconds for browser or audio delivery verification
- **cost:** $0.01–$0.04 per verification; cost scales with evidence extraction, not the final response
- **security:** Read-only verification by default. Browser evidence can contain sensitive account data; retain hashes/snippets and redact secrets. Never turn an unverified receipt into a success claim. Any retry or repair requires separate confirmation.
- **missing:** A typed assertion/evidence schema linking requested intent to observable postconditions; A delivery acknowledgement from the actual pendant/audio endpoint, distinct from relay acceptance

### ""Why did that fail?" Build me a causal timeline for the request: speech received, plan made, actions attempted, approvals or permissions that blocked it, browser/relay handoffs, and final delivery. Separate the first failure from later symptoms and suggest the one next observation that would disambiguate it."
- **useful because:** The current logs are rich but fragmented. A perception layer that distinguishes root cause from downstream symptoms would turn recurring failures—such as UI actions reporting success while Accessibility is false, or relay audio being accepted without a live pendant—into actionable answers.
- **path:** faculty-perception → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-judgement
- **model tier:** cheap background model over structured events; escalate to realtime only when the owner asks during a live conversation
- **latency:** Under 5 seconds for a completed job; stream the first timeline markers immediately for an active job
- **cost:** <$0.02 per completed diagnosis; event normalization dominates, model context stays compact
- **security:** Logs may include commands, URLs, and account identifiers; redact command arguments and query strings by default, retain provenance and timestamps. Do not infer causes where telemetry is missing—label unknown.
- **missing:** A common event identity/correlation contract across relay jobs, local jobs, browser commands, permissions, and pipeline IDs; A read-only causal-analysis route that can query historical events without replaying actions

### ""Only do sensitive things when I am physically wearing the pendant." Use the pendant as a cryptographic presence-and-consent key: for sending messages, purchases, account changes, or exposing secrets, require a fresh hardware challenge and an intentional button hold, then show me exactly which action that proof authorizes."
- **useful because:** A Mac session or browser login can be hijacked or left unattended. Today the system has software approvals but no proof that the owner is physically present. This would make the wearable a real safety boundary across the relay, Mac, browser, and action layer.
- **path:** relay-realtime → faculty-perception → faculty-judgement → faculty-action → mac-planner → browser-extension
- **model tier:** Realtime only to explain the pending authorization; use a cheap background model to summarize the action and evidence.
- **latency:** Under 1 second for presence verification and under 3 seconds for the spoken confirmation.
- **cost:** Negligible per use; hardware pairing and secure-key provisioning dominate implementation cost.
- **security:** Private keys must never leave the pendant. Prevent replay, relay substitution, and stale approvals; bind each challenge to an exact action hash, account, and expiry. Loss of the pendant requires revocation and recovery credentials. Never treat USB attachment or relay registration alone as consent.
- **missing:** Secure-element-backed key storage or equivalent hardened nRF9160 key provisioning; A relay challenge-response protocol bound to action hashes; Mac and browser enforcement that refuses sensitive actions without a valid pendant assertion; A clear owner-facing recovery and revocation flow

### ""When I walk away from my Mac, protect me automatically, and restore my exact working context when I return." Detect pendant proximity loss and return using a secure local link; pause spoken output, hide or lock sensitive browser sessions, suspend queued actions, then restore only the tabs, job, and approval state that were active at departure."
- **useful because:** The owner carries a physical device that can know they are no longer near the computer. This would prevent an unattended Mac or browser session from continuing an AI action, while making interruptions feel continuous instead of forcing the owner to reconstruct context.
- **path:** faculty-perception → mac-planner → browser-extension → relay-realtime → faculty-judgement → faculty-action
- **model tier:** Local deterministic state machine for proximity and locking; background model only to summarize the restored context.
- **latency:** Lock or pause within 2 seconds of confirmed proximity loss; restore a concise context within 5 seconds of return.
- **cost:** Low API cost; requires a reliable BLE/UWB presence channel and browser/session checkpoint storage.
- **security:** Do not rely on RSSI alone or allow a nearby stranger's device to satisfy presence. Encrypt checkpoints; clear sensitive previews after timeout. A false departure must not delete or submit anything. Require fresh consent for irreversible actions after restoration.
- **missing:** BLE or UWB presence hardware/firmware and authenticated pairing; Mac agent hooks for secure lock/pause and browser session redaction; A durable departure checkpoint containing tab IDs, job IDs, approvals, and expiry

### ""Tell me what I was doing when I left, without making me explain it again." At a physical transition—pendant disconnected, Mac closed, or pendant returned—create a private, evidence-backed checkpoint of the owner's active task: the relevant app and browser tab, unsent drafts, pending jobs, last spoken exchange, and unresolved approvals. On return, speak only the smallest useful resume prompt."
- **useful because:** The current system stores many logs and sessions but does not turn a real interruption into a coherent handoff. The pendant, Mac, browser, and relay together can know both the owner's physical transition and digital work state; no single node can produce this safely.
- **path:** faculty-perception → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Cheap background summarization over structured checkpoint data; realtime only for the short resume prompt.
- **latency:** Checkpoint within 5 seconds of a transition; resume prompt available within 3 seconds of reconnection.
- **cost:** <$0.01 per transition; storage and redaction dominate rather than inference.
- **security:** Exclude passwords, secret fields, private message bodies, and raw audio by default; retain source references and short hashes. Checkpoints need per-item TTL and deletion. A resume prompt must never imply an action was completed unless independently observed.
- **missing:** Authenticated transition events from pendant presence, USB, relay, and Mac sleep/lock; A privacy-aware checkpoint schema with source, confidence, and expiry; Cross-surface retrieval that can resolve a browser tab and local job without replaying actions


## Changes it proposed to its own stack

### `mac-harness` — Add a read-only USB reality probe that enumerates the two known serial identities (/dev/cu.usbmodem00096003658* for nRF9160 and /dev/cu.usbserial-0287A9CA for ESP32), opens each at the firmware baud, sends only the documented diagnostic/status query, and records port path, chip response, firmware build, uptime, LTE registration, and last audio counters. Publish a signed snapshot with observedAt and transport=usb_serial; never infer relay registration from USB presence. Surface contradictions when USB says present but /devices says absent, or when pipeline history is mistaken for live telemetry.
- **owner gets:** The owner can wear or plug in the actual hardware and immediately know whether the pendant and audio bridge are alive, rather than receiving the currently misleading answer that relay history proves a live device. This is testable now over the Mac's USB connections.
- effort: Medium: implement a narrowly allowlisted serial reader, firmware diagnostic frame/query, parser, and /device-observation route; add fixture tests for absent, bootloader, stale, and healthy responses.  ·  risk: A malformed query could interfere with the modem or audio bridge; use a strict read-only command and rate limit. Serial paths can change, so identify by USB VID/PID and reject unknown devices. If a port is busy, report unavailable rather than stealing it. Recovery is unplug/replug and process restart.
- cost: No model cost; roughly 1–2 weeks engineering. Existing hardware, negligible power impact.  ·  latency: 1–3 seconds for both ports over USB; no impact on voice path unless explicitly requested.
- security: Serial telemetry can expose firmware identifiers and network state; keep it local by default and send only summarized health to relay with owner consent.
- depends on: A documented read-only diagnostic frame in both nRF9160 and ESP32 firmware; A typed device-observation schema that distinguishes physical USB presence, relay registration, and historical telemetry; Mac agent serial-port permission/allowlist for the two exact USB identities


## What it asked for

_Nothing._
