# Harness derivation — relay-realtime — round 99

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Teach my pendant a personal phrase once—such as “start my focus setup”—and thereafter have it carry out the whole cross-device routine, adapting to what is currently true on my Mac and in my signed-in browser, while telling me what it did over voice."
- **useful because:** The owner gets a genuinely personal hands-free command language instead of repeating brittle step-by-step instructions. A phrase can coordinate the worn pendant, an unattended Mac, and authenticated browser sessions, and can degrade gracefully when one surface is unavailable.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use relay-realtime only to recognize the short phrase and report progress; use a cheaper background model to compile and update the routine from the owner’s teaching example; use mac-planner for Mac actions and browser-extension for authenticated web actions.
- **latency:** Acknowledge the phrase within 500 ms; begin the first action within 2 s. Teaching may take 10–20 s and can be asynchronous; each later routine invocation should report a spoken summary within 5 s of completion or failure.
- **cost:** Roughly $0.01–$0.05 per invocation depending on how much state must be inspected; teaching costs one larger background-model call, while most invocations are short intent recognition plus existing downstream calls. The dominant cost is cross-surface state summarization.
- **security:** A learned phrase can cause real mutations in authenticated services, so the routine definition must show its exact steps and destinations in the dashboard, retain an append-only execution receipt, and let the owner disable or delete it. Secrets remain in the browser/Mac projections; the relay receives only typed actions and outcomes. Do not silently broaden a routine when a site or app changes—report a drift and pause that step.
- **missing:** A routine-teaching API that records an example utterance, resolves it into typed cross-surface steps, and versions the definition; A runtime resolver that binds routine steps to current Mac/browser state and detects definition drift; A pendant-to-relay phrase/alias store with compact identifiers and a spoken progress/error protocol; A dashboard editor and dry-run preview for learned routines

### "While you are carrying out something on my Mac or in my browser, let me interrupt from the pendant with “stop,” “pause,” or “undo the last step,” and have the relay halt safely at the next action boundary, or compensate the last reversible action, then tell me exactly where it stopped."
- **useful because:** Today a spoken request handed to another surface can feel like losing control while the owner is away from the Mac. This gives the wearable a real-time control channel over in-flight multi-step work, without requiring the owner to find a screen or wait for completion.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use relay-realtime for the tiny command classifier and immediate acknowledgement; use deterministic job control and receipt logic for cancellation/compensation, not an expensive model. Ask mac-planner or browser-extension only to stop at declared action boundaries and return typed state.
- **latency:** Acknowledge the interrupt in under 300 ms and issue cancellation in under 1 s. The owner should hear the stopped action and whether compensation succeeded within 3 s.
- **cost:** Negligible model cost for stop/pause/undo; approximately $0.00–$0.01 per interrupt. Engineering cost is in cooperative cancellation, idempotency, and reliable receipt reconciliation across the relay and Mac/browser links.
- **security:** Never claim an undo that was not confirmed by a receipt. A cancellation can leave partial external effects, so the spoken response must name the last completed action and any residual state. Compensation should be limited to actions already classified as reversible; for irreversible work, stop future steps and report the boundary. Keep the owner’s maximum-access policy—this is control and observability, not an approval gate.
- **missing:** A durable in-flight job control channel from the pendant relay to Mac and browser command queues; Cooperative cancellation checkpoints and idempotency tokens in mac-planner/mac-vision/browser-extension; A typed compensation map tied to action receipts, with explicit partial-failure states; A low-latency pendant interrupt event and spoken status protocol

### "Let me say “private mode” or press the pendant button twice before a sensitive request, and have that conversation stay ephemeral: no transcript or memory entry, no browser/Mac forwarding unless I explicitly say so, and an audible/LED indication when private mode is active and when it ends."
- **useful because:** The owner can use the wearable in public or discuss passwords, health, or confidential work without having to trust every downstream log and memory projection. It makes privacy a fast, understandable physical interaction rather than a dashboard setting discovered too late.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use a deterministic local button/phrase state machine and relay-realtime acknowledgement; do not spend a larger model call on privacy classification. Downstream agents receive an explicit ephemeral-session token and must refuse persistence unless the owner exits private mode and reissues the request.
- **latency:** Enter private mode locally in under 100 ms and confirm by tone/LED immediately; relay confirmation within 500 ms. Exiting mode should take effect on the next utterance and be confirmed within 1 s.
- **cost:** Near-zero per-use inference cost. Storage and implementation cost is modest, but requires auditing every transcript, voice-run, job, browser inspection, and memory write path so ephemeral events cannot leak into ordinary logs.
- **security:** Fail closed: if the relay cannot prove private-session handling, it must answer that the request was not sent rather than forwarding it. Do not retain raw audio, transcript, embeddings, tool arguments, receipts, or browser captures from the private interval. The owner needs a physical timeout/visual state and a dashboard audit that only records that private mode was used—not its content.
- **missing:** A pendant firmware privacy-mode state with double-button trigger, timeout, and distinct LED/tone feedback; An end-to-end ephemeral session token propagated through relay, Mac planner, browser extension, and job/receipt services; A non-persistent audio/transcript/logging path with deletion guarantees for in-flight buffers; A dashboard privacy-state indicator and test harness that verifies no private payload reaches memory or history


## What it asked for

_Nothing._
