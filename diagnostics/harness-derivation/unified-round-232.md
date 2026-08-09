# Harness derivation — unified — round 232

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What have you learned about me that I didn’t explicitly ask you to remember? Show me each source, and let me forget any one of them everywhere.”"
- **useful because:** This directly fixes the system’s most important memory defect: silently extracted facts are currently invisible to their subject. It gives the owner a recognisable review surface, an evidence capsule, and a deletion result that distinguishes local deletion from pending relay/R2 erasure. The pendant can announce only that review is waiting; the Mac dashboard shows the sensitive detail, and the owner can use the physical approval latch for the destructive erase.
- **path:** relay-realtime → mac-planner → browser-extension → pendant
- **model tier:** background for extraction and clustering; realtime only when the owner asks to review or erase
- **latency:** Initial inventory under 3 seconds from indexed facts; each item’s provenance under 1 second; deletion receipt under 2 seconds locally, with off-machine replicas explicitly marked pending
- **cost:** About $0.01–$0.05 per inventory refresh depending on transcript volume; deletion is mostly storage/network I/O, not model cost
- **security:** Never expose raw transcript/audio by default; show the minimum evidence span needed to recognise the fact. Bind erase to a fact ID and evidence hash, require explicit confirmation for destructive deletion, audit the erase request but not the erased fact contents, and never claim replicated deletion is complete until relay/R2 acknowledge it.
- **missing:** A first-class extracted-fact candidate store with evidence hashes and replica locations; A dashboard review/delete view wired to context-graph and facts.json; Relay/R2 tombstone propagation and acknowledgement; A pending-fact spoken notification that does not leak the fact over an untrusted link

### "“The Mac restarted. Continue the thing you were doing, but do not repeat anything that already happened; tell me what you skipped and what still needs me.”"
- **useful because:** Today a crashed run can be discovered only by ledger ID, ordinary ledgers are left open, relay jobs have no expiry lease, and browser lease sweeping is not running. This capability turns those facts into safe continuity: idempotent/additive steps may resume, unrepeatable or unknown steps stop for the owner, and every skipped/completed step is spoken and shown with its receipt.
- **path:** relay-realtime → mac-planner → browser-extension → pendant
- **model tier:** deterministic policy engine for replay decisions; background model only to explain the resulting plan in owner language
- **latency:** Recovery scan in under 2 seconds at Mac startup; no action is dispatched until the deterministic gate and, where required, physical approval complete
- **cost:** Negligible model cost for the gate; roughly $0.001–$0.01 for an optional explanation
- **security:** Never replay based on reversibility alone: allow only replaySafety idempotent/additive, require a fresh physical approval for riskTier irreversible-write/off-machine/uncontained, and block all later steps after an ask. Use leases and idempotency keys to prevent two Macs or a stale relay worker acting concurrently. Preserve the audit trail while redacting sensitive parameters.
- **missing:** orchestrator closeLedger on normal completion; relay_jobs lease_until and requeue sweep; startup caller for planResume/resumeLedger; browser bridge supervisor invocation; a next-conversation delivery path for pending approval rather than pretending the pendant can be interrupted

### "“For anything that sends a message, buys something, or changes an account, make me press the pendant button every time—show me exactly what is about to happen, and never silently downgrade if the pendant is offline.”"
- **useful because:** This gives the owner a durable, understandable safety boundary across browser and Mac actions instead of relying on each planner’s classification. The relay stages a digest, the browser/Mac executor refuses direct dispatch, and the pendant’s physical_transaction_approval_latch supplies one nonce-bound consent. If the pendant or relay is unavailable, the action remains queued or fails closed; it is never converted into ordinary approval because that is convenient.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** deterministic policy and digest matching; realtime only to explain the staged action in conversation
- **latency:** Stage and display the digest within 1 second; execution within 2 seconds after an approval event; offline state is immediate fail-closed
- **cost:** Near-zero model cost for policy matching and hashing; under $0.01 for an optional natural-language explanation
- **security:** Match policy by action type, destination origin/account, and exact plan digest—not by the model’s wording. Bind approval to expiry, nonce, replay counter, and world/plan fingerprints. Do not send page secrets to the pendant. Log approval and execution receipts, but redact message bodies and payment details from routine telemetry. Explicitly surface “approval unavailable” rather than offering a bypass.
- **missing:** A policy store editable by the owner (action classes, domains/accounts, always-confirm vs never-allow); A browser/Mac pre-dispatch interception point that cannot be bypassed by the generic executor; Relay persistence and delivery for staged approval frames; A distinct authorization credential or process so approval is not equivalent to the broad AGENT_TOKEN; An owner-visible pending approval control when the pendant is offline

