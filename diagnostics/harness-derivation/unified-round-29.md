# Harness derivation — unified — round 29

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I got interrupted—what did I miss, and what should I do next?”"
- **useful because:** The pendant can capture the exact interruption boundary, while the Mac and authenticated browser recover the surrounding calendar, messages, documents, and task state. The owner gets a short, evidence-linked resumption brief instead of manually reconstructing context.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the realtime model only to recognize the spoken request and interruption marker; use a cheaper background model to correlate the time window, summarize evidence, and rank next actions.
- **latency:** Acknowledge on the pendant within 500 ms; deliver a first spoken answer within 10 seconds and finish deeper browser evidence within 60 seconds. If browser is offline, return the local transcript/time boundary and retry enrichment later.
- **cost:** Roughly $0.01–$0.05 per invocation, dominated by authenticated page extraction and summarization; most requests should use the cheaper background tier.
- **security:** The time window may expose private mail, calendar, and browser content, so only the owner's already-authorized sessions are queried. Return source links/snippets and avoid sending, editing, or submitting anything. Require confirmation before creating follow-up tasks or contacting anyone; allow per-source opt-out and automatic deletion of the temporary transcript bundle.
- **missing:** A first-class pendant interruption marker carrying monotonic time plus wall-clock estimate into the relay; A cross-surface correlation job that joins the marker to Mac audio/transcript, calendar, authenticated browser tabs, and existing job receipts; A cited resumption-brief object with retry state when the Mac or browser is offline; A dashboard/pendant delivery path for the brief and a user-configurable private-source allowlist

### "“That answer was wrong—show me exactly why, fix the memory, and don’t make the same mistake again.”"
- **useful because:** Today the owner cannot challenge a spoken answer and have the system trace it across the relay, Mac, browser evidence, and stored context. This capability turns errors into auditable corrections: identify the claim, retrieve the originating sources and transformations, let the owner select the truth, and prevent stale or contradicted facts from resurfacing.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use realtime only for the short spoken acknowledgement and clarification. Use a cheaper background model for source retrieval, contradiction analysis, provenance assembly, and memory repair.
- **latency:** Acknowledge within 500 ms; provide the claim and preliminary source trail within 5 seconds; complete cross-surface verification and present the proposed correction within 30 seconds. If a private surface is unavailable, explicitly mark the correction incomplete and retry later.
- **cost:** Approximately $0.02–$0.08 per correction, dominated by authenticated source retrieval and provenance summarization; routine acknowledgements remain inexpensive realtime turns.
- **security:** The trace may contain private mail, calendar, browser pages, and voice transcript fragments. Query only already-authorized surfaces, redact secrets from spoken output, retain source hashes and minimal snippets by default, and require explicit confirmation before changing durable memory. Never silently rewrite facts or erase the original claim.
- **missing:** A claim-level provenance graph linking spoken responses to relay prompts, model outputs, Mac actions, browser extracts, and stored facts; A contradiction/correction workflow with owner confirmation and immutable before/after memory history; Cross-surface retrieval that can re-open the exact authenticated browser evidence or local artifact used for a claim; A dashboard and pendant receipt showing what was corrected, why, and which future responses it will affect


## Changes it proposed to its own stack

### `hardware` — Move the wearable audio design from the nRF9160 DK prototype to a production board with a native 24 kHz (or 48 kHz decimated) digital microphone path, a dedicated low-power audio/DSP core or Opus offload, and a full-duplex-capable LTE/BLE companion. Keep the ESP32 bridge only as a development fixture. Add a hardware clock/format negotiation line so the relay can select 24 kHz playback without the current 31,250 Hz I2S workaround.
- **owner gets:** The owner gets intelligible, natural-sounding speech and fewer dropped/robotic responses while wearing the device, rather than a prototype whose 15,625 Hz capture and ~87%-of-one-core encode/decode load leave little headroom for reliable conversation.
- effort: High: audio schematic and board spin, codec/driver port, RF/power validation, acoustic enclosure tuning, and an end-to-end acceptance test across LTE-M. Prototype on an evaluation board first, then a 2–3 revision wearable PCB.  ·  risk: Higher power draw, RF/audio coexistence issues, and codec timing regressions could shorten battery life or make calls less stable. Recover by retaining the current DK/ESP32 profile as a negotiated low-bandwidth fallback and gating rollout behind measured packet-loss, latency, and battery tests.
- cost: Approximately $25–$80 in prototype components/board per unit and several engineering weeks; production BOM increase roughly $8–$25 depending on audio DSP/codec and companion radio. API cost is unchanged; lower retransmits may reduce relay bandwidth cost.  ·  latency: Potentially 5–20 ms lower audio buffering if native clocks remove resampling, but initial firmware may add negotiation delay. Fallback mode preserves today's behavior.
- security: No new cloud data is required. Firmware and codec images need signed OTA updates; clock negotiation must be bounds-checked so malformed packets cannot exhaust DSP or radio resources.
- depends on: Define and test the 24 kHz superwideband acceptance criteria; Implement a negotiated audio profile in pendant firmware, relay transcoding, and playback; Measure battery and RF coexistence on the selected production radio/audio combination

