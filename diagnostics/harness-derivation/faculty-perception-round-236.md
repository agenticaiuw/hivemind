# Harness derivation — faculty-perception — round 236

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac perception permissions and bridge state** — At 2026-08-09T01:48Z, the authenticated Mac snapshot reports Accessibility and Screen Recording granted for com.aipendant.agent, all listed automation grants present, permissions.ready=true, browser extension online with 2 Safari tabs and 0 pending commands, and relay reachable with mac bridge online. This supersedes the earlier denied-permission state; it does not establish a pendant is connected.
  - evidence: read_continuity_snapshot(include=['relay','pipeline']) resolved to GET /ops/snapshot, HTTP 200; body status.permissions and status.browser/relay payload.

## Capabilities it proposed

### "“Did my morning brief actually reach me, and if not, where did it stop?”"
- **useful because:** The current system can report that a routine or Mac job completed, but that is not a causal delivery chain and is not evidence the owner heard anything. This answer would join the scheduled trigger, run, generated artifact, relay announcement, Mac/browser state, and (when a pendant exists) device playback into one honest verdict: delivered-to-socket, played, interrupted, missing, or unknown. It would save the owner from trusting a green ‘completed’ badge that may only mean the Mac ran.
- **path:** relay → mac → browser → pendant
- **model tier:** background for scheduled reconciliation; realtime only when the owner asks the question
- **latency:** Under 3 seconds from cached event indexes; up to 10 seconds only when a fresh Mac/browser probe is needed.
- **cost:** Low: one short judgement call over compact event records; the dominant cost is no model call for routine polling, with realtime tokens only for an interactive explanation.
- **security:** Expose only the owner’s own routine/job metadata and bounded artifact summaries. Never infer hearing from relay bytes. Pendant playback evidence must be device-originated, and any browser content must retain its existing untrusted/provenance labels. Require confirmation before replaying or re-running a missed brief.
- **missing:** A routine-level causal join record linking routine run -> job -> artifact -> announcement/audio -> playback event.; The already-accepted device playback acknowledgement (audio_delivery_ack_queue) must be emitted by a registered pendant; no pendant is currently registered.; A relay/Mac reader that maps the existing job, receipt, pipeline, and announcement records into explicit stop reasons rather than relying on Mac-side completion.

### "“Tell me when something you remember about me conflicts with what is true on this Mac.”"
- **useful because:** A machine-derived fact can be pinned as a high-confidence owner preference and injected into every prompt even when it is stale or wrong; the live snapshot now proves the Mac’s actual timezone/permission/browser state independently. This capability would surface contradictions before they cause a wrong schedule, privacy decision, or action, while preserving owner-authored facts as distinct from machine observations.
- **path:** mac → relay → browser
- **model tier:** background rule engine first, with a cheap model only to explain a detected conflict in one spoken sentence
- **latency:** Continuous checks at startup and before any action; under 500 ms for deterministic comparisons and under 2 seconds for an explanation.
- **cost:** Near-zero for comparisons over structured facts; occasional small text-model call for a concise explanation.
- **security:** Do not read secret fact values into the spoken alert; say which fact class conflicts and offer a private detail view. Never overwrite or delete owner memory automatically. Mark machine observations with source and capture time, and require confirmation for any correction.
- **missing:** A conflict detector that compares memory facts’ source.origin, confidence, expiry, and lastUsedAt against live machine-context and permission/browser observations.; A durable, dismissible contradiction record with first-seen/last-seen timestamps so the owner is not repeatedly interrupted.; A policy distinguishing owner-stated intent from machine-sampled observations; the current projection makes both look similarly authoritative.

### "“Before you act, what parts of your picture are live, stale, or simply unavailable?”"
- **useful because:** The owner currently has no compact way to know that Safari and the Mac bridge are live while the pendant is absent, or that historical pipeline audio is not current device telemetry. A trust fence shown before an action prevents the system from silently turning recorded history, a stale memory preference, or a missing device into asserted reality.
- **path:** pendant → relay → mac → browser
- **model tier:** Deterministic perception summary; use the realtime model only to phrase the result in the owner’s requested short spoken style.
- **latency:** Under 1 second from the continuity snapshot cache; refresh only sources whose freshness bound has expired.
- **cost:** Negligible model cost when cached; one small realtime response when spoken. Storage is a bounded ring of source observations and contradiction transitions.
- **security:** The fence must fail closed for unavailable sources and must not expose browser page text or secret memory values. Display source, observedAt, freshness bound, and uncertainty—not fabricated confidence. An action using an unknown source should require confirmation.
- **missing:** A user-facing trust matrix with per-source freshness bounds and explicit unavailable/unknown states.; A pendant branch that reports the offline-reality-beacon when a device eventually registers; today the correct pendant state is absent, not healthy.; A cache-aware reader that distinguishes live Mac/relay/browser observations from historical pipeline records and machine-sampled memory.

