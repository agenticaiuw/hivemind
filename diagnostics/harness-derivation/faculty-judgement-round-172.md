# Harness derivation — faculty-judgement — round 172

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Give me my briefing, and if I miss part of it, pick up exactly where I stopped—never tell me it was delivered unless the pendant confirms I heard it.”"
- **useful because:** Today generation and relay acceptance can look successful while the pendant may never download or play the audio. A delivery-aware briefing would distinguish generated, downloaded, started, finished, and interrupted, resume at the exact item/position after a disconnect, and avoid duplicate replays. This is the clearest path from ‘the system said it did it’ to ‘I actually received it.’
- **path:** relay → pendant → mac-planner → dashboard-ux
- **model tier:** Use the cheap deterministic relay for artifact state, deduplication, ACK reconciliation, and resume offsets; use the low-latency model only to produce a short spoken recovery sentence when an item is interrupted or missing.
- **latency:** Normal briefing delivery remains streaming; ACK ingestion under 100 ms. Recovery status should be available on reconnect within 1 s, with no model call unless wording is needed.
- **cost:** Usually <$0.001 per briefing beyond existing TTS/audio generation; storage and ACK writes dominate, not inference.
- **security:** ACKs must be authenticated to a device session, monotonic-sequence checked, idempotent, and bound to an opaque artifact/item ID rather than transcript text. Dashboard may show detailed evidence; spoken recovery must not reveal sensitive briefing content. Require confirmation before replaying a sensitive item aloud.
- **missing:** A durable join between briefing item IDs, audio artifact IDs, and pipeline/job IDs; Server-side reconciliation that consumes record_pendant_delivery_event and marks delivery truth in receipts; Resume-aware briefing queue semantics on the relay and dashboard; A Mac/USB transport adapter for the currently tethered but LTE-unregistered pendant

### "“When I press the pendant’s marker button as I leave, make a private handoff packet; when I mark that I’m back, tell me only what changed and what needs my attention.”"
- **useful because:** The wearable is the only surface that knows the owner intentionally crossed a real-world boundary, while the Mac and browser know what was open and what changed. This turns an otherwise meaningless offline moment marker into a reliable, privacy-preserving return ritual: no accidental ‘where were you?’ inference, and no replay of stale tabs or sensitive page contents.
- **path:** pendant → mac-planner → browser-extension → relay → dashboard-ux
- **model tier:** Use deterministic snapshots, hashes, timestamps, and diffing for almost everything. Use a cheap background model only to compress already-authorized change summaries; never send page bodies or raw calendar/mail content merely to create the packet.
- **latency:** Departure marker acknowledgement under 200 ms locally; snapshot within 3 s when USB is available. Return summary within 2 s, otherwise queue it and say it is still assembling.
- **cost:** <$0.002 per handoff when compression is needed; most packets are hashes and structured state, so storage and browser polling dominate.
- **security:** The owner explicitly marks the boundary; still default to app/domain names, counts, deadlines, and hashes—not tab titles, mail subjects, or page text. Packets expire after 24 hours and can be deleted as one object. A disconnected Mac must not claim it captured the departure snapshot; it should record marker-only and say what was unavailable.
- **missing:** A marker_kind extension and packet identifier on the existing offline_moment_bookmark record; A USB bridge that carries sw1 marker events to the Mac while LTE is unregistered; A read-only snapshot/diff contract spanning Mac jobs, browser tabs, pipeline state, and authoritative machine timezone; A durable relay handoff store with explicit expiry and deletion

### "“Before any words leave the pendant, check whether they are safe to say aloud here; if not, give me a useful redacted answer or put it on my private dashboard instead.”"
- **useful because:** The strongest existing redaction runs only through briefingTriage. pendantSpeech and audioBrief can currently speak arbitrary result text, including sensitive browser or mail content, and they do not know whether the owner is in public. A single final gate on every audio path would prevent the most damaging class of failure without requiring the model to be trusted.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard-ux
- **model tier:** Deterministic classifier and policy evaluator at the final audio boundary; no expensive model for ordinary blocks. Use the realtime model only to produce a minimal safe paraphrase when structured fields cannot be reduced mechanically.
- **latency:** Under 20 ms for classification/policy and under 150 ms for a safe replacement. A blocked item should never wait on a model before silence; dashboard delivery can be asynchronous.
- **cost:** Near-zero inference cost for normal traffic; occasional paraphrase costs <$0.001. The main engineering cost is routing every spoken path through one gate.
- **security:** Treat sensitivity as a disclosure policy input, not an authorization level. Ship a conservative policy object with empty trusted-origin exceptions until the owner sets them; every block must name the rule and retain a local audit receipt without storing the raw spoken secret. The pendant should receive only the approved text, never the withheld payload. Public/bystander state is not currently available, so the gate must honestly use explicit owner mode, active focus/session state, and a ‘unknown—suppress’ fallback rather than inventing presence.
- **missing:** A mandatory final hook shared by pendantSpeech, audioBrief, pipeline audio, and spoken confirmations; A policy table for destination and sensitivity classes, editable by the owner and versioned in receipts; A trustworthy public/private presence input or explicit owner-selected privacy mode; A safe paraphrase generator that cannot see withheld raw content

