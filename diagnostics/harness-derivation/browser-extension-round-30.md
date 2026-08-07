# Harness derivation — browser-extension — round 30

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If my browser session is unavailable, reconnect it and continue the private-page job when Safari comes back; tell me what was completed, what is waiting, and what needs me."
- **useful because:** Authenticated browser work currently fails silently when the extension disappears or stale commands remain queued. This would make long-running private-page jobs dependable across sleep, browser restarts, and relay outages without repeating actions or losing the evidence gathered so far.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for queue recovery, extraction, and reconciliation; realtime only for the owner's spoken status request
- **latency:** Queue immediately; resume within one heartbeat after Safari reconnects; spoken status under 2 seconds from cached job state
- **cost:** Usually <$0.01 per recovery (D1/relay and local bridge calls dominate); model cost only when page state must be reconciled or summarized
- **security:** Private URLs and extracted page text stay on the Mac/relay job scope; never replay a mutating browser command whose receipt is unknown. Show the pending action and require the owner's existing confirmation before send/purchase/delete. Pendant should receive status, not page contents by default.
- **missing:** A durable browser job state machine with per-command idempotency keys and receipts (not just an in-memory pending queue); Extension heartbeat/reconnect handling that marks stale devices and rebinds a named session when Safari returns; A recovery reconciler that can compare before/after page fingerprints and classify a command as applied, not-applied, or unknown; Pendant/relay event delivery for job-paused, resumed, and needs-attention states; Dashboard controls to retry, abandon, or inspect the evidence bundle

### "When I say “what am I looking at?”, use the Safari tab I’m currently viewing to give me a short spoken explanation, and let me say “that one” or “open the details” to navigate within the page hands-free."
- **useful because:** Today the pendant can converse and the browser can be driven, but they do not share the owner's moment-to-moment visual context. This would make dense authenticated dashboards, documents, and forms accessible while the owner is away from the keyboard, without requiring them to describe or copy the page.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime for the short spoken grounding exchange and disambiguating “that one”; background model for page extraction, section ranking, and explanation. Use the browser's authenticated session, never public search, when a live tab is available.
- **latency:** Return a first grounding sentence within 3 seconds; follow-up navigation within 2 seconds after the owner's selection; extraction may continue in the background for long pages.
- **cost:** About $0.01–$0.05 per interaction, dominated by realtime audio and one page extraction; cache the current page fingerprint and extracted headings to avoid repeated model calls.
- **security:** The page may contain private work, financial, or health data. Keep raw DOM/text on the Mac job scope, send only the requested excerpt/summary to the relay, and make the pendant response ephemeral by default. Navigation is reversible; filling or submitting anything remains outside this mode and must produce a preview first. Do not infer that the owner selected a control from vague speech—ask a concise disambiguation question.
- **missing:** A browser-to-voice context binding that atomically captures the active tab and page fingerprint at utterance time; Semantic page regions with stable spoken labels (for example, “the second overdue invoice”) and a short-lived mapping from labels to DOM targets; A low-latency relay event carrying selected extracted text and navigation results to the pendant; An extension command for active-tab capture plus scoped read/scroll/focus navigation; A privacy indicator and dashboard history showing which page excerpt was spoken


## Changes it proposed to its own stack

### `browser-harness` — Implement a crash-safe browser command ledger and reconnect reconciler. Persist each command with jobId, sessionId, deviceId, idempotency key, expected page fingerprint, dispatch/result timestamps, and receipt. On extension heartbeat, classify pending commands as safe-to-retry, already-applied, or unknown by reading the bound tab and comparing the expected fingerprint; quarantine unknown mutations instead of replaying them. Expire orphaned commands with a visible reason and preserve their evidence.
- **owner gets:** A sleeping or restarted Safari should not make the owner wonder whether a logged-in form was filled, repeat work, or accidentally perform an action twice. Jobs can continue automatically for reads and stop precisely where the browser state is ambiguous.
- effort: Medium: D1/local JSON schema, bridge reconciliation loop, extension heartbeat metadata, and dashboard status panel; requires integration tests for disconnects during every supported command.  ·  risk: A weak fingerprint could misclassify a changed page; recover by defaulting to unknown and showing the last URL, screenshot/extracted snippet, and command. Read-only retries are safe; high-impact actions remain quarantined. Migration must import current pending commands as unknown rather than replay them.
- cost: Negligible storage and relay requests; occasional one extra page read per reconnect. No additional model call unless semantic reconciliation is needed.  ·  latency: Normal commands unchanged; reconnect adds roughly one heartbeat plus a page read before resuming.
- security: Improves auditability and prevents duplicate private-page mutations. Keep page text and screenshots scoped to the job retention policy; do not send them to the pendant unless requested.
- depends on: A durable browser job/session model; Extension heartbeat including stable device and tab identity; Result receipts and evidence retention; A dashboard or API for paused/unknown command review


## What it asked for

_Nothing._
## Its own summary

Discovered the live state: Safari is currently offline, only the never-used home-chrome registration is reported, two browser commands are pending, and three stale browser sessions remain on disk. I notified mac-planner. I proposed a new cross-node capability for reconnecting and resuming private-page jobs, plus a crash-safe browser command ledger/reconciler that classifies commands as applied, safe-to-retry, or unknown instead of replaying blindly. I do not need another permission this round; the immediate operational need is restoring the real Safari extension heartbeat and reconciling the two orphaned commands.

**Biggest unknown:** Whether the two pending commands changed any page before Safari went offline; without the extension reconnecting, they must remain unknown and must not be replayed.

