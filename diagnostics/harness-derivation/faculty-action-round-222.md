# Harness derivation — faculty-action — round 222

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Remember this, and turn it into a task with the right context.” I press the pendant bookmark button while speaking; later the system gives me a concise, actionable reminder tied to what was on my Mac/browser at that moment."
- **useful because:** A bookmark today preserves an audio artifact, but not the situation that made it useful. This would capture the owner's intent plus a privacy-filtered foreground/browser context, resolve it asynchronously into a task, and let the owner find the resulting reminder without reconstructing where the thought came from.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime only acknowledges the press and streams a tiny event; a cheaper background model classifies/transcribes the memo and extracts due date, entities, and confidence. Mac-planner performs the reminder write; faculty-perception verifies the resulting reminder and context linkage.
- **latency:** Immediate tactile acknowledgement under 250 ms; upload can be deferred offline. Semantic extraction within 30 s of connectivity; reminder creation only after confidence threshold or explicit confirmation.
- **cost:** One short background transcription/extraction call, typically <$0.01–$0.05; Mac and relay work dominate neither latency nor cost.
- **security:** Context capture must be allowlisted and redact passwords, message bodies, and page secrets; browser contributes URL/title and selected non-sensitive metadata, not DOM contents by default. Never create a high-impact task or send a message solely from an ambiguous memo. Missing context or low confidence becomes an inbox item, not a fabricated reminder.
- **missing:** A typed context-bundle schema correlating pendant bookmark/audio with an observed Mac/browser snapshot; A background memo-to-task extraction worker with confidence and confirmation policy; A privacy allowlist for browser/app context fields; A dashboard view showing source audio, extracted task, and verification provenance

### "“If I say undo that now, reverse the last reversible thing you did, and tell me if it really went back.” The pendant or voice request should select a recent verified action and execute its compensating operation, not merely claim success."
- **useful because:** A verified action can still be a mistake. A bounded undo window gives the owner a practical escape hatch for calendar edits, reminders, file moves, and drafts without requiring them to remember the original UI path.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime parses the short undo request; a cheaper deterministic action-ledger component selects only an unexpired reversible receipt and its predeclared compensator. Mac-planner executes the compensator, and faculty-perception independently verifies the postcondition.
- **latency:** Resolve the target in under 1 s and stage the compensator immediately; execute within 3 s after the owner’s existing physical approval for any class policy marks as confirm-required. Unknown verification must stop retries and be surfaced.
- **cost:** Near-zero model cost for ledger lookup; at most a small classification call when the spoken reference (“the thing from earlier”) is ambiguous. Mac verification is the main latency.
- **security:** Only actions with an explicit inverse, bounded expiry, and before-state digest qualify. Never synthesize an inverse for a send, deletion, purchase, or external side effect. Require the existing physical transaction approval latch for anything beyond local drafts/reminders; expose the exact human-readable target and mark rollback unknown when verification cannot establish it.
- **missing:** A compensator field and before-state digest in actionLedger receipts; A bounded undo index that survives relay restarts but stores no page secrets; A route that stages an inverse operation against a receipt without re-planning from ambiguous prose; Per-action-class owner policy for which compensators may run immediately

### "“Do not act if the pendant has come off me, even if a queued approval or voice command arrives; tell me when it is safe to continue.” The wearable should distinguish an intentional hand interaction from a pendant lying on a desk or in a bag."
- **useful because:** A physical approval is only meaningful if the owner is actually wearing and handling the pendant. Off-body detection prevents queued actions, accidental button presses, and stale approvals from being treated as deliberate consent, especially while the Mac/browser remain online.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Firmware performs the low-latency IMU/orientation and button-correlation test locally; relay applies the signed wearable-presence state to pending operation leases. No expensive model is needed except optional background tuning from anonymized motion features.
- **latency:** Presence state update within 300 ms of a stable off-body transition; a pending operation is frozen immediately and expires conservatively. Re-wear can resume status delivery, but never silently approves an operation.
- **cost:** Negligible inference/API cost; roughly 1–3 mA intermittent IMU duty-cycle power and a small firmware footprint. Engineering cost is integrating the already-owned LSM6DSOX and calibrating per-owner thresholds.
- **security:** Transmit only a signed state, confidence, monotonic counter, and transition time—not raw motion traces. Treat uncertainty as off-body for irreversible actions. A re-wear event only restores the ability to review/approve; it cannot consume an approval generated while absent. Avoid claiming identity authentication: this is presence/handling evidence, not biometrics.
- **missing:** Firmware integration of the owned LSM6DSOX on i2c2, with calibration and signed presence transitions; A relay lease rule that invalidates or freezes pending approvals on off-body/uncertain state; A compact pendant haptic/audio status pattern for frozen versus resumed operations; A test fixture covering desk, pocket, bag, and deliberate two-button handling

