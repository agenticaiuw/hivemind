# Harness derivation — faculty-action — round 143

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Keep working on this until the requested result is actually true—if a Mac or browser step fails, inspect the fresh state, repair it, and tell me exactly what remains."
- **useful because:** Today execution can stop after a receipt even when the postcondition is false. This makes the action agent close the loop: perception verifies each step, judgement chooses a bounded repair, and action retries only the failed portion, rather than leaving the owner to diagnose a half-completed task.
- **path:** faculty-judgement → faculty-perception → faculty-action → mac-planner → mac-vision → browser-extension → relay-realtime
- **model tier:** Use the expensive realtime tier only for the owner's live decision or an ambiguity; use a cheaper background model for repair planning and keep deterministic action/verification local.
- **latency:** First action within 2 seconds; each repair cycle under 10 seconds, with a hard limit of 3 cycles before asking the owner.
- **cost:** Usually 1–3 cheap planner calls plus local Mac/browser operations; roughly $0.01–$0.08, dominated by vision or long repair reasoning.
- **security:** A failed action must not silently broaden scope. Every repair is constrained to the original goal, sensitive fields are redacted, and irreversible or newly discovered targets require the existing physical approval policy. Export only hashes/minimal snippets as proof unless the owner asks for detail.
- **missing:** A durable repair-loop orchestrator that can call perception after each executor receipt; A typed failure taxonomy and bounded repair plans; A correlation field linking action attempt, verification receipt, and repair attempt

### "Change this across all the places it matters—for example, update my contact detail in Contacts and the signed-in web account—show me one combined diff, then apply it and confirm every copy matches."
- **useful because:** The owner currently has to know which surface contains a setting and repeat the request. A coordinated Mac-plus-browser action can discover the relevant copies, present one reviewable change set, commit only after approval, and independently verify each target, preventing silent divergence.
- **path:** faculty-judgement → faculty-perception → faculty-action → mac-planner → browser-extension → relay-realtime
- **model tier:** Cheap background planning for target discovery and diff generation; realtime only when the owner is interacting or a target is ambiguous. Deterministic executors perform field edits.
- **latency:** Discovery and a readable diff in 5 seconds; commit in 10–30 seconds depending on browser targets; verification before reporting success.
- **cost:** About $0.02–$0.10 per invocation, mostly target discovery and browser vision; Mac AppleScript and field verification are negligible.
- **security:** Never copy secrets between surfaces by default. Display values masked where sensitive, require the existing physical approval latch for account/security changes, retain per-target before/after hashes, and stop rather than partially commit if a target's identity is uncertain.
- **missing:** Cross-surface target discovery adapters; A single diff/approval envelope spanning Mac and browser sessions; Compensating undo or explicit partial-commit recovery for targets that reject the update

### "Only let this job keep running while my pendant is physically present; if the USB link disappears, pause safely, tell me what was completed, and resume only when the device is back."
- **useful because:** The pendant is physically connected to the Mac today even though it is not LTE-registered. Presence can become a real safety boundary: unplugging it is an immediate, understandable way to pause a long or consequential Mac/browser workflow, with no microphone or network assumption.
- **path:** pendant → mac-terminal → mac-planner → faculty-action → faculty-perception → relay-realtime
- **model tier:** Deterministic serial heartbeat and job lease on the Mac/relay; use a cheap model only to summarize the paused state. No realtime model is needed for detection.
- **latency:** Detect link loss within 500 ms and pause before the next action; reconnect and state reconciliation within 3 seconds.
- **cost:** Near-zero model cost; a small local daemon and serial I/O consume negligible CPU, with no cloud traffic required for presence detection.
- **security:** Fail closed on serial ambiguity, stale heartbeat, or device reset. The pendant receives only opaque job state, never page contents or secrets. Resume requires reconciliation against fresh Mac/browser state, not blind replay; irreversible actions remain subject to owner approval.
- **missing:** A Mac serial-presence daemon for /dev/cu.usbmodem00096003658* and a stable framing protocol; A lease/pause state in the durable job runner; A resume reconciler that invokes fresh verification before continuing; A relay route to surface tether state and paused-job notices

### "When the right condition becomes true, do this for me—for example, send the prepared message only when I'm no longer in a meeting and the recipient's page is open; otherwise keep it staged and tell me why it has not fired."
- **useful because:** The owner can schedule by clock and can execute now, but cannot delegate a conditional action whose safety depends on live Mac, calendar, browser, and pendant state. This turns intent into a guarded handoff instead of a premature send or a forgotten draft.
- **path:** faculty-judgement → faculty-perception → faculty-action → mac-planner → browser-extension → relay-realtime → pendant
- **model tier:** Use a cheap background evaluator for deterministic predicates and event routing; invoke the realtime model only when a condition is ambiguous or the owner needs a live explanation.
- **latency:** Evaluate event-driven predicates within 1 second of a state change; never poll more often than once per 10 seconds; expire or request clarification at the user-specified deadline.
- **cost:** Usually near-zero model cost with local event/state checks; approximately $0.005–$0.03 when natural-language conditions need interpretation.
- **security:** Conditions must compile to an explicit, owner-visible predicate before arming. Sensitive calendar/page contents stay local; no action runs after expiry, identity change, browser-session loss, or a stale observation. Irreversible actions still require the existing deliberate physical approval, at firing time—not when the condition is armed.
- **missing:** A typed conditional-intent representation with predicates, deadline, and stale-state policy; Event subscriptions joining calendar/app/browser/pendant state rather than timer-only routines; A durable armed-but-not-executed state with explanations and cancellation; A final fresh verification gate immediately before side effect


## What it asked for

_Nothing._
## Its own summary

Discovered that Safari/browser bridge is live (9 tabs), Mac full-control planner and browser extension report online, while the relay device table still does not list the physically tethered pendant. Recorded three new capabilities: (1) bounded self-healing execution that verifies, repairs, and re-verifies instead of trusting receipts; (2) one reviewed diff and commit across Mac and signed-in browser copies; (3) USB-pendant presence as a fail-closed lease that pauses jobs on link loss and reconciles before resume. I still need a reliable serial-presence/framing implementation, durable job lease/pause state, and a fresh inventory confirming these do not already exist; I also need the owner to decide which synchronized data classes are allowed to cross surfaces.

**Biggest unknown:** The live inventory is internally inconsistent: the Mac/browser bridge is online, but the device registry says only Mac bridge and an offline mobile device. Until serial presence is exposed as a first-class observation, I cannot honestly claim the pendant is the active safety boundary.

