# Harness derivation — faculty-perception — round 195

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live mac reachability and permissions** — At snapshot time 2026-08-08T22:48Z, Mac local agent reports accessibility trusted, screen recording granted, requiredMissing/optionalMissing empty, ready=true; browser extension online on Safari X.com tab 3584108 with 4 tabs and zero pending commands; relay reachable with D1 store and Mac bridge online.
  - evidence: read_continuity_snapshot(include relay,pipeline) resolved to GET /ops/snapshot, HTTP 200; returned status.permissions and browser/relay payload.

## Capabilities it proposed

### "“I’m back. Show me exactly what I was doing, what changed while I was away, and put me back at the next safe step.”"
- **useful because:** This is the single most useful daily behavior: a grounded re-entry, not a vague summary. It would join the live Mac window/screenshot, browser tab and page evidence, unfinished Mac jobs/receipts, and relay/pipeline events, then explicitly separate observed state from inference and offer one reversible next action. Accessibility and Screen Recording are now actually ready, so it can inspect the current UI rather than pretending the last ledger is current.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a cheap background summarizer for the bounded snapshot; reserve realtime for the owner's spoken question and judgement/action for the one next step.
- **latency:** 3-5 seconds for the evidence bundle; under 1 second for the spoken acknowledgement. Vision is the dominant latency.
- **cost:** Roughly $0.01-$0.05 per return depending on screenshot/OCR and summary tokens; no cloud browser call if the extension already supplies the page.
- **security:** Screenshots and browser content can contain secrets. Keep evidence capsules local, redact before relay/model submission, display source and capture time, and require confirmation before typing, sending, deleting, or navigating away. Stale UI must be labeled stale rather than treated as present truth.
- **missing:** A single orchestration route that joins current /observe, browser state, jobs/receipts, pipeline, and evidence capsules with per-source timestamps.; Mount browserProvenance routes and make the relay/browser result carry a joinable capsule ID/hash for cloud reads.; A structured Mac vision observation receipt keyed to the action ledger, not just an image.

### "“Tell me what changed in my browser or Mac since I last checked, show me before-and-after proof, and undo only the changes I choose.”"
- **useful because:** Owners need an audit they can trust after delegated work, especially when a site or app may have changed state. This would correlate browser command receipts, evidence capsules/content hashes, Mac action-ledger pre/post state, and current visual state into a diff with provenance; it would not confuse a successful click with a confirmed page mutation.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Cheap deterministic diffing and hashing first; use a small text model only to explain semantic changes; realtime only for the spoken request.
- **latency:** 2 seconds for ledger/evidence diffs, up to 6 seconds when a fresh screenshot or page read is needed.
- **cost:** Usually <$0.01 (local hashes and receipts); up to $0.03 for one semantic explanation or fresh browser read.
- **security:** Never send full secret fields to the model; use redacted capsule claims and withheld digests. Undo must be limited to action-ledger steps marked resumable and require confirmation for external side effects. A missing before-state must be reported as unverified, not reconstructed.
- **missing:** A mounted browser provenance endpoint and a standard mutation receipt join between browser commandId and Mac ledger stepKey.; A read-only diff endpoint that returns before/after hashes, source timestamps, and confidence without exposing secret values.; A safe undo planner that refuses when the observed DOM/app state no longer matches the recorded post-state.

### "“Before you do anything consequential, prove you heard me correctly; if the pendant audio is degraded, ask me to repeat instead of guessing.”"
- **useful because:** A wearable command can be clipped, noisy, or packet-damaged while the Mac and browser are perfectly healthy. This capability makes perception—not model confidence—the gate: the pendant's local capture verdict, relay transcript, and the current Mac/browser target must agree before an action is released. It prevents the worst failure mode: a plausible misheard command changing the owner's files, messages, or web account.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → faculty-perception → faculty-judgement → faculty-action
- **model tier:** No expensive model for the first gate: firmware quality verdict and packet sequence checks are deterministic. Use realtime transcription for a clear utterance; use the cheaper planner only after a valid transcript and target evidence exist.
- **latency:** Local unusable-audio rejection under 150 ms at utterance end; 1-2 seconds for a repeat prompt; 3-6 seconds for target verification before an external action.
- **cost:** Negligible firmware/relay metadata cost; roughly $0.01-$0.04 only when a clear utterance reaches transcription/planning.
- **security:** Quality metrics, not raw audio, should leave the pendant unless the owner explicitly requests a recording. Never downgrade a degraded verdict because the transcript looks confident. Confirmation is mandatory for messages, purchases, deletion, navigation with side effects, and any mismatch between browser evidence and intended target.
- **missing:** A relay contract carrying the offline-capture-integrity-sentinel sequence/verdict and packet-loss window alongside the transcript.; A judgement policy that treats degraded/unusable as a hard stop and records the refusal reason in the pipeline.; A pre-action target echo that identifies the exact app/tab/account/object using browser evidence or Mac observation.

