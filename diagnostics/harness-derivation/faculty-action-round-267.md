# Harness derivation — faculty-action — round 267

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Stop everything I asked the pendant to do right now."
- **useful because:** One deliberate emergency gesture should halt every active or queued Mac, browser, and iPhone operation, not merely cancel the latest transaction. This gives the owner a reliable physical brake when an action looks wrong or the pendant was triggered accidentally.
- **path:** pendant → relay → mac-planner → browser → iOS
- **model tier:** Realtime only to interpret the spoken stop; cancellation propagation and bookkeeping use relay/background code.
- **latency:** Pendant-to-relay acknowledgement under 500 ms when connected; active executor cancellation under 2 s; queued work must not begin after the stop nonce is accepted.
- **cost:** Negligible model cost after intent recognition; small relay and executor state-machine work dominates.
- **security:** The stop command must be authenticated, monotonic, and idempotent, with a short-lived signed stop nonce. It may interrupt reversible work but must not claim that an already-submitted irreversible action was undone. Surface an explicit unknown outcome for races, and never treat a stale stop as a later stop.
- **missing:** A fleet-wide cancellation primitive spanning relay jobs, Mac execution, browser commands, and iOS actions; A pendant gesture mapping for emergency stop that is distinct from ordinary approval/cancel; Executor contract requiring every long-running action to poll a stop generation

### "Fill in the password and submit this form, but don't show or tell me the password."
- **useful because:** The owner can delegate credentialed browser work without secrets entering the planner prompt, pendant audio, action receipts, screenshots, or model context. The browser performs a just-in-time Keychain injection into the exact field and returns only a redacted success/failure proof.
- **path:** browser → mac-planner → relay → pendant
- **model tier:** Realtime model identifies the intended site and field; a deterministic browser-side secret broker and local Keychain API perform injection, so secrets never go to the model or relay.
- **latency:** Under 3 seconds for lookup and fill; submission remains staged for the existing physical approval latch when the site is consequential.
- **cost:** Near-zero model overhead; engineering is dominated by a local secret-broker and browser-extension integration.
- **security:** Require explicit per-origin and per-field allowlists, WebAuthn/Keychain authorization where available, one-time in-memory handles, no clipboard, no screenshots after injection, and zeroization after submit. Receipts contain origin, field label hash, and outcome only. Never inject into an origin or field whose DOM identity changed without re-confirmation.
- **missing:** A local secret-broker capability scoped to origin, field, and one execution nonce; Browser extension action that accepts an opaque secret handle rather than plaintext; Redaction rules that prevent form values entering snapshots, logs, receipts, or relay events

### "Make this change everywhere, but don't let two actions touch the same file, browser record, or phone setting at once."
- **useful because:** The mind can execute multi-surface work without races: a Mac file rename, browser upload, and iPhone update either acquire disjoint resource leases or wait and ask. This prevents two queued requests from overwriting each other while still allowing unrelated work in parallel.
- **path:** relay → mac-planner → browser → iOS → pendant
- **model tier:** Background/deterministic scheduler computes resource keys and conflict sets; realtime is used only if the owner must resolve a conflict.
- **latency:** Lease decision under 100 ms; conflicting work waits with a spoken/haptic explanation and a bounded expiry rather than silently failing.
- **cost:** No meaningful per-invocation model cost; implementation is a scheduler and adapters that declare touched-resource keys.
- **security:** Resource keys must be opaque where they contain private paths, with only coarse labels exposed to the owner. Leases expire, are fenced by monotonically increasing epochs, and are released on verified completion, cancellation, or crash recovery. Never claim exclusivity for an adapter that cannot declare its targets.
- **missing:** A cross-surface resource lease service with fencing tokens; Action adapters that declare read/write resource keys before execution; Recovery logic that reconciles abandoned leases from job receipts and fresh perception

### "If you get stuck or find two plausible choices, ask me one tiny question on the pendant and continue the same task after I answer."
- **useful because:** Long-running Mac/browser/iPhone work should not abort or guess when a recipient, account, or matching file is ambiguous. The pendant can present a bounded choice or yes/no prompt, capture one response while the owner is away from the Mac, and resume the exact paused operation with its original approvals and evidence.
- **path:** relay → pendant → mac-planner → browser → iOS
- **model tier:** Background model pauses and structures the ambiguity; realtime is used only to phrase the short prompt and parse the owner's response. Execution remains on the local Mac/browser agents.
- **latency:** Pause safely within 1 second of detecting ambiguity; prompt under 10 seconds of speech; resume within 2 seconds after the owner's answer, or expire and leave the operation paused.
- **cost:** One small model call per ambiguity; the main cost is a durable interaction state and adapters that can checkpoint/resume.
- **security:** The prompt must contain only minimum-disclosure labels, never page secrets or full message bodies. Bind the answer to operation ID, step ID, and a nonce; reject late answers after expiry or after the underlying target changed. A response must resolve only the advertised choices, never act as free-form authorization.
- **missing:** A durable paused-step question protocol spanning relay and pendant; A structured choice/yes-no input path from the pendant (wheel plus second button would be ideal); Executor checkpoints that can resume without replaying completed side effects; Fresh perception check before resumption

