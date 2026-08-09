# Harness derivation — mac-planner — round 214

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-device-and-browser-state** — Safari browser bridge is online with 2 tabs; active tab URL is https://www.google.com and title reports Google Maps. Pending browser commands and spool are both zero. Mac bridge is online, while the pendant itself remains LTE-unregistered but USB-attached per system context.
  - evidence: GET /browser/status returned online:true, tabCount:2, pendingCommands:0, spool.spooled:0; discover devices returned home-macbook-bridge online and Safari on MacIntel online.

## Capabilities it proposed

### "When I say “make this change,” carry it through the browser or Mac, verify in the actual app that the intended result happened, and tell me on the pendant exactly what changed—or what failed."
- **useful because:** Today an action receipt can say a click or file write ran, but not that the external application accepted the change. This closes the loop across relay planning, browser session state, Mac execution, and wearable feedback, preventing silent false success.
- **path:** relay-realtime → browser-extension → mac-planner → pendant → dashboard
- **model tier:** Use realtime only to interpret the live request and speak the result; use a cheaper background model for DOM/state comparison and receipt summarization.
- **latency:** 5–15 seconds for browser/Mac execution and verification; pendant acknowledgement within 1 second, then a final spoken result.
- **cost:** About $0.01–$0.05 per invocation; dominated by one verification/comparison model call, not the deterministic actions.
- **security:** The verifier must receive only the target app state and redact secrets. Never claim success from an executor receipt alone. Destructive or externally visible actions need the owner's configured policy; the current FULL_CONTROL path has no gate, so ship this disabled until policy entries are explicit.
- **missing:** A browser command that returns a stable postcondition snapshot (URL/title/selected DOM fields) rather than only command completion; A relay correlation ID shared by pendant speech, Mac job, browser command, and verification receipt; An owner-configured unattended-action policy

### "When I plug the pendant into my Mac, automatically dock it: upload any offline bookmarks or buffered reply audio, reconcile them into my timeline, run the audio/link diagnostic if the last session was unhealthy, and tell me what was recovered."
- **useful because:** The pendant is physically attached over USB today while LTE is unregistered, so this provides immediate value in the real hardware state: offline moments and interrupted replies become durable instead of waiting for cellular registration, and a failed audio session is diagnosed before the next call.
- **path:** pendant → mac-planner → relay-realtime → dashboard
- **model tier:** No realtime model for synchronization; deterministic USB framing and relay ingestion, with a cheap background model only to turn recovered events into a short human summary.
- **latency:** LED/serial acknowledgement under 500 ms; sync within 30 seconds for a normal queue; diagnostic is opt-in and may take 1–2 minutes.
- **cost:** Usually <$0.005 (mostly storage/HTTP); optional summary costs <$0.01. No audio transcription unless the owner explicitly asks.
- **security:** Treat the USB serial link as a local trusted transport only after explicit pairing. Encrypt queued data at rest where possible, delete SD copies only after relay acknowledgement, and never upload ambient audio from bookmarks unless its existing opt-in is enabled.
- **missing:** A resolved mac_serial_exchange tool or Mac route for framed read/write on /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A dock protocol exposing pendant_store manifests and acknowledgements; An attach event from the Mac bridge and idempotent relay ingestion keyed by item UUID

### "At the start of a calendar block, prepare me without opening the microphone: inspect the event and its linked browser tabs/files, put only the relevant briefing on my pendant, and after the block let me press once to get decisions, unresolved items, and the next action."
- **useful because:** This turns a scheduled event into a two-sided workflow: the Mac gathers context and the browser supplies authenticated session state, while the pendant gives a glanceable pre-brief and a durable post-meeting trigger. It avoids always-on listening and still helps when the owner joins from a different app.
- **path:** mac-planner → browser-extension → relay-realtime → pendant → dashboard
- **model tier:** Cheap scheduled/background model for preparation and post-block synthesis; realtime only if the owner asks a follow-up by voice.
- **latency:** Prepare 2–5 minutes before the event; post-block result in under 10 seconds after the button request.
- **cost:** $0.01–$0.04 per event, dominated by summarizing selected agenda/page text; no cost for empty or cancelled events.
- **security:** Calendar titles and authenticated page text are sensitive: select only event-linked domains, redact credentials and unrelated tabs, and keep output on the owner's relay/pendant unless explicitly exported. It must never silently record meeting audio.
- **missing:** A calendar-to-browser-link extractor that handles event URLs and attached documents; A scheduled trigger that can address the existing pendant inbox with expiry and priority fields; A post-block owner signal (button bookmark or calendar end) associated with the event ID

