# Harness derivation — mac-terminal — round 218

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live USB diagnostics availability** — The newly granted mac_usb_serial_diagnostics still cannot resolve against the live inventory (223 routes/99 actions; best action:get_mac_status 0.226), so no serial frame was read this round. Physical USB remains asserted by system context, but bench truth is unavailable through a typed tool.
  - evidence: mac_usb_serial_diagnostics call returned unresolved with nearestRealCapabilities action:get_mac_status, GET /machine-context, action:check_input_permissions.

## Capabilities it proposed

### "When I say “take care of this” while wearing the pendant, use whatever authenticated browser page I am looking at, make the needed change on my Mac, and tell me exactly what changed (or what blocked it) without making me repeat the context."
- **useful because:** This is the system's defining advantage: the pendant supplies immediate intent, Safari supplies sessions and page state the cloud cannot access, the Mac performs the real action, and the relay returns a concise spoken result. It turns a vague spoken request into a completed cross-surface task rather than another chat answer.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision
- **model tier:** Realtime only for intent capture and the final short spoken acknowledgement; use the cheaper planner/background model for browser-page interpretation, action planning, and verification.
- **latency:** Acknowledge dispatch in under 1 second; begin work within 2 seconds; typical completion 5–20 seconds, with truthful queued/offline status if Safari or Mac is unavailable.
- **cost:** About $0.01–$0.05 per task depending on page interpretation; most steps use the cheaper planner, with realtime tokens limited to two short turns.
- **security:** The browser session may expose private page data to the planner and the requested action may mutate an authenticated account. Keep page text and screenshots on the Mac/relay path, redact secrets from spoken output, retain source URL and action receipt, and use the owner's existing maximum-access policy while stating the exact target before irreversible actions.
- **missing:** A single intent contract joining pendant turn ID, active Safari tab/session, Mac job ID, and spoken result; A browser command that returns a structured mutation receipt plus post-action verification, not only page content; A relay state machine that can keep speaking status updates when the Mac job outlives the voice turn

### "What did you actually change for me today, and show me the evidence for each item? Give me a short spoken list, and let me ask about one item to hear its URL, result, and whether it can be undone."
- **useful because:** The owner currently has to trust that a remote Mac/browser job finished. This turns the distributed system into an accountable assistant: the pendant gives an accessible audit query, the Mac supplies job and action receipts, and the browser supplies provenance rather than an unverifiable summary.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Use a cheap background summarizer over structured receipts; realtime is only for the spoken query, disambiguation, and final answer.
- **latency:** Initial answer under 3 seconds from local job/history indexes; item detail under 2 seconds. Never wait on a live browser round trip when a durable receipt already answers it.
- **cost:** Under $0.01 per query when summarizing structured records; dominated by retrieval, not generation.
- **security:** Only expose records belonging to the owner and avoid reading command environment, tokens, or raw page text into speech. Preserve exact source URL, timestamps, status, reversibility, and post-state; distinguish 'executed' from 'planned' and 'verified.'
- **missing:** A cross-surface evidence index joining job ID, receipt ID, browser provenance record, and pendant turn ID; A speech-safe receipt projection that strips secrets and long stdout while retaining exact failure reason and undo availability; A query route for spoken filters such as today, browser, failed, or undoable

