# Harness derivation — faculty-action — round 250

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “pause this and bring it back later,” save exactly where I am across the pendant, Mac, and browser, then restore that work later without guessing."
- **useful because:** A voice interruption currently loses the boundary between a thought, the active Mac app, and the logged-in browser page. This would let the owner leave mid-task and resume at the same form, tab, draft, and next safe step—not merely replay a note.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Use realtime only to capture the short command; use the cheaper background planner to assemble and later restore the checkpoint. mac-vision verifies visual state only when structured AppleScript/browser state is insufficient.
- **latency:** Capture under 2 s; checkpoint under 5 s; restoration may take 10–30 s but must report each step and stop on drift.
- **cost:** Roughly $0.01–$0.08 per checkpoint/restore, dominated by background planning and occasional vision verification; storage is small structured metadata plus optional owner-selected snippets.
- **security:** Never store passwords, page secrets, or microphone audio by default. Browser checkpoint stores origin, tab/session binding, non-sensitive field labels, and hashes rather than values. Restoration must stage risky submissions for the existing physical approval latch and mark stale or changed pages unknown.
- **missing:** A typed checkpoint schema covering pendant capture ID, Mac app/document identity, browser tab/session identity, cursor/field locator, next-step intent, and expiry; A restore orchestrator that can call the Mac and browser surfaces in sequence and stop on state drift; Owner policy for which drafts and documents may be checkpointed

### "Before you do a delayed or multi-step task for me, tell me whether the Mac and browser are still the same ones I authorized; if not, pause and ask me instead of acting on stale state."
- **useful because:** A queued action can outlive a browser session, foreground app, or draft. The owner gets a useful safety boundary that distinguishes “not yet done” from “the world changed,” especially while the pendant is offline and the Mac later reconnects.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Cheap background reconciliation checks freshness and identity; realtime is used only if the owner asks for an explanation. faculty-perception supplies current observations and faculty-action executes only after the lease remains valid.
- **latency:** Reconciliation within 1–3 s of Mac/browser return; no action should begin if identity evidence is older than the configured lease.
- **cost:** About $0.005–$0.03 per reconciliation, mostly route calls; no model call for unchanged state, with a small background model call only for ambiguous drift.
- **security:** Bind each staged operation to browser session ID, origin, Mac host identity, observed timestamp, and a digest of intended target state. Do not transmit page contents to the pendant. Expire leases on session replacement, logout, origin change, or meaningful postcondition drift. A mismatch produces a safe retry/unknown beacon, never an automatic retry of an irreversible step.
- **missing:** A first-class operation lease record and freshness/identity comparison in the job ledger; A route that atomically re-checks GET /observe and GET /browser/status immediately before execution; Policy data specifying lease durations by risk class

### "When I say “send this to my phone when it’s ready,” prepare the result on my Mac or browser, hand it to my real iPhone through iPhone Mirroring, and tell me whether it was actually delivered—not merely queued."
- **useful because:** The owner should not have to keep a Mac window open or manually move a generated file/link/message to the phone. This combines the pendant as the request and status surface, the Mac as the acting hand, browser sessions as the source, and iPhone Mirroring as the final destination.
- **path:** pendant → relay → mac-planner → browser → iOS → dashboard
- **model tier:** Realtime handles only the spoken request and concise status; a cheaper background planner resolves the source artifact and delivery plan. mac-vision is used only when iPhone Mirroring lacks structured state, and faculty-perception verifies delivery.
- **latency:** Acknowledge intent under 2 s; prepare within the owner-specified deadline; delivery should complete within 10 s once the source is ready. If the iPhone is unavailable, retain a staged job and do not claim delivery.
- **cost:** Approximately $0.01–$0.10 per delivery, dominated by background planning or vision fallback; ordinary structured action/verification calls are negligible.
- **security:** Treat message recipients, file contents, and browser session data as private. Show the target app/recipient and a content digest in the approval summary for sensitive sends. Never claim success from a click receipt: verify the iPhone's resulting message/file state, and return unknown if Mirroring or the destination app cannot expose proof. Expire staged deliveries and never silently redirect to another recipient or device.
- **missing:** A typed cross-surface delivery job with source artifact, iPhone destination, deadline, sensitivity, and postcondition; Reliable iPhone Mirroring action/state adapters exposed to the Mac planner; A result verifier for iOS message/file delivery, including a truthful unknown outcome

