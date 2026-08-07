# Harness derivation — mac-planner — round 60

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent-readiness** — Live Mac agent v0.5.0 is reachable and full-control mode is enabled, but operational readiness is false because Accessibility is not trusted and Screen Recording is not granted; browser extension is offline with 3 pending commands.
  - evidence: GET /ops/status at 2026-08-07T10:51:09Z returned fullControlMode=true, accessibility.trusted=false, screenRecording.granted=false, ready=false, browser.online=false, pendingCommands=3.

## Capabilities it proposed

### "Park this and let me pick it up later."
- **useful because:** The pendant can capture an interruption in one sentence while the owner is away from the desk; the relay preserves it, the Mac records what was actually open, and the browser contributes authenticated page context without requiring the owner to reconstruct the task later. A later spoken 'resume my parked items' returns a short, evidence-linked queue and can reopen the exact workspace.
- **path:** pendant → relay → mac-vision → mac-planner → browser-extension → dashboard
- **model tier:** Use realtime only for the pendant utterance and later spoken retrieval; use a cheaper background model to normalize the task card, deduplicate parked items, and rank them by freshness and urgency.
- **latency:** Acknowledge the park command in under 1 second; capture Mac/browser state within 5 seconds; resume brief in under 3 seconds when cached, otherwise clearly say it is still gathering context.
- **cost:** Low per park/resume: one short realtime turn plus a small background extraction call; storage and browser/Mac inspection dominate operational cost, not tokens.
- **security:** The capture may include private tab titles, selected text, mail/calendar snippets, and local filenames. Keep evidence local or encrypted, redact secrets by default, bind each card to the initiating device/session, and expose deletion/export. Never submit browser mutations as part of parking or resuming without an explicit separate command.
- **missing:** A real read-only Mac inspection implementation (the granted mac_readonly_inspect schema currently returns 'no implementation').; A browser command enqueue path that can reliably snapshot already-open authenticated tabs with request IDs and tab affinity.; A durable cross-surface task-card store with checkpoints, provenance, TTL, and a resume endpoint.; A compact pendant/dashboard view for listing, dismissing, and reopening parked items.

### "Privacy curtain on."
- **useful because:** The owner should be able to make the whole hive stop observing and speaking sensitive context instantly, without hunting through Mac settings or closing browser tabs. A physical pendant gesture would pause relay transcription, suppress spoken playback, freeze Mac/browser observation and queued automation, and show a clear local status; turning it off would resume only with an explicit boundary so private moments are not accidentally captured or acted on.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** No model is needed for the immediate transition. Use a small background model only to reconcile interrupted jobs afterward and explain what was paused; realtime handles only the owner's explicit spoken status query after the curtain is lifted.
- **latency:** The pendant LED/haptic acknowledgement must occur locally within 100 ms; relay and Mac/browser pause propagation should complete within 1 second. Resume status should be available within 2 seconds, with interrupted jobs remaining paused until reconciled.
- **cost:** Near-zero inference cost for state transitions; minor durable-state and heartbeat traffic. Reconciliation summaries use an inexpensive background model only when needed.
- **security:** The curtain state must be fail-closed: loss of relay connectivity, reboot, or ambiguous state must not resume capture or queued actions. Persist only a minimal encrypted on/off epoch, never the private audio or page contents. Browser sessions must stop extraction and Mac must suppress screenshots/UI snapshots; queued mutations must not execute while paused. Show an unmistakable physical indication and provide a local-only emergency-off path.
- **missing:** A firmware-level privacy-curtain event and persistent state that survives dropped links and reboot.; A relay-wide privacy epoch propagated to every paired surface with fail-closed expiry semantics.; Mac and browser hooks that cancel observation, audio delivery, and queued automation immediately, then report exact pause boundaries.; A dashboard and spoken status contract showing which jobs were paused, dropped, or safely resumable without exposing their private contents.

