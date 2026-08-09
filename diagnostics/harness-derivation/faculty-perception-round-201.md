# Harness derivation — faculty-perception — round 201

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-perception-readiness** — Live /ops/snapshot at round 201 reports Accessibility trusted, Screen Recording granted, all required/optional permissions present, and permissions.ready=true for AI Pendant Agent; browser extension online with 6 Safari tabs and zero pending commands; relay reachable with D1 and Mac bridge online.
  - evidence: read_continuity_snapshot include relay invoked GET /ops/snapshot, HTTP 200, body status.permissions and browser/relay payload.

## Capabilities it proposed

### "“What am I looking at right now, and what should I pay attention to?”"
- **useful because:** Today the voice agent can know a browser URL or ask a model to inspect a page, but it cannot reliably fuse the owner's actual focused window, screenshot, browser DOM, and relay/pipeline freshness into one grounded answer. This would turn the pendant into an eyes-free screen companion: it names the exact app/tab, extracts visible claims, distinguishes page text from inference, and says when the view is stale or inaccessible.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision
- **model tier:** Use the realtime model only to phrase the short spoken answer; use a cheaper background/vision model for screenshot OCR and DOM summarization, with deterministic metadata assembly before the model sees it.
- **latency:** 2–4 seconds for a first answer; 8 seconds maximum if a screenshot and DOM capture are both needed. The current live state supports this: Accessibility and Screen Recording are ready, Safari extension is online, and the relay/Mac bridge are reachable.
- **cost:** Roughly $0.01–$0.05 per invocation depending on screenshot resolution and vision tokens; DOM extraction and app metadata are negligible. Cache the observation by tab/window timestamp so a follow-up costs only text generation.
- **security:** Screenshots and page text can contain secrets. Redact password fields and known secret locators before leaving the Mac; only send the focused window plus requested browser region, never all six tabs by default. Ask confirmation before reading a sensitive app aloud or exposing its contents to the relay.
- **missing:** A single Mac observation contract joining GET /observe, focused-app state, browser snapshot/inspect, timestamp, and redaction metadata; A relay tool that accepts that bounded observation as grounded context rather than treating it as ordinary prompt text; A browser-side region selector so “this chart” does not upload the whole page

### "“Save what I’m looking at so I can ask about it later.”"
- **useful because:** A fleeting browser view currently disappears when the tab changes, while the Mac already has a content-addressed evidence-capsule schema that can preserve redacted text, source URL, region, hash, and expiry. This capability would let the owner create a spoken, resumable bookmark from the exact visible page/region, then later ask “what did I save?” or “open the source again” without relying on memory or an untraceable relay scrape.
- **path:** pendant → browser-extension → mac-planner → relay-realtime → mac-vision
- **model tier:** Use deterministic capture and hashing on the Mac; use a cheap text model only to produce a one-line title/summary and classify sensitivity. Realtime is needed only for the spoken confirmation and later retrieval conversation.
- **latency:** Capture confirmation under 2 seconds for DOM text; under 5 seconds if a screenshot/vision crop is needed. Retrieval should be under 1 second from the local capsule index, with relay fallback only when the Mac is unavailable.
- **cost:** Usually under $0.01 per save; deterministic extraction dominates no API cost, and a small summarization call is optional. Storage is bounded by the existing capsule limits (24-hour body TTL, 7-day tombstones, 500 live bodies).
- **security:** Never capture password fields, secrets, or the entire page by default. Show/speak the source host and expiry. A later open/action requires confirmation if it would submit, purchase, send, or mutate. Capsule content must remain local; relay receives only a redacted summary or capsule ID unless the owner explicitly asks for remote use.
- **missing:** A voice-triggered call site to the existing local evidenceCapsules mintCapsule() and browserProvenance recordExtraction() modules; Mounting the existing browserProvenance routes, which are currently unmounted; A browser command that captures the owner-selected region rather than only the active tab

