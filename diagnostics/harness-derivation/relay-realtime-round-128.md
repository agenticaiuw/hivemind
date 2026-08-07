# Harness derivation — relay-realtime — round 128

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Route this to my Mac and tell me when it’s done."
- **useful because:** It makes the pendant feel like a real assistant: you can speak a task, it gets sent to the right place, and you get a clear spoken update without babysitting the process.
- **path:** relay → mac-bridge → faculty-action → faculty-perception
- **model tier:** Realtime model for intent capture; cheaper Mac-side planner for the actual work; relay-only status reads when possible.
- **latency:** Fast first response (under a second) to acknowledge routing; completion can arrive later as a spoken update when the job finishes.
- **cost:** Low for routing and status checks; the expensive part is any Mac-side planning or long-running actions, which should not run on the relay.
- **security:** Must avoid inventing details. Status must be read from an authoritative job record. Spoken status should be verbatim from the status source to prevent false confirmation.
- **missing:** relay_route_intent needs an implementation, not just a schema; a shared job identity mapping between relay job records and Mac job records; a delivery path for completion notifications back to the pendant session

### "“Pick up where I left off.” (Optionally: “and finish the application/order/message I was working on.”)"
- **useful because:** Today an interrupted task is effectively lost across the pendant, Mac, and authenticated browser. This would let the owner walk away, return hours later, and resume safely: the relay identifies the last incomplete workflow, the browser extension reopens or inspects its authenticated tab, the Mac agent checks the local app state, and judgement reconciles what actually happened before continuing. It would report the exact next step aloud instead of blindly repeating an action or forcing the owner to reconstruct context.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use relay-realtime only to recognize the short resume request and give a concise progress response; use faculty-perception/judgement for state reconciliation and mac-planner (gpt-5.6-luna) for multi-step continuation. Invoke mac-vision only when visual UI state is required; use a cheaper background model to summarize old receipts/checkpoints.
- **latency:** Acknowledge within 500 ms from the pendant, then speak a brief “I found the unfinished step” update within 3–5 seconds. Long browser or Mac work may continue asynchronously, with a final spoken result when available.
- **cost:** Roughly one realtime turn plus one planner/judgement invocation per resume; approximately $0.03–$0.15 depending on screenshots and workflow length. Browser and Mac inspection dominate latency and token cost, not the short voice turn.
- **security:** The browser may contain authenticated private data and the Mac may contain unsent drafts. State snapshots and receipts must be scoped to the owner and encrypted in transit/at rest, with redaction of secrets. Before continuing, compare the checkpoint against current UI/server state and never claim success from an old receipt. Because the owner allows reversible actions without prompts, proceed with those; clearly announce irreversible or externally visible actions before doing them.
- **missing:** A durable cross-surface workflow checkpoint format recording intent, current step, identifiers, observed state, and idempotency keys; A resume/reconcile endpoint that can inspect the latest Mac receipt, browser tab/session, and pendant conversation together; Mac/browser adapters that expose stable state fingerprints and detect that a tab or app has materially changed; A completion or failure push path to the pendant for work that outlives the initial voice turn

### "“Did I already send/submit that?” or “Is the thing I asked for actually done?”"
- **useful because:** The owner needs a trustworthy answer about real-world state, not a replay of the last command. The pendant should ask the always-on relay to gather independent evidence: sent mail or calendar state on the Mac, confirmation/receipt in the authenticated browser, and the prior action receipt. It would reconcile contradictions and say “confirmed,” “not confirmed,” or “cannot tell,” with the evidence and timestamp. This prevents duplicate messages, duplicate purchases, and false confidence after a dropped connection.
- **path:** pendant → relay-realtime → faculty-perception → faculty-judgement → mac-planner → browser-extension → mac-vision → faculty-action
- **model tier:** Realtime handles intent extraction and the short spoken answer. Faculty-perception gathers structured evidence; faculty-judgement performs confidence and contradiction analysis. Use mac-planner for local inspection and browser-extension for authenticated web verification; reserve mac-vision for unstructured UI evidence. No expensive action model is needed unless the owner explicitly asks to repair an unconfirmed state.
- **latency:** Speak an acknowledgement immediately, collect evidence in 3–8 seconds, and give a confidence-labeled answer. If one source is slow, report partial evidence rather than waiting indefinitely.
- **cost:** Approximately $0.02–$0.10 per verification, dominated by Mac/browser inspection and any screenshot/OCR; the realtime utterance itself is a small fraction.
- **security:** This may inspect private Mail, files, and authenticated pages, so evidence must be owner-scoped, minimally retained, and redacted in logs. Never infer completion from intent or a queued job alone. External side effects are not performed by this capability; any corrective action must be a separate explicit request.
- **missing:** A common evidence schema with source, timestamp, object identity, observation, and confidence; Read-only cross-surface verification orchestration that can query Mail/Calendar/local apps and authenticated browser sessions in one request; Entity and idempotency matching so “that message” or “the application” maps to the correct item; A pendant response format for confidence, contradiction, and cited evidence rather than a bare success/failure

