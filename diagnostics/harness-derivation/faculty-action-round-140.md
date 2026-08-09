# Harness derivation — faculty-action — round 140

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/browser readiness round 140** — Mac agent is healthy v0.5.0, relay reachable, Safari bridge online with 9 tabs and zero pending commands; Accessibility and Screen Recording are now granted and all listed automation permissions are ready. No pendant appears in the live device list, and browser bridge reports no capabilities/nonce yet.
  - evidence: GET /health; GET /browser/status; GET /ops/status at 2026-08-08T00:46Z

## Capabilities it proposed

### "“The thing timed out—don't retry it. Find out whether it actually happened, tell me exactly what state it is in, and only offer a safe repair.”"
- **useful because:** Network and browser actions can commit remotely while the executor loses its response. Blind retries can send duplicate messages, create duplicate calendar events, or double-submit forms. This capability turns an ambiguous receipt into a reconciled outcome using fresh Mac/browser evidence, then either closes it as succeeded, safely compensates it, or leaves it explicitly unresolved for the owner.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-action → faculty-judgement
- **model tier:** Background model for reconciliation planning; realtime only to explain the result on request.
- **latency:** Up to 10 seconds after timeout for idempotency lookup and fresh verification; never auto-retry a non-idempotent action.
- **cost:** Roughly $0.01–$0.05 per incident, dominated by one planner call; verification and relay storage are negligible.
- **security:** Relay stores only operation IDs, action class, and evidence hashes; browser secrets remain in the browser. Compensation or any second mutation requires the existing physical approval latch. An unresolved state must be spoken plainly rather than inferred from a stale receipt.
- **missing:** A durable operation-reconciliation state machine distinguishing succeeded, failed-before-commit, failed-after-commit, and unknown; Idempotency-key propagation for supported Mac/browser mutations; A narrow compensation-plan interface that faculty-action can stage but not execute without approval

### "“When my pendant is USB-connected to my Mac, use it as a presence key: let this Mac prove it is paired to my pendant before accepting sensitive action requests, even when LTE is unavailable.”"
- **useful because:** The owner gets a local, LTE-independent trust boundary. A stolen or unattended Mac process cannot claim to be the pendant, and sensitive actions can be bound to the physical device actually worn or connected. This uses the hardware that is physically present today rather than assuming LTE registration.
- **path:** pendant → mac-planner → mac-terminal → relay-realtime → faculty-action → faculty-judgement
- **model tier:** Cheap background cryptographic protocol and policy code; no realtime model is needed for challenge verification.
- **latency:** Under 500 ms for a USB challenge-response; pairing setup may take 30 seconds and explicit owner confirmation.
- **cost:** Under $0.01 per pairing or authorization; no model tokens after protocol implementation.
- **security:** The pendant must never export private key material or form secrets. Pairing must require a deliberate sw1 gesture and show a distinct LED/audio cue. Revocation must be possible from the Mac and relay. USB transport is authenticated, not merely identified by a serial path; sensitive requests remain staged if the proof is absent.
- **missing:** Firmware-held device key and nonce-signing command over the nRF9160 USB serial link; Mac agent USB device enumeration and challenge-response route; Relay device registry and revocation records for pendant public keys; Policy mapping which action classes require physical presence

### "“Show me a replayable timeline of everything you did for that request—what the pendant confirmed, what the Mac/browser changed, what was independently verified, and what remains unknown.”"
- **useful because:** A single success/failure sentence hides the exact boundary between intention, execution, and truth. A cross-device timeline lets the owner audit a consequential action later, diagnose a partial workflow, and hand an evidence bundle to support without exposing browser secrets.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-action
- **model tier:** Cheap structured event aggregation; use the realtime model only when converting the timeline into a spoken explanation.
- **latency:** Receipts should append within 1 second; opening the timeline should render in under 3 seconds.
- **cost:** Less than $0.01 per timeline; storage is bounded by retention policy and evidence hashes.
- **security:** Events are append-only and hash-chained, but payloads are minimized: no page contents, credentials, or microphone audio by default. Private evidence snippets require an explicit owner request. The timeline must label executor receipts separately from verifier evidence and never upgrade an executor claim to verified truth.
- **missing:** A single operation ID propagated through relay, Mac jobs, browser commands, pendant approval, and verifier calls; Append-only event schema with hash links and redaction classes; Owner-facing Mac or spoken timeline route with retention and deletion controls

### "“Before you commit that change, prove that the person, account, amount, and page/app state you planned against are still the same; if anything changed, stop and ask me again.”"
- **useful because:** A plan can be correct when created and dangerous seconds later: a browser tab can switch accounts, a price or recipient can change, or an app can move focus. The owner gets protection against stale-intent execution rather than learning only afterward that the wrong target was mutated.
- **path:** faculty-judgement → faculty-action → faculty-perception → mac-planner → mac-vision → browser-extension → relay-realtime
- **model tier:** Cheap deterministic state-diff and policy evaluation; use a slower model only to explain a detected mismatch.
- **latency:** 100–500 ms for local app/browser revalidation; up to 3 seconds for a fresh perception read. Any mismatch blocks the mutation.
- **cost:** Under $0.01 per guarded action; dominated by occasional screenshot/DOM or app-state capture.
- **security:** Capture only declared locators and hashes, never whole pages or secrets. A mismatch is fail-closed. Reapproval must bind to the new state digest, not merely repeat the old spoken consent.
- **missing:** Precondition snapshots attached to every planned mutation; A deterministic diff policy for identity, recipient, amount, destination, and account fields; An execution gate that refuses stale snapshots before invoking Mac/browser action tools

