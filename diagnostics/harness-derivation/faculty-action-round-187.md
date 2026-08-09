# Harness derivation — faculty-action — round 187

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **device reachability** — Live device inventory still exposes only Safari, the Mac bridge, and an offline mobile device; it does not expose the nRF9160 pendant or ESP32 bridge, despite the current bench statement that both are USB-connected. Any relay/LTE assumption remains false; a local serial surface is still needed for execution and verification.
  - evidence: discover(devices) returned Safari on MacIntel, home-macbook-bridge online, and cloudflare-contract-test mobile offline; no pendant or ESP32 entry.

## Capabilities it proposed

### "“Only let a queued high-impact Mac action proceed while I am demonstrably holding the pendant; if I put it down or walk away before the deadline, cancel it and tell me why.”"
- **useful because:** This turns physical possession into a continuous safety boundary rather than a one-time approval click. A stolen/unattended pendant, accidental button press, or dropped Bluetooth/USB connection cannot leave a staged email, purchase, or deletion authorized after the owner has left.
- **path:** pendant → relay-realtime → mac-planner → faculty-judgement → faculty-action → faculty-perception
- **model tier:** background for policy and risk classification; realtime only for the brief pending spoken/haptic interaction
- **latency:** motion/connection state sampled locally within 250 ms; cancellation propagated within 2 seconds; no model call needed for the fast path
- **cost:** Negligible inference cost after implementation; local IMU and link-state sampling dominate, with occasional background policy evaluation <$0.01 per staged action.
- **security:** IMU data must remain coarse presence evidence, not a location or behavior history. The relay should receive signed presence epochs and a monotonic counter, never raw motion traces. Fail closed on stale epochs, clock ambiguity, replay, or link loss; this supplements rather than replaces the existing physical_transaction_approval_latch.
- **missing:** Firmware integration for the owned LSM6DSOX on enabled i2c2, including a signed presence epoch and tamper/stale timeout.; Relay policy field distinguishing continuous possession-required actions from ordinary staged approvals.; A Mac executor hook that pauses or invokes the existing undo path when the possession lease expires, followed by independent postcondition verification.

### "“Show me, on the pendant, exactly what this action would change across my Mac and browser, let me rehearse it without committing anything, and only then offer approval.”"
- **useful because:** The owner can safely ask for consequential work without trusting an opaque plan. The Mac/browser perform a dry-run or produce a before/after diff, faculty-perception independently checks the preview, and the pendant presents a short digest before the existing physical approval latch can authorize the real commit.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-action
- **model tier:** background for dry-run planning and diff compression; realtime only to narrate the compact preview
- **latency:** preview in 5–15 seconds for one app/site; up to 45 seconds for a multi-surface workflow; approval response remains immediate
- **cost:** Roughly $0.03–$0.15 per preview depending on screenshots and number of surfaces; deterministic state collection should dominate, not the realtime model.
- **security:** Never send page secrets, form values, or full screenshots to the pendant or relay. Redact sensitive fields before hashing/diffing. A preview digest must be bound to the exact operation nonce and expire if any observed state changes. Dry-run must be genuinely non-mutating, and commit still requires the physical latch plus independent verification.
- **missing:** A dry-run contract for Mac and browser actions that returns typed intended mutations and redacted before/after evidence.; A digest renderer constrained to the pendant's single LED/audio channel, with a way to request more detail on the Mac.; A commit guard refusing to execute if the preview hash, browser URL, app state, or operation nonce changed.

### "“Run this multi-step task, but stop the moment the world differs from the plan; explain the divergence on the pendant and let me choose whether to resume, revise, or undo.”"
- **useful because:** Long workflows fail silently today when a browser session expires, a file changes, or an app takes a different branch. A transaction-level watchdog makes automation truthful and recoverable: each step is independently checked, unexpected state pauses the job, and the owner gets a concrete decision instead of a misleading success.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → faculty-action → faculty-perception → pendant
- **model tier:** background for plan decomposition and divergence explanation; realtime only for the owner-facing alert and decision
- **latency:** verification after every step within 2 seconds; owner response can remain pending for hours without holding a Mac process open
- **cost:** About $0.01–$0.08 per workflow for typed checks; screenshot-based checks can raise this to $0.20. Cost scales with steps, so prefer hashes and app/browser state over images.
- **security:** Never auto-resume after a mismatch. Persist only redacted state hashes and locator provenance. If the Mac disappears, mark the operation unknown rather than failed or completed. Undo must be a separately verified operation and must not expose secrets to the relay or pendant.
- **missing:** A first-class operation state machine with per-step checkpoints, pause/resume/revise/undo transitions, and durable deadlines.; Executor support for cooperative pause and cancellation across Mac and browser jobs.; An amendment to verify_operation_step carrying operation_id/step_id plus observed provenance and a structured divergence reason, then a relay event that can reach the pendant.

