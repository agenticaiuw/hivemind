# Harness derivation — mac-terminal — round 276

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Run a two-chip bench health check and tell me whether the pendant can hear me, whether the audio bridge can play back, and exactly what failed.”"
- **useful because:** The chips are physically on this Mac now but the system currently treats the pendant as simply offline. This gives the owner a useful, honest answer in minutes: enumerate the USB devices, run the existing dual-UART capture scripts, parse bounded health/counter frames from nRF9160 and ESP32, correlate them with the Mac audio devices, and speak a single diagnosis rather than dumping logs. It is the fastest path from 'connected by cable' to a real end-to-end conversation test.
- **path:** pendant → relay → mac-planner → mac-terminal
- **model tier:** Use the cheap Mac planner and deterministic parsers for port discovery, UART capture, and known frame decoding; use realtime only to turn the resulting structured verdict into a concise spoken answer when asked through the pendant.
- **latency:** 5–10 seconds for port enumeration and bounded captures; up to 30 seconds only when a chip is silent. Never wait indefinitely for a UART.
- **cost:** Usually <$0.01 in model/API cost; most work is local shell I/O and parsing. No audio or raw logs need leave the Mac unless the owner explicitly asks for them.
- **security:** Read-only diagnostic. Keep raw UART logs local, redact tokens/identifiers in the spoken summary, cap bytes and duration, and report 'no frame observed' rather than infer health. This must not claim LTE or wearable operation: USB bench mode is a separate verdict.
- **missing:** A real implementation behind the already-requested bounded USB serial diagnostic schema (the grant is unresolved in the live inventory); A small host-side framing parser for the nRF9160 and ESP32 diagnostic formats; A typed run_bench_health_check orchestration route/tool, which was requested but is still pending

### "“If an action fails, fix it or hand it to the right surface automatically, then tell me what you changed.”"
- **useful because:** Today a failed shell, browser, or iPhone step is a dead end: the owner gets an error and must restate the task. A failure-aware hive would classify the failure from the actual receipt, choose a bounded recovery (retry an idempotent read, switch from structured browser action to vision, reopen a missing app, or ask the relay to wait for the Mac), and stop with a precise explanation when recovery is unsafe. The owner experiences completion instead of brittle automation.
- **path:** relay → mac-planner → mac-vision → browser-extension → ios-control
- **model tier:** Deterministic failure taxonomy and retry/idempotency checks first; gpt-4.1-mini only for visual recovery; gpt-5.6-luna for ambiguous replanning; realtime only for the final low-latency status exchange.
- **latency:** Under 2 seconds for receipt classification; one recovery attempt within 10 seconds; never loop more than twice without stating why it stopped.
- **cost:** <$0.03 typical, dominated by an occasional vision snapshot or replanning call. Deterministic retries and app reopening are effectively free.
- **security:** Only retry operations explicitly marked idempotent; never repeat send/delete/purchase/message actions. Preserve the original and recovery receipts, expose the changed plan to the owner, and keep browser/session data on its existing authenticated surface.
- **missing:** A recovery policy engine that consumes action receipts and labels operations idempotent or non-repeatable; Wiring executionContext's existing retry/idempotency machinery into real /execute jobs; A way for computer_use_task to receive the job abort signal and return structured failure causes; A cross-surface handoff contract so Mac planner can request browser or iOS recovery without losing the original job identity

### "“Make this change everywhere it matters, and prove to me afterward that it actually took effect.”"
- **useful because:** A single successful Mac action is not proof of the owner's real state: notifications may still be enabled on the mirrored iPhone, a browser session may override the setting, or the Mac command may have silently targeted the wrong context. This capability plans a small set of cross-surface mutations, records pre-state, performs them, then independently reads post-state from Mac, browser, and iOS and reports confirmed, unverified, or partial. It turns 'done' into a falsifiable result instead of a green receipt.
- **path:** pendant → relay → mac-planner → browser-extension → ios-control
- **model tier:** Use deterministic pre/post probes and typed actions wherever possible; use gpt-5.6-luna only to map the owner's natural-language scope to surfaces and resolve conflicts. Realtime is only the spoken confirmation/status channel.
- **latency:** 5–15 seconds for Mac/browser changes and verification; up to 30 seconds for iPhone Mirroring. If one surface is offline, return the partial result immediately rather than pretending global success.
- **cost:** <$0.02 for ordinary settings changes; vision is avoided unless iOS or a browser page exposes no structured state. The dominant cost is the optional verification snapshot.
- **security:** Mutations remain under the owner's existing maximum-access policy, but the system must show the exact scope before acting, preserve pre/post receipts, and never claim a surface was changed without a fresh read. Browser credentials and phone content stay on their respective surfaces.
- **missing:** A first-class postcondition/verification field on action plans and receipts; Structured read actions for common Mac, browser, and iOS state that can be compared before and after; A cross-surface transaction coordinator with explicit partial-success semantics and a single job identity; A pendant response format for concise confirmed/partial/unverified results