### "Watch me do this once, then make it a safe command I can repeat later."
- **useful because:** The owner can teach a genuinely new cross-surface workflow by demonstration instead of describing every step. The system records abstract targets and variable slots—not screenshots or secrets—then later plans the workflow, asks for confirmation at risky steps, and verifies each result.
- **path:** mac-vision → browser → iOS → mac-planner → relay → pendant
- **model tier:** A slower background model converts the demonstration into a typed workflow; realtime is unnecessary except for the owner's initial and later voice commands.
- **latency:** Demonstration analysis can take up to 30 seconds; a later invocation should begin within 2 seconds and pause for clarification rather than guessing.
- **cost:** One moderate model call per new demonstration, then low-cost deterministic execution; visual trace storage and workflow review dominate implementation.
- **security:** Never retain raw screen recordings, passwords, message bodies, or unrelated windows. Replace literals with typed slots and origin/app constraints. The owner must review the generated workflow before it becomes reusable; every replay requires fresh target checks and existing approval policy.
- **missing:** A privacy-preserving demonstration recorder across native Mac, browser, and iOS surfaces; A typed workflow compiler that separates stable target identity from variable data; A review/edit surface for the owner to approve generated steps and risk classifications; Replay-time fresh perception and postcondition verification

### "Find the conflicting versions of this information across my apps and make them agree, changing only what is necessary."
- **useful because:** The owner gets a single consistency repair across Calendar, Mail, Notes, browser accounts, and iPhone rather than manually hunting stale copies. The system shows a compact conflict table, chooses an explicitly supported source of truth or asks, then applies the smallest set of edits and reports anything it could not safely reconcile.
- **path:** mac-planner → browser → iOS → relay → pendant
- **model tier:** Background model extracts and compares structured facts; deterministic adapters perform edits; realtime is only for resolving an unresolved conflict.
- **latency:** Initial scan under 15 seconds for a bounded set of apps; no mutation until the owner approves the proposed diff; repair receipts within 5 seconds per surface.
- **cost:** Moderate background extraction cost per scan, dominated by reading multiple app surfaces; mutation is cheap once facts are structured.
- **security:** Use field-level minimization and hashes for unchanged private values. Never infer that two similar records are identical without source and timestamp evidence. Stage destructive merges, preserve an undo plan, and require physical approval for external messages or consequential account changes.
- **missing:** A cross-surface structured-fact extractor with provenance and timestamps; Conflict policy that distinguishes authoritative, newer, and merely similar values; A minimal-diff planner with per-field approvals and compensating edits; Adapters for Calendar, Mail, Notes, browser forms, and iPhone state

### "Open this suspicious file, tell me what it contains, and keep it from changing anything on my Mac."
- **useful because:** The owner can ask for useful handling of untrusted downloads without handing a document or link unrestricted access to files, credentials, browser sessions, or outbound communication. The Mac opens it in an isolated disposable environment, extracts only requested facts, and destroys the environment after a receipt is captured.
- **path:** browser → mac-planner → mac-terminal → relay → pendant
- **model tier:** Background model analyzes extracted text or rendered pixels; realtime is unnecessary unless the owner asks a follow-up question.
- **latency:** Create the isolated workspace in under 5 seconds; bounded analysis under 30 seconds; no network or host-file mutation by default.
- **cost:** Moderate engineering and storage overhead for disposable sandboxes; per-request model cost depends on extracted document size.
- **security:** Default-deny network, clipboard, Keychain, host filesystem, camera/microphone, and browser-cookie access. Enforce file-size, CPU, memory, and time limits. Treat extracted instructions as untrusted data, never as commands. Require explicit approval before exporting a file or opening any external link.
- **missing:** A hardened disposable Mac sandbox or VM adapter; A safe extractor/rendering service with resource limits and malware-aware scanning; A capability boundary that prevents the model from invoking host actions during analysis; A redacted evidence channel for returning only the requested facts


## What it asked for

_Nothing._
