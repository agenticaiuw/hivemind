# Harness derivation — faculty-action — round 228

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Do the task, and don't tell me it succeeded unless you independently checked the result; if it failed safely, fix it or tell me exactly what remains."
- **useful because:** This would make the system's central promise trustworthy across the pendant, relay, Mac, and browser: judgement plans, faculty-action executes, faculty-perception verifies fresh postconditions, and only then does the pendant announce success. Safe reversible failures can be retried automatically; irreversible or ambiguous outcomes stop with a truthful unknown state instead of a false success.
- **path:** relay-realtime → faculty-judgement → faculty-action → faculty-perception → mac-planner → mac-vision → browser-extension → unified
- **model tier:** Use the realtime model only to clarify the owner's request and narrate the result; use the cheaper background/local planner for decomposition, execution, retries, and evidence comparison.
- **latency:** 2-5 seconds for a simple Mac action, 10-30 seconds for a browser or multi-step task; verification must happen before the success beacon, even if that adds one round trip.
- **cost:** Low-to-moderate: one planning call plus local execution and a small verification call; the dominant cost is model reasoning for recovery, not the read-only verifier or receipts.
- **security:** Postcondition evidence must be sensitivity-labeled and default to hashes/minimal snippets. Never send page secrets or form contents to the pendant. A failed verification must not trigger an unbounded retry loop; irreversible actions require the existing physical transaction approval latch and an unknown result must be surfaced rather than guessed.
- **missing:** A first-class orchestration contract linking operation_id, step_id, executor receipt, verifier provenance, retry budget, and final outcome across POST /plan and POST /execute.; A recovery policy that classifies a failed postcondition as retryable, needs approval, or unknown without inventing owner policy.

### "Save this thread so I can continue it later on my Mac, exactly where we left off."
- **useful because:** A spoken conversation should become a resumable work item rather than disappearing into audio history. A deliberate pendant bookmark captures the current turn; the relay creates a compact encrypted continuation capsule containing the transcript cursor, unresolved decision, active operation, and relevant Mac/browser session handles. Later, the Mac or browser can reopen the right context without replaying private audio or making the owner repeat themselves.
- **path:** relay-realtime → faculty-judgement → faculty-perception → faculty-action → mac-planner → mac-vision → browser-extension → unified
- **model tier:** Use the realtime model only to identify the bookmark boundary and state the one-sentence continuation summary; use a cheaper background model/local code to assemble, index, expire, and retrieve capsules.
- **latency:** Bookmark acknowledgement under 500 ms on the pendant; capsule persistence within 2 seconds; resume in 3-8 seconds once the Mac/browser is reachable.
- **cost:** Low: one short summary generation per bookmark and otherwise storage/lookup; transcript and private page contents should not be re-sent when a stable handle or digest is sufficient.
- **security:** Capsules must be encrypted, scoped to the owner, expire by default, and contain opaque references rather than passwords, cookies, full browser pages, or raw microphone audio. Resuming an action must re-check current state and use the existing physical approval latch for consequential steps. The owner needs a way to list and delete capsules.
- **missing:** A continuation-capsule schema with transcript cursor, operation/job references, browser session handle, expiry, sensitivity labels, and a redacted human summary.; A pendant bookmark-to-relay event that binds the bookmark to the active conversation/session without storing a second audio copy.; A resume endpoint that rehydrates only the minimum context and invokes fresh perception before action.

### "Don't interrupt me while I'm busy; hold anything non-urgent and tell me at the first safe moment."
- **useful because:** The wearable can know that an alert was delivered, while the Mac can observe foreground work and the browser can report an active session. Together they can defer non-urgent spoken interruptions instead of talking over a meeting or typing session, then deliver a compact queue at a natural pause with a haptic cue. Urgent items bypass the queue, and every deferral is visible rather than silently lost.
- **path:** relay-realtime → faculty-judgement → faculty-perception → faculty-action → mac-planner → browser-extension → mac-vision → unified
- **model tier:** Use local rules for urgency, quiet hours, active foreground app, and queueing; use a cheaper background model to compress deferred items. Reserve realtime for the owner's explicit request or an urgent alert.
- **latency:** Observe and classify within 1 second of an attempted delivery; urgent alerts under 2 seconds; deferred digest under 5 seconds after a safe delivery opportunity.
- **cost:** Low: mostly route reads, queue operations, and one small summarization call for a batch. No continuous model streaming is needed.
- **security:** Foreground app names and browser session metadata are sensitive; retain only coarse categories and short-lived timestamps. Never infer availability from an absent heartbeat. An urgent classification must be explainable and configurable by the owner, with conservative defaults. Do not use the pendant microphone to monitor conversations.
- **missing:** A durable interruptibility policy with owner-set urgency classes, quiet windows, expiry, and a safe-default unknown state.; A delivery arbiter that combines /observe, /browser/status, scheduled jobs, audio playback acknowledgements, and current conversation state without treating stale presence as current availability.; A pendant queue presentation that distinguishes urgent, deferred, expired, and failed delivery using the existing outcome beacon.

