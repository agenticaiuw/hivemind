# Harness derivation — faculty-action — round 168

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Test the pendant and audio bridge end to end, and tell me exactly what passed.""
- **useful because:** The hardware is physically attached to the Mac today, but there is no owner-facing way to turn that into a trustworthy health result. This would exercise both serial devices, button/LED paths, the ESP32 I2S bridge, and the already-accepted 24 kHz path, then return a receipt instead of a vague 'connected'.
- **path:** pendant → mac-planner → mac-terminal → relay-realtime → faculty-perception → faculty-action
- **model tier:** background for deterministic diagnostics; realtime only to explain failures conversationally
- **latency:** 15–60 seconds for a full fixture; under 3 seconds for a cached connection check
- **cost:** <$0.01 per run; almost all cost is local serial and fixture time, not model tokens
- **security:** No microphone capture and no flashing. Serial output may contain identifiers, so redact device IDs by default. Require explicit confirmation before any firmware write or reset.
- **missing:** A typed Mac diagnostic operation that enumerates the two known serial ports and returns exit code, stdout/stderr, and timestamps; A read-only pendant/bridge test protocol with a versioned receipt; A relay route to persist the diagnostic receipt and expose it to faculty-perception

### ""Make this a safe, resumable job: if the Mac loses connection halfway through, continue when it comes back and don't repeat anything that already happened.""
- **useful because:** Long tasks currently span a wearable, relay, Mac, and browser, but a link drop can leave the owner unsure whether a side effect happened. A resumable step ledger with idempotency keys, postcondition verification, and a physical resume/cancel gesture would let the system finish real work without duplicate sends or silent partial completion.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-judgement → faculty-action → faculty-perception
- **model tier:** background for planning and reconciliation; realtime only for immediate owner questions
- **latency:** Immediate local acknowledgement; reconciliation within 5 seconds of Mac/browser return
- **cost:** <$0.03 per job, dominated by a small planning/reconciliation call; storage and verification are local
- **security:** Never replay an irreversible step from an ambiguous receipt. Store hashes and action IDs, not page secrets. Resume requires the existing deliberate pendant confirmation for risky steps; unknown outcomes are surfaced as unknown.
- **missing:** A durable per-step idempotency/lease record shared by relay and Mac; A narrow executor receipt schema with actionId/attemptId and explicit unknown outcome; Integration of verify_operation_step into commit decisions, not merely post-hoc display; A reconnect handshake between pendant and relay for pending jobs

### ""When I am interrupted, give me one short wearable summary and let me defer it without opening the Mac.""
- **useful because:** The pendant is the only surface continuously available, while the Mac and browser know the actual context. This would have the relay combine urgency, active Mac app/browser state, and owner quiet-hours policy into a privacy-minimized spoken/LED card; a button gesture defers it and records the exact reminder, so interruptions become actionable instead of lost.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** small background model for ranking and summarization; realtime only when the owner asks follow-up
- **latency:** Under 2 seconds from event to a compact wearable notification; deferred item durable immediately
- **cost:** <$0.01 per event with local state extraction and short summaries; batch low-priority events to reduce calls
- **security:** Send only coarse app/site labels and event metadata to the relay, never page contents by default. Suppress private-window and secure-input context. Deferral is reversible; any external action still requires confirmation.
- **missing:** A push event contract carrying urgency, expiry, and privacy classification; A pendant notification queue that can distinguish unread, deferred, expired, and acknowledged items; A Mac/browser context projection limited to labels rather than content; A two-button gesture mapping for acknowledge versus defer

### ""Let me use the assistant on private Mac and browser data without raw page contents, messages, or documents leaving the Mac unless I explicitly allow it.""
- **useful because:** Today the relay can coordinate the Mac, browser, and wearable, but the owner cannot express a durable, inspectable rule for what private content may cross that boundary. A local data firewall would make the system useful for sensitive work rather than forcing an all-or-nothing trust decision.
- **path:** mac-planner → mac-terminal → browser-extension → relay-realtime → pendant → faculty-perception → faculty-judgement
- **model tier:** A small local model/classifier for field detection and redaction; realtime only for explaining a blocked transfer
- **latency:** Under 300 ms for known patterns; under 2 seconds for an unfamiliar document with a preview
- **cost:** <$0.01 per request when local; occasional background classification dominates
- **security:** The firewall itself must run before relay serialization, fail closed on uncertainty, and emit only policy-safe hashes/labels. The owner needs an inspectable transfer log and one-time override; secret values must never be included in previews or model prompts.
- **missing:** A Mac-local egress interception point before relay/job serialization; A typed policy language for source, destination, field class, purpose, and expiry; A redaction engine that preserves task utility while proving what was withheld; A wearable-readable override summary that never reveals the protected value

