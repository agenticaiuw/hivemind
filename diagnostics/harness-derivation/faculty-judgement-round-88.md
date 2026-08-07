# Harness derivation — faculty-judgement — round 88

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“When I walk away from my Mac, save exactly where I was and what I meant to do; when I come back or ask from the pendant, give me a 20-second handoff and let me resume without hunting.”"
- **useful because:** The owner loses time and intent at the ordinary boundary between desk and life. This would turn a physical transition into a reliable, privacy-aware handoff: the pendant notices the link change, the Mac captures the active work state, the browser contributes the relevant private tab context, and the relay preserves it until the owner is ready. It is not just a Mac snapshot or a reminder; it preserves the unfinished goal and the next safe action across all bodies.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a cheap background model to compress the handoff and extract a single next action; use realtime only when the owner asks for or receives the short spoken handoff. Deterministic code should collect app/tab/job metadata and enforce privacy and expiry; no expensive model is needed for collection.
- **latency:** Capture within 3 seconds of a Mac↔pendant transition; reconnect response under 1 second from cached state; spoken brief under 20 seconds. Background compression may take up to 30 seconds.
- **cost:** About $0.002–$0.01 per transition, dominated by one small background summarization; near-zero cost when no meaningful state changed. Storage is a small encrypted record per transition.
- **security:** Capture only allowlisted app names, window titles, URLs, selected text, and explicit in-progress jobs; never capture passwords, page bodies, or secrets by default. Local redaction must happen before relay upload; private browser data needs the existing authenticated bridge and a short TTL. Resuming an external side effect (send, buy, delete, submit) must still require confirmation. Provide a pendant stop gesture and owner-visible delete/forget controls.
- **missing:** A pendant link-transition event with monotonic timestamp and local queueing while offline; A Mac snapshot endpoint that reports active app/document, unsaved-edit hints, and in-progress relay jobs without screen recording; Browser bridge support for a user-approved current-tab semantic summary with tab/session affinity; An encrypted, expiring cross-surface handoff record and a deterministic relevance/secret-redaction policy; A resume protocol that presents the next action as a proposal rather than silently executing it; A reconnect-triggered pendant audio queue and acknowledgement so the owner can defer or dismiss the handoff


## Changes it proposed to its own stack

### `interaction` — Add a cross-surface “claimability ladder” enforced before every spoken completion or status answer. It classifies each requested fact/action as observed-live, observed-cached-with-age, queued-not-confirmed, or unavailable; requires the response to name the source and freshness for non-live states; and automatically offers the narrowest useful fallback (for example, AppleScript Calendar instead of an unavailable browser tab). For actions, it distinguishes accepted, started, completed, and receipt-verified rather than collapsing them into “done.” The pendant uses a compact spoken form; the Mac dashboard exposes the evidence trail.
- **owner gets:** The owner has repeatedly asked for mail, calendar, browser access, and job completion, and failures have been easy to mistake for success. This makes the assistant trustworthy in ordinary life: it will say “I queued it, but cannot verify completion” instead of inventing certainty, and it will still help through another reachable surface.
- effort: Medium: shared response-state schema, router middleware, fallback mapping, and concise voice rendering; then test against offline pendant, disconnected bridge, stale cached tabs, and interrupted Mac jobs.  ·  risk: More cautious answers may feel less magical, and a fallback could expose a different source than expected. Recover by showing source/age, preserving the original request, and requiring confirmation for any fallback that mutates data. Never infer completion from HTTP acceptance alone.
- cost: Negligible runtime cost; a few hundred tokens of structured evidence per task. Occasional cheaper model call only for fallback selection when deterministic mappings do not suffice.  ·  latency: Under 50 ms for classification; fallback discovery may add normal tool latency, but it should be explicit rather than delaying a definitive answer.
- security: Improves security by preventing stale/private evidence from being presented as current. Source labels must not leak sensitive URLs or secret values into spoken output; retain detailed provenance only behind authenticated dashboard access.
- depends on: A shared typed evidence/result envelope across POST /execute, GET /jobs/:jobId/receipts, browser action results, and Mac action receipts; A small registry of allowed read-only fallbacks (AppleScript/Mac routes versus authenticated browser); The existing receipt/undo and browser request-id work must remain attached to results

### `hardware` — Add a physically latching microphone disconnect and a separate privacy-status indicator to the pendant: a normally-open analog switch or codec power gate controlled by a recessed slider, plus a bright edge LED that is electrically driven from the mute state rather than software. Expose the state to firmware and include it in signed session metadata so the relay can refuse to claim that audio is available while the microphone is physically muted.
- **owner gets:** The owner should be able to wear an always-available assistant without having to trust software when discussing private matters. A real, visible, hardware-enforced mute gives them an immediate boundary they can verify by touch and sight, including when the network or firmware is malfunctioning.
- effort: Medium hardware revision: add the switch, indicator driver, PCB routing, enclosure opening, debounce and boot-state handling, then update firmware, relay session negotiation, and manufacturing tests. This is deliberately not reducible to a software mute button.  ·  risk: A damaged or partially engaged switch could leave the owner uncertain, and a hard power gate can create audible pops or lose an utterance. Use a fail-closed mute state, debounce with a hardware RC filter, ramp codec power, emit a local confirmation tone only on unmute, and show the last transition in diagnostics. If the LED fails, the physical position remains authoritative and the relay treats unknown state as muted.
- cost: Roughly $0.30–$1.50 in components plus PCB/enclosure revision; under 10 mW for the indicator while active, zero microphone power while muted. No per-use API cost.  ·  latency: Negligible; hardware mute is immediate. Session negotiation may take one extra round trip when changing state so the relay and Mac do not process stale audio.
- security: Strongly positive: audio cannot reach the codec/transport while muted, and the relay receives an attested state instead of trusting a UI flag. The indicator must not be software-suppressible. This does not protect audio already transmitted before the switch was engaged, so the device should maintain only a very short prebuffer.
- depends on: A signed pendant session-state field for physical mute/unknown; Relay audio ingress rejection when mute is asserted or state is unknown; Firmware diagnostics and manufacturing test coverage for switch and indicator faults; A clear enclosure and industrial-design decision for the tactile control


## What it asked for

_Nothing._
