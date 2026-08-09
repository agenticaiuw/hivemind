# Harness derivation — faculty-action — round 169

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Give me an undo button for the last safe Mac or browser action: if I press the pendant within the grace period, reverse it and tell me whether the reversal was verified.”"
- **useful because:** The owner can recover from an accidental move, rename, draft edit, or browser navigation without finding the original app. It makes proactive automation tolerable because correction is physical, fast, and explicit.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Deterministic action ledger and inverse planner first; background model only to derive an inverse for unfamiliar reversible operations; realtime for the brief spoken confirmation.
- **latency:** Undo staging immediately; physical undo dispatch under 1 s; verification within 3 s or report unknown rather than claiming success.
- **cost:** <$0.02 for an unusual inverse; ordinary actions use existing ledger and no model call.
- **security:** Only actions classified reversible may enter the undo capsule. Store minimal before-state hashes or safe identifiers, not secrets. Expiry, single-use nonce, and verification are mandatory; deletion, external sends, and irreversible submissions are never auto-undone.
- **missing:** A first-class inverse/compensation schema in the existing action ledger; A pendant command for selecting the most recent undo capsule and returning a signed decision; Verifier support for inverse postconditions plus a visible unknown outcome

### "“When I press the pendant, freeze a tiny handoff of what I’m currently doing—foreground Mac app, active browser page, and the next obvious step—so I can resume it later by asking.”"
- **useful because:** The owner can leave a task mid-stream and recover it without remembering which tab, document, or draft mattered. It joins wearable intent, Mac state, browser sessions, and relay memory into a usable personal continuity feature.
- **path:** pendant → mac-planner → mac-vision → browser-extension → relay-realtime → dashboard
- **model tier:** Realtime only to name the handoff when asked; background/cheap model summarizes the captured state; deterministic collectors gather app/tab metadata.
- **latency:** Capture under 2 s; spoken confirmation under 1.5 s; later retrieval under 2 s.
- **cost:** <$0.01 per capture and retrieval when metadata-only; vision is invoked only if the owner explicitly asks for visual context.
- **security:** Default payload is metadata and owner-supplied label, excluding page text, clipboard, passwords, and private fields. Sensitive pages require explicit confirmation before capture. Retention and deletion must be visible in the dashboard.
- **missing:** A durable handoff object and retrieval route (distinct from browser inspection and job receipts); A pendant press event bridge while the pendant is USB-attached but not relay-registered; A policy for private-tab/app redaction

### "“If an action gets stuck or the page changes underneath you, stop safely, tell me exactly what blocked it on the pendant, and let me resume from that checkpoint after I answer—without starting the whole task over.”"
- **useful because:** Today a multi-step task can leave the owner guessing whether it ran, partially ran, or needs repeating. A checkpointed recovery path turns failures into a short clarification instead of duplicate sends, lost drafts, or abandoned work.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Deterministic executor checkpoints and postcondition verifier first; cheap background model summarizes the failure; realtime only handles the owner’s clarification.
- **latency:** Detect and checkpoint within 2 s of failure; spoken blocker summary within 3 s; resume within 5 s after clarification.
- **cost:** <$0.02 per recovery, mostly one small summarization call; ordinary successful actions add no model cost.
- **security:** Checkpoint must contain redacted locators and hashes by default, never passwords or full page contents. An uncertain postcondition must block retries until verification or explicit owner choice. External sends remain staged behind the existing physical approval latch.
- **missing:** A durable checkpoint schema linking operation, step, executor receipt, and verifier evidence; A resume route that can safely replay only the uncompleted suffix; A pendant notification/event path while the hardware remains USB-attached but relay-unregistered

### "“Before you make a consequential change across my Mac and browser, show me one compact commit card—exact destination, fields or files affected, and side effects—and let one deliberate pendant approval commit the whole batch atomically, or leave everything untouched.”"
- **useful because:** The owner gets the safety of reviewing one truthful change-set instead of approving opaque individual clicks. A failed browser step cannot leave half a message sent and half a file changed; the system either commits the declared batch or reports that it did not.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Cheap deterministic diff/transaction builder and policy engine; realtime model only summarizes the card in speech when needed. Never use a model as the commit authority.
- **latency:** Build the card in under 2 seconds; approval-to-commit under 1 second; independent verification under 3 seconds, otherwise report unknown and do not claim atomic success.
- **cost:** <$0.02 for unusual semantic diffs; ordinary file/browser diffs are deterministic. Storage is a bounded encrypted transaction journal.
- **security:** The card must be generated from the exact executable plan, not a model paraphrase. Secrets and private page content are represented by typed redactions and hashes. Approval binds to a digest, destination, expiry, and monotonic counter. If any step cannot provide prepare/commit or compensation semantics, the whole batch must remain staged.
- **missing:** A two-phase prepare/commit or compensation contract for Mac and browser action types; A digest-bound commit card renderer that can be acknowledged on the pendant without exposing secrets; A verifier that checks the aggregate postconditions and distinguishes all-committed, compensated, and unknown; A durable transaction journal shared by relay, Mac, and browser bridge

