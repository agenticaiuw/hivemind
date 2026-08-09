# Harness derivation — faculty-action — round 146

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **granted audio_path_probe availability** — The granted audio_path_probe schema is not implemented in the live inventory; invocation returned unresolved, nearest DELETE /focus. Do not claim a fresh audio measurement from it.
  - evidence: audio_path_probe(mode=capabilities,duration_ms=1000,inject_packet_loss_pct=0,fixture=none,persist_receipt=true) returned resolution=unresolved.

## Capabilities it proposed

### "Finish this task completely: if the app, browser, or file is not in the desired state, fix it and keep going until you can prove it is."
- **useful because:** Today an action can execute and then stop at a failure or ambiguous receipt. This gives the owner one dependable request: judgement plans, Mac/browser action executes, faculty-perception independently verifies, and faculty-action repairs and retries safe steps instead of making the owner diagnose partial completion.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use realtime only for the spoken request and approval; use a cheaper background planner for repair planning. faculty-perception performs read-only checks; faculty-action executes only reversible or explicitly approved retries.
- **latency:** Initial acknowledgement under 1 s; ordinary completion under 10 s; repair loop may run up to 60 s with spoken progress and a hard retry budget.
- **cost:** Usually one realtime turn plus 1–3 cheap planner/verifier calls; Mac/browser execution dominates wall time, not token cost.
- **security:** Never retry irreversible or duplicate-prone actions automatically. Each step declares idempotency, preconditions, and risk; a failed verification pauses for pendant approval. Data stays on relay/Mac/browser except the minimal spoken summary and hashed evidence.
- **missing:** A durable operation state machine joining planner steps, executor receipts, and verify_operation_step results; Idempotency and retry-budget metadata on action steps; A repair planner that can generate bounded compensating actions; A unified owner-visible result/unknown status across relay and pendant

### "If I lose the connection halfway through, resume the exact task where it stopped when I reconnect—without repeating anything that already happened."
- **useful because:** A wearable conversation, relay, Mac, and authenticated browser currently have different notions of progress. A durable cross-surface checkpoint lets the owner unplug, close the lid, or lose LTE and later hear exactly what is pending, what was verified, and what must not be repeated.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background model compacts checkpoints and chooses a resume narration; realtime is used only when the owner reconnects and asks for status.
- **latency:** Checkpoint writes under 200 ms after every step; reconnect summary under 2 s; no background model call is needed for simple state rendering.
- **cost:** Negligible per-step storage and hashes; occasional cheap summarization call, dominated by relay persistence rather than API tokens.
- **security:** Checkpoint stores references, hashes, risk and status—not passwords, page bodies, or microphone audio. Browser session identifiers are encrypted and scoped to the originating session. Resume requires fresh verification for any stale app/browser state and physical approval for pending high-risk work.
- **missing:** A durable operation checkpoint record shared by relay, Mac agent, and browser bridge; Crash/link-drop hooks that atomically persist step state before dispatch; Resume endpoint that returns pending/verified/unknown steps; Expiry and redaction policy for browser/session references

### "Stop whatever you are doing right now, including a browser submission or Mac workflow, and make sure it really stopped."
- **useful because:** The owner has no reliable physical emergency brake for an action already in flight. A spoken command alone can be delayed by the same workflow it is meant to stop; a pendant-originated interrupt must outrank queued work, cancel cooperative executors, and independently establish whether anything escaped before the stop.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime only for recognizing the stop request and concise status; cancellation propagation and post-stop verification use deterministic code and a cheap background verifier.
- **latency:** Pendant interrupt accepted locally in under 100 ms; relay fan-out under 500 ms; final stopped/unknown report under 3 s.
- **cost:** Near-zero model cost after the initial utterance; dominated by cancellation fan-out and independent verification calls.
- **security:** The interrupt must be authenticated to the active pendant session, work without microphone access, and fail closed on link loss. It cannot claim success for non-cancellable operations; those become explicitly unknown and require verification. No page contents or secrets are sent to the pendant.
- **missing:** High-priority interrupt channel from pendant firmware through relay; Cancellation tokens understood by Mac and browser executors; A post-interrupt reconciliation protocol for already-dispatched steps; Distinct pendant audio/LED acknowledgement for stopped versus unknown

