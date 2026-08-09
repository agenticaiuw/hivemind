# Harness derivation — faculty-action — round 236

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Do the whole thing, but don't tell me it worked unless every step is independently verified.""
- **useful because:** Turns fragile multi-step Mac/browser actions into truthful transactions: each step is executed, checked against fresh state, and either committed with provenance or surfaced as unknown with safe recovery. The owner gets fewer silent failures and no invented success.
- **path:** unified → faculty-judgement → faculty-action → faculty-perception → mac-planner → mac-vision → browser-extension → relay-realtime → pendant
- **model tier:** Background model plans the saga; realtime model only handles the owner's live clarification; deterministic action and verifier code handle execution/evidence.
- **latency:** 5–15 seconds for a short 3-step transaction; each verification adds roughly 0.5–2 seconds. Long workflows become resumable jobs rather than holding the voice turn open.
- **cost:** Low-to-moderate: one planning call plus cheap verifier calls per step; dominant cost is model planning, not receipts or hashes.
- **security:** Never send page secrets or full private content to the pendant. Require the existing physical transaction approval latch for irreversible steps. Store only locator-scoped, sensitivity-labelled evidence and hashes; if a verifier cannot establish the postcondition, report unknown and stop rather than retrying blindly.
- **missing:** An operation/saga coordinator that assigns operation_id and step_id, persists dependencies and compensation actions, and exposes a resumable state machine.; Action receipts need an attempt_id correlation field so verify_operation_step can bind evidence to the exact execution.; A deterministic compensation policy for reversible Mac jobs and browser mutations.

