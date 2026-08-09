# Harness derivation — mac-terminal — round 228

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live USB diagnostic capability** — The granted mac_usb_serial_diagnostics tool is still unresolved against the live inventory, so no serial bytes were read this round. The device inventory reports only Safari on MacIntel, home-macbook-bridge online, and cloudflare-contract-test offline; it does not expose the two physically connected serial devices as a callable capability.
  - evidence: mac_usb_serial_diagnostics call returned unresolved; best match action:get_mac_status score 0.226. devices discovery returned only the three listed devices.

## Capabilities it proposed

### "Are the pendant and audio bridge healthy right now, and can they carry a complete voice turn? If I plug them in, run a bounded dual-chip bench test, identify which side failed, and give me one concrete fix."
- **useful because:** The owner currently has two physically connected boards but no truthful end-to-end answer short of manually reading UART logs. This turns today's real USB setup into a one-command confidence check for power, enumeration, framing, audio timing, and relay-independent voice continuity.
- **path:** mac-planner → mac-terminal → relay-realtime → unified
- **model tier:** Use deterministic shell/serial parsing for enumeration, counters, CRCs, frame timing, and known firmware health markers; use a cheap background model only to translate a structured failure into a likely fix. Realtime is unnecessary unless the owner asks by voice.
- **latency:** Start within 1 s, collect 5–10 s of bounded UART data, and report a diagnosis within 15 s. Never leave a capture process running after the test window.
- **cost:** Near-zero model cost for healthy runs; roughly $0.00–$0.02 only when translating an unfamiliar failure. Dominant cost is the fixed 5–10 s hardware observation window.
- **security:** USB logs can contain identifiers and raw diagnostic text; keep them local by default and send only parsed counters/error classes to the relay. Do not flash firmware or modify devices as part of health checking. Require a separate explicit request for any repair or reset action.
- **missing:** A real bounded serial-read capability or typed wrapper over run_shell that can open the two known /dev/cu ports without shell-string parsing; A framing parser for the nRF9160 and ESP32 diagnostic protocols and a shared health schema; A deterministic test command that injects a short loopback/audio stimulus without opening the owner's microphone; A cross-chip correlation ID so the Mac can distinguish stale boot logs from this test run

### "Stop the thing you just started when I tap the pendant's cancel control, even if the Mac command is still running, and tell me whether it actually stopped or merely finished before the cancel arrived."
- **useful because:** A spoken assistant can start an irreversible or simply annoying Mac/browser operation and then leave the owner waiting. A physical cancel path is the one advantage of a wearable: it works without finding the right window, and it closes the current gap where POST /jobs/:jobId/cancel only sets a cooperative signal while run_shell continues for up to 120 seconds.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → unified
- **model tier:** Deterministic transport and process-group cancellation; realtime only speaks the short result. No model is needed to decide whether a kill succeeded.
- **latency:** Button acknowledgement under 200 ms; send cancel under 300 ms; terminate the child process group within 1 s and report verified state within 2 s.
- **cost:** Negligible API cost and storage. The work is firmware event handling, relay routing, and Mac process supervision.
- **security:** A stale or duplicated cancel must not affect a later job: bind it to the active job ID and monotonic generation, reject expired IDs, and have the Mac verify the process is gone before reporting stopped. Browser cancellations should stop the queued command, not claim that a remote site reverted a partial mutation.
- **missing:** A dedicated second-button or existing cancel intent mapping that does not delay sw0's active-edge recording behavior; Relay event routing for a signed cancel carrying job ID, generation, and timestamp; Mac execution using a tracked process group and actual kill/wait semantics rather than execAsync without signal; A terminal job state distinguishing stopped, completed-before-cancel, and cancellation-requested-but-unverified

### "When you change something in an authenticated web page for me, prove that the requested state is now true, tell me exactly what changed, and if the page disagrees or the session expired, stop claiming success and tell me what remains."
- **useful because:** Browser automation today can dispatch a click or fill, but the owner needs a trustworthy outcome rather than a click receipt. The browser can observe the postcondition, the Mac can retain the session and undo metadata, the relay can report failure while away from the screen, and the pendant gives a concise spoken result.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision → unified
- **model tier:** Use deterministic before/after selectors, network/result status, and page assertions first; use a cheap model only to map a natural-language request to a candidate postcondition. Realtime is limited to the spoken summary.
- **latency:** Preview the intended change in under 2 s, perform it in the site's normal latency, and verify within 2 s of the action settling. If verification cannot run, report 'unverified' rather than success.
- **cost:** Usually no extra model call beyond planning; $0.00–$0.03 when semantic postcondition extraction is needed. Browser observation dominates latency, not tokens.
- **security:** Authenticated pages and post-change values are private. Store selectors, hashes, and provenance rather than full page contents; redact secrets and one-time codes. Verification must not cause a second mutation, and any undo must be a separately identified action.
- **missing:** A browser action contract with explicit precondition, mutation, postcondition, and evidence fields; A structured browser assertion primitive that can re-read the target after navigation/network settling; A receipt that binds browser evidence and provenance to the Mac job and spoken report; A three-state result (verified, failed, unverified) propagated to the pendant instead of binary success

