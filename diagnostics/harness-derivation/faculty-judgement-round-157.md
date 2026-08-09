# Harness derivation — faculty-judgement — round 157

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "After a briefing, when I ask “what did I actually hear?”, give me a truthful list of items that finished playing, items I interrupted or never received, and let me replay only the missed ones."
- **useful because:** A generated audio file is not the same as the owner receiving it. This turns the pendant into a reliable memory aid: it distinguishes delivered knowledge from merely produced knowledge and avoids repeating items already heard.
- **path:** relay-realtime → pendant → mac-planner → dashboard
- **model tier:** background for assembling the receipt-backed digest; realtime only for the short spoken answer
- **latency:** under 2 seconds for the spoken status; replay should begin at the next available audio boundary
- **cost:** <$0.01 per query when receipts are structured; model cost dominates only when compressing many missed items
- **security:** Speak only item titles and delivery states by default; require explicit request to reveal sensitive content. Use artifact IDs and authenticated device-session ACKs, never raw audio, as the join key. A replay must be gated by the owner’s normal physical playback control.
- **missing:** A durable join from briefing item IDs to generated artifact IDs; A read API that combines record_pendant_delivery_event events with briefing item metadata; A retry/replay operation that creates a fresh artifact without marking the original as heard

### "When I get back to my Mac, tell me in one short account what the hive changed while I was away: files or reminders created, browser drafts prepared, actions refused, and anything still awaiting my physical approval."
- **useful because:** Today each body reports its own completion and the owner has to reconstruct the day from unrelated logs. A return-home account answers the human question—what changed in my life, what did not, and what needs me—without implying that a server-side job was actually completed on the pendant.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background model over structured receipts, with a cheap deterministic grouping pass first; realtime only when the owner asks for the spoken sentence
- **latency:** precompute after each job and keep the spoken answer under 1 second
- **cost:** <$0.02 per daily digest; grouping and deduplication should be deterministic, with model tokens spent only on final compression
- **security:** Default to application names, action types, and reversible status—not document contents, mail bodies, URLs with secrets, or third-party names. Every line links to a receipt and provenance explanation. Destructive or externally visible actions must be explicitly labeled and never described as successful without a receipt.
- **missing:** A durable relay-job/Mac-job/browser-command foreign-key mapping instead of telemetry-only localJobId; A single read model for action receipts, refusals, pending approvals, and pendant delivery ACKs; An owner-return trigger based on a real USB pendant/session event or an explicit “I’m back” utterance; A deterministic dedupe and state transition for queued, applied, undone, expired, and refused effects

### "Keep my pendant usable when LTE is unavailable: if it is plugged into my Mac over USB, carry the live voice session and audio over that tether automatically, then resume the same conversation over radio later without making me start over."
- **useful because:** The hardware is physically present and testable now, while LTE registration is not. The owner should not lose the central benefit of a wearable simply because the radio is offline; USB should be an immediate, transparent fallback and radio should become a transport change rather than a new conversation.
- **path:** pendant → mac-planner → relay-realtime → relay
- **model tier:** realtime for the voice session; deterministic transport/session code for failover and replay, with no background model required
- **latency:** USB audio round-trip target under 250 ms; transport failover should be announced in one brief tone or sentence and preserve the current turn
- **cost:** Negligible model increment; engineering cost is serial framing, stream buffering, authenticated session handoff, and hardware soak testing. Audio bandwidth is already proven at 24 kHz/60 ms frames.
- **security:** Treat USB as an authenticated local transport, not an implicit trust boundary: bind the serial session to the Mac agent bearer/session, rotate a nonce on every attach, and reject stale radio commands. Do not persist microphone PCM on the success path. On failover, either complete or explicitly cancel a turn—never duplicate speech or actions.
- **missing:** A production USB serial transport between /dev/cu.usbmodem00096003658* and the local agent; A transport-neutral pendant session protocol with sequence numbers, replay protection, and half-open detection; A relay session lease/handoff that accepts a new transport without creating a second job; A tested USB path for the ESP32 audio bridge and nRF9160 together, including backpressure at the proven 60 ms Opus framing

### "Notice when I repeatedly correct the same kind of decision, show me the pattern with concrete examples, and let me teach one reusable rule without silently changing your behavior."
- **useful because:** The owner should not have to restate the same preference every week, but an assistant must not infer a permanent life rule from one exception. This capability turns corrections into an explicit, reviewable lesson: “you declined these three Friday tidy-ups; should I stop proposing them on Fridays?” It improves judgement rather than merely adding another automation.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background model clusters correction receipts and drafts a candidate rule; deterministic policy evaluation enforces only rules the owner explicitly accepts; realtime speaks only the short proposal
- **latency:** candidate suggestions can arrive in a daily digest; acceptance must return in under 1 second and affect the next matching decision
- **cost:** <$0.03 per candidate rule, dominated by clustering a small set of receipts; accepted rules reduce future model calls
- **security:** Never infer sensitive traits or apply a rule from behavior alone. Show the exact examples, scope, expiry, and exceptions before acceptance. A rule affecting external communication, spending, deletion, or sensitive disclosure must remain confirmation-required even after acceptance. Store a rule’s provenance and make revocation immediate across all surfaces.
- **missing:** A durable correction record that distinguishes owner override, system refusal, failure, and ordinary completion; A rule-candidate schema with scope, examples, exceptions, expiry, confidence, and owner acceptance state; A shared accepted-rule store consumed by relay, Mac, browser, and pendant rather than a Mac-local in-memory registry; A replay/evaluation view showing how the candidate would have changed past decisions without mutating them


## What it asked for

_Nothing._
