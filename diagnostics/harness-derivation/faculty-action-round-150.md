# Harness derivation — faculty-action — round 150

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Before you carry out a sensitive action, make sure this pendant is physically beside my Mac and let me approve this exact Mac/browser session from the pendant.""
- **useful because:** It prevents a relay or stale browser session from treating a remote/replayed approval as the owner's intent. The pendant is USB-connected today, so this can be tested now without LTE.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → faculty-perception → faculty-action
- **model tier:** background for session binding and receipt checks; realtime only for the spoken confirmation
- **latency:** Presence proof under 300 ms; approval prompt under 1 s; execution receipt under 5 s
- **cost:** Low API cost: one short realtime turn and a few small relay events; dominated by browser/Mac execution, not model tokens.
- **security:** The pendant sends only a device-held nonce, session id hash, and monotonic counter—not page contents or secrets. Reject stale, replayed, disconnected, or session-mismatched proofs. Owner confirmation remains required for the action risk class.
- **missing:** A serial presence daemon that forwards signed challenge/response from /dev/cu.usbmodem00096003658* to the Mac agent; Binding physical_transaction_approval_latch envelopes to a specific Mac job and browser session; A relay policy rule that refuses execution when presence expires

### ""If an action partly ran or cannot be verified, tell me exactly what is uncertain and let me choose retry, undo, or leave it alone from the pendant—don't silently run it twice.""
- **useful because:** Real-world Mac/browser work often fails after a click but before a receipt. A recovery decision prevents duplicate messages, purchases, or edits while still making useful progress instead of abandoning the job.
- **path:** relay-realtime → pendant → faculty-perception → faculty-judgement → faculty-action → mac-planner → browser-extension
- **model tier:** background model for classifying recovery options and drafting a concise status; realtime only when the owner must choose
- **latency:** Surface uncertainty within 2 s of executor timeout; owner choice acknowledged under 1 s; retry/undo starts immediately
- **cost:** Low-to-moderate: one compact status turn only for ambiguous outcomes; most successful actions use no extra model call.
- **security:** Never offer undo unless perception has identified a concrete reversible inverse. Include job/step id, last verified state, and expiry. Retry requires a fresh idempotency key; irreversible or sensitive recovery is staged for the existing physical approval latch.
- **missing:** A recovery state machine distinct from ordinary success/failure; Idempotency keys and inverse-action descriptors in actionLedger receipts; A pendant-safe spoken/LED vocabulary for retry, undo, and abandon

### ""The moment my pendant disconnects from the Mac, stop any staged sensitive work and tell me what was prevented; when it reconnects, do not resume without a new approval.""
- **useful because:** A lost cable, sleeping Mac, or walking away becomes a real safety boundary instead of an invisible failure. It protects browser sessions and queued Mac actions during the exact period when the owner is no longer present.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → faculty-action → faculty-perception
- **model tier:** No model for the hot-path fence; background model only to summarize prevented jobs after the event
- **latency:** Disconnect fence under 500 ms; event receipt under 2 s; no model call on the safety path
- **cost:** Negligible API cost; a serial heartbeat and durable relay event dominate implementation, not inference.
- **security:** Fail closed on serial loss, heartbeat timeout, nonce rollback, or Mac agent restart. Cancel only staged/unstarted work; never pretend an already-submitted external action was undone. Persist a signed disconnect epoch and require a new physical approval after reconnect.
- **missing:** USB serial heartbeat watcher for /dev/cu.usbmodem00096003658*; Relay-wide execution fence consulted by Mac and browser executors; Reconnect epoch and durable prevented-job receipts

### ""For important work, don't just tell me it succeeded: have the Mac, the browser, and the relay independently witness the same result, then give me one tamper-evident receipt I can ask about later.""
- **useful because:** Today an executor receipt can say a click or command ran even when the external state differs. A cross-surface witness quorum would make the system honestly distinguish committed, contradictory, and unknown outcomes for actions such as sending, filing, booking, or changing settings.
- **path:** faculty-action → faculty-perception → mac-planner → browser-extension → relay-realtime → pendant → unified
- **model tier:** Background model normalizes the three observations into a compact human explanation; no realtime model is needed unless the owner asks. Cryptographic comparison and quorum decisions are deterministic.
- **latency:** Collect witnesses within 5 seconds for ordinary actions; return committed/contradictory/unknown immediately when the deadline expires.
- **cost:** Low: three small structured observations and one background summarization only for a user-facing explanation; storage of hashes/metadata dominates rather than tokens.
- **security:** Each witness signs a narrowly scoped observation containing operation id, step id, timestamp, locator, and state hash. Never merge unlike locators or treat a missing witness as success. Sensitive evidence stays local; relay stores hashes and provenance, with snippets only under explicit owner request.
- **missing:** A witness-quorum protocol that defines independent Mac, browser, and relay observations; A durable receipt graph linking executor attempt, postcondition witnesses, contradictions, and expiry; A user-facing pendant query/voice verb for retrieving a historical receipt without exposing page contents by default

