# Harness derivation — faculty-action — round 160

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“When I approve something on the pendant, carry it out on my Mac or in my signed-in browser, then tell me plainly whether it definitely happened, is still running, or is unknown—and recover or stop safely if the connection drops.”"
- **useful because:** This would make the system a trustworthy hand rather than a fire-and-forget command channel: the owner gets one physical approval, execution across the Mac/browser, independent fresh verification, and honest recovery semantics even during a USB/LTE/link failure.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-judgement → faculty-perception → faculty-action
- **model tier:** Realtime only for the brief approval conversation; use background/local Mac planning and perception for execution, polling, and verification.
- **latency:** Pending cue under 500 ms; approval acknowledgement under 1 s; ordinary actions begin within 2 s; verification polls until a bounded deadline and then reports unknown rather than guessing.
- **cost:** Low-to-moderate per invocation: one realtime turn only when clarification is needed; most cost is local Mac/browser polling and occasional perception evidence, not model generation.
- **security:** The pendant receives only an opaque action summary/digest, never secrets or page contents. Require the existing physical approval latch, bind approval to action digest and expiry, independently verify postconditions, and require confirmation before retries or irreversible recovery. Data leaving the device is limited to approval nonce and status.
- **missing:** A live typed USB-serial control/heartbeat surface for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A durable executor state machine that correlates action, attempt, approval, and verification receipts; The granted verifier needs actionId/attemptId correlation added; LTE registration and device enrollment for use away from the Mac

### "“Use the pendant as a local safety remote while it is plugged into my Mac: show me that a risky Mac/browser action is waiting, let me approve or cancel with the safe gesture, and keep the decision queued until the Mac confirms it consumed it.”"
- **useful because:** The hardware is physically present today even though it is not relay-registered. This gives the owner a useful, testable security boundary now: a deliberate action on the worn device can authorize a browser or Mac operation without putting credentials or page contents on the pendant.
- **path:** pendant → mac-planner → browser-extension → mac-terminal → relay-realtime → faculty-action
- **model tier:** Use the local Mac agent for serial framing and action dispatch; use the realtime model only to explain the pending action or resolve ambiguity.
- **latency:** LED/audio pending cue within 300 ms of staging; approval-to-dispatch under 1 s over USB; queued decisions survive temporary bridge restarts and expire deterministically.
- **cost:** Near-zero model cost for clear requests; USB serial and local state-machine work dominate. Audio cue uses the already verified 24 kHz path.
- **security:** Only a digest, risk class, short human-readable summary, expiry, and nonce cross the serial link. Reject expired, consumed, or digest-mismatched envelopes. A short press must never approve; approval is the deliberate safe gesture on sw1. Never execute locally on the pendant.
- **missing:** Typed serial identity/heartbeat/counter diagnostics and an approval-envelope serial protocol; A Mac-side bridge daemon that binds serial device identity to the authenticated owner session; Owner-configured policy deciding which risk classes may be approved locally versus staged

### "“Start this multi-step job, and if my Mac, browser, or relay restarts, resume from the last step you independently proved—not from the beginning—and ask me only about the step that actually needs me.”"
- **useful because:** Today a complex task can be handed off, but a crash or lost browser session can leave the owner unsure whether to restart, risking duplicate sends, purchases, or edits. A resumable, verified workflow would make long jobs dependable across the real boundaries of this hive.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → faculty-action → faculty-perception → pendant
- **model tier:** Background/local planning for the workflow graph and retries; realtime only for a clarification or physical approval that is genuinely needed.
- **latency:** Checkpoint each completed step within 2 s; resume detection within 10 s of a reconnect; never auto-retry an irreversible step without an idempotency key or renewed approval.
- **cost:** Low-to-moderate: local persistence and state checks dominate; model calls only for ambiguous recovery or changed UI.
- **security:** Persist only action summaries, digests, locators, and result hashes; keep secrets in the browser session/Mac keychain. A resumed step must revalidate preconditions and expiry, and the owner must be told when evidence is stale or unavailable.
- **missing:** A durable workflow graph with per-step idempotency keys and verified checkpoints; A reconnect/reconciliation protocol shared by relay, Mac agent, and browser bridge; Verifier correlation fields tying evidence to workflow and attempt IDs

