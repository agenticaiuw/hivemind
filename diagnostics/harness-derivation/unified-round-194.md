# Harness derivation — unified — round 194

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I didn't hear that—play your last answer again exactly, and tell me whether it actually reached the speaker.”"
- **useful because:** A dropped or interrupted response should be recoverable without making the owner repeat the question or receiving a different regenerated answer. The pendant is the only node that can truthfully distinguish relay acceptance, bridge receipt, playback start, and playback completion.
- **path:** pendant → relay → mac-planner
- **model tier:** deterministic for artifact selection and receipt interpretation; realtime only for the short spoken status
- **latency:** Under 300 ms to select and begin replay once the button/utterance is recognized; no new model round-trip for the audio itself.
- **cost:** Near-zero incremental inference; storage is a bounded reference to the last response and its delivery events, not raw audio on the pendant. Dominant cost is one relay receipt read.
- **security:** Replay only the exact artifact bound to the current conversation and owner session; never infer the last answer from unrelated jobs. Expire references after a short retention window and honor the privacy latch. Require confirmation before replaying sensitive content if the receipt marks it sensitive.
- **missing:** A production action that asks the relay for the last playable response artifact by conversation/turn ID; An executor that retransmits the same artifact after a failed or interrupted playback receipt; A pendant-facing spoken/button trigger wired to the existing delivery acknowledgement records

### "“Move this task to my browser and finish it there; tell me exactly what changed.”"
- **useful because:** This makes the hive meaningfully more than a voice wrapper: the pendant can hand an intent to the Mac, the browser can use the owner's already-authenticated session, and the result comes back as a bounded artifact with a spoken summary. It avoids asking the owner to restate context or expose credentials to the relay.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** background/planner model for decomposing the handoff and interpreting the result; deterministic policy layer for target-tab binding, risk classification, and completion receipts.
- **latency:** Acknowledge handoff in under 1 s; allow 10–60 s for browser work, with progress available by voice. Never hold the realtime audio loop open while the browser works.
- **cost:** One planner invocation plus existing browser/Mac action calls; dominant cost is browser task execution, not inference. No continuous vision unless the target site requires it.
- **security:** Bind execution to an explicit tab/session URL pattern and least-privilege action plan. Preview irreversible or external-submit actions and require the physical_transaction_approval_latch nonce. Return only a redacted result summary; never send page secrets through the relay.
- **missing:** A first-class handoff envelope carrying conversation turn, intent, browser target, and return address; A durable result artifact that joins browser command receipts to the originating voice turn; An owner-facing progress/timeout path when the browser tab disappears

### "“Before I ask you to do anything, is the whole system ready right now—and what part would fail if I tried?”"
- **useful because:** The owner currently has to discover outages by issuing a task that times out. A spoken preflight gives a truthful, cross-surface readiness answer and routes around a missing pendant, offline browser, stale lease, or degraded audio before work is attempted.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** deterministic health aggregation and policy; background model only to phrase the ranked explanation in plain language.
- **latency:** Under 500 ms from the voice request, using cached health with freshness timestamps; probe only the stale surface and cap the response at 2 s.
- **cost:** Near-zero model cost; a few authenticated health/status reads dominate. No browser page contents or audio need leave the device.
- **security:** Expose only capability and freshness, not URLs, tokens, page data, or detailed host inventory. Treat stale as unknown rather than healthy. Never auto-repair or launch an action from a preflight; offer repair separately with confirmation.
- **missing:** A correlated readiness snapshot with per-surface freshness and dependency edges; A policy mapping readiness states to safe alternatives (for example, queue rather than submit); A concise owner-facing voice response and optional diagnostics receipt

### "“For this website, never send, purchase, delete, or publish anything unless you read back the exact target and I explicitly confirm; remember that rule.”"
- **useful because:** The owner should be able to establish a durable behavioral boundary once instead of relying on the model to notice risk on every task. The rule travels with the authenticated browser session and applies even when a later request is vague or comes from a different model tier.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Deterministic policy engine evaluates every planned action; a cheaper background model may help translate the owner's natural-language rule into a reviewed policy, but cannot weaken or bypass it.
- **latency:** Policy lookup adds under 20 ms per action; confirmation readback should happen before dispatch. Rule creation can take one conversational turn and must produce a compact spoken summary.
- **cost:** Negligible per-action inference; one policy-compilation call when the owner creates or edits a rule. Storage is bounded metadata keyed to a site/session pattern, not page contents.
- **security:** Rules need explicit scope, version, expiry, and deny-by-default conflict resolution. The owner must be able to list, test, disable, and delete them. A rule must survive relay/Mac restarts and be included in action receipts so an execution cannot claim it was unaware.
- **missing:** A durable owner policy store and evaluator shared by browser and Mac planners; A pre-dispatch hook that can veto POST /execute and browser commands regardless of model output; A voice-readable policy management path and policy-version receipt field

