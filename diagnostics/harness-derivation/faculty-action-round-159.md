# Harness derivation — faculty-action — round 159

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **device inventory versus physical USB** — Live devices inventory currently reports Safari, home-macbook-bridge online, and cloudflare-contract-test mobile offline; it does not expose the physically connected nRF9160/ESP32 serial endpoints. Treat USB presence as hardware fact but not as an authenticated relay device session until a typed serial transport/identity probe exists.
  - evidence: discover(devices) returned only Safari on MacIntel, home-macbook-bridge, and cloudflare-contract-test; owner-provided hardware status says both chips are physically connected over USB.

## Capabilities it proposed

### "Undo the last thing you had me do."
- **useful because:** A mistaken send, edit, or browser change becomes recoverable by voice instead of requiring the owner to reconstruct the prior state. The system only offers undo when it has a recorded inverse and independently verifies the rollback.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for inverse planning; realtime only for the spoken request and concise confirmation
- **latency:** Under 2 seconds to report whether an inverse is available; under 10 seconds for a reversible rollback, with a physical confirmation for risky undo
- **cost:** Usually one cheap planning call plus executor/verifier calls; roughly $0.01–$0.05 depending on whether browser state must be inspected. Mac/browser execution dominates latency, not inference.
- **security:** Never invent an inverse. Store only action metadata and redacted before-state hashes unless the owner explicitly permits content capture. Undo of messages, purchases, or deletions must require the pendant approval latch and must report unknown if verification cannot establish the restored state.
- **missing:** A durable inverse-action record in the action ledger, including redacted before-state sufficient to construct an inverse; A typed undo route that dispatches inverse operations to Mac or browser and returns a job id; Verifier support for comparing restored state to the recorded pre-action digest

### "Only let this action happen if the pendant is physically present and connected."
- **useful because:** A stolen or unattended browser session cannot complete a staged action merely because the Mac is unlocked. The pendant becomes a presence-bound approval device: USB-attached operation works today, and the same contract can later use the authenticated LTE link.
- **path:** pendant → mac-bridge → relay → browser → dashboard
- **model tier:** No expensive model required for the gate; use deterministic relay policy and realtime only to explain a denial
- **latency:** Presence check and approval acknowledgement under 500 ms over USB; under 3 seconds over LTE
- **cost:** Negligible inference cost; implementation and serial transport are the dominant work. LTE fallback adds normal relay bandwidth costs only.
- **security:** The relay must bind a one-time nonce to the specific device identity, connection session, action digest, expiry, and monotonic counter. Never send secrets or page contents to the pendant. Deny on stale heartbeat, transport change, digest mismatch, or ambiguous disconnect; do not silently queue an approved action for later execution.
- **missing:** Authenticated USB serial protocol between the connected nRF9160 pendant and Mac bridge; Presence policy hook in the existing physical_transaction_approval_latch; Freshness/identity fields in the relay device session and audit receipt

### "Before you commit that change, tell me exactly what will change and let me approve the diff from the pendant."
- **useful because:** The owner gets a concrete, spoken preview of a browser form, calendar edit, file move, or message draft rather than approving an opaque action summary. This catches wrong recipients, dates, and fields while the session is still reversible.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Cheap background model to summarize a structured diff; realtime only for the short preview and approval exchange
- **latency:** Preview within 3 seconds for a live page or Mac app; approval remains pending until the owner makes the deliberate physical gesture
- **cost:** Typically $0.005–$0.03 for diff summarization plus Mac/browser calls; screenshots or large page content are the cost driver and should be avoided by default.
- **security:** Diff extraction must redact secrets and private fields, with field-level sensitivity labels. The pendant receives a concise summary and digest, never passwords or full page contents. If the state changes after preview, invalidate the digest and require a fresh preview and approval.
- **missing:** A structured before/after diff schema shared by Mac and browser executors; A prepare-only executor mode that mutates nothing but captures the proposed field/file/app changes; Digest invalidation when the target state changes between preview and commit

### "For the next 20 minutes, handle only the low-risk items in my inbox, tell me each result, and stop immediately if anything is ambiguous."
- **useful because:** The owner gets useful bounded autonomy instead of approving hundreds of repetitive actions one by one. A temporary, scope-limited campaign can operate across the logged-in browser and Mac while the pendant remains the physical stop/control surface; uncertainty or scope drift halts the campaign rather than guessing.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background model for item classification and batching; realtime only for campaign start/stop and exceptions
- **latency:** Begin within 3 seconds; process items continuously, with each result reported within 5 seconds and an immediate stop on a policy violation or lost pendant presence
- **cost:** Approximately $0.02–$0.10 per 20-minute campaign, dominated by page inspection and per-item verification; use a cheaper model for repetitive classification
- **security:** The lease must specify exact app/site, operation classes, maximum item count, expiry, and a no-escalation rule. Never include secrets in model context. Each mutation gets a precondition digest, independent postcondition verification, and an auditable receipt. A pendant stop gesture must revoke the lease locally and at the relay; disconnect, stale presence, or ambiguity fails closed.
- **missing:** A campaign/lease primitive that binds a bounded set of action classes and expiry to one physical approval without widening scope; Per-item policy and verification receipts with an atomic stop boundary; A pendant-visible campaign state and immediate local kill/stop transport over USB and later LTE


## Changes it proposed to its own stack

### `integration` — Add a local USB serial transport adapter that exposes the physically connected nRF9160 pendant and ESP32 audio bridge as a loopback device session to the Mac bridge, carrying only approval/status envelopes and health counters. Keep LTE registration optional: when the pendant is USB-attached, the Mac bridge can deliver pending transaction nonces and receive sw1 approval/cancel decisions without pretending the device is LTE-registered.
- **owner gets:** The owner can use the pendant as a real action key and status surface today while it is plugged into the Mac, rather than waiting for relay registration. Losing LTE would no longer make confirmation impossible, and the system would clearly say which transport carried each decision.
- effort: Medium: serial framing, device identity handshake, reconnect handling, and relay-session binding; no firmware flash should be assumed. Validate against the two live USB serial endpoints before enabling execution.  ·  risk: A spoofed serial device or stale reconnect could authorize the wrong action. Use challenge-response, monotonic counters, expiry, and fail-closed session invalidation. Recover by discarding the session and requiring a new physical approval; never replay buffered approvals.
- cost: Near-zero API cost; modest Mac CPU and serial bandwidth. Hardware already connected; no component purchase.  ·  latency: Adds roughly 10–100 ms locally; improves behavior when LTE is unavailable.
- security: Strengthens physical presence, but creates a new local trust boundary that must be authenticated and audited.
- depends on: physical_transaction_approval_latch; relay device-session identity and freshness fields; a concrete serial-port diagnostic/transport surface (the previously requested free-form diagnostic tool is still unavailable)


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities and one concrete integration change: (1) voice-triggered verified undo with inverse-action records, (2) presence-bound approval requiring the physically connected pendant, and (3) spoken structured before/after diffs before committing a Mac/browser change; plus USB serial transport for the currently connected nRF9160 and ESP32. The live device inventory still omits those USB endpoints, so I recorded that discrepancy and notified mac-terminal. I still need a typed, authenticated serial diagnostic/session surface with device identity, freshness, reconnect behavior, and approval/status counters; free-form shell diagnostics are not sufficient.

**Biggest unknown:** Whether the connected serial devices already expose a usable framing/protocol and stable identity, or whether firmware/bridge work is needed to create one. Until that is known, presence-bound execution must fail closed rather than claim the pendant approved anything.

