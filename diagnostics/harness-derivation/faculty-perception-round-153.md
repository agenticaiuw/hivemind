# Harness derivation — faculty-perception — round 153

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-observability** — At 2026-08-08T02:16Z, Mac agent reports Accessibility and Screen Recording granted, inputReachability verified, browser extension online in Safari on x.com with 9 tabs and zero pending commands; relay reachable and Mac bridge online. Pendant remains absent from live device list.
  - evidence: GET /ops/snapshot and GET /observe returned 200 with permissions.ready=true, inputReachability.status=verified, browser.online=true, pendingCommands=0; discover devices lists only home-macbook-bridge and cloudflare-contract-test.

## Capabilities it proposed

### "“What happened while I was away—and show me the proof for anything that changed?” Give me a spoken, time-ordered account that separates observed screen state, browser evidence, Mac execution receipts, relay state, and (when available) what the pendant actually played; open the relevant proof on the Mac when I ask."
- **useful because:** This would be the system’s most useful daily behavior: it would stop treating a completed job or a socket write as truth, and let the owner audit a missed interval without reconstructing it from five dashboards. The newly verified screen-recording and Accessibility grants make visual capture real rather than hypothetical.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Background model builds a bounded event timeline and provenance joins; realtime model only speaks the concise answer and handles follow-up questions.
- **latency:** Initial digest under 5 seconds from cached records; a requested visual proof under 3 seconds per item.
- **cost:** Usually <$0.01 per digest with a small text model; visual proof dominates (one screenshot/vision call per ambiguous item), while spoken delivery is local 24 kHz TTS.
- **security:** Screenshots and browser titles can contain private data. Store hashes, redacted snippets, and capsule IDs by default; require explicit confirmation before showing or transmitting a full screenshot. Never label an item heard unless the pendant playback event exists.
- **missing:** A relay-to-Mac evidence-capsule bridge: relay browser reads currently mint no ID or hash, while Mac evidenceCapsules.js already has the schema.; A real device-originated played/consumed event; device_playback currently has readers but zero emitters.; A single timeline joiner that correlates immutable jobId/commandId/stepKey/capsuleId across the existing stores.

### "“Before I leave the Mac, prove that my pendant can still hear me and that I can hear it back.” Run a short readiness check over the USB-connected pendant/audio bridge, relay, and Mac, report each hop separately, and refuse to call the device ready unless firmware health, uplink capture quality, relay acknowledgement, and downlink playback are all evidenced."
- **useful because:** The owner currently cannot distinguish “the Mac bridge is online” from “the worn device will work away from the desk.” A pre-departure proof catches the most expensive failure—discovering a dead wearable during a real interaction—and gives a precise repair target instead of a vague offline state.
- **path:** pendant → relay → mac-terminal → mac-planner → dashboard
- **model tier:** Cheap deterministic checks and a background model for diagnosis; realtime is used only if the owner asks a spoken follow-up.
- **latency:** 10–20 seconds for a USB loopback plus relay round trip; report partial results immediately if LTE registration is absent.
- **cost:** Near-zero API cost; local serial/audio probes dominate time. One optional relay test request is negligible.
- **security:** Do not upload raw microphone audio. Send only beacon counters, capture-integrity metrics, packet IDs, and bounded hashes. USB serial access and relay credentials must remain local; confirmation is required before any external test utterance.
- **missing:** A Mac-agent allowlisted serial probe for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA.; Firmware wiring for the accepted offline-reality-beacon and offline-capture-integrity-sentinel into a one-shot diagnostic response.; A relay test transaction that returns an authenticated, device-correlated receipt rather than treating socket bytes as playback.

