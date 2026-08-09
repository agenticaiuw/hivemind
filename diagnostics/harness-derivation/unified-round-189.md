# Harness derivation — unified — round 189

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What needs my attention right now?” Give me one short spoken triage of only actionable items: pending physical approvals, queued pendant alerts, interrupted Mac/browser work, and commitments with missing evidence, ordered by expiry or consequence; let me say “do the first one,” “snooze it,” or “show me why.”"
- **useful because:** The owner currently has to know which subsystem to query and cannot distinguish an actually pending action from stale history. This makes the pendant a single attention surface while preserving the rule that it never silently acts: selection can stage work, but risky execution still uses the physical approval latch.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for periodic indexing and deterministic triage; realtime only for the brief spoken summary and selection
- **latency:** under 2 seconds for a cached summary; under 5 seconds after a refresh
- **cost:** roughly $0.005–$0.03 per refresh depending on whether commitment evidence needs model interpretation; deterministic pending counts dominate the cheap path
- **security:** Do not send page contents or secrets into the summary model. Bind evidence queries to explicit tabs/apps, redact identifiers in speech, and require the existing physical_transaction_approval_latch for off-machine or irreversible actions. Snooze and dismissal need receipts so they cannot erase audit history.
- **missing:** A typed aggregator over pending inbox/approval, interrupted work, and commitment evidence; A durable attention item schema with expiry, source binding, snooze state, and deduplication; A pendant command path that can select/stage an item on the next conversation without unprompted push; Dashboard controls for inspect, snooze, and dismiss

### "“Show me everything you inferred about me, where each item came from, and forget this one.” List extracted facts in language I can recognize, expose the originating evidence capsule and derived copies, and erase exactly the selected fact everywhere except the action audit trail; report off-machine deletion as requested-and-pending."
- **useful because:** The system currently remembers facts the owner did not explicitly create, yet there is no owner-facing inventory or precise erase control. This turns hidden memory into a governed, inspectable feature and respects the owner's distinction between forgetting a fact and deleting an action history.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** background for extraction normalization and duplicate/copy linkage; realtime for spoken listing, confirmation, and result
- **latency:** list in under 2 seconds from an index; erase receipt in under 5 seconds locally, with remote replication status explicit
- **cost:** $0.01–$0.08 per extraction/index update; listing and deletion are deterministic. Storage/index maintenance dominates rather than inference.
- **security:** Evidence may contain private audio/transcripts, so show bounded excerpts and provenance labels, never dump raw capsules by default. Require a clear spoken or physical confirmation before deletion, authenticate the owner session, preserve action/job history, and use cryptographic tombstones so an erased fact cannot be recreated by replay. Remote relay/R2 deletion must be an honest pending state, not a false success.
- **missing:** A first-class extracted-fact record with human label, confidence, evidence IDs, derived-copy IDs, created/last-seen timestamps, and retention state; A cascade tombstone operation spanning facts.json, context graph, relay D1/R2, and caches; Owner-facing list/search/detail/erase routes and a deletion receipt; A re-extraction guard that honors tombstones

### "“Recover the work that stopped when the Mac or browser went away.” Reconcile durable step receipts, leases, and world state; automatically continue only idempotent or additive steps, pause before unrepeatable or unknown steps, and tell me exactly what will happen before asking for the pendant approval when needed."
- **useful because:** A disconnected machine currently leaves the owner with stale jobs and no safe continuation path. This would make a long-running research, browser, or file task survive outages without ever replaying an email, purchase, message, or other unrepeatable action by accident.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic policy and receipt reconciliation first; background model only to explain ambiguous evidence in plain language
- **latency:** diagnosis under 3 seconds; resume decision under 1 second after receipts are available; execution remains task-dependent
- **cost:** Usually <$0.01 per recovery because ledger/receipt comparison is deterministic; model explanation adds about $0.01–$0.04.
- **security:** The resume gate must key on replaySafety, not reversibility: idempotent/additive may continue, unrepeatable/unknown must stop. Recheck plan digest, world fingerprint, approval TTL, and browser command lease. Never treat an open ledger as interrupted until orchestrator closure is fixed; preserve a complete recovery receipt.
- **missing:** Close-ledger calls for ordinary orchestrator completion so history is not falsely classified as interrupted; A relay_jobs lease_until and expiry/requeue sweep; A production caller for planResume/resumeLedger that executes only the returned safe set; A delivery path for pending approval on the owner's next conversation plus durable approval-store persistence; Stale inflight timeout and reconciliation rules

