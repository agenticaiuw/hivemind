# Harness derivation — faculty-perception — round 142

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac and browser observability** — At 2026-08-08T01:39Z the Mac agent is healthy and fully ready: Accessibility and Screen Recording are granted, browser extension online with 9 Safari tabs and zero pending commands, relay reachable with D1 storage, and no pendant appears in the live device inventory.
  - evidence: GET /ops/status and GET /ops/snapshot returned agent.permissions.ready=true, browser.online=true/tabCount=9/pendingCommands=0, relay.reachable=true/store=d1; discover(devices) listed only Safari on MacIntel, home-macbook-bridge, and offline cloudflare-contract-test.

## Capabilities it proposed

### "Tell me only facts that are simultaneously current in my open browser, verified by the Mac, and safe to act on; cite the tab, timestamp, and what changed if the page moves."
- **useful because:** This would turn browser access into dependable perception rather than an uncited paragraph. It prevents acting on a stale or login-wall page, and is the single most useful perception capability because it joins the browser's private session, the Mac's authority, the relay's conversation, and the owner's wearable request.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background for capture and hashing; realtime only to summarize the already-verified result
- **latency:** Under 2 seconds for an already-open tab; up to 5 seconds if the extension must refresh its inspection
- **cost:** Usually <$0.01 per request; dominated by no model call or a small realtime summary, not page capture
- **security:** Never send page bodies to the relay by default. Keep content and hashes on the Mac; return only redacted claims and a capsule ID. Login walls, secrets, and changed tabs must yield 'not verified' rather than guesses. Acting on a claim requires explicit confirmation if the claim is stale or the tab changed.
- **missing:** Relay-to-Mac evidence receipt carrying capsuleId, contentHash, tab/session pseudonym, and capture time; Mount local browserProvenance routes and make relay read_web_page return a correlation ID/hash; A verifier that compares the requested tab identity and current hash immediately before action

### "If my last spoken request was noisy or clipped, tell me exactly what was unreliable and ask me to repeat before doing anything; if it was clear, show the quality evidence you used."
- **useful because:** Speech recognition errors currently look like valid intent. A compact, device-measured quality verdict lets judgement distinguish 'the owner asked X' from 'the audio was unusable', avoiding dangerous actions and needless retries while offline or on a noisy walk.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → dashboard
- **model tier:** No LLM for quality classification; use the pendant sentinel and a cheap relay rule. Realtime only reformulates the verdict for the owner.
- **latency:** Under 150 ms after utterance end for clear/degraded/unusable; repeat prompt within 500 ms
- **cost:** Negligible inference cost; a few hundred bytes of telemetry per utterance
- **security:** Transmit metrics, not raw audio. Never infer consent or intent from a degraded transcript. Keep monotonic sequence numbers and reject duplicate/out-of-order verdicts. A degraded utterance can request clarification but must not silently trigger Mac actions.
- **missing:** Relay schema and reader for the offline-capture-integrity-sentinel verdict; A judgement policy mapping unusable/degraded/clear to repeat, clarify, or proceed; Mac action receipts linked to the utterance quality sequence

### "Before you answer 'nothing happened' or 'it worked', tell me what the system could not observe, which devices were absent, and how old each source is."
- **useful because:** The most dangerous perception error is a confident negative: no pendant event is not the same as no event, and a completed Mac job is not proof that audio played. This gives the owner an explicit uncertainty boundary instead of fabricated completeness.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Cheap background aggregation of typed status records; realtime only speaks the concise uncertainty report
- **latency:** Under 1 second from cached snapshot; under 3 seconds for fresh relay/Mac reads
- **cost:** <$0.005 per request; dominated by one bounded status read, no page or audio content
- **security:** Expose metadata and reasons, not page contents, transcripts, or credentials. Distinguish absent, stale, unsupported, and failed. Never collapse a missing pendant heartbeat into offline unless registry semantics support it. Preserve source timestamps and clock domains.
- **missing:** A truthful normalized schema for unknown/absent/stale/observed outcomes; A single authenticated endpoint replacing the currently unresolved continuity snapshot tool; Readers for device_playback absence, bounded retention, browser pending state, and relay delivery-vs-playback distinction

### "When I ask what is happening, give me a synchronized 'now' packet: the exact Mac/browser state, the relay's state, and the pendant's last local frame, all normalized to one capture instant, with any clock disagreement shown instead of hidden."
- **useful because:** Today each surface reports a different slice and time, so the owner cannot tell whether a failure is current, delayed, or already recovered. A synchronized packet would make the collective's present state understandable during real incidents and ordinary interruptions.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Background aggregation with deterministic normalization; realtime only narrates the packet when asked.
- **latency:** Under 2 seconds when connected; if a node is absent, return its last frame and age rather than waiting indefinitely.
- **cost:** Near-zero model cost; bounded metadata payload under 10 KB per request.
- **security:** Do not include page bodies, audio, credentials, or private application content. Use monotonic sequence numbers and explicit clock domains. Mark estimates and stale frames distinctly; never interpolate a missing pendant frame.
- **missing:** A capture-barrier protocol that requests frames from Mac, browser, relay, and pendant within a bounded interval; A shared schema for wall-clock, monotonic-clock, boot/session ID, and source freshness; A dashboard and spoken formatter that preserve disagreement rather than selecting one timestamp

### "Find the answer across my private browser tabs and Mac files without uploading either source; tell me the minimum redacted result that proves the answer, and let me choose whether the underlying evidence may ever leave the Mac."
- **useful because:** The owner currently must choose between weak cloud-only browsing and exposing private material to a model. A local federated perception query would search browser sessions and Mac data where they live, return only a minimal proof, and make privacy an explicit per-answer choice.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-terminal → dashboard
- **model tier:** Local Mac model or deterministic extractors for search and redaction; realtime only handles the spoken request and summarizes the redacted result.
- **latency:** Under 5 seconds for up to 9 open tabs plus indexed local sources; stream progress if longer.
- **cost:** Usually <$0.01, dominated by local inference; no page/body token cost to the cloud unless the owner opts in.
- **security:** Browser and file contents remain on-device by default. Use capability-scoped, ephemeral query tokens; redact secrets before any relay transmission; record which sources were searched without recording their contents. Require confirmation before exporting evidence or acting on it.
- **missing:** A local federated query planner spanning browser-extension reads and Mac search; A proof-minimization/redaction layer that can answer without returning source bodies; A pendant-to-Mac privacy consent state that survives a dropped relay connection

### "If a fact I relied on changes, find every pending reminder, briefing, draft, and planned action that depends on it, mark them suspect, and tell me what must be rechecked before anything runs."
- **useful because:** Current provenance can explain an individual browser read, but the system cannot propagate a correction through work already queued elsewhere. This prevents stale facts from quietly becoming reminders, spoken announcements, or real-world actions hours later.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Background dependency indexing and deterministic invalidation; realtime only explains the affected items.
- **latency:** Under 3 seconds after a source-change event; scheduled rescans may run in the background.
- **cost:** <$0.01 per invalidation; dominated by local indexing, with no need to resend source bodies.
- **security:** Store only hashes, claim IDs, dependency edges, and redacted summaries. Never infer that a changed page invalidates unrelated work. Quarantine is fail-safe and reversible; releasing an item requires owner confirmation for consequential actions.
- **missing:** A durable claim/dependency graph joining browser evidence, pipeline runs, reminders, announcements, routines, and action-ledger steps; Change notifications or bounded rechecks for browser tabs and external sources; A quarantine state understood by the relay scheduler, Mac job runner, and announcement queue


## What it asked for

_Nothing._
