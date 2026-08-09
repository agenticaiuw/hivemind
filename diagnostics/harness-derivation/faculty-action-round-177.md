# Harness derivation — faculty-action — round 177

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Do that, and tell me exactly what happened.” Have the system carry out a multi-step Mac/browser task, independently verify the final state, and report a compact proof on the pendant rather than merely saying it was dispatched."
- **useful because:** Today dispatch, execution, and truth are separate. This would make the owner's spoken command trustworthy: it either names the verified final state or clearly says unknown, with no false success.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision → faculty-perception → faculty-action
- **model tier:** Use realtime only for the short owner interaction; use a cheaper background planner for decomposition and faculty-perception for verification.
- **latency:** First acknowledgement under 1 s; execution may take minutes; final verified receipt within 5 s of the last action.
- **cost:** Roughly $0.01–$0.08 per task, dominated by browser/vision checks; no continuous audio cost.
- **security:** The pendant receives only a human-readable result and opaque receipt hash, never page secrets. Irreversible submissions require the existing physical transaction approval latch. Evidence defaults to hash/minimal snippet.
- **missing:** A single orchestrator that binds plan step IDs to executor receipts and verify_operation_step results; A pendant delivery path for compact verified receipts while USB/LTE links differ; A canonical result state enum: verified, failed, partially_completed, unknown

### "“If I lose connection now, finish safely and tell me when I’m back.” Preserve an already-approved, in-flight Mac/browser operation across a pendant or relay disconnect, resume only idempotent steps, and deliver the final verified result when the pendant reconnects."
- **useful because:** A dropped wearable link should not strand a half-completed task or cause duplicate clicks. This turns unreliable connectivity into a bounded, understandable handoff instead of requiring the owner to guess whether to retry.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-action → faculty-perception
- **model tier:** Background/cheap model for retry classification and reconciliation; realtime only when the owner reconnects and asks for status.
- **latency:** Persist the operation state before every side effect; resume within 10 s of Mac availability; speak the reconciled result within 2 s of reconnect.
- **cost:** <$0.01 per resumed operation; dominated by one reconciliation model call, with storage and relay traffic negligible.
- **security:** Only operations carrying an unexpired approval lease may resume. Never replay non-idempotent browser submits; mark them unknown and require a new physical approval. Encrypt receipts at rest and expire them.
- **missing:** An operation journal with durable step checkpoints and idempotency keys; A resume policy that distinguishes safe retry, compensatable step, and manual re-approval; Reconnect delivery that can fetch pending receipts without replaying the action

### "“Undo what you just did.” Within a short, visible window, let me make one deliberate pendant gesture that reverses the last reversible Mac/browser action, then verify the restored state and tell me if reversal was complete."
- **useful because:** The owner gets a practical safety net for accidental edits, file moves, volume changes, or drafted messages without needing to find the Mac UI. It is stronger than a generic undo button because it proves the old state returned.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-action → faculty-perception
- **model tier:** No realtime reasoning after the initial command; use deterministic action metadata and a cheap verifier, escalating only when rollback is ambiguous.
- **latency:** Offer the undo window immediately; execute the reversal under 2 s for local actions and under 8 s for browser actions; verify before reporting success.
- **cost:** <$0.01 per undo, mostly verification; no model call for metadata-backed reversals.
- **security:** Only reversible actions with a recorded before-state are eligible. A gesture can request undo but cannot override approval requirements for destructive compensations. Sensitive before-state is retained as a hash or encrypted local snapshot, not sent to the pendant.
- **missing:** Before-state capture in action receipts, not just after-state logs; Per-action compensators for common AppleScript, file, and browser mutations; A pendant-visible expiry countdown and safe failure wording

### "“Take care of this dispute until it is actually resolved.” Let the system manage a long-running case across email, web portals, documents, and calendar: gather the case facts privately, prepare each proposed communication, obtain a deliberate pendant approval before sending, watch for replies, schedule follow-ups, and stop only when an independently verified resolution or an explicit owner decision exists."
- **useful because:** Today the owner can ask for one browser click or one draft, but must personally remember every later reply, deadline, and escalation. This would turn a vague real-world outcome—refund, support case, insurance claim, cancellation—into a supervised process that survives days and interruptions without silently sending anything.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision → faculty-judgement → faculty-perception → faculty-action
- **model tier:** Use a cheaper background model for case extraction, deadline tracking, and draft preparation; use realtime only for the owner's approval conversation and exceptions. Use deterministic policy for send/stop rules.
- **latency:** Acknowledge intake in 2 s; produce the first case plan within 30 s; monitor replies on a scheduled cadence; require no continuous session. Approval prompts should reach the pendant within 2 s of a proposed outbound action.
- **cost:** Approximately $0.05–$0.50 per case over its lifetime, dominated by document/reply extraction and occasional vision checks; polling and storage are minor.
- **security:** Browser credentials and message contents remain on their native Mac/browser surfaces; the pendant gets only a redacted summary and approval digest. Every outbound message or form submission requires a fresh, scoped physical approval. Expired cases, changed facts, unknown sender identity, and irreversible commitments stop rather than retry. Keep an append-only case audit with deletion controls.
- **missing:** A durable case state machine with deadlines, reply correlation, and escalation rules; A native watcher for new email/browser responses that can wake a sleeping relay without scraping secrets into model context; Scoped approval envelopes that bind the exact outbound text, recipients, attachments, and expiry; Independent verification of receipt/acceptance and a clear owner-facing 'resolved versus waiting versus unknown' state

