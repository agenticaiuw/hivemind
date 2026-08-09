# Harness derivation — faculty-perception — round 145

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac reachability** — At 2026-08-08T01:49:39Z, /observe reports inputReachability.status=verified, Accessibility and Screen Recording trusted for com.aipendant.agent, uiActionsWillReachTheScreen=true, secureInput=false; /ops/status reports permissions.ready=true and browser extension online.
  - evidence: GET /observe and GET /ops/status both returned HTTP 200 with these fields.

## Capabilities it proposed

### "Before you send, delete, buy, or change anything, prove to me exactly what screen and browser target you are acting on, then tell me if the result matches."
- **useful because:** Prevents the most expensive class of mistakes: acting on a stale tab, wrong account, changed page, or misidentified UI target. It uses live observation rather than trusting a model's last screenshot.
- **path:** pendant → mac-planner → mac-vision → browser-extension → relay-realtime
- **model tier:** Realtime only for the brief spoken confirmation; deterministic Mac/browser checks and a cheaper text model for comparison.
- **latency:** 1–3 seconds before an action; under 2 seconds after it for verification.
- **cost:** About $0.01–$0.05 per guarded action; dominated by one screenshot/vision comparison, not voice.
- **security:** Screenshots and URLs stay on the Mac unless the owner explicitly allows cloud reasoning. Require spoken confirmation for irreversible actions. Redact passwords and payment fields from evidence.
- **missing:** A standard pre/post action evidence record joining /observe, browser tab identity, action ledger step, and postcondition; A computer-use policy hook that can pause execution until the owner confirms a mismatch

### "When I ask what happened while I was away, give me a ranked list of only the things you can prove, with the exact source and freshness for each, and separate 'the system did it' from 'I heard it'."
- **useful because:** The current surfaces can report Mac execution, relay acceptance, browser state, and permissions, but those are different facts. A ranked proof list would stop completed jobs or delivered bytes being mistaken for owner awareness.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Cheaper background model assembles the bounded digest; realtime only answers follow-up questions.
- **latency:** 3–8 seconds on request; no work while idle beyond existing event capture.
- **cost:** Under $0.01 per request when using existing event records; the dominant cost is optional cloud transcription or summarization.
- **security:** Do not send page bodies or private app content to the relay by default. Show coverage limits and mark unavailable pendant playback explicitly. Retain hashes and metadata longer than raw content.
- **missing:** A single typed evidence envelope with source timestamps and freshness; A relay-to-Mac join ID for browser reads and a real pendant playback event

### "Use my pendant voice as a roaming sensor: tell me what is on the screen in front of me, what tab or app it is, and whether it changed since the last time I asked, without making any changes."
- **useful because:** The owner can ask a context question while away from the keyboard and receive a grounded answer about the Mac's current foreground app and browser tab, including a change warning instead of a stale description.
- **path:** pendant → mac-vision → browser-extension → mac-planner → relay-realtime
- **model tier:** Realtime voice handles the short question and answer; local vision/OCR and deterministic browser inspection do the perception, with a cheaper model for summarization.
- **latency:** 2–4 seconds for a current-state answer; change detection should be effectively instant when the extension heartbeat arrives.
- **cost:** Roughly $0.01–$0.04 per query; local screenshot/OCR is free, with cloud vision the dominant cost if enabled.
- **security:** Never upload the screen by default; keep captures local and redact sensitive regions. Require confirmation before escalating from observation to action.
- **missing:** A local, persisted perceptual snapshot keyed by tab/window/app and content hash; A pendant-connected transport (the pendant is currently absent from the registry)

### "Let me ask, “What exactly happened when I approved that?” and hear a synchronized replay of the Mac screen, browser tab, spoken exchange, and action outcome, with unknown gaps called out instead of invented."
- **useful because:** Today each surface can retain fragments, but the owner cannot reconstruct one moment across them or distinguish what was visible, said, executed, and physically heard. A synchronized replay would make consequential actions understandable after the fact.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → unified
- **model tier:** Background model builds the timeline and compresses it; realtime only answers the owner's short follow-up by voice.
- **latency:** 5–15 seconds to assemble a replay; immediate playback once assembled.
- **cost:** $0.02–$0.10 per replay, dominated by optional visual summarization; raw event joining is local and cheap.
- **security:** Keep raw audio/screenshots on the Mac, encrypt replay indexes, redact secrets before any cloud summary, and require owner confirmation before exposing sensitive app content aloud.
- **missing:** A synchronized monotonic/wall-clock event ledger shared by pendant, relay, Mac, and browser; Durable links between voice turns, screenshots, browser results, action receipts, and actual audio playback; A replay assembler that preserves explicit unknown intervals rather than treating missing data as success

### "Make this change across my Mac and browser as one transaction: show me every target first, commit only if they still match, and stop with a recoverable plan if any one target changes."
- **useful because:** A multi-step request can currently partially succeed across separate surfaces, leaving calendars, files, tabs, or messages inconsistent. The owner needs an all-or-nothing boundary, not merely an undo button after the fact.
- **path:** pendant → mac-planner → mac-vision → browser-extension → relay-realtime
- **model tier:** A cheaper planner computes the prepare/commit graph; realtime is reserved for the owner's final spoken commit and abort notifications.
- **latency:** Up to 10 seconds to prepare and verify targets; commit should finish within the existing action latency.
- **cost:** $0.01–$0.08 per transaction, mainly target verification and any vision comparison.
- **security:** No commit without explicit owner confirmation for irreversible effects. Secrets never enter the transaction log. Rollback must be capability-aware and report non-reversible side effects honestly.
- **missing:** A distributed transaction coordinator spanning Mac action ledger, browser command receipts, relay jobs, and pendant cancellation; Prepare and postcondition contracts for each action type, with idempotency keys and compensating operations; A durable commit decision and recovery queue that survives a Mac, browser, or relay disconnect

