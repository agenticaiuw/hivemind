# Harness derivation — unified — round 150

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Approve this staged action on the pendant, and only then carry it out; if I miss it, remind me next time I talk to you.""
- **useful because:** This is the missing trustworthy bridge from spoken intent to real-world action: the owner gets a physical, replay-resistant consent step instead of a spoken promise that a blocked plan will execute. It works while the Mac or browser is offline and never treats relay acceptance as consent.
- **path:** relay → pendant → mac-planner → browser-extension
- **model tier:** deterministic approval orchestration; use realtime only to explain the staged action and background for reconciliation
- **latency:** Stage receipt under 1 s; next-conversation delivery under 2 s when connected; physical approval event reflected in relay under 5 s over USB/LTE
- **cost:** <$0.01 per staged action; dominated by one small planner turn only when the requested action is ambiguous
- **security:** Relay stores only a digest, nonce, risk tier, expiry, and redacted summary—not page secrets. Approval must bind plan digest and world fingerprint, expire, reject replay, and require the pendant nonce. Sending mail, purchases, deletion, and off-machine actions remain confirmation-required.
- **missing:** Implement the shared approvalHandoff relay store contract and delivery receipts; Wire the accepted physical_transaction_approval_latch event into the relay and Mac executor; Fix orchestrator ledger closure and add a real relay job lease/requeue before any resume or approval replay; Expose a next-conversation pending-approval readback because the pendant cannot receive unsolicited speech

### ""Keep this conversation alive if the Mac, LTE link, or browser drops—switch to USB now and give me one short sentence when continuity is restored.""
- **useful because:** Today the physically connected pendant and audio bridge are usable even though LTE is unregistered, but a transport failure can split one turn into duplicated or lost audio. A sequence-preserving handoff makes the wearable feel like one continuous assistant rather than three fragile sessions.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** deterministic transport state machine; background model only summarizes a recovered gap
- **latency:** Detect failure within 500 ms; USB takeover at the next turn boundary within 100 ms; reconnect reconciliation within 3 s
- **cost:** Negligible model cost during steady state; <$0.01 only if a recovery summary is needed
- **security:** Transport tokens are scoped to one session and device; monotonic turn/frame counters prevent replay and duplicate playback. USB audio remains local to the Mac; relay receives only the same framed audio permitted by the active session. Never silently switch to a phone path.
- **missing:** Implement the already-accepted usb_fallback_audio_session firmware behavior on both nRF9160 and ESP32 bridge; Add a relay transport lease and explicit ownership handoff endpoint keyed by session and turn sequence; Make the Mac bridge publish USB serial health and bridge acknowledgements into pipeline events; Add a compact owner-visible continuity receipt and recovery summary

### ""Use my own timezone for personal times, the Mac timezone for Mac-local operations, and tell me when those disagree instead of guessing.""
- **useful because:** The system currently has an explicit conflict: owner memory says America/Chicago while Mac-resolved operations are authoritative in America/New_York. A provenance-aware time answer prevents missed reminders, wrong routine interpretation, and false claims about where the owner is.
- **path:** relay → mac-planner → pendant → browser-extension
- **model tier:** deterministic timezone provenance resolver; background model only phrases the conflict
- **latency:** Under 100 ms for normal conversion; surface a conflict in the same spoken response, never defer it
- **cost:** Near zero; timezone database lookup and policy evaluation only
- **security:** Do not infer physical location from IP, LTE, or Mac zone. Persist only the selected policy and provenance, not location history. Personal timezone remains an owner-controlled setting and must not silently overwrite Mac-local semantics.
- **missing:** A first-class owner timezone setting with explicit source and effective dates; A resolver API that labels every instant as owner-local, Mac-local, or zoneless; Routine and voice-note callers must pass temporal provenance through instead of accepting bare digits; One owner decision: confirm whether America/Chicago is still the personal timezone