### "Before I rely on the pendant, tell me whether the whole path is healthy right now: pendant input, Mac/relay reachability, ESP32 headphone audio, and the last end-to-end spoken reply. If anything is not proven, say exactly which link failed and what I can still use."
- **useful because:** A wearable assistant is only useful when the owner can trust the path, not merely the cloud health endpoint. This gives one honest readiness answer that combines the physically connected chips, the Mac agent, relay reachability, and recent audio evidence—especially important because the pendant is not LTE-registered today.
- **path:** pendant → mac-terminal → mac-planner → relay-realtime → relay-realtime
- **model tier:** No expensive model for collection: deterministic health probes and counter checks first. Use a cheap model to turn the structured result into a concise explanation; realtime speaks only the final result.
- **latency:** Bench mode under 5 seconds; wearable mode under 2 seconds using cached counters, with a clear 'last proven X minutes ago' age rather than waiting indefinitely.
- **cost:** Negligible API cost; one short summarization call only when the state changes or the owner asks for explanation.
- **security:** Return health metadata, versions, sequence counters and ages—not audio contents or shell environment. Do not claim LTE readiness from USB evidence; label bench-connected, relay-connected, and wearable-registered as separate states.
- **missing:** A real serial health collector for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA (the current typed grant still does not resolve); A shared health schema carrying packet sequence, underrun count, last acknowledged turn, and link kind; A relay endpoint that records the last successful end-to-end audio turn and its age; A deterministic readiness reducer that refuses an overall green result when any required link is stale

### "For the next hour, handle routine browser and Mac work silently, but interrupt me through the pendant only when a decision is genuinely required; bundle low-priority results into one spoken digest, and never wake me twice for the same blocker."
- **useful because:** Today every completion, failure, and browser question competes for the owner's attention, while the pendant is the one surface that can reach them away from the Mac. This makes attention itself an explicit resource: work continues in the background, decisions arrive once, and routine success stays out of the owner's head.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision
- **model tier:** Use deterministic urgency/dependency rules for most events and a cheap background model to cluster duplicate blockers and write the digest. Reserve realtime for the one interrupt that needs an immediate spoken exchange.
- **latency:** A required decision should reach the owner within 10 seconds of being detected; routine events may wait until the requested digest deadline. Deduplication must be local and immediate, not delayed behind model generation.
- **cost:** Roughly $0.01 or less per hour of ordinary work; event clustering uses a cheap model only when new evidence arrives, and realtime is used only for escalations.
- **security:** The policy must not suppress safety-critical or irreversible failures. Store an explicit attention lease with expiry, urgency, source job, and deduplication key; do not send page contents or shell output to the pendant unless needed for the decision. The owner must be able to say “interrupt me now” to override it.
- **missing:** An attention-policy primitive shared by relay, Mac jobs, and browser commands, with expiry and escalation levels; A durable blocker identity that deduplicates the same problem across retries, browser tabs, and Mac jobs; A pendant command/status protocol for acknowledge, snooze, escalate, and digest-now that works across offline periods; A scheduler that emits one evidence-linked digest instead of independent completion notifications

### "Don't tell me a job is finished until you have checked the actual outside state it was meant to change; if the Mac receipt says success but the browser or service disagrees, tell me the contradiction and leave the task unresolved."
- **useful because:** A process exiting successfully is not the same as the owner's goal being true. This gives the owner outcome-level truth: the Mac can execute, the browser can inspect the authenticated result, and the relay can explain disagreement instead of confidently announcing a false completion.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision
- **model tier:** Use deterministic postconditions where available (URL, DOM field, file hash, receipt state); use a cheap verifier model only to interpret page evidence. Realtime speaks only the final verdict or asks for a missing postcondition.
- **latency:** Verification within 5 seconds after a mutation for a normal page; long-running services may be polled for up to a declared deadline with intermediate status and no premature success.
- **cost:** About $0.005–$0.03 per verified task, dominated by an extra browser read or screenshot; much cheaper than repairing a silently wrong external state.
- **security:** Verification must use the same authenticated browser session and preserve source URL/time. Never treat a cached page or stale receipt as proof. For destructive changes, report observed state without taking a compensating action unless explicitly requested.
- **missing:** A first-class postcondition attached to every Mac/browser action, expressed as a typed observation rather than free text; A verifier that can correlate action receipt, browser provenance, and observed external state with freshness timestamps; A tri-state result contract: verified, contradicted, or unverified—separate from executor success/failure; A relay speech template that names the evidence and contradiction without leaking page secrets