### ""When I ask for help with a sensitive document, show me exactly which facts the assistant used and let me revoke that access later.""
- **useful because:** The owner needs more than an action receipt: they need provenance for reasoning over personal files and a way to withdraw future access. This creates a user-visible, time-bounded evidence capsule linking the pendant request, Mac/browser sources, extracted facts, and downstream actions without copying the entire source document to the relay.
- **path:** pendant → mac-planner → mac-vision → browser-extension → relay-realtime → faculty-perception → faculty-action
- **model tier:** Background model for local evidence extraction and summarization; realtime only for a spoken provenance query
- **latency:** Initial capsule within 5 seconds; revocation takes effect before the next relay dispatch
- **cost:** <$0.05 per sensitive task, dominated by local extraction and a compact encrypted index
- **security:** Evidence capsules must contain hashes, locators, sensitivity labels, and minimal snippets by default—not source contents. Revocation must prevent future reuse but honestly cannot erase copies the owner explicitly exported; that limitation must be displayed.
- **missing:** A Mac-local evidence capsule/index with source hashes and retention expiry; A revocation-aware relay authorization check on every downstream use; A provenance response surface on the pendant, not just a dashboard; A clear distinction between source access, derived fact, and action authorization

### ""Teach the assistant my preferred way of doing recurring tasks by watching only the outcomes I approve, then let me preview and edit the learned routine before it ever runs automatically.""
- **useful because:** The current system can run routines, but the owner cannot safely turn repeated, approved work into a personal procedure without hand-authoring every step. Outcome-based learning would use actual Mac/browser receipts and owner corrections while keeping automatic execution disabled until the routine is reviewed.
- **path:** pendant → mac-planner → browser-extension → faculty-action → faculty-perception → faculty-judgement → relay-realtime
- **model tier:** Background model for clustering approved outcomes and drafting routine candidates; realtime only for preview questions
- **latency:** Draft after 3–5 approved repetitions; preview under 2 seconds; no automatic execution until explicit review
- **cost:** <$0.05 per candidate routine; storage and clustering dominate, not realtime inference
- **security:** Never learn from rejected, private, or ambiguous actions. Candidate routines must show every parameter and side effect, expire unless renewed, and require the existing physical approval boundary for risky steps. Do not infer secrets or credentials into a routine.
- **missing:** An outcome-only learning dataset separated from raw page/document contents; A routine-diff/preview editor with parameter sensitivity labels; A promotion workflow from candidate to enabled routine; Negative examples and owner rejection signals that prevent unsafe generalization


## What it asked for

### `c6-j004` (context) — current pendant hardware revision and button count
- why: Fresh hardware discovery reports exactly one user button, while earlier firmware notes in the established record described sw0 and sw1 and gesture headroom. Action confirmation and defer/cancel proposals depend on this.
- would change: If one button is authoritative, I will design all confirmation/defer flows around press/release timing and avoid assuming a second gesture input; if two are physically present, I will target sw1 for safe approval/cancel.

## Its own summary

I discovered the live inventory again: Safari has 9 tabs and the Mac bridge is online; the mobile device is offline. I recorded three capabilities: (1) a read-only USB pendant + ESP32 diagnostic with typed exit codes and a 24 kHz receipt, (2) resumable cross-surface jobs with idempotency, postcondition verification, and safe physical resume—the highest-value proposal this round, because it prevents duplicate real-world side effects after link loss, and (3) privacy-minimized wearable interruption cards with acknowledge/defer semantics. The recorder noted the first is close to an existing audio self-test, so its genuine gap is the serial/provenance contract, not another audio feature.

**Biggest unknown:** The authoritative pendant hardware revision: fresh hardware discovery says one user button (sw0), while older firmware notes said sw0/sw1. I still need that resolved before specifying safe approval, cancel, or defer gestures. I also still need a typed read-only Mac serial diagnostic surface returning argv/exit code/stdout/stderr and a durable cross-surface step ledger that can feed verify_operation_step into commit decisions.

