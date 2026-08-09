# Harness derivation — relay-realtime — round 256

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I press the pendant and say “what am I looking at?”, have you inspect my current Mac screen and browser tab, explain the relevant page in one sentence, and let me say “do that” to act on the exact thing I meant."
- **useful because:** The owner is often away from the keyboard and cannot narrate URLs, app names, or page state. This turns the pendant into a conversational control surface for the screen already in front of them, with the Mac supplying pixels and browser sessions supplying authenticated context.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Realtime relay for the short exchange; mac-vision gpt-4.1-mini for screen grounding; mac-planner gpt-5.6-luna only after the owner says the follow-up action.
- **latency:** Initial spoken answer under 4 seconds; screen capture and focused-app/browser inspection in parallel, with a concise fallback if either surface is offline.
- **cost:** About $0.01–$0.05 per inspection depending on screenshot tokens; the relay turn dominates only when the owner asks a follow-up.
- **security:** A screenshot and page metadata leave the Mac and may contain secrets. Redact known credential fields, never speak hidden values, bind the follow-up action to the captured page/session, and require a fresh explicit utterance for mutations.
- **missing:** A live mac-vision computer-use loop (currently disabled) that can return a focused screenshot plus structured UI/page grounding; A relay session primitive that pins the captured screen/browser state to the next utterance; A safe handoff from browser-extension inspection to mac-planner action

### "Let me say “send this to Alex” while wearing the pendant, and have the system resolve “this” from the item currently open on my Mac or in my authenticated browser, show me a spoken preview of the exact recipient, subject, and attachment, then carry out the send when I say “send it.”"
- **useful because:** Today the owner must bridge the physical distance to the Mac by naming files, URLs, and recipients manually. This makes deictic speech (“this”, “that page”, “the report”) useful across the pendant, Mac filesystem, and browser session without guessing silently.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Realtime relay resolves the dialogue and asks one clarification if needed; mac-vision/browser-extension establish the referent; mac-planner prepares the outbound action and returns a deterministic preview.
- **latency:** Resolve and speak a preview within 6 seconds; hold execution until the explicit second utterance, then report the resulting receipt.
- **cost:** Roughly $0.03–$0.10 per request, dominated by one screenshot/page extraction and planner call; no continuous monitoring cost.
- **security:** Referent confusion could disclose or send the wrong document. Include canonical path/URL, recipient identity, content hash and attachment list in the preview; expire the preview after 60 seconds and never infer a recipient from a vague name when multiple matches exist.
- **missing:** Cross-surface referent resolution that joins focused UI, browser tab, selected file and recent spoken noun phrases; A preview token that cryptographically binds the spoken confirmation to the prepared content and recipient; A Mac/browser action adapter for the final send that returns content hashes and delivery receipts

### "Before you act on a consequential request, tell me whether the Mac and browser agree about what will happen. If they disagree, speak the conflict (“the page shows $80 but the Mac cart has $95”), ask me which source to trust, and only then continue."
- **useful because:** A wearable voice command has little visual affordance for catching stale tabs, unsaved edits, wrong accounts, or changed prices. Independent evidence comparison lets the owner safely operate across surfaces without requiring them to stand at the Mac and inspect both states themselves.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Cheap background perception calls gather structured facts; realtime relay compresses only the disagreement and asks the owner; judgement/action tiers execute after resolution.
- **latency:** Normal agreement in 3–5 seconds; disagreement may take 8 seconds but should speak an immediate “I found a conflict” cue before the full details.
- **cost:** About $0.02–$0.08 per consequential request, mostly two small perception calls; routine low-risk requests bypass it.
- **security:** The comparison itself may expose private page data in speech. Speak only fields necessary to decide, hash or redact sensitive values, and retain the evidence bundle only for the conversation’s short lifetime.
- **missing:** A structured evidence schema shared by faculty-perception, Mac planner, and browser inspection; A relay conflict detector that compares claims with provenance and freshness timestamps; A spoken resolution state that binds the owner’s choice to the subsequent action


## Changes it proposed to its own stack

### `integration` — Add a transport-handoff layer that treats the USB-connected nRF9160 pendant and the ESP32 audio bridge as a local edge path when LTE is absent: the Mac bridge should advertise the pendant session to the relay, forward button/audio/downlink packets over serial, preserve one monotonic conversation ID across USB↔LTE transitions, and reconcile acknowledgements so a reply is neither lost nor played twice.
- **owner gets:** The owner can use the pendant today at a desk or in a dead LTE area without the conversation failing, then walk away and continue on LTE without restarting or losing the reply. The same physical pendant behaves as one device instead of two unrelated modes.
- effort: Medium-high: bridge daemon, relay session reconciliation, serial reconnect handling, and hardware soak tests across unplug/replug and LTE return.  ·  risk: Duplicate audio, stale sessions, or replayed commands during a handoff. Recover with monotonic packet sequence numbers, durable relay acknowledgements, bounded replay windows, and a visible/ spoken “connection changed” status rather than pretending continuity.
- cost: Minimal API cost; approximately 20–40 hours engineering. No new hardware required for the currently USB-attached boards; optional always-on Mac helper uses negligible CPU and under 1 W average.  ·  latency: USB path can be lower latency than LTE; handoff may add 1–3 seconds while reconnecting and reconciling.
- security: The Mac becomes a local transport authority. Pair the serial device to the relay with a rotating key, bind the bridge to the existing device identity, and reject commands from an unpaired USB device.
- depends on: A real Mac bridge daemon for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; An authenticated pendant announce/session route on the relay; Sequence-numbered acknowledgements for the audio and command pipelines; The existing POST /pipeline/audio and POST /pipeline/events semantics

### `interaction` — Add a “quiet confirmation” interaction: after the owner gives a command from the pendant, the relay sends a short haptic/LED-coded preview event to the device and waits for a distinct physical confirmation gesture, while the spoken channel remains free for unrelated conversation. The Mac/browser action is released only when both the spoken intent and the physical preview acknowledgement match the same nonce.
- **owner gets:** In a noisy street, meeting, or situation where speaking a second confirmation is awkward, the owner can approve a prepared action with the pendant itself while still getting an accurate spoken preview. It reduces accidental sends without making every command a verbal ritual.
- effort: Medium: add nonce-bound preview records, a firmware gesture/state, relay timeout handling, and adapters that defer execution until acknowledgement.  ·  risk: A gesture could be accidental or misunderstood. Use a short expiry, require the preview to be generated first, provide a cancel gesture, and revert to spoken confirmation when the device cannot signal reliably.
- cost: Low API cost; roughly 1–2 weeks firmware/relay work. No new hardware if the existing button can use a press pattern; a second button would make the gesture clearer but is not required.  ·  latency: Adds 0.5–2 seconds for the physical acknowledgement; no added cost for read-only commands.
- security: Improves protection against accidental high-impact actions, but the nonce must be unguessable and bound to device identity and session. Do not treat a stale button event as confirmation.
- depends on: A relay preview/nonce record associated with POST /plan and POST /execute; A firmware event route using the existing button/LED state machine; A real execution gate rather than merely logging confirmation; The existing offline alert inbox for surfacing a preview when the link briefly drops


## What it asked for

_Nothing._
