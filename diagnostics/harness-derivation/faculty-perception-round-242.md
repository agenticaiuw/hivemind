# Harness derivation — faculty-perception — round 242

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live perception state 2026-08-09** — GET /ops/status and GET /observe show the exact AI Pendant Agent is Accessibility-trusted, Screen Recording granted, inputReachability verified, browser extension online with 2 tabs, relay reachable via bridge, and no pendant-facing route exists on this Mac agent. GET /v1/devices/status is not a route on localhost:8000, so relay device registry cannot be asserted from this surface.
  - evidence: Authenticated GET /ops/status HTTP 200; authenticated GET /observe HTTP 200; authenticated GET /v1/devices/status HTTP 404.

## Capabilities it proposed

### "When I ask “what exactly happened?”, reconstruct the last request as a causal, evidence-linked timeline: what the pendant captured, what the relay understood, what the Mac/browser did, and what is actually observable now—calling out every unproven link."
- **useful because:** Today a completed Mac job or relay-delivered audio can be mistaken for an owner-heard result. This gives the owner one honest answer that separates utterance, interpretation, execution, screen state, and physical playback instead of collapsing them into “done.”
- **path:** pendant → relay → mac → browser
- **model tier:** A cheap background summarizer builds the timeline; realtime is used only for the owner's follow-up question. Vision is invoked only when a browser or screen postcondition must be checked.
- **latency:** 2–5 seconds for the common case; up to 10 seconds when a fresh screen/browser observation is required.
- **cost:** Usually <$0.01 using stored receipts and a small model; a fresh vision observation is the dominant additional cost.
- **security:** The report must redact transcript/audio and page text according to existing evidence-capsule policy, never imply playback from relay bytes, and require confirmation before exposing sensitive browser claims or taking a repair action.
- **missing:** A durable correlation ID carried from pendant utterance through relay turn, Mac job, browser command, and receipt.; A reader that joins pipeline events, action-ledger steps, browser provenance, and relay job status into one causal graph.; A device-originated playback event from the already-accepted audio_delivery_ack_queue, so the final node can say heard rather than merely sent.

### "Before you click, type, send, delete, or edit anything, tell me whether the target I approved is still the target on screen; if it changed, stop and show me the mismatch instead of guessing."
- **useful because:** A plan can be correct when made and dangerous seconds later. This turns the newly verified screen-control capability into a perception fence: the owner gets protection from stale tabs, changed forms, login walls, and focus changes without having to watch the screen.
- **path:** pendant → relay → mac → browser
- **model tier:** Use the cheap Mac/browser inspection path for stable regions; invoke the vision model only on a changed or ambiguous region. Realtime should speak the short verdict, not analyze the page.
- **latency:** Under 700 ms for a stable browser target; 2–4 seconds for a fresh screenshot and visual comparison.
- **cost:** Near-zero for URL/title/ref checks; <$0.02 for an ambiguous screenshot comparison, dominated by vision tokens.
- **security:** Never transmit page pixels or form values unless the owner has already authorized that domain; treat login walls and secret locators as hard stops; destructive or external-send actions always require explicit confirmation after the final check.
- **missing:** A precondition object in each planned action containing target URL/tab identity, locator, and redacted content hash.; A read-only compare endpoint that evaluates the precondition immediately before execution and returns match/mismatch with evidence.; An execution gate that refuses stale actions rather than merely logging the mismatch.

### "If I say “repeat what you heard,” show and speak the exact transcript with its capture-quality verdict, the words you were uncertain about, and the action you would have taken—without taking it until I confirm."
- **useful because:** Speech errors are currently invisible: a fluent answer can hide clipping, packet gaps, or a bad boundary. The owner can catch a misheard name, number, or command before it reaches Mail, Messages, a browser form, or a destructive Mac action.
- **path:** pendant → relay → mac → browser
- **model tier:** The pendant's local integrity sentinel supplies the tiny quality verdict; a cheap text model formats the transcript and highlights uncertainty. Realtime only handles the immediate spoken repeat-back.
- **latency:** Less than 1 second for local quality and transcript replay metadata; 2–3 seconds if retranscription is requested.
- **cost:** <$0.005 when reusing the stored transcript; retranscription audio tokens dominate and may cost <$0.03 per retry.
- **security:** Keep raw audio local and bounded; redact secrets in the displayed transcript; never echo an OTP, password, or private message aloud without confirmation; a degraded/unusable capture must force repeat rather than silently proceed.
- **missing:** A relay contract that preserves utterance sequence, transcript alternatives, and the offline-capture-integrity-sentinel verdict together.; A Mac route that renders a redacted transcript and proposed action separately from execution.; A hard policy hook making low-quality or ambiguous speech ineligible to authorize external or destructive actions.

