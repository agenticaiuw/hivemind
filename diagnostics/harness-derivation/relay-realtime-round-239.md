# Harness derivation — relay-realtime — round 239

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "What’s going on with my Mac and browser right now?"
- **useful because:** Quick situational awareness helps the owner avoid interrupting work in progress and makes voice commands safer.
- **path:** mac-planner → browser-extension → relay-realtime
- **model tier:** Low-latency for the spoken response; Mac/browser provide the state
- **latency:** Fast status snapshot under a second when available; fall back to last known state if offline.
- **cost:** One status request plus a small spoken reply; cheap compared to planning and execution.
- **security:** Status can reveal sensitive apps or pages; keep summaries generic unless the owner asks for specifics.
- **missing:** A consolidated status snapshot endpoint that includes mac + browser + relay health in one response to reduce chatter

### "Use the best place to do this: if it’s simple, do it now; if it’s complex, hand it to my Mac and keep me posted."
- **useful because:** The owner shouldn’t have to think about routing. This reduces friction and errors, especially while moving.
- **path:** relay-realtime → mac-planner → browser-extension → faculty-judgement → faculty-action
- **model tier:** Relay for intent capture; judgement/action tiers for routing; Mac/browser for execution
- **latency:** Fast initial acknowledgement; background planning for complex tasks.
- **cost:** Cheap for simple reversible actions; higher for multi-step workflows and browser automation.
- **security:** Complex workflows may touch mail or files; require confirmation for destructive actions and keep receipts.
- **missing:** A reliable routing primitive (or plan endpoint) visible to the relay so it doesn’t invent a protocol; Better receipts/telemetry for routed actions to support spoken summaries

### "Before you act, tell me when the world has changed underneath my request: “The page is no longer the same,” “that file was edited,” or “the amount changed.” Then show me the exact old and new value and continue only with the part that is still valid."
- **useful because:** A wearable assistant acting across a live browser and Mac can otherwise apply a stale plan to a changed page or document. The owner gets a trustworthy warning at the point of divergence, not a vague failure after a wrong click or overwritten value.
- **path:** pendant → relay → browser → mac-planner → mac-vision → dashboard
- **model tier:** Cheap structured diffing first; gpt-5.6-luna only to explain an ambiguous semantic conflict; realtime relay speaks the single urgent warning.
- **latency:** Detect divergence before every mutating step, adding under 500 ms for structured state and under 2 seconds for a screenshot/OCR comparison.
- **cost:** About $0.005–$0.05 per guarded step; the dominant cost is an occasional screenshot/vision comparison, not speech.
- **security:** Diffs may expose private page or document contents. Keep raw snapshots local to the Mac/browser where possible, send only redacted changed fields, and expire evidence after the job. This is an advisory conflict detector, not a confirmation gate, matching the owner's maximum-access policy.
- **missing:** A precondition/evidence field on every planned action; Browser DOM snapshots and Mac accessibility/screen snapshots normalized into comparable state; A semantic diff service that distinguishes harmless layout churn from value or identity changes; A partial-plan replanner that can continue safe steps after a conflict

### "Make my pendant remember the conversation correctly: after I say “use the same editor,” “send it to him,” or “the one from yesterday,” resolve that reference from the relevant Mac, browser, and recent voice context without replaying my entire history or leaking unrelated facts."
- **useful because:** The owner can speak naturally instead of restating filenames, people, and prior decisions. This is especially valuable while away from the Mac, where the relay must resolve a short follow-up against the right task and surface rather than guess from a giant transcript.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Realtime relay for reference resolution; the existing projection and a cheap entity linker do retrieval; gpt-5.6-luna is invoked only when two candidates remain ambiguous.
- **latency:** Resolve ordinary references in under 300 ms from the stable projection; ask one concise clarification within 1 second when confidence is low.
- **cost:** Usually under $0.01 per turn because the projection is small; ambiguity may add one planner call.
- **security:** Only surface-scoped facts should be injected. Browser-derived facts must remain task-matched, sensitive values must stay redacted, and unresolved ambiguity must be spoken rather than silently choosing the wrong person or file.
- **missing:** Wire projectContext(surface, task) into conversationContext.js so the live voice prompt uses the measured projection instead of legacy memory blocks; Persist short-lived conversation entities and pronoun links with expiry and confidence; Return provenance for each resolved reference so the relay can explain “I mean the Outlook draft from yesterday” without exposing unrelated memory

### "While my Mac is asleep or offline, let me say “check my logged-in dashboard,” “download the invoice,” or “tell me if anything changed,” and have the relay use my already-authenticated browser session safely, then speak the result on the pendant when I am walking."
- **useful because:** The browser holds sessions the relay cannot currently reach unless the owner's Mac is online. This is the clearest everyday gap between a wearable and an ordinary voice assistant: the owner should not have to wake a laptop to read a page they are already signed into.
- **path:** pendant → relay → browser → dashboard
- **model tier:** Realtime relay for the utterance; a low-cost browser worker for navigation/extraction; gpt-5.6-luna only for page interpretation or a multi-step task; background execution for long downloads.
- **latency:** Speak an acknowledgement in under 1 second, return a simple reading in under 10 seconds, and queue longer work with an asynchronous pendant alert.
- **cost:** About $0.01–$0.10 per request, dominated by browser rendering and OCR for visually complex pages; text-only extraction should be cheap.
- **security:** This requires moving capability, not passwords: store session cookies in an encrypted, owner-scoped browser vault and never send them to the model. Require explicit device pairing and revocation, isolate each site, redact page data in logs, and make downloads/results expire. High-impact actions such as sending, purchasing, or deleting remain visibly reported as such.
- **missing:** A Cloudflare Browser Rendering or equivalent worker with persistent encrypted per-owner sessions; A pairing/import flow from the existing Safari extension that transfers an authenticated session without exposing cookies to the relay model; Browser action execution and extraction routes that work with the Mac absent, plus download storage and expiry; A durable relay-to-pendant inbox path for spoken results and failures


## What it asked for

_Nothing._
## Its own summary

Recorded three non-duplicate proposals: (1) precondition-aware cross-surface conflict detection that catches stale browser/Mac state before mutations, (2) live voice reference resolution wired to the existing scoped memory projection, and (3) authenticated browser access from the pendant while the Mac is offline. The third is the highest-value missing capability: it needs a paired encrypted browser-session worker, safe browser execution/extraction, and durable pendant delivery. The first proposal collided with an existing end-to-end handoff idea and was not recorded; I did not rephrase it.

**Biggest unknown:** Whether the existing browser watch routes can be extended to a true relay-hosted authenticated session, or whether a new Cloudflare Browser Rendering/session vault must be built; no further discovery was allowed this round.