### "“When an action could send, buy, delete, or publish something, give me a physical challenge on the pendant and do not release it until I answer that exact challenge.”"
- **useful because:** A spoken “yes” can be accidental, misheard, or issued while the owner is distracted. A short-lived challenge displayed/spoken by the system and confirmed with a deliberate pendant gesture creates a last-mile authorization boundary that the Mac, browser, and relay cannot silently bypass. The owner gets confidence that a consequential action did not happen merely because a model inferred intent.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Deterministic challenge generation, nonce binding, timeout, and replay protection; no model call for the authorization itself. Realtime only speaks the challenge and receives the owner's answer.
- **latency:** Challenge in under 500 ms after the proposed action; 10-20 second expiry; action release immediately after verified confirmation.
- **cost:** Negligible inference cost; roughly $0.01 or less in relay metadata per confirmed action. Firmware change is the dominant engineering cost.
- **security:** Bind the challenge to the exact action digest, target, account, and expiry; reject replay and stale confirmations. Never speak secrets in the challenge. A lost link must fail closed. The owner should be able to configure which action classes require this gate.
- **missing:** A firmware gesture distinct from ordinary conversation control, with a monotonic counter and signed confirmation frame.; A relay authorization object containing action digest, nonce, expiry, and device session identity.; Mac/browser executors that refuse to act without a matching authorization object and record the authorization in the receipt.

### "“Give me a private mode: for the next conversation, keep the audio, transcript, screenshots, browser claims, and action details off the relay and erase the temporary material when we finish.”"
- **useful because:** The owner should be able to use a cloud-connected wearable without having every sensitive conversation become durable system context. A physical gesture would establish an explicit privacy boundary across the pendant, relay, Mac, and browser—not just a model instruction. The system would announce exactly which local functions are unavailable in this mode and provide a verifiable expiry receipt.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → unified → faculty-perception
- **model tier:** Deterministic policy enforcement and deletion receipts; use realtime only for the conversation itself. No summarizer should see or retain the private payload.
- **latency:** Mode activation under 1 second; teardown and local purge under 3 seconds, with a visible receipt of what was erased and what could not be erased.
- **cost:** Lower than normal use because persistence, summarization, and most relay calls are suppressed; engineering cost is policy propagation and deletion verification.
- **security:** Privacy mode must be fail-closed: if the relay cannot honor no-store semantics, the pendant must refuse to start. Do not promise deletion of third-party browser/server history. Keep only a minimal non-content audit marker, unless the owner opts out of even that.
- **missing:** A privacy lease propagated from pendant to relay, Mac agent, browser extension, and model routing.; No-store request handling for realtime audio, pipeline traces, screenshots, browser provenance, and action receipts, plus local purge verification.; A device-visible activation/deactivation indicator and a recovery path when the link drops.

### "“If the link is down, remember this request safely and finish it later—but only after showing me exactly what was recorded and asking again before anything external happens.”"
- **useful because:** Today an interruption can turn a spoken request into either lost intent or an unsafe attempt to act on stale context. An encrypted, expiring intent escrow would let the pendant preserve the owner's goal offline, while preventing an old command from executing against a changed browser, file, account, or price. On reconnection the Mac and browser would re-evaluate the target, and the owner would get a fresh confirmation.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Firmware stores only a compact encrypted intent envelope; a cheap background model reconstructs a draft when connectivity returns; judgement compares the new target/evidence to the original before any action. Realtime is used only for the reconnection briefing.
- **latency:** Offline capture acknowledgement under 300 ms; reconnection reconciliation within 5 seconds; no action until explicit fresh confirmation.
- **cost:** Minimal storage and relay metadata; one inexpensive planning call per recovered intent, with no charge while offline.
- **security:** Use device-bound encryption, monotonic sequence numbers, expiry, and one-time consumption. Never persist raw audio by default. If target identity, account, or relevant page state changed, discard the action draft and ask the owner rather than adapting silently.
- **missing:** A bounded encrypted intent-envelope format and firmware NVS ring distinct from the SD failure buffer.; Relay/Mac ingestion and reconciliation that treats an offline envelope as untrusted evidence, not an authorization.; A changed-target detector spanning browser evidence, Mac state, and action policy, with explicit owner re-confirmation.


## What it asked for

_Nothing._
