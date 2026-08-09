# Harness derivation — mac-terminal — round 227

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “do this from the pendant,” make it a single tracked transaction: capture my spoken intent, let the Mac or browser act, and tell me exactly once whether it completed, failed, or is still waiting—even if the USB link drops."
- **useful because:** This is the core thing no isolated node can provide: the pendant is the only always-with-owner input, the Mac/browser hold the private sessions and execution reach, and the relay must preserve the transaction across disconnection. It prevents duplicate purchases/messages and stops the owner wondering whether an action happened.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → unified
- **model tier:** Realtime only for intent extraction and the one-sentence spoken acknowledgement; use the cheaper background tier for execution planning, receipt reconciliation, and retry classification.
- **latency:** Acknowledge queued/dispatched locally within 300 ms; execute in the background; speak completion within 1 s of the durable receipt arriving. USB loss must not create a second execution.
- **cost:** About $0.01–$0.04 per invocation depending on whether speech needs realtime inference; most retries and receipt reconciliation are local code and negligible.
- **security:** The intent and action receipt leave the pendant to the relay; browser pages and shell outputs may contain secrets and must be redacted in the spoken/log view. Sending mail, deleting files, purchases, and other destructive actions still require the owner's existing confirmation policy. Exactly-once keys must be persisted before dispatch.
- **missing:** A durable transaction record joining pendant turn ID, relay job ID, Mac job ID, browser command ID, and final receipt; A reconnect reconciler that maps queued/offline intent to one execution and rejects stale duplicate IDs; A compact receipt endpoint that the pendant can fetch and cache without replaying full shell/browser output

### "Run a bench call now: use the connected nRF9160 pendant and ESP32 bridge, stream a short 24 kHz superwideband audio round trip, and tell me whether capture, encoding, USB transport, decoding, and playback each passed."
- **useful because:** The hardware is physically present today but LTE is not registered. This gives the owner a real end-to-end acceptance test instead of a false “online” claim, and isolates whether a bad call is codec, framing, UART, relay, or speaker playback.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal
- **model tier:** Use deterministic host scripts and a cheap background evaluator for frame counters/latency; use realtime only if the owner asks for a spoken interpretation of the test.
- **latency:** Start within 2 s, run a 10–20 s fixture, and report per-stage pass/fail plus round-trip latency within 5 s of completion.
- **cost:** Near-zero model cost when deterministic; under $0.01 for optional summarization. It consumes USB power and roughly one short audio fixture, not a live microphone session.
- **security:** The fixture must be synthetic or a locally selected test phrase, never an unattended open microphone. UART logs can contain identifiers and should remain on the Mac unless the owner explicitly asks to upload them. The result must say “bench USB only,” never imply LTE wearable readiness.
- **missing:** A bounded, read-only serial/frame health action implemented over the existing run_shell path for the two known ports; A canonical 24 kHz test fixture and framing parser shared by nRF9160 and ESP32; A result schema with stage counters, CRC/frame loss, codec timing, and explicit USB-versus-LTE transport label

### "I’m leaving the Mac—give me a two-sentence handoff of what I was doing, what is waiting on me, and the exact browser tab or file to resume from the pendant; when I return, restore that handoff instead of making me reconstruct it."
- **useful because:** The pendant and relay can preserve continuity when the owner physically moves away, while the Mac and browser are the only nodes that can see the focused editor, private tab, and unfinished local jobs. This is not a bookmark: it is a live, expiring work-state handoff with an explicit resume target and pending-human-action list.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → unified
- **model tier:** Use deterministic collection for focused app, active tab metadata, open jobs, and recent receipts; use the background tier to compress that into a short handoff. Realtime is only for the pendant's spoken readout or a follow-up question.
- **latency:** Capture in under 1 s when requested; speak the two-sentence handoff within 2 s. On return, offer restoration in under 3 s, without auto-submitting any pending form or message.
- **cost:** Usually under $0.01 per handoff; the expensive model is unnecessary unless the task state is ambiguous or spans many tabs.
- **security:** Private URLs, filenames, and page titles stay in the relay only as encrypted, expiring metadata; never include page bodies or credentials in the voice summary. Restoring may focus/open a tab or file, but sending, deleting, purchasing, or submitting remains behind the existing owner policy.
- **missing:** A cross-surface handoff record with TTL, owner-visible summary, focused-app/tab/file locators, pending job IDs, and a resume-safe state; Mac capture of focused editor/file and active Safari tab metadata at the exact request time; A resume endpoint that validates the tab/file/job still matches before focusing it and reports drift instead of silently acting

### "After you do something for me, prove that the result actually exists—not just that the command returned success. For example, verify that the file is where it should be, the browser portal shows the new state, or the message appears in Sent, then tell me “verified” or “not verified” from the pendant."
- **useful because:** Today execution success is often mistaken for world success: a shell command can exit zero before a file is durable, a browser click can be accepted without the server committing it, and a network loss can hide the outcome. Independent postcondition checking would prevent false confidence, especially for work initiated hands-free from the pendant.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → faculty-perception → faculty-action
- **model tier:** Use deterministic postcondition probes wherever possible: filesystem stat/hash, browser re-read of the relevant structured field, or a second read-only API check. Use the background tier to choose and explain ambiguous evidence; reserve realtime for the concise spoken result.
- **latency:** Announce “checking” immediately, then verify within 2 seconds for local files and under 8 seconds for browser/server state. If verification times out, say unverified rather than guessing or retrying a side effect.
- **cost:** Usually negligible for local checks; roughly $0.005–$0.02 for an ambiguous browser-result interpretation. The dominant cost is an extra browser or Mac read, not model inference.
- **security:** Verification may reread private browser pages or sensitive files, so retain only a redacted claim, locator, timestamp, and evidence hash. Never treat a matching screenshot or stale cache as proof; require a fresh source and clearly label partial evidence. Verification must never repeat the original mutation.
- **missing:** A typed postcondition model for file, browser-field, message, and job outcomes with freshness requirements; A read-only verification phase attached to each executable action and persisted with the action receipt; A compact evidence capsule that the relay can send to the pendant without exposing page contents or shell output


## What it asked for

_Nothing._