### "“Show me exactly what will happen before you do it.” For any high-impact Mac or browser action, produce a reversible preview of the external effect—recipient, fields, files, money, permissions, and resulting page diff—then let me approve that exact digest on the pendant; if reality differs, abort instead of adapting silently."
- **useful because:** The owner currently has to trust a plan or inspect a screen unaided. A preflight simulation makes approval meaningful: the physical gesture authorizes one concrete effect, not an evolving agent interpretation.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision → faculty-judgement → faculty-perception → faculty-action
- **model tier:** Cheap deterministic extraction for fields and diffs, with a stronger model only when the action's consequences are ambiguous; realtime speaks the short summary.
- **latency:** Preview in under 5 s for ordinary forms/files and under 15 s for multi-page workflows; no side effect before approval.
- **cost:** $0.01–$0.10 per preview, mostly browser inspection and document diffing.
- **security:** Never execute a 'preview' by submitting or triggering an irreversible endpoint. Redact secrets from the pendant summary. Bind approval to a canonical digest of exact values, recipients, attachments, and scope; any DOM or file change invalidates it.
- **missing:** A dry-run/sandbox contract for Mac and browser action types; Structured consequence extraction and human-readable diff rendering; Approval envelopes that carry the exact preview digest and invalidation conditions; A fail-closed detector for side effects that cannot be simulated

### "“For the next hour, you may handle routine scheduling, but never spend money or send anything external without asking.” Let me create a temporary, plain-language delegation policy from the pendant, have it enforced consistently by the relay, Mac, and browser, and revoke it with one safe gesture."
- **useful because:** The owner can currently approve individual actions, but cannot safely grant a narrow burst of autonomy. This would reduce repetitive interruptions while preserving a hard boundary around money, external communication, and sensitive data.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-judgement → faculty-action → faculty-perception
- **model tier:** Use realtime to clarify and read back the policy; compile it to deterministic predicates and use a cheaper background model only for classifying candidate actions.
- **latency:** Compile and read back the policy in under 3 s; policy checks add under 100 ms per action; revocation propagates within 1 s.
- **cost:** Under $0.02 per policy session, dominated by the initial language-to-policy compilation; enforcement is local and cheap.
- **security:** Default deny on ambiguity or missing policy. Policies are scoped by time, surface, action class, recipient/domain, and spend limit; they cannot authorize irreversible actions or bypass the physical transaction latch. Display a short active-policy status and append every allowed/denied decision to an audit log. Revoke locally if relay connectivity drops.
- **missing:** A typed policy language and compiler with conservative deny semantics; A single enforcement hook used by Mac actions, browser commands, and relay jobs; Pendant commands for read-back, activation, and revocation with monotonic expiry; Conflict resolution when a temporary policy meets an existing approval requirement


## Changes it proposed to its own stack

### `integration` — Add a USB-tethered pendant control session: when the nRF9160 is attached at /dev/cu.usbmodem00096003658* and the ESP32 bridge at /dev/cu.usbserial-0287A9CA, the Mac agent should expose them as a signed local transport for button events, approval-latch decisions, status LEDs, and 24 kHz audio—without pretending the pendant is LTE-registered. The relay should route this transport exactly like a reconnecting remote device, with explicit usb_local provenance on every receipt.
- **owner gets:** The owner can wear and use the real pendant today at their desk, even before cellular registration works. Button approval, spoken responses, and truthful completion status would work over the cable instead of silently falling back to a simulation or failing as if no device existed.
- effort: Medium: a serial framing adapter, device identity handshake, reconnect state machine, and routing/provenance changes; validate against the existing 24 kHz acceptance probe without flashing firmware.  ·  risk: A serial disconnect must fail closed: no approval is inferred and no audio/action is claimed delivered. Guard against talking to the wrong USB serial device using VID/PID plus a challenge-response identity. Recover by returning operations to pending/unknown and requiring a fresh gesture if the link drops mid-approval.
- cost: No API cost; approximately 1–2 engineering weeks. Existing USB cables only; negligible additional power beyond the attached boards.  ·  latency: Button/status round trip should be under 100 ms locally; reconnect detection under 2 s. Audio remains governed by the measured 60 ms framing path.
- security: USB becomes a privileged local control channel, so require authenticated device handshake, monotonic counters, and separate usb_local provenance. Never send form secrets or page contents to firmware.
- depends on: A concrete serial-port/device-diagnostics surface (currently not available); An implementation of the existing physical_transaction_approval_latch over USB; A relay receipt schema that records transport provenance; Owner approval to run the serial adapter; no flashing or firmware mutation


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities and one integration change: independently verified end-to-end action receipts, disconnect-safe resumption of approved operations, verified pendant-triggered undo, and a fail-closed USB-local transport for the physically connected nRF9160/ESP32 pair. The most important is the first: the system must stop saying 'done' until faculty-perception independently verifies the final Mac/browser state. I still need a durable operation/step journal with idempotency and before-state metadata, a canonical verified/failed/unknown result schema, and a concrete serial diagnostics/identity surface before the USB path can be run safely. The owner still needs to choose proactive-versus-staged policy; I will not invent it.

**Biggest unknown:** The live receipt shape: whether browser and Mac execution currently expose stable action_id/attempt_id, before-state, and postcondition evidence fields. Without that, dispatch can be correlated but independent verification and safe resume/undo cannot be made truthful.

