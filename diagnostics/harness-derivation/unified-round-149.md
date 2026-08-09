# Harness derivation — unified — round 149

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Prepare that email/form/action, show me exactly what will happen, and let me approve it with the pendant—then tell me whether it really completed.”"
- **useful because:** This closes the system’s most dangerous silent gap: the code can classify and stage risky actions and the pendant approval latch exists, but the relay approval contract is schema-only and the spoken approval loop currently cannot complete. The owner gets a physical consent boundary plus a truthful completion receipt.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Planner tier to draft and summarize the action; deterministic approval, digest/world checks, nonce verification, and completion receipts; realtime only to speak the concise readback.
- **latency:** Stage and speak a preview within 3 s. Physical approval should be accepted within 1 s of reconnect. Completion receipt within 10 s, or explicitly remain pending.
- **cost:** <$0.03 typical invocation; planner tokens dominate. No extra model call for approval or evidence verification.
- **security:** Persist the existing plan digest, world fingerprint, expiry, confirm word, deliveredAt, and replay state in the relay—not browser page contents or form secrets. Require the pendant nonce and monotonic counter; refuse changed-world, expired, already-decided, or not-delivered approvals. Separate approval authority from execution credentials before treating this as a strong security boundary.
- **missing:** Production implementation of shared/approvalHandoff.js APPROVAL_STORE_CONTRACT; A delivery path that can speak the preview on the next conversation and set deliveredAt; A relay-to-Mac approval event and nonce verifier; A dashboard/voice status path for awaiting, approved, refused, and completed

### "“Run a quiet check before I rely on the pendant, and tell me whether my voice will be captured, delivered, and heard end to end.”"
- **useful because:** A healthy relay or successful WAV is not proof that sound reached the bridge or speaker. This gives the owner a single, measurable preflight result across the already-shipped 24 kHz path, USB hardware available now, and the actual delivery acknowledgement boundary.
- **path:** pendant → relay → mac-terminal → mac-planner
- **model tier:** Deterministic fixture and threshold evaluator; background model only if the owner asks for a natural-language explanation.
- **latency:** Under 8 s for the full duplex fixture; never run automatically during a live conversation.
- **cost:** <$0.005, primarily device/relay I/O; no model cost for HEALTHY/DEGRADED/FAILED.
- **security:** Use synthetic audio only, with no microphone recording and no SD writes. Return counters, hashes, and thresholds—not captured speech. Require explicit owner invocation.
- **missing:** A production trigger/route that invokes the existing fixture over USB or LTE; Bridge acknowledgement correlation through physical playback start/finish; A compact owner-facing verdict mapped to the 24 kHz acceptance thresholds

### "“Show me every piece of my conversation or action data you still hold, grouped by where it lives and when it expires; let me delete selected items across the pendant, relay, Mac, and browser.”"
- **useful because:** The owner cannot currently answer the basic privacy question—what survives a failed upload, a relay job, a browser inspection, or a Mac receipt—and the pending retention-policy question should become an explicit user-controlled operation rather than an invisible default. It is especially valuable because the pendant has an SD failure buffer and the Mac/relay have durable job and receipt stores.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Deterministic inventory, retention, and deletion executor; background model only to summarize categories in plain language. Never let a model decide deletion scope.
- **latency:** Inventory under 5 s; deletion receipt under 10 s per surface. If a surface is offline, show pending deletion and retry rather than claiming success.
- **cost:** <$0.01, dominated by cross-surface reads and receipt writes; no model cost for the core operation.
- **security:** Require an explicit physical or spoken confirmation per deletion batch. Redact audio contents and secrets from the inventory; show type, size, age, location, hash, and retention reason. Use tombstones and authenticated receipts so an offline pendant deletion cannot silently reappear when it reconnects. Never delete evidence needed to prove a safety or financial action without a second, clearly labeled confirmation.
- **missing:** A typed cross-surface data inventory contract with retention/expiry metadata; A deletion/tombstone protocol for the pendant OUTBOX/INBOX and relay stores; Mac and browser deletion handlers with per-item receipts; An owner-configurable retention policy, since none is established yet

### "“Stop every action you started—browser submissions, Mac jobs, and queued relay work—right now, and tell me which ones were actually stopped versus already irreversible.”"
- **useful because:** The pendant’s privacy latch can stop capture and playback, but it cannot currently halt actions already dispatched to the Mac, browser, or relay. A physical global stop would give the owner a meaningful emergency brake when an automation behaves unexpectedly, instead of merely silencing the wearable while the outside-world action continues.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Deterministic cancellation/fencing and receipt reconciliation; realtime model only to explain the compact result aloud.
- **latency:** Fence new work within 300 ms of the pendant event; send cancellation requests to reachable surfaces within 2 s. Never claim an irreversible external action was undone.
- **cost:** <$0.01 per invocation; state transitions and receipts dominate, with no model call required for the decision.
- **security:** The event must carry a monotonic physical-stop counter and device authentication. Relay and Mac must reject commands older than the stop fence, while already-started actions report an honest cancellation race. Require a second deliberate local gesture to clear the stop state; do not let a browser page or model clear it. Preserve minimal audit receipts without retaining page contents or audio.
- **missing:** A pendant stop/fence event distinct from local_privacy_latch; A relay-wide cancellation fence covering queued and processing jobs; Mac and browser executors that check the fence before each action and return cancellation receipts; A reconciliation record for actions that crossed the fence before it arrived; A safe local-clear ceremony and boot persistence policy

