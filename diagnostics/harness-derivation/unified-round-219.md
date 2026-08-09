# Harness derivation — unified — round 219

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live device inventory** — The live devices inventory currently exposes Safari on MacIntel (online), home-macbook-bridge (online), and cloudflare-contract-test (offline); it does not expose an LTE-registered pendant or ESP32 bridge as a network device.
  - evidence: discover(category=devices) in round 219

## Capabilities it proposed

### "“Before you act, show me the exact browser page, Mac file, and message you are about to touch, and let me approve that one package on the pendant.”"
- **useful because:** It makes the pendant a real cross-surface consent boundary instead of a spoken promise. The owner sees the concrete targets and approves a hash-bound package, preventing a changed tab, file, or recipient from silently inheriting consent.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic planner, target fingerprinting, and approval verification; use the expensive realtime model only to explain the proposed package in the owner's words.
- **latency:** Preview in 1–3 seconds; physical approval result applied within 2 seconds of link availability; expiry in 10 minutes.
- **cost:** <$0.01 per approval; hashing and world snapshots dominate, not inference.
- **security:** Never include page secrets or form values in the pendant payload. Bind plan digest, world fingerprint, recipient/path, expiry, and monotonic nonce; refuse on any target drift or replay. Keep approval authority separate from execution credentials when possible.
- **missing:** A relay implementation of the existing approval handoff contract; A delivery/readback path that can mark approval delivered; A dashboard preview joining browser and Mac target fingerprints; Privilege separation so approval cannot equal unrestricted execution

### "“When a conversation or job breaks, tell me exactly which side failed and what I can safely retry.”"
- **useful because:** Today relay acceptance, Mac completion, browser completion, and physical playback are separate facts. A single owner-facing incident answer would distinguish lost input, unexecuted action, unconfirmed browser result, and undelivered audio, then offer only replay-safe next steps.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic correlation and replay-safety classification; background model summarizes the evidence only after the facts are assembled.
- **latency:** Initial diagnosis under 3 seconds from cached receipts; deeper evidence under 10 seconds.
- **cost:** <$0.01 per diagnosis; reads and correlation dominate. No audio or browser page content leaves the device unless explicitly requested.
- **security:** Redact page contents and sensitive parameters; expose IDs, timestamps, hashes, and outcome classes. Never recommend retry for unrepeatable or unknown actions. Require physical approval for any proposed side-effecting retry.
- **missing:** A durable correlation ID spanning pipeline, relay job, Mac receipt, browser command, and pendant delivery; A typed retry recommendation endpoint using replaySafety rather than reversibility; A compact owner-facing failure vocabulary and cached incident timeline

### "“Before anything leaves this Mac, show me what data is going out, where it will land, and how long it will remain.”"
- **useful because:** The owner has a deletion policy but no view of the egress itself. A live, plain-language data-flow receipt would expose whether content is audio, transcript, extracted fact, browser form data, or diagnostics, and would make off-device retention an informed choice rather than a hidden side effect.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic taint labels, destination and retention lookup; background model only summarizes a complex receipt. No realtime inference needed.
- **latency:** Show the egress preview in under 1 second for known routes; block until the owner confirms when a new or sensitive class appears.
- **cost:** Near-zero model cost; hashes, labels, and destination metadata are cheap. The main cost is maintaining accurate route instrumentation.
- **security:** The preview itself must not reveal secrets. Use content-class labels and byte counts by default, with exact excerpts only after explicit request. Treat unknown data classes as sensitive and fail closed. Record the owner's decision without storing the payload.
- **missing:** Taint labels attached to pipeline audio/events, browser commands, extracted facts, and diagnostics; A destination/retention registry covering Mac, relay D1, R2, browser session, and microSD failure path; A preflight gate that can block unapproved sensitive egress without requiring Accessibility

### "“Fill out this form, but disclose the minimum information needed and show me every field you chose to omit or alter.”"
- **useful because:** Forms routinely request more personal data than the transaction requires. The owner should not have to understand each site's dark pattern or manually redact every field. This capability would negotiate a least-disclosure submission while preserving the owner's control over the final values.
- **path:** browser-extension → mac-planner → relay → pendant → dashboard
- **model tier:** Planner/background model determines field purpose and necessity from the page and task; deterministic policy enforces the owner's declared disclosure rules. Realtime is unnecessary.
- **latency:** Analyze a normal form in 2–5 seconds; present a review package before submission. Never submit automatically when necessity is uncertain.
- **cost:** About $0.01–$0.05 for a complex form analysis; browser inspection and policy evaluation dominate.
- **security:** Page contents and proposed values are sensitive. Keep raw values on the Mac/browser, send only field labels and classifications to the relay when possible, and require pendant approval for every newly encountered sensitive category. Never invent substitute identity data.
- **missing:** Field-purpose and necessity classifier with an uncertainty state; Owner-configurable disclosure policy (required, avoid, never, ask); Browser-side redaction/substitution preview and a tamper-evident submission receipt; A physical approval package that includes the target origin and final field digest