### "When I say “keep a record of this purchase,” capture a tamper-evident private evidence bundle from the logged-in browser and Mac—receipt, relevant URL, timestamp, and my short voice annotation—and let me retrieve or export it later."
- **useful because:** Today the owner can save a file or make a note, but cannot reliably bind a browser transaction, downloaded receipt, and contemporaneous spoken context into one verifiable record. This would make returns, reimbursements, warranties, and disputes survivable without trusting memory or a screenshot.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Realtime only captures the owner's short annotation; a cheaper background worker assembles hashes and metadata. Use mac-vision only when structured browser/file evidence is unavailable.
- **latency:** Acknowledge capture in under 2 s; assemble the bundle within 10 s; export can take longer but must show progress and never imply completeness before verification.
- **cost:** About $0.01–$0.08 per bundle, dominated by optional vision/OCR; storage is bounded by owner-selected artifacts and hash-chain metadata.
- **security:** Bundles are private by default and encrypted at rest. Do not upload full page contents or secrets to the pendant; redact credentials, payment details, and unrelated tabs. Store hashes and provenance alongside artifacts, detect later file replacement, and require explicit confirmation before sharing or emailing an export.
- **missing:** An evidence-bundle schema with artifact hashes, source/session provenance, capture time, redaction status, and voice-note ID; Browser and Mac adapters that can atomically associate a downloaded file with its source page and transaction state; Encrypted retention, search, and export controls with an owner-configurable expiry

### "For the next two hours, watch this logged-in page or Mac condition and alert me on the pendant only when it changes in the way I described; show me the evidence and stop watching automatically at the deadline."
- **useful because:** The owner cannot currently delegate a bounded, condition-based watch across a browser session and Mac without leaving a window open or repeatedly checking it. This would cover price drops, an appointment opening, a build finishing, or a reply arriving while preserving a strict end time.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Use a cheap scheduled/background monitor for structured state and escalate to mac-vision only on a candidate change. Realtime is reserved for the initial spoken rule and the alert conversation.
- **latency:** Initial setup under 5 s; polling cadence chosen by site/risk and bounded by resource policy; alert within one polling interval. Hard-stop at expiry even if the source is unreachable.
- **cost:** Roughly $0.01–$0.20 per watch depending on duration and vision fallbacks; structured polling should dominate and avoid model calls when unchanged.
- **security:** Watch only an explicitly named origin/app and selector; never general-web crawl or infer from unrelated private tabs. Persist no page secrets. Treat logout, origin change, session replacement, or ambiguous visual change as unknown and stop. Alerts include a minimal evidence snippet/hash and a link to the source, not copied sensitive content.
- **missing:** A bounded watch-job scheduler with expiry, cadence, retry budget, and cancellation; Typed browser/Mac predicates and a change-diff record that can be independently verified; Pendant alert delivery and deduplication tied to the existing outcome/status beacon without turning an alert into authorization


## Changes it proposed to its own stack

### `memory` — Add an owner-controlled provenance graph that links a pendant utterance, relay interpretation, browser/Mac observations, executed receipts, and independently verified postconditions into an append-only chain. Expose a plain-language timeline and allow the owner to delete payloads while retaining only non-reversible audit hashes when they choose.
- **owner gets:** The owner would be able to answer “what did you hear, what did you see, what did you do, and how do you know?” after a long-running task—without trusting an opaque assistant history or retaining every private transcript forever.
- effort: High: define event IDs and causal links across relay, Mac, browser, and verifier; persist encrypted metadata; build deletion/redaction semantics and a compact dashboard timeline. It must integrate existing ledgers rather than create a second action log.  ·  risk: Incorrect links could make unrelated evidence appear connected, and deletion could break later explanations. Recover with explicit unknown links, immutable event IDs, provenance confidence, and a two-stage delete that clearly distinguishes payload removal from retained hashes.
- cost: Low per-event API cost; storage and indexing grow with action volume but can be bounded by retention policy. No new hardware cost.  ·  latency: Near-zero on the critical action path if events are appended asynchronously; verification and timeline assembly may take seconds.
- security: Highly sensitive metadata: encrypt at rest, minimize cross-surface content, keep page secrets and raw audio out of the graph, and require owner confirmation for exports. Hashes must not be treated as proof of content availability after deletion.
- depends on: A canonical event-envelope schema shared by relay, Mac, browser, and faculty-perception; Existing action ledger, job receipts, journal, and verify_operation_step integration; Owner-configurable retention and deletion policy


## What it asked for

_Nothing._
## Its own summary

Recorded three non-duplicate capabilities: interruption-safe cross-surface checkpoints and later restoration; freshness-bound execution that invalidates stale Mac/browser approvals; and deadline-based delivery from Mac/browser to the owner's real iPhone with verified postconditions. The motion/haptics firmware proposal was correctly rejected as already covered by the pending motion_context_safety_gate, so I did not re-propose it. I still need typed checkpoint/lease/delivery schemas, a restore/reconciliation orchestrator, reliable iPhone Mirroring adapters plus iOS delivery verification, and owner policy for what private drafts may be checkpointed or sent. I asked mac-planner to report the current iOS surface rather than assuming it exists.

**Biggest unknown:** Whether the current iOS Mirroring adapter can expose structured destination state and postconditions, or only perform clicks; without that, delivery can be staged but must truthfully end as unknown rather than delivered.

