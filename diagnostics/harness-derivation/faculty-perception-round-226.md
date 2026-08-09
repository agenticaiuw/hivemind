# Harness derivation — faculty-perception — round 226

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-permissions** — The live Mac agent reports Accessibility and Screen Recording granted for com.aipendant.agent, all required permissions ready=true, and browser extension online with 3 Safari tabs and 0 pending commands at 2026-08-09T00:51:31Z.
  - evidence: GET /machine-context returned permissions accessibility.trusted=true, screenRecording.granted=true, ready=true; read_continuity_snapshot GET /ops/snapshot returned browser online, tabCount=3, pendingCommands=0.
- **live-device-state** — Current device discovery shows home-macbook-bridge online and Safari browser online; no nRF9160 pendant is present in the live device table.
  - evidence: discover(category=devices) returned Safari on MacIntel online, home-macbook-bridge online, and cloudflare-contract-test offline; no pendant row.

## Capabilities it proposed

### "“Before you act, tell me whether this request is grounded in what actually happened across my Mac, browser, relay, and pendant—and show me any contradiction.”"
- **useful because:** This would be the system’s single most valuable perception capability: it would prevent a relay receipt, a Mac-completed job, or a browser snapshot from being mistaken for owner-visible reality. It builds a causal evidence chain and explicitly flags conflicts such as ‘Mac says completed’ versus ‘pendant never acknowledged playback,’ rather than emitting another best-effort digest.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → unified
- **model tier:** Cheap background model builds and compares the evidence graph; realtime only speaks the short verdict. Deterministic checks handle timestamps, IDs, hashes, and acknowledgement state before any model interpretation.
- **latency:** Under 500 ms for an existing job or utterance; under 3 s when browser provenance or a fresh relay read must be joined.
- **cost:** About $0.001–$0.01 per check; most work is local deterministic joins, with a small model call only for naming the contradiction.
- **security:** Only hashes, opaque IDs, stage names, and redacted snippets should cross surfaces by default. Full browser content stays on the Mac capsule store. Any conclusion that would trigger a side effect requires owner confirmation when evidence is contradictory or merely asserted.
- **missing:** A shared correlation ID carried from voice turn to Mac job, browser command, relay job, and pendant artifact; A relay-to-Mac export of stable browser-read ID/content hash so relay reads can enter the existing evidence-capsule schema; A reader that treats device playback events as physical evidence instead of trusting Mac completion; A bounded, append-only contradiction record with source, observedAt, and confidence

### "“Warn me—and pause the action—when the world changed underneath a plan, like a browser tab, Mac file, relay job, or device state becoming stale.”"
- **useful because:** A status report after the fact is not enough. This is a perception fuse that detects time-of-check/time-of-use failures and forces a re-observation before an email, purchase, deletion, or other consequential action. It protects the owner from acting on a stale tab, stale permission state, expired relay job, or a result invalidated by a reconnect.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → unified
- **model tier:** No expensive model for the fuse: deterministic freshness windows, revision/hash checks, and event ordering. Use a cheap model only to explain the single blocking reason in the owner’s preferred one short sentence.
- **latency:** 150 ms for local revision/freshness checks; at most 2 s for one targeted re-read before asking for confirmation.
- **cost:** Usually under $0.001 per check; dominated by an occasional browser snapshot or relay read, not inference.
- **security:** The fuse should expose only the minimum changed field (for example ‘price changed’ or ‘permission changed’), not page contents or secrets. It must never silently retry a destructive operation after a mismatch; require confirmation and preserve the old/new hashes for audit.
- **missing:** Revision tokens or content hashes on Mac action preconditions and browser snapshots; A freshness policy by artifact type (seconds for checkout/permissions, minutes for ordinary reading); An action executor that accepts preconditions and atomically refuses on mismatch; A machine-readable event clock shared by relay, Mac, browser, and eventually pendant

### "“If my speech was clipped, noisy, or interrupted, tell me exactly what you understood and do not carry out the dangerous part until I confirm.”"
- **useful because:** A wearable system must distinguish ‘the owner said it’ from ‘the microphone produced a plausible transcript.’ The pendant’s local integrity verdict can stop an unsafe command before LTE or transcription; the relay can carry quality metrics with the transcript; Mac planning can downgrade to a clarification instead of executing. This is a cross-device safety behavior, not another audio-quality dashboard.
- **path:** pendant → relay-realtime → mac-planner → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Firmware and relay use deterministic quality thresholds; realtime gives a brief repeat request. A cheap text model classifies whether the requested operation is consequential. Never spend the expensive tier to infer confidence from audio that the sentinel already marked unusable.
- **latency:** Local unusable-capture decision under 100 ms after utterance end; repeat request within 300 ms. A degraded-but-usable utterance may take the normal 1–2 s planning path, with no action until confirmation.
- **cost:** Negligible inference cost for clear/unusable verdicts; roughly $0.001–$0.005 only when degraded speech needs a short clarification.
- **security:** Send metrics (VAD boundaries, loss, clipping, RMS, clock continuity, sequence number), not raw microphone audio, unless the owner explicitly retries. Bind the verdict to the utterance sequence so a late packet cannot authorize a newer command. Destructive actions require a second clean capture or explicit confirmation.
- **missing:** A shared utterance sequence and quality envelope in the relay transcript/job schema; A policy reader that maps quality=unusable/degraded to ‘repeat’/‘confirm’ rather than allowing execution; A visible receipt that states ‘not acted on because capture was degraded’; A pendant-originated quality event path once the real device registers; the current live table has no pendant

