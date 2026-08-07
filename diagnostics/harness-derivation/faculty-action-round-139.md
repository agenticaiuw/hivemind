# Harness derivation — faculty-action — round 139

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **pendant-local-transport** — The live device registry still reports only home-macbook-bridge and Safari; no LTE-registered pendant. Hardware specs nevertheless identify the real nRF9160 and ESP32 serial paths as physically connected to the Mac, so local USB action/event transport is the immediate way to make the worn surfaces testable.
  - evidence: discover(devices) returned Safari, home-macbook-bridge, cloudflare-contract-test only; system hardware note names /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA as physically connected.

## Capabilities it proposed

### "Start a focus session for 45 minutes: pause only the distracting browser tabs I name, set my Mac's notification mode, open the one document I am working on, and play a focus sound through my headphones. A long press on the pendant cancels and restores every before-state; when the timer ends, restore automatically and tell me what changed."
- **useful because:** This turns a spoken intention into a bounded, reversible routine spanning the worn control, Mac apps, authenticated browser state, and audio output—without leaving the owner to reconstruct or undo it.
- **path:** relay-realtime → faculty-judgement → faculty-action → mac-planner → browser-extension → relay-realtime
- **model tier:** Realtime only for the initial short command and final spoken status; use a cheaper background model to classify named tabs and compile the reversible before/after plan.
- **latency:** Acknowledge in under 1 second; apply the reversible setup in under 8 seconds; restore within 2 seconds of cancel or expiry.
- **cost:** About $0.01–$0.04 per session, dominated by initial intent parsing; Mac/browser actions and timer execution are local.
- **security:** Only named tabs/apps are touched. Capture exact before-state and never close or discard unsaved content. Notification-mode changes are reversible. Require spoken confirmation only if a requested tab has unsaved edits; otherwise the pendant button is cancel-only.
- **missing:** A transaction-like multi-surface state snapshot/restore primitive; Pendant-to-Mac cancel event over USB fallback and later LTE; A Mac notification-mode action with an explicit restore token; Bridge playback start/stop routed through the same session id

### "When a long-running Mac or browser task finishes while I am away, give me a private completion chime in my headphones and a one-sentence pendant announcement; say what succeeded and what needs me. If I say 'undo that' within ten minutes, undo the last reversible step and report the exact result."
- **useful because:** The owner can delegate work without watching a screen. The physical audio path closes the loop, and a time-limited spoken undo makes remote execution recoverable instead of silently accumulating surprises.
- **path:** relay-realtime → faculty-action → mac-planner → browser-extension → pendant → bridge
- **model tier:** Background model summarizes the durable receipt; realtime is reserved for the brief announcement and any follow-up command.
- **latency:** Chime within 2 seconds of receipt publication; spoken summary within 5 seconds; undo command acknowledged within 1 second and completed within 10 seconds for local actions.
- **cost:** Under $0.01 per completion; mostly local receipt formatting and audio transport, with model cost only for multi-step summaries.
- **security:** Announcement must not speak secrets from private tabs. Use sensitivity labels and headphones-only output. Undo expires after ten minutes and is available only when the receipt proves reversibility; never infer undo for a send, purchase, or deletion.
- **missing:** A durable completion-notification subscription keyed to job ownership; Receipt-to-safe-spoken-summary redaction; A pendant/bridge notification channel and time-limited undo resolver

### "While I am away from my Mac, read me the next item in my action queue through the pendant, one sentence at a time. I can say “skip,” “snooze tomorrow,” or “prepare it”; prepare may gather pages, open files, and draft reversible work on the Mac, but it must stop before sending, buying, deleting, or submitting. The pendant button advances or pauses the queue."
- **useful because:** It gives the owner a practical way to turn idle moments into reviewed progress without opening a screen, while keeping consequential actions behind the existing confirmation boundary. The worn device supplies attention and control; the Mac and browser do the actual preparation.
- **path:** relay-realtime → faculty-judgement → faculty-action → mac-planner → browser-extension → pendant → bridge
- **model tier:** Use a cheap background model to rank and summarize queued work; use realtime only for the short spoken item and the owner's spoken choice.
- **latency:** First item in 3 seconds, each next item in under 1 second from cached summaries; preparation starts within 5 seconds and returns a receipt when complete.
- **cost:** About $0.01 per 10-item triage session, dominated by summarization; action execution and audio are local.
- **security:** Never speak secret values from private pages; sensitivity-aware summaries must say only that attention is needed. “Prepare it” is limited to reversible actions. Snoozes and skips need durable audit records, and queue access must be bound to the owner's active pendant session.
- **missing:** A queue model that unifies reminders, unfinished jobs, browser review items, and drafts without duplicating them; Spoken-summary redaction with sensitivity-aware fallback wording; A pendant button protocol for next/pause/skip and a USB transport while the device is unregistered; A prepare-only execution policy that returns a typed receipt

