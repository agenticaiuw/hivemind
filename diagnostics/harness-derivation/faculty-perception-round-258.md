# Harness derivation — faculty-perception — round 258

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-surface-status-2026-08-09T04:07Z** — At the latest authenticated snapshot, the Mac agent is ready with Accessibility and Screen Recording granted; relay is reachable with D1 and Mac bridge online; Safari browser extension is online on one YouTube tab with zero pending commands; nrf9160-pendant is present in the registry but offline (its last-seen timestamp is historical). This does not establish pendant receipt or playback.
  - evidence: read_continuity_snapshot(include relay,pipeline) resolved to GET /ops/snapshot, HTTP 200, snapshot status fields; functions.discover(category=devices) lists nrf9160-pendant offline.

## Capabilities it proposed

### "“Reconstruct exactly what happened with that request — what I said, what the Mac did, what the relay accepted, whether the pendant received it, and whether I actually heard it; show me the uncertain links instead of calling it completed.”"
- **useful because:** The system currently collapses Mac execution into completion even though device_playback has zero emitters, and relay “delivered” only means bytes were handed to a socket. This would be the single most useful trust feature: every action and spoken answer gets a causal chain with explicit unknowns, clock-domain/freshness warnings, and no false success.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Background/cheap model builds the event graph; realtime only answers the owner's question and speaks a short verdict.
- **latency:** Background update within 5–15 seconds of each event; conversational answer under 1.5 seconds from cached graph.
- **cost:** About $0.005–$0.03 per reconstructed incident; most cost is graph summarization, not reads.
- **security:** Do not export page bodies or audio by default; carry opaque IDs, hashes, timestamps, and bounded snippets. Treat device playback as unknown until a device-originated event is authenticated. Require confirmation before replaying sensitive content.
- **missing:** A relay-to-Mac event join keyed by job/run/artifact ID; A firmware-originated authenticated played/received event (the accepted audio_delivery_ack_queue is the basis, but not yet callable); Clock-domain normalization and a UI/voice renderer for partial chains

### "“Tell me when the system’s own facts contradict each other in a way that could make you act wrongly — and tell me which source is authoritative, rather than silently choosing.”"
- **useful because:** Perception has already found a machine-authored America/Chicago preference pinned at confidence 0.99 while the actual Mac is America/New_York; device absence is also ambiguous because the registry is capped and the pendant does not heartbeat. A contradiction sentinel would prevent wrong routine times, false offline claims, and action based on stale state.
- **path:** relay → mac → browser → dashboard → pendant
- **model tier:** Cheap background rules first; use a stronger model only to explain a novel contradiction in owner language.
- **latency:** Evaluate on context refresh and before any consequential action; explanation under 2 seconds, no continuous model call.
- **cost:** Near-zero for rule checks; under $0.01 for an uncommon novel-conflict explanation.
- **security:** Never overwrite owner facts automatically. Label provenance (owner, machine, device, inferred), preserve both values, and require owner confirmation to resolve. Avoid exposing credentials or private browser content in alerts.
- **missing:** A provenance-aware conflict record with severity and expiry; Pre-action hook that faculty-judgement must consult; A visible/voice alert policy so low-value contradictions do not spam the owner

### "“When I come back online after a bad connection, tell me which words or actions may have been lost, how good the capture was, and whether anything actually reached my ear — then ask me to repeat only what is unsafe to guess.”"
- **useful because:** The accepted offline beacon and capture sentinel can establish link and utterance quality, but today those facts are not joined to the Mac transcript, relay job, or action receipt. This turns packet loss and offline intervals into an honest recovery conversation instead of silently transcribing damaged speech or treating a queued answer as heard.
- **path:** pendant → relay → mac → dashboard
- **model tier:** Firmware emits compact metrics; a cheap background correlator joins them; realtime handles only the short recovery prompt and clarification.
- **latency:** On reconnect, local verdict immediately; server-side join in under 3 seconds; owner prompt under 1 second after join.
- **cost:** Under $0.01 per reconnect; metrics are tiny and summarization is bounded.
- **security:** Upload quality counters and opaque sequence IDs, not raw audio by default. Persist only bounded metadata in the pendant NVS ring; never routine-write the SD failure buffer. Do not repeat or execute an uncertain command without explicit confirmation.
- **missing:** A reconnect join protocol carrying beacon/capture sequence IDs into relay and Mac pipeline events; A transcript/action policy that maps clear/degraded/unusable to repeat, review, or block; Pendant is currently absent/offline in the live registry, so hardware verification must wait for a real registration

### "“When I say ‘that one’, ‘this page’, or ‘send it’, know which thing I mean from what I’m looking at now — and ask a one-word clarification instead of guessing when the visual, browser, and speech context disagree.”"
- **useful because:** The browser is live on a real YouTube tab and the Mac now has Screen Recording/Accessibility, but speech perception has no durable, cross-surface referent fence. This would join the pendant utterance with the current browser tab, screenshot/DOM region, recent Mac focus, and evidence capsule so actions target the object the owner is actually indicating rather than the last-mentioned object.
- **path:** pendant → mac → browser → relay
- **model tier:** Cheap deterministic candidate ranking (active tab, focused app, recent capsule); realtime model only resolves the short utterance and asks clarification when margin is low.
- **latency:** Candidate set under 200 ms; screenshot/DOM read under 700 ms; clarification or action decision under 1.5 seconds.
- **cost:** Usually <$0.01 per turn; screenshot and DOM capture dominate, with no model call for unambiguous deictic references.
- **security:** Screenshots and browser contents are sensitive. Redact passwords/payment fields, retain only a short-lived content hash and region metadata, and require confirmation before destructive clicks or sends. Never infer consent from pointing alone.
- **missing:** A shared turn ID joining pendant audio, active Mac window, browser tab, and evidence capsule; A bounded referent resolver that exposes candidates and confidence to judgement/action; Owner policy for whether an ambiguous reference gets a spoken clarification or a pendant vibration

### "“Before you tell me something important, show me which facts are independently corroborated by different parts of my system, which are merely repeated copies, and what evidence would disprove them.”"
- **useful because:** Today the system can collect evidence capsules, pipeline traces, browser readings, and relay state, but it cannot distinguish independent confirmation from the same stale assertion copied across surfaces. A corroboration lens would prevent a Mac-authored belief from masquerading as device truth, expose single points of failure, and let the owner choose whether an uncertain fact is safe to act on.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Cheap deterministic provenance and dependency analysis first; use the expensive realtime model only to explain the resulting evidence graph in conversation.
- **latency:** Maintain incrementally in under 2 seconds after a source update; answer an owner query in under 1.5 seconds from the cached graph.
- **cost:** Usually below $0.01 per query; storage and graph maintenance dominate, not model tokens.
- **security:** Do not expose raw private page/audio content when metadata and hashes suffice. Preserve source boundaries so a relay echo of a Mac claim is not counted as independent. Require confirmation before using a low-corroboration fact for an external action.
- **missing:** A provenance graph with source-independence/dependency edges, not just event links; Attested origin labels for pendant, relay, Mac, and browser observations; A claim API that returns supporting evidence, counterevidence, freshness, and a disproof test; Judgement/action integration that treats corroboration level as a policy input


## What it asked for

_Nothing._
