# Harness derivation — faculty-perception — round 166

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live cross-surface state at 2026-08-08T02:58Z** — Mac agent and browser bridge are live; /observe reports inputReachability=verified, Accessibility and Screen Recording granted, and /ops/snapshot reports relay reachable with D1, but the Mac agent itself has no /v1/devices/status route. Browser has one online Safari device on x.com with 9 tabs and zero pending commands. Pipeline history includes a run marked 'Response waiting for the pendant' and a separate nrf9160 alert_delivered event, but no current pendant registry proof.
  - evidence: GET /ops/snapshot, GET /observe, GET /browser/status, GET /pipeline returned 200; GET /v1/devices/status returned 404 on the Mac agent.

## Capabilities it proposed

### "Tell me only when the system's surfaces disagree about whether something happened, and say exactly which claim is stronger."
- **useful because:** Today a pipeline can say 'completed' or 'waiting for the pendant' while the relay only accepted bytes and the device may be absent. A contradiction-first answer prevents the owner acting on a false completion, without making them read a whole digest.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background for continuous comparison; realtime only to speak a one-sentence incident when confidence changes
- **latency:** Under 2 seconds after a new event; no polling faster than each surface's existing heartbeat
- **cost:** Near-zero when event-driven; one short realtime turn only for an owner-facing alert, roughly a few cents depending on audio duration
- **security:** Compare opaque IDs, timestamps, stage names, and delivery receipts rather than copying page text or secrets. Require confirmation before turning a contradiction into a retry or external action.
- **missing:** A shared causal event ID carried from relay job through Mac pipeline to pendant playback; A reader that treats device_playback as evidence only when a device-originated event exists; A signed or authenticated pendant-originated playback event; current completed status is not hearing proof

### "Before you act in my browser, tell me if the page I am looking at has changed identity, session, or account since I last approved it—and stop automatically if it has."
- **useful because:** The live browser is on x.com with nine tabs and an online extension, while browser commands can outlive the tab state. This would prevent an action approved for one account, tab, or page from landing on a different logged-in surface after navigation or session drift.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → dashboard
- **model tier:** background deterministic checks (URL/origin/title/tab/session fingerprints); realtime only when an interruption must be spoken
- **latency:** 50–150 ms before each browser action; no model call for unchanged fingerprints
- **cost:** Negligible for hashes and route reads; occasional vision/model escalation costs cents and is only needed when the page is visually ambiguous
- **security:** Never transmit page bodies to the relay for this check. Store HMAC-pseudonymous tab/session identifiers and origin plus redacted locator. Any account change, login wall, or missing proof becomes a hard stop requiring owner confirmation.
- **missing:** A stable, extension-signed page/session identity and monotonic navigation counter on every inspect/result; A precondition field on browser_enqueue_command and an atomic compare-at-execution check; A cross-surface receipt that the Mac vision loop and extension inspected the same tab revision

### "Use the pendant over USB right now even if LTE and the relay are unavailable, then reconcile the conversation with the cloud when it reconnects."
- **useful because:** The hardware is physically testable over USB serial but the nRF9160 has never registered with the relay. Today that makes a connected wearable look absent. A local USB mode would let the owner use the real 24 kHz audio path now, preserve an honest offline transcript/event queue, and catch up later instead of pretending cloud delivery happened.
- **path:** pendant → mac-terminal → mac-planner → relay-realtime → relay → dashboard
- **model tier:** realtime for the live local voice turn; background model for reconciliation and duplicate detection after reconnect
- **latency:** Local button-to-audio response under 500 ms when USB is present; reconnect reconciliation within 30 seconds of relay availability
- **cost:** No cloud cost for local turns except optional transcription/model calls; reconciliation is a small background call. USB serial framing and local audio buffering dominate engineering work.
- **security:** Pair the serial device by hardware identity and explicit owner approval; never accept arbitrary serial commands. Encrypt or redact queued transcripts, cap the queue, and label every result local-only until a relay receipt exists. Do not write routine metadata to the pendant's microSD failure buffer.
- **missing:** A Mac USB-serial transport for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A local voice/session endpoint that speaks the existing 24 kHz PCM/Opus framing without requiring relay registration; A durable, deduplicated reconciliation protocol that maps local turn IDs to relay jobs and emits device playback evidence when connected

