# Harness derivation — relay-realtime — round 261

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "What can you do right now, and what’s actually available while I’m offline?"
- **useful because:** The owner avoids confusion and broken commands. A quick capability check keeps expectations aligned with reality, especially when the Mac is asleep or the browser is unavailable.
- **path:** relay-realtime → mac-planner → browser-extension → pendant
- **model tier:** Realtime
- **latency:** Under a second for a spoken summary.
- **cost:** Very low; mainly reading inventories and device status.
- **security:** Avoid exposing internal URLs or tokens. Speak a simple summary.
- **missing:** A unified relay capability inventory endpoint (the relay has no self-capabilities route); Reliable device status endpoint for the pendant/bridge (some status paths were absent)

### "“I’m leaving my Mac. Keep the exact state of this work available, and when I ask later, put me back where I was.”"
- **useful because:** Today a worn owner loses the relationship between the open Mac apps, Safari tabs, unsaved editor state, and the spoken intent as soon as they walk away. A durable, owner-visible checkpoint would let the pendant become a reliable handoff between physical places instead of a remote button.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime handles the short capture and acknowledgement; mac-planner/mac-vision collect the state and a cheaper background model labels the checkpoint and later resolves “that work.”
- **latency:** Acknowledge in under 1 second; capture in 5–10 seconds; restoration can take up to 30 seconds with spoken progress.
- **cost:** Roughly $0.01–$0.05 per checkpoint/restore, dominated by vision or long state summarization; most checkpoints should be structured metadata with no model call.
- **security:** The checkpoint may contain window titles, URLs, clipboard text, and unsaved content. Keep it encrypted, scoped to the owner, redact secrets by default, show exactly what was captured in the dashboard, and expire checkpoints unless pinned. Restoration must produce an auditable receipt and never silently discard unsaved work.
- **missing:** A first-class checkpoint schema and encrypted storage on the relay; Mac APIs to snapshot and restore app/browser/editor state, including unsaved documents where supported; A pendant command and inbox reply for naming, listing, and restoring checkpoints; A durable cross-surface reference resolver for phrases such as “the work from when I left”

### "“Use the logged-in browser session I left on my Mac to finish this while I’m away, then tell me exactly what happened.”"
- **useful because:** The owner can currently speak to the pendant while away, but authenticated browser work is tied to an online Mac and there is no resumable, portable browser worker. This would turn the browser session into a reachable personal capability for tasks that cannot wait for the owner to return.
- **path:** pendant → relay → browser-extension → mac-planner → dashboard
- **model tier:** Realtime only normalizes the request and reports progress; a cheaper background planner executes the browser workflow, with a vision-capable model only for ambiguous page states.
- **latency:** Immediate acceptance and a first status sentence in 2 seconds; execution may run for minutes and must survive dropped pendant, Mac reconnects, and browser navigation changes.
- **cost:** $0.02–$0.20 per task depending on page count and vision retries; storage and browser session relay dominate operational cost rather than speech.
- **security:** Session cookies and page contents are extremely sensitive. Do not export cookies to the relay by default: use a local browser worker or an explicitly paired encrypted session enclave, scope each job to an allowlisted origin supplied by the owner, retain only action receipts, and make login, payment, deletion, and message-send steps explicitly inspectable. The owner’s maximum-access policy means this is not a blanket deny layer; it is transparent execution and recovery.
- **missing:** A resumable browser worker that can operate when the Mac is unavailable, or a secure Mac-hosted worker with reconnectable leases; Encrypted session handoff/lease protocol without exposing raw cookies; Job checkpoints, idempotency, and recovery after page changes or link loss; Pendant-friendly progress and failure summaries delivered through the existing inbox