### "“Put this work in a named project mode: keep its browser tabs, Mac files, pending actions, and spoken context together, and switch back to my other work without mixing them.”"
- **useful because:** The owner’s work is currently split across conversation sessions, active-project state, browser tabs, Mac jobs, and receipts. A project mode would prevent accidental cross-project actions and let the pendant resume the right context without pretending all open tabs and memories belong to one task.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Deterministic binding and isolation; background model only summarizes a project’s state or resolves an explicit owner rename.
- **latency:** Switch in under 500 ms for local state; no model call required. A project summary can arrive within 2 s.
- **cost:** Small metadata records and existing session/job queries; low inference cost because switching is deterministic.
- **security:** Every action, browser target, receipt, and extracted context must carry a project binding. Refuse ambiguous cross-project references rather than guessing. Switching must not expose one project’s page contents or secrets in another project’s spoken summary.
- **missing:** A shared project binding on sessions, browser commands, jobs, receipts, and context-graph facts; A cross-surface switch/status endpoint with an explicit active-project token; A policy that blocks actions whose project binding is absent or conflicting


## Changes it proposed to its own stack

### `integration` — Close the physical_transaction_approval_latch loop end to end: when prepare/approve stages a plan, persist the approval record in the relay's durable store, deliver a compact spoken summary plus nonce-bound challenge during the next pendant conversation, accept exactly one signed physical approval/cancel event, re-evaluate plan digest/world fingerprint/expiry, and only then dispatch the original plan. Add a separate authorization boundary so approval cannot be substituted for the executor's bearer credential, and mark the ledger settled after dispatch.
- **owner gets:** A deliberate button press would become a real safety boundary for browser submissions, messages, deletes, and off-machine actions instead of a green LED whose approval event has nowhere to go. The owner gets an honest “approved and executed” or “expired/cancelled” result.
- effort: Medium-high: relay schema/store and delivery integration, pendant event verification, bridge orchestration, and tests for replay, expiry, world changes, and reconnects.  ·  risk: A bug could execute a stale or duplicate action. Recover by requiring nonce, plan digest, world fingerprint, monotonic counter, expiry, idempotency key, and physical cancel; default all mismatches to refusal. Fix orchestrator closeLedger before enabling any resume or approval recovery.
- cost: Small D1 metadata and a few relay reads/writes per staged action; no audio storage. Engineering cost is chiefly integration and adversarial testing.  ·  latency: Adds one conversational turn and typically 1–3 s after the physical decision before execution; no impact on ordinary read-only actions.
- security: Improves security only if approval persistence and execution authorization are separated; the current shared AGENT_TOKEN would otherwise let an approver execute directly. Keep page contents/form secrets off the pendant.
- depends on: Relay implementation of APPROVAL_STORE_CONTRACT; A pendant delivery path that can present a pending challenge on the next conversation; Signed physical approval/cancel event verification and replay counter; orchestrator closeLedger fix; A durable relay job lease/requeue policy

### `context` — Add a fail-closed provenance label to every owner-facing fact, browser result, Mac job, and spoken response: source surface, project binding, sensitivity class, and whether the value was observed, inferred, or model-generated. Make the label travel through relay handoffs and appear in receipts and the next-conversation summary.
- **owner gets:** When the system says “done” or remembers something, the owner can tell whether it came from a real browser/Mac observation or an inference, and which piece of work it belongs to. That prevents a plausible sentence from silently becoming a false fact or wrong-project action.
- effort: Medium: shared envelope/schema changes, propagation through planners and relay, and migration for old records.  ·  risk: Missing labels could block otherwise harmless responses during rollout. Recover by marking legacy data unknown and allowing read-only display while refusing mutation or memory extraction from unlabeled results.
- cost: Small metadata overhead per event and receipt; no meaningful model cost.  ·  latency: Negligible serialization overhead; deterministic checks add milliseconds.
- security: Improves least-privilege and auditability, but labels are not authorization by themselves. Enforce the provenance at dispatch and memory-ingest boundaries.
- depends on: A shared event envelope across relay, Mac, browser, and pendant; Project binding capability or equivalent explicit task identity; Existing GET /jobs/:jobId/receipts and context-graph ingestion paths


## What it asked for

_Nothing._
## Its own summary

Recorded three new cross-surface capabilities and one integration direction this round: exact last-answer replay with a truthful stop-point, voice-to-browser task handoff with bounded receipts, and spoken whole-system readiness preflight; plus wiring the already-accepted physical approval latch into prepare/relay/execute. The highest-value result is that a failed hearing event can be recovered without regenerating a different answer, while readiness prevents blind task timeouts.

**Biggest unknown:** The remaining blocker is implementation inventory, not product intent: whether the relay currently retains a replayable response artifact and whether approval/readiness records have any durable cross-surface store. To ship the proposals, I still need those routes or a small relay envelope/store, plus the pendant delivery path for next-conversation approval. USB is not a product transport and should not be used to fill this gap.