### ""Undo the last thing you did for me.""
- **useful because:** Makes recovery a first-class wearable action instead of requiring the owner to remember which app or job changed. The system resolves the latest reversible ledger entry, previews the exact reversal, gets deliberate physical confirmation when needed, executes it on the Mac/browser, and verifies the prior state was restored.
- **path:** pendant → relay-realtime → faculty-judgement → faculty-action → faculty-perception → mac-planner → browser-extension → mac-vision → unified
- **model tier:** Cheap background model selects and explains the latest reversible receipt; deterministic ledger/undo handlers execute; realtime is only for a concise confirmation exchange.
- **latency:** Under 3 seconds to present the candidate; 3–10 seconds to undo and verify, depending on the app or browser.
- **cost:** Low: mostly indexed receipt lookup and deterministic undo, with a small model call only when the human-readable summary is ambiguous.
- **security:** Never infer reversibility from prose. Use actionRisk and explicit receipt metadata; irreversible or externally visible changes remain staged. Require the existing physical latch for anything beyond a local reversible change. If the target has aged out or state diverged, show unknown and do not perform a compensating guess.
- **missing:** A user-facing latest-action index spanning Mac jobs and browser commands, with explicit reversible_until and compensation metadata.; A pendant input path for selecting among multiple recent actions (rotary encoder plus the owner's planned second button), since two DK buttons are already occupied.; A verified undo receipt that links the original operation and restored-state evidence.

### ""Prepare this message/order/form, show me exactly what will be sent, and only send it when I deliberately approve it on the pendant.""
- **useful because:** Combines browser-held sessions, Mac execution, and the wearable's physical boundary into a practical safe-send flow. The owner can delegate tedious filling while keeping the final high-risk act physically under their control, with proof that the submitted fields match the approved draft.
- **path:** browser-extension → mac-vision → mac-planner → faculty-action → faculty-perception → faculty-judgement → relay-realtime → pendant → unified
- **model tier:** Background model extracts a redacted draft and risk summary; deterministic browser actions fill fields; realtime speaks only the short summary; verification is read-only and independent.
- **latency:** Draft in 3–8 seconds; approval prompt immediately; send plus verification in 2–6 seconds after the physical gesture.
- **cost:** Moderate for complex forms because field mapping and redaction may require vision/model calls; simple forms are mostly deterministic browser commands.
- **security:** The pendant receives only a digest, risk class, destination and human-readable redacted summary—not credentials, full card numbers, or private page contents. Bind approval to a digest of exact field values and destination, expire it quickly, and refuse if any field changes. Verification must check the resulting URL/app state without opening a microphone or mutating anything.
- **missing:** A canonical draft digest over normalized browser fields and destination, shared by browser execution, approval latch, and verifier.; A browser-side snapshot/diff that can prove the submitted values matched the approved digest without exfiltrating secrets.; A standard post-submit receipt linking command_id, approval nonce, and verify_operation_step provenance.

### ""Try this risky workflow in a disposable copy first, show me the exact diff and side effects, then apply the same plan to the real thing only if I approve on the pendant.""
- **useful because:** Lets the owner safely test unfamiliar automations—file reorganizations, browser settings, or multi-step edits—without gambling the real account or workspace. The system can expose what would change before a real commit, including side effects a normal dry-run misses.
- **path:** faculty-judgement → faculty-action → faculty-perception → mac-planner → mac-terminal → mac-vision → browser-extension → relay-realtime → pendant → unified
- **model tier:** A background model creates the plan and summarizes the diff; deterministic sandbox/clone execution and state comparison do the safety-critical work; realtime only explains the result.
- **latency:** 10–60 seconds for a small workflow; larger jobs run asynchronously and return a wearable completion summary.
- **cost:** Moderate engineering and storage cost; per-use model cost is low-to-moderate, dominated by summarizing the observed diff rather than execution.
- **security:** The disposable environment must not inherit production cookies, payment credentials, SSH keys, or secret environment variables. Browser tests need an isolated profile with network egress blocked or allowlisted. Approval must bind to a hash of the tested plan and diff; if the real state differs, refuse to apply.
- **missing:** A Mac sandbox/clone executor for allowlisted filesystem and browser operations with secret stripping and network isolation.; A normalized cross-surface diff format that includes created/changed/deleted files, browser mutations, and external requests.; A plan-replay validator proving the approved plan is equivalent to the real execution plan, not merely similar prose.

### ""Keep working on this until it is actually done, but stop and ask me only when the next step would cross a boundary I did not authorize.""
- **useful because:** Gives the owner durable, bounded autonomy instead of a brittle one-turn command: the relay can keep a job alive across link drops and Mac/browser delays, while the action agent pauses at newly discovered risk boundaries and resumes from verified checkpoints rather than repeating work.
- **path:** unified → faculty-judgement → faculty-action → faculty-perception → relay-realtime → mac-planner → mac-terminal → mac-vision → browser-extension → pendant
- **model tier:** Cheap background orchestration manages the state machine; a stronger model is invoked only when the workflow encounters ambiguity or a new risk class; realtime is not used for waiting.
- **latency:** Immediate acknowledgement, then minutes or hours asynchronously; resume within one scheduling tick after a dependency returns.
- **cost:** Low-to-moderate: durable job state and receipts dominate; model calls occur only at boundary decisions.
- **security:** Authorization must be a scoped capability token with expiry, target set, maximum risk, and allowed external side effects—not a blanket 'keep going.' Every pause includes the reason and pending action; the pendant can revoke the token. Never resume after state drift without fresh perception.
- **missing:** A durable workflow runtime with checkpointed dependencies, leases, expiry, and resumable step graph.; A policy evaluator that can classify a newly encountered action and distinguish already-authorized steps from boundary crossings.; A pendant revocation message that the relay can enforce before the next action, including while the Mac is offline.

### ""Tell me what changed in the world because of your actions, not just whether your command ran.""
- **useful because:** Separates executor success from real-world consequence. After sending, editing, scheduling, or changing a browser-backed service, the system reports externally observable effects, affected objects, and anything it could not verify—so the owner does not confuse a successful click with a successful outcome.
- **path:** faculty-action → faculty-perception → faculty-judgement → mac-planner → mac-vision → browser-extension → relay-realtime → pendant → unified
- **model tier:** Deterministic postcondition probes gather state; a background model turns provenance into a concise causal narrative; realtime only delivers the summary.
- **latency:** 2–10 seconds after an action for local/browser effects; external services may remain pending and be rechecked asynchronously.
- **cost:** Low-to-moderate: most work is read-only probes and hashes; model cost is a short explanation over structured evidence.
- **security:** Evidence collection must be locator-scoped and sensitivity-aware, never dumping page contents or message bodies to the pendant. Clearly label observed, inferred, and unknown effects. Do not poll external systems indefinitely or claim delivery from a local UI transition.
- **missing:** A causal effect schema linking action receipts to affected entities and postcondition probes across app, file, browser, and external-service states.; Read-only adapters for common external confirmation signals (sent-item state, calendar event identity, upload/job status) with freshness limits.; A provenance renderer that preserves evidence hashes and exposes uncertainty in both relay text and compact haptic output.


## Changes it proposed to its own stack

### `integration` — Add a target-binding preflight and TOCTOU guard to every cross-surface action: capture GET /observe and GET /browser/status immediately before execution, bind the intended foreground app/browser session/tab and freshness window into the operation, re-check the binding immediately before each irreversible step, and stop with an unknown result if focus, session identity, secure-input state, or tab URL changes unexpectedly.
- **owner gets:** Prevents the most dangerous class of mistakes: a command intended for one tab or app landing in another after the owner switches focus, a browser session goes stale, or a login/security state changes. The pendant can say exactly why the action paused instead of silently acting on the wrong screen.
- effort: Medium: policy middleware plus operation metadata and verifier integration; no new model required.  ·  risk: Legitimate focus changes during a long workflow may pause it. Recover by re-observing and asking for renewed approval rather than guessing; reversible steps can be resumed from their last verified checkpoint.
- cost: Negligible API cost; two small read-only state calls per guarded step.  ·  latency: Adds roughly 100–500 ms per preflight on a local Mac, plus a verifier call only when state changed.
- security: Improves target isolation and prevents confused-deputy actions. Do not include URLs, titles, or secure-input details in pendant payloads beyond a redacted target label and digest.
- depends on: operation coordinator with step IDs; canonical browser session/tab binding; receipt attempt_id correlation; owner-confirmed policy for what state changes are safe to re-approve

### `interaction` — Add a compact wearable recovery protocol for an operation that stops unknown: one short acknowledgement presents the failure class and next safe option; the planned rotary encoder selects retry, inspect, undo, or dismiss; the second button confirms only the selected safe/reversible branch, while irreversible continuation still uses the existing physical transaction approval latch.
- **owner gets:** When an action fails away from the Mac, the owner can recover without opening a laptop or accidentally repeating a half-completed send. It turns an opaque error into four deliberate choices in the owner's hand.
- effort: Medium-high: requires the planned rotary encoder and second button in the product enclosure, a bounded pending-choice queue, and relay-to-pendant summaries.  ·  risk: A stale choice could be applied to a changed operation. Bind each choice to operation_id, step_id, digest, expiry, and current verified state; otherwise discard it and request a fresh summary.
- cost: Small firmware and relay storage cost; no meaningful model cost.  ·  latency: Immediate haptic response; 1–3 seconds for relay state refresh.
- security: The pendant receives no content or secrets, only typed risk, redacted label, digest and options. Never make a short press approve a dangerous branch.
- depends on: rotary encoder and extra button hardware integration; existing tactile_action_outcome_beacon; operation coordinator and verify_operation_step; physical_transaction_approval_latch


## What it asked for

_Nothing._
## Its own summary

Recorded three cross-surface capabilities and two changes: verified transactional execution, voice/wearable undo, safe browser send with digest-bound approval, target-binding TOCTOU guards, and wearable recovery choices. Live discovery shows AI Pendant Agent now has Accessibility and Screen Recording, Safari bridge is online (stale ~14s, zero pending commands), and the Mac is observable. The granted audio_path_probe still does not resolve to a live implementation, so no audio measurement was claimed.

**Biggest unknown:** The physical nRF9160 pendant is still absent from the live device table despite the bench-USB statement; I still need a real device registration/transport and the operation coordinator fields (operation_id, step_id, attempt_id, canonical digest) before these action capabilities can be executed end to end.