### "“Put me in a private work session: let the Mac and my logged-in browser use sensitive data locally, but do not send page contents, credentials, screenshots, or transcripts to the relay or pendant; tell me when a step would cross that boundary.”"
- **useful because:** Today the owner must choose between useful automation and exposing sensitive material to the cloud path. A private session would let the browser and Mac act on local secrets while the relay receives only opaque operation IDs, policy decisions, and redacted outcomes. The owner gets an explicit boundary instead of relying on undocumented behavior.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-judgement → faculty-action → faculty-perception
- **model tier:** background for local policy compilation and redaction; realtime only for short boundary alerts
- **latency:** Policy check under 100 ms locally; boundary warnings within 1 second; no cloud model call for ordinary steps
- **cost:** Less than $0.01 per session after implementation; local hashing/redaction dominates. Exceptional policy questions can use a slower model.
- **security:** The relay must fail closed when it cannot classify a field. Secrets must never be placed in job receipts, prompts, pendant audio, or screenshots. Private-session state needs an owner-visible expiry and explicit exit gesture. Local logs should contain only typed field classes and hashes.
- **missing:** A capability-level data-flow policy enforced before Mac/browser executor calls, rather than a prompt convention.; Browser and Mac adapters that return typed sensitivity labels and redacted result envelopes.; A pendant-visible private-mode state and fail-closed relay routing for all session events.

### "“Give me a daily autonomy budget: you may perform low-risk maintenance automatically, but stop when the budget, time window, data-sharing limit, or number of external messages would be exceeded, and ask me on the pendant before continuing.”"
- **useful because:** The owner cannot safely delegate recurring work today without either approving every trivial step or granting an unbounded assistant. A budgeted contract makes autonomy measurable: spend, duration, external side effects, and sensitivity are accumulated across Mac, browser, relay, and pendant, with a physical escalation when the contract is exhausted.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-judgement → faculty-action → faculty-perception
- **model tier:** background for planning and accounting; realtime only when a budget threshold needs an immediate owner decision
- **latency:** Budget checks under 200 ms per step; scheduled maintenance may run asynchronously; escalation should reach the pendant within 2 seconds
- **cost:** Usually <$0.02 per maintenance run; accounting is deterministic. Model cost is only for ambiguous risk classification or contract explanation.
- **security:** Budgets must be monotonic and durable across crashes and link loss, with separate limits for local edits, external messages, purchases, and sensitive data. Never silently borrow from another category. Reset requires an explicit owner gesture and a visible period/zone; unknown receipts reserve budget rather than releasing it.
- **missing:** A durable owner-authored autonomy-contract schema and runtime accounting ledger spanning relay jobs, Mac actions, and browser commands.; Risk/cost estimators that emit typed units before execution, not estimates after the fact.; A pendant interaction for approve-once, pause, and budget reset that cannot be confused with ordinary recording.

### "“Before accepting sensitive commands, prove that the pendant, audio bridge, Mac agent, and browser bridge are the expected software versions and have not been replaced; show me a simple trusted/untrusted result and quarantine the untrusted link.”"
- **useful because:** Today the owner has no end-to-end answer to whether the device asking for confirmation is genuine or whether a stale bridge can receive sensitive work. Attestation would make the pendant a real security boundary rather than merely a button attached to an unverified transport.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-action
- **model tier:** background and deterministic cryptographic verification; no realtime model needed except to explain a failure
- **latency:** Under 3 seconds at session start and after firmware/bridge changes; cached measurements may be reused until a component changes
- **cost:** Negligible model cost; hardware-backed key provisioning and verification infrastructure dominate engineering cost.
- **security:** Private keys must never be exportable or stored only in ordinary flash. Attestation reports should contain measurements, versions, nonce, and capability claims—not page contents, audio, or owner data. Fail closed on unknown firmware, rollback, nonce reuse, or missing bridge. Recovery must require a physical re-enrollment ceremony.
- **missing:** A secure element or hardware-backed key path on the pendant and ESP32 bridge; current bench hardware has none.; Signed firmware manifests and measured-boot/attestation code for both chips and the Mac/browser agents.; Relay enrollment, revocation, and quarantine semantics with owner-visible recovery.


## What it asked for

_Nothing._
