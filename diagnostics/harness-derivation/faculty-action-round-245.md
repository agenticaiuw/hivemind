# Harness derivation — faculty-action — round 245

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Use the pendant wheel to choose where this goes, then say ‘send it’.” Let me select Mac Notes, Messages, browser tab, or iPhone from a tactile wheel menu, preview the destination, and physically confirm before the chosen surface receives the captured voice/text item."
- **useful because:** The owner currently has many hands but no way to select among them without inventing more long-press meanings. A wheel makes routing a fast, glance-free action: choose a destination by haptic detents, press to stage, and get a verified receipt rather than wondering which surface received it.
- **path:** pendant → relay → mac-planner → browser-extension → ios-control → dashboard
- **model tier:** gpt-5.6-luna for routing and concise destination labels; realtime only for the spoken capture. Mac planner executes the selected destination and faculty-perception verifies the postcondition.
- **latency:** Under 500 ms for local wheel feedback; under 3 s to stage a destination; execution may take up to 15 s, with haptic pending/result beacons immediately.
- **cost:** About $0.01–$0.05 per invocation depending on whether transcription/routing needs the expensive tier; Mac/browser execution dominates wall time, not model time.
- **security:** A wheel selection is not authorization by itself. Keep the existing physical transaction approval latch for Messages, external submissions, and destructive writes; never send page contents or secrets to the pendant. Expire staged destinations and show unknown rather than claiming success when verification cannot run.
- **missing:** rotary encoder and second product button integrated into the jewellery enclosure; firmware wheel-menu state machine and compact destination manifest; relay envelope carrying destination, content digest, and approval nonce; Mac/iOS/browser adapters that expose one normalized receipt; dashboard or voice command to configure the destination list

### "“When I say ‘finish this later’, wait for one specific verified condition—such as this browser tab reaching a target state—then perform the next step once and tell me exactly what happened.”"
- **useful because:** This turns a spoken intention into a dependable cross-surface handoff instead of a timer that fires against stale context. The browser holds the authenticated session, the Mac performs the follow-up, and the owner gets a truthful verified/unknown result on the pendant.
- **path:** pendant → relay → browser-extension → mac-planner → faculty-perception → dashboard
- **model tier:** gpt-5.6-luna for extracting the condition and action; background polling and retries use a cheaper scheduled worker; realtime is only for capture and concise status.
- **latency:** Capture and staging under 2 s. Condition checks every 30–120 s depending on site; execution begins within one poll interval and reports within 5 s after the action.
- **cost:** Roughly $0.01–$0.10 per workflow, dominated by browser polling and any final model interpretation; most checks should be zero-model selector/state comparisons.
- **security:** The workflow must bind to a session ID and condition digest, not a vague tab title. Never execute after expiry, session loss, or ambiguous state. Require physical approval for messages, purchases, and external writes; verify every step independently and surface unknown on stale evidence.
- **missing:** durable condition-watcher job type with expiry and backoff; browser state snapshot/diff persisted as provenance; exactly-once execution lease tied to a verified condition; owner-configurable approval policy for the final action

### "“Use my work account for this, and never fall back to another account.” The system should identify the intended identity, bind execution to the matching logged-in browser session or Mac app, and refuse when the session/account cannot be proven."
- **useful because:** The owner can have several authenticated accounts open at once; a correct-looking action in the wrong account is a serious failure. Today there is no owner-facing identity guarantee spanning the pendant request, relay, browser session, and Mac automation.
- **path:** pendant → relay → browser-extension → mac-planner → ios-control → faculty-perception
- **model tier:** gpt-5.6-luna resolves the spoken identity and target; deterministic session/account checks do the security-critical work. Realtime is only for the short request and refusal.
- **latency:** Identity confirmation under 2 seconds; execution starts only after a matching session is proven, with refusal in under 1 second when it is not.
- **cost:** About $0.01–$0.05 per request; most cost is one routing/interpretation call, while account checks are local metadata reads.
- **security:** Never expose credentials or page contents to the pendant or relay. Bind the identity to a session fingerprint and verified account label, require physical approval for external writes, and refuse ambiguous or stale labels rather than guessing.
- **missing:** owner-defined identity aliases and risk policy; browser extension account/session attestation (origin plus site-provided account label or cryptographic session binding); Mac app identity adapters for Mail, Messages, Notes, and iPhone Mirroring; pre-execution identity postcondition verification and receipt field