### ""Fill out the form using my saved information, but do not send any private field values to the relay or model; show me exactly which fields were filled and let me approve submission from the pendant.""
- **useful because:** The owner can automate sensitive forms without exposing addresses, payment details, health data, or account identifiers to the cloud model. The browser performs secret-bearing operations locally, while the relay sees only a redacted field manifest and the pendant approves the final submission.
- **path:** browser-extension → relay → pendant → mac-planner
- **model tier:** deterministic browser-side field mapping and redaction; realtime model only interprets the owner’s request and explains the manifest
- **latency:** Field discovery and local fill under 2 s; redacted preview under 1 s; submission only after physical approval
- **cost:** <$0.01 per form; model cost is limited to intent interpretation, not page contents or secrets
- **security:** The browser must never send field values, screenshots, DOM text containing secrets, or autofill databases to the relay. Use origin-scoped capability tokens, field-type allowlists, redact-by-default manifests, one-time submission nonces, and a clear distinction between locally filled and actually submitted. Purchases, messages, and irreversible forms always require physical approval.
- **missing:** A browser-extension local-secret broker that returns only typed field metadata and hashes; A redacted form-diff protocol with origin, field labels, and sensitivity classes; A browser-side submit gate bound to the pendant transaction nonce; A browser receipt proving which fields were filled and whether submission occurred without including values

### ""Treat the pendant as my presence key: allow routine low-risk actions while I am physically connected, but require a fresh physical presence proof when it disconnects or a sensitive action starts.""
- **useful because:** This gives the owner useful hands-free continuity without making the bearer token or a stale browser session equivalent to the owner’s physical presence. USB-attached pendant, relay, Mac, and browser jointly establish a short-lived presence lease that collapses immediately on disconnect.
- **path:** pendant → mac-planner → browser-extension → relay → mac-vision
- **model tier:** deterministic cryptographic policy and lease evaluation; no expensive model call for authorization
- **latency:** Presence establishment under 300 ms; disconnect revocation under 1 s; sensitive-action challenge under 2 s
- **cost:** Near-zero model cost; small relay and browser state records dominate
- **security:** Do not use proximity alone as authorization for purchases, deletion, messages, or account changes. Bind leases to device identity, USB session, browser origin, and monotonic counters; rotate keys; fail closed on clock ambiguity and stale heartbeats; never transmit raw audio as proof. A presence lease is not approval.
- **missing:** A hardware-backed pendant identity/key or protected credential store; Mutual challenge-response between pendant, Mac bridge, relay, and browser extension; A revocable, origin-scoped presence-lease service distinct from the bearer AGENT_TOKEN; Executor policy that separates presence eligibility from action approval

### ""When I ask you to handle something across my Mac and browser, give me one tamper-evident timeline showing what was observed, what was changed, and what I still need to do—not three unrelated status pages.""
- **useful because:** The owner currently has separate pipeline, Mac job, browser command, and pendant evidence. A causally linked timeline would make multi-surface work auditable and understandable: observation, decision, action, physical confirmation, external effect, and remaining obligation are visibly distinct.
- **path:** relay → mac-planner → browser-extension → pendant
- **model tier:** deterministic event correlation and hash-chain construction; background model may summarize the finished timeline
- **latency:** Append each event under 100 ms; produce a short spoken status under 2 s; full timeline available asynchronously
- **cost:** <$0.01 per workflow; storage and hashing dominate, not inference
- **security:** Store hashes and redacted metadata by default, not page contents or audio. Bind events to session, command, ledger, and pendant counters; identify missing receipts rather than inferring success; make deletion/retention owner-configurable and preserve no hidden copy.
- **missing:** A shared event envelope with causal parent IDs across relay, Mac, browser, and pendant; Append-only hash chaining and receipt verification across the four surfaces; A joiner that correlates pipeline IDs, job IDs, browser command IDs, and pendant transaction counters; A user-facing timeline/readout that distinguishes observed, attempted, completed, and unverified


## What it asked for

_Nothing._