### "“When you change something in my browser or Mac, show me exactly what changed and give me one safe undo.” Execute a multi-surface action, capture a before/after visual and semantic diff, bind it to the browser command and Mac receipt, then offer a single reversible undo without pretending the change succeeded until the post-state is observed."
- **useful because:** With Screen Recording and Accessibility now verified, the agent can finally see and manipulate the real UI, not merely report that an API call returned. This makes browser and desktop automation trustworthy for consequential work: the owner sees the result, the provenance, and the recovery path.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Background planner chooses reversible actions; vision model compares before/after; realtime model narrates only the result or asks for confirmation on irreversible steps.
- **latency:** 2–8 seconds for a browser action and diff; longer workflows become a tracked Mac job with progress.
- **cost:** One or two vision calls per action are the main cost (roughly <$0.03); browser bridge and Mac receipts are local.
- **security:** Before/after captures may expose secrets. Redact passwords and sensitive locators, retain hashes and small regions by default, and require confirmation for sends, purchases, deletion, or navigation with side effects. Undo must be offered only when the ledger says the step is resumable.
- **missing:** A mounted browserProvenance route and a join from browser result to the existing evidence capsule and action ledger.; A standard post-state observation contract for both browser and Mac actions, including stale-tab detection.; Owner policy for which action classes may run without confirmation.

### "“Only interrupt me when I can actually receive it; otherwise hold it and tell me why you waited.” Have the pendant, Mac, browser, and relay jointly infer a live interruption window from the owner’s current conversation/audio state, foreground app, calendar/meeting state, and wearable availability; deliver urgent items at the first safe window, and later explain the decision and any missed window."
- **useful because:** Today the system can queue or speak, but it cannot know whether an interruption was socially or cognitively receivable. This would make the wearable feel considerate rather than merely connected: no news briefing over a meeting, no lost urgent alert because the pendant was disconnected, and no silent deferral whose reason the owner has to guess.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Deterministic policy engine consumes presence signals; a cheap background model classifies ambiguous activity and summarizes the decision. Realtime is reserved for the actual urgent spoken interruption.
- **latency:** Presence state under 1 second; urgent delivery decision under 2 seconds; deferred items reevaluated every 15–30 seconds.
- **cost:** Low API cost when signals are deterministic; occasional model classification is cents per hour at most. Audio remains local except for explicitly requested conversation understanding.
- **security:** Foreground windows, calendar titles, and microphone-derived activity are sensitive. Keep raw audio and screen pixels local, export only coarse states (in-call, speaking, driving-like, idle), let the owner set per-source urgency rules, and require confirmation before using calendar or screen content for inference.
- **missing:** A privacy-preserving presence signal contract spanning Mac foreground/meeting/audio state, browser activity, relay reachability, and pendant availability.; A durable decision record with reason, policy version, defer-until, and eventual outcome so the owner can audit every suppressed interruption.; A delivery scheduler that treats device playback confirmation as distinct from relay socket delivery and retries only when the owner’s policy permits.

### "“Let me approve a sensitive browser action from the pendant without bringing the screen to you.” Create a walk-away approval transaction: the browser extension shows a redacted preview and exact target, the Mac signs the current-page snapshot, the relay holds the transaction, the owner approves or rejects by voice/button on the pendant, and execution is allowed only if the page has not changed; speak the final result and keep a revocable receipt."
- **useful because:** The owner can be away from the desk yet safely approve a real purchase, message, permission, or form submission. Today approval, page freshness, browser identity, and spoken consent are separate facts; a stale tab or a look-alike page can turn an apparently confirmed action into the wrong action.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Deterministic transaction state machine and cryptographic page binding; a small model summarizes the preview. Realtime handles only the owner’s short approve/reject exchange.
- **latency:** Preview in 2 seconds, approval response immediately, execution and receipt under 5 seconds; timeout after a configurable minute.
- **cost:** Usually <$0.01 per transaction; one optional vision comparison is the dominant model cost. Hashing, signatures, and browser bridge work are local.
- **security:** Never read or speak secrets in the preview. Bind approval to operationId, tab/session pseudonym, URL origin, redacted field descriptors, content hash, expiry, and policy. Reject on any page mutation, navigation, extension restart, or duplicate approval; require a second explicit confirmation for money movement or external messages.
- **missing:** A relay-held approval escrow with nonce, expiry, one-time consumption, and device-scoped authorization.; A browser-extension attestation of the exact tab/session and a post-preview mutation hash.; A pendant input path for authenticated approve/reject plus a durable, revocable receipt that joins browser, Mac, relay, and playback outcomes.