### "“Answer this using what is on my screen, what I just said, and my saved context—but do not save the page or quote it back later.”"
- **useful because:** A wearable assistant should answer questions about the owner’s current work without forcing them to narrate or manually copy sensitive text. Today the surfaces can inspect pieces independently, but there is no single, privacy-bounded spoken query that joins live Mac/browser evidence with scoped memory and then guarantees the evidence is discarded.
- **path:** pendant → relay → mac-vision → browser-extension → mac-planner → dashboard
- **model tier:** Realtime performs the short spoken synthesis after evidence collection; mac-vision or browser extraction supplies only relevant regions, and a cheaper redaction pass strips secrets before synthesis.
- **latency:** First spoken acknowledgement under 1 second; answer in 3–8 seconds; if evidence collection exceeds that, speak one progress update and return a concise answer.
- **cost:** $0.01–$0.08 per question, driven by screenshots and multimodal inference; structured DOM/accessibility extraction should be preferred to images.
- **security:** Screen and browser contents can include credentials, health data, and private messages. Evidence should be held in memory only, transmitted over the paired channel, redacted before model input, excluded from conversation history and long-term memory, and represented in the dashboard by a retention receipt. The owner must be able to say “forget that evidence” and verify deletion.
- **missing:** A live evidence envelope combining browser snapshot, Mac accessibility/UI state, utterance, and projected memory; A strict ephemeral-retention mode in conversationContext and model logging; Secret/PII redaction for screenshots, DOM text, clipboard, and accessibility trees; A provenance-aware answer format that says which surface supported each claim without replaying sensitive content

### "“If someone else picks up or hears my pendant, do not let them use my Mac, browser sessions, or private memory; if I say the emergency phrase, lock everything and tell my chosen contact.”"
- **useful because:** The pendant is physically worn but the current command path appears to trust possession of the device and an active session. A stolen pendant, overheard voice, or replayed recording could reach the owner’s Mac and logged-in browser. Owner-bound authentication and an emergency lockout would make daily remote control safe enough to rely on.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime performs local wake/voice liveness scoring and immediate lock acknowledgement; a deterministic policy service revokes leases and the Mac agent applies lock actions. No expensive model is needed for the normal path.
- **latency:** Reject or accept a command in under 500 ms when the pendant is connected; revoke active Mac/browser leases and speak confirmation within 2 seconds.
- **cost:** Negligible per command after enrollment; one-time voice enrollment and occasional liveness calibration may cost under $0.05, with the main cost being secure key storage and recovery UX.
- **security:** Voice is not a perfect secret and emergency phrases can be overheard. Use a device-held key plus voice liveness as two signals, never voice alone; support a physical recovery procedure, immediate dashboard revocation, encrypted biometric templates that never leave the owner’s devices, and clear false-reject fallback. Emergency lock must be reversible by the owner but not by a remote agent acting on an untrusted voice.
- **missing:** Hardware-backed pendant identity and signed session challenges; On-device or paired-phone speaker verification/liveness, with enrollment and recovery; Lease revocation across relay, Mac, and browser workers; An emergency lock/notify action and audit trail


## Changes it proposed to its own stack

### `context` — Make every live voice turn assemble a bounded, surface-scoped context envelope from the existing memory projection, current machine context, and the active browser/Mac evidence, with byte-stable preferences first and an explicit ephemeral-retention flag. Replace the legacy duplicated prompt blocks at conversationContext.js with this envelope and emit a provenance/expiry receipt for each injected item.
- **owner gets:** The pendant would stop forgetting stable preferences or dragging unrelated old page facts into replies. Answers would be shorter, more accurate, and able to say whether they came from the owner, the Mac, or the current browser without leaking stale sensitive context.
- effort: Small-to-medium relay change plus integration tests; larger only if evidence adapters are missing.  ·  risk: A projection bug could omit a needed fact or expose a sensitive one. Fall back to the legacy prompt on projection failure, enforce hard token and sensitivity ceilings, and log hashes rather than raw content.
- cost: Reduces recurring context tokens materially (the measured projection saves about 222 tokens/turn); minimal storage cost for receipts.  ·  latency: One local projection lookup; should reduce model latency by shrinking prompts.
- security: Improves isolation by honoring surface scopes and making ephemeral evidence explicit; requires tests for voice/mac/browser boundary leaks.
- depends on: Wire conversationContext.js to projectContext(surface, task); Add ephemeral evidence envelope and provenance receipt fields; Keep the existing memory store and projection rules as the source of truth


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities and one stack change. The strongest new capability is owner-bound command authentication with emergency lockout; the most valuable cross-node direction is durable work handoff, though the recorder flagged it as close to existing checkpoint ideas. I also recorded privacy-bounded live evidence answering and wiring the existing scoped memory projection into live voice context.

**Biggest unknown:** Which existing Mac/workbench routes already snapshot and restore complete app/browser state. The recorder specifically warned that /workbench/contexts and /workbench/jobs/:jobId/handoff were not fully inventoried, so that must be checked before claiming durable handoff is entirely missing.