### "Show me exactly what information you sent to each device or website while doing that, and let me revoke anything that should not remain."
- **useful because:** The owner currently gets action receipts, but not a comprehensible, cross-surface account of data movement. A provenance ledger would answer which transcript fragments, files, form fields, and derived summaries crossed the relay, Mac, browser, or third-party boundary, with hashes and destinations rather than copying secrets into a new report. It would make privacy inspectable after the fact and support targeted deletion or credential/session revocation where possible.
- **path:** faculty-perception → faculty-action → relay-realtime → mac-planner → mac-terminal → browser-extension → mac-vision → unified
- **model tier:** Use deterministic instrumentation and hashing for collection and joins; use a cheaper model only to render a plain-language explanation. Realtime is unnecessary unless the owner asks during an active task.
- **latency:** No more than 100 ms added per action for event capture; an on-demand report in 2-5 seconds; revocation requests may take longer but must show pending versus completed.
- **cost:** Low-to-moderate storage and hashing cost, with small summarization calls only when requested. The dominant engineering cost is adding data-boundary events to every executor and browser adapter.
- **security:** The ledger must not become a second secret store: default to field names, classifications, sizes, destination identities, and salted hashes; retain raw values only under explicit owner policy. Reports need access control and expiry. Deletion must distinguish local erase, remote deletion requested, and impossible-to-recall exposure.
- **missing:** A canonical data-flow event schema linking operation/step, source classification, destination, transformation, retention, and deletion status across relay, Mac, and browser.; Instrumentation hooks in POST /execute and browser commands that emit those events even on failure.; A user-facing revocation/deletion workflow that can invalidate browser sessions, remove local artifacts, and report limits honestly.

### "Handle this for the next hour, but do not spend money, contact anyone, or use files outside this folder; stop and show me what you found when the limit is reached."
- **useful because:** The owner needs useful autonomy without granting an all-purpose agent. A bounded delegation contract would travel with the task across relay, Mac, and browser: allowed destinations, files, action classes, time, number of attempts, and external side effects are enforced mechanically. The system can research, draft, and prepare work unattended, then stop at a declared boundary instead of silently escalating its authority.
- **path:** faculty-judgement → faculty-action → faculty-perception → relay-realtime → mac-planner → mac-terminal → mac-vision → browser-extension → unified
- **model tier:** Use deterministic policy enforcement and local planners for limits; use a cheaper background model for research and drafting. Realtime only handles clarification or a boundary decision that the owner explicitly asks to resolve.
- **latency:** Contract validation under 100 ms before each action; ordinary work proceeds at current latency; a boundary stop and pendant notification within 2 seconds of reaching a limit.
- **cost:** Low per invocation once policy enforcement exists; storage is a compact signed contract and counters. Model spend becomes predictable because token, time, step, and retry budgets are hard ceilings.
- **security:** The contract must default-deny unspecified capabilities, bind to a specific operation and expiry, and be checked locally even if the relay is unreachable. Browser cookies and Mac credentials remain inaccessible unless explicitly named as an allowed capability. Exceeded budgets produce a stopped/unknown result, never an automatic extension.
- **missing:** A signed, portable delegation-contract schema with allow/deny rules for paths, domains, action classes, time, spend, token and step budgets.; Enforcement hooks in Mac shell/AppleScript, browser actions, relay jobs, and queued retries, with counters that survive crashes.; A compact owner-facing preview and post-run report showing each consumed budget and the exact boundary that stopped the task.


## What it asked for

_Nothing._
## Its own summary

This round produced three non-duplicate capabilities. The highest-value one is an end-to-end truthful executor: faculty-action runs the plan, faculty-perception independently verifies fresh postconditions, and the pendant announces success only after evidence; safe failures can recover, ambiguous ones remain unknown. I also proposed resumable conversation-to-work capsules (bookmark on the pendant, encrypted relay handoff, fresh Mac/browser context on resume) and an attention-safe delivery arbiter that defers non-urgent interruptions until the Mac/browser indicate a safe moment. What I still need is implementation of the missing orchestration contracts: operation/step IDs joined to executor receipts and verifier provenance, a redacted continuation-capsule schema and resume endpoint, and an owner-editable interruptibility/urgency policy. I also still need a real source for Mac lock/wake state; until then availability must remain unknown, not inferred.

**Biggest unknown:** Whether the owner wants the first policy defaults for retries, capsule expiry, urgency, and safe delivery chosen conservatively by the system or explicitly configured before these capabilities are built.

