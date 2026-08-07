# Harness derivation — mac-terminal — round 129

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“The task failed—figure out why, repair what you can, retry only the failed part, and tell me if it is truly finished.”"
- **useful because:** Today a failed shell or browser step leaves the owner to diagnose it manually. The Mac can collect exit status and local diagnostics, the browser can verify session/page state, and the relay can keep a bounded recovery loop alive after the voice turn ends. This turns failure into a resolved outcome rather than a vague error, without pretending a retry succeeded.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** background for diagnosis and retry planning; realtime only for the short spoken status
- **latency:** Start recovery within 2 seconds; allow up to 2 minutes for bounded retries, with an exception-only pendant update.
- **cost:** About $0.01–$0.05 per failed task; most cost is one background diagnosis/replan, not the normal command.
- **security:** A retry can repeat side effects, so it must use the existing action receipts to identify completed steps and explicitly label irreversible shell/browser effects. No secrets leave the Mac; send only exit status, sanitized diagnostics, and cited browser state. Never claim completion without a postcondition check.
- **missing:** A durable recovery state machine that distinguishes failed, retrying, repaired, and blocked; Per-action retry classification and postcondition probes for arbitrary run_shell results; A relay-to-Mac completion/error event that can wake the pendant without another voice turn

### "“Use the pendant over USB as my physical job remote: start the queued Mac/browser task, show progress with its light or haptic feedback, and alert me only when it needs a decision.”"
- **useful because:** The pendant is physically attached to this Mac now even though LTE registration is absent. That makes a useful offline-first mode testable today: a button or serial event can start/pause/cancel a relay job, while the Mac executes and the relay retains status. The owner gets a wearable control surface instead of needing to reopen a screen or voice session.
- **path:** pendant → mac-planner → relay-realtime → browser-extension → dashboard
- **model tier:** No model for transport/progress; use a cheap background model only to compress a blocked-job explanation into a short wearable message.
- **latency:** Button-to-acknowledgement under 300 ms over USB; progress updates at most every 5 seconds; blocked explanations under 10 seconds.
- **cost:** Near-zero API cost for control and progress; occasional ~$0.001–$0.01 summarization for a blocked state.
- **security:** USB events must be bound to the currently paired pendant and job ID; a lost/reconnected cable must not duplicate starts. Haptic/LED output should reveal only coarse status, not private page contents. Starting a job is reversible, but cancel semantics must be explicit.
- **missing:** nRF9160 USB-serial event and LED/haptic protocol implementation; Mac bridge transport that maps serial button events to authenticated job commands; A compact job-progress/status packet and reconnect/idempotency handling

### "“What did you change on my Mac and in my browser since [time]?”"
- **useful because:** The existing receipts make individual actions inspectable, but the owner still lacks one cross-surface answer: files/settings/apps/shell commands and browser mutations summarized as a time-bounded change set, with links to receipts and available undo. This is especially valuable after unattended work or while away from the screen.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Cheap background model for grouping and summarizing; realtime only to answer a follow-up about one receipt.
- **latency:** Under 3 seconds for a small time window; under 15 seconds for a day of activity.
- **cost:** About $0.002–$0.02 per query, dominated by summarizing many receipt records; raw filtering should be local/relay-side.
- **security:** Filter by owner/session and redact command arguments, tokens, clipboard, and page text unless requested. Report uncertainty when a shell command's side effects cannot be enumerated. Undo links must target exact receipt IDs and never imply arbitrary shell reversibility.
- **missing:** A normalized cross-surface event index joining Mac action receipts, shell metadata, browser inspections, and relay job IDs; Filesystem/settings post-action diff probes for commands whose effects are opaque; A time-range query and redaction layer exposed to the dashboard and pendant