### "“Finish signing in and tell me when it’s ready.” (When the browser is waiting for a one-time code or approval.)"
- **useful because:** An authenticated browser workflow currently stalls when it reaches an MFA/OTP prompt while the owner is away from the Mac. The browser extension would publish only that a challenge is waiting and its origin, the pendant would collect the code or approval instruction by voice, and the relay would deliver it once to the matching tab. The owner could complete a legitimate sign-in without exposing the Mac screen or manually returning to it; the relay would then have the browser verify the resulting page before reporting success.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Realtime performs tightly scoped speech recognition and confirmation of the challenge origin; no generative model should transform the code. The browser extension performs exact one-shot delivery and page verification. Use faculty-judgement only to match the challenge to the owner’s active request and detect a changed origin.
- **latency:** Challenge notification under 1 second, code delivery under 2 seconds after the owner speaks, and verification within 5 seconds. Expire the pending exchange quickly rather than holding a voice turn open.
- **cost:** Approximately $0.005–$0.03 per challenge, mostly realtime audio and a browser inspection; negligible model cost if the code is handled as opaque text.
- **security:** OTP/TOTP codes and approval links are secrets. Do not store, echo, transcribe to general history, or send them to a language model; keep them in volatile memory for one delivery attempt. Bind the challenge to exact origin, tab/session, request ID, and short expiry; reject mismatches. Never ask the owner to read a code from an unverified origin, and never auto-approve a push notification without an explicit spoken instruction.
- **missing:** A browser-to-pendant challenge event containing verified origin, tab/session ID, challenge type, expiry, and request ID; A volatile, single-use secret-input channel that bypasses transcript/history/model logging; Browser extension support for injecting an opaque code and returning cryptographic/page-state verification; A relay event push path and pendant UX for challenge alerts and expiry/failure


## Changes it proposed to its own stack

### `relay` — Implement the granted relay_route_intent tool as a real routing shim: normalize the utterance, choose target (mac-planner vs mac-vision) based on a small intent classifier, POST to /v1/mac/plan or /v1/bridge/work as appropriate, record a relay jobId, and return a spoken acknowledgement immediately.
- **owner gets:** They can just talk. The system routes the request correctly without them needing to say “use the Mac” or “open the browser,” and it gives a quick, confident spoken acknowledgement.
- effort: Medium: a thin classifier plus glue code, plus tests for ambiguous utterances and failure modes.  ·  risk: Misrouting. Mitigate with conservative defaults and a fallback to mac_delegate for ambiguous requests. If routing fails, return a clear spoken error and do not start work.
- cost: Small per invocation; mostly CPU for classification and an HTTP call.  ·  latency: Adds under a second for classification; leaves heavy work to downstream agents.
- security: Must not leak bearer tokens in logs; must validate and sanitize utterances and context before forwarding.
- depends on: relay job record store remains available; /v1/mac/plan and /v1/bridge/work remain reachable


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities: trustworthy interrupted-work resume, cross-surface completion verification, and secure wearable-mediated browser MFA handoff. Each names the missing connective protocol/state/event work rather than assuming current routes are sufficient.

**Biggest unknown:** Whether any existing backlog item already covers the specific browser MFA secret-input path or cross-surface evidence reconciliation; I did not perform further discovery because the owner instructed me to stop.

