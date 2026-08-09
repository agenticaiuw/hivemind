# Harness derivation — unified — round 222

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "After my Mac or browser reconnects, continue the interrupted task only if the exact tab, page identity, and world state still match; otherwise tell me what changed and give me a new plan instead of replaying anything."
- **useful because:** A relay job can remain processing for 24 hours and the ledger resume engine exists but is never invoked; browser leases can also expire without the supervisor running. This capability would make outages recoverable without duplicate sends, purchases, edits, or form submissions, while making stale-page changes visible to the owner.
- **path:** relay-realtime → mac-planner → browser-extension → dashboard → pendant
- **model tier:** Deterministic state machine for leases, replaySafety, page/world fingerprints, and idempotency; background model only to explain a mismatch in plain language.
- **latency:** On reconnect, fingerprint and decision in under 1 second; resume idempotent work immediately; hold unrepeatable work for the next owner conversation and physical confirmation.
- **cost:** Negligible model cost for normal recovery; <$0.01 only when a mismatch needs explanation. Dominant costs are a few browser inspection calls and durable relay writes.
- **security:** Bind a resume token to job ID, action digest, origin/tab identity, and expiry. Never treat a stale inflight ledger as evidence that an action completed. Auto-resume only idempotent/additive steps; block unrepeatable/unknown steps. Record both the pre-reconnect and post-reconnect fingerprints.
- **missing:** Close ordinary orchestrator ledgers so completed work is not falsely classified as interrupted; A lease_until and requeue sweep for relay_jobs, plus activation of browser lease sweeping; A reconnect coordinator that calls planResume and GET /workbench/jobs/:jobId/handoff, then executes only the safe subset; A concise owner-facing mismatch receipt surfaced through the next pendant conversation

### "Give me a portable privacy report of everything this system currently holds about me—facts, voice-note metadata, browser artifacts, relay copies, and pending deletions—with a checksum, retention location, and last-access time."
- **useful because:** Deletion is only trustworthy if the owner can first see the inventory and later verify what remains. This is not an action history: it is a bounded data map across the pendant, Mac, browser, and relay, including copies that are pending remote erasure. It makes the system auditable without exposing secrets in ordinary conversation.
- **path:** dashboard → relay-realtime → mac-planner → browser-extension → pendant
- **model tier:** Deterministic inventory and hashing; background model may turn opaque paths and record types into a readable summary, but must not decide what is included.
- **latency:** Generate a local report in under 5 seconds; mark remote replica probes pending rather than blocking. Reconcile remote locations in the background and append signed updates.
- **cost:** Minimal model cost; mostly filesystem/database enumeration and hashing. A full report may cost a few cents in I/O/egress if remote replicas must be queried.
- **security:** Encrypt the export, require explicit owner request, redact credentials, tokens, raw audio, and page contents by default, and make inclusion opt-in per category. Include only metadata and cryptographic hashes unless the owner explicitly requests content. Store no extra permanent copy of the report.
- **missing:** A cross-surface inventory schema with stable object IDs and location/retention fields; Read-only adapters for facts/context graph, voice notes, browser spool/results, relay D1/R2, and pendant OUTBOX/INBOX manifests; A signed report format and one-time download/expiration mechanism; A reconciliation worker that updates remote pending states without silently declaring deletion complete

