# Harness derivation — faculty-perception — round 144

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac accessibility and screen recording are live and verified** — GET /observe at 2026-08-08T01:46:22.978Z reports accessibility trusted=true, screenRecording=true, inputReachability.status=verified, uiActionsWillReachTheScreen=true, secureInputActive=false for com.aipendant.agent; /ops/snapshot independently reports permissions.ready=true and no requiredMissing.
  - evidence: probe_http GET /observe and GET /ops/snapshot responses
- **browser and relay are currently live** — At 2026-08-08T01:46Z Safari browser bridge is online with 9 tabs, zero pending commands/spooled items, and the relay is reachable with macBridgeOnline=true; the registered relay devices still contain only home-macbook-bridge online and cloudflare-contract-test offline, no pendant.
  - evidence: probe_http GET /ops/snapshot, GET /browser/status, and discover devices

## Capabilities it proposed

### "“Keep me from accidentally exposing private information while I’m using the computer: warn me through the pendant before I paste, send, or dictate something sensitive into the current app.”"
- **useful because:** The Mac can now genuinely observe and reach the screen, while the pendant is the only channel likely to interrupt the owner without stealing focus. Combining foreground app, secure-input state, browser session, clipboard/form target, and local speech quality can prevent irreversible privacy mistakes rather than merely report them afterward.
- **path:** pendant → mac-vision → mac-planner → browser-extension → relay-realtime
- **model tier:** Realtime only for the short risk explanation; deterministic local classifiers and a cheaper background model should classify text and target. Relay is fallback when pendant is connected.
- **latency:** Under 300 ms from a paste/send trigger to local pendant warning; no network round trip required for the block/warn decision.
- **cost:** Near-zero for local rules/redaction; occasional cheap model call for ambiguous classification, under $0.01 per ambiguous event. Dominant cost is screenshot/clipboard inspection, not tokens.
- **security:** Sensitive clipboard/form contents must stay on the Mac unless the owner explicitly permits cloud classification. Default to warning, never silently block; require confirmation only for high-confidence secrets or external recipients. Secure-input fields and passwords must be treated as opaque and never captured.
- **missing:** A Mac event hook that sees paste/send/dictation before commit; A local sensitivity classifier with target-domain and recipient context; A pendant-connected low-latency warning/confirmation path

### "“Tell me, through the pendant, when the computer task I delegated has actually reached a visible result—and stop waiting if the screen shows a login wall, error, or an unexpected app.”"
- **useful because:** Today the Mac can see the screen and post input, but completion records can precede visible success. This gives the owner a trustworthy handoff: the relay speaks only after the Mac vision loop verifies the rendered result, while the pendant can interrupt or ask for help when the loop is stuck.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension
- **model tier:** Use deterministic checks and a cheap vision model for routine state classification; reserve realtime for the spoken escalation and owner reply.
- **latency:** Poll/observe every 1–2 seconds; speak within 3 seconds of verified success or a blocking state. Stop after 25 vision steps or a configurable timeout.
- **cost:** About $0.01–$0.10 per multi-step task depending on screenshot count; vision tokens dominate. No cost for local observation and job receipts.
- **security:** Screenshots may contain private data and browser sessions. Keep frames on the Mac by default, redact known secrets, upload only the minimum crop for vision, and require confirmation before submitting or deleting. Login walls must be reported, never bypassed.
- **missing:** A durable task state that joins Mac jobId to the latest observed visual state; A verifier that distinguishes visible success from merely completed input; A relay announcement path that carries verifier evidence and interruption reason

### "“When I’m wearing the pendant, let me say ‘what’s on my screen?’ and give me a short, grounded answer that names the exact app/page and tells me whether you can act there.”"
- **useful because:** The owner can now grant the agent real screen reach, and Safari is live with multiple sessions. A spoken screen synopsis would turn the wearable into an accessible status surface: it combines live Mac observation with browser session metadata and explicitly distinguishes observation from action capability.
- **path:** pendant → relay-realtime → mac-vision → browser-extension → mac-planner
- **model tier:** Cheap vision/text summarization for the snapshot; realtime only for the conversational turn and follow-up. No background model needed.
- **latency:** 1–2 seconds for a compact synopsis, with a cached observation usable immediately if fresh within 5 seconds.
- **cost:** Roughly $0.005–$0.03 per request; one small screenshot and short summary dominate. Cache identical foreground state to avoid repeated vision calls.
- **security:** Do not read secure-input/password fields; announce that content is unavailable rather than guessing. Keep screenshots local where possible, redact secrets before any relay/model upload, and say whether the answer came from browser DOM/session metadata or visual inference.
- **missing:** A single observation response that joins foreground app, screenshot/OCR, browser tab title/URL, and action reachability; Pendant voice routing and a freshness-aware cache; Redaction and provenance labels in the spoken response

