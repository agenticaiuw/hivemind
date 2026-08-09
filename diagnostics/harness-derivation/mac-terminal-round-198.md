# Harness derivation — mac-terminal — round 198

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **USB serial bench access** — The granted mac_usb_serial_diagnostics schema is not implemented in the live inventory; a call over all four documented nRF9160/ESP32 ports returned unresolved, so no bounded serial health/frame read is possible this round.
  - evidence: mac_usb_serial_diagnostics({ports:[/dev/cu.usbmodem00096003658,/dev/cu.usbmodem00096003658A,/dev/cu.usbmodem00096003658B,/dev/cu.usbserial-0287A9CA],read_ms:500,max_bytes:4096}) returned resolution=unresolved, nearest action:get_mac_status score 0.226.

## Capabilities it proposed

### "Fix this until it works, and tell me when it is actually done."
- **useful because:** Today a failed shell step becomes a dead job with no exit code, no retry, and no useful recovery. This would turn the Mac into a persistent repair worker: diagnose the real failure, try the next safe remedy, verify the postcondition, and report a truthful success or an exhausted attempt count through the pendant.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension → dashboard
- **model tier:** Use a cheap background model for stderr classification and retry planning; reserve realtime only for the owner's spoken request and final concise answer.
- **latency:** First attempt starts within 2 seconds. Each repair iteration may take up to 2 minutes (matching shell timeout), with a pendant progress pulse and a final answer as soon as verification completes.
- **cost:** Typically 1-3 inexpensive planner calls plus the existing Mac executions; dominant cost is repeated model context and any authenticated documentation page reads, not the relay.
- **security:** The loop can perform multiple unattended mutations under the owner's deliberate FULL_CONTROL policy. It must preserve every attempted command, cwd, exit code, stdout/stderr digest, and postcondition; never claim success from exit code alone. Browser credentials stay in the extension, and only extracted error/procedure evidence leaves it. A configurable attempt/time budget prevents runaway loops.
- **missing:** execFile/child-process receipts with exit code, signal, pid, and bounded stdout/stderr; a retry loop that is actually wired to /execute and can checkpoint between attempts; postcondition assertions over files, processes, browser state, and HTTP health; relay-to-pendant progress events for multi-attempt work

### "Save exactly where I am so I can say 'resume that' later, even after the Mac or browser restarts."
- **useful because:** A real task is split across the owner's foreground app, shell cwd/branch, unsaved files, authenticated Safari tabs, and the spoken context that motivated it. A durable handoff capsule would let the pendant name the task later and have the Mac and browser reopen the same evidence instead of making the owner reconstruct it from memory.
- **path:** pendant → mac-planner → mac-terminal → browser-extension → relay → dashboard
- **model tier:** A small background model should summarize and redact the capsule; realtime is only needed when the owner says resume and expects immediate spoken confirmation.
- **latency:** Capture in under 5 seconds. Resume should restore the shell project and browser session in under 10 seconds, then ask the planner only for unresolved steps.
- **cost:** One short summarization call at capture and one at resume; most work is local metadata and existing browser/session operations.
- **security:** Capsules may contain private tab URLs, repository paths, and command output. Keep raw evidence on the Mac/extension, store only a signed manifest and short summary at the relay, encrypt any pendant copy, and expire capsules by age. Resuming must re-check current branch, files, tab identity, and network rather than blindly replaying old mutations.
- **missing:** a first-class resumable-capsule store with versioned evidence references; Mac capture of foreground app, cwd, git state, and bounded dirty-file hashes; browser session/tab identity and a restore operation tied to existing authenticated sessions; a compact pendant token/label that survives reboot and resolves through the relay

### "Publish this and don't tell me it worked until the real website proves it is live."
- **useful because:** A local command succeeding is not the same as the external result being live. This would coordinate the Mac's repository/build commands with the browser's authenticated deployment or monitoring session, wait for propagation, inspect the actual result, and give the pendant a short success/failure answer backed by URLs and timestamps.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension → dashboard
- **model tier:** Use a cheap background planner for build/deploy polling and page-claim extraction; realtime only handles the spoken request and final answer.
- **latency:** Start immediately; allow a configurable 10-minute propagation window with sparse progress events rather than repeated conversational turns.
- **cost:** One planning call, one or two browser inspections, and local shell work. Polling is mostly cheap HTTP/extension activity; model cost is dominated by interpreting the final page evidence.
- **security:** The browser may hold production credentials and the shell may hold repository secrets. Keep credentials and raw page content on their owning surfaces, pass only claims plus provenance, verify the target project/environment before mutation, and never equate a green local exit code with deployment success. Expire the job if the browser session disappears.
- **missing:** A cross-surface execution contract joining one /execute job to one browser command and one relay job; Browser-side wait/assert operations for deployment status, not only inspection/capture; A provenance-backed postcondition record containing environment, URL, observed status, and timestamp; Pendant progress/completion delivery for long-running jobs