### "“Months from now, prove exactly what this system changed, sent, or deleted—what I approved, what the browser showed, what the Mac executed, and whether the pendant actually acknowledged it—without retaining the private content itself.”"
- **useful because:** Current receipts are scattered by surface and are not a tamper-evident, owner-verifiable chain. This gives the owner durable accountability without turning the system into an audio or transcript archive: each consequential event is represented by a content hash, actor/surface, approval nonce, monotonic sequence, and outcome, while sensitive payloads remain redacted or local.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** deterministic hashing, signing, and chain verification; background model only to summarize a verified chain in plain language
- **latency:** Append a receipt synchronously before reporting success; verification under 1 second for a normal job and under 5 seconds for a year of compact receipts
- **cost:** Minimal compute and storage; approximately 1–4 KB per consequential event plus periodic relay replication
- **security:** Hashing must not be presented as deletion proof unless replica tombstones are also recorded. Keep bodies, page contents, and audio out of the chain by default. Protect the signing key from the Mac agent; include explicit unknown/unverified states when a surface failed to attest. The owner must be able to export and independently verify the chain.
- **missing:** A device-held signing key or secure monotonic anchor on the pendant; One canonical receipt envelope shared by relay, Mac, browser, and audio-delivery acknowledgements; Append-only relay storage with key rotation and export; Browser and Mac hooks that emit pre-effect and post-effect attestations rather than only final job status; An owner-facing verifier/export format

### "“Handle this logged-in website task, but do not show the model my passwords, payment details, private messages, or unrelated tabs; let me approve only the exact fields and action that leave the browser.”"
- **useful because:** Today browser automation is broad enough that a screenshot, page read, or tab listing can expose more than the task requires. A capability-level disclosure firewall would let the owner use logged-in sessions without making the model a general reader of their private browser. The browser performs extraction and redaction locally, the relay receives a minimal typed action record, and the pendant confirms the final sensitive write.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** deterministic browser-side policy and schema extraction; realtime model sees only the redacted task representation
- **latency:** Redaction and field classification under 300 ms per page; owner-visible staged action under 2 seconds
- **cost:** Minimal model cost when DOM schemas are known; occasional background classification under $0.01 per unfamiliar page
- **security:** Default-deny page regions and origins; never transmit raw screenshots or DOM when a structured field suffices. Treat hidden fields, clipboard, downloads, autofill, and cross-origin frames as sensitive. Bind the approved field values and destination to an exact digest, expire it quickly, and fail closed if the page changes. The extension must make the disclosure decision locally rather than trusting model instructions.
- **missing:** A browser-extension local disclosure policy engine with DOM-region labels; Typed redaction and structured extraction primitives in browser actions; A relay protocol carrying schemas/digests instead of page content; A visible owner review showing precisely which fields will be read or written; Per-origin policy storage and a safe reset/export mechanism

### "“For this sensitive task, keep the conversation and page data on my Mac—use the pendant only for audio controls and a yes/no confirmation, and prove nothing crossed the relay.”"
- **useful because:** The current architecture assumes relay visibility for the live model, but some owner tasks should be possible without sending private browser content off the Mac. A sealed local session would route transcription, planning, and browser inspection to a Mac-local model or approved local runtime, while the pendant carries only control events and minimal confirmation. The owner receives a verifiable boundary receipt rather than a promise.
- **path:** pendant → mac-planner → browser-extension → relay-realtime
- **model tier:** Mac-local model for sensitive content; deterministic relay policy and receipt verifier; no realtime relay inference for sealed sessions
- **latency:** Local response latency within 2–5 seconds depending on model; entering sealed mode and issuing its boundary receipt under 1 second
- **cost:** Local compute cost rather than per-request relay tokens; optional local model hardware/runtime is the dominant cost
- **security:** The boundary must include telemetry, crash logs, browser extension traffic, model downloads, and fallback behavior—not merely the main prompt. Fail closed if the local model is unavailable; never silently fall back to relay. Show the owner the exact surfaces allowed, retain only a redacted boundary receipt, and require explicit exit before normal relay mode resumes.
- **missing:** A Mac-local inference runtime and model-selection policy; Browser extension routing that guarantees page data stays local; Relay enforcement of a sealed-session token and traffic deny rule; Pendant-visible sealed-mode state and exit confirmation; A network-level audit proving no sensitive payload crossed the relay


## What it asked for

### `c24-2mny` (context) — owner's mandatory-confirmation policy for external actions
- why: The staged physical approval capability needs the owner’s actual boundary: which actions must always require a pendant press (sending messages, purchases, account/security changes, or additional categories), and whether any trusted destinations are exempt.
- would change: I will treat all proposed external writes as fail-closed by default, but will not encode exemptions or a permanent policy until the owner answers. With the answer, I can specify the policy schema and test cases rather than inventing a security boundary.