### "“For purchases, messages, and uploads, enforce my non-negotiable invariants—recipient, account, amount, attachment, and destination—at the moment of submission, and block if the live page differs from what I approved.”"
- **useful because:** The owner is protected from the most dangerous class of automation failure: a stale tab, changed price, wrong account, or swapped attachment being submitted after an apparently correct plan. Approval means the exact live transaction, not an earlier draft.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Deterministic typed invariant checker over live DOM/app state; model only extracts candidate fields into a reviewable schema and never decides equality or safety.
- **latency:** Live pre-submit check under 500 ms; block immediately on mismatch; spoken mismatch explanation under 2 s.
- **cost:** Near-zero for typed fields; occasional cheap extraction call when a new site has no adapter.
- **security:** Never send field values to the relay when local comparison suffices. Hash or redact secrets and private message bodies. Site adapters must fail closed when a field cannot be located or has ambiguous currency/account identity. Owner-editable invariants need versioning and explicit confirmation.
- **missing:** A typed invariant schema and per-action risk policy; DOM/app-state locators with provenance for recipient, amount, account, attachment, and destination; A pre-submit interception hook in browser and Mac executors; A digest that binds invariant values to the existing physical approval latch

### "“Let me ask, ‘What did you change while I was away?’ and get a trustworthy, privacy-filtered account of Mac and browser changes since a physical checkpoint, with links to undo or inspect each item.”"
- **useful because:** The owner can safely delegate while away without reconstructing activity from scattered logs. It distinguishes verified changes, failed attempts, and unknown state, so the owner can decide what to keep rather than blindly trusting a summary.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Deterministic event/provenance aggregation and diffing; cheap background model turns the verified event list into a short spoken account; realtime only answers the question.
- **latency:** Checkpoint query under 2 s for normal history; spoken summary under 3 s; never delay logging on model availability.
- **cost:** <$0.01 per query; mostly local aggregation, with model tokens proportional to number of verified changes.
- **security:** Default to app/site/action metadata and hashes, not page bodies, message contents, or credentials. Private apps/tabs are collapsed to ‘private activity’ unless explicitly included. Every summary item links to raw provenance and retention/deletion controls.
- **missing:** A cross-surface append-only change journal with checkpoint cursors (not merely executor receipts); Mac and browser adapters that emit before/after hashes and privacy classes for state changes; A query/diff route that reports verified, failed, compensated, and unknown outcomes separately; A pendant checkpoint gesture and spoken retrieval path


## Changes it proposed to its own stack

### `integration` — Add a local USB-pendant adapter in the Mac bridge: watch /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA, parse only the firmware's framed button/status/telemetry messages, attach a bridge-held monotonic sequence and device-session nonce, and emit signed relay events. Expose connect/disconnect and last-seen state to the action and checkpoint services, without claiming LTE registration.
- **owner gets:** The physically connected pendant becomes useful today instead of invisible: presses can approve, cancel, bookmark, or acknowledge a Mac/browser task while the owner is wearing it, and the UI can truthfully say when the device is absent.
- effort: Medium: serial framing adapter, reconnect handling, schema tests, and a local diagnostic panel; no firmware flash required.  ·  risk: Malformed or spoofed serial input could authorize actions. Fail closed on framing, session changes, counter rollback, and disconnect; require the existing physical approval latch for consequential actions. Recover by disabling the adapter and falling back to Mac-only staging.
- cost: Negligible API cost; roughly 1–2 weeks engineering. No hardware cost or extra power beyond the already-connected USB devices.  ·  latency: Button-to-relay event under 100 ms locally; reconnect state within 1 s.
- security: Improves security only if the bridge authenticates the device session and never treats arbitrary serial text as consent. Keep payloads free of audio, secrets, and page content.
- depends on: A documented firmware serial frame schema and button mapping; A device identity/attestation mechanism distinct from the relay's absent LTE device record; Existing physical_transaction_approval_latch policy and verifier receipts


## What it asked for

_Nothing._
## Its own summary

Recorded three connective capabilities and one concrete integration change. (1) Undo capsules for reversible Mac/browser actions, with one-use expiry and independently verified reversal. (2) Resumable handoff cards capturing redacted foreground-app/browser context so the owner can leave and later resume work. (3) Checkpointed failure recovery: stop on uncertainty, explain the blocker on the pendant, and resume only the unfinished suffix after clarification. I also recorded a USB pendant/ESP32 adapter change so the physically connected hardware can emit authenticated local events today, without falsely claiming LTE registration. A proposed USB presence-key capability was rejected as an existing duplicate, so I did not count or rephrase it.

**Biggest unknown:** The exact firmware serial frame schema, device identity/attestation method, and current pendant button mapping are still unknown. Until those exist, the Mac bridge cannot safely turn a serial press into approval or cancellation. The pendant remains absent from the relay device table even though both USB chips are physically connected; no further owner request is needed from me this round, but those are the concrete engineering inputs still required.