### "“Hold onto this task and carry it out when the right context appears—only while I’m available, before it expires, and using the browser session that is already signed in.”"
- **useful because:** The owner should be able to delegate intent from the pendant without forcing an immediate action: for example, queue a form draft until the Mac is awake and the right site is open, or ask to send a prepared reply only during a chosen time window. Today the relay, Mac, and browser can each do pieces, but none owns a durable, context-sensitive escrow with expiry, preconditions, and a final handoff back to the owner. This makes the system useful while the owner is walking away from the keyboard without turning an ambiguous command into an unsafe blind automation.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Use a cheap background planner to normalize the intent into explicit preconditions, expiry, and an action graph; use deterministic context watchers and browser/Mac actions to execute; reserve realtime for accepting the spoken request and reporting the final outcome.
- **latency:** Acknowledge the escrow on the pendant within 2 seconds. Evaluate conditions on event arrival or a low-frequency schedule. Once conditions match, execute within 10 seconds and give the owner a short confirmation or a request for clarification.
- **cost:** Usually under $0.02 per escrow, dominated by one planning call; condition checks and job state are local/relay-side. No repeated model call is needed while waiting.
- **security:** Never execute an expired or materially changed intent. Show the exact action, target account/site, preconditions, and expiry in the pending record; require a fresh owner confirmation when the action is consequential or the browser session changed. Keep credentials in the browser and transmit only intent/status.
- **missing:** A durable relay-side escrow record with explicit preconditions, expiry, cancellation, and a stable intent ID; Context events from the Mac (awake/unlocked/active app/network) and browser (session/URL/page state) that can satisfy or invalidate preconditions; A planner/executor contract that revalidates the page and action immediately before dispatch; Pendant UI for listing, cancelling, and distinguishing waiting, expired, blocked, and completed escrows

### "“Make this a private moment everywhere right now, and restore my exact workspace when I say I’m back.”"
- **useful because:** The owner cannot currently make one spoken privacy command cover the Mac display, browser capture/session, iPhone Mirroring, and the pendant's own audio behavior. A hive-level privacy mode would immediately stop screen/browser observation, pause queued remote work, mute or stop spoken output, and obscure sensitive windows; a later return command would restore the prior app/tab/session focus instead of leaving the workspace scrambled. This is a felt benefit when another person walks into the room, not another audit feature.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → ios-control
- **model tier:** Realtime handles the short voice command and immediate acknowledgement; deterministic Mac/browser/iOS actions perform the privacy transition and restore snapshot; no expensive model is needed unless the prior workspace cannot be restored structurally.
- **latency:** Acknowledge in under 300 ms and apply local mute/visual concealment within 1 second. Complete cross-surface suspension within 3 seconds; restore only after an explicit return command.
- **cost:** Near-zero per invocation after implementation; at most one lightweight state snapshot. No cloud transcript or screenshot should be needed for the privacy transition.
- **security:** The privacy command must be recognized locally or with a cached phrase when the relay is unreachable. It must fail closed for capture and speech, avoid persisting screenshots or page text, and make restoration opt-in rather than automatically reopening sensitive content.
- **missing:** A pendant/relay emergency privacy state that takes precedence over active voice and queued jobs; Mac actions for atomic workspace snapshot, concealment, and restore, including browser and iPhone Mirroring state; Browser-extension and iOS hooks that suspend capture/automation and acknowledge the mode; A visible local indication that privacy mode is active even when the network is down

