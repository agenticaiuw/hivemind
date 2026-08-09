# Harness derivation — faculty-action — round 253

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If my Mac restarts or the browser disconnects halfway through something I asked you to do, resume it safely without doing it twice."
- **useful because:** Today a lost executor receipt can leave an action in the dangerous state where retrying duplicates it and stopping abandons it. This gives the owner a truthful, crash-safe continuation across relay, Mac, and browser.
- **path:** relay → mac-planner → mac-vision → browser → pendant
- **model tier:** background for reconciliation and receipt interpretation; realtime only for the owner's live question
- **latency:** Reconcile within 10 seconds of reconnect; never trade correctness for speed.
- **cost:** Usually <$0.01 per recovery; dominated by one perception/verification call, not the relay bookkeeping.
- **security:** Persist only opaque operation and step IDs, hashes, risk class, and minimal postcondition evidence. On reconnect, faculty-perception must independently inspect current Mac/browser state before any retry. High-risk or ambiguous steps remain staged for the owner's physical approval; never infer success from an executor receipt alone.
- **missing:** A durable per-step idempotency key and dependency graph shared by relay jobs and Mac/browser executors; A recovery coordinator that asks faculty-perception to classify each interrupted step as committed, not-started, or unknown and chooses retry/compensation; A compensation contract for reversible steps

### "When something may have happened but you cannot prove it, tell me exactly what is unknown and give me the safest next step instead of retrying blindly."
- **useful because:** A duplicate email, purchase, deletion, or form submission is often worse than waiting. The owner gets a compact explanation and a recovery option grounded in fresh Mac/browser evidence, rather than a confident but false success.
- **path:** faculty-perception → mac-vision → browser → relay → pendant → mac-planner
- **model tier:** background for evidence reconciliation; realtime only to explain the incident conversationally
- **latency:** Produce an incident card within 15 seconds; do not mutate state while assembling it.
- **cost:** <$0.02 per incident, dominated by fresh perception and one concise explanation.
- **security:** Evidence is minimized and redacted: app/site identity, step IDs, timestamps, and hashes by default, never form secrets or page contents on the pendant. The card must distinguish committed, not-started, and unknown, expire stale evidence, and require explicit physical approval before any recovery mutation.
- **missing:** A first-class unknown-result incident object linked to operation/step IDs; A safe-recovery catalog describing query-only checks, compensating actions, and actions that are forbidden after uncertainty; A pendant rendering for unknown versus verified success that does not expose sensitive content

### "Show me which pending action needs my attention, let me scroll through them on the pendant, and let me approve or cancel exactly one without opening my phone."
- **useful because:** The existing approval latch can safely hold decisions offline, but a single LED/button cannot safely select among several pending operations. A wheel plus the second button turns that safety primitive into a usable daily control surface while keeping secrets off the wearable.
- **path:** relay → pendant → mac-planner → browser → faculty-perception
- **model tier:** Realtime only to summarize the selected risk; selection, expiry, and rendering are firmware/relay state machines
- **latency:** Haptic acknowledgement under 100 ms; relay synchronization opportunistic and safe across link loss.
- **cost:** Negligible inference cost; firmware work and rotary input are the dominant cost.
- **security:** Pendant receives only opaque operation ID, short risk-labelled summary, deadline, and digest—not page contents, credentials, or message bodies. Approval is a deliberate wheel click/second-button gesture, signed with the monotonic counter; expired, consumed, or digest-mismatched entries are refused. Unknown outcomes cannot be presented as success.
- **missing:** Rotary encoder and second product button, plus jewelry-compatible enclosure integration; A compact signed pending-item protocol and deterministic ordering/expiry rules; Firmware support for wheel navigation and DRV2605L haptic patterns (i2c2 is currently disabled)

### "Before sending, buying, deleting, or changing anything, warn me if the Mac or browser is in the wrong account or workspace, and let me switch to the right one without exposing its contents to the pendant."
- **useful because:** A correct instruction executed in the wrong logged-in account is still a real-world failure. Today the system can act through sessions but cannot provide a unified identity boundary across Mac apps, browser profiles, and the wearable.
- **path:** pendant → relay → mac-planner → mac-vision → browser → faculty-perception
- **model tier:** Background model for account/workspace classification; realtime only for the brief warning and owner choice
- **latency:** Identity check under 3 seconds before a mutating step; no mutation until the check is fresh.
- **cost:** Typically under $0.02 per guarded operation; dominated by one browser/Mac state inspection.
- **security:** Return only opaque account labels such as “personal Gmail” or “work Slack,” never addresses, page contents, or credentials to the pendant. Treat unknown identity as a hard stop. Switching sessions requires explicit owner approval and a fresh verification afterward.
- **missing:** A cross-surface identity attestation schema for app, browser profile, tenant/workspace, and freshness; Read-only Mac/browser probes that expose stable account fingerprints without secrets; A policy hook in every mutating executor that blocks when the attestation is absent, stale, or mismatched

### "Undo the last thing you did, but only if you can prove the reversal will not damage anything else; otherwise show me the safest manual recovery."
- **useful because:** Most automation systems stop at success, leaving the owner to repair mistakes. A verified inverse would make everyday delegation safer for edits, moves, drafts, settings, and browser changes without pretending every action is reversible.
- **path:** pendant → relay → mac-planner → mac-terminal → mac-vision → browser → faculty-perception
- **model tier:** Background model generates candidate inverses; faculty-perception verifies current state; realtime explains the choice only when needed
- **latency:** Generate a reversal preview within 10 seconds; execute only after fresh verification and, for destructive classes, physical approval.
- **cost:** $0.01–$0.05 per undo preview, depending on evidence and inverse planning.
- **security:** Never delete or overwrite based on inference. Store a bounded, encrypted before/after manifest containing paths, object IDs, hashes, and risk—not secret contents. Reversal must be idempotent, expiry-bound, and report unknown when external side effects cannot be undone.
- **missing:** A typed inverse-action registry covering Mac files, app state, browser mutations, and external side effects; Before/after snapshots with provenance and retention limits; A dry-run reversal preview and a policy that separates locally reversible changes from irreversible external actions

### "Why did that happen? Show me a human-readable chain from my spoken request to the exact Mac/browser changes, approvals, and evidence, including where uncertainty entered."
- **useful because:** Today receipts and logs are fragmented by surface. The owner cannot independently understand whether the system misunderstood them, chose the wrong target, or executed correctly but encountered an external failure.
- **path:** pendant → relay → mac-planner → mac-vision → browser → faculty-judgement → faculty-perception
- **model tier:** Background model builds the explanation from signed events; realtime summarizes it conversationally when the owner asks
- **latency:** Return a first causal explanation within 5 seconds, with deeper evidence loaded on demand.
- **cost:** Usually under $0.02; dominated by summarizing a multi-step event chain.
- **security:** Default to redacted labels, hashes, timestamps, risk, and provenance. Sensitive page text, message bodies, and credentials stay on the originating surface. Every claim must link to an event or be explicitly marked inference; never fabricate a causal link from timing alone.
- **missing:** A tamper-evident cross-surface event graph with request, plan, executor, approval, verification, and external-result edges; Stable correlation IDs propagated through relay jobs, Mac actions, browser commands, and pendant decisions; A redaction and owner-facing explanation layer that can distinguish evidence, model choice, and unknown


## What it asked for

_Nothing._
