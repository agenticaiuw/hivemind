# Harness derivation — mac-terminal — round 259

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live hardware reachability** — The live device inventory reports Safari on MacIntel with 2 tabs online and home-macbook-bridge online, but the granted bounded USB serial diagnostic cannot resolve to any live capability. Therefore I cannot honestly claim a UART frame or chip health from this round.
  - evidence: discover(devices) returned Safari on MacIntel online and home-macbook-bridge online; mac_usb_serial_diagnostics returned unresolved with nearest action:get_mac_status score 0.225.

## Capabilities it proposed

### "When something I asked you to do fails, fix it instead of merely telling me it failed."
- **useful because:** Today a failed shell or browser step strands the owner with an opaque error and no next move. This capability would classify the failure, gather the missing evidence, choose a bounded alternative (including a browser or Mac route when the first surface is wrong), and return one truthful result rather than blindly rerunning a side effect.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background model for diagnosis and repair planning; realtime only for the short voice acknowledgement.
- **latency:** Acknowledge within 1 s; diagnose and repair within 30 s for ordinary Mac/browser failures, with progress updates on the pendant.
- **cost:** About $0.01–$0.08 per recovery, dominated by the diagnostic model and any browser page snapshot; no cost for already-captured job receipts.
- **security:** The repair engine must distinguish safe re-reads from side effects, carry the original job's sensitivity into every fallback, and never claim success without an independent postcondition. Shell output and authenticated page content stay on the Mac/browser surfaces; require explicit owner confirmation only where the existing action semantics already demand it.
- **missing:** durable failure taxonomy with exit code, signal, stderr and normalized cause; a recovery plan attached to the original job and ledger, with loop/de-duplication limits; postcondition checks for common Mac and browser actions; an executor API that can launch a replacement action while preserving the original audit chain

### "Don't tell me an action is done until you can prove the result is visible where I asked for it."
- **useful because:** A command can exit zero while changing the wrong project, a browser click can hit a stale tab, and a Mac window can open behind another app. Independent verification prevents false completion and lets the pendant's completion beacon mean something the owner can trust.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Cheap background verifier with deterministic checks first; realtime speaks only the final proof or the exact uncertainty.
- **latency:** Verify within 3 s for local UI/file actions and 8 s for browser-backed actions; if verification cannot complete, report 'unverified' rather than retrying blindly.
- **cost:** $0.001–$0.02 per action when deterministic checks suffice; page snapshots and vision are the dominant cost.
- **security:** Verification must not leak page contents into relay logs. Store hashes, titles, app/window identifiers, URLs and narrow predicate results rather than screenshots by default. The pendant must receive a three-state result (proven, failed, unverified), never a fabricated completion.
- **missing:** a declarative postcondition schema for shell, file, UI and browser actions; Mac probes for foreground app/window and file hashes, plus browser predicates scoped to the originating tab; receipt fields linking the attempted action to its proof artifact and timestamp; firmware mapping for proven versus unverified without colliding with recording and inbox patterns

### "While you're working on my Mac or in a browser, let me interrupt and redirect the task by speaking naturally: 'stop searching that site and use the other tab instead.'"
- **useful because:** Long computer tasks currently force the owner to wait, cancel ineffectively, or start over. A pendant interruption should preserve completed work, stop at the next safe action boundary, incorporate the correction, and continue with the same job identity and context across the Mac and authenticated browser.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime model parses the short interruption and acknowledges it; a cheaper planner recompiles only the remaining steps using the existing job context.
- **latency:** Acknowledge in under 500 ms, reach a safe boundary in under 2 s, and resume within 5 s unless the current action is non-interruptible.
- **cost:** $0.005–$0.04 per redirect, dominated by replanning the remaining steps; negligible cost for the event and existing snapshots.
- **security:** The correction must be scoped to the active job and owner session, with an immutable record of what already ran. Never rewind or duplicate side effects. Sensitive browser text stays in the browser harness; the relay carries only the correction, job ID and compact state summary.
- **missing:** a live job-control channel from relay/pendant to the Mac executor; step-level pause points and an explicit non-interruptible action contract; replanning that consumes completed ledger steps without redoing them; a compact pendant protocol for correction text and acknowledgement