### "When I press the pendant, tell me what is on the screen I am looking at, in one sentence, and let me ask a follow-up without touching the Mac."
- **useful because:** The owner can get immediate, context-aware help while standing away from the keyboard: the Mac supplies the current visual/app state, the browser supplies structured page meaning and provenance when applicable, and the pendant supplies the physical trigger and spoken interaction. Today those surfaces can inspect independently but cannot form one low-friction 'explain this screen' turn.
- **path:** pendant → mac-vision → mac-planner → browser-extension → relay → dashboard
- **model tier:** Use a compact vision/language model for the first screen summary and a cheaper text model for follow-ups; use realtime only for the spoken exchange.
- **latency:** Initial answer within 3 seconds, follow-ups within 1.5 seconds when the screen has not changed; invalidate the summary immediately after a meaningful window/tab change.
- **cost:** One vision/context call per button-triggered snapshot and cheap follow-up calls. Cost is bounded by snapshots, with cached structured browser inspection avoiding repeated screenshots.
- **security:** Screens may contain passwords, private messages, or work data. Process the screenshot locally on the Mac where possible; send only a redacted visual summary and browser provenance to the relay; never persist raw screenshots by default. Require an explicit local privacy mode that suppresses capture.
- **missing:** A pendant-triggered screen-context event carrying a turn ID; A Mac-vision snapshot plus foreground-window attestation joined to the active browser inspection; A relay conversation primitive that retains the snapshot context for follow-up turns without resending the image; A privacy/redaction result and expiry policy for screen context

### "Before I submit this form, tell me exactly what it will send and what will change, without submitting it."
- **useful because:** Authenticated browser forms are one of the highest-risk places for an assistant to act. The owner should be able to use the pendant as a preflight: the browser exposes actual field values and destination, Mac vision identifies warnings or hidden state, and the relay explains the likely consequence in plain speech while leaving the page untouched.
- **path:** pendant → relay → browser-extension → mac-vision → mac-planner → dashboard
- **model tier:** A small text model can summarize structured fields and provenance; use vision only when the page contains canvas/visual warnings. Realtime is reserved for the owner's spoken question.
- **latency:** Under 3 seconds for ordinary structured forms; under 6 seconds when a screenshot is required.
- **cost:** Usually one low-cost summarization call plus browser inspection; screenshots and large forms are the dominant cost and should be capped.
- **security:** Form values may include credentials, financial data, or health information. Keep raw values in the extension, redact secrets before relay/model transfer, show the exact destination and changed fields, and make the operation strictly non-mutating. The answer must distinguish observed fields from inferred consequences.
- **missing:** A browser dry-run inspection that returns field names, values/redaction classes, submit destination, and client-side validation without clicking submit; A structured diff between current form state and the payload the page would send; A provenance-backed explanation of warnings and side effects; A pendant request/response path for long form summaries


## Changes it proposed to its own stack

### `integration` — Add a Mac USB bench gateway that opens the nRF9160 and ESP32 serial devices by stable USB identity, registers them as a temporary local pendant/audio-bridge pair, and forwards authenticated relay events and audio frames over the existing local agent. It should expose a session-scoped packet timeline (sequence, CRC, ACK, latency, drops) and deterministic fixture injection, without pretending the pendant is LTE-registered. On disconnect it emits the same truthful offline state used by the real relay path.
- **owner gets:** The owner can wear and speak to the actual pendant today while it is attached to the Mac, hear the real bridge audio, and find transport failures before trusting an LTE deployment. It turns the physically connected hardware from an inert serial accessory into a testable local version of the product.
- effort: Medium-high: native serial implementation, USB identity matching, framing/CRC parser, local-agent lifecycle, and relay/pipeline adapter; then a small dashboard view for packet traces.  ·  risk: A bad parser could wedge a serial port or feed malformed frames into firmware. Keep the gateway read-only by default, require an explicit fixture mode for frame injection, bound buffers, and tear down both ports on stale heartbeat. Never report LTE registration from USB presence.
- cost: No API model cost for forwarding; modest Mac CPU and under 1 W additional USB power. Engineering cost is the serial framing and integration work.  ·  latency: Local audio/control path should be sub-100 ms; packet trace adds negligible overhead if sampled rather than copying full audio.
- security: The local gateway handles microphone/audio and relay credentials. Keep it loopback-only, use the existing bearer token, redact payload bytes from durable logs, and persist hashes/counters rather than raw audio.
- depends on: A real implementation of the granted mac_usb_serial_diagnostics or an equivalent narrowly scoped serial gateway; Stable framing/CRC specifications for both boards; POST /pipeline/audio and POST /pipeline/events adapters that accept a local bench transport; A temporary device/session registration path distinct from /v1/devices/status, which is currently 404


## What it asked for

_Nothing._
## Its own summary

Recorded two owner-facing capabilities not available today: pendant-triggered explain-this-screen with cached follow-ups, and a non-mutating authenticated browser form preflight that reports the exact payload and consequences. Both require new cross-surface wiring despite many underlying inspection/audio routes existing.

**Biggest unknown:** Whether either idea collides with an unobserved backlog entry; no further discovery is possible this round.