### "“Let me set a daily limit for each kind of automation—messages, purchases, file changes, and browser submissions—and refuse anything that would exceed it, with a running total I can inspect from the pendant.”"
- **useful because:** Current risk classification decides whether an individual action needs approval, but it does not protect the owner from a loop of individually acceptable actions or an automation that repeats across jobs. A physical-device-visible budget is a practical guard against aggregate harm and surprise cost.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Deterministic policy and accounting; planner/realtime models may propose actions but cannot alter budgets or bypass refusals.
- **latency:** Budget check under 50 ms before dispatch; usage receipt within 2 s. No model invocation on the hot path.
- **cost:** Negligible relay KV/SQLite storage and <$0.001 per check; no token cost.
- **security:** Budgets must be signed/configured by an authenticated owner operation and mirrored to the pendant so offline behavior is conservative. Count accepted, attempted, and externally confirmed actions separately. Fail closed when accounting is unavailable; prevent clock rollback and replay with monotonic counters. Never expose message content in the totals.
- **missing:** A typed action taxonomy shared by actionRisk, browser, and relay jobs; An atomic per-owner budget ledger with reset windows and idempotent charge keys; Pre-dispatch enforcement in both Mac and browser executors; A pendant readout and offline cache of remaining budget; Owner-facing setup and an explicit physical confirmation for raising a limit

### "“For the next hour, let this one task finish on this one browser tab, but do not let it touch anything else; show me the scope and revoke it from the pendant if I change my mind.”"
- **useful because:** One approval per action is cumbersome for a bounded multi-step task, while a broad AGENT_TOKEN is dangerously overpowered. A short-lived, physically authorized delegation would let the owner approve useful workflows without granting the automation unrestricted access to every Mac app or browser session.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Deterministic capability-token issuance, scope matching, expiry, and revocation; planner model may construct a plan but cannot broaden the token.
- **latency:** Issue the scoped grant within 2 s after physical approval; each action authorization under 20 ms; revocation fence under 300 ms when connected.
- **cost:** <$0.01 per delegation, mostly durable relay and Mac/browser receipt writes; no recurring model cost.
- **security:** Use an unguessable, device-approved token bound to owner, job, exact tab/session pattern, action types, resource paths, max count, expiry, and plan digest. Enforce deny-by-default on scope mismatch and stale world state. Do not put secrets or page contents in the token. Revocation must be monotonic and fail closed during link loss.
- **missing:** A capability-token verifier in Mac and browser executors; A relay-issued scoped grant record and revocation fence; A pendant UI/state for active grant, expiry, and revoke; A policy for whether world changes invalidate the grant; A separate approval credential from the broad execution bearer token


## Changes it proposed to its own stack

### `relay` — Implement the approvalHandoff relay half as a durable, expiring state machine: persist the prepared record and bounded index, deliver the redacted readback on the owner's next conversation, set deliveredAt only after playback acknowledgement, accept exactly one physical_transaction_approval_latch nonce, and publish the resulting approved/refused/completed state to Mac/browser. Add a lease and CAS around approval consumption.
- **owner gets:** The owner can finally approve a dangerous browser or Mac action from the pendant and receive an honest result instead of hearing “waiting for approval” while the action is discarded.
- effort: Medium-high: relay schema/store, next-conversation delivery integration, event verification, and end-to-end tests across USB today and LTE later.  ·  risk: A bug could execute an action twice or accept a stale approval. Mitigate with plan/world digests, expiry, nonce+counter replay checks, one-shot state transitions, and refusal by default on missing delivery or changed world. Recover by leaving the action pending, never guessing.
- cost: Low storage (bounded approval records and index); <$0.01 per staged action in relay I/O, no additional model call.  ·  latency: Adds up to one conversation boundary for delivery and normally <1 s for approval verification; no cost on ordinary safe actions.
- security: Improves the physical consent boundary, but does not become true privilege separation until approval and execution credentials differ. Redacts page contents and secrets from relay state.
- depends on: physical_transaction_approval_latch firmware behavior; A next-conversation pendant delivery event; An authorization separation between /approve and /execute; Orchestrator closeLedger integration so stale plans are not offered for approval


## What it asked for

_Nothing._
## Its own summary

This round recorded three new owner-facing capabilities: (1) a durable physical-approval-to-completion loop for staged Mac/browser actions, (2) an explicit cross-surface data inventory and selective deletion flow, and (3) a quiet synthetic end-to-end audio preflight with a truthful HEALTHY/DEGRADED/FAILED verdict. I also recorded the concrete relay change needed to make the existing pendant approval latch actually work. The proposed USB/LTE conversation handoff was rejected as an existing capability, so I did not rephrase it.

**Biggest unknown:** The owner’s retention/deletion policy is still unanswered, and it materially determines the deletion capability’s defaults. Technically, the other blockers are whether a next-conversation delivery event can set approval deliveredAt, whether bridge playback acknowledgements are wired end to end, and LTE registration (USB is real and testable now; LTE assumptions remain false).

