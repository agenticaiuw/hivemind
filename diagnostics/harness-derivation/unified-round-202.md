# Harness derivation — unified — round 202

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live delivery failure and Mac permissions** — The Mac agent and browser are currently online and all required permissions are granted. A recent scheduled morning-news pipeline rendered 24 kHz mono PCM successfully (430,836 bytes, 0 clipped samples) but the relay report failed with HTTP 413 Payload Too Large; the run is failed and delivery remains composed_on_mac/awaitsDevice with heard=unknown.
  - evidence: GET /ops/status returned ready=true, accessibility and screenRecording granted, relay reachable, browser online. GET /pipeline returned pipelineId job_e60ca5d3-ee2e-4e2e-9fe4-87266d8f20b2 with tts done followed by error detail Payload Too Large (413), and delivery state composed_on_mac.

## Capabilities it proposed

### "Make every scheduled briefing either play on the pendant or clearly tell me why it did not; never say a briefing is complete when only the Mac rendered it."
- **useful because:** The live pipeline currently renders 430.8 KiB of 24 kHz PCM, then fails reporting with HTTP 413 while the run is marked failed and delivery says composed_on_mac/awaitsDevice. This turns a routine that sounds completed into silence. The owner gets a truthful fallback and a recoverable play-later item instead of a false success.
- **path:** relay → mac-planner → pendant → dashboard
- **model tier:** background for routine classification and concise fallback; realtime only when the owner asks what happened
- **latency:** Under 2 seconds to classify a failed delivery; do not block the routine on repair. A play-later artifact may upload asynchronously.
- **cost:** Small background-model call only on failure (roughly $0.005-$0.02); transport work dominates, not inference.
- **security:** The fallback must contain only the briefing text and opaque artifact/job IDs; no raw PCM in dashboard logs. Require the existing physical approval latch for any action beyond queuing playback.
- **missing:** adaptive audio artifact transport that avoids relay 413 (chunked/resumable or Opus manifest); a scheduler transition that distinguishes rendered_on_mac from delivered_to_pendant/heard; a durable play-later inbox item tied to the failed job

### "Let me ask, 'What did you learn about me this week?' and review each extracted fact with its source, then delete one fact and every derived copy without deleting my action history."
- **useful because:** The owner explicitly cannot see facts the system extracts autonomously. A weekly, evidence-backed review makes memory understandable and makes individual erasure practical rather than trusting an invisible facts.json.
- **path:** relay → mac-planner → dashboard → pendant
- **model tier:** background model for clustering and plain-language summaries; deterministic code for provenance, deletion scope, and authorization
- **latency:** Generate the review asynchronously within 30 seconds; individual fact listing should return in under 2 seconds; deletion receipt under 5 seconds.
- **cost:** One background summarization call per weekly review, roughly $0.02-$0.10 depending on evidence volume; deterministic storage/query work dominates otherwise.
- **security:** Show only facts already bound to this owner and redact secrets by default. Deletion must require explicit confirmation, erase the fact, derived graph copies, and evidence capsule across relay/Mac, while retaining job audit history and reporting off-machine deletion as pending.
- **missing:** a provenance-preserving fact/evidence query and individual erase transaction; a dashboard review surface with confirmation and pending remote-erase state; a weekly routine that does not silently add new facts

### "For each routine, let me choose 'speak now', 'make available to play later', or 'text only', and have the system honor that mode even if the pendant or relay is offline."
- **useful because:** The current routines all behave as if audio delivery is mandatory, yet the live morning-news run produced speech on the Mac and then failed at the relay. A per-routine delivery contract lets the owner choose reliability over immediacy and avoids wasting TTS/audio work when text is sufficient.
- **path:** relay → mac-planner → pendant → dashboard
- **model tier:** deterministic routing for the delivery mode; background model for the routine's actual content; realtime is unnecessary unless the owner interrupts and asks for it live
- **latency:** Mode decision under 100 ms. Text-only routines complete normally; play-later artifacts can settle asynchronously within 30 seconds; speak-now should fail visibly within 5 seconds if the device cannot be reached.
- **cost:** Text-only saves TTS and audio transfer cost. Play-later adds bounded artifact storage; no extra model call unless a shorter fallback is requested.
- **security:** Persist only the selected mode and opaque job/artifact IDs. Dashboard must show whether content is text-only, rendered, queued, delivered, or heard; never imply hearing from Mac rendering alone. Changing a routine's mode is a setting mutation and should require normal confirmation.
- **missing:** a routine deliveryMode field and UI/API to edit it; mode-aware pipeline state transitions and scheduler behavior; a durable text/result inbox for offline play-later mode; device reachability and terminal delivery evidence

### "Before you use my browser or Mac for a task, tell me exactly what private data would leave this device, where it would go, and let me approve only that narrowly scoped disclosure from the pendant."
- **useful because:** Today the system can act through authenticated browser sessions and relay models, but the owner has no reliable boundary showing whether page text, attachments, account identifiers, or screenshots will cross from the Mac to the relay. A per-action data-egress manifest would make powerful computer use trustworthy rather than opaque.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic taint/provenance analysis for the manifest and enforcement; a cheap background model may summarize the manifest in plain language. Realtime is used only to explain an already-generated manifest during a live conversation.
- **latency:** Generate the manifest before any external call, under 300 ms for ordinary browser/Mac actions; physical approval may take as long as the owner needs. No network request containing protected data may begin before approval.
- **cost:** Low inference cost because the decision is policy and provenance based; roughly $0.001-$0.01 only when a natural-language explanation is requested. The main cost is implementing data-flow instrumentation and browser/Mac adapters.
- **security:** The manifest itself must not include secret values—only categories, destinations, byte counts, and redacted field names. Bind approval to an action digest, destination, scope, expiry, and one-time nonce; reject changed pages, changed recipients, or changed attachments. Fail closed if provenance is unknown, and preserve only an audit receipt, not the disclosed contents.
- **missing:** taint labels and byte-level provenance from browser page reads, screenshots, clipboard, files, and typed inputs; a preflight gate that can stop browser/Mac execution before transmission; pendant delivery of a compact disclosure summary and binding to the existing physical transaction approval latch; relay enforcement that rejects an action whose disclosure digest was not approved

