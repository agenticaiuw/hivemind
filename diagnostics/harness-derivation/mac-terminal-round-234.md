# Harness derivation — mac-terminal — round 234

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/relay readiness** — Mac local agent is healthy with full control and browser extension online; Safari has two tabs and is currently on YouTube. Relay is reachable, paired/configured, and reports macBridgeOnline=true. The latest iOS status job says the Mac screen is locked, so phone reads/drives are unavailable despite the mirroring app running.
  - evidence: GET /ops/status returned agent.ready=true, fullControlMode=true, browser online, relay reachable and macBridgeOnline=true; GET /jobs returned completed ios_status with state mac-locked.

## Capabilities it proposed

### "When I say “diagnose the pendant,” capture a bounded dual-chip UART session, correlate it with the relay/audio pipeline and Mac-agent logs, then tell me the single most likely fault and leave a timestamped bug report in my workspace."
- **useful because:** The owner currently has to collect nRF9160 and ESP32 logs by hand and separately inspect relay state. This turns a bench failure into an actionable diagnosis, using the wearable as the trigger and the Mac as the instrument.
- **path:** pendant → relay → mac-planner → mac-terminal → dashboard-ux
- **model tier:** background for log correlation and report writing; deterministic shell capture and health reads first, with planner escalation only when signatures conflict
- **latency:** Begin capture and speak “diagnosing” within 1 s; 10–30 s for a 5 s bounded capture and report, never leave an unbounded serial process running.
- **cost:** Usually one deterministic Mac job plus a small background summarization call (~2k–5k tokens); shell capture and health probes dominate latency, not model cost.
- **security:** UART logs can contain identifiers and audio transport metadata; keep raw logs local, send only redacted signatures to relay/model, and require explicit confirmation before uploading raw logs or opening an external issue.
- **missing:** A host-side bounded dual-UART capture/parser with stable framing and timestamps; A correlation adapter that joins capture timestamps to relay pipeline telemetry and Mac job IDs; A local bug-report writer that stores raw evidence separately from the redacted summary

### "Tell me “what is happening right now?” and give one short spoken answer covering the pendant link, any Mac job currently running, whether Safari is online, and whether the Mac is locked or ready to act."
- **useful because:** The system spans several surfaces and currently exposes contradictory partial truths: the Mac can be locked while the browser is online, and a job can remain marked processing after a restart. One truthful spoken status prevents the owner from guessing whether an action is pending, impossible, or complete.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard-ux
- **model tier:** deterministic aggregation with a cheap background formatter; no realtime model unless the owner asks a follow-up
- **latency:** Under 700 ms for the facts and under 2 s for speech; stale signals must be labeled with age rather than hidden.
- **cost:** Near-zero model cost for the normal path; one aggregation request and cached speech. The expensive work is none if endpoint payloads are already available.
- **security:** Do not speak URLs, tab titles, or sensitive job output by default. Return only state, age, and a safe label; require a separate request to reveal details.
- **missing:** A single cross-surface status contract with freshness timestamps and explicit unknown/locked states; A relay endpoint that merges pendant transport state with Mac-agent and browser presence; A deterministic voice intent and formatter for this exact query

### "Let me say “privacy mode” on the pendant, and have the whole hive immediately stop sending voice, page content, and Mac evidence to cloud services until I say “privacy mode off.” Keep the pendant usable locally and show me a truthful local indicator of the mode."
- **useful because:** The owner can currently trust individual surfaces but cannot establish one privacy boundary across the wearable, relay, browser session, and Mac. A single spoken switch would make sensitive moments understandable and controllable without unplugging hardware.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard-ux
- **model tier:** deterministic policy transition; no model call for enabling/disabling or enforcement, with optional local Mac speech fallback
- **latency:** Enforce within 250 ms of the command being recognized; the pendant must acknowledge locally even if the relay is unreachable.
- **cost:** Negligible per-use model cost after recognition; implementation cost is policy propagation and local fallback behavior.
- **security:** The mode transition itself must not depend solely on cloud confirmation. Persist a signed local policy epoch, suppress browser/page payloads and cloud audio, and make the default after reboot conservative. The owner should explicitly opt back into cloud transmission.
- **missing:** A device-to-relay privacy-policy command with monotonic epoch and local acknowledgement; Mac and browser middleware that refuses cloud/page/evidence uploads while the epoch is active; A local recognition/fallback path for turning privacy mode off without transmitting the protected utterance