### ""When the Mac and browser disagree about which account, recipient, file, or tab an action would affect, stop and ask me to resolve the identity from the pendant before doing anything.""
- **useful because:** The most dangerous automation failures are semantically valid actions applied to the wrong identity. A deliberate identity conflict state is safer than silently choosing whichever surface answered first, especially with multiple logged-in browser accounts.
- **path:** faculty-action → faculty-perception → faculty-judgement → mac-planner → browser-extension → relay-realtime → pendant
- **model tier:** Background model extracts a short discriminating question from structured conflicts; deterministic matching detects disagreement. Realtime is used only to ask the owner.
- **latency:** Detect conflict within 2 seconds; ask one concise question and hold the operation for up to 10 minutes.
- **cost:** Low: model invoked only on disagreement, with redacted account labels or locally generated aliases rather than page contents.
- **security:** Do not speak full emails, tokens, or private page text aloud by default. Use owner-defined aliases, hashes, and origin labels; expire the held operation and require fresh approval if identity changes.
- **missing:** Canonical identity/resource aliasing across Mac and browser observations; A first-class conflict outcome in action plans and receipts; Pendant interaction for selecting one of two redacted candidates


## Changes it proposed to its own stack

### `integration` — Add a read-only USB pendant presence adapter to the Mac agent: open /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA, parse only link/heartbeat/monotonic-counter frames, and publish a signed presence epoch to the relay. Do not flash, build, or write firmware; fail closed on malformed frames and expose reconnect/disconnect receipts.
- **owner gets:** Sensitive work can be tied to the pendant actually being attached to this Mac today, and walking away or unplugging it becomes visible immediately rather than leaving queued work looking runnable.
- effort: Medium: serial framing adapter, launchd supervision, relay event schema, tests with recorded fixtures; no firmware change required for a first read-only presence version.  ·  risk: A stale serial port or reconnect could falsely look present. Require fresh challenge/response, monotonic counter, timeout, and explicit epoch changes; recovery is fail-closed and requires new approval.
- cost: Near-zero API cost; one lightweight daemon and a few relay events per minute.  ·  latency: Disconnect detection 100–500 ms depending on heartbeat interval; negligible impact on ordinary actions.
- security: Improves locality and replay resistance while deliberately collecting no audio, text, page data, or secrets. Device identity and counters still require authenticated binding.
- depends on: A documented pendant serial heartbeat/frame format; Relay acceptance of presence epochs; Executor policy hook that consults the epoch before starting staged work

### `context` — Introduce a durable operation provenance graph rather than a flat action log: represent intent, plan revision, executor attempt, each independent observation, contradiction, owner decision, and final status as linked immutable nodes with explicit freshness and scope. Expose a compact hash-chain receipt to the pendant and retain sensitive evidence only on the originating Mac/browser surface.
- **owner gets:** When they ask "did that really happen?" days later, the system can answer which surface saw what, when it became stale, and whether the conclusion was verified or merely inferred—without pretending an executor acknowledgement proves an external result.
- effort: High: schema, append-only storage, correlation across relay/Mac/browser, retention rules, and a voice-friendly receipt query.  ·  risk: More states can confuse users and storage can retain sensitive metadata. Keep the spoken vocabulary to committed, not committed, contradicted, or unknown; hash and expire evidence by default; never rewrite history.
- cost: Small persistent storage and occasional background summarization; no continuous realtime inference.  ·  latency: Adds milliseconds for receipt linking; historical queries may take 1–3 seconds.
- security: Improves tamper evidence but creates a metadata trail. Encrypt local evidence, minimize relay payloads, and make deletion propagate through linked nodes.
- depends on: A stable operation/step identity shared by Mac, browser, relay, and perception; Independent postcondition witness events; Owner-configurable evidence retention


## What it asked for

_Nothing._
## Its own summary

Round 150 produced three new action capabilities and one implementation change. The highest-value addition is a physical-presence-bound execution fence: a USB-connected pendant challenge/response is bound to the exact Mac/browser job, so stale or remote approvals cannot start sensitive work. I also recorded an ambiguous-outcome recovery flow (retry/undo/abandon with verified inverse and idempotency) and a disconnect fail-closed fence that prevents staged work from resuming after the pendant leaves. The integration change is a read-only serial presence adapter for the two live USB devices, with epochs and receipts.

**Biggest unknown:** The pendant serial heartbeat/frame protocol and authenticated device binding are still undocumented, and no executor policy hook is confirmed to consult a relay presence epoch before starting work. I still need those protocol details plus a concrete way to test disconnect/reconnect and ambiguous browser outcomes without performing irreversible actions.

