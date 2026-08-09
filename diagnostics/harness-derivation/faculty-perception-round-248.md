# Harness derivation — faculty-perception — round 248

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live device registry and Mac permissions** — At 2026-08-09T03:31Z, the Mac agent reports Accessibility and Screen Recording granted, requiredMissing=[] and ready=true; Safari browser extension is online on YouTube tab 85. Device discovery currently lists nrf9160-pendant as registered but offline, last seen 2026-08-09T02:56:31.366Z; this is registry evidence, not current connectivity.
  - evidence: read_continuity_snapshot include relay/pipeline resolved GET /ops/snapshot HTTP 200; discover devices returned nrf9160-pendant offline and the Mac status payload reported permissions.ready=true.

## Capabilities it proposed

### "“Did that request really change the thing I named, or did the system only report success?”"
- **useful because:** This would be the system's most valuable trust boundary: a single answer tied to one operation that compares the captured before-state with an independently re-read after-state, distinguishes changed/unchanged/unknown, and names the exact evidence. It prevents a completed Mac job, browser receipt, or relay delivery flag from being mistaken for an owner-visible result.
- **path:** pendant → relay → mac-planner → browser-extension → ios-control
- **model tier:** Background model for evidence correlation; realtime only to phrase the final answer.
- **latency:** 1–3 seconds after an operation, with a 10-second retry window for stale browser or iPhone reads.
- **cost:** Roughly $0.01–$0.04 per verification; dominated by one or two Mac/browser observations, not model tokens.
- **security:** Before/after values may contain private page, message, or app content. Redact secrets and retain only hashes, field locators, and bounded excerpts; require explicit confirmation before reading sensitive fields or declaring a destructive change.
- **missing:** An operation-bound verifier that accepts operation_id+attempt_id and runs a postcondition read across the owning surface.; Every mutating action must publish a stable operation_id and a pre-state capture; current receipts are not consistently joinable to independent verification.; Explicit unknown outcomes for locked screens, stale tabs, inaccessible iPhone mirroring, and app-side asynchronous saves.

### "“Why didn't I hear that, and what was the first thing that failed?”"
- **useful because:** Instead of a misleading completed/failed label, the owner gets a causal boundary: no pendant link, relay never accepted audio, socket dropped, device received but capture/playback degraded, or Mac/browser was stale. It can recommend a repeat only when the evidence says repeating is useful, and it preserves the distinction between absent evidence and a proven failure.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Cheap background classifier over compact telemetry; realtime is used only if the owner asks during a live conversation.
- **latency:** Under 2 seconds for a recent item; up to 15 seconds to reconcile delayed reconnect telemetry.
- **cost:** About $0.005–$0.02 per incident; telemetry collection dominates, with a small classification prompt.
- **security:** Audio content must not leave the device for diagnosis. Send only sequence numbers, packet-loss counters, relay byte counts, interruption reason, and bounded timestamps. Never infer hearing from socket writes; show unknown when device playback telemetry is absent.
- **missing:** A relay-to-device causal event chain keyed by artifact_id and monotonic sequence, including socket interruption and reconnect epochs.; Firmware emission and relay ingestion of the already-accepted playback lifecycle events, plus offline-reality-beacon and offline-capture-integrity-sentinel frames in the same schema.; A bounded incident correlator that chooses the earliest proven failure and exposes competing hypotheses rather than inventing one.

### "“Before you use that remembered preference, is it actually mine, current, and consistent with the machine?”"
- **useful because:** The system currently injects high-confidence machine-written facts into the owner's context as if they were preferences. This capability would expose provenance, contradiction, age, and authority before a routine, reminder, or answer relies on a fact—preventing silent errors such as a stale machine timezone controlling a scheduled action.
- **path:** relay → mac-planner → pendant
- **model tier:** Cheap background audit when a fact is read or changed; realtime only for the short explanation to the owner.
- **latency:** Normally under 300 ms from the local fact store; a cross-surface consistency check may take 1–2 seconds.
- **cost:** Under $0.005 per fact check; local reads dominate and model use is optional.
- **security:** Do not expose private memory contents in relay logs. Return provenance class, confidence, timestamps, and a redacted conflict summary; changing or deleting a fact requires explicit owner confirmation.
- **missing:** A read-only authority evaluator that treats source.origin separately from kind and confidence, and returns owner/machine/inferred/unknown.; Conflict checks against authoritative local observations such as /etc/localtime and live device/browser state, with a durable suspect marker rather than silently rewriting memory.; A projection rule that prevents suspect machine facts from entering the cacheable Owner context head until reviewed.

