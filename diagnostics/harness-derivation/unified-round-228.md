# Harness derivation — unified — round 228

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Watch this logged-in page and, when the condition becomes true, prepare the action—but do not do it until I approve on the pendant.”"
- **useful because:** This turns the pendant into a safe, persistent escrow for tasks that depend on a private browser state: price drops, an appointment slot opening, a document becoming available, or a form reaching a review step. The owner does not need to keep a tab open mentally, yet nothing is submitted without a physical approval at the moment of truth.
- **path:** relay-realtime → browser-extension → mac-planner → pendant → dashboard
- **model tier:** background for condition polling and deterministic planning; realtime only to explain the staged action in the next conversation
- **latency:** Condition checks every 30–120 seconds; staging under 2 seconds after a change; approval response under 2 seconds when the pendant is linked
- **cost:** ~$0.001–$0.01 per check depending on whether a model is needed; most checks are browser snapshots and deterministic predicates, not model calls
- **security:** Bind the escrow to an explicit tab/session target, page fingerprint, action digest, expiry, and one-time physical transaction nonce. Never send page contents to the relay except the minimum redacted predicate evidence. Require confirmation for every off-machine or irreversible action; cancel on page/world drift.
- **missing:** A first-class condition watcher that persists a browser target and predicate; A relay implementation that carries staged approval state and expiry across reconnects; A browser-side redacted predicate evaluator and page-change receipt; A single owner-facing escrow list with cancel/expire controls

### "“At the end of the day, tell me only what this system learned about me today, show me the exact evidence for each fact, and let me forget any one of them.”"
- **useful because:** The system currently extracts facts into hidden stores that the owner cannot inspect. A daily, evidence-bound review makes memory useful without making silent surveillance permanent: every item is understandable, confidence-labelled, and individually erasable together with its derived copies and off-machine replicas.
- **path:** relay-realtime → mac-planner → pendant → dashboard → browser-extension
- **model tier:** background model for extraction and clustering; deterministic code for provenance, redaction, deletion propagation, and the spoken summary
- **latency:** Batch once daily in under 60 seconds; deletion acknowledgement within 5 seconds locally and reported as pending for relay replicas
- **cost:** ~$0.02–$0.10 per daily digest depending on transcript volume; storage and hash/index work dominate less than inference
- **security:** Only extract candidate facts from explicitly retained conversation data; attach source turn IDs, timestamps, and confidence. Show a short redacted quote rather than raw audio by default. Deletion must tombstone the fact, derived graph entities, evidence capsule, and relay copies, while preserving action audit history. Never infer the owner's physical timezone from the pendant.
- **missing:** A first-class fact inbox with provenance capsules and per-fact delete; A deletion transaction spanning facts.json, context graph, relay D1/R2, and cached projections; A daily review scheduler and owner-visible digest UI; A pendant interaction for ‘show next fact / forget this’ when the Mac is unavailable

### "“If my conversation is interrupted, keep the unsent answer and let me continue from the exact point I stopped—without replaying anything I already heard.”"
- **useful because:** A dropped link currently risks either losing the answer or repeating it. A cross-surface turn ledger would make interruption survivable: the owner hears each segment once, the relay knows what was accepted versus physically played, and the next connection resumes from the first unacknowledged audio boundary.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension
- **model tier:** realtime for the live turn; deterministic background worker for segment persistence, reconciliation, and retry
- **latency:** Record segment receipts inline with <100 ms overhead; reconcile after reconnect within 3 seconds; resume at the next 60 ms Opus boundary
- **cost:** <$0.01 per interrupted turn; metadata dominates, with no extra model call unless the owner asks for a summary of the lost segment
- **security:** Persist only encrypted segment hashes and short-lived transcript pointers by default. Bind every segment to conversation, turn, sequence, and codec profile; deduplicate on event ID. Privacy latch must cancel capture and playback and prevent queued segments from surfacing. Never treat relay acceptance as proof of playback.
- **missing:** A durable per-turn segment manifest joining relay receipts to pendant playback acknowledgements; Reconnect reconciliation that can discard already-heard segments and resume only gaps; A bounded encrypted pending-downlink store with expiry; A user-visible ‘resume / discard’ choice after a long outage

### "“Give me a bounded delegation window: handle routine messages and scheduling until 5 PM, but never contact anyone new, spend money, or cross this list of domains—and show me exactly what you did afterward.”"
- **useful because:** The owner could safely hand over a class of repetitive work for a few hours instead of approving every individual action or granting the agent unlimited authority. The pendant provides an immediate local kill switch; the relay enforces expiry and scope even when the Mac is unattended; the browser and Mac execute only actions inside the signed budget.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background/planner tier for classification and batching; deterministic policy enforcement for every action; realtime only for spoken setup, revocation, and urgent exceptions
- **latency:** Delegation activation under 3 seconds; each action checked under 100 ms before dispatch; end-of-window report within 30 seconds
- **cost:** ~$0.02–$0.20 per delegation window depending on message volume and model classification; browser/Mac work dominates model cost
- **security:** Use a signed, expiring capability token containing allowed apps/domains, action classes, recipient set, spend limit, data-handling rule, and max step count. Default deny on ambiguity, new recipient, attachment, external upload, or irreversible action. The pendant must revoke locally without relay reachability; every action gets a receipt and the final report cannot be edited by the executor.
- **missing:** A first-class temporary delegation policy and token evaluator; A relay-side revocation/expiry service that survives Mac restarts; A pre-dispatch policy hook for every browser and Mac action; A compact pendant status/revocation interaction and owner-readable action digest