### "If I ask from the pendant, 'finish this when my Mac is available,' queue the work safely, wake or wait for the Mac, use my existing browser sessions when it returns, and tell me whether it finished before the deadline without keeping me connected."
- **useful because:** The owner's Mac is not always awake or online, while the relay and pendant can remain reachable. This would make the hive useful away from the desk: a request becomes a durable, deadline-bound handoff instead of failing because the local executor is asleep. It is materially different from a scheduled reminder because it carries the owner's live intent, browser context, and a verifiable result.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Use a cheap background model for decomposition and retry-safe planning; use realtime only to capture the short request and announce completion. The relay should perform deterministic lease, deadline, and retry management.
- **latency:** Acknowledge and persist the request in under 500 ms. Resume within 10 s of the Mac becoming reachable; announce a result within 5 s after browser verification. Never wait synchronously on the pendant.
- **cost:** About $0.01–$0.05 per deferred task, dominated by planning or browser interpretation; reconnect polling and durable state are negligible. Healthy deterministic tasks should incur no realtime generation after dispatch.
- **security:** The relay must not copy authenticated page contents into durable cloud state. Store a capability-scoped task lease and opaque browser-session reference; execute only against the originally bound Mac/browser session and expire it at the deadline. A resumed task must re-check preconditions because the page may have changed. Require explicit confirmation for any newly discovered high-impact mutation, but do not gate ordinary trusted execution.
- **missing:** A durable relay-side deferred-work queue with deadlines, leases, and exactly-once or explicitly replay-safe semantics; Mac sleep/wake and reachability integration, including a local agent heartbeat and an OS wake mechanism where supported; A browser-session capability lease that can be resumed without exporting cookies or page contents; A result protocol that distinguishes completed, expired, blocked-by-precondition, and never-started; Pendant offline acknowledgement and later spoken completion tied to the original request ID

### "When I come back to my Mac, tell me only what changed while I was away: actions the system completed, browser pages or jobs that changed, anything that expired or needs my decision, and where I left off."
- **useful because:** The owner should not have to reconstruct a distributed system's history from jobs, browser tabs, and voice turns. This is a return-to-context capability spanning the always-awake relay, the wearable's departure/return signal, the Mac's local records, and authenticated browser sessions. It is not a calendar briefing: it reports changes caused by or relevant to this hive since the owner's last presence.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Collect events deterministically and summarize with a cheap background model. Use realtime only for the short spoken digest when the owner asks or reconnects; never spend the expensive tier on collecting state.
- **latency:** Detect return within 2 s of the Mac/pendant becoming available, build the digest in under 5 s, and speak it in under 30 s. If evidence is incomplete, say so explicitly.
- **cost:** Roughly $0.005–$0.03 per return, dominated by summarization; event collection and deduplication are local and inexpensive.
- **security:** Do not send unrelated private browser content to the relay. Keep an append-only local event cursor and transmit only event types, titles, timestamps, and redacted outcomes. The digest must label inferred versus observed facts and never imply a browser change from a queued command alone.
- **missing:** A presence/session boundary shared by pendant and Mac, with explicit away and returned timestamps; A normalized event stream joining voice turns, Mac jobs, browser commands, page-watch changes, and relay delivery state; A local change cursor with durable acknowledgement so the same event is not spoken twice; A summarizer that can cite the underlying job or provenance record for every spoken item

### "If I start using the same Mac or browser window while you are working, yield immediately, preserve your place, and tell me whether I can take over or whether you need me to finish one specific step before you resume."
- **useful because:** An assistant that competes with the owner's hands is unsafe and frustrating even when every individual action is authorized. The Mac can detect foreground/window and input ownership, the browser extension can detect human DOM events, the relay can preserve the task lease, and the pendant can announce a clean handoff without making the owner hunt for a job ID.
- **path:** pendant → mac-planner → mac-vision → browser-extension → relay-realtime → unified
- **model tier:** Use deterministic input/window/session conflict detection and task checkpointing. A cheap model may explain the one blocked step; realtime only announces the handoff. No expensive model should decide whether a human is actively using a window.
- **latency:** Detect competing human input within 100 ms for local UI events, pause dispatch within 300 ms, and speak a handoff status within 1 s. Resume only after an explicit owner command or a quiet-window policy expires.
- **cost:** Negligible inference cost in the normal path; at most $0.005 for an explanatory summary. The main work is event plumbing and checkpoint state.
- **security:** Do not capture keystrokes or page text merely to detect control. Use window focus, accessibility event types, browser event metadata, and coarse timestamps. A human takeover must revoke the automation lease so delayed commands cannot land after the owner edits the page.
- **missing:** A shared per-window/per-tab automation lease with revocation and generation numbers; Mac Accessibility event monitoring that reports focus and human interaction without recording key contents; Browser extension hooks for human DOM/input activity and navigation races; Checkpoint/resume contracts for browser and Mac actions, including a non-resumable state that requires a fresh plan; A pendant status message that distinguishes paused-for-owner from failed


## What it asked for

_Nothing._
