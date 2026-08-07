# Harness derivation — unified — round 35

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Pause this task and let me resume it later—even if I leave, the Mac sleeps, or the browser page changes."
- **useful because:** Long tasks become safe and recoverable instead of restarting from memory or silently acting on stale pages. The pendant provides an immediate park/resume control, while the relay, Mac, and browser preserve enough evidence to continue exactly where they stopped.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background model for checkpoint summarization and reconstruction; realtime only for the short park/resume voice interaction; deterministic validators for freshness and irreversible-step gates.
- **latency:** Park acknowledgement under 1 second; checkpoint persistence under 5 seconds; resume briefing under 10 seconds, with longer work continuing asynchronously.
- **cost:** About $0.01–$0.08 per checkpoint/resume depending on screenshot/OCR and model use; most checkpoints should be deterministic JSON and cost near zero. Storage and browser/Mac polling dominate operational cost.
- **security:** Checkpoint may contain private URLs, page text, file paths, and screenshots. Encrypt relay storage, minimize/redact sensitive fields, bind browser state to tab/session IDs, expire capsules, and never replay a send/delete/purchase step without fresh owner confirmation. Stale or changed preconditions must force a review rather than guessing.
- **missing:** Durable task-capsule schema with versioned checkpoints and leases; Mac capture/restore adapter for active app, document, selection, and reversible UI state; Browser checkpoint adapter recording tab/session provenance and page fingerprints; Relay lease expiry, wake/retry, and resume orchestration; Pendant park/resume gesture and local acknowledgement; Freshness/precondition validator and dashboard showing checkpoint evidence; End-to-end crash, sleep, network-drop, and stale-page tests

### "Before you do that, rehearse the whole change and tell me what it would affect—without touching the real account, files, or messages."
- **useful because:** The owner can safely ask “what if?” about a genuinely multi-surface task instead of trusting a textual plan. A private browser session, Mac files/UI, and the relay each contribute state; the system builds a disposable shadow run, detects conflicts and hidden side effects, and returns an evidence-backed impact report before any real action.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic snapshot/diff and policy checks first; use a cheaper background model to explain the resulting impact graph. Reserve realtime for the spoken request and concise result.
- **latency:** A small rehearsal should return in 15 seconds; larger workflows continue in the background and leave a completion receipt and audio summary.
- **cost:** Roughly $0.02–$0.15 per rehearsal, dominated by screenshots/DOM extraction and model explanation; deterministic diffs and shadow filesystem operations are otherwise low cost. Temporary snapshots require bounded encrypted storage.
- **security:** Shadow state can contain authenticated page data, file contents, and message drafts. Keep it encrypted and short-lived, never transmit raw secrets to the model, label every simulated versus live value, and make execution a separate explicit approval with a fresh re-check. Sites that cannot be safely shadowed must be reported as “not simulated,” never guessed.
- **missing:** Cross-surface disposable snapshot format for Mac and authenticated browser state; Shadow filesystem/app runner and browser emulation or transaction interception layer; Side-effect classification and simulation adapters for mail, calendar, purchases, and file operations; Evidence graph and dashboard diff viewer that clearly separates simulated from live state; Fresh-state revalidation and approval handoff from rehearsal to execution; Retention, redaction, and secure deletion policy for rehearsal artifacts


## Changes it proposed to its own stack

### `hardware` — Design the production pendant as a transport-agnostic audio endpoint with a BLE 5.x companion path to the owner’s phone, while retaining LTE-M for standalone operation. Add a small local jitter/record buffer and a transport manager: use phone Wi‑Fi/5G when paired and healthy, fall back to LTE-M when not, and expose the active path to the relay. The relay should preserve one call/session identity across transport handoff so Mac/browser work and voice context do not reset.
- **owner gets:** Speech remains intelligible in the real places LTE-M struggles—indoors, congested cells, or while the agent is speaking—without requiring the owner to restart a conversation or carry a separate hotspot. Standalone LTE still works when the phone is absent.
- effort: High: new production PCB/radio validation, iOS/Android companion, BLE audio/data protocol, relay session migration, and RF/battery testing. Prototype first with an nRF9160 + phone app and packet-loss fault injection.  ·  risk: BLE pairing failures or handoff races could interrupt calls; recover by keeping LTE as authoritative fallback, making handoff at frame boundaries, and retaining a short local replay buffer. Phone metadata and audio transit through the companion app; require explicit pairing, OS-level permissions, encrypted BLE, and clear active-transport indication.
- cost: Prototype app/protocol engineering is substantial; production BOM roughly +$3–$8 for BLE-capable companion MCU/antenna changes if not integrated in the main SoC, plus phone app maintenance. Runtime phone path can reduce LTE airtime; local buffering costs tens of KB of RAM/flash.  ·  latency: BLE-to-phone adds roughly 10–40 ms; Wi‑Fi/5G should reduce cloud RTT versus LTE-M. Handoff target under 500 ms with no audible gap.
- security: Adds a paired-phone trust boundary and another endpoint holding transient audio/session identifiers. Use mutually authenticated rotating keys, no long-lived secrets in the pendant, encrypted relay tokens, and wipe buffers after delivery.
- depends on: 24 kHz end-to-end audio acceptance criteria; link-aware duplex congestion governor; transport handoff/session migration protocol; companion mobile surface and permission UX; audio link fault-injection test harness


## What it asked for

### `c7-c4ui` (context) — owner's acceptable phone-companion behavior and privacy boundary
- why: I proposed a BLE phone fallback to solve measured LTE-M duplex loss, but need to know whether the owner would accept a paired phone as a transport and whether calls may traverse it.
- would change: If phone transport is acceptable, prioritize seamless handoff and companion UX; if not, keep the proposal LTE-only and focus on modem/RF or codec changes without introducing a new endpoint.

## Its own summary

I found no existing explicit resumable task capsule—only the generic “keep working after I leave” capability—so I recorded a concrete cross-node capability: pendant park/resume, relay leases and checkpoints, Mac UI/file state, browser tab/session provenance, and freshness gates before resuming. I also recorded a hardware change for the measured LTE-M duplex loss: BLE phone transport fallback with seamless relay session migration, while retaining standalone LTE-M. I still need the owner’s privacy/acceptance decision on a paired-phone transport, plus implementation dependencies: durable capsule schema/lease runner, Mac and browser checkpoint adapters, freshness validators, pendant gesture, and audio transport-handoff testing.

**Biggest unknown:** Whether the owner permits a paired phone to carry live audio/session traffic; that determines whether the most effective fix for the measured LTE-M packet loss is a new transport path or an LTE-only redesign.

