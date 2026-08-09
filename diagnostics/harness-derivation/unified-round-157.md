# Harness derivation — unified — round 157

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “stage this purchase for me,” prepare the exact browser checkout, read back the merchant, amount, and destination, then let me approve it with the pendant’s physical hold; only after that approval should the browser submit, and tell me whether it completed."
- **useful because:** This is the single most valuable cross-surface trust boundary: the browser can reach authenticated checkout, the relay can persist an action-bound digest, and the worn device can provide consent without receiving credentials or page contents. It prevents the current dangerous gap where a blocked plan is merely spoken about and discarded.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** background for page extraction and risk summary; deterministic code for digest, amount/destination binding, expiry, and approval; realtime only for the short spoken readback
- **latency:** Stage preview under 5 s; spoken confirmation under 2 s; submission starts within 1 s of the physical approval receipt; receipt may take up to 10 s.
- **cost:** About $0.01–$0.05 per staged checkout, dominated by planner/page interpretation; deterministic approval and receipt work is negligible.
- **security:** Never send passwords, payment details, or page secrets to the pendant or model. Bind approval to tab/session, merchant, amount, destination, plan digest, world fingerprint, expiry, and nonce. Require confirmation before final submission and refuse on any page or amount change. Log redacted receipts only.
- **missing:** Relay implementation of APPROVAL_STORE_CONTRACT and delivery/readback path; Browser submit adapter that accepts the pendant nonce and revalidates the digest immediately before submit; A separate authorization boundary so approval cannot be used as an unrestricted /execute credential; Orchestrator closeLedger integration and relay job leases before resuming staged work

### "At the end of each day, give me one short spoken sentence containing only the unfinished commitments you can prove from my notes, mail, calendar, and bound browser tabs, and let me mark each one done or defer it from the pendant."
- **useful because:** It turns the existing commitment detector and evidence query into a reliable personal closeout instead of another generic summary: the owner hears only items with provenance, and every dismissal or deferral becomes explicit rather than silently disappearing.
- **path:** mac-planner → browser-extension → relay-realtime → pendant
- **model tier:** background model for candidate extraction and compression; deterministic evidence binding and state transitions; realtime only to speak the final sentence and accept a short disposition
- **latency:** Generate by the scheduled evening run in under 30 s; pendant response within 2 s of a button press; evidence refresh under 5 s.
- **cost:** Roughly $0.01–$0.04 per daily run, dominated by reading and compressing candidate evidence; disposition events are negligible.
- **security:** Search only explicitly bound apps/tabs and data since the commitment was made. Redact message bodies and secrets from relay logs. Do not infer completion from absence. A completion requires owner confirmation or a new evidence receipt; deferral must carry an expiry and remain local to the owner.
- **missing:** A durable commitment record with owner-confirmed done/deferred states and expiry; Pendant interaction mapping for cycling, done, and defer that does not collide with recording or the existing sw1 bookmark; A scheduled spoken-delivery path that can surface the sentence on the next conversation rather than assuming unprompted push

### "When the pendant is connected by USB but LTE is unavailable, let me have a normal conversation locally, then hand the session back to LTE at a turn boundary without repeating or losing audio; tell me in one sentence which transport carried each turn."
- **useful because:** The hardware is physically testable now even though the pendant is not LTE-registered. This makes the device useful today, while preserving standalone LTE behavior later, and prevents duplicated speech or a cut-off reply during handoff.
- **path:** pendant → mac-planner → relay-realtime → mac-vision
- **model tier:** deterministic transport/session state machine for ownership, sequence continuity, and handoff; realtime model for conversation only
- **latency:** USB capture-to-response should feel conversational, under 500 ms first-audio latency where the local Mac path permits; handoff waits for a turn boundary and completes under 1 s.
- **cost:** About $0.01–$0.08 per conversation turn depending on model audio usage; USB framing, deduplication, and handoff are negligible.
- **security:** Authenticate the USB peer before exposing microphone/audio. Keep monotonic session and turn counters, reject replayed frames, and make the transport status visible. Do not silently route audio through another machine without the owner’s configured policy. Persist only failure-buffer audio under the existing SD rule.
- **missing:** Mac-side USB serial transport adapter for /dev/cu.usbmodem00096003658* and ESP32 bridge coordination; Relay/session protocol that treats USB and LTE as mutually exclusive owners and switches only at turn boundaries; A transport policy setting (lte_only, usb_fallback, or phone_fallback) and an end-to-end test against the currently unregistered LTE state