### "When I come back to my Mac, tell me what changed while I was away—not a list of jobs, but the meaningful before-and-after differences in my browser work, files, and active project, with anything still needing me called out."
- **useful because:** The owner experiences the system as a continuity partner, not a queue. Today jobs and logs describe actions, but they do not answer the human question 'what is different now?' across Safari, the Mac project, and the pendant's deferred work.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Capture compact structured snapshots deterministically at departure/return; use a cheap model to summarize only the computed diffs. Realtime is unnecessary except for a short spoken version requested from the pendant.
- **latency:** Snapshot on departure under 1 second; return briefing under 5 seconds for normal state. Never block the Mac or copy full page text when hashes, titles, URLs, file metadata, and receipts suffice.
- **cost:** Usually below $0.01 per return; storage is compact metadata, and generation runs once per return rather than per event.
- **security:** Snapshots must be owner-scoped, encrypted or access-controlled, and redact page bodies, command environments, and secrets. Record which source produced each diff and mark changes observed versus inferred. The owner must be able to delete a snapshot interval.
- **missing:** A durable departure/return snapshot primitive spanning browser tabs, active project, jobs, and pending pendant work; A typed diff model that distinguishes owner-relevant mutations from noise such as tab reloads or timestamps; A compact redacted projection suitable for speech and a drill-down view with source receipts; A trigger from Mac lock/unlock or pendant proximity/reconnect to define the interval without requiring manual setup


## Changes it proposed to its own stack

### `firmware` — Add a bridge-side audio integrity controller spanning the nRF9160 stream and ESP32 A2DP source: sequence every PCM packet, measure queue depth and resampler/A2DP underruns, emit compact health counters over the existing bench UART, and switch between two bounded buffer targets (low-latency and starvation-safe) without changing the owner's conversation. On a gap, insert bounded comfort silence and resynchronize at the next packet boundary instead of replaying stale audio. Have the Mac bench harness run a 60-second loopback test and publish a pass/fail report before a firmware build is treated as wearable-ready.
- **owner gets:** The owner hears a continuous reply instead of silence, clicks, or old speech when the fixed 44.1-kHz SBC bridge is briefly starved. It makes the real prototype measurable today and prevents an apparently successful task from ending with audio that never reached the headphones.
- effort: Medium: packet headers/counters and a small state machine in both firmwares, one compact UART diagnostic frame, and a Mac test script. The resampler and A2DP path remain unchanged initially; only queue policy and recovery are new.  ·  risk: A bad resynchronization could drop a syllable or add latency. Gate the adaptive mode behind a build flag, retain the current static path as fallback, and fail back to silence-plus-status rather than repeating stale frames.
- cost: No API cost. Roughly 2–6 kB flash and under 4 kB RAM on ESP32; under 2 kB RAM on the nRF side. No hardware cost or material power increase.  ·  latency: Low-latency mode unchanged; starvation-safe mode may add 20–60 ms only when underruns are detected.
- security: Health frames contain sequence numbers, timing and counters only—no audio or user content. UART logs should remain local and be bounded/rotated.
- depends on: A host-side serial reader and framing parser (currently absent; the attempted typed serial diagnostic remains unresolved); A shared packet sequence field between nRF9160 and ESP32; A bounded dual-chip capture test using the existing diagnostics/dual_chip_autocapture.sh


## What it asked for

_Nothing._
## Its own summary

Discovered live hardware/device state and confirmed the new serial diagnostic grant still has no implementation: the resolver cannot reach either USB port. I recorded that finding and produced four forward proposals: (1) a cross-surface “take care of this” flow, (2) an ESP32/nRF audio-integrity controller with underrun counters and recovery, (3) spoken evidence-backed history of what actually changed, and (4) one honest whole-path readiness answer separating bench USB proof from LTE/wearable proof. I also notified relay-realtime of the serial gap.

**Biggest unknown:** Whether the physically connected nRF9160 and ESP32 are emitting valid health/audio frames right now. What is still needed is an actually implemented bounded serial collector/framing parser, a shared packet-health schema, and a relay record of the last successful end-to-end audio turn; without those, Mac and relay health endpoints can only prove partial reachability, never headphone audio or wearable readiness.