### "If I say “lock everything,” let me physically hold the pendant button to quarantine every surface—cancel Mac jobs, revoke browser commands, stop relay speech, and refuse new actions until I unlock it."
- **useful because:** A compromised or misunderstood action path currently spans relay, Mac, and browser. The owner needs one unmistakable physical escape hatch that works even when the screen is unavailable or the network is unreliable.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** firmware state machine plus deterministic relay/Mac/browser handlers; no model call for activation or enforcement
- **latency:** Pendant enters quarantine immediately offline; relay, Mac, and browser converge within one heartbeat or 2 seconds when connected
- **cost:** Negligible runtime/API cost; engineering is protocol and cancellation work, with a bounded offline command journal
- **security:** Use a dedicated long-press/chord and signed monotonic nonce, not speech alone. Quarantine must fail closed, survive reconnect, avoid deleting user data, and require the same physical gesture plus explicit spoken/UI confirmation to clear.
- **missing:** A device-originated signed quarantine/release event accepted while offline; A relay-wide lease that rejects new work and broadcasts cancellation; Mac and browser handlers that cancel pending jobs/commands and report which ones could not be interrupted

### "Before you send, buy, delete, or publish anything, speak me the exact consequence and let the pendant’s physical button approve that exact plan—not a later or different one."
- **useful because:** A screen approval can be stale or ambiguous, and a voice “yes” can be accidentally captured. A nonce-bound physical approval gives the owner a short, auditable moment where the intended consequence, browser state, and action payload are all the same object.
- **path:** relay-realtime → pendant → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** deterministic plan hashing and nonce validation; realtime model only summarizes consequences in one short sentence
- **latency:** Plan-to-spoken summary under 1 second; accept the button only for a 30-second nonce window; reject stale approvals immediately
- **cost:** Near-zero inference cost beyond the normal plan; modest implementation cost for canonicalization, signing, and replay protection
- **security:** Canonicalize and hash the complete action, target, account/session fingerprint, and visible precondition. Never allow approval to authorize a mutated plan; show a refusal if browser state changes. Destructive actions still require confirmation even if a routine previously allowed them.
- **missing:** A firmware button event carrying a monotonic counter and authenticated session nonce; A canonical action digest shared by relay, Mac, and browser before execution; An execute precondition that atomically compares the approved digest with the action actually sent

### "When I walk away, let me press the pendant once and later say “resume what I was doing”; bring back the exact browser tab, Mac files, unfinished plan, and the next safe step without making me explain it again."
- **useful because:** Today browser sessions, Mac jobs, and relay work are separate records, so returning to an interrupted task requires guesswork. A physical handoff would turn leaving the desk into a deliberate checkpoint and make the wearable the owner’s task bookmark.
- **path:** pendant → browser-extension → mac-planner → mac-vision → mac-terminal → relay-realtime → dashboard
- **model tier:** deterministic checkpoint capture and restoration; a cheaper background model summarizes the checkpoint and proposes the next step; realtime speaks only the short resume prompt
- **latency:** Checkpoint completes in under 2 seconds; resume should restore context within 5 seconds, then pause before any external side effect
- **cost:** Small background summarization cost per checkpoint; storage is bounded metadata plus redacted evidence, while browser/Mac restoration dominates engineering
- **security:** Capture URLs and window/session identifiers but redact page bodies, secrets, tokens, and private fields. Restore only the same account/session when fingerprints match; otherwise present a read-only explanation and require approval. Never auto-send or delete on resume.
- **missing:** A cross-surface checkpoint schema linking browser session/tab revision, Mac job/ledger state, relay job, and pendant event; A pendant-originated checkpoint trigger and durable upload queue; Atomic browser/Mac restore preconditions plus a resume receipt that distinguishes restored context from executed action


## What it asked for

_Nothing._
## Its own summary

Established fresh state: the Mac agent is healthy; Accessibility, Screen Recording, input reachability, and all listed automation grants are now verified. Relay is reachable on D1, the browser extension is online on Safari/x.com with 9 tabs and no pending commands, while the Mac agent's /v1/devices/status is definitively absent. Pipeline history still contains completion/waiting-for-pendant claims without current pendant proof. I recorded three capabilities: contradiction-first completion claims, browser session-drift hard stops, and a USB-local pendant mode that can work before relay registration.

**Biggest unknown:** The newly granted read_continuity_snapshot still cannot resolve at runtime (nearest routes are /ops/snapshot and /pipeline), so there is no single authenticated cross-surface read. We also still lack a live, read-only USB serial health view and therefore cannot establish whether either physical chip is currently responding, only that the cloud relay has no pendant registry evidence.