### "Use my logged-in browser session to complete this site task without exposing my password or page secrets to the relay, and let me approve the exact site operation from the pendant before it runs."
- **useful because:** The browser has authenticated reach that the relay and Mac planner do not, but today delegation either exposes too much page context or relies on an unscoped command path. A capability token bound to one browser origin, operation, and expiry would let the owner use authenticated services safely while keeping credentials in the browser.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Realtime model interprets the request and explains the proposed operation; deterministic browser policy enforcement executes it. Use a cheaper model only to summarize the final result.
- **latency:** Preview in 2 seconds; pendant approval round trip under 3 seconds; execution and result under 10 seconds.
- **cost:** <$0.02 per invocation; cost is dominated by interpreting the request and summarizing the result, not token issuance.
- **security:** The relay must receive only an operation summary, never credentials, cookies, or unrestricted DOM. Tokens must be origin-bound, single-use, short-lived, and include an argument hash. The pendant approval should display or speak the exact target and mutation. Deny silently broadened redirects and cross-origin navigation.
- **missing:** Browser-extension support for origin-scoped, single-use capability tokens and operation previews; A relay protocol carrying an operation hash to the pendant and back; A browser-side allowlist of safely expressible site operations

### "When I ask “what was I looking at when I marked that moment?”, reconstruct the relevant Mac app, browser page, calendar context, and pendant bookmark as a private, time-bounded evidence view, then let me discard it permanently."
- **useful because:** A timestamped bookmark today records the moment but not the surrounding context. This would make the pendant's physical bookmark useful for recovering forgotten work without requiring always-on recording: it joins a local event with the browser and Mac state that existed at that instant.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Deterministic timestamp joining and redaction first; a background model summarizes only the selected evidence. Realtime is used only for the spoken query and answer.
- **latency:** Capture metadata at bookmark time in under 1 second; reconstruction in 5–20 seconds when requested.
- **cost:** <$0.03 per reconstruction, mainly summarization; storage cost is small metadata plus explicitly selected snapshots.
- **security:** This is potentially sensitive historical surveillance. Store minimal, encrypted, short-retention snapshots; exclude password fields, private browsing, microphone audio, and unrelated windows; require explicit user retrieval and provide immediate deletion with an auditable receipt.
- **missing:** A bookmark-time snapshot hook for active app identity and browser semantic state; A privacy-preserving, redacted snapshot store keyed to the existing moment-bookmark event; A join service that tolerates clock skew between pendant, browser, and Mac

### "For a high-impact action, prepare everything on the Mac and in the browser, but do not commit until I physically press the pendant; if the relay or browser link is compromised, the pending action must expire rather than run."
- **useful because:** Voice is convenient but weak as sole authorization for sending, publishing, deleting, or changing important records. A physical pendant confirmation creates a usable separation between planning and commitment while preserving unattended preparation and the owner's control.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → dashboard
- **model tier:** Realtime model produces the plain-language action preview; deterministic hashing, expiry, and commit checks enforce the approval. No expensive model is needed after approval.
- **latency:** Preview immediately; approval window configurable from 30 seconds to 10 minutes; commit confirmation under 5 seconds.
- **cost:** <$0.01 per action; cryptographic signing and verification are negligible, with model cost limited to preview wording.
- **security:** The approval must bind to an exact action hash, target account/origin, files, and arguments; replay and duplicate presses must fail. Never treat a generic button event as approval. The owner must explicitly configure which action classes require this mechanism.
- **missing:** A pendant-to-relay signed challenge/response channel that works over the current USB path and later LTE; Action-plan hashing shared by POST /plan, POST /execute, and browser commands; An explicit owner policy registry defining high-impact action classes


## What it asked for

_Nothing._