### "If the browser, Mac screen, relay job, or pendant telemetry disagree about what is happening, say “these sources conflict,” explain the conflict briefly, and ask me which source to trust before doing anything."
- **useful because:** The dangerous failure is not missing data but plausible contradictory data: a browser tab moved, a Mac action finished, while relay or device state is stale. Explicit disagreement is safer than silently choosing one.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → unified
- **model tier:** Deterministic comparison detects conflicts; a cheap model explains them; realtime only delivers the short spoken warning and collects the owner's choice.
- **latency:** Under 1 second for conflict detection on every guarded operation; under 3 seconds for the spoken explanation.
- **cost:** Well under $0.01 when comparing typed metadata; vision is invoked only when metadata conflicts.
- **security:** Expose only the minimum conflicting fields aloud, especially in public. Treat owner selection as scoped and temporary, never as a blanket trust override.
- **missing:** A source-specific freshness and authority policy, including transport and clock uncertainty; Typed conflict records that preserve both observations and the owner's resolution; Planner enforcement that blocks action whenever an unresolved conflict concerns its target


## Changes it proposed to its own stack

### `context` — Add a typed cross-surface evidence envelope emitted for every guarded action and perception answer: observation time, source (Mac/browser/relay/pendant), freshness, content hash, target identity, precondition, postcondition, and confidence. Store only metadata plus redacted snippets locally; let every reader distinguish observed, inferred, and unknown.
- **owner gets:** The owner gets an answer they can trust and audit instead of a fluent claim that quietly mixes a stale tab, a completed Mac job, and an unheard announcement.
- effort: Medium: define the envelope, emit it at /observe, browser result, job receipt, and pipeline boundaries, then render it in voice and dashboard.  ·  risk: Schema drift or false confidence if writers omit fields; reject incomplete envelopes and show 'unknown' rather than filling gaps.
- cost: Negligible storage and model cost; hashes and metadata are local.  ·  latency: Under 100 ms for emission; no additional model turn unless summarization is requested.
- security: Improves security by preventing raw screenshots/page bodies from crossing surfaces; redact before hashing or storing.
- depends on: Mount the existing browser provenance routes and connect them to browser results; Define the missing pendant playback event separately; never infer it from relay bytes

### `mac-harness` — Build a local perception timeline keyed by window/tab identity and content hash. On browser heartbeat or /observe polling, record only foreground app, URL/title, tab/window IDs, screenshot hash, and a short redacted diff; expose 'changed since timestamp' to the voice planner.
- **owner gets:** A question asked from the pendant gets a current answer and an explicit changed/not-changed result, rather than a description of whatever the agent saw several minutes ago.
- effort: Medium: use the now-verified Screen Recording/Accessibility path plus existing /observe and browser heartbeat, with bounded local storage.  ·  risk: Sensitive UI metadata could leak or hashes could be mistaken for content proof; keep it local, redact titles/URLs by policy, and label hashes as identity only.
- cost: Low disk/CPU; no cloud inference for unchanged screens.  ·  latency: Heartbeat updates are near-real-time; a query adds roughly one local observation cycle.
- security: Screen capture is enabled now, so enforce a denylist for passwords, banking, and secure input before any model upload.
- depends on: Owner policy for which apps/tabs may be observed; A local route that returns the timeline and freshness rather than requiring the model to infer it

### `integration` — Add a USB shadow-device bridge on the Mac: detect /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA, ingest the pendant reality beacon and audio-integrity frames, and expose them as a local diagnostic source while LTE registration is absent. Forward only signed health summaries to relay when connectivity exists.
- **owner gets:** The owner can test the real wearable and audio bridge today on the desk, get honest 'connected over USB, not LTE' status, and validate perception/delivery behavior before wearing it outside.
- effort: High: serial framing, device identity, reconnect handling, and a relay adapter; firmware already has the beacon/integrity behavior but no live registered pendant.  ·  risk: USB disconnects and stale frames could be mistaken for health; include monotonic sequence numbers, last-seen age, and transport='usb' in every report. Never treat USB presence as LTE reachability.
- cost: Small Mac CPU cost; no API cost except optional relay summaries.  ·  latency: Sub-second local health updates; relay forwarding is best effort.
- security: Authenticate the serial peer by expected USB identity/build hash; do not expose raw audio or keys over diagnostic routes.
- depends on: A Mac serial reader/allowlist for the two live USB ports; A relay endpoint accepting transport-qualified beacon frames


## What it asked for

_Nothing._
## Its own summary

Fresh discovery: /ops/status and /observe now verify the exact AI Pendant Agent identity has Accessibility and Screen Recording, permissions.ready=true, and UI actions will reach the screen. Safari extension is online with zero pending commands; the live tab changed from Google to x.com between probes. Relay and Mac bridge are reachable, but the nRF pendant still is not registered. I recorded the verified reachability finding and proposed three capabilities plus three concrete changes: evidence-bound guarded actions, proof-ranked away digest, current-screen/change perception, a typed evidence envelope, local perception timeline, and a USB shadow-device bridge for the physically connected prototype. The USB bridge is especially actionable now because LTE registration is absent.

**Biggest unknown:** The granted read_continuity_snapshot tool still does not resolve at runtime (nearest routes are /ops/snapshot and /pipeline), so I cannot obtain one typed cross-surface continuity read. I still need either a resolver fix for that grant or an authenticated route that returns freshness, liveness, pending work, and provenance in one response. Separately, the USB serial reader and relay transport for the absent-but-physically-connected pendant remain unbuilt.