### "Let me approve a sensitive action by pressing the pendant, then have the Mac and my authenticated browser complete it without making me type a password or read a one-time code aloud."
- **useful because:** Today the pendant can ask for work and the Mac/browser can act, but there is no trustworthy physical confirmation that binds the owner's hand to one exact pending action. This would make high-consequence workflows—sending a prepared message, submitting a purchase, changing an account setting, or approving a release—fast and usable while keeping credentials inside the browser session.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime tier handles the short confirmation exchange; deterministic Mac/browser execution performs the prepared action, with a background verifier checking the expected account and target before reporting completion.
- **latency:** Show the pending action on the pendant within 1 s, accept the button confirmation within 500 ms, and complete ordinary browser submission within 10 s.
- **cost:** $0.002–$0.02 per approval; cryptographic challenge and deterministic checks dominate neither API nor device cost.
- **security:** Bind the press to a nonce, exact action digest, target origin/account, expiry and one-time use; refuse stale, changed, or cross-session approvals. Never transmit passwords, OTP contents, or unrestricted page text to the relay. A lost pendant must be revocable, and offline presses must not authorize later-mutated work.
- **missing:** a pendant-backed asymmetric key or secure enclave and signed challenge-response protocol; relay support for displaying a canonical action summary and issuing a one-time nonce; browser extension support for origin/account binding and WebAuthn-like submission without exposing credentials; Mac executor support for atomic approval-to-dispatch and immutable action-digest receipts; recovery and revocation UI in the dashboard


## Changes it proposed to its own stack

### `mac-harness` — Add a durable, content-addressed execution capsule for every run_shell action: preserve the exact pre-rewrite action, the post-rewrite action actually dispatched, resolved cwd, argv/shell mode, environment key names with secret values replaced by HMACs, PID/process-group, start/finish monotonic times, exit code or terminating signal, bounded stdout/stderr artifact hashes, and a replay/diagnostic token. Join that capsule to the job, receipt, and ledger IDs before dispatch; mark cancellation as requested, delivered, or ineffective.
- **owner gets:** When the Mac says 'failed' or 'done', the owner can finally ask what actually ran, in which project, and whether cancellation worked—without exposing API keys or losing the evidence when output is large. It also makes the repair and proof capabilities above possible instead of guessing from a flattened error string.
- effort: Medium: change computerControl runShell to spawn with argv/process-group metadata, add redacted capsule storage and receipt joins, then expose read-only retrieval through existing job/receipt routes. Add tests for rewrite, timeout, signal, >64KB output, and process-tree cleanup.  ·  risk: Capturing too much command output could retain secrets or fill the workspace; cap and redact aggressively, hash large artifacts, and rotate capsules with jobs. Process-group termination can kill intentional children; keep current execution semantics by making cleanup evidence-first and only add killing as an explicit future operation.
- cost: Low disk and CPU overhead (typically under 50 KB metadata plus bounded output per action); no model cost. HMAC uses an existing local secret and never stores environment values.  ·  latency: Under 20 ms metadata overhead before/after a shell action; no added conversational latency unless the owner requests the capsule.
- security: Improves auditability while reducing secret exposure: environment values are never persisted, command text can be redacted by sensitivity class, and retrieval remains bearer-authenticated. The raw child still has current maximum access, unchanged.
- depends on: stable job↔ledger ID propagation; a real closeLedger call on every execute outcome; bounded artifact storage and retention policy; spawn/exec implementation that reports exit status and supports process-group identity


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing capabilities: failure repair rather than opaque failure, independent proof before completion, and spoken mid-task redirection across pendant/Mac/browser. I also proposed a Mac execution capsule that preserves pre/post-rewrite commands, exit signal, process identity, redacted environment fingerprints, bounded output evidence, and truthful cancellation state. The live inventory says the Mac bridge and Safari are online, but the granted USB diagnostic still has no implementation, so I recorded that no UART/chip health was established.

**Biggest unknown:** The key missing fact is whether the physically connected nRF9160 and ESP32 are enumerated and producing valid frames. I still need a real bounded serial diagnostic implementation (or a narrowly scoped shell-backed equivalent) before making any claim about bench transport. For the proposed redirect capability, I also need a live relay-to-active-job control channel and the actual semantics of relay_event_push; neither is currently callable.

