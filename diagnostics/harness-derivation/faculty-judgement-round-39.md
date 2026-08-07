# Harness derivation — faculty-judgement — round 39

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Before I approve this, tell me whether anything important changed since you prepared it.”"
- **useful because:** Prepared actions go stale: a meeting moves, an invoice changes, a web form expires, or someone replies while the owner is deciding. The owner gets a short, spoken delta and a fresh approve/edit/abandon choice instead of blindly applying yesterday's plan.
- **path:** relay-realtime → browser-extension → mac-planner → mac-vision → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Background model computes normalized before/after deltas and risk; realtime is used only for the final one-sentence spoken decision brief and follow-up conversation.
- **latency:** On approval, 2–5 seconds for a lightweight recheck; up to 15 seconds for several authenticated tabs plus Mac files. Never block the initial draft; the sentinel runs only between draft and commit.
- **cost:** Usually <$0.02 per approval: most cost is browser/Mac reads and a small background comparison; realtime costs only the short spoken summary. No repeated full-page context should be sent to the model—hashes, changed fields, and cited snippets suffice.
- **security:** Recheck only the tabs/files used by the draft, with the same owner session and least privilege. Do not upload whole private pages or unrelated Mac content. Sending, deleting, purchasing, or submitting still requires explicit approval after the delta; if a source cannot be revalidated, fail closed and say so.
- **missing:** A durable draft/plan record containing source fingerprints, extracted fields, intended mutations, and expiry; Typed browser and Mac read snapshots with stable provenance and redaction; A pre-commit gate in faculty-action that can pause an already prepared job and return a compact delta to the pendant; A pendant approval UI that distinguishes approve-unchanged from approve-after-change

### "“Make this conversation safe to continue with other people around.”"
- **useful because:** The owner should not have to choose between using the assistant and accidentally exposing private mail, account names, reminders, or spoken answers in a room. A deliberate privacy mode would turn the pendant into a socially safe interface: brief neutral audio, no secrets spoken, and private work diverted to a trusted screen or held for later.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Realtime handles the immediate mode switch and short neutral replies; a cheaper background model classifies queued work and prepares a private Mac/browser review, with no need to resend sensitive context.
- **latency:** Mode switch and acknowledgement under 300 ms locally; each private task can be queued in under 2 seconds. The owner should never wait for classification to receive a safe response.
- **cost:** Under $0.01 per interaction when no private task is queued; dominant cost is optional background summarization of deferred work. Local mode state avoids repeated prompt context.
- **security:** Privacy mode must be an explicit button gesture or spoken command, not inferred solely from microphone audio. While active, the relay must redact secrets from speech generation, suppress private source titles/URLs, and prevent browser/Mac mutations unless separately approved. A visible Mac indicator and a distinct pendant tone should show the mode; fail closed on uncertain classification. Private audio and transcripts should not be retained by default.
- **missing:** A pendant-local privacy-mode state with a physical gesture, unmistakable tone, and persistence across reconnects; A relay speech policy that can guarantee secret-free responses and reject a response containing protected entities; Typed sensitivity labels and redaction for browser, Mac, memory, and queued audio results; A cross-surface private inbox on the Mac that receives deferred work without speaking its contents; End-to-end tests with reconnects, model failure, and accidental wake words


## Changes it proposed to its own stack

### `firmware` — Replace the prototype's split 16 kHz uplink / 24 kHz playback path with a negotiated end-to-end superwideband session: relay advertises Opus mode and bitrate, pendant reports buffer/packet-loss telemetry, and both sides switch among 24 kHz, 16 kHz, and a tiny text-only fallback without dropping the conversation. Add a resumable audio-item protocol so a relay-generated brief from Mac/browser work carries item IDs, source links, and play position; a button press pauses/skips and the next session resumes exactly there.
- **owner gets:** The pendant sounds like a dependable everyday assistant rather than a demo: clearer speech when the network is good, intelligible fallback in a bad spot, and no lost place in a briefing when life interrupts.
- effort: Medium-high: relay negotiation and telemetry, firmware jitter buffer/state machine, bridge clock validation, and acceptance tests across packet loss, reconnect, and sleep/wake. Requires replacing the current prototype assumptions and an actual product audio path.  ·  risk: Higher decode CPU (currently roughly 87% of one core when encode and decode overlap) can cause underruns or heat; cap decode complexity, monitor buffer depth, and fall back before audio breaks. A malformed resume token could replay or skip a private item; sign item metadata and expire it. Recover by resetting to the last acknowledged item boundary.
- cost: No meaningful per-request API increase; telemetry is small. Prototype hardware may need a better audio MCU/codec or dual-core budget, roughly $5–20 BOM increase depending on product choice, plus battery impact from sustained decode.  ·  latency: Negotiation adds <200 ms at session start; 60 ms frames remain interactive. Fallback switching should complete within one frame; resume metadata is asynchronous.
- security: Audio and source URLs remain encrypted in transit; avoid logging transcript/audio payloads in telemetry. Item IDs should be opaque, and private source links must not be spoken or exposed to an unauthenticated bridge.
- depends on: A production pendant/bridge audio design rather than the current Nordic development-kit prototype; Relay support for durable audio items and acknowledgements; A verified reconnect/session identity shared by pendant and relay