### "“Watch for this exact condition in my signed-in browser or Mac app, and only then perform the approved next step; if it never becomes true, tell me when the watch expired instead of acting on a guess.”"
- **useful because:** This turns the system into a useful personal operator for delayed, real-world tasks—waiting for a package status, a reply, a build, or a page state—without making the owner repeat the request or leaving an unbounded dangerous automation running.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-judgement → faculty-action → faculty-perception
- **model tier:** Use cheap scheduled/local polling and deterministic selectors for the watch; use realtime only when the condition is ambiguous or the owner changes the instruction.
- **latency:** Condition checks on a configurable cadence (5–60 s); trigger action within 2 s of a positive observation; hard expiry and quiet-hours enforcement are mandatory.
- **cost:** Low when selectors and hashes suffice; occasional perception/model calls only for changed layouts or ambiguous states.
- **security:** The watch envelope must include exact scope, expiry, allowed action, and risk class. Freshly verify the condition immediately before acting; never treat a notification or stale cached page as proof. Require physical approval for the resulting risky action.
- **missing:** A durable conditional-watch state machine with leases, expiry, and cancellation; Typed condition probes across browser fields, URLs, app state, and files; A scheduler that remains awake in relay but delegates observation to the Mac when available


## Changes it proposed to its own stack

### `integration` — Add an execution watchdog and reconciliation loop spanning relay, Mac/browser, and pendant: every dispatched action gets a monotonic attempt record, deadline, last-seen executor heartbeat, and explicit terminal state (verified, failed, cancelled, or unknown). On timeout it stops issuing retries, asks faculty-perception for a fresh postcondition check, and presents the owner a recovery choice on the pendant/Mac rather than silently duplicating an irreversible action.
- **owner gets:** If Wi‑Fi, USB, browser sessions, or the Mac agent disappear halfway through an action, the owner will know whether it happened and can recover without duplicate purchases, messages, or edits.
- effort: Medium-high: durable state and idempotency keys in relay/local agent, watchdog scheduling, and adapters for browser and Mac receipts; can be piloted with reminders/files before irreversible actions.  ·  risk: A false timeout could report unknown while the action later completes; idempotency keys and a postcondition read reduce duplicate retries. If the watchdog itself is down, the existing action receipt remains available and no automatic retry occurs.
- cost: Small storage and background polling cost; negligible model spend when executor receipts are complete, with extra perception cost only after a timeout.  ·  latency: Adds no delay to dispatch; normal completion is unchanged, while timeout resolution may take 1–5 seconds for a fresh verification.
- security: Improves safety by making unknown a first-class result and preventing blind retries; logs action summaries/digests, not secrets or page contents.
- depends on: A durable action/attempt ledger shared by Mac and relay; A live read-only verification route with actionId/attemptId correlation; Typed serial heartbeat if pendant status is part of the escalation path

### `context` — Create a privacy-preserving action handoff record that lets faculty-judgement specify a task once and faculty-action retrieve only the minimum execution context at each step: current app/session, locator or file target, preconditions, expiry, and sensitivity. On reconnect, the Mac/browser rehydrates that narrow context rather than replaying the entire conversation or exposing secrets to the relay/pendant.
- **owner gets:** Long or interrupted tasks would stop forgetting what they were doing, while the owner’s private browser sessions and credentials remain on the Mac instead of being repeatedly copied into cloud context.
- effort: Medium: define a versioned context envelope, local encrypted store, and redaction-aware retrieval; migrate existing job and browser session records incrementally.  ·  risk: An incorrect locator or stale context could target the wrong item; bind every envelope to a session and fresh precondition check, and fail closed on version mismatch.
- cost: Reduces repeated prompt/context tokens and cloud data transfer; small local storage overhead.  ·  latency: Adds one local context lookup per step (milliseconds); avoids expensive re-planning after reconnect.
- security: Strongly reduces secret leakage and context over-sharing; encrypted at rest and scoped by sensitivity, with relay seeing digests and summaries only.
- depends on: A durable workflow/checkpoint record; Mac-local encrypted storage and session binding; Read-only fresh state verification before each action


## What it asked for

_Nothing._
## Its own summary

Recorded three actionable proposals. The highest-value one is a cross-surface “do it and prove it” transaction: staged physical approval on the pendant, Mac/browser execution, independent fresh postcondition verification, and explicit verified/failed/cancelled/unknown outcomes. I also recorded a USB-local pendant approval path that is testable on today’s physically connected chips, and an execution watchdog/reconciliation loop that prevents blind retries after link loss. Still needed: a typed serial identity/heartbeat/envelope protocol and Mac bridge for the two live USB devices; durable action/attempt/idempotency state; verifier correlation by actionId/attemptId; and owner policy data for which risk classes can be approved locally. LTE enrollment remains needed only for away-from-Mac operation. I asked mac-terminal and faculty-perception for their exact field requirements.

**Biggest unknown:** Whether either connected USB device currently exposes a stable application protocol or only a bootloader/console; no agent yet has a typed, read-only serial probe that can establish identity, counters, and heartbeat without modifying or flashing hardware.