### "When I ask “what happened, in what order?”, show me a short, tamper-evident timeline joining my pendant button events, USB/LTE transport changes, relay receipts, Mac jobs, and browser actions, with uncertainty called out instead of invented timestamps."
- **useful because:** Today each surface has fragments and different clocks; the owner cannot establish whether an action was captured, handed off, executed, or merely promised. A signed ordering record would make disputes and failures understandable without pretending the pendant has wall-clock time.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** deterministic event-chain verification and clock-offset handling; background model only to compress the verified chain into one spoken sentence
- **latency:** Query under 3 s for a normal session; longer histories stream as pages, never blocking the next conversation.
- **cost:** Under $0.01 per query; storage and signature verification dominate, not inference.
- **security:** Use opaque event IDs, monotonic counters, relay signatures, and redaction by default. Never expose page secrets or raw audio. Distinguish device order from Mac wall-clock order and report unsynchronized clocks explicitly.
- **missing:** A shared signed event-envelope schema across firmware, bridge, relay, Mac, and browser; A relay append-only event index with bounded retention and redacted projections; Clock-offset calibration records and a verifier that refuses to manufacture absolute device times; Owner-configurable retention/deletion policy

### "Let me say “find the thing I just saw” and have the system locate the matching page, file, note, or staged result across the bound browser tabs and my Mac, then read me the exact source and open it without changing anything."
- **useful because:** The owner repeatedly encounters information across browser and Mac surfaces but has no unified, provenance-preserving retrieval. This would turn the pendant into a reliable recall interface rather than requiring him to remember which machine held the artifact.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** background retrieval/reranking model over local metadata and user-authorized page/file indexes; deterministic source binding and read-only open action; realtime only for the spoken answer
- **latency:** First candidate under 4 s, with up to three source candidates; opening the selected source under 1 s.
- **cost:** About $0.01–$0.06 per search, dominated by embedding or reranking; indexing runs locally in the background.
- **security:** Search only explicitly bound tabs, apps, and workspace paths. Keep document contents on the Mac where possible; send hashes, titles, and minimal snippets to relay. Opening is read-only and must preserve tab/session affinity. Never search secrets unless the owner names the bound source.
- **missing:** A local unified metadata index for browser inspections, workspace files, notes, and job artifacts; Stable artifact IDs and content hashes that survive tab reloads and file moves; A typed read-only search route returning source, confidence, and exact binding; Owner retention/deletion policy for the index

### "When I say “run this privately,” keep the entire turn on the Mac and pendant, visibly prove that no relay, browser, or cloud action was used, and refuse if the requested task needs a remote session or an authenticated browser."
- **useful because:** The owner has a real privacy latch, but today there is no positive, per-turn proof of routing. A private mode should be a verifiable boundary for sensitive drafts, notes, and spoken thoughts—not a preference that can silently fall back to cloud when local execution fails.
- **path:** pendant → mac-planner → relay-realtime → browser-extension → dashboard
- **model tier:** Local Mac model or deterministic local processing for private turns; no realtime cloud model; deterministic policy enforcement and receipt generation
- **latency:** A local text answer under 3 s where the Mac model permits; refusal should be immediate when a required capability is remote.
- **cost:** Cloud API cost is zero for private turns; local model CPU and battery are the dominant cost.
- **security:** Enforce an egress-deny session token, disable relay persistence and browser actions, and emit a signed local receipt listing permitted surfaces. The receipt must contain metadata only, never private content. A network failure must fail closed, not switch modes.
- **missing:** A Mac-local model/runtime or deterministic private-task subset; A per-turn routing lease enforced by relay and Mac, not merely a prompt flag; Network-egress and browser-action denial hooks with auditable receipts; A clear owner policy for whether local model logs and crash dumps may retain content


## Changes it proposed to its own stack

### `relay` — Implement the approvalHandoff contract as a durable relay record: persist prepared plan digest, world fingerprint, nonce, expiry, confirm word, delivery state, and decision; expose a pending-approval selector on the next owner conversation and atomically consume exactly one pendant approval/cancel event. Refuse expired, changed, already-decided, or not-delivered records.
- **owner gets:** A staged action will stop vanishing after it says “waiting for approval”; the owner can approve the exact action from the next natural conversation and receive a real outcome.
- effort: Medium: D1 schema/index, read/write routes, relay-to-session selection, and integration tests for replay and expiry.  ·  risk: A relay bug could expose or misbind an approval. Mitigate with least-privilege records, redacted payloads, digest/world checks, atomic compare-and-set, and fail-closed refusal. Recover by leaving the staged action pending rather than executing.
- cost: Low storage and request cost; one small durable record per pending approval, bounded by TTL.  ·  latency: Adds tens of milliseconds to approval selection; no cost on ordinary turns.
- security: Improves security only if approval is a separate capability from /execute; do not reuse the AGENT_TOKEN as the authority boundary.
- depends on: A distinct approval authorization boundary; Pendant physical_transaction_approval_latch event ingestion; Orchestrator closeLedger call so stale completed plans are not treated as interrupted