### "When I say “do this when I’m back,” queue the action with its exact preconditions, then execute it only when the Mac is unlocked, the required browser session is present, and the request has not expired; tell me what happened on the pendant afterward."
- **useful because:** The owner often has the pendant away from the desk while authenticated browser sessions and Mac permissions exist only at home. Today a request is either attempted immediately or becomes an opaque pending job; this would turn physical presence and session readiness into explicit, trustworthy triggers.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard-ux
- **model tier:** deterministic queue and precondition evaluator; use a cheaper background model only to clarify an ambiguous action before it is queued
- **latency:** Queue acknowledgement under 1 s; readiness checks every 5–10 s; execute within 2 s of all preconditions becoming true.
- **cost:** Near-zero recurring model cost for explicit requests; storage and polling are the dominant costs.
- **security:** Bind the queued request to the originating device, browser host/session, and expiry. Never treat “Mac online” as “Mac unlocked.” Destructive actions remain separately confirmed at execution time, not merely at queue time.
- **missing:** A durable preconditioned-job schema with expiry and device/session binding; Mac lock-state and browser-session events exposed to the relay rather than inferred from stale heartbeats; A pendant receipt that distinguishes queued, waiting-for-unlock, waiting-for-browser, expired, and executed


## Changes it proposed to its own stack

### `relay` — Make every Mac execution an end-to-end trace: assign one execution context ID before dispatch, persist the job↔ledger↔receipt join, capture exit code, start/finish/duration, bounded stdout/stderr hashes, timeout/cancellation state, and a boot-time reconciliation state. Stream only redacted progress events to the pendant and retain full evidence locally. Add automatic retry only for idempotent read actions; never retry arbitrary shell mutations.
- **owner gets:** When a command fails or the Mac restarts, the owner should hear exactly whether it ran, timed out, was killed, or never started—and be able to resume safe reads without repeating side effects. Today cancellation cannot stop a running shell, completed ledgers remain open, and jobs cannot be joined to their receipts.
- effort: Medium-high: modify executor and job tracker, use process groups/signals, close ledgers in orchestrator, reconcile processing jobs at boot, and add a small redaction/trace layer.  ·  risk: A mistaken retry could duplicate a mutation; classify retries conservatively and default unknown shell actions to no retry. A crash during reconciliation may mark an actually running child stale, so verify process-group ownership before finalizing.
- cost: Negligible storage overhead if output is capped and hashed; modest implementation cost. No additional model calls on the normal path.  ·  latency: Adds under 20 ms for receipt/trace persistence; retries improve perceived reliability but can add bounded delay for safe reads.
- security: Improves auditability while avoiding secret leakage: never persist inherited environment values or raw sensitive output in relay events; keep full evidence local.
- depends on: A host process-group execution wrapper that exposes exit status and signal reason; A stable execution-context ID passed in planMeta before /execute; A fixed ledger close path and boot reconciliation routine

### `hardware` — Add a small secure element to the next pendant revision and use it as the non-exportable root for device identity, local privacy-policy signing, outbox encryption, and command receipts. Pair it with relay-side key rotation and a recovery ceremony using the owner's Mac, without changing the one-button interaction or requiring a display.
- **owner gets:** A stolen or cloned pendant should not be able to replay queued actions, impersonate the owner's wearable, or expose offline voice/outbox data. The owner gets a device that remains trustworthy across USB, LTE-M, relay, and Mac handoffs rather than merely connected.
- effort: High: hardware respin and secure-element driver, manufacturing/provisioning flow, relay key lifecycle, firmware migration, and recovery UX.  ·  risk: Lost or failed hardware could strand encrypted offline records; support an owner-authorized recovery key and bounded key rotation. A provisioning bug could brick devices, so retain a factory diagnostic mode that cannot execute owner actions.
- cost: Roughly a few US dollars per unit in hardware at low volume, plus negligible power in the sleep budget; modest per-device relay storage and cryptographic CPU cost.  ·  latency: Tens of milliseconds for signing/decryption on command boundaries, not on the audio sample path.
- security: Strongly improves authenticity and confidentiality, but introduces key-management responsibility and a recovery secret that must never be placed in ordinary model context.
- depends on: A stable pendant identity and pairing protocol; Relay support for key rotation and receipt verification; A Mac-based recovery/provisioning utility


## What it asked for

_Nothing._
