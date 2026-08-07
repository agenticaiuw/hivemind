# Harness derivation — unified — round 100

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I come back to the pendant, tell me in one short sentence what changed or finished across my Mac and logged-in browser since I last left, with a way to resume anything unfinished."
- **useful because:** Today work is split across a wearable conversation, Mac jobs, and private browser tabs; the owner should not have to remember which surface held the unfinished thread. A compact return briefing turns elapsed time into continuity without replaying stale detail.
- **path:** pendant → relay → mac-bridge → browser → dashboard-ux
- **model tier:** Background/scheduled reconciliation uses a cheaper model; realtime is used only to compress the already-collected delta into the owner's one-sentence spoken return.
- **latency:** Capture a departure checkpoint in under 1 second; reconcile on job completion or reconnect in under 10 seconds; speak within 2 seconds of the next pendant session.
- **cost:** Low: mostly event/state diffs and one short realtime utterance; roughly $0.002–$0.02 per return depending on how many completed jobs and browser changes need summarization. Storage is small JSON checkpoints.
- **security:** Only authenticated Mac and browser metadata plus cited result snippets leave those surfaces; never include page contents unless needed for the requested resume. Private-page deltas need session ownership and expiry. Sending mail, submitting forms, deleting, or purchasing still requires confirmation.
- **missing:** A durable cross-surface departure checkpoint schema keyed to the pendant session; Mac and browser event emission for completed/failed/paused work and meaningful page deltas; A reconnect hook that asks the relay for the delta and exposes resumable job IDs; An explicit owner setting for what counts as a meaningful change and quiet hours

### "For the next hour, let you handle routine, reversible errands across my Mac and logged-in browser without interrupting me, but pause and ask before anything that sends, buys, deletes, or commits me."
- **useful because:** The owner currently has to choose between constant prompts and broad, persistent trust. A spoken, time-limited delegation would let the pendant, relay, Mac, and browser cooperate during a real busy period while guaranteeing that high-consequence actions still stop for approval.
- **path:** pendant → relay → mac-bridge → browser → dashboard-ux
- **model tier:** Use a cheap policy evaluator for every action; reserve realtime only for the owner's delegation command and any approval prompt. The model proposes actions, but a deterministic policy engine enforces the scope, expiry, and forbidden verbs.
- **latency:** Acknowledge delegation in under 1 second; policy decisions under 100 ms locally on the Mac/relay; approval prompts should reach the pendant within 2 seconds of a blocked action.
- **cost:** Low ongoing cost: mostly signed policy checks and ordinary task inference, about $0.001–$0.02 per delegated task. One short realtime turn is needed to establish or amend the delegation.
- **security:** Delegation must be represented as a signed, narrowly scoped capability token bound to owner, surfaces, allowed action classes, and an absolute expiry; never infer permission from conversational tone. Browser sessions and Mac jobs must re-check the token at execution time. Sending mail, purchases, deletion, credential changes, external messages, and irreversible submissions must be hard-denied until explicit confirmation. Dashboard must show active delegations and revoke them immediately.
- **missing:** A cross-surface capability-token and policy-enforcement service, checked at both planning and execution; A small canonical action taxonomy distinguishing read, reversible write, and irreversible commitment; Pendant and dashboard controls to show, revoke, and confirm the active delegation; A tamper-evident audit record proving which delegation authorized each action


## Changes it proposed to its own stack

