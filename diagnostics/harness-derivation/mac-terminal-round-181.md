# Harness derivation — mac-terminal — round 181

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/browser/relay state** — Mac agent v0.5.0 is online in FULL_CONTROL_MODE with Accessibility, Screen Recording, and automation permissions granted; relay and browser extension are online. Safari has 9 tabs and active tab is x.com/home. Vision loop is enabled but vision upload consent is false.
  - evidence: GET /ops/snapshot returned 200 with agent.fullControlMode=true, permissions.ready=true, relay.macBridgeOnline=true, browser.online=true, tabUrl=https://x.com/home, tabCount=9, computerUse.loopEnabled=true, visionUploadConsented=false.

## Capabilities it proposed

### "I pressed the pendant while I was working. Put me back exactly where I left off: identify the active Mac project and browser tab, reopen the relevant windows, restore the last working context, and tell me the next unfinished step over the pendant."
- **useful because:** This is the single most useful hive capability: the pendant supplies the physical moment and voice, the Mac knows foreground apps/projects, Safari holds authenticated sessions, and the relay preserves the request while any one link is unavailable. It turns interruption and sleep into a recoverable work state rather than asking the owner to reconstruct it from memory.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** background for snapshot indexing and context matching; realtime only for the short spoken confirmation and ambiguity question
- **latency:** Capture in under 1 s; restore in under 8 s for known apps/tabs; if vision is needed, up to 20 s with progress on the pendant
- **cost:** Usually <$0.01 per resume (small context match); <$0.05 when a vision pass is needed. Dominant costs are browser snapshot storage and occasional vision inference.
- **security:** Authenticated tab URLs, window titles, project paths, and a short screen-derived context leave the Mac only as encrypted relay state. Never upload page contents by default; ask before including secrets or transmitting a screenshot. Reopening a tab is reversible, but typing or submitting anything requires a separate explicit intent.
- **missing:** A durable context-capsule schema joining pendant timestamp/button event, foreground app, active project, browser session/tab, unfinished job, and last spoken turn; Mac capture hooks for foreground window and project/session at the existing marker event; A restore planner that can reopen/focus windows and browser tabs without confusing stale tabs; A compact spoken 'next step' summarizer with confidence and an owner-visible evidence trail

### "Run this Mac task until it actually succeeds: if a command fails, diagnose the exit code and stderr, choose a safer equivalent or repair, retry only the failed step, and tell me exactly what changed and what remains blocked on the pendant."
- **useful because:** Today a failed shell step is flattened into a message, cancellation cannot stop a running process, and nothing retries. This capability makes the trusted maximum-access Mac useful in real work: transient network failures, stale paths, missing CLIs, and partial multi-step jobs recover without the owner manually deciphering logs or accidentally repeating completed side effects.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → dashboard
- **model tier:** cheap background model for deterministic exit-code classification and bounded repair suggestions; realtime only to report a dangerous ambiguity or final result
- **latency:** First failure diagnosis under 2 s; one repair attempt within 10 s; hard cap of 3 attempts or 2 minutes per step, with immediate pendant status updates
- **cost:** <$0.02 typical; mostly local execution, with model cost only for unknown stderr. Large logs should be summarized locally before inference.
- **security:** The owner has deliberately chosen unrestricted execution, so this is not a gate. Preserve the original command, repaired command, exit code, stderr hash, and diff of touched paths; never silently substitute a destructive command. Require a distinct owner instruction before retrying a non-idempotent mutation, while allowing automatic retries for reads and explicitly idempotent steps.
- **missing:** Capture and persist process exit code, signal, pid, timeout-versus-exit distinction, and bounded stdout/stderr tails; A repair classifier with an idempotency declaration per action and a step-level retry budget; AbortSignal wiring to the child process so cancellation kills the actual process, not just the between-step loop; A durable job/ledger join and boot reconciliation so retries cannot duplicate a step after agent restart; Pendant-friendly progress and final receipts carrying original-versus-repaired command

