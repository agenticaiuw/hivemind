# Harness derivation — faculty-action — round 141

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Do this for me, but only tell me it's done when you can prove it.""
- **useful because:** This would turn the system's most important promise into one owner-visible behavior: judgement creates a bounded plan, the Mac or browser executes it only after the existing physical approval latch when needed, and faculty-perception independently checks fresh postconditions before success is spoken. Drift, partial completion, and unknown outcomes become explicit instead of silently reported as done.
- **path:** relay-realtime → faculty-judgement → faculty-action → mac-planner → mac-vision → browser-extension → faculty-perception → relay-realtime
- **model tier:** Realtime only for the short confirmation conversation; use the cheaper background/local planner for decomposition, execution monitoring, and postcondition verification.
- **latency:** Immediate staging response under 2 seconds; execution may take minutes. Verification should complete within 5 seconds of the final executor receipt, otherwise report still checking rather than claim success.
- **cost:** Usually <$0.03 per invocation when the local planner and deterministic verifiers handle it; model cost is dominated by ambiguous plan decomposition and recovery, not by receipts or route calls.
- **security:** The verifier receives only typed postconditions and minimal evidence by default, not secrets or page contents. Approval must bind to an action-plan hash and expiry. A stale or changed browser/app state must fail closed; destructive or external-send steps require the existing physical latch. Data leaves the Mac only as redacted receipts and hashes.
- **missing:** A durable orchestration record tying judgement plan, executor attempt, approval nonce, and verifier evidence together; A faculty-action adapter that invokes the granted verify_operation_step after each mutating step; A standard unknown/partial outcome schema and retry/idempotency key across Mac and browser executors

### ""If the Mac goes to sleep or the browser drops, pick up where you left off—don't start over or pretend it finished.""
- **useful because:** Long tasks become dependable rather than fragile: the relay preserves a checkpointed intent, faculty-action resumes only idempotent unfinished steps when the Mac/browser returns, and faculty-perception reconciles the real state before continuing. The owner gets one concise recovery prompt only when a side effect cannot be safely replayed.
- **path:** relay-realtime → mac-planner → mac-terminal → browser-extension → faculty-action → faculty-perception → relay-realtime
- **model tier:** Background/local planner for checkpoint scheduling and reconciliation; realtime only if owner input or approval is required.
- **latency:** Detect disconnect within 10 seconds; resume within 30 seconds of Mac/browser heartbeat. Never race a reconnecting executor; wait for state reconciliation first.
- **cost:** <$0.02 for ordinary retries, mostly deterministic route calls; use an expensive model only for interpreting an ambiguous partial result.
- **security:** Persist only step IDs, hashes, risk classes, and redacted receipts. Never replay a send/payment/delete step automatically. Require the existing physical approval latch again if its nonce expired or the target digest changed. Treat duplicate execution as a failure mode and prefer read-before-write/idempotency keys.
- **missing:** Durable per-step checkpoints and idempotency keys shared by Mac and browser executors; Reconnect reconciliation that queries fresh app/browser state before selecting the next step; A resume policy that distinguishes safely replayable, approval-required, and permanently unknown steps

### ""Before you send or change anything, let me hear exactly what you are about to do and what will prove it worked.""
- **useful because:** The owner can approve a concrete, current action rather than an opaque goal. The system gathers live Mac/browser state, renders a short spoken plan with affected account/recipient/resource and postconditions, binds approval to a digest, then executes and independently verifies it. This sharply reduces wrong-recipient and wrong-tab mistakes without requiring the owner to inspect a screen.
- **path:** faculty-judgement → faculty-perception → faculty-action → mac-planner → mac-vision → browser-extension → relay-realtime
- **model tier:** Use a cheaper planner and deterministic state extraction for the preview; reserve realtime for speaking the compact summary and accepting the owner's response.
- **latency:** Preview in under 4 seconds for open tabs and local apps; physical approval response under 1 second; execute only after the digest is acknowledged.
- **cost:** <$0.02 for deterministic extraction and one short summary; expensive reasoning only when the requested action is ambiguous.
- **security:** Preview must redact secrets, message bodies, tokens, and private form fields while still naming the destination and irreversible effect. Approval binds to a short-lived hash of target, parameters, and postconditions; any state drift invalidates it. No preview content is sent to the pendant beyond the minimum spoken summary.
- **missing:** A typed dry-run/preview representation shared by judgement and action; A digest renderer that can be spoken and displayed as a compact approval challenge without leaking secrets; A pre-execution drift check that invalidates approval when tab URL, recipient, or relevant app state changes