### `browser-harness` — Add a final, read-only browser transaction revalidation immediately before any staged submit: verify bound tab/session, origin, merchant, amount, destination, and visible confirmation state; return a typed preSubmitReceipt with a fresh digest and refusal reason, and require the pendant nonce to match that digest.
- **owner gets:** The owner’s physical approval cannot be tricked into approving one page state while the browser submits another after a redirect, price change, or tab takeover.
- effort: Medium-high: adapter contracts for supported checkout shapes, DOM extraction tests, redirect/session binding, and fail-closed integration with the executor.  ·  risk: Sites vary and legitimate dynamic pages may refuse. Recovery is a spoken “page changed; review again,” never a blind retry. Do not use screenshots or model guesses as the sole proof.
- cost: Negligible API cost for deterministic checks; engineering cost is maintaining site-independent selectors and typed refusal cases.  ·  latency: Adds roughly 0.5–2 s before submit depending on browser round trip.
- security: Reduces confused-deputy and stale-approval risk; secrets remain in the browser and are never copied to relay or pendant.
- depends on: Durable approval handoff; Browser tab/session affinity and typed inspection results; Separate approval-vs-execution authorization

### `interaction` — Create a transport status envelope spoken at turn boundaries and recorded in the receipt: usb-local, lte, or handoff-pending, plus session/turn sequence and whether audio was captured, relayed, decoded, and physically played. Never switch transport mid-turn; on loss, finish or explicitly mark the turn interrupted.
- **owner gets:** When the pendant is USB-attached today and LTE is added later, the owner will know where the conversation ran and will not hear duplicated replies or wonder whether a sentence disappeared during unplugging.
- effort: Medium: shared state machine across firmware serial framing, Mac bridge, relay session, and receipt formatting; fault-injection coverage for unplug/reconnect at every phase.  ·  risk: A bad state transition could strand a session or duplicate a turn. Recover with a monotonic sequence, idempotent turn IDs, bounded timeout, and a clear local fallback; never replay audio automatically without a new turn.
- cost: Tiny metadata overhead; no model cost beyond one short status phrase when configured.  ·  latency: No hot-path delay except waiting for the current turn boundary; status phrase is deferred to the next natural pause.
- security: Makes routing observable and prevents silent third-party transport; policy must default to LTE-only or USB fallback explicitly, not guess.
- depends on: USB serial adapter for the live nRF9160 and ESP32 ports; A relay session owner/lease that can distinguish USB from LTE; usb_fallback_audio_session firmware behavior

### `context` — Introduce a signed cross-surface event envelope and verifier. Each pendant, bridge, relay, Mac job, and browser command emits an opaque event ID, predecessor ID, monotonic source counter, source-local time (if any), payload hash, redaction class, and signature; the relay stores only the bounded redacted chain and exposes verified projections, explicitly labeling gaps and unsynchronized clocks.
- **owner gets:** The owner can finally ask what happened and get an auditable answer about capture, handoff, execution, and playback instead of a plausible narrative assembled from unrelated logs.
- effort: High: firmware/bridge emitters, relay schema and append-only index, Mac/browser adapters, key rotation, projection queries, and fault-injection tests for loss, replay, fork, and clock skew.  ·  risk: A broken chain could falsely imply an action occurred or leak sensitive metadata. Fail closed on verification gaps, keep raw payloads off relay, bound retention, and provide a local export for forensic review.
- cost: Small storage and signature CPU cost per event; no recurring model cost for verification.  ·  latency: Asynchronous append; no conversation hot-path delay. A verified timeline query may take 1–3 seconds.
- security: Raises integrity and provenance substantially, but requires protected device keys and careful redaction; compromise of one source must not let it forge another source’s events.
- depends on: Owner retention/deletion policy; Per-surface signing keys and rotation; A relay append-only event index; Typed receipt adapters for Mac and browser actions


## What it asked for

_Nothing._
## Its own summary

Round 157 produced three owner-facing capabilities and three implementation changes. The highest-value proposal is a browser checkout staged on the Mac, bound to a durable relay approval record, physically approved on the pendant, and submitted only after final browser revalidation. I also proposed provenance-backed evening commitment closeout and a USB/LTE turn-boundary transport envelope, plus concrete relay, browser, and interaction changes. The live system has Safari online, the Mac bridge online, and the pendant/bridge are physically testable over USB despite LTE registration still being absent.

**Biggest unknown:** The owner’s personal timezone remains unresolved and conflicts with the Mac’s authoritative America/New_York resolution (owner memory says America/Chicago); do not silently substitute either for the other. Product privacy/retention policy is also still pending from an earlier context request. Engineering blockers are the durable approval relay/delivery loop, separate approval authorization, final browser pre-submit revalidation, and the USB serial transport adapter/session lease.