### "“Why didn’t that work, and what can you do next without me repeating it?”"
- **useful because:** The live system now has enough reach to see the focused UI, browser command results, Mac permissions, relay reachability, and pipeline traces, but those facts are not fused into an owner-facing failure explanation. This capability would distinguish a blocked permission, stale browser session, relay outage, model refusal, or action-side failure, preserve the original target, and choose a safe retry or ask one precise question instead of making the owner start over.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension
- **model tier:** Use deterministic classifiers for transport/permission/receipt failures and a cheap reasoning model for the causal summary and next-step selection. Realtime only speaks the concise explanation and asks for confirmation if the retry mutates external state.
- **latency:** Under 2 seconds for known failures from existing receipts; up to 6 seconds for a fresh browser/UI probe. Never silently retry a destructive action.
- **cost:** Under $0.01 for receipt-based diagnoses; $0.02–$0.06 when a screenshot or browser reinspection is needed. Caching the failed target and evidence hash avoids re-uploading context.
- **security:** A retry may repeat a send, purchase, deletion, or form submission. Classify actions by reversibility, require confirmation for external side effects, and keep error screenshots/page text local or redacted. State clearly when the evidence only proves the Mac attempted an action, not that a remote service accepted it.
- **missing:** A canonical failure envelope joining job/receipt IDs, browser command IDs, focused-app observation, permissions state, and relay/pipeline stage; A safe retry planner that understands idempotency and refuses to replay unknown side effects; A spoken error taxonomy that exposes evidence and uncertainty instead of saying generic 'it failed'

### "“Show me exactly what you saw, decided, and changed when you did that.”"
- **useful because:** The owner cannot currently obtain a single, trustworthy replay of an action: the Mac may have a receipt, the browser may have a result, and the relay may have a spoken response, but none is bound into one tamper-evident account of the target, observation, decision, and resulting state. This would let the owner audit an important action without trusting a vague 'done' message.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension
- **model tier:** Build the bundle deterministically from local observations, browser provenance, action ledger, pipeline trace, and receipts. Use a cheap model only to narrate the bundle in plain language; realtime is needed solely for the spoken request and concise answer.
- **latency:** Under 3 seconds for an already-finished action; up to 10 seconds to collect missing before/after evidence. If evidence is unavailable, return an explicit gap rather than reconstructing it.
- **cost:** Usually below $0.01 because the bundle is assembled locally; up to $0.03 for a summary of a large bundle. Storage is bounded with hashes and redacted excerpts rather than raw screenshots.
- **security:** The bundle may contain private page text, messages, or file names. Keep raw evidence on the Mac, redact secrets, expose only selected excerpts over the relay, and require confirmation before sharing or exporting a bundle. A hash proves consistency, not truth of the original observation; say that explicitly.
- **missing:** A single immutable action-replay record binding observation hash, planner decision, confirmation, command IDs, receipts, and before/after state; A relay endpoint that can request and stream a redacted replay bundle from the Mac; A UI/voice response that distinguishes observed facts, model decisions, and inferred conclusions

### "“Stop everything I just asked you to do.”"
- **useful because:** There is no single owner-visible stop boundary across realtime speech, relay jobs, Mac actions, browser commands, and vision loops. A cancellation may stop one queue while another continues. A physical pendant stop would give the owner a reliable emergency brake for an ambiguous or unsafe chain, including work already handed to the Mac.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension
- **model tier:** No expensive reasoning is needed: a signed, monotonic cancellation token should propagate deterministically. Realtime only acknowledges the stop and reports which components confirmed it.
- **latency:** Pendant-to-relay cancellation under 500 ms when connected; Mac/browser acknowledgement under 2 seconds. Offline pendant should latch the stop locally and prevent queued playback or reconnection from resuming the cancelled chain.
- **cost:** Negligible per invocation; a bounded cancellation ledger and a few control frames. Hardware work is firmware integration with the existing button and link, not a new radio.
- **security:** A stop command must not be spoofable or replayable. Bind it to an owner/device session, use a monotonic sequence, and make cancellation fail-closed for queued actions. It should stop speech and reversible work, but clearly report external side effects that already escaped the system.
- **missing:** A cross-surface cancellation protocol with one chain ID and monotonic stop sequence; Relay fan-out that cancels realtime generation, pending announcements, and delegated jobs; Mac/browser handlers that honor cancellation between action steps and return confirmed stopped/too-late states; Pendant firmware handling for offline stop latching and reconnect replay