### "Before you make a consequential change, let me rehearse the entire operation: show the browser edits, Mac file/app changes, messages that would be sent, and the exact point where an irreversible side effect begins—without touching the real world."
- **useful because:** Today planning and execution are separate and a preview rarely spans the browser session, Mac state, and relay delivery. A true rehearsal lets the owner catch a wrong account, recipient, file, or interpretation before one step escapes into an irreversible side effect.
- **path:** pendant → relay → mac → browser
- **model tier:** Use a cheaper planning model to construct a typed operation graph; use the vision model only to render browser previews. Realtime speaks a compact rehearsal summary and asks for confirmation.
- **latency:** 3–8 seconds for a normal multi-step rehearsal; under 2 seconds for a stored plan with no visual ambiguity.
- **cost:** About $0.01–$0.05 per rehearsal, dominated by browser screenshots and any document diffing; no external side effects until confirmation.
- **security:** Preview data may contain private logged-in content, so keep it on the Mac where possible and redact secrets. Never emulate a send as if it occurred. Confirmation must name the irreversible boundary, recipient/account, and final content.
- **missing:** A dry-run executor that can produce DOM/file/app diffs without committing them.; A typed operation graph with reversible and irreversible nodes, rather than an opaque action list.; Browser and Mac adapters that snapshot pre-state and render a faithful post-state preview, including relay speech delivery as a separate non-world-changing node.

### "Treat a request spanning email, browser, files, and the pendant as one transaction: if a later step fails, automatically undo every earlier reversible step, stop at the first irreversible boundary, and tell me exactly what remains."
- **useful because:** A multi-surface task can currently report individual success while leaving a half-finished, dangerous world. The owner gets all-or-nothing behavior where possible and an explicit repair list where it is not, instead of discovering partial completion later.
- **path:** pendant → relay → mac → browser
- **model tier:** A low-cost planner builds the transaction and compensation graph; realtime is reserved for announcing a pause, failure, or confirmation. No expensive model is needed for deterministic rollback.
- **latency:** Under 1 second to detect a failed step and halt; rollback may take 2–10 seconds depending on browser and app count.
- **cost:** Usually <$0.01 beyond the original task; cost is dominated by any re-observation needed to verify compensating actions.
- **security:** Never auto-undo irreversible sends, purchases, or deletions. Require confirmation for compensation that could itself have side effects, preserve a tamper-evident before/after record, and isolate browser credentials from relay logs.
- **missing:** A cross-surface transaction coordinator with durable step IDs and dependency order.; Compensation handlers that cover browser mutations and AppleScript/app mutations, not only the existing Mac job undo path.; A final verifier that checks actual file/UI/browser state after rollback rather than trusting an action receipt.

### "Give me a private, time-limited handoff mode: while I am away, let the system watch one browser task and one Mac task, ask no unnecessary questions, but wake me on the pendant only when a defined risk, ambiguity, deadline, or screen change occurs—and revoke the handoff automatically."
- **useful because:** The owner cannot currently delegate bounded attention across a logged-in browser, Mac applications, and a wearable without either constant supervision or broad trust. This would make “handle this while I’m busy” safe, quiet, and genuinely cross-device.
- **path:** pendant → relay → mac → browser
- **model tier:** A cheap policy evaluator and deterministic watchers handle routine progress; realtime is used only for the interrupt spoken to the owner. Vision runs on change events, not on a polling loop.
- **latency:** Normal state changes detected within 1–3 seconds; an interrupt should reach the owner within 2 seconds after a risk event when a pendant is connected.
- **cost:** Low when event-driven; roughly <$0.02 per handoff, with vision-token cost proportional to changed screens.
- **security:** The handoff must be capability-scoped (specific account, tab, files, recipients, and expiry), visible in a revocation panel, and fail closed on browser login changes, secure-input fields, permission prompts, or a missing pendant. Relay must not retain page content or secrets.
- **missing:** A signed delegation envelope shared by relay, Mac agent, and browser extension with scope, expiry, and revocation.; Event-driven browser/Mac change watchers with risk classification and a pendant delivery path that proves receipt.; A policy engine distinguishing progress from an interrupt-worthy ambiguity, plus a durable audit of every delegated step.


## What it asked for

_Nothing._
## Its own summary

Fresh probes establish that the exact AI Pendant Agent now has Accessibility and Screen Recording, inputReachability is verified, Safari's browser bridge is online with two tabs, and the relay is reachable through the Mac bridge. The local Mac agent does not expose /v1/devices/status, so pendant registry truth still requires a relay-facing read. I recorded three new owner-facing capabilities: causal cross-surface reconstruction of what happened, a pre-action target-drift fence, and safe transcript/capture-quality repeat-back before authorization. The proposals deliberately identify missing joins/gates rather than pretending existing receipts prove hearing or that existing inspection prevents stale actions.

**Biggest unknown:** Whether any physical pendant is connected remains unestablished: the Mac agent has no pendant route and its relay payload only says the bridge is online. We still need a relay-side device-status read and, separately, the firmware playback acknowledgment path before anyone can claim the owner heard audio.

