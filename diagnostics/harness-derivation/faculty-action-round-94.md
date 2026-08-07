# Harness derivation — faculty-action — round 94

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Prepare this on my Mac and logged-in browser, then ask me on the pendant to confirm; only after I press the button should you commit it, and tell me exactly what happened."
- **useful because:** This is the missing handoff between preparation and real-world commitment: the Mac/browser can gather and stage a transaction, while the worn pendant is the one surface that can ask the owner at the moment of action. It prevents accidental sends or purchases and still works when the owner is away from the Mac.
- **path:** faculty-judgement → relay-realtime → mac-planner → browser-extension → mac-vision → pendant → relay
- **model tier:** Use the realtime model only for the brief spoken confirmation and disambiguation; use the cheaper background planner for gathering data, preparing fields, and validating the final diff.
- **latency:** Preparation may take seconds to minutes; spoken confirmation should arrive within 1 second of the final diff becoming stable. The commit must expire if not confirmed within 2 minutes or if the browser/Mac state changes.
- **cost:** Usually <$0.03 per transaction excluding model/provider fees; most cost is background browser extraction and Mac planning, not the short realtime confirmation.
- **security:** Do not send mail, buy, delete, or submit without the physical confirmation token. Bind the token to a hashed final diff, target tab/session, owner identity, and short expiry; invalidate on any precondition change. Never transmit page secrets to the pendant or relay beyond a concise summary.
- **missing:** A pendant-side confirmation primitive with local button event and visible/aural lease state; A verify_operation_step/verify_action_proof preflight API that can bind confirmation to the exact planned step; Browser bridge recovery and tab/session affinity while the transaction is staged; A durable staged-transaction record with expiry and cancellation

### "After you do something for me, verify that the intended real-world result actually happened—not merely that the command returned success—and tell me if the outcome is confirmed, disproved, or still unknown."
- **useful because:** Today an action can produce a successful-looking receipt while Accessibility is ineffective, a browser bridge is offline, or a site has rejected the change. The owner needs truth about the result, not just whether an agent attempted a command. Verification could independently check that a sent message appears in Sent, a calendar event exists with the expected fields, a file has the expected hash, or a browser transaction shows its confirmation state.
- **path:** faculty-judgement → faculty-action → mac-planner → mac-vision → browser-extension → relay-realtime → relay
- **model tier:** Use a cheaper background model to derive and run deterministic postconditions; use the realtime model only to explain an ambiguous outcome briefly to the owner.
- **latency:** Add up to 2–10 seconds for deterministic verification, with longer workflows allowed to remain pending. Never claim success until the postcondition passes or explicitly mark the outcome unknown.
- **cost:** Low: usually one or two lightweight reads per action; model cost is dominated by ambiguous reconciliation, which should be rare.
- **security:** Verification must be scoped to the target resource and avoid exposing private contents. For irreversible actions, require a predeclared postcondition and retain before/after evidence. If verification cannot safely inspect the target, report unknown rather than retrying.
- **missing:** A typed postcondition language for Mac, browser, filesystem, and service outcomes; Independent read-back adapters that do not reuse the mutating command's success flag; Receipt fields for expected outcome, verification evidence, confidence, and unknown state; A retry policy that distinguishes failed execution from successful-but-unverified execution


## Changes it proposed to its own stack

### `integration` — Install a mandatory action-preflight gate between faculty-judgement plans and every mutating executor. For each step, require a fresh signed observation (<=15 s) proving the target surface is reachable: Mac inputReachability/uiActionsWillReachTheScreen for UI actions, browser extension online plus matching session/tab for browser actions, and a live lease for any pendant-triggered action. If the proof is absent, stale, or mismatched, do not dispatch; persist a blocked receipt with the exact missing precondition and wake/re-evaluate on the next device heartbeat. Include the observation hash and expiry in the final receipt so a later agent can tell whether the action really reached the world.
- **owner gets:** The system currently reports UI actions as successful while doing nothing and has nine browser commands pending against an offline bridge. This prevents silent no-ops, avoids replaying stale browser work, and tells the owner exactly what must recover before an action can safely happen.
- effort: Medium: shared executor middleware, signed observation schema, TTL/heartbeat watcher, blocked-receipt state and tests across Mac and browser backends.  ·  risk: A false-negative preflight may delay a harmless action; recover by allowing an explicit owner-approved override for a named step and recording it. Never auto-replay a mutating step after recovery without revalidation.
- cost: Negligible API/storage cost; one small observation record per attempted step and occasional heartbeat checks.  ·  latency: Adds <100 ms when healthy; blocked work waits for recovery rather than consuming repeated 20–45 s browser timeouts.
- security: Improves safety by binding execution to fresh reachability proof; observation hashes reveal state metadata but no page contents or secrets.
- depends on: verify_operation_step tool or equivalent shared preflight API; action lease/receipt schema integration; browser bridge heartbeat and Mac inputReachability observation


## What it asked for

_Nothing._
## Its own summary

Recorded a new capability: outcome-verified actions. The system must independently check the intended real-world postcondition after execution and report confirmed, disproved, or unknown, rather than trusting command success or receipts. This addresses the observed Accessibility no-op and offline browser conditions without duplicating the existing action queue or receipt proposals.

**Biggest unknown:** The exact postcondition adapters and proof schema do not exist yet; they must be designed for each action surface and must never turn an unverified result into an automatic retry.

