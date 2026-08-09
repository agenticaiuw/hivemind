# Harness derivation — faculty-action — round 201

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **audio delivery truth gap** — Live pipeline history contains a 24 kHz 420.7 KiB PCM response that rendered on Mac but pipeline failed reporting bridge result with HTTP 413; delivery explicitly proves only Mac composition, not relay departure or playback, because no device_playback event/job id exists.
  - evidence: GET /pipeline response for pipelineId job_e60ca5d3-ee2e-4e2e-9fe4-87266d8f20b2: error Payload Too Large; delivery state composed_on_mac, awaitsDevice true, heard unknown, heardBecause says firmware never calls playback reporters and live duplex holds no job id.

## Capabilities it proposed

### ""Do this across my Mac and browser, and don't tell me it's done until every step is independently verified; if a later step fails, recover or tell me exactly what remains.""
- **useful because:** This is the system's defining promise: judgement can choose a workflow, but today execution receipts alone cannot establish that the world changed. A single transactional runner would combine Mac/browser hands, the pendant's physical approval boundary, and faculty-perception's verifier into one truthful outcome instead of a plausible success message.
- **path:** unified → faculty-judgement → faculty-action → faculty-perception → mac-planner → mac-vision → browser-extension → relay-realtime
- **model tier:** Use a cheap background model to normalize the workflow and summarize receipts; use realtime only for owner-facing interruption/approval; use faculty-perception's deterministic verifier for postconditions, never an LLM assertion.
- **latency:** Stage within 1 s, owner approval is interactive, each action 1–10 s, verification under 2 s per step; on timeout return unknown rather than claiming success.
- **cost:** Low-to-moderate: mostly existing Mac/browser calls and verifier reads; model cost is a short plan plus final summary, dominated by screenshots or page evidence only when needed.
- **security:** Never put secrets or page contents on the pendant. Require the existing physical transaction approval latch for risky steps, bind approval to an operation hash and expiry, verify after every mutation, and stop on digest mismatch or unknown state. Compensation must be explicitly reversible and separately verified.
- **missing:** A durable operation executor that correlates action receipts, step IDs, verifier evidence, and compensation attempts; A commit protocol that treats verified postconditions as the only success state and exposes partial/unknown states; A narrow addition to verify_operation_step for actionId/attemptId correlation

### ""The workflow partly happened and then failed—make it safe: undo what can be undone, leave what cannot alone, and give me a precise recovery checklist.""
- **useful because:** Multi-step actions currently strand the owner between executor receipts and truth. A recovery operator would inspect the operation ledger, classify each step as verified/reversible/unknown, run only safe compensations, and hand the unresolved remainder back to judgement instead of retrying blindly or duplicating side effects.
- **path:** faculty-action → faculty-perception → faculty-judgement → mac-planner → browser-extension → relay-realtime
- **model tier:** Background model for deterministic recovery planning and concise explanation; no realtime model unless the owner is present for a confirmation. Perception performs read-only checks; action performs only approved compensations.
- **latency:** Detect partial failure immediately after a failed receipt; produce a recovery plan in under 3 s, execute approved compensations sequentially, and stop on the first unknown postcondition.
- **cost:** Low: existing receipt and read-only verification routes dominate; extra model tokens only for the recovery summary. Potentially saves expensive duplicate actions and human cleanup.
- **security:** Never auto-retry non-idempotent steps. Require explicit owner approval for compensation that could delete, send, or overwrite. Preserve the original operation hash, evidence provenance, and cancellation reason. Unknown means paused, not success or failure.
- **missing:** A compensation graph in each plan declaring idempotency, inverse action, and acceptable residual state; An operation-recovery endpoint that atomically leases one recovery attempt and records its result; A user-visible partial-state object shared by relay and pendant outcome beacon

### ""If I touch the pendant while I'm moving or it is hanging against me, don't trigger an action; give me a private, reliable way to mark or cancel something without looking at a screen.""
- **useful because:** The owned IMU and haptic motor can make the physical approval boundary usable in daily wear: distinguish a deliberate stationary approval from a swing/impact, and render cancel/unknown privately. This is not another approval latch; it makes the latch safe and dependable in the actual jewellery form factor.
- **path:** pendant → faculty-action → faculty-perception → relay-realtime → unified
- **model tier:** No expensive model on-device. Firmware classifies motion locally; relay uses a cheap rules model only to select a haptic pattern and action policy. Realtime speaks only when the owner requests it.
- **latency:** Motion gate under 50 ms, haptic acknowledgement under 150 ms, no network dependency for rejecting an unsafe gesture; queued outcome delivery when link returns.
- **cost:** Very low API cost; firmware work only. Hardware already owned (LSM6DSOX, DRV2605L, motor); power cost is short IMU windows plus brief haptic pulses.
- **security:** Motion must only veto or defer approval, never create approval. Keep secrets and action payloads off-device; sign the gesture response and bind it to the pending nonce. Fail closed on sensor fault, stale nonce, or link ambiguity. Avoid continuous raw motion upload.
- **missing:** Firmware integration of i2c2, LSM6DSOX and DRV2605L (currently disabled/not in CMake); A calibrated stationary/impact classifier and privacy-preserving motion summary; A protocol field on the physical approval latch for motion-quality and sensor-fault state