### "Use my Mac and authenticated browser to finish the task, but give the pendant only a private, redacted answer: detect tokens, passwords, personal identifiers, and secret page fields locally, keep raw output on the Mac, and let me ask for one specific redacted detail at a time."
- **useful because:** The hive can currently move sensitive browser text and shell output through relay context even when the owner only needs a yes/no or a small result. Local redaction makes authenticated browser automation and unrestricted shell genuinely wearable: the pendant can report progress and conclusions without turning the relay or spoken channel into a secret exfiltration path.
- **path:** browser-extension → mac-terminal → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** local deterministic scanners first (credential formats, key names, email/phone patterns); cheap background model only for semantic field classification; realtime speaks the already-redacted answer
- **latency:** Redaction under 300 ms for ordinary command/page output; under 2 s for large authenticated pages; no raw payload should wait on a cloud model
- **cost:** Near-zero for deterministic patterns; <$0.01 for an occasional local/cheap semantic classifier. Storage cost is a bounded encrypted local artifact, not API tokens.
- **security:** Raw stdout, browser text, screenshots, and command arguments stay on the Mac by default. Redaction must fail closed on uncertainty, preserve an audit hash and rule version, and never send environment variables or cookies to the relay. A deliberate owner request for a specific field should still return the minimum necessary value and expire from relay memory.
- **missing:** A Mac-local streaming redaction layer applied before pipeline events, browser results, job responses, and spoken TTS; Secret detectors that understand macOS keychain paths, environment-variable names, OAuth/JWT/private-key formats, and authenticated DOM fields; A capability to request a single field from a local artifact without uploading the artifact; Dashboard controls showing redaction decisions and allowing local-only inspection; End-to-end tests proving no raw stdout/page text enters relay logs or pendant audio

### "Before you automate across my Mac and authenticated browser, make a named checkpoint. If I say “put it back,” restore the files, window/app layout, browser tabs and drafts to that checkpoint, and show me exactly what could not be restored."
- **useful because:** The owner can safely delegate genuinely large work rather than limiting the agent to reversible toy actions. A checkpoint spanning local files, open apps, authenticated tabs and in-progress browser drafts is something no Mac-only, browser-only, or pendant-only node can provide; it makes the hive experimentally useful while preserving a clear escape hatch.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → mac-vision → dashboard
- **model tier:** background model for state-diff summarization and restore planning; realtime only for the spoken checkpoint/restore confirmation
- **latency:** Checkpoint acknowledgement under 2 s for ordinary work; restore plan under 5 s; execution may take up to 30 s with per-surface progress on the pendant
- **cost:** <$0.03 per checkpoint/restore in normal use; storage and browser snapshot retention dominate, with vision inference only for window/layout reconstruction
- **security:** Checkpoint data can contain private files, authenticated page state, and draft text. Keep raw artifacts encrypted and local by default, send only hashes/metadata to relay, expire checkpoints by owner policy, and never restore a submission or external side effect as if it were a draft. Restoration must report conflicts rather than overwrite newer owner changes.
- **missing:** A versioned checkpoint store for file hashes/content, app/window geometry, browser tab/session state, and draft DOM fields; Per-surface capture and restore adapters that distinguish reversible local state from irreversible external actions; Three-way conflict detection between checkpoint, current state, and intended restore; A durable checkpoint ID carried through relay, Mac jobs, browser commands, receipts, and pendant status; Dashboard diff and selective-restore controls

### "Make a handoff packet for the person taking over: gather the relevant Mac files, authenticated browser evidence, commands that ran, decisions, open questions, and a short next-step checklist; redact secrets and give me a reviewable package before anything is shared."
- **useful because:** The owner currently has to reconstruct a task for another person by hand. This would turn the pendant’s spoken request into a coherent, evidence-backed handoff assembled from the Mac shell, active browser session, job receipts, and relay memory—without exposing the authenticated session itself.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → dashboard
- **model tier:** background model for organizing and summarizing local evidence; realtime only for clarifying the recipient and announcing that a draft is ready
- **latency:** Draft in under 20 s for a normal task; large projects can run in the background with a pendant completion beacon
- **cost:** $0.02–$0.10 depending on local artifact volume; summarization dominates, while the package should be generated and stored locally
- **security:** Never export cookies, tokens, hidden DOM fields, environment variables, or unrestricted screen captures. Default to a local draft and require owner review before sharing. Every included artifact needs provenance, timestamp, and a sensitivity label; sharing destination and link expiry must be explicit.
- **missing:** A local artifact collector joining shell outputs, receipts, selected files, browser evidence capsules, active project, and context graph; A provenance-preserving redaction and citation format for the handoff document; A review UI with per-item inclusion/exclusion and recipient-specific export policies; A durable package format with expiry, revocation, and a share audit trail; A relay command that can notify the pendant when the draft is ready without sending its contents

