# Harness derivation — faculty-action — round 196

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If an action partly succeeds or times out, stop the workflow, tell me exactly which steps are proven and which are unknown, and offer only safe compensating steps—never blindly retry a possibly-submitted browser or Mac action."
- **useful because:** The dangerous failure is not a clean error; it is an ambiguous side effect such as a message sent but no receipt. This lets the owner recover without duplicate sends or hidden partial state, using the pendant for a concise alert and the Mac/browser for repair.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-perception
- **model tier:** background for workflow bookkeeping; realtime only for the owner's immediate explanation
- **latency:** Initial classification under 2 seconds; verification and compensation may take 5–30 seconds, with explicit pending state.
- **cost:** Low: mostly deterministic ledger and verifier calls; one cheap model call only to explain recovery options.
- **security:** Never auto-compensate an irreversible action. Do not include secrets or page contents in pendant messages. Compensation requires the existing physical approval latch when externally visible or destructive.
- **missing:** A first-class workflow recovery record linking step receipts, verifier evidence, and allowed compensations; A compensation policy per action class, defaulting to stop-and-ask; A relay verb to deliver recovery choices and outcomes to the pendant

### "Before executing an approved multi-step task, re-check that the Mac app, browser session, target record, and relevant files are still the ones I approved; if anything changed, invalidate the approval and ask me again instead of acting on stale context."
- **useful because:** An approval made against a stale page or changed file is not meaningful consent. This prevents the classic failure where a queued action runs later against a different account, recipient, tab, or document.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-perception → faculty-judgement
- **model tier:** background deterministic comparison; realtime only if the owner is waiting
- **latency:** One preflight under 1 second for host/browser state; up to 5 seconds when file or page verification is required.
- **cost:** Negligible model cost; bounded calls to existing observation and verification endpoints.
- **security:** Hashes and stable locators should be used instead of transmitting form secrets or page contents. Any mismatch must fail closed and discard the approval nonce; never silently broaden a locator.
- **missing:** A signed approval binding containing state hashes/locators and an expiry; A pre-execution invalidation hook in the executor; A compact mismatch explanation rendered by the pendant

### "When I approve a task that needs both my browser and Mac, execute it as a resumable handoff: show me which surface is waiting, preserve completed steps, and resume only after fresh verification—without repeating anything that may already have happened."
- **useful because:** Today a browser bridge drop or Mac restart can leave a task stranded between surfaces. A resumable handoff turns that into a truthful, recoverable operation instead of either losing work or duplicating it.
- **path:** pendant → relay → mac-planner → browser-extension → mac-terminal → faculty-perception
- **model tier:** background for state-machine transitions; realtime for concise owner-facing status
- **latency:** Status changes should reach the pendant within 1–2 seconds; resume can wait for the relevant surface and verify each checkpoint.
- **cost:** Low-to-moderate: durable operation records and verification calls dominate; no large model context needed.
- **security:** Persist only opaque IDs, hashes, and minimal summaries. Expire approvals and sensitive browser bindings. A resumed action must require the same physical approval policy if its target or risk changed.
- **missing:** A durable cross-surface operation state machine with checkpoint IDs and idempotency keys; Surface-specific wake/rebind notifications for Mac and browser sessions; A resume endpoint that requires fresh t21-8d1c verification before each side effect

### "Give the system a bounded objective such as “get this appointment booked this week under $200,” let it search and negotiate across my logged-in browser and Mac, and have it stop automatically at explicit limits—price, date window, recipient, number of attempts, and irreversible side effects—while asking me only when a boundary or ambiguity is reached."
- **useful because:** The owner gets the outcome rather than having to dictate every click, but retains a comprehensible safety perimeter. This is materially different from a fixed macro: the system can adapt across sites and applications while proving it stayed within the delegation contract.
- **path:** pendant → relay → mac-planner → browser-extension → mac-terminal → faculty-judgement → faculty-perception
- **model tier:** Background/cheap model for search, comparison, and bookkeeping; realtime only for an interruption or boundary question.
- **latency:** Permit minutes for web search and booking; every boundary decision should be surfaced within 2 seconds and execution pauses until resolved.
- **cost:** Moderate: several browser/Mac actions and perception checks, with cheap models for candidate ranking; expensive inference only for ambiguity or owner-facing explanation.
- **security:** The delegation contract must be signed and immutable for the run, with explicit allowlists for accounts, merchants, recipients, spend, time, retries, and side-effect classes. Never expose credentials to the pendant. Any contract expansion requires a new physical approval; failed or ambiguous payment/submission must halt rather than retry.
- **missing:** A first-class signed delegation contract and evaluator for quantitative and categorical limits; A planner/executor loop that can compare candidates without committing and then commit exactly one chosen candidate; A pendant interaction for concise boundary questions and contract-expansion approval; A ledger that records every attempted side effect against the contract, including rejected attempts