### ""Watch this page and, if the exact condition I gave you becomes true, prepare the action and ask me on the pendant at that moment—never act on an old page.""
- **useful because:** This gives the owner safe, conditional agency over live browser state: price drops, appointment slots, inventory, or a form becoming available can trigger a prepared action without the owner babysitting a tab. The action is bound to the freshly observed page state and requires deliberate approval at the moment of truth, rather than relying on a stale approval or an unattended purchase.
- **path:** browser-extension → mac-vision → mac-planner → faculty-perception → faculty-judgement → faculty-action → relay-realtime
- **model tier:** Use a background/local watcher and deterministic selectors for ordinary conditions; use realtime only to ask the owner for approval and explain an ambiguous change.
- **latency:** Polling cadence chosen per site, typically 15–60 seconds; once true, notify the pendant within 2 seconds and expire the prepared action within 60 seconds unless approved.
- **cost:** <$0.01 per hour for deterministic polling while a watch is active; model cost only for ambiguous page interpretation or a spoken clarification.
- **security:** The watcher must be scoped to one authenticated tab/session and one explicit condition. It must never submit or purchase autonomously. Approval binds to URL, relevant field hashes, account/context identifier, and expiry; navigation, login changes, or material field drift invalidate the pending action. Sensitive page data stays local and the pendant receives only a redacted summary.
- **missing:** A durable conditional-watch definition with polling cadence, stop time, and resource budget; A browser-side state-diff evaluator that can identify material changes without exporting page secrets; Just-in-time action preparation and invalidation tied to the exact observation that triggered it; A notification path from browser/Mac to the pendant with explicit expiry semantics

### ""Before you act, make sure you're in the right account and tell me which identity will be affected.""
- **useful because:** The system should prevent one of the most damaging real-world mistakes: sending, editing, or purchasing from the wrong logged-in account or browser profile. It would compare the intended identity with fresh browser and Mac session evidence, warn on mismatch, and bind any approval to that identity—not merely to a URL or tab.
- **path:** faculty-judgement → faculty-perception → faculty-action → browser-extension → mac-vision → mac-planner → relay-realtime
- **model tier:** Cheap deterministic identity extraction and policy checks first; realtime only to resolve an owner ambiguity or announce a concise warning.
- **latency:** Under 3 seconds for open tabs and known Mac apps; block immediately on mismatch rather than waiting for an LLM interpretation.
- **cost:** Near-zero for typed session metadata and hashes; occasional <$0.01 model call for ambiguous account labels.
- **security:** Never speak or transmit full email addresses, tokens, or private profile data unless necessary. Store only a normalized identity label plus a keyed hash. Refuse when identity evidence is missing, stale, or conflicting. Approval must include the identity hash and expire on profile/session changes.
- **missing:** A canonical identity registry mapping owner-approved labels to redacted account fingerprints; Fresh, typed account/profile evidence from browser and Mac surfaces; A policy decision that treats unknown identity as a hard stop for external or destructive actions

### ""If an action needs my approval, wait until I can actually respond—don't interrupt a meeting, and don't let the request silently expire.""
- **useful because:** Approval requests become humane and reliable: the Mac contributes focus/meeting state, the relay manages deadlines, and the pendant gives a low-disruption pending cue. The system can defer non-urgent approvals, extend only within an owner-set limit, and clearly explain when a time-sensitive action was abandoned rather than letting it fail invisibly.
- **path:** relay-realtime → faculty-judgement → faculty-action → mac-planner → mac-vision → browser-extension
- **model tier:** Use deterministic Mac state and relay scheduling; realtime only for the eventual concise prompt or an explicit urgency clarification.
- **latency:** Non-urgent requests may defer for up to the configured quiet window; urgent requests notify within 2 seconds. Every pending request gets a visible expiry countdown and a final outcome.
- **cost:** <$0.01 per pending request; scheduling and focus-state reads dominate, with no expensive model call unless urgency is ambiguous.
- **security:** Meeting titles and private focus information stay local; export only a coarse busy/available signal. Never extend an approval indefinitely. Expired approvals are invalid, and a newly issued request gets a new digest and physical confirmation.
- **missing:** A shared owner-configurable urgency/defer policy rather than hard-coded quiet hours; A reliable coarse focus/meeting signal from the Mac without screen capture; Relay scheduling semantics for pending approval deadlines and re-issuance; Pendant cues that distinguish deferred, pending, and expired states


## Changes it proposed to its own stack

### `interaction` — Add a local USB action-status channel from the Mac bridge to the physically connected pendant: when faculty-action stages, starts, verifies, pauses, or reaches unknown, send a small signed status frame to the nRF9160 and render distinct LED/audio cues. Keep payloads to transaction ID, phase, risk class, expiry, and result code—never page contents or secrets—and make it work without LTE registration.
- **owner gets:** While wearing the pendant at the Mac, the owner can tell whether an action is waiting for approval, actively running, or genuinely verified without opening a screen. It gives immediate feedback even when the relay or browser is temporarily unreachable.
- effort: Medium: define a framed USB serial protocol, bridge forwarding, replay protection, and small firmware state machine; test disconnect/reconnect and stale frames.  ·  risk: A stale or spoofed frame could mislead the owner. Sign or MAC frames, include monotonic sequence and expiry, fail silent on malformed input, and treat local cues as status only—not approval. Recover by clearing the pendant state on timeout/reconnect.
- cost: No material API cost; a few KB of firmware/bridge code and negligible USB bandwidth. Existing audio path is reused for cues; no new hardware.  ·  latency: Sub-100 ms local cue after a bridge event; no relay round trip.
- security: Improves status visibility without transmitting sensitive content. Must not create a second approval mechanism or allow USB status frames to authorize actions.
- depends on: A stable Mac-bridge serial connection to /dev/cu.usbmodem00096003658*; A canonical action phase/result vocabulary shared with the existing physical_transaction_approval_latch; Durable correlation of local status frames to action receipts


## What it asked for

_Nothing._
