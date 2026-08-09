# Harness derivation — relay-realtime — round 250

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “keep an eye on this until it is resolved,” have the pendant watch the relevant Mac, browser, and relay state, interrupt me only when something materially changes or a decision is needed, and give me a one-sentence explanation plus the exact next choice."
- **useful because:** Today the owner must remember to poll jobs, watches, and disconnected computer work separately. This would turn the pendant into a quiet delegated assistant: no repeated status chatter, but no silent failure or stale task either. It is useful precisely because the wearer is away from the Mac.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use relay-realtime only to classify the spoken request and phrase an interruption; use a cheaper background model for change summaries and mac-planner/mac-vision for checks and actions.
- **latency:** Acknowledge in under 1 second; checks may run for minutes or days. Interrupt within 30 seconds of a detected material change.
- **cost:** About $0.01–$0.05 per check cycle depending on model summarization; most cycles should be no-change and use deterministic diffs. Storage and polling dominate operational cost, not realtime speech.
- **security:** Watching authenticated browser pages and local Mac state can expose sensitive changes. Store only hashes and redacted diffs by default, encrypt watch state, and require explicit enrollment of each watch target. Never speak page contents aloud unless the owner asks.
- **missing:** A durable cross-surface watch coordinator that can attach one watch to a job, browser page, or Mac predicate and normalize their change events; Materiality/debounce policy shared by relay and browser/mac agents; A reliable push path from coordinator to pendant inbox, with expiration and deduplication; User-facing watch enrollment and cancellation in the dashboard

### "Take whatever I am discussing on the pendant and hand it to my Mac as a usable artifact: open the right app or browser page, put the relevant transcript, links, and decisions there, and leave me a visible “continue here” workspace when I sit down."
- **useful because:** A worn voice interface is excellent for capturing intent while walking but poor for inspecting long text or editing. Today the conversation and the Mac actions are separate worlds. This would make the pendant a true front door to a persistent desktop task rather than a voice-only dead end.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime handles the short handoff utterance and extracts the target; a background planner assembles and labels the artifact. mac-planner executes app/file actions and browser-extension supplies authenticated links or page state.
- **latency:** Acknowledge immediately; create a first usable workspace within 10 seconds when the Mac is online, otherwise queue it and notify when available.
- **cost:** Roughly $0.02–$0.10 per handoff, dominated by transcript condensation and artifact generation; deterministic open/type actions are cheap.
- **security:** The artifact may contain private speech and authenticated URLs. Keep it local to the owner’s Mac by default, redact secrets from the relay payload, show provenance and timestamps, and let the owner say “erase that workspace” to remove it.
- **missing:** A first-class handoff artifact schema (summary, transcript spans, links, decisions, pending questions, provenance); A Mac-side workspace renderer that can target Notes, VS Code, a browser tab, or a generated local file; Session identity linking the pendant conversation to a Mac workspace without leaking raw audio; A reconnect path that completes a queued handoff when the Mac returns


## Changes it proposed to its own stack

### `hardware` — Add a deliberate privacy control to the jewellery pendant: a tactile hardware microphone-disconnect switch (or a mechanically latching second button) that removes microphone power locally, plus a latched privacy state reported over serial/LTE and a distinct haptic confirmation. The relay must refuse to start capture while the latch is engaged and must surface the state in every health/voice response.
- **owner gets:** The owner can physically know—and prove—that the pendant cannot hear them, even if software is crashed, misconfigured, or the network is compromised. This makes wearing an always-available microphone acceptable in private places and gives an immediate answer to “are you listening?” without reaching for a Mac or phone.
- effort: Medium hardware spin and firmware integration: route mic power through a normally-open/closed privacy switch, debounce and persist the state, expose it in the device beacon, and add a relay-side capture interlock and dashboard indicator. Validate across USB and LTE reconnects and brownouts.  ·  risk: A stuck or accidentally engaged switch makes voice capture unavailable; recover by a clear tactile position, haptic confirmation, and a spoken/LED diagnostic when the owner presses the talk button. Fail closed on uncertain GPIO state. Ensure the switch cannot short the battery or leave the codec powered.
- cost: Prototype enclosure/PCB change roughly $2–$8 in parts and assembly; negligible steady-state power change, with a few hundred microamps at most for a sensing pull-up.  ·  latency: No added speech latency. The relay should reject a press immediately from the last beacon and re-check the device state before accepting audio.
- security: Strongly improves privacy by enforcing consent below the application layer. The relay must not be able to override it; report only boolean state and diagnostic timestamps, never raw mic data.
- depends on: A firmware GPIO/power-domain implementation on the nRF9160 and ESP32 audio bridge; Extend offline-reality-beacon with privacy-latch state and a monotonic transition counter; A relay capture gate that treats missing or stale privacy state as unavailable rather than permissive; A physical enclosure revision consistent with the owner’s jewellery form factor


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing additions: (1) a quiet cross-surface watch that interrupts only on material changes or decisions, (2) a pendant-to-Mac handoff that creates a usable continuation workspace, and (3) a hardware-enforced microphone privacy latch with relay interlock. The first is the highest-value daily capability because it lets the owner delegate without polling while away from the Mac.

**Biggest unknown:** Whether the existing watch and session routes already have an unobserved artifact/push contract; the proposals deliberately identify the missing cross-surface coordinator, durable handoff artifact, and hardware privacy boundary rather than assuming those routes are sufficient.

