# Harness derivation — faculty-action — round 157

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Send this message, but stop if the recipient, attachment, or final text differs from what I approved—and tell me whether it was actually sent.”"
- **useful because:** The owner gets a trustworthy, end-to-end send operation rather than an optimistic click: Mac/browser executes, faculty-perception independently checks the final draft and post-send state, and the pendant’s physical transaction latch is the last consent boundary. If a tab reloads, recipient changes, or the result is ambiguous, it stops and reports unknown instead of claiming success.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use realtime only for the owner’s short approval conversation; use the cheaper background planner for the action plan and faculty-perception verifier.
- **latency:** Plan under 2 s; physical approval immediate; browser execution under 10 s; verification under 3 s, with an explicit unknown state on timeout.
- **cost:** About $0.01–$0.05 per operation; browser/verification latency and relay orchestration dominate, not tokens.
- **security:** The relay receives only a redacted action summary and hashes; page contents and form secrets stay on Mac/browser. Require physical approval for send, never auto-retry a non-idempotent submit, and retain an append-only receipt. Missing: a production binding from physical_transaction_approval_latch to the operation commit coordinator.
- **missing:** operation commit coordinator that binds plan hash, approval nonce, executor receipt, and verify_operation_step result; browser adapter exposing stable recipient/attachment/draft locators without exporting secrets; owner-configurable risk policy for which send classes require the latch

### "“When I say ‘pick this up later,’ save a resumable capsule of exactly where we are in the Mac/browser task, and let me resume it from the pendant without starting over.”"
- **useful because:** Long tasks currently become opaque jobs or stale browser tabs. A capsule would capture the plan version, current step, browser session/tab identity, safe UI anchors, and what remains—then let the owner resume after sleep, a link drop, or a changed tab. The owner can ask for status and get a concise spoken answer, while execution refuses to continue if perception finds the state has drifted.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Cheap background model summarizes and compacts the state; realtime is used only when the owner asks to resume or clarify.
- **latency:** Checkpoint under 1 s after a step; resume preflight under 3 s; no model call for ordinary status reads.
- **cost:** Usually <$0.01 per checkpoint; storage and browser-state inspection dominate.
- **security:** Capsules must contain opaque session IDs and locator hashes, never cookies, page secrets, or raw private text. Expire capsules and require renewed physical approval for consequential continuation. Missing: a durable capsule schema and drift-aware resume gate.
- **missing:** durable task-capsule store with redacted state and expiry; browser session snapshot/restore contract with tab affinity; resume gate that calls perception before every consequential continuation

### "“If my Mac task loses its connection or the browser changes underneath it, recover what is safe, tell me what was not done, and offer one-tap resume from the pendant.”"
- **useful because:** This turns a dropped-link failure into a bounded recovery the owner can actually trust. The relay retains the operation intent and last verified checkpoint; the Mac agent reconciles current app/browser state; faculty-perception distinguishes not-started, completed, and ambiguous; the pendant presents a short outcome and a deliberate resume/cancel gesture. It prevents duplicate sends and avoids making the owner reconstruct state manually.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background model classifies recovery and drafts the spoken summary; realtime only handles the owner’s resume/cancel exchange.
- **latency:** Relay detects loss immediately; reconciliation within 5 s of Mac return; owner decision in one gesture.
- **cost:** <$0.02 typical; reconciliation calls and durable receipts dominate.
- **security:** Never replay non-idempotent actions from an executor receipt alone; require independent postcondition verification and a fresh approval after ambiguity. Keep payloads redacted and bind recovery to an operation hash/expiry. Missing: recovery state machine with idempotency keys and explicit ambiguous outcome.
- **missing:** durable recovery state machine (checkpoint, interrupted, reconciled, ambiguous, resumed, cancelled); idempotency-key support in Mac/browser executors; relay push to pendant for concise recovery status