### "Let me say “pause this everywhere” during any task. Freeze the active Mac, browser, and pendant work at a named checkpoint, preserve the exact open pages, drafts, files, and pending actions, and later let me say “resume the checkpoint” or “discard it.” Resuming must first show me what changed while it was paused."
- **useful because:** Today a multi-surface task can continue in inconsistent fragments if the owner is interrupted. A real checkpoint lets them safely switch contexts, sleep, or disconnect without losing the state of work in progress.
- **path:** relay-realtime → faculty-judgement → faculty-action → mac-planner → browser-extension → relay-realtime
- **model tier:** Use a background model to summarize external changes and reconstruct the checkpoint; realtime only handles the short pause/resume commands.
- **latency:** Pause acknowledgement under 1 second; checkpoint captured within 5 seconds; resume diff available within 10 seconds.
- **cost:** $0.02–$0.08 per checkpoint, dominated by diffing browser/file state; storage is small structured metadata plus selected local snapshots.
- **security:** Checkpoint contents may include private pages and drafts. Encrypt at rest, bind to the owner/session, redact secrets from spoken diffs, and require confirmation before applying any external changes discovered during the pause.
- **missing:** A cross-surface checkpoint schema with immutable state hashes; Mac file/draft snapshot adapters and browser DOM/session snapshot adapters; Conflict analysis that distinguishes owner edits from agent edits; A restore planner that can resume without replaying already-completed side effects

### "When I say “show me what you would do,” give me a dry-run of the complete Mac-and-browser action: the exact files, tabs, fields, and messages that would change, plus a spoken summary through the pendant. Let me edit the plan by voice, then execute only the approved version and produce a machine-checkable before/after record."
- **useful because:** The owner gets the confidence of seeing a complete action before it happens, including hidden cross-tab dependencies that a simple confirmation misses. Voice remains sufficient even when the owner is not looking at the Mac.
- **path:** relay-realtime → faculty-judgement → faculty-action → mac-planner → browser-extension → pendant → bridge
- **model tier:** A cheaper planning model builds the dry-run; realtime converts only the final diff and voice edits into a concise interaction.
- **latency:** Initial plan under 8 seconds for ordinary tasks; voice edits acknowledged under 1 second; execution starts only after the final plan hash is approved.
- **cost:** $0.03–$0.15 per dry-run depending on number of tabs and files; local diffing dominates latency, not audio.
- **security:** Never send or submit during simulation. Include source URLs, file paths, field-level before/after values, and sensitivity labels. Approval must bind to the final plan hash so later mutations cannot silently alter the approved action.
- **missing:** A side-effect-free action simulator for Mac and browser operations; A plan-hash approval protocol shared by relay, Mac, and browser bridge; Field/file-level diff extraction and spoken redaction; A typed execution proof tied to the approved plan


## Changes it proposed to its own stack

### `integration` — Add a local USB pendant companion transport in the Mac bridge. Discover /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA by VID/PID, expose a framed authenticated command/event channel, and route the same action-session ids used by relay jobs over USB when LTE registration is absent. Add a simulator mode that replays UART events without flashing, and make every command idempotent with an expiry and a local receipt.
- **owner gets:** The pendant and audio bridge become usable today while attached to the Mac instead of waiting for LTE registration; focus controls, completion alerts, and cancellation can be tested end to end on the real worn hardware.
- effort: Medium: serial framing, reconnect/lock handling, bridge routing, and simulator tests; no firmware flash required for the first event-only prototype.  ·  risk: A stale USB device or partial frame could trigger an old action. Bind commands to short-lived session ids, reject unknown firmware versions, require explicit device nonce, and default to read-only telemetry. Recover by disconnecting the transport and using the existing Mac-only route.
- cost: Negligible API cost; roughly 1–2 weeks engineering. No hardware purchase; serial traffic is low power relative to the prototype boards.  ·  latency: Local event delivery should be 20–100 ms, materially faster than relay round trips; reconnect may take up to 3 seconds.
- security: USB is a local trust boundary, not automatically trusted: authenticate the frame, redact UART payloads from logs, and never expose modem credentials. This does not bypass owner confirmation for destructive actions.
- depends on: A stable serial framing contract from the firmware source; A typed action-session/receipt schema; Owner-controlled build and secrets configuration if firmware changes become necessary

### `model-routing` — Add an action-safety compiler between judgement and execution that decomposes every multi-surface plan into typed effects (read, draft, local mutation, external send, purchase, deletion), computes dependencies and reversibility, and routes each effect to the correct surface. It must reject plans whose stated approval scope does not cover their effects, rather than relying on prose instructions in a prompt.
- **owner gets:** The owner can ask for an outcome naturally while the system reliably prevents an innocent-looking step from crossing into sending, buying, deleting, or submitting. It makes action behavior predictable across Mac, browser, relay, and future pendant transports.
- effort: High: effect taxonomy, adapters for every action type, dependency analysis, policy evaluation, and migration of existing jobs; requires adversarial tests against real receipts.  ·  risk: Incorrect classification could block useful work or permit a dangerous side effect. Default unknown operations to blocked, retain the existing execution path as a fallback, and require explicit owner confirmation for any unclassified effect.
- cost: Small per-action model cost if compiled locally; approximately $0.01–$0.05 for complex plans. Engineering effort is substantial.  ·  latency: Adds roughly 100–500 ms for ordinary plans and several seconds for complex dependency graphs.
- security: Strongly improves least-authority enforcement. Effect metadata and proofs must avoid storing secret field values; policy decisions need an auditable hash and timestamp.
- depends on: A typed action schema across Mac/browser/relay; Reliable field-level receipts from each executor; The owner’s authoritative confirmation policy; A shared plan identity carried through execution and receipts


## What it asked for

_Nothing._