### "“Give me a safe rehearsal of this computer task: show the exact files, fields, messages, and external effects it would change, and let me approve only that concrete effect set.”"
- **useful because:** The owner can distinguish a harmless draft from an irreversible send, deletion, purchase, or permission change before anything runs. The rehearsal is generated from the actual current Mac/browser state, not a generic plan, and approval becomes invalid if the effect set changes.
- **path:** faculty-judgement → faculty-perception → faculty-action → mac-planner → mac-vision → browser-extension → relay-realtime
- **model tier:** Background planner for effect extraction; realtime only for the owner's conversational presentation.
- **latency:** 3 seconds for common Mac/browser tasks; longer tasks return a staged rehearsal rather than mutating.
- **cost:** $0.01–$0.04 per rehearsal, mostly planner/perception calls; no cost for approval itself.
- **security:** Effect descriptions are redacted and typed; secrets and full page content never enter the relay. The system must explicitly mark unenumerable side effects (network sends, scripts, downloads) and refuse approval when the forecast is incomplete for high-risk actions.
- **missing:** Effect-set schema covering file, app, browser, network, and communication side effects; Dry-run adapters for Mac and browser action types; Approval binding to an effect-set digest and invalidation on state change


## Changes it proposed to its own stack

### `integration` — Add an operation identity and reconciliation envelope that every relay handoff, Mac job, browser command, pendant approval, executor receipt, and verify_operation_step call carries. The envelope must include operation_id, step_id, attempt_id, idempotency key, risk class, and terminal state (verified, failed, unknown), with a rule that an executor receipt alone cannot close the operation.
- **owner gets:** When a connection drops mid-task, the owner gets one trustworthy answer instead of duplicate actions or a misleading success. Partial work can be finished safely and the exact unresolved boundary remains visible.
- effort: Medium: shared schema, adapters in relay/Mac/browser, and reconciliation tests for timeout-after-commit cases.  ·  risk: Old clients may omit IDs; treat them as legacy unknown rather than guessing. A malformed envelope must halt mutation and surface an actionable error. Recovery is compatibility parsing plus explicit owner approval for repair.
- cost: Negligible runtime/API cost; modest storage for bounded event and receipt metadata.  ·  latency: Adds one local serialization step and usually one verifier round trip (sub-second locally, up to several seconds for browser state).
- security: Improves auditability; IDs and hashes only cross relay by default. Must not place page contents or credentials in the envelope.
- depends on: verify_operation_step; Existing job receipts and journal routes; Browser command correlation IDs; Physical approval latch for any compensating mutation

### `interaction` — Add a cross-device commitment barrier that converts a natural-language request into a typed effect set before execution. The Mac/browser adapters must enumerate intended writes and external sends, faculty-perception must hash the relevant live state, and faculty-action may execute only the approved effect-set digest. Any unenumerated or newly discovered effect forces a return to staged state rather than silently proceeding.
- **owner gets:** The owner can approve exactly what will happen instead of trusting a vague “send it” confirmation, and unexpected side effects become a stop—not a surprise discovered in an inbox or filesystem afterward.
- effort: High: define effect taxonomy, instrument every mutating adapter, build dry-run/unknown-effect handling, and test partial enumeration across Finder, Mail, Calendar, browser forms, and shell intents.  ·  risk: Some applications cannot expose a complete effect forecast. Those actions must degrade to blocked/unknown, never claim a complete rehearsal. Old actions without adapters remain staged until migrated.
- cost: Small storage and hashing overhead; one extra perception/planning call per guarded action, typically a few cents at most.  ·  latency: Adds roughly 1–4 seconds before execution; zero added latency for explicitly unguarded read-only work.
- security: Reduces accidental disclosure and unauthorized mutation. Effect metadata must use sensitivity labels and avoid copying secrets or full document contents to relay.
- depends on: Existing action risk and approval modules; Typed Mac/browser mutation adapters; verify_operation_step; Operation IDs and state digests


## What it asked for

_Nothing._
## Its own summary

Recorded three new capabilities and one integration change: (1) reconcile timeout/unknown actions from fresh Mac/browser evidence without blind retries, (2) use the USB-connected pendant as a cryptographic, LTE-independent presence key, and (3) provide a redacted, replayable cross-device action timeline; plus propagate operation/step/attempt/idempotency IDs through executor and verifier paths. Fresh live probes show the Mac, relay, Safari bridge, Accessibility, and Screen Recording are ready, with 9 Safari tabs and no pending commands.

**Biggest unknown:** The physical pendant is still absent from the live device registry and the browser bridge has no nonce/capabilities. I still need the nRF9160 USB serial device to be registered and a firmware-side challenge-response endpoint (with the owner's explicit pairing gesture) before presence-bound execution can be implemented or honestly tested.