### "Fill in this private form for me, but never show or tell the AI my password, recovery code, or payment secret."
- **useful because:** The browser may hold an authenticated session, yet the model cannot safely perform secret-bearing completion without risking exposure in prompts, receipts, or spoken output. A local secret broker would let the owner complete routine forms while keeping values inside the Mac/browser boundary.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime model handles intent and field descriptions only. A deterministic local broker maps approved field labels to Keychain/password-manager entries; the model receives only success, refusal, or a redacted validation error.
- **latency:** Preview under 2 s; local fill under 500 ms; submission still requires the existing physical approval latch when it has external side effects.
- **cost:** One cheap intent parse per request; no token cost for secret values. Engineering cost is local broker integration and audit testing.
- **security:** Secrets never enter relay logs, model context, browser inspection payloads, or pendant storage. Require domain/origin binding, exact field allowlists, expiry, and physical approval before submit. Refuse unfamiliar origins, hidden fields, and ambiguous matches.
- **missing:** A Mac-local Keychain/password-manager broker; Browser extension command that fills an opaque secret handle without returning its value; Redacted audit receipts proving which origin and field class were filled; Origin-bound approval metadata integrated with the physical latch


## Changes it proposed to its own stack

### `integration` — Add a cable-presence and pendant-session watchdog spanning the Mac bridge and relay. While a physical pendant session is attached over /dev/cu.usbmodem00096003658* or the ESP32 bridge over /dev/cu.usbserial-0287A9CA, tag dispatched operations with a live session lease. On disconnect, stop dispatching new steps, cancel only reversible queued work, mark already-dispatched work unknown, and require fresh postcondition verification plus (for risky work) the existing physical transaction approval latch before resuming.
- **owner gets:** Unplugging or losing the wearable becomes a safe pause rather than a silent half-action or accidental replay. The owner can reconnect and continue without wondering whether an email, purchase, or browser submission happened.
- effort: Medium-high: serial presence observer, lease propagation through relay/job records, cancellation policy integration, reconnect reconciliation tests on both USB paths.  ·  risk: False disconnect could pause harmless work; recovery is reconnect plus reconciliation. Never infer that an irreversible action failed merely because the cable vanished; classify it unknown and verify independently.
- cost: No meaningful API cost; small Mac daemon CPU and sub-watt USB-connected device overhead. Storage adds a few lease and event records per operation.  ·  latency: Sub-second pause on link loss; reconnect reconciliation typically 1–3 s.
- security: Improves fail-closed behavior. USB device identity and monotonic session counters must be authenticated; do not treat relay registry alone as evidence of pendant presence.
- depends on: A real read-only serial observer for both named USB devices (currently missing); Durable operation state machine/checkpoint records; Integration with existing actionRisk, prepareApprove, actionLedger, policyRouter, and physical_transaction_approval_latch

### `interaction` — Add an owner-visible 'side-effect ledger' that turns every compound operation into a plain-language before/after boundary: files created or changed, messages drafted versus sent, browser fields filled versus submitted, and steps that remain irreversible. Render a compact version through pendant audio/LED and a detailed version in the dashboard, with a single command to dispute a line and trigger re-verification rather than silently rewriting history.
- **owner gets:** The owner can finally answer “what did you actually change?” without reading logs or trusting a vague success phrase. It makes partial completion, irreversible residue, and disputed evidence understandable at the moment they matter.
- effort: Medium: normalize executor receipts and independent verification into typed ledger entries, add redaction and human summaries, and provide dispute/recheck flow.  ·  risk: Overly broad summaries could leak private content or create false certainty. Store hashes and structured deltas by default; show snippets only after explicit request and sensitivity checks.
- cost: Small storage and one cheap summarization call for complex operations; no recurring hardware cost.  ·  latency: Adds under 1 s for simple summaries; detailed ledgers can load asynchronously.
- security: Improves accountability but creates a new sensitive audit surface. Encrypt at rest, apply retention limits, and never include credentials or full page bodies by default.
- depends on: Typed action receipts with before/after references; Independent postcondition verification; A durable operation identifier shared across relay, Mac, and browser; Owner-configurable retention and sensitivity policy


## What it asked for

_Nothing._