### ""Did I actually hear the last answer? If not, send it again—but only after you know whether the pendant received and played it.""
- **useful because:** Live evidence shows the current pipeline can render 420.7 KiB/24 kHz PCM on the Mac yet fail reporting to the relay with HTTP 413, and its delivery state explicitly says audio leaving the Mac and playback are unknown because the firmware has no job ID to report. The owner currently cannot distinguish 'prepared', 'delivered', and 'heard'. This closes that truth gap across Mac, relay, and pendant.
- **path:** faculty-action → faculty-perception → relay-realtime → mac-planner → pendant → ESP32 audio bridge → unified
- **model tier:** Cheap background state machine for delivery reconciliation; realtime only when the owner asks or a retry needs a conversational response. No model should infer hearing from upload completion.
- **latency:** Receipt of each stage within 250 ms when connected; answer a status query within 1 s; retry only after a bounded timeout and explicit deduplication.
- **cost:** Low API cost. Dominant cost is telemetry bytes and one verification/read pass; send compact hashes, byte ranges, and event IDs rather than PCM or transcripts.
- **security:** Use opaque artifact/job IDs and checksums, signed device playback events, monotonic counters, and deduplication. Never claim heard from Mac rendering or relay upload. Do not transmit microphone data as proof. A replay requires owner intent and must not duplicate an external action.
- **missing:** Fix the observed 413 result-report path by reporting metadata separately from large PCM, or use the durable audio upload route; Bind the generated audio artifact to a pendant job ID before delivery begins; Implement device_playback start/finish/interruption events from nRF9160/ESP32 and independently verify them; A status/replay operation that distinguishes composed_on_mac, uploaded, received, started, finished, interrupted, and unknown

### ""Prepare this action now, but only commit it if the important details are still exactly what I approved when you are ready to send it.""
- **useful because:** Today approval and execution can be separated by a stale browser page, changed amount, different recipient, or a delayed job. The owner needs an action escrow that re-reads critical fields immediately before the irreversible step and refuses to commit if any invariant changed. This is a new safety primitive, not merely another approval prompt: it protects against time-of-check/time-of-use races across the Mac, browser session, relay, and pendant.
- **path:** faculty-judgement → faculty-action → faculty-perception → browser-extension → mac-planner → relay-realtime → pendant → unified
- **model tier:** Cheap deterministic comparison for invariant hashes and expiry; use the realtime model only to explain a refusal or request a fresh approval. Never use an LLM to decide whether two sensitive values match.
- **latency:** Prepare immediately; just-in-time recheck within 500 ms of commit; if the page or app cannot be freshly read, remain escrowed rather than guessing.
- **cost:** Low: one additional read/verification per committed action and compact hashes; model tokens only on mismatch explanation.
- **security:** The pendant receives only a redacted human summary and opaque escrow nonce, never secrets or page contents. Hash canonicalized recipient/amount/target fields with domain separation, bind them to expiry and session identity, reject stale DOM/app state, and require the existing physical approval latch after a mismatch or any material change.
- **missing:** A first-class escrow record containing canonical invariants, sensitivity labels, expiry, session binding, and commit nonce; Fresh pre-commit reads for browser fields and Mac app state with provenance, not cached planner observations; A commit endpoint that atomically compares invariants and consumes the nonce, returning changed/unknown without executing; Owner-configurable policy for which changed fields are fatal versus reviewable


## Changes it proposed to its own stack

### `integration` — Add a durable operation coordinator between plan/execute and verification: every step receives operation_id, step_id, attempt_id, idempotency key, declared inverse, and expected postcondition; the coordinator waits for executor receipt, invokes read-only verification, commits only on verified evidence, and emits partial/unknown states plus a compensation lease. Extend verify_operation_step to accept the attempt correlation and return it in provenance.
- **owner gets:** They stop hearing 'done' when a click merely returned, and after a network or app failure they get one safe recovery path rather than duplicate sends or a mystery half-completed task.
- effort: Medium-high: schema and persistence changes across planner, executor, verifier, job journal, and relay; integration tests for crash/retry races.  ·  risk: A coordinator bug could delay otherwise successful work or run an inverse twice. Use idempotency keys, one active lease, crash recovery, and fail-closed unknown status; retain existing direct routes as a compatibility path.
- cost: Small storage and read-call increase; one verifier read per mutating step. No new model requirement.  ·  latency: Adds typically 100–500 ms for verification per step; avoids expensive and dangerous blind retries.
- security: Improves security by binding approval and evidence to one operation attempt; no secrets sent to pendant. Requires authenticated provenance and replay protection.
- depends on: Owner policy for which action classes may auto-compensate versus require approval; A live implementation of verify_operation_step rather than the current unresolved grant; Stable operation/step IDs in POST /execute receipts


## What it asked for

_Nothing._
## Its own summary

Round 201 produced four recorded proposals: (1) verified transactional cross-surface execution, (2) safe partial-workflow recovery, (3) IMU-gated private physical approval for the owned pendant hardware, and (4) truthful audio delivery/heard status. Live discovery found a concrete failure: a 420.7 KiB 24 kHz response rendered successfully on the Mac but bridge-result reporting failed with HTTP 413; the pipeline explicitly cannot prove relay departure or playback because no device_playback event/job ID exists. I recorded that finding. Current Mac/relay/browser are healthy and Accessibility/Screen Recording are now granted, so that old blocker is no longer current.

**Biggest unknown:** I still need the executor/verifier contract implemented: stable operation_id/step_id/attempt_id correlation in execute receipts, a live verify_operation_step implementation, and a durable pendant audio job ID plus signed playback start/finish/interruption events. I also need the owner's runtime policy for which action classes may auto-compensate versus require approval. My GET probes of POST /prepare and POST /approve returned 404 because the probe method was GET, so their actual POST schemas remain unverified.

