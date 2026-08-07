# Harness derivation — browser-extension — round 52

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Continue the thing I was doing in Safari, exactly where I left off.”"
- **useful because:** Today a browser task is tied to a live extension/tab and is easily lost when Safari sleeps, the extension disconnects, or the owner moves away from the Mac. The owner should be able to resume an interrupted authenticated workflow from the pendant without hunting for the tab, repeating completed steps, or guessing what is currently on screen. The system would speak a compact state summary, accept dictation for the next reversible field, and leave the workflow paused at the same point if the link drops.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision → dashboard
- **model tier:** Use a cheaper background model to normalize the saved workflow state and compare the current page to the checkpoint; use realtime only for the owner's low-latency voice commands and spoken status. Use mac-vision only when DOM selectors are unavailable.
- **latency:** A resume status should be audible within 2 seconds when the Mac and extension are online. Reattaching and verifying the page may take up to 10 seconds. State compaction can happen asynchronously after each step.
- **cost:** Roughly $0.005–$0.03 per resume depending on whether vision is needed; most cost is page extraction and occasional screenshot reasoning, not the relay heartbeat.
- **security:** Persist workflow checkpoints rather than passwords: opaque tab/session identifiers, URL origin, page title, completed step IDs, field labels, redacted value hashes, and evidence snippets only where allowed. Authenticated page content stays on the Mac/browser bridge. Never infer that a changed tab is the same task; require a matching origin and semantic page fingerprint before resuming. Dictated values should be encrypted in transit and discarded after successful local application. Submitting, sending, purchasing, or other irreversible actions remain paused with an explicit preview.
- **missing:** A durable cross-surface workflow checkpoint format with step-level before/after evidence and semantic page fingerprints.; Browser-bridge reconnect and tab reattachment that can distinguish the original task from a merely similar page.; A relay-to-pendant resumable status channel for queued browser jobs and spoken progress receipts.; A local, encrypted checkpoint store with retention and redaction rules.; Planner support for converting a voice utterance into the next reversible browser action without losing the paused workflow context.


## Changes it proposed to its own stack

### `browser-harness` — Add an offline-aware browser queue supervisor distinct from the durable job runner: when /browser/status reports the Safari extension offline, atomically classify pending commands as queued (safe to replay), expired (lease exceeded), or unsafe-to-replay (type/click after unknown tab state); stop the 45-second waiter, persist the last known tab/session fingerprint and step id, and resume queued read/navigation work automatically on the next heartbeat. Emit one reconnect receipt to the pendant/relay with pending count, skipped commands, and exact recovery point; provide an idempotent janitor to clear only expired orphan commands rather than replaying them blindly.
- **owner gets:** A dropped Safari extension or sleeping Mac would no longer turn a private-page task into a silent timeout or leave three invisible commands stranded. When the owner returns, the system resumes reading at the right tab and tells them exactly what completed, instead of duplicating clicks or making them restart the request.
- effort: Medium: browserBridge queue state machine plus heartbeat-triggered supervisor, persisted lease/fingerprint records, and a small relay/mac status event adapter; tests for crash/reconnect and tab mismatch.  ·  risk: Replaying a stale click/type could duplicate a reversible UI mutation or land on a different page. Default replay is limited to navigate/read/wait and commands with matching tab URL/title fingerprint; uncertain mutations are marked skipped with a receipt. Recovery is manual re-enqueue, not a gate on unrelated actions.
- cost: Negligible API cost; one small D1/local JSON status record per pending command and a heartbeat event. No browser-minutes consumed while offline.  ·  latency: No added latency while online; reconnect recovery begins on the first heartbeat, and removes the current 45-second blocking timeout behavior.
- security: Persist only tab metadata, command hashes, and status—not page contents or credentials. Keep authenticated page text in Safari/local agent and redact URLs where configured.
- depends on: A functioning Safari extension heartbeat (existing); Typed/idempotent command IDs already present (chg-14accc01 partial); The durable browser job runner remains optional; this supervisor should also protect ad-hoc /execute commands


## What it asked for

_Nothing._