### "“Make this private now, and tell me what stopped listening.”"
- **useful because:** The owner cannot currently establish one privacy boundary across pendant microphone capture, relay realtime sessions, Mac audio, browser observation, and queued announcements. A spoken request is itself a weak control if the system is already listening. A physical pendant privacy latch, propagated to every surface, would make privacy state observable and fail closed rather than relying on per-component settings.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision
- **model tier:** Use firmware and relay control logic deterministically; no model call is needed to enforce privacy. Realtime may speak a short confirmation only after every reachable surface reports the requested state.
- **latency:** Local microphone mute and capture inhibition under 100 ms; relay/Mac/browser acknowledgements under 2 seconds. If any surface cannot confirm, report “partially private” and keep local capture disabled.
- **cost:** Negligible runtime/API cost. Requires a small durable privacy-state record and control messages; no continuous model usage.
- **security:** Privacy state must be fail-closed, monotonic, authenticated, and durable across reconnects/reboots. Do not send the owner’s spoken privacy command to remote services after the latch is engaged. Queued audio and screenshots should be suppressed or discarded according to an explicit retention policy, with only minimal state telemetry retained.
- **missing:** A hardware privacy latch or long-press gesture independent of the speech pipeline; A signed privacy-state protocol shared by pendant, relay, Mac agent, and browser extension; Relay enforcement that rejects audio/session creation and suppresses announcements while private; Mac/browser enforcement that disables observation, microphone capture, pending commands, and screenshot uploads; A visible/physical indicator and a concise confirmation state


## Changes it proposed to its own stack

### `model-routing` — Add a grounded-reference escalation policy: when the owner says “that,” “this,” or “the thing on screen,” first resolve a live observation from the focused Mac window and browser tab; if confidence is below a threshold or the observation is older than 10 seconds, invoke mac-vision for a bounded screenshot/DOM capture; attach source timestamps and redaction state to the planner context, and refuse to act when the reference remains ambiguous. Route extraction/summarization to a cheap model and reserve realtime for the final spoken reply.
- **owner gets:** The owner can point with ordinary speech instead of repeating URLs or app names, while the system stops guessing which of several open tabs or windows they meant. It makes “close that,” “summarize this,” and “what does this error mean?” dependable now that the exact agent binary has Accessibility and Screen Recording permission.
- effort: Medium: a routing policy plus a small grounded-observation envelope and confidence test; integrate existing /observe, browser status/inspect, and mac-vision actions. No new model or hardware is required.  ·  risk: A screenshot can expose sensitive content, and an incorrect reference could cause a destructive action. Mitigate with region/window scoping, secret redaction, a visible/spoken target confirmation before irreversible actions, and a hard stale-observation timeout. Recover by falling back to a clarification question.
- cost: Negligible deterministic overhead; roughly $0.005–$0.03 when vision is needed. Most short follow-ups reuse the cached observation and incur only realtime text/audio cost.  ·  latency: Adds 100–300 ms for metadata; 1–3 seconds for a screenshot/vision escalation. The owner gets an immediate “I’m checking the focused window” response if the capture is slower.
- security: Improves security by making the target explicit and bounded, but introduces screenshot handling. Keep raw screenshots local, send redacted crops or extracted text only, and log capsule/hash references rather than page bodies.
- depends on: A normalized observation envelope spanning GET /observe, browser inspect/status, and mac-vision output; A policy hook in planner/action routing to require grounded target confidence; Owner confirmation for destructive actions


## What it asked for

_Nothing._