### "“Before I approve this, show me the complete privacy route: what leaves the pendant, what reaches the relay, what the Mac or browser stores, and exactly which secrets are redacted.”"
- **useful because:** The owner cannot currently see the data-flow consequences of a voice request or browser action. This would turn privacy from a hidden implementation detail into an approval decision: a concise route diagram, fields leaving each surface, retention destination, and a reversible choice to keep the work local, redact it, or cancel it.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Deterministic taint tracking and schema inspection do the actual accounting; a cheap model summarizes the route in one spoken sentence. Realtime is only needed to ask for approval at the moment of transmission.
- **latency:** Under 300 ms for already-known schemas; under 2 s when a browser page or queued job must be inspected before approval.
- **cost:** Usually <$0.002 per request; dominated by no model call, with a small summarization call only for complex routes.
- **security:** The audit must never copy the very secret it is explaining. It should use typed labels and hashes, keep the route ledger local, and require confirmation before raw audio, page text, credentials, or sensitive files cross the relay. A malicious page must not be able to influence its own classification.
- **missing:** A single taint-label vocabulary shared by firmware, relay, Mac, and browser; Outbound interception hooks at each cross-surface boundary, including synthesized audio and browser command payloads; A local, append-only privacy route receipt with retention and deletion controls; An approval protocol that binds the owner’s choice to one request hash and expires it

### "“Only interrupt me when this is worth breaking my attention; otherwise hold it, explain why you waited, and deliver it when I become available.”"
- **useful because:** The system today can queue or speak, but it cannot perceive the owner’s real interruption cost. A wearable can detect speaking/noise and connection state, the Mac can expose active meeting/focus/app state, the browser can show whether the owner is mid-checkout or composing text, and the relay can arbitrate while devices disappear. The owner gets fewer intrusive interruptions without losing urgent information—and a truthful explanation of every delay.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → unified
- **model tier:** A deterministic urgency/interruption policy handles most decisions; a cheap background model ranks ambiguous items. Realtime is used only for urgent delivery or a short ‘held until available’ explanation.
- **latency:** Under 200 ms for local hold/deliver decisions; urgent escalation within 1 s. Availability changes should be reflected within 3 s across the relay.
- **cost:** <$0.003 per queued item; ranking and policy evaluation are local, with no expensive inference for ordinary notifications.
- **security:** Presence signals stay local and are reduced to coarse states (available, speaking, driving-like unavailable, focused), never raw microphone or screen recordings. The owner can set hard exclusions. A high-priority sender must not bypass the policy without an explicit rule, and held content needs bounded retention.
- **missing:** A cross-surface availability state with signed freshness and explicit expiry; A policy engine that separates urgency, interruption cost, and owner exceptions; A durable hold/release queue that records why an item was delayed and prevents duplicate delivery; Pendant-side local sensing and a real registered pendant; the current live device table has none

### "“Forget this request everywhere—find every copy, revoke it on the relay, Mac, browser, and pendant, and prove what was deleted versus what could only be tombstoned.”"
- **useful because:** The owner cannot currently obtain a trustworthy erasure answer across the hive. This capability would discover copies by correlation and content hash, stop queued delivery, revoke browser evidence, delete eligible Mac audio and relay records, and return an honest residue report for immutable logs or offline pendant storage. It is especially valuable for accidental recordings, private browser pages, and secrets spoken aloud.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Deterministic index and hash joins perform discovery, revocation, and deletion; a cheap model only turns the residue report into plain speech. No realtime reasoning is needed except to confirm the owner’s target and scope.
- **latency:** A first inventory in 2 s; urgent queued-delivery revocation under 500 ms. Full multi-store sweep may run in the background, with progress and a final receipt.
- **cost:** <$0.005 per erasure request; storage scans dominate, not model tokens.
- **security:** Erasure itself is destructive and must require explicit confirmation, with a precise scope preview. Authenticate the owner, never reveal deleted secret contents, preserve only minimal non-content audit tombstones, and distinguish ‘deleted,’ ‘revoked,’ ‘expired,’ ‘offline pending,’ and ‘cannot reach.’ A compromised browser must not be allowed to claim deletion.
- **missing:** A global content-address/correlation index spanning relay jobs and announcements, Mac ledgers/audio, browser capsules, and pendant records; Deletion/revocation APIs for every store, including relay announcements and audio whose current retention sweep is not automatic; A pendant reconnect handshake that accepts erasure tombstones before any queued playback; A signed erasure receipt that lists stores visited, timestamps, and residual reasons


## What it asked for

_Nothing._
## Its own summary

Fresh discovery found the Mac agent is now fully permission-ready (Accessibility, Screen Recording, automation; ready=true), the browser bridge is online with three Safari tabs and no pending commands, the relay is reachable, and no nRF9160 pendant is present. I recorded those facts. I proposed three non-duplicate capabilities: a cross-surface reality/evidence graph, a stale-world precondition fuse that blocks actions after drift, and quality-gated speech execution that refuses degraded captures. The most important remaining need is a shared correlation/sequence contract spanning Mac, browser, relay, and the eventual pendant, plus a relay-originated browser evidence bridge and a real pendant playback/quality event path. Do not request TCC permission again: it is granted now.

**Biggest unknown:** Whether the relay and Mac already expose an undocumented shared correlation identifier or event clock; the live inventory shows the component routes, but no established observation proves those joins exist.