### "“Before you send money, publish, delete, or submit anything consequential, make me prove I am physically present with the pendant and show me exactly what will happen on the Mac screen; refuse stale browser sessions or relay commands.”"
- **useful because:** This would be a genuinely cross-surface safety boundary: a stolen/stale browser session, an unattended Mac, or a cloud relay job could no longer complete a high-impact action without a fresh physical gesture and a matching visual preview. The pendant supplies presence; the Mac supplies the rendered target; the browser supplies session identity; the relay supplies a one-time challenge.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension
- **model tier:** Deterministic policy and cryptographic nonce checks should decide eligibility. Use a cheap model only to summarize the preview; realtime speaks the short confirmation prompt.
- **latency:** Preview in under 2 seconds; challenge expires after 30 seconds and must be confirmed locally on the pendant.
- **cost:** Negligible for nonce/policy work; under $0.02 for an optional visual/text summary. Screenshot capture and redaction dominate.
- **security:** Never send secrets or full screenshots to the relay by default. Bind the challenge to action hash, browser tab/session, foreground app, and pendant boot/session identity. Physical confirmation must not be inferred from voice alone. High-impact actions remain deny-by-default when any binding is stale.
- **missing:** A cross-surface challenge protocol binding pendant gesture, action hash, browser session, and rendered preview; A Mac preflight endpoint that freezes the exact action target before confirmation; A firmware gesture/confirmation event and relay verifier; A policy registry defining consequential actions and expiry rules

### "“When I am busy or in a call, remember the useful things I say and do not interrupt me; later, at the first safe moment, give me a tiny spoken queue with why each item was held and let me dismiss or act on it from the pendant.”"
- **useful because:** The wearable can detect speech quality and the Mac can observe the active app, but today there is no shared notion of interruption safety. This would make the system socially usable: it preserves actionable intent without speaking over a meeting, presentation, dictation, or focused work, then resumes at a contextually safe boundary rather than a fixed timer.
- **path:** pendant → mac-planner → mac-vision → browser-extension → relay-realtime
- **model tier:** Local deterministic interruption signals should handle calls, secure-input, full-screen presentation, and active typing. Use a cheap background model to compress queued items; realtime is reserved for the eventual spoken digest.
- **latency:** Capture intent locally within 500 ms; no interruption during unsafe context; offer the digest within 5 seconds after a safe boundary is detected.
- **cost:** Usually near-zero; roughly $0.01 per queued batch if summarization needs a model. Audio feature extraction and foreground-app observation dominate device work.
- **security:** Do not retain raw microphone audio by default. Store compact intent transcripts with sensitivity labels and a user-configurable retention limit. Secure-input and private meeting contexts must suppress capture or keep it entirely local.
- **missing:** A shared interruption-state machine spanning pendant VAD, Mac foreground/meeting signals, and relay announcements; A durable intent queue with per-item sensitivity, urgency, expiry, and owner disposition; A safe-boundary detector and pendant dismiss/act controls; An explicit owner policy for what may be remembered during calls

### "“If the Mac, browser, relay, or pendant loses connection while I am in the middle of something, recover the conversation and pending action as one coherent session when it returns—without repeating a message or silently dropping one.”"
- **useful because:** The owner should not have to know which node failed. The pendant can be offline, the browser can hold a private session, and the relay can outlive the Mac; a session-level reconciliation protocol would preserve intent and avoid duplicate sends, duplicate speech, and phantom completion across those failure boundaries.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension
- **model tier:** Use deterministic sequence numbers, idempotency keys, and state reconciliation. A cheap background model may summarize conflicts; realtime only explains a conflict to the owner.
- **latency:** Reconnect reconciliation within 3 seconds; never replay an action or spoken item until its ownership and sequence are resolved.
- **cost:** Negligible protocol/storage cost; occasional <$0.01 conflict summary. Dominant implementation cost is durable cross-node state, not inference.
- **security:** Bind session records to device/session pseudonyms, not raw credentials. Do not replicate browser page contents to the relay unless explicitly authorized. Conflicts involving external side effects must pause and ask the owner rather than choose automatically.
- **missing:** A shared session ID and monotonic event log across relay, Mac, browser, and pendant; Exactly-once idempotency and acknowledgement semantics for speech and actions; A reconciliation endpoint that can distinguish accepted, executed, displayed, played, and unknown; A bounded local pendant spool that survives link loss without using the SD failure buffer for routine writes


## What it asked for

_Nothing._