### "“I don’t trust that answer—freeze exactly what you believed, then investigate it independently and show me the competing timelines.”"
- **useful because:** Today a later observation can overwrite the practical narrative of an earlier turn, and the owner cannot ask the system to preserve the original claim, its evidence, freshness, and uncertainty as a disputable object. This would make mistakes recoverable: it would snapshot the claim, query independent surfaces, identify agreement versus contradiction, and leave an auditable resolution rather than silently revising history.
- **path:** relay → mac → browser → pendant
- **model tier:** Background deterministic evidence collection followed by a small reasoning model; realtime is only needed to explain the dispute conversationally.
- **latency:** Freeze the original claim immediately; return an initial dispute packet in 2 seconds and complete independent probes within 15 seconds.
- **cost:** Low to moderate: most work is structured event capture and hashing; one compact reasoning call compares the timelines.
- **security:** Evidence must be content-minimized and access-controlled. Browser and message contents should remain local unless explicitly included. Preserve original observations immutably, label later corrections as corrections, and require confirmation before any compensating action.
- **missing:** A first-class immutable claim record with source observations, timestamps, freshness, model turn, and the exact uncertainty expressed.; A dispute workflow that can request independent Mac, browser, relay, and device observations without letting one source rewrite another.; A resolution state machine: unresolved, corroborated, contradicted, superseded, or owner-dismissed, with an owner-visible explanation.

### "“For this answer, show me exactly what information crossed from my devices to the relay, what stayed local, and who could read it.”"
- **useful because:** The owner currently cannot audit data egress for a single voice turn or background routine. A browser read, Mac observation, relay job, and future pendant telemetry can cross different trust boundaries, yet the system does not provide a plain-language, per-turn accounting of payload classes, redactions, recipients, retention, or whether a result was only local. This is the most useful privacy answer the collective could provide while still doing work across all surfaces.
- **path:** pendant → relay → mac → browser
- **model tier:** Deterministic egress ledger first; a small background model summarizes it. Realtime only speaks the short answer when asked.
- **latency:** Create the ledger synchronously at each boundary; answer in under 2 seconds from cached structured records.
- **cost:** Low: byte counts, field classifications, hashes, recipients, and retention policies are structured metadata; minimal model tokens for explanation.
- **security:** The ledger itself must not duplicate secrets or page text. Store classifications, hashes, destinations, and byte counts rather than payloads. Make relay access and retention explicit, and require confirmation before exporting a locally captured secret or sensitive browser region.
- **missing:** A per-turn egress ledger spanning pendant capture, Mac processing, browser extraction, relay requests, model inputs, outputs, and durable stores.; A privacy classification/redaction decision at every boundary, including an explicit ‘not inspected’ state rather than assuming redaction.; A retention and recipient view that can distinguish local files, relay D1, browser extension state, and device NVS/SD, including deletion capability where it exists.

### "“Before you do anything consequential, require two independent witnesses to agree on the target and tell me which witnesses they were.”"
- **useful because:** A single stale browser tab, memory fact, relay record, or Mac observation can currently drive an action. This capability would let the owner set an evidence quorum—for example, the active Safari tab plus a fresh Mac accessibility observation, or a relay job plus a device beacon—while treating correlated copies of the same observation as one witness. It is materially safer than a generic confidence score and useful even when one surface is offline.
- **path:** mac → browser → relay → pendant
- **model tier:** Deterministic quorum and independence checks; use a small judgement model only when evidence is semantic rather than typed.
- **latency:** Under 1 second for typed targets; up to 5 seconds for fresh browser/Mac probes. If quorum cannot be reached, stop rather than silently downgrade.
- **cost:** Low for typed comparisons; occasional small model call to normalize names, dates, or page entities.
- **security:** Do not use the same relay-derived record twice as independent evidence. Never use private browser content as a witness without the owner’s existing browser permission. Quorum must gate destructive, financial, communication, and privacy-sensitive actions, and the owner must be able to override explicitly.
- **missing:** A provenance graph that identifies observation ancestry and prevents correlated records from counting as independent witnesses.; Owner-configurable quorum policies by action class, with an explicit unknown/offline outcome.; Planner/action enforcement that refuses execution when the configured quorum is unmet and records the reason in the receipt.


## Changes it proposed to its own stack

### `context` — Create a signed, bounded ‘observation frame’ at every action boundary. The Mac agent records source-specific observedAt/age, origin (owner, machine, relay, browser, device), freshness deadline, and contradiction IDs; the relay carries the frame hash into the job/receipt, while the browser bridge attaches its tab heartbeat and the pendant later attaches its beacon sequence. The planner must consume the frame and either cite the live observation or label the input unknown before acting.
- **owner gets:** When the system says ‘done’ or schedules something, the owner can see whether that conclusion came from a live Mac/browser observation, relay acceptance, old pipeline history, or no device at all. Newly granted Accessibility and Screen Recording make the Mac side observable now; this turns that access into honest answers rather than invisible extra control.
- effort: Medium-high: shared observation-frame schema, Mac capture middleware, relay propagation, browser heartbeat join, planner policy, and Ops UI/voice rendering.  ·  risk: Clock skew, stale frames, and partial propagation could falsely look authoritative. Recover by using monotonic age plus wall-clock timestamps, expiring frames aggressively, and treating missing hashes as unknown rather than accepting the action.
- cost: Small disk/ring-buffer overhead and a few hundred bytes per job; negligible API cost. No routine SD writes on the pendant; use the accepted bounded NVS playback/reality records.  ·  latency: ~10–30 ms locally; no extra model turn. A fresh browser or Mac probe may add up to 1–2 seconds only when the cached frame is expired.
- security: Improves provenance but adds metadata linking actions across surfaces. Hash content, redact browser/page text, scope frames to the owner/session, and never export secrets or raw screenshots to the relay.
- depends on: The live Mac permissions now report ready, so capture can run today.; A relay route/field to carry an observation-frame hash through jobs and receipts.; The accepted offline-reality-beacon and audio_delivery_ack_queue when a real pendant is registered.; A browser heartbeat/result join that preserves tab identity without exposing page contents.


## What it asked for

_Nothing._