### "“Tap my pendant to bind this exact Safari tab and the app I’m looking at, then let me ask about or act on that context without telling you which tab it is.”"
- **useful because:** Owners routinely have several private tabs and half-finished windows open. A physical tap gives the system an unambiguous attention anchor: the Mac reports the foreground app, active tab, selection, and a short-lived screenshot/text fingerprint; the relay and browser surface use that binding for the next request only. This removes the most frustrating class of wrong-tab answers without requiring the owner to narrate UI details.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Realtime for interpreting the immediate request; use a cheaper model for extracting and compressing the bound context.
- **latency:** Under 500 ms from tap to acknowledgement; context available within 3 seconds.
- **cost:** Roughly $0.002–$0.02 per use, dominated by optional screenshot/text compression; the binding itself is local.
- **security:** The binding must expire quickly and be scoped to the paired pendant, Mac session, tab ID, and request. Private page content must remain on the Mac unless the owner asks for relay processing. Never expose a tab merely because it was recently active.
- **missing:** A Mac Accessibility/Screen Recording-backed foreground-app and active-tab capture primitive; A pendant-to-Mac tap/nonce handshake over the live USB serial connection; An ephemeral context-binding token accepted by browser actions and relay planning

### "“Don’t just tell me this is done—prove it from the actual file, app, or webpage, and show me the evidence if it isn’t.”"
- **useful because:** Automation often reports a successful command rather than the real-world result the owner cares about. This capability would perform an independent verification pass against the relevant postcondition: inspect the resulting file bytes, application state, or authenticated DOM, compare it with the requested outcome, and return a cited pass/fail/unknown answer. It is a distinct truth check, not another action history.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Cheap background verifier for deterministic checks; realtime only for the concise spoken verdict.
- **latency:** Under 5 seconds for local files/apps; under 15 seconds for an authenticated page.
- **cost:** About $0.001–$0.015 per verification; most checks should be deterministic and incur no model cost.
- **security:** Verification must use the minimum required page/file scope and redact private values in spoken output. “Unknown” is a valid result when the system cannot establish the postcondition; it must not infer success from an exit code or stale receipt.
- **missing:** A typed postcondition language covering files, app state, browser DOM, and external-visible results; Independent verification executors that run separately from the action's success path; Evidence objects with source, timestamp, locator/hash, and confidence rendered across relay and dashboard

### "“Pack up exactly where I am—open tabs, relevant files, unsent drafts, and the next safe step—so I can resume this work later with one tap.”"
- **useful because:** A normal job receipt records actions, but it does not preserve the owner's human-in-progress state. This creates a resumable work capsule spanning Safari's authenticated tabs, Mac files/apps, unsent text, and the reasoned next step. The owner could sleep, close the laptop, or move to another session and resume without reconstructing context or accidentally submitting a draft.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Background model to summarize intent and propose the next step; deterministic collectors for tabs, files, drafts, and receipts.
- **latency:** Capture within 10 seconds; restore preview within 5 seconds; never auto-submit on restore.
- **cost:** Approximately $0.01–$0.08 per capsule, dominated by summarizing unsent work; storage is bounded and local-first.
- **security:** Capsules can contain highly sensitive authenticated content. Encrypt at rest, bind to the owner's device/session, allow per-item exclusion, expire by default, and keep browser drafts unsent. Restoration must preview every write or tab mutation before applying it.
- **missing:** A cross-surface capsule schema for tab identity, file snapshots, draft text, app state, and next-step rationale; Safe collectors for unsent browser form state and foreground Mac work; Encrypted local/relay storage with selective restore and conflict detection


## What it asked for

### `s17-irxx` (skill) — usb_disconnect_job_cache
- does: When the pendant is USB-attached, it mirrors compact authenticated job acknowledgements and status transitions from the Mac. If the serial link drops, it records the owner's button intent (start, pause, cancel, acknowledge) with a monotonic counter and gives local LED/haptic feedback. On reconnect it uploads the intents exactly once and displays the reconciled result, rejecting stale or duplicate job IDs.
- must be on-device because: It must detect USB loss and drive pendant feedback offline; the relay cannot observe a disconnected serial cable or provide truthful local acknowledgement. This is directly testable with the two physically connected chips before LTE registration exists.
- trigger: USB serial connect/disconnect event, authenticated status packet from the Mac, or a pendant button press while disconnected.
- storage: A 32-entry ring in nRF9160 flash: roughly 32 × 64-byte event records plus a small pairing/sequence header, under 3 KB; no sensitive page text.
- RAM budget: About 4–8 KB buffers/state, comfortably below the 211,608 B application RAM budget; use flash ring writes rather than retaining history in RAM.