### `hardware` — Add a real, electrically enforced microphone privacy control to the product pendant: a recessed two-position mute switch that disconnects the microphone power/data path, a high-visibility mechanical/LED state indicator, and firmware that reports the physical state to relay before accepting voice input. Keep the existing action button separate so privacy mode can be engaged without waking the mic.
- **owner gets:** They can wear and use the assistant around other people without relying on a model to infer whether a conversation is private. The owner gets an immediate, trustworthy way to know the pendant cannot hear or speak private content, even during a dropped network link or server fault.
- effort: Medium hardware/firmware redesign: microphone power gating, debounced state input, enclosure change, boot/reconnect handling, and relay refusal when the reported state is muted. Validate that mute remains effective through brownouts and firmware crashes.  ·  risk: A switch or indicator failure could create false confidence; use a normally-open hardware mute path, test it independently of firmware, and make unknown state mean muted. Power cycling may reset software state, so the physical indicator must remain authoritative. Added enclosure openings can reduce water resistance.
- cost: Approximately $0.30–$2 BOM increase for switch, gating component, indicator, and enclosure work; negligible steady-state power, with a small LED cost only while changing state.  ·  latency: No conversational latency impact. Hardware mute/unmute indication should settle in under 50 ms; reconnect authorization may add at most one handshake round trip after unmuting.
- security: Strongly improves local privacy by making microphone capture impossible while muted; the switch state must be cryptographically authenticated to the relay so a compromised app cannot claim the mic is muted. Do not treat software-only mode as equivalent to hardware mute.
- depends on: A product pendant enclosure and microphone power schematic (the current Nordic development kit is provisional); Firmware support for authenticated hardware-state telemetry; Relay speech and capture gates that fail closed on unknown or stale mute state


## What it asked for

### `t15-p8zd` (tool) — revalidate_pending_plan
- why: The proposed stale-plan sentinel cannot safely compare a prepared browser/Mac action against current state without a typed, least-privilege recheck that returns only changed fields and provenance. Existing generic execution tools are too broad and may commit actions.

```json
{
  "type": "object",
  "required": [
    "planId"
  ],
  "properties": {
    "planId": {
      "type": "string",
      "description": "Durable draft/plan identifier"
    },
    "maxAgeSeconds": {
      "type": "integer",
      "minimum": 0,
      "maximum": 86400
    },
    "sources": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Optional source IDs; defaults to sources captured in the plan"
    },
    "includeSensitiveSnippets": {
      "type": "boolean",
      "description": "Must default false; only true after explicit owner request"
    }
  }
}
```

## Its own summary

Round 39 produced two new, non-duplicate deliverables. (1) Proposed an end-to-end negotiated 24 kHz superwideband audio path with loss-aware fallback, telemetry, and resumable source-linked audio items—directly addressing the owner's stated audio goal while accounting for the prototype's ~87% overlapping codec CPU load. (2) Proposed a cross-surface stale-plan sentinel: immediately before approval, recheck only the browser/Mac sources used by a draft, speak a concise change delta, and fail closed when revalidation is unavailable. I also queued a precise read-only `revalidate_pending_plan` tool request and notified faculty-action about the required pre-commit pause gate.

**Biggest unknown:** Whether the current durable job/receipt implementation can persist source fingerprints and pause a prepared irreversible action before commit. The audio design also still needs a product-grade pendant/bridge decision; the current Nordic development kit is explicitly only a prototype. I still need those implementation facts, plus the relay's durable audio-item/acknowledgement primitives, before these can be made concrete.