### "What left my devices for that task?"
- **useful because:** Today the owner cannot get a trustworthy, human-readable answer about which audio, text, page snippets, files, or metadata crossed from the pendant/Mac/browser to the relay or model. A cross-surface egress receipt would let them inspect the exact categories, destinations, timestamps, retention, and redaction decisions for one task, without exposing the underlying secret again.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Generate the receipt from structured local/relay audit events with a cheaper background model; use realtime only when the owner asks verbally and needs a concise explanation.
- **latency:** Record events synchronously or within 200 ms of transfer; render a task receipt in under 2 seconds from local durable logs. If a surface has no telemetry, say so explicitly rather than claiming completeness.
- **cost:** Low API cost; structured event storage and retention are the main costs. A compact per-task ledger can be kept locally and mirrored as encrypted hashes.
- **security:** The ledger itself can reveal sensitive destinations and filenames. Keep payloads out of the receipt by default, encrypt records, bind them to a task/session, support deletion and export, and distinguish observed transfers from inferred ones. The system must never fabricate a complete audit when an old component was not instrumented.
- **missing:** A shared task-scoped data-egress event schema across pendant, relay, Mac, and browser.; Local and relay append-only audit storage with integrity hashes, retention controls, and redaction metadata.; Instrumentation around transcription, model requests, browser extraction, file reads, and audio delivery.; A dashboard and spoken renderer that explains uncertainty and coverage gaps plainly.


## Changes it proposed to its own stack

### `mac-harness` — Implement the already-granted mac_readonly_inspect operations end to end: running apps, foreground app, accessibility state, UI snapshot, browser tabs, and bounded directory listing. Return typed, redacted results with timestamp, request ID, and explicit unavailable/error states instead of the current hard-coded 'no implementation' response; do not add arbitrary shell access.
- **owner gets:** The assistant can tell the truth about what is open and safely prepare actions without stealing focus or guessing. This is the missing observation half of reliable park/resume, meeting prep, receipts, and browser-to-file workflows.
- effort: Moderate: a small local bridge service plus Accessibility/NSWorkspace/browser adapter tests and a strict approved-path allowlist.  ·  risk: UI APIs can expose private titles or text and may fail under revoked permissions. Default to metadata/snippets, redact sensitive fields, return stale timestamps, and degrade to 'unavailable' rather than inventing state. Recovery is restart the bridge or use the existing action path.
- cost: Negligible API cost; modest local engineering and test effort, no new hardware.  ·  latency: Typically sub-second for app state and directory metadata; UI snapshots may take 1–3 seconds.
- security: Read-only access still reveals private local/browser context. Enforce per-operation scopes, approved paths, redaction, and audit receipts; never use this implementation as a shell proxy.
- depends on: A local Mac bridge implementation owner and Accessibility permission handling; Browser extension status/bridge API for browser_tabs

### `integration` — Add a reconnect reconciliation protocol for the Mac↔browser bridge: every queued browser command carries creation time, initiating pendant/session ID, tab affinity, and an intent hash; when the extension returns online, the Mac first reports queued/stale items and current tab identity, drops expired commands into a visible quarantine, and only replays commands whose intent and tab still match. Emit a concise relay receipt for replayed, skipped, or quarantined work.
- **owner gets:** The owner will not wake up to an old command typing into the wrong logged-in page after the browser was offline. Pending work either resumes against the same context or is clearly surfaced for review, rather than silently failing or causing an unintended mutation.
- effort: Moderate: extend browserBridge/browserSessions queue records, add reconnect handshake and a small dashboard/relay status view, with tests for duplicate delivery, tab replacement, and clock skew.  ·  risk: A legitimate command may be quarantined after a long outage; preserve it for explicit retry. Browser restarts and tab IDs can change, so match URL/origin/title plus a session nonce rather than tab ID alone. Never auto-replay irreversible actions after context mismatch.
- cost: Very low API cost; local D1/file state and a few relay status events dominate.  ·  latency: Adds milliseconds to heartbeat and one reconciliation round-trip on reconnect; prevents much more expensive erroneous actions.
- security: Command metadata and tab identity are sensitive. Store only hashes/minimal origin metadata, encrypt durable records, and do not include page contents in relay receipts.
- depends on: A functioning browser extension heartbeat/command endpoint; Durable queue records with request IDs and idempotency keys; Relay delivery of typed receipts


## What it asked for

_Nothing._