### "“Find the thing I saw last week—search my signed-in browser, Mac files, and recent notes together, show me the evidence, and open the exact place it came from.”"
- **useful because:** Today each surface is searched separately, so the owner has to remember whether a fact was in Safari, a downloaded file, or a local note. A unified personal retrieval action would search only sources the owner already authorized, rank matching claims, retain the source URL/path and timestamp, and let the Mac or browser reopen the exact source. The answer would be grounded in evidence rather than a model's unsupported recollection.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Use local indexes and cheap embeddings/keyword search first; use gpt-5.6-luna only to interpret the natural-language query and reconcile candidates. Realtime is only the voice interface.
- **latency:** Return likely matches in 3 seconds and stream more candidates within 10 seconds. Opening a selected source should take under 5 seconds.
- **cost:** <$0.01 for indexed retrieval; occasional embedding/index maintenance is the dominant background cost. Raw page content remains local to each source.
- **security:** Search only explicitly permitted roots and current authenticated browser sessions; return evidence snippets with source metadata, not broad data dumps. Never index passwords, tokens, or private browser fields, and disclose when a result is only a weak match.
- **missing:** A unified, permission-aware retrieval index spanning local files, browser provenance/findings, and notes; Connectors that emit stable source locators and freshness/deletion updates from each surface; A result schema carrying evidence, confidence, source kind, and an open/reveal action; Pendant-friendly disambiguation when several sources match


## Changes it proposed to its own stack

### `mac-harness` — Run every run_shell action in a dedicated process group with captured PID/exit code and a real deadline signal; persist the original action identity, normalized command fingerprint, start/finish timestamps, and termination reason into the same job and ledger records. On cancel or timeout, kill the process group, settle the receipt, and let the orchestrator close the ledger. On agent boot, reconcile processing jobs and open ledgers into interrupted/terminated states instead of leaving them apparently running forever.
- **owner gets:** A command that hangs, a capture script that waits on an unplugged chip, or a Mac restart will stop being an invisible limbo. The owner can cancel it and trust that it stopped, see whether it timed out or exited 1, and resume only the unfinished work rather than rerunning an unknown side effect.
- effort: Medium: replace exec with spawn/execFile-style process-group supervision, thread AbortSignal, retain exit metadata, close ledgers in orchestrator finally blocks, and add boot reconciliation plus tests for timeout, cancellation, and restart.  ·  risk: Process-group termination can kill descendants the command intentionally launched; preserve an explicit detached opt-out and log the tree. Reconciliation must never auto-rerun mutations; it only marks them interrupted and offers the existing ledger resume path.
- cost: Negligible API cost and no hardware cost; modest local CPU/disk for richer receipts and a bounded process table.  ·  latency: Cancellation becomes immediate instead of waiting up to 120 seconds; normal commands are effectively unchanged.
- security: No new access restriction and no approval gate. Capturing an environment fingerprint rather than raw environment avoids adding secrets to durable records while preserving diagnosis.
- depends on: The existing POST /execute job and action-ledger stores; A stable jobId-to-ledger association in planMeta; The existing GET /ledger/interrupted and GET /ledger/:id/resume recovery endpoints


## What it asked for

_Nothing._
## Its own summary

This round produced three new owner-facing capabilities: (1) a bounded two-chip bench-health verdict (recorded, but flagged close to an existing idea), (2) failure-aware cross-surface recovery that retries only idempotent work and hands off to browser/vision/iOS when appropriate, and (3) postcondition-verified changes across Mac, browser, and iPhone rather than trusting a green receipt. I also recorded a process-group supervision/reconciliation change so hung or orphaned Mac commands become cancellable and truthful. Live discovery confirms Safari and the Mac bridge are online while nrf9160-pendant is relay-offline. The newly granted mac_usb_serial_diagnostics and mac_read_diagnostics schemas still do not resolve against the running inventory, so no serial or host probe actually ran.

**Biggest unknown:** I still need an implemented, bounded USB/UART bench-health route/tool (or a typed run_shell wrapper that can invoke the existing dual-chip capture scripts and parse their frames). The orchestrator has not answered the earlier run_bench_health_check request; I will not re-ask it. Without that implementation I cannot truthfully report microphone/Opus/I2S/bridge health from the physically connected chips.

