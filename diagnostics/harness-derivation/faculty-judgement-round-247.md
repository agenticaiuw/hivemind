# Harness derivation — faculty-judgement — round 247

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What are the four latest items on my Safari Reading List, and which one should I read first?”"
- **useful because:** The owner has asked this repeatedly and currently gets failure. It would turn a known blind spot into a cited, short spoken answer: retrieve the actual Reading List through the authenticated browser, preserve title/URL/date evidence, rank by the owner's current goal, and leave the full links in a note while speaking only the recommendation.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use the browser/Mac harness for retrieval and deterministic recency extraction; use the cheaper background model to rank and summarize; reserve realtime only for the final spoken sentence and follow-up.
- **latency:** Under 8 seconds when Safari is online; if the bridge is offline, say so immediately and offer a queued retry rather than hallucinating or silently using public search.
- **cost:** Roughly $0.01–$0.04 per request, dominated by one browser snapshot/read and a small ranking prompt; no vision call unless the Reading List UI requires it.
- **security:** Read-only browser access, no navigation outside the Reading List origin without confirmation, and URLs/titles stay local unless the owner explicitly asks for sharing. Every spoken item carries its source URL/date in a receipt; failure must be reported as failure, not “no items.”
- **missing:** A production Reading List adapter/command that returns structured title, URL, and saved-at fields (the generic browser actions may need an AppleScript/UI fallback); A durable source citation record linking the browser command to the spoken ranking; A regression test for the currently observed five-tab Safari session and the empty/offline cases

### "“Did I actually hear the last briefing? If not, tell me exactly where it stopped and replay only what I missed.”"
- **useful because:** A generated audio job being accepted is not the same as the owner hearing it. This gives the wearer a trustworthy delivery boundary: distinguish generated, downloaded, started, finished, interrupted, checksum-failed, and never-played; resume from the last confirmed item without repeating the whole brief.
- **path:** relay-realtime → pendant → mac-planner → dashboard
- **model tier:** Deterministic event reconciliation and item selection; use the realtime model only to phrase the one-sentence result or produce a requested compact replay. No expensive model is needed to decide completion.
- **latency:** Under 1 second for a known artifact after ACK ingestion; under 5 seconds when reconciling queued offline events. Replay begins only after the next deliberate play request.
- **cost:** Near-zero model cost for status; about $0.005–$0.02 only for a generated compact replay. Storage is a bounded event ledger keyed by opaque artifact and device sequence.
- **security:** ACKs must be authenticated to the device session, deduplicated by event ID, and checked for monotonic sequence/byte bounds. Speak only the item title and position by default; use provenance to explain why the result says interrupted. Never infer hearing from server acceptance.
- **missing:** A production reconciliation/read route over the events accepted by POST /pipeline/events (the granted recorder currently describes ingestion but no owner-facing query); A stable mapping from audio artifact to briefing item/cursor token; Pendant firmware emission of the already-accepted audio_delivery_ack_queue events on the shipping LTE path, plus a UI route for the owner-facing receipt

### "“The pendant sounded wrong. Find the cause, tell me whether it was the link, codec, or speaker path, and prepare the smallest safe fix and a proof test.”"
- **useful because:** This turns the owner’s direct experience into a bounded diagnosis instead of another vague bug report. It correlates authenticated pendant UART metrics with pipeline/job receipts and the exact audio artifact, identifies whether the failure was packet loss, queue starvation, checksum/download, decode cost, or playback interruption, then prepares a reviewable repair/test plan rather than changing firmware blindly.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** Use deterministic metric thresholds and receipt joins first; a background model writes the explanation and minimal test plan; realtime only answers the wearer. Any firmware or shell mutation is gated by autonomy_policy_evaluate and explicit approval.
- **latency:** Initial diagnosis in 3–10 seconds depending on UART window; draft test plan within 30 seconds. No automatic firmware flash or external issue submission.
- **cost:** About $0.01–$0.05 for explanation and plan generation; dominant cost is collecting/correlating the UART window and pipeline evidence, not model tokens.
- **security:** Keep raw microphone/audio payloads out of the draft; include metrics, opaque artifact IDs, firmware/build hashes, and redacted excerpts only. Draft locally by default, never file externally without confirmation. If evidence conflicts, report unknown rather than choosing a convenient cause.
- **missing:** A typed read/query endpoint for prior pendant delivery events and UART windows, not just an ingestion call; A join key connecting artifactId, pipelineId, jobId, firmware build, and device session; A small library of measured remediation recipes and repeatable audio-quality-probe.mjs acceptance tests; A safe Mac-side test executor that can run the probe and attach results without flashing

### "“That was wrong—show me exactly which assumption caused it, correct only that assumption, and make sure you do not repeat the same mistake.”"
- **useful because:** Today the owner can inspect a receipt or provenance chain, but correcting a bad judgement does not become a scoped, testable improvement. This capability turns a spoken correction into a reversible calibration: identify the mistaken evidence/policy assumption, preserve the owner’s correction, replay the decision in shadow mode, and apply it only to matching future situations. It improves the system through lived use without silently rewriting broad personal memory.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic provenance and policy diff first; use a background model to classify the correction and generate a proposed rule; realtime only acknowledges and asks for confirmation when the correction would affect future external actions.
- **latency:** Acknowledge in under 2 seconds. Produce the evidence chain and proposed scoped calibration within 15 seconds. Shadow-test it against recent decisions asynchronously.
- **cost:** Approximately $0.01–$0.05 per correction, dominated by comparing the correction with prior provenance and running a small shadow evaluation. Storage is a bounded, append-only calibration ledger.
- **security:** A correction must never silently mutate facts, permissions, or owner policy. Store the original decision, correction, scope, expiry, and confirmation state; require explicit confirmation for rules affecting mutation, external communication, or sensitive speech. Allow the owner to revoke one calibration without deleting unrelated memory.
- **missing:** A durable calibration record linking an owner correction to the exact evidence, policy version, action, and affected scope; A shadow-evaluation runner that can compare old versus corrected outcomes without executing actions; A user-facing calibration lifecycle: proposed, confirmed, expired, revoked, and proven useful; A distinction between correcting a one-off fact and correcting a general decision rule, so one mistaken answer cannot overfit the owner


## What it asked for

_Nothing._
