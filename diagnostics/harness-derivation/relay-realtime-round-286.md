# Harness derivation — relay-realtime — round 286

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If the Mac can’t complete what I asked, tell me why and offer the next-best alternative I can approve by voice."
- **useful because:** Owners don’t want a dead-end failure. They want a concise explanation and a safe fallback, like “Safari isn’t open and the browser agent is offline; I can set a reminder or draft an email instead.”
- **path:** relay → mac-bridge → browser → dashboard
- **model tier:** Realtime for the conversational fallback; mac-planner for generating alternatives when the workflow is complex.
- **latency:** Short spoken failure reason immediately, then a single suggested fallback within a second or two.
- **cost:** Mostly cheap status reads and a small plan generation when needed. No continuous monitoring.
- **security:** Alternatives may involve sending messages or modifying files; require confirmation for high-impact actions and avoid exposing private data in spoken output.
- **missing:** A structured error taxonomy from mac-planner jobs to map failures into suggested fallback actions; A small library of fallback templates mapped to tool availability and device state

### "“Make this change everywhere it needs to be changed, but show me the differences before anything irreversible.” Then, after I say “do it,” carry the same change across my Mac files, authenticated browser session, and iPhone, with one coherent result."
- **useful because:** Today each surface can act, but no single request can maintain one intended change across them. This would prevent half-finished edits such as updating a document but not the linked portal or phone setting, and would give the owner one spoken confirmation of what actually changed.
- **path:** pendant → relay → mac-planner → mac-vision → browser → iOS
- **model tier:** Realtime relay extracts the invariant goal and speaks a concise diff; mac-planner (slower background tier) builds a cross-surface dependency plan; mac-vision/browser/iOS perform the concrete actions and return receipts.
- **latency:** A first spoken scope/diff within 3 seconds; planning may take 10–30 seconds; execution can continue asynchronously with a short pendant update at each surface boundary.
- **cost:** Roughly $0.03–$0.20 per request depending on screenshots and planner turns; computer-use screenshots and browser/iPhone verification dominate.
- **security:** The relay must not expose raw credentials or browser page contents unnecessarily. The diff must identify destructive or externally visible changes, and execution must be explicitly requested after preview; retain per-surface receipts and recover by replaying only failed steps.
- **missing:** A cross-surface transaction/intent ID and dependency graph spanning Mac, browser, and iOS; A preview/diff response that can be rendered as a short spoken summary and kept for a later approval; Idempotent action receipts and compensation/retry semantics across POST /execute surfaces; A local planner/computer-use path that is reliable for iPhone Mirroring and browser verification

### "“Keep this request private: transcribe and act on it without sending my words or the screen contents to the relay or any hosted model.” Use the pendant as the microphone and let my nearby Mac do the sensitive work locally, then return only the result to the pendant."
- **useful because:** A wearable is present for secrets precisely when the owner is away from a keyboard, yet the current low-latency path necessarily sends audio to the relay. This would make private banking, health, work, and household requests usable without making the owner choose between convenience and cloud disclosure.
- **path:** pendant → relay → mac-planner → mac-terminal → browser → iOS
- **model tier:** Realtime relay handles only an opaque session token and transport state; a local Mac model/planner performs transcription, reasoning, and computer use. Use the expensive realtime tier only for a short fallback if the Mac disappears.
- **latency:** Local USB-attached operation should begin feedback within 500 ms and return ordinary requests in 2–8 seconds; LTE-to-Mac private tunneling, when available, may take 1–3 seconds before local processing starts.
- **cost:** Near-zero hosted inference cost in the local path; the main cost is a local model process and encrypted relay bytes. Optional fallback incurs normal realtime cost only after an explicit privacy-policy failure.
- **security:** The pendant and Mac need mutually authenticated keys, replay protection, encrypted audio frames, explicit private-mode indication, and zero transcript/screenshot persistence on the Worker. The owner must be told if the Mac is unavailable rather than silently falling back to cloud. Browser credentials remain inside the Mac/browser agent.
- **missing:** A firmware and Mac pairing protocol over the live USB serial links, with a secure session-key handshake; A relay transport mode that forwards opaque encrypted frames without decoding, logging, or model-injecting them; A local speech-to-text and response-audio path on the Mac, including Opus/PCM conversion compatible with the shipped 24 kHz downlink; A durable owner privacy-mode preference and a clear pendant indication when private mode is active

### "“Send that to them,” while I am looking at something on my Mac or phone. Figure out what “that” and “them” mean from the current screen, browser tab, iPhone, and my recent spoken context, tell me your interpretation in one sentence, and carry it out."
- **useful because:** Short wearable commands fail today whenever the owner omits nouns that are obvious from the screen in front of them. This would make the pendant feel situated rather than forcing the owner to dictate URLs, filenames, contact names, and message bodies while away from a keyboard.
- **path:** pendant → relay → mac-planner → mac-vision → browser → iOS
- **model tier:** Realtime relay handles the utterance and asks the local perception tier for a compact candidate set; mac-vision and browser/iOS adapters extract visible labels and stable object IDs; a cheaper planner resolves candidates, while realtime speaks only the selected interpretation.
- **latency:** Candidate interpretation in 2–4 seconds, with a spoken “I mean X to Y” before external sending; screen capture should be one bounded snapshot, not a continuous stream.
- **cost:** About $0.01–$0.10 per request; one local screenshot and OCR/vision pass dominate, with a second model turn only when candidates conflict.
- **security:** Only the active-window crop and explicitly needed browser/iPhone labels should leave the Mac; redact passwords and payment fields before relay use. Never infer a recipient from hidden page state without stating the chosen identity. Keep a short-lived object map and delete it after the action.
- **missing:** A perception endpoint that returns stable object references and visible text from the active Mac, browser tab, and mirrored iPhone in one timestamped snapshot; A cross-surface referent graph linking screen objects to planner action arguments; A confidence/ambiguity response contract that can speak the interpretation before an external side effect; Reliable mac-vision and iOS snapshot adapters, since the current computer-use loop is disabled


## What it asked for

_Nothing._