### `integration` — Make a single authoritative preflight/readiness contract for unified actions. Before planning or claiming completion, the relay queries Mac and browser health, verifies the specific permission/device needed, and labels each requested step ready, queued, blocked, or completed. Reconcile the current contradictory state (requiredMissing=[] but ready=false), automatically cancel or retry stale browser commands when the extension is offline, and include a machine-readable reason plus a spoken one-sentence explanation.
- **owner gets:** Requests such as “read Gmail” or “browser page access” would stop failing opaquely: the owner would immediately hear whether the browser is offline, Accessibility/Screen Recording is missing, or work is queued—and would never be told something succeeded when it did not.
- effort: Medium: define the readiness schema, implement relay preflight and Mac/browser adapters, add stale-command reconciliation, and update voice receipts/dashboard tests.  ·  risk: A strict gate could delay harmless actions or misclassify transient outages. Recover with per-action capability requirements, short health-check TTLs, explicit retry/backoff, and a user-visible “try anyway” path only for reversible reads.
- cost: Negligible API cost (small status requests); saves expensive model turns and repeated failed browser/Mac attempts. Engineering cost is several days plus integration tests.  ·  latency: Adds roughly 100–500 ms when surfaces are online; avoids long opaque timeouts when they are not.
- security: Improves security by preventing actions from being routed through an unintended surface and by making permission state explicit. Do not expose tokens or private URLs in spoken errors; keep detailed diagnostics in the local dashboard.
- depends on: A typed cross-surface context/readiness projection rather than hand-written fleetContext sections; Request IDs and idempotency for browser commands; A durable receipt model that distinguishes accepted, executing, completed, failed, and blocked

### `memory` — Add an append-only claim provenance ledger and correction protocol. Every spoken factual assertion receives a claim ID, source references, retrieval timestamps, transformation/model version, confidence, and expiry. A correction creates a superseding record rather than overwriting history; future context projections exclude superseded claims and expose uncertainty when sources conflict.
- **owner gets:** When the system gets something wrong, the owner can repair one fact confidently and know that the correction will propagate to the pendant, relay, Mac, and browser workflows instead of repeatedly hearing the same error.
- effort: High: instrument realtime responses, planners, browser extraction, Mac receipts, and context projection; build conflict resolution, confirmation UI, migration for existing facts, and end-to-end tests.  ·  risk: More metadata may increase storage and context size, and an incorrect correction could poison future behavior. Mitigate with compact hashes, TTLs, source revalidation, explicit confirmation, reversible supersession, and a visible correction history.
- cost: Moderate storage/engineering cost; small per-response token overhead if only claim IDs and compact provenance are projected. Background verification should use a cheaper model.  ·  latency: Negligible for ordinary answers if ledger writes are asynchronous; 1–5 seconds for an owner-requested verification depending on browser/Mac access.
- security: Provenance can reveal sensitive source locations, so encrypt local records, minimize spoken details, apply source sensitivity labels, and restrict detailed traces to the owner’s authenticated dashboard.
- depends on: A typed context projection with provenance, confidence, and expiry; Stable request/job/action IDs across relay, Mac, and browser; Owner-confirmed memory mutation and durable before/after receipts


## What it asked for

_Nothing._