### "“Before you send anything external, let me verify the actual recipient, exact text, attachments, and destination on the pendant—not a summary—and then prove what the service accepted.”"
- **useful because:** The owner could use the system for email, forms, purchases, and messages without trusting a model summary. The browser or Mac holds the private session and performs the send, while the pendant presents a compact, deterministic digest of the exact outbound bytes and a deliberate physical approval. A post-send receipt distinguishes attempted, accepted, and delivered states.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** deterministic for canonicalizing and hashing the outbound payload; realtime only to read or explain fields on request; background for post-send reconciliation
- **latency:** Digest generation under 500 ms; owner review under 15 seconds; acceptance receipt under 5 seconds after submit
- **cost:** <$0.01 per send for hashing and metadata; model cost is optional and only for a spoken explanation
- **security:** Never show a model-generated paraphrase as approval material. Canonicalize recipient IDs, URLs, body, attachments, and account identity, display a truncation-safe digest with expand-on-demand fields, and bind the physical approval nonce to that digest and page/world fingerprint. Redact secrets while preserving enough data to detect substitution. Refuse if content changes after approval.
- **missing:** A canonical outbound-payload serializer shared by browser and Mac executors; A pendant renderer/voice protocol for exact-field review and digest confirmation; A send-result adapter for service acceptance versus delivery evidence; A route-level preflight gate that prevents unapproved external writes

### "“When I say ‘this is private,’ make every surface converge immediately, tell me what was stopped, and later let me explicitly restore only the parts I choose.”"
- **useful because:** The owner would get a verifiable privacy mode rather than a single local mute: the pendant stops capture/playback, the relay stops accepting and forwarding audio, the Mac pauses queued work, the browser stops polling and exposure, and queued artifacts are classified as discarded, retained, or awaiting explicit restore. The owner can trust the result even while links are down because local enforcement happens first.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** deterministic state machine and receipts; no model call needed except optional natural-language explanation
- **latency:** Pendant mute and capture stop within one local audio frame; relay/Mac/browser convergence target under 2 seconds after connectivity; divergence remains visible rather than silently assumed
- **cost:** Negligible inference cost; bounded receipt/state storage under a few KB per latch transition
- **security:** Local latch is authoritative and fail-closed. Each surface reports an authenticated state transition with monotonic epoch; stale reconnects cannot re-enable capture. Do not erase audit history automatically. Pending raw audio must be explicitly classified, and off-machine deletion must be reported as requested/pending until confirmed.
- **missing:** A cross-surface privacy epoch and authenticated convergence protocol; Queue classification rules for in-flight audio, browser commands, and Mac jobs; A selective restore flow that cannot accidentally clear the pendant latch; A dashboard/talkback receipt that names every surface and its last observed state


## Changes it proposed to its own stack

### `hardware` — Add a low-power coin vibration motor (or linear resonant actuator) with a dedicated driver and a physically isolated mount, and reserve short coded haptic patterns for pending approval, privacy-latch transitions, unread inbox alerts, and playback-start acknowledgement. Keep the single LED as a secondary visual indicator and make haptics locally generated so they work with LTE, Mac, and relay disconnected.
- **owner gets:** The pendant currently asks one LED and one button to communicate recording, staged audio, unread alerts, errors, privacy state, and approval. A vibration pattern is private and perceivable in a pocket or dark room, so the owner can know that an action is waiting or that privacy is active without looking at the device or hearing a sound in public.
- effort: Moderate hardware revision plus a small firmware pattern scheduler; validate vibration coupling, skin comfort, and current draw on the real enclosure.  ·  risk: Added vibration can be distracting or ambiguous if patterns are too similar; a stuck driver could drain the battery. Use a hardware current limit, watchdog-off default, maximum pulse duration, and fall back to LED-only if the driver self-test fails.
- cost: Roughly $0.50–$3 in components and PCB/assembly impact; short pulses likely add tens of mW only while active, negligible average draw. Product battery and enclosure constraints are still owner decisions.  ·  latency: Local feedback within one button/audio event, independent of radio or relay latency.
- security: No new data leaves the pendant. Approval remains a signed physical transaction; haptics only signal state and never authorize by themselves.
- depends on: physical_transaction_approval_latch; local_privacy_latch; offline_alert_inbox; audio_delivery_ack_queue; Owner decision on enclosure, skin contact, and acceptable tactile intensity


## What it asked for

_Nothing._
## Its own summary

Discovered live surfaces (Safari online, Mac bridge online) and the granted tool inventory. Recorded four new proposals: condition-triggered browser task escrow with pendant approval, an evidence-bound daily inferred-fact review/erasure flow, exact-boundary interrupted conversation continuation, and a hardware haptic channel to make privacy/approval/alert state perceivable without the overloaded single LED. The recorder flagged each as somewhat close to existing backlog, so these should be treated as integrated extensions rather than duplicate mechanisms.

**Biggest unknown:** The owner-facing policy and product constraints still needed are: which browser conditions/actions are acceptable for delayed escrow; whether inferred facts should be reviewed daily or only on demand; how long interrupted audio may remain resumable; and acceptable haptic intensity, enclosure size, skin contact, and battery impact. Engineering gaps are the persistent condition watcher, cross-surface fact deletion transaction, per-turn playback reconciliation, and haptic hardware prototype.

