# Harness derivation — relay-realtime — round 151

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “remember this exactly” on the pendant, save a time-and-location-stamped voice clip together with the Mac’s current app/window and any relevant authenticated browser tab, then later let me ask “what was I looking at when I said that?” and hear a cited answer."
- **useful because:** A fleeting spoken thought would become reliably recoverable context, not an isolated transcript. The answer would tie the owner’s physical utterance to the exact digital state they were working in, which no Mac-only or browser-only agent can reconstruct.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime model only for the short capture acknowledgement and retrieval dialogue; a cheaper background model should extract entities and generate the later citation bundle.
- **latency:** Acknowledge capture in under 500 ms; collect Mac/browser snapshots opportunistically within 5 seconds; retrieval response in under 4 seconds.
- **cost:** Roughly $0.01–$0.05 per captured/retrieved item, dominated by transcription and background summarization; raw audio storage dominates bytes, not API spend.
- **security:** Audio, screen metadata, URLs, and possibly page text leave the pendant and may contain secrets. Encrypt at rest, retain raw audio briefly, make authenticated-tab capture explicit in the utterance, and never expose page secrets in spoken output.
- **missing:** A pendant capture endpoint that preserves the original audio and timestamp; A relay correlation record joining voice, Mac foreground-window snapshot, and browser tab inspection; A durable searchable memory index with source citations and retention controls; A browser extension snapshot API callable at capture time

### "Use my pendant as a physical presence key: when I say “use my private browser,” only a currently-attached or recently authenticated pendant can authorize the relay to operate my authenticated browser tabs, and the pendant immediately tells me if that presence expires while work is running."
- **useful because:** It lets the owner safely delegate real authenticated work while away from the Mac without relying on a typed password or a vague cloud session. Stealing a browser cookie alone would not be enough; the worn object becomes the human-presence boundary.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** No expensive reasoning for authorization; use deterministic firmware/relay checks. Realtime speech is only for the owner’s command and concise expiry warning.
- **latency:** Presence verification under 200 ms over USB or under 2 seconds over LTE; browser commands should start within 3 seconds; expiry warning immediately on loss.
- **cost:** Negligible model cost; approximately $5–$20 for a secure-element-backed pendant revision, plus tiny relay storage and heartbeat traffic.
- **security:** A compromised Mac, relay, or pendant could impersonate presence. Use challenge-response keys, nonce-bound job tokens, replay protection, short leases, revocation, and never speak secrets aloud. This is an authorization boundary, not a claim that the pendant proves identity at a distance.
- **missing:** Hardware-backed key storage and challenge-response firmware on the nRF9160 pendant; A relay presence-lease service that binds each browser/Mac job to a nonce and expiry; Browser and Mac command handlers that reject jobs whose lease is absent or stale; A visible pendant LED pattern and dashboard audit trail for lease state

### "Before carrying out a consequential multi-app request, have the Mac planner and browser agent independently reconstruct what will happen, compare their predicted effects, and tell me the disagreement in one spoken sentence; if they agree, execute and return a receipt plus the evidence each used."
- **useful because:** The owner gets a dependable end-to-end operator rather than a single model confidently misreading a page or app. Independent disagreement is especially valuable when the owner is away from the Mac and cannot visually inspect the action.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** Use the realtime tier only to normalize the request and speak the result. Use cheaper planner/vision/judgement models in parallel; reserve a stronger model for resolving only genuine disagreements.
- **latency:** Parallel predictions in 5–10 seconds for ordinary workflows; a disagreement explanation within 2 seconds after both return; execution and receipt can continue asynchronously with spoken completion later.
- **cost:** Approximately $0.05–$0.30 per workflow, dominated by duplicated planner/vision inference and browser extraction; far cheaper than recovering from a wrong external action.
- **security:** Independent agents may share the same blind spot, and page content can be malicious prompt injection. Keep predictions in typed effect schemas, isolate untrusted page text, retain both evidence sets, and never claim agreement means safety. Owner policy currently permits execution without a confirmation gate.
- **missing:** A relay fan-out/fan-in coordinator for one spoken request; A common typed predicted-effects and evidence schema across Mac, vision, and browser agents; A faculty-judgement comparison route that can explain disagreements without taking over execution; An execution lock ensuring the action uses the exact plan that was compared; A spoken completion/status channel for results after the owner stops talking

### "If I double-press the pendant and say “stop,” immediately halt the active Mac or browser workflow, cancel any not-yet-started steps, and tell me exactly which steps already happened and which were prevented."
- **useful because:** The owner can recover from a mistaken command while away from the Mac, using the one control surface they physically have. This is an emergency brake, not a confirmation gate, and it makes autonomous multi-step work materially safer.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Deterministic pendant gesture and relay cancellation path; realtime model only interprets the short spoken stop phrase and summarizes receipts. No expensive planning model is needed.
- **latency:** Cancel signal should leave the pendant within 300 ms and reach the active executor within 1 second; spoken step accounting within 3 seconds.
- **cost:** Near-zero inference cost; modest durable job-state and event storage. Hardware needs only firmware gesture support on the existing one-button device.
- **security:** Cancellation must be authenticated to the active job and idempotent. A lost link may prevent stopping already-running local processes, so the Mac/browser executors need cooperative checkpoints and a clearly reported last-known state. Do not pretend external side effects can be undone.
- **missing:** Pendant firmware double-press/long-press emergency event and local LED acknowledgement; A relay cancellation endpoint and fan-out to Mac and browser executors; Checkpointed execution with cancellation polling between actions; Receipt semantics that distinguish completed, cancelled, and unknown-in-flight steps; A short spoken-status interrupt path that works while no normal turn is active


## What it asked for

_Nothing._
