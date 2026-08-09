# Harness derivation — faculty-perception — round 159

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **macOS input and observation reachability** — As of 2026-08-08T02:37Z, AI Pendant Agent has Accessibility and Screen Recording granted, inputReachability.status=verified, uiActionsWillReachTheScreen=true, secureInputActive=false; Safari browser bridge is online with 9 tabs and zero pending commands. Relay is reachable and Mac bridge online. This is a live cross-surface fact, unlike prior denied state.
  - evidence: GET /observe and GET /ops/snapshot returned HTTP 200; observe reports trusted=true, screenRecording=true, eventsPost=true, inputReachability verified; ops snapshot reports browser online and relay reachable.

## Capabilities it proposed

### "I’m looking at something on my Mac—read the important part to me through the pendant, but skip passwords, one-time codes, and private messages unless I explicitly ask for them."
- **useful because:** The owner can consume a page, dialog, chart, or error while walking or when they cannot stare at the screen. It turns newly verified Screen Recording and Accessibility access into a safe spoken interface, with privacy filtering instead of dumping the screen into the model.
- **path:** pendant → mac-vision → mac-planner → browser-extension → relay-realtime
- **model tier:** Use a small local/cheap vision-text pass for OCR, layout, and secret classification; use realtime only to converse about the selected portion and speak the concise result.
- **latency:** First spoken summary within 2 seconds for a browser page or standard dialog; 4 seconds for a dense screen. If capture is stale or permissions disappear, say that explicitly instead of reading cached text.
- **cost:** Near-zero relay cost for local OCR and redaction; occasional realtime turn around $0.01–$0.05. Screen capture upload is the dominant privacy and bandwidth cost, so keep it local whenever possible.
- **security:** Classify and redact password fields, OTPs, payment numbers, private-message bodies, and hidden off-screen content before any cloud call. Keep only a short hash and app/window metadata by default. Require a deliberate second request to reveal a redacted region, with a spoken warning and no persistence.
- **missing:** A local screen-to-speech reader that consumes the verified /observe and Screen Recording surface; Standardized UI-region redaction labels and a user-visible record of what was withheld; A pendant command for 'read this' that can target the current app, browser tab, or a context-pin region

### "When something goes wrong, tell me what actually happened—not just that it failed: what I said, which tab and app were active, what the Mac attempted, what the relay received, and where the chain broke."
- **useful because:** Today a Mac job marked complete can still mean the pendant never played anything, and a browser command can disappear into a spool. A single spoken incident replay would let the owner recover without reconstructing logs or trusting a misleading completion badge.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension
- **model tier:** Use deterministic event joining and a small summarizer by default; reserve realtime for the owner's follow-up questions. Do not spend the expensive model rebuilding a timeline from raw logs.
- **latency:** Initial answer in under 3 seconds from bounded recent records; deeper replay under 8 seconds. If evidence is absent, name the exact gap and say 'unknown' rather than infer success.
- **cost:** Usually <$0.01 for joining and a cheap summary; $0.02–$0.08 only for a conversational deep dive. The cost is bounded reads, not audio generation.
- **security:** Store event IDs, timestamps, hashes, status, and redacted snippets—not screenshots, full browser text, or audio by default. Separate owner-visible evidence from secrets and preserve source/authentication labels so a Mac assertion cannot masquerade as pendant playback.
- **missing:** A durable correlation ID propagated from pendant utterance through relay pipeline, Mac job, browser command, and playback ledger; A reader that joins /ops/snapshot, /pipeline, /jobs/:jobId/receipts, browser results, and device playback events into one causal timeline; A truthful terminal-state vocabulary distinguishing accepted, executed, socket-delivered, device-received, and owner-heard

### "Keep my private browser and desktop data local by default; if the relay needs context, send only the smallest redacted fact that answers my request, and tell me what crossed the boundary."
- **useful because:** The owner can use powerful cloud voice and browser reasoning without turning every screen, message, or page into a cloud transcript. This is a felt daily benefit: fewer accidental leaks and a clear explanation when information leaves the Mac.
- **path:** pendant → mac-planner → mac-vision → browser-extension → relay-realtime
- **model tier:** Run secret detection, minimization, and policy decisions locally with deterministic rules plus a cheap classifier; send only approved summaries to realtime. Never ask realtime to decide whether raw secrets are safe to upload.
- **latency:** Under 300 ms for common local redaction; under 2 seconds when a browser region needs inspection. A missing classification or stale browser heartbeat blocks upload and yields a local explanation.
- **cost:** Most requests incur no extra model cost; occasional local classifier work is negligible. Cloud voice cost is reduced because only compact, redacted context crosses the link.
- **security:** Default-deny for passwords, OTPs, payment data, private messages, and hidden DOM. Attach sensitivity, origin, hash, and redaction counts to every outbound context capsule; retain an owner-readable audit trail with bodies withheld. Explicitly confirm before revealing a withheld region.
- **missing:** A mandatory local egress gate wrapping relay voice, web-read, browser, and planner inputs; One sensitivity taxonomy shared by evidenceCapsules, browser provenance, Mac vision, and relay payloads; A small spoken disclosure receipt such as 'title and 42-word summary sent; 3 secrets withheld'

