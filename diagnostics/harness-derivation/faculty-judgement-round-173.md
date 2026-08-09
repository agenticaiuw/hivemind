# Harness derivation — faculty-judgement — round 173

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Did you actually hear my last question, and did I hear your answer?""
- **useful because:** Today a server receipt can say an answer was generated while the owner still cannot tell whether audio downloaded, started, finished, was interrupted, or never reached the pendant. This gives one honest, source-linked answer instead of claiming success from generation alone. It is especially valuable now because the pendant is physically testable over USB even though it is not LTE-registered.
- **path:** pendant → relay → mac-planner
- **model tier:** Cheap deterministic reconciliation; use the realtime model only to phrase an anomalous result conversationally.
- **latency:** Under 500 ms when ACKs are present; up to 2 s while correlating the latest pipeline and Mac bridge records.
- **cost:** Near-zero model cost for normal cases; at most a few hundred tokens of realtime phrasing for an ambiguity. Engineering cost is artifact/session correlation and a durable event index.
- **security:** Expose only opaque artifact IDs, delivery states, byte counts, and timestamps; never replay transcript or audio. Reject unauthenticated device sessions and duplicate event IDs. Require no owner confirmation because this is read-only.
- **missing:** A stable join from pipeline artifact to the originating relay/Mac job and conversation turn (today the ID namespaces are disconnected).; A real durable reconciliation/read route over POST /pipeline/events data, including offline replay and duplicate suppression, rather than merely accepting events.; Pendant firmware wiring that emits authenticated downloaded/playback ACKs over the currently live USB serial path.

### ""For any personal answer, tell me what is observed, what is inferred, and what may be stale—without making me interrogate the system.""
- **useful because:** A confident wrong answer about a meeting, bill, reservation, or browser page is more damaging than a brief uncertainty. The system already captures evidence and sensitivity in scattered stores, but the owner has no compact epistemic view. This would make the assistant trustworthy in daily life: every consequential answer carries a short confidence/freshness/source explanation, and stale evidence is surfaced instead of silently reused.
- **path:** relay → mac-planner → browser-extension → pendant
- **model tier:** Cheap deterministic claim assembly and freshness checks; use the expensive realtime model only to summarize conflicts in natural speech.
- **latency:** Under 1 s for an existing claim; under 3 s when gathering fresh browser/Mac evidence.
- **cost:** Low: mostly local indexing and bounded source snippets; occasional 100–300 token realtime explanation. No raw source text needs to leave the Mac unless the configured policy permits it.
- **security:** Never treat the existing normal/sensitive/secret classifier as authorization. Preserve source sensitivity, redact secrets before speech, and show opaque source labels on the pendant. Claims that are stale, asserted, or ungrounded must not be eligible for external mutation without confirmation.
- **missing:** Mount and persist browserProvenance routes, then connect capsule IDs to derived memory facts so revocation reaches claims.; A unified claim projection joining evidence capsules, memory facts, action receipts, and current source timestamps; existing stores are separate.; An owner-configurable freshness policy by source and an explicit rule for how much provenance may be spoken aloud.

### ""Turn this page into the right action, but show me the source and make me approve the exact thing on the pendant first.""
- **useful because:** This is the safe bridge from authenticated browser knowledge to real-world action: the browser supplies the source, the Mac prepares a bounded draft, the relay explains the consequence, and the pendant supplies deliberate physical consent. The owner gets useful automation without trusting a model's silent interpretation or allowing a page read to become an unintended send/purchase/change.
- **path:** browser-extension → mac-planner → relay → pendant
- **model tier:** Cheap deterministic extraction, policy evaluation, and preview first; realtime model only for ambiguous intent or a concise spoken explanation.
- **latency:** Preview in 2–5 s; approval response under 1 s after the physical press; no mutation until the approval nonce and plan hash match.
- **cost:** Usually near-zero model cost for typed page fields and policy checks; 200–800 tokens only when interpretation is ambiguous. Mac/browser execution dominates time.
- **security:** The pendant must receive only a redacted summary, source label, plan hash, expiry, and risk class—not passwords, page bodies, or form secrets. Bind approval to the exact plan hash, origin, target, and expiry; fail closed on page drift or stale plans. Mutations and external sends always require the physical latch, while read-only extraction does not.
- **missing:** Wire browserProvenance/capsule source records into the prepare/approve ledger so the owner can inspect exactly what grounded the proposal.; Implement the documented relay-side APPROVAL_STORE_CONTRACT; today approval state is Mac-local and not durable across a link drop.; Add a browser/Mac plan recheck that compares origin, relevant fields, and page version immediately before execution, then consumes the one-time physical approval.; A compact pendant rendering for source + consequence + approve/cancel over the existing physical transaction approval latch.

### ""Forget everything you learned from this source, everywhere—and prove to me what was removed and what could not be removed.""
- **useful because:** Deleting a browser capture or memory fact today leaves copies in other stores: graph notes, derived facts, provenance, relay projections, and sometimes queued artifacts. The owner cannot honestly know whether a revoked source still influences future answers. This capability turns forgetting into a verifiable life operation: identify every descendant, revoke or delete it where possible, stop future reuse immediately, and return an explicit residue report instead of claiming total erasure.
- **path:** browser-extension → mac-planner → relay → pendant
- **model tier:** Deterministic graph traversal, tombstoning, and residue accounting; use the realtime model only to explain the result in plain language.
- **latency:** Initial quarantine under 1 s; complete local sweep within 5 s for normal stores; relay confirmation may be asynchronous and surfaced later through the pendant inbox.
- **cost:** Near-zero model cost. Storage and indexing work dominate; no source content needs to leave the Mac. A small durable tombstone and deletion certificate is retained rather than the deleted content.
- **security:** Match by authenticated source identity, capsule ID, origin, and derivation links—not by fuzzy text alone. Never speak deleted content back. Preserve only hashes, store names, timestamps, and failure reasons in the certificate. Quarantine affected claims before attempting deletion so they cannot influence an action during the sweep. Destructive deletion requires explicit confirmation unless the owner has separately configured automatic source revocation.
- **missing:** A provenance edge from every derived fact, graph entity, memory projection, and relay event back to its source capsule or source ID; current derived facts often have no capsule link.; One cross-store revocation coordinator covering captures, evidence capsules, memory facts, context graph, browser provenance, queued jobs/audio, and fleet-memory retractions.; Relay-side durable tombstones and a monotonic source-revocation epoch so offline Mac/browser/pendant records cannot resurrect revoked knowledge.; A read-only deletion certificate route that reports removed, quarantined, unreachable, and retained-hash records with retry status.


## What it asked for

_Nothing._