### "Search my Mac files, Notes, Mail, and currently open browser tabs for a phrase, but keep the search and source contents on the Mac and return only the smallest cited excerpts I ask for."
- **useful because:** The owner currently has separate app/browser automation, but no privacy-preserving cross-surface retrieval. Sending entire notes, mail, or pages to a relay just to answer a local search is an unnecessary exposure; local indexing would make the pendant useful as a universal recall button without exporting the corpus.
- **path:** pendant → mac-planner → browser-extension → relay
- **model tier:** Local deterministic index/query first; background model only to rank or summarize already-selected excerpts. Realtime is unnecessary unless the owner asks a conversational follow-up.
- **latency:** Common searches under 1 second from the Mac; first index build may take minutes and should be resumable. The relay receives only the query result capsule, never the corpus.
- **cost:** No per-query model cost for exact search; modest local disk/index cost and occasional background ranking calls ($0-$0.01 per query).
- **security:** Index stays encrypted and local, with app/path allowlists and per-source consent. Mail bodies, passwords, banking pages, and attachments are excluded by default. Return provenance (app, title, timestamp, local path) and redact secrets before any relay transfer.
- **missing:** a local unified index with source-specific permissions and incremental updates; a browser content snapshot/query adapter that does not export full tabs; a small result-capsule protocol from Mac to relay/pendant; owner controls for excluded apps, folders, and retention

### "For any answer you give me, let me ask 'how do you know?' and hear a compact evidence chain showing what was observed on the pendant, Mac, browser, or relay, when it was observed, and what remains inference or unknown."
- **useful because:** The system currently mixes rendered, queued, delivered, and inferred states in owner-facing language. A provenance view would let the owner distinguish a live observation from a model guess and quickly catch silent no-ops without reading logs or trusting confidence wording.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic evidence assembly and freshness checks; background model only compresses the chain into plain speech. Realtime is appropriate for the owner's immediate follow-up question.
- **latency:** Evidence chain assembled in under 500 ms from cached receipts; if a fresh probe is needed, say so and return a pending state rather than fabricate certainty. Spoken explanation under 5 seconds.
- **cost:** Near-zero for deterministic chains; occasional short summarization call, roughly $0.001-$0.01. Storage is bounded by references and hashes, not copied source content.
- **security:** Evidence capsules contain hashes, timestamps, source labels, and redacted excerpts—not secrets or full pages. Respect app/tab bindings and owner deletion policy. Clearly mark stale, inferred, contradictory, and unavailable evidence.
- **missing:** a uniform evidence-capsule schema across pendant events, relay receipts, Mac jobs, and browser results; claim-to-evidence links in model responses and routine outputs; freshness/contradiction evaluation and a pendant-sized spoken rendering; owner controls to inspect the full chain in the dashboard


## Changes it proposed to its own stack

### `relay` — Add an artifact negotiation and resumable upload protocol for audio: before sending PCM, the Mac asks the relay for accepted limits and profiles; it prefers Opus or bounded chunks with a manifest, retries only missing chunks, and records a terminal transport reason (accepted, queued, rejected-too-large, expired). A 413 must never leave the pipeline in an ambiguous active state.
- **owner gets:** Long scheduled answers will stop disappearing at the relay boundary. The owner gets either playable audio or a precise 'queued/rejected' explanation, and retries do not regenerate speech unnecessarily.
- effort: Medium-high: relay schema/routes, Mac uploader, manifest verification, and migration tests for existing 24 kHz output.  ·  risk: Chunk reordering, duplicate uploads, or stale manifests could produce corrupted audio. Use content hashes, idempotent chunk IDs, bounded retention, and validate the reconstructed WAV/Opus before exposing it to the pendant.
- cost: Negligible storage metadata; bandwidth may decrease substantially with Opus. One extra negotiation request per artifact.  ·  latency: Adds one negotiation RTT; resumable retries reduce worst-case latency and avoid retransmitting hundreds of KiB.
- security: Opaque artifact IDs and per-chunk hashes; do not put audio or briefing text in URLs/logs. Expire abandoned manifests.
- depends on: POST /pipeline/audio must accept a manifest/chunk mode; GET /pipeline/:pipelineId/audio/:direction must expose reconstructed artifact status; GET /jobs/:jobId/receipts must include transport terminal state; audio_delivery_ack_queue should consume the artifact ID rather than invent another receipt store


## What it asked for

_Nothing._
## Its own summary

Discovered live state and recorded three new owner-facing capabilities plus a relay change. The key measured defect is concrete: Mac and browser are online, permissions are fully granted, 24 kHz TTS succeeds, but the relay rejects the 430.8 KiB result with HTTP 413; the system correctly knows only that it rendered on the Mac, not that the owner heard it. I proposed (1) truthful routine completion with play-later fallback, (2) owner-controlled routine delivery modes, (3) evidence-backed weekly extracted-fact review with scoped deletion, and (4) resumable/negotiated audio artifact transport.

**Biggest unknown:** The exact maximum payload accepted by the live relay and whether its intended fix is chunked PCM, Opus artifacts, or both. I still need that transport contract implemented/tested between Mac /pipeline/audio and relay delivery, plus a scheduler state transition that cannot mark a routine complete while delivery is merely composed_on_mac.