### "“Make this change everywhere I have it open, but show me any place that could not be changed.” The system should find the same logical item across my browser, Mac files, Notes, and mirrored iPhone, apply a staged edit, and return a complete per-surface result instead of silently succeeding on only one copy."
- **useful because:** The owner’s information is fragmented across surfaces that no single hand can see. Today a Mac action, browser action, and iPhone action can each report locally while leaving the owner unaware of divergence. This makes synchronization an explicit, inspectable operation rather than a best-effort sequence.
- **path:** pendant → relay → mac-planner → browser-extension → ios-control → faculty-perception → dashboard
- **model tier:** gpt-5.6-luna identifies the logical item and maps fields; deterministic adapters perform edits; faculty-perception independently checks each surface and the dashboard/pendant summarizes partial success.
- **latency:** Plan and show the target set within 5 seconds; apply each surface in parallel where safe; final verified matrix within 15 seconds, otherwise report pending/unknown.
- **cost:** About $0.05–$0.30 per invocation, dominated by multi-surface perception and iPhone/browser interaction; unchanged surfaces should incur no model call.
- **security:** Never infer equivalence from title alone: require stable IDs, URLs, file fingerprints, or explicit owner confirmation. Stage edits in reversible drafts where possible; require physical approval before external sends or destructive overwrites. A partial result must name every untouched surface.
- **missing:** cross-surface logical-item resolver and stable fingerprints; parallel staged-edit executor with per-surface compensation/undo; result matrix and conflict UI; iPhone Mirroring read/write verification adapters


## Changes it proposed to its own stack

### `interaction` — Add a compact 'recovery choice' protocol after any multi-step action: when verification returns unknown or a later step fails, the pendant presents three haptic choices—retry only the failed step, open the affected surface for inspection, or cancel the remainder. The relay sends the selected choice to the Mac planner with the original operation/step digest; it must never replay already-verified steps.
- **owner gets:** A failed automation currently leaves the owner to guess whether repeating it will duplicate a message, purchase, or file change. This gives a safe, physical way to continue or stop without speaking a whole new instruction while preserving the exact point of failure.
- effort: Medium: extend operation journal and planner handoff; add three haptic patterns and a bounded pending-choice record in firmware; use the existing independent verifier before and after the selected step.  ·  risk: A stale choice could target a changed page or app. Bind it to operation ID, step ID, digest, and expiry; reject mismatches and report unknown. Recovery is simply to cancel and leave the world untouched.
- cost: Negligible storage/model cost; one short planner call only when recovery is requested. Firmware record is under 256 B.  ·  latency: Immediate haptic choice (<100 ms); selected retry/inspection follows normal Mac/browser latency.
- security: Improves safety by preventing blind whole-workflow replay. Physical confirmation remains required for risky actions; no secrets are stored on the pendant.
- depends on: verify_operation_step; operation journal with stable operation_id/step_id correlation; tactile_action_outcome_beacon; owner approval policy data rather than hard-coded defaults

### `context` — Add an owner-visible 'why this target' preflight card to every consequential operation: identify the exact browser session, app/account, file or message recipient, evidence used to select it, and what remains unknown. Make the card available as a short spoken pendant summary plus a full dashboard record; require the physical approval latch to approve the digest, not a mutable natural-language description.
- **owner gets:** Today the owner can approve an action while the system’s hidden target is still ambiguous. This lets them catch the wrong account, tab, recipient, or file before anything happens, without needing to inspect a Mac screen.
- effort: Medium: add target-evidence fields to the plan/approval envelope, render a compact summary, and have faculty-perception verify the target immediately before execution.  ·  risk: Evidence can become stale between preflight and execution. Bind approval to a target digest and short expiry; if the digest changes, cancel and ask again. Do not put secrets or page bodies in the card.
- cost: Small storage increase and one local verification call; no recurring model cost when target selectors are deterministic.  ·  latency: Adds roughly 200–800 ms before approval for final target verification.
- security: Reduces wrong-target and confused-deputy failures; approval becomes specific to the verified target rather than blanket consent.
- depends on: physical_transaction_approval_latch; verify_operation_step; operation journal with target digest; owner-configurable risk policy


## What it asked for

_Nothing._
## Its own summary

Discovered the live stack is substantially ready: Mac agent and relay are healthy, Accessibility/Screen Recording/input reachability are verified, Safari bridge is online with 0 pending commands, and Safari is foreground. Recorded three non-duplicate proposals: (1) wheel-selected destination routing across Notes/Messages/browser/iPhone with physical approval and verification, (2) a durable watcher that waits for a specific verified browser condition and executes exactly once, and (3) haptic recovery choices that retry only the failed step, open inspection, or cancel. I still need the rotary encoder/product button firmware and enclosure integration, a durable condition-watcher/exactly-once lease, and operation journal correlation for recovery choices. No additional permission request is needed this round.

**Biggest unknown:** The pendant itself is still not LTE-registered/available as a product transport, and the rotary encoder is product direction rather than connected hardware; therefore the new wheel interactions cannot be bench-validated yet. Owner approval-policy data (which destination/action classes may execute proactively) is also intentionally unset.