### "“Before you act, can you prove this is the right account, device, and session—not merely a page that looks right?”"
- **useful because:** The owner currently has no dependable identity fence across Safari, iPhone Mirroring, Mac apps, and the relay. A logged-in page, a stale tab, or a second account can look valid while an action lands in the wrong place. This capability would pause with a concrete identity report—or refuse as unknown—before sending, purchasing, publishing, or changing data.
- **path:** pendant → relay → mac-planner → browser-extension → ios-control
- **model tier:** Background perception model for extracting and comparing identity signals; realtime only for the owner's confirmation prompt.
- **latency:** 1–2 seconds for a normal preflight; up to 8 seconds when the iPhone mirror or browser must refresh.
- **cost:** About $0.01–$0.05 per preflight, dominated by screenshots/page reads and optional OCR or vision; no continuous model spend.
- **security:** Account names, email addresses, and page contents are sensitive. Keep raw screenshots local, transmit only redacted identity claims and salted hashes, and require confirmation whenever evidence is partial, conflicting, or derived from a visual guess.
- **missing:** A cross-surface identity evidence contract with issuer, account pseudonym, session/tab ID, observedAt, and confidence—not just URL/title.; Browser and iPhone adapters that expose the currently selected account and authentication freshness without revealing credentials.; A relay-side policy gate that treats conflicting or stale identity as unknown and blocks consequential actions rather than letting the planner guess.

### "“After you handled that, show me exactly what private data left each device, who received it, and how long it will remain.”"
- **useful because:** Today the owner cannot obtain a trustworthy privacy receipt for a voice turn or computer action. Relay reads, browser content, Mac screenshots, and audio can cross trust boundaries without one joined account of what was disclosed. A bounded receipt would make the hive auditable and let the owner revoke or shorten retention instead of relying on undocumented behavior.
- **path:** pendant → relay → mac-planner → browser-extension → ios-control
- **model tier:** Cheap deterministic ledger construction; use a background model only to summarize the receipt in plain language.
- **latency:** Receipt available within 1 second after each operation, with late-arriving device and relay events appended for 60 seconds.
- **cost:** Under $0.01 per operation; storage and hashing dominate, not inference.
- **security:** The receipt itself must not reproduce secrets. Store data classes, byte/character counts, destination, purpose, retention deadline, and content hashes; protect it with the same owner authorization as the underlying data. Deletion claims must be explicit about stores outside the system's control.
- **missing:** A cross-surface disclosure event schema with operation and artifact IDs, redaction class, destination, retention policy, and deletion status.; Instrumentation in relay voice/browser paths, Mac screenshots/actions, browser extension results, and pendant audio queues.; Owner-facing retention and revocation controls that distinguish local deletion, relay deletion, and third-party service retention.


## Changes it proposed to its own stack

### `relay` — Change device presence semantics from a single online boolean to explicit states: live (<90s heartbeat), stale-registered (seen before but no heartbeat), never-seen, and unobservable. Include observedAt, source (device heartbeat vs Mac-authored registry), registry age, and an evidence note in /v1/devices/status and the continuity snapshot. Never label nrf9160-pendant simply offline when its converse path does not heartbeat.
- **owner gets:** The owner can immediately tell “the pendant is disconnected now,” “this device was only paired months ago,” and “we have no device evidence,” instead of treating a stale row as a current outage or believing a Mac bridge heartbeat proves a pendant is alive.
- effort: Small-to-medium: relay schema/normalizer, status consumers, and dashboard copy; add tests around stale and restart-erased memory stores.  ·  risk: Existing clients may assume boolean online and misclassify new states. Preserve online for compatibility, add presenceState and migrate consumers; recover by reverting the presentation layer without changing records.
- cost: Negligible storage and compute; no model cost.  ·  latency: None for reads; status computation is local.
- security: Avoid exposing device identifiers beyond existing authenticated scope; source labels reduce false trust but do not add access.
- depends on: Pendant heartbeat or offline-reality-beacon frames when hardware is actually connected; Relay registry persistence in D1 for durable last-seen history; A consumer that renders unknown/stale distinctly


## What it asked for

_Nothing._
## Its own summary

Discovered and recorded a changed live state: the Mac agent now has Accessibility and Screen Recording, with permissions.ready=true; Safari's bridge is online on a YouTube tab; the relay registry contains nrf9160-pendant but only as stale/offline last-seen evidence. I proposed (1) operation-bound before/after verification, (2) causal audio-delivery failure diagnosis, (3) provenance/authority checking for remembered facts, and (4) relay presence states that distinguish live, stale-registered, never-seen, and unknown. I also notified faculty-action of the permission and registry change.

**Biggest unknown:** Whether the nrf9160 device is physically connected and capable of sending the newly accepted beacon/playback telemetry. Registry presence is not current connectivity; a direct pendant heartbeat or USB bench observation is still missing.