### "Stop everything now—cancel anything pending, prevent new browser or Mac actions, and tell me what was already sent or changed."
- **useful because:** A spoken emergency stop is the fastest recovery from a mistaken instruction, compromised session, or simply realizing the wrong thing is happening. It must distinguish canceled work from irreversible changes instead of claiming that 'stop' undid the world.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision
- **model tier:** Implement the stop path as deterministic, authenticated control-plane logic; use realtime only to summarize the resulting state. No model should be required to decide whether cancellation succeeded.
- **latency:** Pendant-to-local-Mac cancellation under 500 ms when connected; relay cancellation under 2 seconds; report partial containment immediately if a link is down.
- **cost:** Negligible API cost; one short spoken summary. The valuable work is local queue cancellation and browser command revocation, not inference.
- **security:** Require a physical button hold or owner voice authenticated on the active session; do not let arbitrary page text trigger it. Use a monotonic emergency epoch so queued commands from before the stop are rejected after reconnect. Log only command IDs and outcomes, not page contents.
- **missing:** A cross-surface emergency epoch checked by Mac executor, relay scheduler, and browser extension; Idempotent cancel/revoke endpoints for every pending Mac job, relay job, and browser command; A pendant-local offline stop latch that survives a dropped relay link and reports partial versus complete containment

### "Put me in private mode for the next hour: keep listening for my local stop gesture, but do not send microphone, screen, browser, or message content off this Mac; when I leave private mode, show me exactly what was held and what was discarded."
- **useful because:** The owner gets a dependable physical privacy boundary instead of hoping each feature remembered to redact. They can walk into a meeting or handle sensitive material without unplugging the system, while retaining a clear account of what never left the device.
- **path:** pendant → mac-planner → mac-vision → browser-extension → relay-realtime → dashboard
- **model tier:** Make the privacy latch and egress enforcement deterministic firmware/Mac policy, not an LLM decision. Use a cheap local summarizer for the exit report; realtime is used only if the owner asks a spoken follow-up.
- **latency:** The local latch must take effect within 250 ms and block new uploads immediately, even with the relay unavailable. Exit report in under 3 seconds from bounded counters and hashes.
- **cost:** Negligible API cost while private mode is active; local metadata accounting is cheap. The cost is implementation across every egress path, not inference.
- **security:** The latch must be monotonic and fail closed across reconnects, queued jobs, browser spool, and relay retries. Store only counts, command IDs, timestamps, and content hashes; never retain blocked raw audio or screen data merely to explain it. Require a deliberate physical gesture or a locally authenticated command to exit.
- **missing:** A device-originated privacy epoch that Mac, relay, browser extension, and audio/upload paths must enforce before sending bytes; A single egress broker covering realtime audio, screenshots, browser captures, pipeline audio, and queued commands; A durable, owner-readable private-mode receipt distinguishing blocked, locally processed, discarded, and already-transmitted data

### "Let me hand you a task while I am offline, but do not execute it until every required precondition is freshly true; if any precondition fails, explain which one and leave the task untouched."
- **useful because:** The owner can delegate useful work across sleep, travel, and intermittent connectivity without turning an old instruction into a dangerous surprise. It makes deferred autonomy conditional and inspectable rather than merely queued.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheap deterministic condition evaluator and signed state checks; use realtime only to capture the owner's natural-language task and explain a blocked condition.
- **latency:** Persist the request locally and at the relay within 1 second when connected; evaluate conditions on each relevant state change; execute only after a fresh all-clear, otherwise notify within 5 seconds.
- **cost:** Low: one short realtime turn at creation and occasional cheap condition evaluation; no repeated expensive model calls while waiting.
- **security:** Conditions must be explicit, typed, and expire. A stale browser login, changed recipient, missing attachment, or revoked permission must block execution. Keep secrets on the owning surface and make cancellation monotonic across reconnects.
- **missing:** A signed precondition language spanning time, app state, browser origin, account identity, and device health; A durable deferred-intent record with leases, expiry, cancellation epoch, and per-condition evidence; A relay/Mac executor that refuses to run an intent whose evidence is stale, even if a queued job says ready

### "When I ask whether something is safe to share, give me a concrete boundary report: which device saw it, which model received it, what was removed, where it is stored, and when it will stop being available."
- **useful because:** The owner can make informed decisions about private material instead of accepting an opaque 'secure' label. This is especially valuable when voice, browser sessions, Mac automation, and a cloud relay cooperate on one request.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Generate the report from signed structured telemetry with a cheap summarizer; never ask a language model to reconstruct data-flow facts from prose logs.
- **latency:** Answer in under 2 seconds for the current turn and expose a durable receipt immediately after the operation. If retention or downstream processing is unknown, say unknown rather than inventing a policy.
- **cost:** Negligible incremental model cost; compact event receipts reduce later context and support cheap summaries.
- **security:** Receipts must not echo the sensitive content they describe. Use content hashes, sensitivity labels, processor IDs, timestamps, retention commitments, and revocation status. A receipt itself should be access-controlled and deletable without deleting the underlying compliance record prematurely.
- **missing:** A signed data-lineage envelope propagated with audio, screen, browser, and planner payloads; A relay-to-Mac retention registry that reports actual deletion/expiry rather than advertised TTLs; A dashboard and spoken query surface for per-turn data-flow receipts


## What it asked for

_Nothing._
## Its own summary

Established fresh live state: Mac agent is fully permission-ready (Accessibility, Screen Recording, Automation; inputReachability verified), Safari bridge is online with 9 tabs and zero pending commands, relay is reachable, and Mac bridge is online. Recorded three new owner-facing capabilities: private screen-to-pendant reading with redaction, truthful cross-surface incident replay, and deterministic emergency stop with an offline epoch. The granted read_continuity_snapshot tool remains unresolved by the live resolver, so /ops/snapshot was used directly instead.

**Biggest unknown:** There is still no live nRF9160 pendant in the relay registry, and no authenticated cross-surface correlation/playback evidence. We need the pendant to register and emit the accepted playback ledger before claiming anything was physically heard.