### "“Move this conversation from the pendant to my Mac without making me repeat myself, and tell me exactly what context you carried over.”"
- **useful because:** The pendant is best for capture and interruption, while the Mac is best for long work and authenticated browser tasks. The owner should be able to change surfaces at a natural turn boundary without losing the active goal, pending commitments, approvals, or conversational state—or accidentally duplicating an action.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic handoff manifest and deduplication; a background model compresses only the spoken context that must fit the destination, with sensitive content omitted unless needed.
- **latency:** Handoff package ready within 2 seconds at a turn boundary; destination acknowledgement within 5 seconds. No mid-utterance cutover.
- **cost:** <$0.01 for routine handoffs; background summarization is the main variable cost.
- **security:** Bind the handoff to a conversation and turn nonce, include only the minimum context, expire it quickly, and require the pendant latch/approval for any pending side effect. The Mac must not replay an already-dispatched action.
- **missing:** A first-class conversation handoff manifest with source/destination, turn sequence, pending side effects, and redaction decisions; Destination acknowledgement and exactly-once adoption semantics; A user-visible carried-context diff and an explicit handoff failure state; Surface routing policy that distinguishes capture, execution, and display ownership

### "“Revoke that browser session from the pendant right now, and prove that its queued commands, cookies, and pending jobs can no longer act.”"
- **useful because:** A browser session can remain authenticated while the owner is away from the Mac. Today the pendant's privacy latch stops local capture/playback but does not provide a targeted remote kill switch for a compromised or misplaced browser session. This gives the owner an immediate, physical, session-specific containment action.
- **path:** pendant → relay → browser-extension → mac-planner → dashboard
- **model tier:** Deterministic revocation and convergence verification; no model call is needed except optional natural-language explanation.
- **latency:** Issue the revocation locally in under 1 second; relay and browser acknowledgement within 5 seconds. If unreachable, retain the revocation until reconnect and report the unresolved surfaces.
- **cost:** Negligible API cost; small durable revocation record and browser heartbeat traffic.
- **security:** The pendant must emit a signed session/device nonce, not a browser secret. Revocation must invalidate command leases, cancel queued commands, rotate the browser bridge capability, and avoid claiming cookie invalidation unless the browser extension actually cleared it. Require a deliberate physical hold and show partial convergence honestly.
- **missing:** A pendant-targeted session revoke event and durable relay revocation list; Browser extension handling that invalidates its bridge token and clears or isolates session state; Mac job cancellation tied to the revoked session; A read-only convergence receipt covering browser, relay, Mac, and queued work


## Changes it proposed to its own stack

### `integration` — Add a typed egress ledger at every pipeline, browser-result, extracted-fact, and relay upload boundary. Each record carries source class, destination, retention class, byte count, content hash, consent/approval ID, and a redacted preview; unknown classes fail closed. Expose a joined preview before dispatch and a receipt after dispatch.
- **owner gets:** The owner can know, before speaking or acting, whether audio, transcript, browser data, or an inferred fact is leaving the Mac and where it will persist. It turns the existing deletion promise into an understandable privacy boundary.
- effort: Medium-high: instrument four producers, add a registry and join layer, then test redaction and failure-closed behavior.  ·  risk: Incorrect labels could falsely reassure or block useful work. Recover by marking uncertain data sensitive, preserving immutable hashes, and making the ledger append-only while allowing payload erasure separately.
- cost: Negligible storage and model cost; roughly one small metadata record per transfer. No routine audio copy is introduced.  ·  latency: <50 ms for local metadata; preview may add up to 1 second when destination policy must be fetched.
- security: Improves least privilege and auditability, but the egress ledger becomes sensitive metadata. Encrypt it, redact by default, and exclude raw payloads.
- depends on: A destination/retention registry; Stable correlation IDs across pipeline, relay, Mac, and browser; Owner-facing preview/confirmation surface


## What it asked for

_Nothing._