### `hardware` — Replace the prototype's 15,625 Hz I2S microphone plus ESP32 bridge arrangement with a product audio front end that natively captures 24 kHz (or 32 kHz downsampled to 24 kHz), provides clocked full-duplex I2S, and has enough DSP/headroom for simultaneous Opus encode/decode. Keep the single-button/LED UX, but reserve the currently free SPI/I2C buses for codec control and health telemetry.
- **owner gets:** The owner gets genuinely intelligible superwideband speech rather than a 24 kHz playback label fed by narrow capture, with fewer dropouts and less latency during two-way conversation.
- effort: High: select a low-power digital microphone and codec/bridge, redesign clocking and PCB, update Zephyr audio drivers and the relay's format negotiation, then validate RF, battery, and acoustic performance in an enclosure.  ·  risk: Clock-domain or driver regressions could produce silence, drift, or doubled audio. Recover with a board-revision feature flag and retain the current 16 kHz compatibility mode until end-to-end acceptance passes; field-upgrade firmware must be able to fall back per device.
- cost: Prototype engineering plus roughly $8–$25 BOM increase depending on codec and bridge; a few to tens of mW additional audio power. API cost is unchanged, though 24 kHz Opus may modestly increase uplink bytes.  ·  latency: Potentially lower perceived latency by removing bridge resampling and reducing CPU contention; budget 1–3 ms codec/clock overhead, subject to measurement.
- security: No new data class; audio remains encrypted in transit. Codec health telemetry should exclude raw audio and use coarse counters only.
- depends on: Define and run the pending 24 kHz end-to-end audio acceptance criteria; Measure current Opus CPU/RAM and packet-loss behavior under simultaneous encode/decode; Choose a production pendant SoC/codec instead of treating the nRF9160 DK as the product

### `integration` — Introduce a signed, expiring delegation token propagated from relay to Mac and browser job execution. Every planned and executable action must resolve to a canonical risk class and revalidate the token immediately before side effects; receipts must record token ID, scope, expiry, and confirmation provenance. Add a pendant long-press and dashboard revoke path that invalidates the token server-side and causes queued jobs to stop before their next side effect.
- **owner gets:** The owner can safely say “handle routine things for the next hour” and get uninterrupted help without granting the system permanent authority or wondering afterward why an action was allowed.
- effort: Medium-high: define the action taxonomy, token format and revocation store, add enforcement middleware to relay/Mac/browser executors, and test expiry, replay, queue races, reconnects, and clock skew.  ·  risk: A classification bug could let a consequential action through, or an overly strict class could interrupt harmless work. Default-deny unknown actions, require server time rather than device clocks, and retain the existing receipt/undo path for reversible actions. Roll out read-only and simulated enforcement first.
- cost: Negligible storage and compute; one small signed token and an audit row per job. No meaningful model-cost increase.  ·  latency: Usually under 100 ms for policy lookup/signature validation; revocation checks add one bounded local/relay read before side effects.
- security: Improves least privilege and auditability, but creates a sensitive revocation/token service. Bind tokens to the owner account and intended surface, rotate signing keys, expire aggressively, and never place secrets in pendant speech transcripts.
- depends on: Canonical action-risk taxonomy shared by plan and execute; Execution middleware in both Mac and browser bridges; Server-side revocation and durable audit storage; Owner-visible delegation status and revoke controls


## What it asked for

_Nothing._
## Its own summary

Discovered the live fleet and owner state. Recorded a new cross-surface capability: when the owner returns to the pendant, reconcile Mac jobs and authenticated-browser changes since departure into one cited, resumable sentence. Also recorded a product-hardware change for real 24 kHz capture/full-duplex audio, because the prototype currently captures at 15,625 Hz and simultaneous Opus encode/decode consumes about 87% of a core. The existing relay, job, browser-inspection, session, briefing, and pipeline routes are usable building blocks, but the connective checkpoint/event layer is missing.

**Biggest unknown:** The critical unresolved product decisions are still the authoritative timezone (owner memory says America/Chicago while the Mac reports America/New_York), the end-to-end 24 kHz audio acceptance thresholds/product audio target, and production pendant constraints. For the new return-brief capability, we still need a durable departure-checkpoint schema, Mac/browser completion-and-change events, reconnect/resume semantics, and the owner's definition of a meaningful change/quiet hours. The orchestrator's granted list is currently empty, so previously requested audio and device skills are not visibly available to this agent yet.