### "“Hand this exact item to Alex for me, but let them see only what I chose, for one day, and tell me when they opened it.”"
- **useful because:** The system can act across the owner’s devices, but it cannot safely delegate a bounded piece of work or information to another human. This would turn the pendant into a controlled handoff tool rather than an assistant that only talks back to its owner: select a source on the browser or Mac, review the redacted packet, send it through an approved channel, and receive an auditable open/expiry signal.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard-ux
- **model tier:** Deterministic packet construction, redaction, recipient/domain policy, expiry, and receipt tracking. Use the expensive model only to draft a concise handoff from owner-approved source spans; never let it choose the recipient or expand the source.
- **latency:** Preview in under 2 seconds; sending only after explicit physical approval. Delivery/open receipts may arrive asynchronously, with a short spoken confirmation when they do.
- **cost:** Typically under $0.01 per handoff; costs are outbound message/API fees and receipt storage, not inference.
- **security:** Default to no external recipient allowlist and no raw source bodies in model prompts. Require physical approval over the exact recipient, fields, expiry, and action. Use a one-time signed packet, revoke link, recipient-visible provenance, and fail closed if the browser session or mail permission is stale. Never infer that an open receipt means agreement or completion.
- **missing:** A recipient/permission model distinct from the owner’s own surface permissions; A structured redacted handoff packet and review UI; An outbound delivery adapter with open/expiry/revocation receipts; A physical approval binding that covers recipient, payload hash, and expiry

### "“Before I share this, let me say exactly what to remove—names, prices, or the whole quoted section—and show me the final version on my Mac before I approve it.”"
- **useful because:** Pattern redaction is not enough for ordinary private material: a client name, negotiation number, or quoted paragraph may be harmless in one context and damaging in another. The owner should be able to author a semantic redaction over a specific source, inspect the exact resulting artifact locally, and approve that artifact—not trust a model’s claim that it removed the right thing.
- **path:** pendant → mac-planner → browser-extension → relay → dashboard-ux
- **model tier:** Use deterministic source-span selection and diffing for the actual redaction. A low-cost model may suggest candidate spans, but it cannot apply them without owner approval; the realtime model only handles the owner’s short spoken editing commands.
- **latency:** Candidate preview in 2 seconds for a page or document under the local size cap; physical approval remains an explicit pause. Re-render after each edit in under 500 ms.
- **cost:** Near-zero model cost for deterministic edits; occasional span suggestions under $0.005. Local rendering and browser interaction dominate.
- **security:** Never send the unredacted source to the relay solely to redact it. Keep source and final artifact local until approval; bind approval to a content hash, destination, recipient, and expiry. Show removed spans and an extraction-resistant plain-text preview, and fail closed if a source changes after preview.
- **missing:** A local redaction editor with semantic spans and a stable artifact hash; A browser/Mac preview surface that renders the exact outbound bytes; An approval envelope that binds redaction version, destination, recipient, and expiry; Outbound adapters that accept the approved artifact rather than re-reading the source


## Changes it proposed to its own stack

### `hardware` — Add a normally-open, physically actuated microphone power gate between the SPH0645 microphone and the nRF9160 input, with a two-position tactile slider or latching push switch and a GPIO sense line. Firmware must refuse capture unless the gate reports enabled; the relay and Mac may observe the state but may never override it. Keep the existing software privacy latch as a second, independent stop.
- **owner gets:** The owner gets a privacy control whose truth does not depend on firmware, a live session, LTE, USB, or a model. They can feel and see that the microphone is physically disconnected before entering a sensitive place, and a compromised or stale command cannot silently reactivate it.
- effort: High: board rework or a small inline daughterboard, enclosure change, GPIO/ADC sensing, boot and brownout handling, and measured audio-noise validation. Prototype is feasible on the currently USB-attached pendant before a PCB revision.  ·  risk: A failed-open switch could disable speech; a failed sense line must fail closed in firmware. EMI, contact bounce, and added capacitance may affect the I2S mic signal. Recovery is manual switch inspection plus a diagnostic report; no remote command should bypass the gate.
- cost: Prototype roughly $5–$20 in switch, tiny analog gate, wiring, and enclosure work; negligible steady-state power, with a few microamps at most for state sensing.  ·  latency: No meaningful capture latency; add only a short debounce before reporting a changed state.
- security: Substantially improves the physical privacy boundary by making remote capture impossible while disabled. The state itself should be treated as sensitive operational metadata and signed in device diagnostics.
- depends on: Confirm SPH0645 electrical interface and available inline access on the live pendant; Define a fail-closed boot policy for an unknown or broken gate-sense signal; Update the existing local privacy latch to report hardware-gate state rather than implying software mute is physical


## What it asked for

_Nothing._
## Its own summary

Three owner-facing capabilities were recorded: (1) delivery-verifiable briefings that resume only from authenticated pendant download/playback ACKs, (2) a physically marked departure/return handoff packet that diffs Mac/browser state without retaining page content, and (3) a mandatory final spoken-content firewall covering every audio path, not just briefingTriage. The first is the single most useful: it makes “delivered” mean the owner actually received it. The immediate implementation gaps are the USB serial adapter for the currently tethered pendant, durable artifact↔briefing-item joins, a marker-kind extension to the existing offline bookmark, and a policy-backed final audio hook.

**Biggest unknown:** USB-tethered local voice feasibility remains unanswered: specifically which existing Mac/relay process can ingest nRF9160 and ESP32 serial events, authenticate them, and route them into the new delivery and marker flows. Owner disclosure and interruption preferences also remain intentionally unset; the proposed policies must stay conservative, editable, and provenance-visible rather than guessed.