### "“Give this agent a temporary, narrowly scoped power—only these exact files/sites, only until 5 PM, and revoke it immediately if I press the pendant button.”"
- **useful because:** Today approval is mostly a one-shot consent. The owner needs delegation that is useful while they are away without becoming an open-ended grant: a cryptographically bounded capability can authorize a defined workflow, resource set, deadline, and spend limit, while the pendant remains an offline revocation switch. The relay can hold the delegation, the Mac can act when it wakes, and the browser can use an existing authenticated session without exposing credentials.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background model compiles and checks the delegation policy; realtime is used only to explain the scope and acknowledge approval/revocation.
- **latency:** Issuing or revoking a grant should take under 2 seconds; enforcement adds no perceptible delay to ordinary actions.
- **cost:** Under $0.01 per grant; durable policy storage and audit receipts dominate.
- **security:** The model must never mint broader authority than the owner approved. Bind grants to resource hashes, exact route/action classes, expiry, nonce, and a monotonic revocation epoch. Do not transmit passwords or page contents to the relay. Every denied or out-of-scope attempt should be visible to the owner. Missing: a capability-token enforcement layer spanning relay, Mac executor, and browser bridge.
- **missing:** scoped capability-token format and verifier shared by relay, Mac, and browser; pendant revocation epoch that works during link loss and reconciles safely later; executor enforcement before every action, not only at plan creation; dashboard showing active grants, expiry, use count, and revocation

### "“Handle this private website task, but let the relay know only whether each required condition passed—not the page text, account data, or secrets.”"
- **useful because:** The owner could use authenticated browser sessions for banking, health, and work portals without making sensitive contents part of model context. The browser performs local extraction and returns typed predicates or hashes; Mac execution proceeds only when those predicates match the plan, and the pendant can approve the final action without seeing the secret.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background planner defines typed predicates; realtime only handles the owner’s request and approval. No model should receive raw private page content.
- **latency:** Predicate evaluation under 500 ms; ordinary tasks remain under 5 s unless the browser requires navigation.
- **cost:** Less than $0.01 per predicate bundle; browser-side evaluation dominates.
- **security:** A predicate can itself leak sensitive information, so classify sensitivity, rate-limit queries, bind predicates to a specific origin and tab, and prevent arbitrary selector exfiltration. Missing: a browser privacy enclave/typed-result protocol and Mac executor support for predicate-only preconditions.
- **missing:** origin-bound browser predicate evaluator; typed privacy labels and leakage budget; executor precondition API that accepts predicate proofs rather than page text; audit receipt proving what was evaluated without recording the value


## Changes it proposed to its own stack

### `interaction` — Add a pendant emergency automation freeze gesture on sw1: it publishes a signed revocation epoch, relay immediately stops queued and in-flight cancellable work, browser bridge refuses new commands, Mac agent marks non-idempotent operations unknown, and the owner later receives a reconciliation summary. This is a global stop control, not an approval or per-job cancel.
- **owner gets:** The owner can stop the entire hive instantly when a device is lost, a browser looks wrong, or an action starts behaving unexpectedly—even without opening the Mac or finding the phone.
- effort: Medium-high: firmware gesture/state, relay fan-out, executor checks, browser refusal path, and reconciliation UI.  ·  risk: A false trigger could interrupt useful work; require a deliberate sw1 hold/chord and make every interrupted operation recoverable rather than replayed. If the link is down, queue the revocation with monotonic precedence and apply it on reconnect.
- cost: Negligible API cost; small firmware and durable-state overhead.  ·  latency: Emergency propagation target under 1 second while connected; no normal-path cost beyond an epoch check.
- security: Strongly positive: creates a physical kill switch and closes the gap between approval and revocation. Must authenticate epochs and reject stale reconnect messages.
- depends on: physical_transaction_approval_latch (s10-j9l4) gesture/event plumbing; relay push to Mac and browser; executor-wide revocation-epoch checks; operation reconciliation for interrupted non-idempotent work


## What it asked for

_Nothing._