### "Fill online forms for me while showing me, on the pendant, exactly which sensitive fields are about to leave my devices; let me approve each field category (identity, contact, financial, medical) once for this task, and automatically omit fields that are not necessary for the stated purpose."
- **useful because:** The owner can get tedious applications and checkouts done without surrendering an entire profile to every website. The browser session can see the form, the Mac can source local data, and the pendant provides a private approval surface without displaying secrets.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-perception
- **model tier:** Cheap background model for field-purpose classification; realtime only for a sensitive-field approval prompt.
- **latency:** Classify a form in under 3 seconds; pause immediately before each new sensitive category is transmitted.
- **cost:** Low-to-moderate: DOM inspection and local data lookups dominate; model calls are small and structured.
- **security:** Never send raw field values to the relay or model. Approval must bind to origin, field locator, purpose, and a digest of the value; reject changed fields and cross-origin redirects. Financial and medical categories should default to deny.
- **missing:** A local-only field-value broker with category and purpose labels; A browser command that can preview a field without reading its secret value into the planner; A pendant protocol for category-level consent and expiration; A proof that omitted fields were not submitted

### "After I say “handle this,” have the system turn a messy real-world request into a private, auditable action plan: identify the people, accounts, dates, and money involved; show me only the decisions that materially change the outcome; and let me revoke the delegation from the pendant at any moment before the final side effect."
- **useful because:** The owner gets an assistant that can take responsibility for translating intent into coordinated work without forcing them to supervise every intermediate step. A persistent audit trail and instant physical revocation make broad delegation understandable and safe.
- **path:** pendant → relay → mac-planner → browser-extension → mac-terminal → faculty-judgement → faculty-perception
- **model tier:** Background planner for decomposition and candidate comparison; realtime only for the small number of material decisions and revocation handling.
- **latency:** Plan in under 10 seconds for ordinary tasks; revocation must preempt queued work within 500 ms where technically possible.
- **cost:** Moderate: structured planning and multiple read-only checks; no large context should be resent after each step.
- **security:** The plan must separate observation from commitment, carry an expiry and revocation epoch, and require the existing physical approval for irreversible effects. Revocation must be honored even if the Mac or browser reconnects later; queued jobs must fail closed.
- **missing:** A revocation epoch enforced by relay, Mac, and browser before every side effect; A compact plan/diff representation suitable for the pendant; A durable decision ledger linking owner decisions to each executed step; Preemption semantics for already-running actions


## Changes it proposed to its own stack

### `hardware` — Add a low-profile detented rotary encoder with integrated push switch to the jewellery pendant, wired to two interrupt-capable GPIOs plus one button input, with debounce and wake-from-sleep support. Reserve the encoder for selecting among queued status/recovery items and choosing a safe response; do not overload sw0's active-edge recording path.
- **owner gets:** The owner can distinguish several pending or failed actions without a screen, voice, or twenty ambiguous long-press meanings: turn to hear/select the item, press to acknowledge or choose a safe recovery option. It makes the pendant usable in public and matches the intended jewellery form.
- effort: Medium hardware revision and firmware input/state-machine work; enclosure and waterproofing need redesign.  ·  risk: False counts or accidental presses could select the wrong item; require an explicit press-and-release confirmation and keep destructive approval on the existing physical transaction latch. Recovery is to ignore invalid quadrature sequences and fall back to sw1 status acknowledgement.
- cost: Roughly $2–8 in parts and PCB/enclosure changes; negligible additional power except wake interrupts.  ·  latency: Sub-50 ms input response; no model latency for navigation.
- security: Improves safe selection but must not itself authorize irreversible actions; retain nonce-bound approval and fail closed on ambiguous input.
- depends on: physical_transaction_approval_latch; tactile_action_outcome_beacon; A new enclosure/PCB revision with two GPIOs and a debounced encoder driver


## What it asked for

_Nothing._
## Its own summary

Round 196 produced four non-duplicate proposals. The single most useful is ambiguity-safe cross-surface recovery: when a Mac/browser action may have happened but its receipt is missing, stop, independently verify, distinguish proven/unknown steps, and offer only approved compensations—never blind-retry. I also proposed stale-context invalidation before execution, resumable Mac↔browser handoffs with checkpoint verification, and a physical rotary encoder for selecting queued recovery/status items without overloading recording controls. What I still need is not another observation: the system needs a durable operation-recovery state machine, signed state-bound approvals with invalidation hooks, compensation policy data, and a relay-to-pendant recovery-choice protocol. I also asked judgement for fresh gaps.

**Biggest unknown:** Whether /prepare and /approve are truly live routes or merely established descriptions; proposal recording noted they were not fully inventoried. The next useful step is a complete live schema check for those routes and for operation-level recovery/compensation primitives, not another generic action proposal.