### "“Keep this under my budget” — before starting a task, show the expected model, browser, relay, and Mac costs, reserve that amount, and refuse or ask before crossing my daily/weekly limit. Afterward give me an actual usage receipt and let me reclaim unused reservations."
- **useful because:** The owner currently cannot set a hard spending boundary across model inference, web research, browser work, and queued background jobs. A single budget contract would make delegation predictable instead of requiring the owner to understand which surface or model tier is charging him.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic accounting and reservation; background model only estimates uncertain task cost; realtime only for the short spoken preflight
- **latency:** preflight in under 1 second for known task types, under 3 seconds when a research estimate is needed; settlement is asynchronous
- **cost:** The feature itself is mostly database arithmetic and costs cents or less per task; the dominant cost is the task being authorized, which is precisely what the reservation makes visible.
- **security:** Budget state must be authenticated and append-only enough to prevent a failed or duplicated job from hiding spend. Estimates must be labeled estimates, reservations must expire, and cloud execution must be blocked when no valid reservation exists. Do not infer a financial limit from conversation; require the owner to set it explicitly.
- **missing:** A durable owner budget policy with daily/weekly windows and currency; Per-route/model/provider metering for relay, browser, Mac, and background jobs; Atomic reservation and settlement records tied to job IDs and receipts; A deterministic cost ceiling for unknown browser or shell work; Dashboard and pendant controls for set, inspect, override, and revoke a budget


## Changes it proposed to its own stack

### `hardware` — Add a low-power coin vibration motor with a dedicated transistor/driver and a protected GPIO, while retaining the existing LED as a secondary indicator. Define three short, non-speech patterns for staged approval, privacy-latch transition, and unread alert; the firmware must keep the patterns local and must not use vibration for recording without an explicit owner policy.
- **owner gets:** The pendant can communicate silently in a pocket, in bright sunlight, or when the owner cannot look at its single LED. A vibration cue would make physical approval and privacy state unmistakable without forcing the owner to hear an interruption or inspect a screen.
- effort: Small hardware spin plus enclosure, current-limit, driver, firmware pattern table, and bench validation against radio/audio timing. Requires an actual prototype because the current nRF9160 DK is not a wearable product enclosure.  ·  risk: Extra current and mechanical noise may reduce battery life or be uncomfortable against skin. A failed driver must default to no vibration, never block audio or the privacy latch. Patterns must be distinguishable from accidental button feedback and covered by power-on/self-test.
- cost: Roughly $0.50–$2 in components and PCB area at prototype quantities; brief pulses are typically a few to tens of mA, but product battery and thermal figures are not established. No API cost.  ·  latency: Local feedback can begin within tens of milliseconds of the button/state event; no relay or model round trip.
- security: Improves consent and privacy-state observability but must not become a hidden approval channel. Approval remains a deliberate physical hold and signed nonce; vibration only reports state.
- depends on: A product battery/skin-contact decision from the owner; A final pendant PCB/enclosure rather than relying on the current DK; Firmware pattern arbitration with the existing LED, privacy latch, and physical transaction approval latch


## What it asked for

_Nothing._
## Its own summary

Round 189 produced three recorded capabilities. The highest-value one is a spoken cross-surface attention triage: “What needs my attention right now?” It unifies pending approvals, held pendant alerts, interrupted work, and commitment evidence, but stages rather than silently executes. I also recorded safe outage recovery keyed to replaySafety, with explicit prerequisites (ledger closure, relay leases, production resume caller, and approval delivery). The extracted-fact inventory/erase idea was recorded but the recorder flagged it as close to an existing backlog item, so I will not restate it further. Discovery confirms Safari is online with two tabs and the Mac bridge is online; the mobile device is offline.

**Biggest unknown:** I still need implementation, not another conceptual primitive: a typed attention-item aggregator and owner-facing controls; production wiring for the existing resume engine; and a durable fact-provenance/tombstone implementation if the owner chooses to pursue memory governance. I also need owner policy values for attention snooze/escalation and confirmation wording, but I will not invent them or re-request the already-denied Accessibility/Screen Recording grants.