### "Watch for this condition across my Mac and authenticated browser—when it becomes true, perform the prepared steps once, leave an evidence trail, and tell me on the pendant; if the condition is ambiguous or the browser session expires, wait instead of guessing."
- **useful because:** This gives the owner dependable event-driven automation rather than brittle timers: a page change, local file/build result, network state, and active project can jointly trigger a useful action. The relay can wait while the Mac sleeps, the browser can observe authenticated state, and the pendant can report completion or explain why it stayed idle.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → dashboard
- **model tier:** cheap background evaluator for normalized page/file/system predicates; realtime only for setup questions and final spoken notification
- **latency:** Evaluate local/browser events within 2 s of observation; execute a prepared action within 5 s; retain durable watches for weeks without model polling
- **cost:** <$0.01 per event using deterministic predicates; occasional semantic page interpretation may cost <$0.02. The relay’s durable watch storage is the main non-model cost.
- **security:** Watch definitions and resulting evidence may contain private URLs, filenames, and page data. Keep selectors and raw snapshots local where possible, encrypt relay state, scope each watch to one browser session/project, and never allow a watch to silently submit an external side effect after session renewal or a changed page shape.
- **missing:** A cross-surface predicate/watch schema for browser DOM evidence, local files/processes, network, project, and job state; Event subscriptions from browser heartbeat/results and Mac filesystem/job telemetry instead of periodic planner polling; Exactly-once trigger leases and durable completion records across relay sleep, Mac restart, and browser reconnect; A prepared-action validator that detects stale selectors, changed files, or expired authentication; Pendant controls for pause, inspect, and disable of a named watch


## Changes it proposed to its own stack

### `integration` — Add a USB-presence session broker that binds /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA to the live Mac agent, exposes framed pendant/bridge telemetry as a local stream, and mirrors only connection state, button edges, audio acknowledgements, and CRC/error counters to the relay. When LTE is absent, route voice and action-status traffic over USB without changing turn IDs; when USB disappears, close the session and let the existing durable outbox resume later.
- **owner gets:** The owner can wear and test the actual pendant today instead of waiting for LTE registration. A button press, spoken turn, and Mac action can work in the same room with truthful offline behavior, and disconnects stop being mysterious because the pendant and dashboard show the exact transport state.
- effort: Medium-high: serial framing/permissions, reconnect state machine, turn-ID mapping, bridge clocking, and integration tests with unplug/replug and partial frames.  ·  risk: A malformed frame or stale reconnect could duplicate audio or button actions. Use CRC, monotonic sequence numbers, bounded frame queues, and exactly-once command IDs; quarantine a device after repeated framing errors and preserve pending records for later replay.
- cost: No API cost for telemetry; roughly 1–2 weeks engineering. Negligible CPU and USB power overhead; existing boards and cables suffice.  ·  latency: USB event-to-relay under 50 ms locally; reconnect recovery under 2 s. LTE remains the fallback when available.
- security: Only authenticated local serial identities and signed/framed payloads should be accepted; never stream raw microphone frames to logs. Relay receives telemetry and audio only under the existing pairing/session key.
- depends on: A real serial diagnostic/streaming tool for the two connected USB devices (requested and still pending); A serial protocol adapter for the nRF9160 pendant and ESP32 bridge; Relay support for a Mac-local USB transport identity alongside LTE/device identity; Integration of the existing truthful_action_status_beacon and audio_link_truth_and_recovery firmware states


## What it asked for

_Nothing._
## Its own summary

Found the live system healthy: Mac agent, relay, and Safari extension are online; FULL_CONTROL_MODE and all relevant macOS permissions are active; active Safari tab is x.com/home with 9 tabs. Recorded three capabilities (return-to-work reconstruction, failure-aware shell repair, and local-first redaction) plus a USB-tethered pendant integration change. The strongest remaining direction is making the physically connected pendant usable over USB today, with no LTE assumption. I still need the already-requested USB serial diagnostics and browser local-artifact export capabilities; I did not re-request them.

**Biggest unknown:** The actual framing/protocol and current firmware behavior on /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA. Without serial diagnostics, I cannot verify button/audio frames, reconnect semantics, or safely bind the live hardware to the Mac relay.