### "“Forget that moment everywhere.” After I make a voice note or bookmark, I should be able to name it or press a deliberate cancel gesture and have the system find and delete its audio, transcript, extracted task, Mac/browser context snapshot, relay copies, and queued delivery records across every surface."
- **useful because:** A wearable assistant can accumulate intimate recordings and action context faster than an owner can manually clean them up. Today there is no single, truthful erasure operation spanning the pendant’s failure-path store, relay queues, Mac jobs, and browser-derived artifacts. This gives the owner a human-understandable privacy escape hatch rather than asking them to trust that one copy was deleted.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime handles only the immediate acknowledgement and disambiguation. A deterministic background erasure coordinator resolves the event’s opaque IDs and propagates signed tombstones; faculty-perception independently verifies file, queue, job, and browser state. No model should infer deletion from silence.
- **latency:** Acknowledge within 250 ms. Mark the item non-deliverable immediately, even if disconnected; complete reachable-surface deletion within 10 s and retry offline surfaces until expiry. Report partial/unknown rather than claiming complete erasure.
- **cost:** Low model cost; mostly bounded relay, Mac, and browser I/O. A short disambiguation call may cost <$0.01 when the spoken reference is ambiguous.
- **security:** The erase command itself needs deliberate physical confirmation and replay-resistant item IDs. Do not send raw private content to the relay just to identify it; use opaque IDs and local hashes. Tombstones must prevent late offline uploads from resurrecting content. Immutable operational security logs should retain only the minimum fact that an erasure was requested/completed, never the erased payload or its transcript.
- **missing:** A cross-surface privacy object manifest mapping one capture to every derived artifact and copy; A signed tombstone protocol understood by pendant OUTBOX/INBOX, relay, Mac jobs, and browser commands; Read-only erasure verification for pendant storage and relay retention, not just Mac/browser postconditions; A conservative policy for backups, model-provider retention, and artifacts already exported outside the system; A pendant-local delete-and-quarantine behavior that works while offline and never deletes unrelated queue items

### "“Stop everything I have pending.” A deliberate emergency gesture on the pendant should revoke every uncommitted action lease across the relay, Mac agent, and browser—not merely cancel the item currently visible—and return a signed receipt listing what was cancelled versus already committed."
- **useful because:** When the owner notices a mistaken command, a stale approval, or a compromised session, hunting through individual jobs is too slow. A physical all-stop gives them one dependable brake that works even when the Mac UI or browser is confusing.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** No generative model is needed for the revoke itself. The relay performs deterministic lease revocation; Mac/browser agents cancel only uncommitted work; faculty-perception verifies cancellation and classifies already-committed operations as not reversible.
- **latency:** Pendant-local latch under 200 ms; relay revocation on next connectivity and Mac/browser cancellation within 2 s when online. The system must expose unknown reachability rather than imply remote cancellation succeeded offline.
- **cost:** Negligible API/model cost; bounded control messages and verification receipts.
- **security:** Use a distinct multi-button or long-press gesture so it cannot be triggered accidentally. The pendant stores a monotonic revocation epoch while offline; every executor rejects leases older than that epoch. This is cancellation, never deletion or rollback, and must not pretend an external send was unsent.
- **missing:** A global revocation epoch understood by relay, Mac, and browser executors; An offline pendant command and compact receipt queue for revocation state; Executor semantics distinguishing accepted, cancelled-before-commit, committed, and unknown; A dashboard and haptic/audio language for partial reachability

### "“Put me in confidential mode for the next hour.” The pendant should enforce a time-bounded privacy boundary: no audio/context leaves the device, no new browser or Mac snapshots are attached to captures, and queued private material is held locally until I explicitly release or discard it."
- **useful because:** The owner needs a practical way to enter a sensitive meeting, medical visit, or conversation without remembering which individual subsystems must be disabled. A single bounded mode is safer than relying on a verbal promise that every surface will stop collecting context.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic policy enforcement on pendant and relay; realtime only confirms entry/expiry. No model should inspect confidential-mode audio or context. A background reconciler can verify that no prohibited event was accepted.
- **latency:** Enter locally within 250 ms and enforce before the next capture/upload. Expiry must be monotonic and survive link loss; remote policy convergence is reported as unknown until confirmed.
- **cost:** Negligible model cost; small policy envelopes and status receipts.
- **security:** Confidential mode must fail closed on uncertain expiry or link state, never silently revert early, and visibly indicate its state through the existing safe cue. It cannot guarantee third-party microphones or external app logging are disabled; the dashboard must state that boundary. Any held data must be encrypted and deletable without upload.
- **missing:** A signed mode lease with monotonic expiry and fail-closed semantics; A capture/upload policy hook shared by pendant, relay, Mac, and browser; A local encrypted quarantine distinct from ordinary failure-path delivery; A clear owner-visible status and explicit exit/discard action