### "“Turn the half-remembered thing I said while away from the Mac into a source-linked note, but do not keep my raw recording.” The pendant should buffer a short utterance offline, the Mac should later identify the active app/page and relevant browser context, and the relay should reconcile the transcript into a dated note with confidence, provenance, and a clear request for correction when the context match is weak."
- **useful because:** People lose useful thoughts precisely when they cannot stop to file them. Today capture, browser context, transcription, and note creation are disconnected; the owner either repeats the thought or receives an ungrounded note that looks more certain than it is. This would preserve the thought while making uncertainty and source explicit.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** On-device firmware performs bounded buffering and quality metrics; a background transcription/context model does reconciliation after reconnect; realtime is unnecessary unless the owner asks to review or correct it.
- **latency:** Offline capture immediate; after reconnect, draft within 10 seconds and final note only after owner correction or high-confidence match.
- **cost:** Low: short audio transcription and one context-matching call per note. Storage is bounded metadata plus encrypted temporary audio, deleted after transcription or timeout.
- **security:** Raw speech and page context are sensitive. Keep audio encrypted and short-lived, redact secrets before relay upload, never infer a source from URL alone, show confidence and competing matches, and require confirmation before writing to external notes or creating tasks.
- **missing:** A pendant offline utterance handoff that carries sequence, quality verdict, and deletion deadline rather than a permanent recording.; A Mac context snapshot API that can correlate the utterance time with foreground app and browser tab without exporting full screen contents.; A reconciliation record joining transcript, context candidates, owner correction, and final note ID with explicit grounded/asserted status.


## Changes it proposed to its own stack

### `integration` — Implement a cross-surface evidence join ledger, not a new event store: accept immutable operationId/attemptId/stepKey from Mac and browser actions, attach existing capsuleId/contentHash, job receipt, pipeline run, relay delivery state, and (when firmware exists) playback sequence; expose a redacted read model to the dashboard and voice layer with explicit unknown edges.
- **owner gets:** Every answer about “did it happen?” would show the missing link instead of silently upgrading a Mac-side completion into success. The owner gets one honest status—observed, executed, delivered-to-socket, played, or unknown—and can act on the exact broken hop.
- effort: Medium: schema/adapter work across existing action ledger, browser provenance, pipeline trace, relay jobs, plus one read route; no new capture format.  ·  risk: Adapters could disagree or leak sensitive page content. Keep the join ledger metadata-only, reject mutable identifiers, and make unknown the fail-closed result; recover by replaying source receipts because existing stores remain authoritative.
- cost: Negligible storage and API cost; hashes and IDs only. One background join pass per action.  ·  latency: Adds under 100 ms for local joins; remote relay evidence may remain pending and must be surfaced as pending rather than blocking unrelated actions.
- security: Improves security by preventing ungrounded claims; capsule bodies remain behind existing redaction/revocation controls. Require scoped reads for full evidence.
- depends on: Relay browser reads must return a stable request ID and content hash so Mac can mint the existing capsule.; Firmware must emit the already-approved playback acknowledgement queue.; Mount browserProvenance routes and define the operationId/attemptId/stepKey contract.


## What it asked for

_Nothing._
## Its own summary

Fresh observation: /ops/snapshot and /observe now prove the exact AI Pendant Agent has Accessibility and Screen Recording, inputReachability=verified, browser extension online in Safari with 9 tabs and zero pending commands, relay reachable, and Mac bridge online. The pendant itself is still absent from the live registry. I recorded this fact. I proposed three owner-facing capabilities: the highest-value evidence-backed away digest, a pre-departure USB pendant/audio readiness proof, and visual before/after diffs with safe undo; plus an integration change for a metadata-only cross-surface evidence join ledger. The proposals explicitly build past existing routes rather than pretending those routes already correlate truth.

**Biggest unknown:** The newly granted read_continuity_snapshot is still reported by describe as unresolved, so I cannot use one authoritative continuity read; /ops/snapshot is the current substitute. The key remaining product blockers are the relay browser capsule bridge, a standard immutable operation/attempt/step join contract, and a real pendant-originated playback acknowledgement. Also, no pendant is registered today, so wearable readiness cannot yet be hardware-verified.