### "After you change something in a browser or on the Mac, independently read it back and tell me whether the intended result is actually present—not merely that the command returned success."
- **useful because:** The current action receipts can say a command ran while the real world may have rejected it, a page may have navigated, or a save may have failed. An independent verification pass turns “I did it” into “the requested state is observable,” and reports ambiguous outcomes instead of claiming success.
- **path:** browser-extension → mac-planner → relay-realtime → dashboard → pendant
- **model tier:** Deterministic verifier first: use a bound read-only query and compare expected postconditions. Use a cheaper background model only to explain structured mismatches; never let it invent evidence.
- **latency:** Verify within 2 seconds for browser/Mac reads; if the target is eventually consistent, poll with a bounded 30-second window and speak “pending” rather than waiting indefinitely.
- **cost:** Usually no extra model call and <$0.01; costs are one or two read-only browser/Mac queries. External sites with slow propagation dominate latency.
- **security:** Verification bindings must be least-privilege and limited to the target tab/app/path. Never use a write-capable action as a check. Redact page contents and secrets; preserve a small evidence hash/snippet with timestamp, URL/app identity, and confidence. If evidence conflicts, mark the job uncertain and do not retry automatically.
- **missing:** A postcondition schema attached to each action plan (observable selectors, file predicates, or app state); A generic read-only verifier that can query browser and Mac targets and return evidence candidates; Receipt joins that distinguish command accepted, effect observed, and effect later contradicted; Owner-facing language for success, failed, pending, and unverifiable outcomes

### "Warn me—and by default stop—when an action would send my personal data to a new website, app, or relay destination. Show exactly which data fields would leave, where they would go, and let me set durable per-destination rules such as allow, ask, or deny."
- **useful because:** Today the browser and Mac can act with the owner's credentials, but there is no unified data-egress boundary. A page upload, form submission, email, or relay handoff can move sensitive information without a plain-language inventory of the destination. This gives the owner a durable privacy perimeter rather than relying on noticing each individual action.
- **path:** browser-extension → mac-planner → relay-realtime → dashboard → pendant
- **model tier:** Deterministic destination and field-policy engine for enforcement; a cheap background model may classify ambiguous text into a review queue, but it cannot override a deny rule. Realtime is used only to explain a blocked transfer during conversation.
- **latency:** Evaluate before dispatch in under 300 ms for known destinations; pause for at most 10 seconds for an owner decision, then deny. Policy updates should apply on the next action without restart.
- **cost:** Near-zero for known schemas and hashes; occasional classification costs <$0.01 per ambiguous payload. Browser inspection and payload redaction dominate compute, not model inference.
- **security:** Inspect only the bound tab/app and never copy raw secrets into the relay or pendant. Store field categories and hashes rather than payloads. Default unknown destinations to ask/deny, protect policy changes with explicit confirmation, and log destination, category, rule, and outcome without retaining content.
- **missing:** A pre-dispatch data-flow interception point for browser submissions, Mac messages/files, and relay uploads; A local sensitive-data classifier with conservative categories (credentials, financial, health, identifiers, private audio/text) and confidence; A durable per-origin/per-app policy store with versioned rules and a dry-run explanation; Receipt fields proving what was blocked or allowed without recording the sensitive payload

### "Put the system in guest mode for the next hour: answer general questions, but do not use or reveal my memories, browser sessions, files, or personal facts, and leave a receipt proving that the boundary held."
- **useful because:** A wearable is present around other people, yet today privacy is effectively all-or-nothing: the assistant can be conversationally useful or fully latched. A time-limited guest mode lets someone nearby use the device without exposing the owner's context or allowing actions through the owner's authenticated surfaces.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic capability firewall and context selector; realtime model handles only guest-safe dialogue. No planner or browser action is available in guest mode unless the owner explicitly exits it.
- **latency:** Enter locally in under one second and enforce immediately, including when the relay is unreachable. Guest responses should retain normal conversational latency; exit and receipt reconciliation can complete when connectivity returns.
- **cost:** Negligible additional model cost; a small amount of local policy state and audit metadata. A guest-safe model route may be cheaper than the full personal context route.
- **security:** The mode must be a device-local state, survive link loss, have a hard expiry, and prevent inference from personal context—not merely hide the final wording. Browser/Mac credentials and stored facts must be capability-denied. The receipt should contain policy version, start/end, and blocked-access counters, never guest speech by default.
- **missing:** A firmware guest-mode state and local expiry/LED indication distinct from the existing privacy latch; A server-side context firewall that makes personal memory and browser/Mac tools unavailable, rather than asking the model to self-censor; A relay/Mac receipt proving blocked reads and blocked actions across the interval; An owner-only authenticated exit path that cannot be triggered by a guest voice request