## Changes it proposed to its own stack

### `firmware` — Integrate the already-owned LSM6DSOX on i2c2 as a conservative wearable-presence state machine: sample low-rate acceleration/gyro, detect stable off-body versus handled transitions, persist a monotonic transition counter, and expose only signed state/confidence/timestamp to the relay. Gate pending operation leases on this state; never turn re-wear into approval. Add bench fixtures for desk, pocket, bag, and deliberate sw1 handling before enabling it for irreversible actions.
- **owner gets:** A queued action cannot be approved by a pendant lying on a desk or buried in a bag. The owner gets a real safety boundary around physical consent without transmitting raw motion or adding a new sensor.
- effort: Medium: enable i2c2 in devicetree, add an LSM6DSOX driver/state machine, signed transition envelope, relay lease handling, and bench calibration. No new hardware procurement.  ·  risk: False off-body detection can freeze a legitimate approval; false worn detection could weaken the boundary. Bias uncertain states toward frozen, require stable dwell times, expire pending leases on sensor faults, and provide a safe audio/haptic explanation. Do not describe it as identity authentication.
- cost: No API inference cost; approximately 1–3 mA intermittent IMU duty-cycle power and modest flash/RAM. Uses the already purchased IMU and DRV2605L only if haptic is later wired.  ·  latency: Local transition decisions under 300 ms; relay state propagation depends on link. No effect on the 24 kHz audio codec path if sampling is low-rate and interrupt-driven.
- security: Improves physical-consent integrity while exposing only signed coarse state. Requires replay protection via monotonic counter and strict fail-closed behavior.
- depends on: Relay operation-lease support that freezes on off-body/uncertain state; Firmware integration of LSM6DSOX on i2c2; Bench test harness and owner-selected dwell/calibration thresholds

### `relay` — Add a privacy-and-control coordinator that maintains a per-capture artifact graph, a monotonic global revocation epoch, and signed confidential-mode leases. It must fan out revoke/hold/delete commands to pendant, Mac, and browser, accept idempotent receipts, and expose partial completion without collapsing unknown into success.
- **owner gets:** The owner gets one trustworthy control surface for the two moments that matter most: “stop everything now” and “nothing from this period leaves.” It closes the dangerous gap where each node believes another node handled the privacy decision.
- effort: Large cross-surface protocol work: schema/versioning, relay persistence, executor hooks, pendant queue changes, browser command handling, and adversarial/offline tests.  ·  risk: A coordinator bug could suppress legitimate work or falsely report privacy. Default to fail-closed, use bounded expiries, preserve only opaque IDs in control records, and require independent verification before success is announced.
- cost: Low runtime/API cost; moderate engineering and storage cost for compact manifests and receipts.  ·  latency: Local pendant decisions remain sub-second; online propagation adds one control round trip. Offline nodes remain explicitly unknown.
- security: Materially strengthens revocation and data-boundary guarantees; requires signed envelopes, replay protection, key rotation, and careful separation of control metadata from private payloads.
- depends on: Cross-surface artifact identity and tombstones; Executor support for revocation epochs; Pendant firmware support for offline policy/revocation state; Browser bridge command acknowledgement and verification


## What it asked for

_Nothing._
## Its own summary

This round recorded four non-refactoring proposals: (1) context-linked bookmark-to-task capture across pendant, relay, Mac, and browser; (2) a bounded, receipt-backed undo window for reversible Mac/browser actions; (3) off-body wearable-presence enforcement so a pendant on a desk or in a bag cannot approve queued actions; and (4) the concrete firmware change integrating the owned LSM6DSOX on i2c2 and fail-closed relay lease gating. The single most valuable addition is the receipt-backed undo path: it turns verified execution into recoverable execution rather than a one-way gamble. What I still need is implementation ownership for the missing pieces: a typed context bundle and privacy allowlist, compensator/before-state fields in action receipts, and the relay lease rule that freezes approvals on off-body or uncertain state. I also need the owner to choose conservative dwell thresholds and which action classes are eligible for automatic undo versus requiring approval.

**Biggest unknown:** Whether the existing action ledger/prepare-approve implementation can accept compensators and before-state digests without a new route; the proposal recorder noted those routes were not fully inventoried, so I should not assume their exact schemas.