## Changes it proposed to its own stack

### `integration` — Make every browser/Mac action plan carry an explicit postcondition and verification phase. The executor should produce three separate receipt states—dispatched, observed, and contradicted/unknown—and refuse to report success when the read-back is absent. Use the existing action ledger to persist the verifier result and link it to the original receipt.
- **owner gets:** The owner hears a truthful answer about whether a change really happened, instead of a misleading “done” after a click or shell command merely returned. Failed saves and stale pages become visible without requiring the owner to inspect the screen.
- effort: Medium: add postcondition builders for common action types, a read-only browser/Mac verifier, receipt schema fields, and tests for positive, negative, and eventually-consistent outcomes.  ·  risk: Some actions have no observable postcondition; they must be reported as unverifiable, not blocked forever. A bad predicate could produce false confidence, so require evidence timestamps and target identity and expose the evidence to the owner. Recover by marking unknown and asking for a new plan rather than retrying.
- cost: Negligible recurring API cost; one extra read-only query per verified action. Development cost is the main impact.  ·  latency: Adds roughly 0.2–2 seconds for verification, with bounded polling only for explicitly eventual targets.
- security: Improves safety by keeping verification read-only and target-bound; avoid recording page contents or secrets, and hash/redact evidence.
- depends on: The recorded post-action independent verification capability; A stable postcondition schema for browser and Mac action types; Correct ledger closure and receipt joins so verification is not mistaken for dispatch

### `model-routing` — Add a payload-minimization gate before any model invocation: classify the request context locally, replace unnecessary personal fields with typed placeholders, and route sensitive operations to a local deterministic path whenever possible. The relay should receive only the minimum evidence required for the selected task, with a machine-readable disclosure record.
- **owner gets:** The owner gets the system's help without routinely shipping whole conversations, documents, or browser pages to a model. A task can still use “customer name” or “account number” as placeholders when the value itself is irrelevant, reducing exposure without requiring the owner to remember a privacy command every time.
- effort: High: local redaction/classification, placeholder-preserving prompt construction, model capability declarations, and regression tests proving that required fields survive while unrelated fields do not.  ·  risk: Over-redaction can make a task fail or alter meaning. The system must show missing-field explanations and request the smallest additional disclosure, never silently substitute guesses. Recovery is a user-approved one-time reveal scoped to the current task.
- cost: May reduce cloud token cost by shrinking context; local classification adds CPU but no meaningful per-call API cost. Some tasks may need an extra clarification turn.  ·  latency: Adds tens to hundreds of milliseconds locally; clarification can add a conversational turn when a value is genuinely required.
- security: Strongly reduces data exposure and creates an auditable disclosure boundary. Placeholder maps must remain local and be erased with the task unless explicitly retained.
- depends on: The recorded data-egress policy capability; A local, conservative sensitive-data classifier; Model/provider manifests declaring which tasks can run without raw values; A disclosure receipt that records categories and destinations, not payloads


## What it asked for

_Nothing._
## Its own summary

Recorded four non-duplicate proposals: (1) reconnect-safe interrupted-task continuation gated by replaySafety and fresh tab/world fingerprints; (2) portable cross-surface privacy inventory report with hashes and pending remote-replica states; (3) independent post-action verification that distinguishes dispatched from observed/contradicted; and (4) an integration change making postconditions and verification mandatory in action receipts. A browser-to-pendant approval proposal was correctly rejected as a duplicate of the existing physical approval loop.

**Biggest unknown:** The remaining blocker is implementation reach, not product direction: the relay still needs job leases/requeue, ordinary ledgers must close, browser lease sweeping must run, and read-only browser/Mac evidence plus stable postcondition schemas need to be wired. I still need those production integrations and a least-privilege browser identity/evidence binding; I am not re-requesting the already-pending browser_identity_attestation.

