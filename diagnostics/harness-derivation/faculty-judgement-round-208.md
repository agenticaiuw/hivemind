# Harness derivation — faculty-judgement — round 208

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Show me yesterday’s interruptions as if I had chosen a different quiet-hours or urgency policy—what would you have spoken, queued, or suppressed?”"
- **useful because:** The interruption policy is currently a placeholder and the owner cannot safely tune it by trial-and-error. A retrospective simulator makes the consequences visible without changing the live policy or disturbing the owner.
- **path:** relay → mac → pendant → dashboard
- **model tier:** Background model for summarizing a deterministic replay; use the cheap policy evaluator for every event and reserve the expensive model for the final plain-language comparison.
- **latency:** Up to 10 seconds for a day; return a progressive count first and a complete comparison within 30 seconds.
- **cost:** Low: deterministic replay dominates; roughly $0.01–$0.05 for an optional natural-language summary. Storage/querying of event receipts is the dominant engineering cost, not inference.
- **security:** Replay must redact notification bodies and private snippets by default, show only item titles/categories, and never execute or enqueue anything. The owner explicitly requests any sensitive detail in the dashboard. Preserve the policy version and input evidence so results are reproducible.
- **missing:** A durable, append-only attention-decision journal containing candidate event, evidence references, owner state, policy version, and ACT/QUEUE/SUPPRESS result; A read-only replay endpoint that feeds historical events through autonomy_policy_evaluate and attention_arbitrate without emitting; A dashboard comparison view and a policy draft/accept step

### "“At the moment you suggested or did that, what did you actually know, which sources were stale, and what changed afterward?”"
- **useful because:** Current provenance can explain an action or item, but it does not reconstruct the time-bounded state that produced the judgement. This prevents false confidence after calendars, pages, permissions, or goals change and lets the owner distinguish a bad decision from a later world change.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Background model only for the final narrative; deterministic assembly of timestamped evidence, policy, receipts, and state snapshots should do the work.
- **latency:** 3 seconds for a compact answer, 15 seconds when browser and Mac evidence must be joined.
- **cost:** Low inference cost, about $0.01 per reconstruction; the main cost is bounded durable snapshots and indexed joins.
- **security:** Default to source IDs, hashes, freshness, and redacted excerpts. Do not resurrect revoked content. A reconstruction is read-only and must label inferred fields versus captured-at-the-time fields; dashboard-only sensitive expansion requires explicit confirmation.
- **missing:** A timestamped decision-context envelope written atomically with every judgement: source IDs and freshness, owner state, policy version, context-handoff handle, and resulting action/brief item ID; A cross-surface join index connecting relay job IDs, Mac jobs, browser commands, pipeline events, and pendant delivery ACKs; A read-only temporal reconstruction route that refuses to imply evidence not present at the decision time

### "“If I revoke this source, exactly which memories, brief items, pending actions, and spoken artifacts would disappear or become unsafe—and which copies would remain?”"
- **useful because:** Revocation today is not a real boundary: derived facts and context-graph copies can survive an evidence revoke. A read-only blast-radius report lets the owner make an informed deletion decision before discovering that sensitive material remains elsewhere.
- **path:** dashboard → relay → mac → browser → pendant
- **model tier:** Deterministic graph traversal and content-addressed joins first; a cheap background model may turn the result into a short explanation, never decide the deletion scope.
- **latency:** Under 3 seconds for indexed records; up to 20 seconds for a full historical scan.
- **cost:** Low inference cost, under $0.02 per report; storage/indexing of provenance edges is the main cost.
- **security:** Default output is counts, IDs, hashes, sensitivity classes, and retention deadlines—not raw quotes. Never mutate during preview. Revocation must be transactional or clearly report partial completion, preserve tombstones, and require a separate explicit confirmation for cross-store deletion.
- **missing:** A durable source-to-derived-artifact edge on facts, context-graph entities, briefing items, audio artifacts, and external drafts; A read-only impact-preview route that computes complete, partial, and unlinked descendants before POST /evidence/revoke; A transactional revocation worker with per-store receipts, retry, and an honest unresolved-items report

### "“Only tell me you told me after the pendant actually downloaded and started playing it; if it did not, recover without making me repeat myself.”"
- **useful because:** A generated response or Mac receipt is not proof the owner heard anything. The owner should receive a truthful delivery state—played, interrupted, rejected, or unknown—and the system should preserve the unplayed response for one-tap replay or a compact text fallback rather than falsely closing the interaction.
- **path:** relay → pendant → mac → dashboard
- **model tier:** Deterministic state machine for delivery truth and retry; use a cheap background model only to compress an unplayed response into a safe fallback.
- **latency:** Under 1 second to acknowledge download/playback events; recovery decision within 3 seconds of a failed or interrupted ACK.
- **cost:** Near-zero model cost for state transitions; optional summarization under $0.01. The dominant cost is durable event retention and replay handling.
- **security:** Use opaque artifact IDs and authenticated device sessions, never transcript text in delivery events. Enforce idempotency and monotonic device sequence numbers. Never replay a private artifact to a public route; an unknown audience must remain blocked until explicitly resolved.
- **missing:** A durable delivery-state reducer that joins pipeline receipts with pendant ACKs and distinguishes generated, downloaded, started, finished, interrupted, and no-audio; An idempotent recovery policy that can enqueue replay or a redacted alternate channel without duplicating speech; Owner-visible delivery receipts and a compact pending-response handle that survives relay/Mac restarts

### "“Before you act on an important fact, show me the independent signals that agree, the ones that disagree, and what single check would settle it—do not silently average them.”"
- **useful because:** The system currently tends to compose whatever each surface returns, while empty or stale reads can look authoritative. The owner should get a disagreement-first answer that distinguishes corroboration from duplicated copies and recommends the cheapest decisive check before an external action.
- **path:** relay → mac → browser → dashboard → pendant
- **model tier:** Cheap deterministic evidence clustering and freshness checks first; background model only writes the concise explanation after the conflict set is computed.
- **latency:** 5 seconds for local receipts and memory; up to 20 seconds when a read-only browser check is needed.
- **cost:** Usually under $0.02; browser reads and evidence indexing dominate, not model inference.
- **security:** Read-only by default. Do not expose raw private snippets on the pendant; show source classes, timestamps, and hashes, with dashboard expansion only after confirmation. Never treat two derived records from one source as independent corroboration.
- **missing:** A source-lineage graph with independence groups, freshness, and authority scope; A typed read-only corroboration planner that can request one decisive check without mutating anything; A policy hook that blocks or downgrades external actions when required independent evidence is absent


## Changes it proposed to its own stack

### `hardware` — Replace the development-kit speaker path with a product pendant that has a physically switched private receiver path (low-power in-ear or bone-conduction transducer) plus a deliberately selected public speaker fallback, and add a real two-state privacy indicator (separate privacy LED or e-ink shutter) tied to the hardware mute switch. The relay labels each artifact private/public; firmware refuses private artifacts when only the public path is active.
- **owner gets:** The pendant can finally speak calendar, mail, and personal reminders without broadcasting them to people nearby. Today audio modules have no confidentiality gate and the board has only one LED and a prototype output path; this makes privacy a physical property rather than a model promise.
- effort: High: product audio/mechanical redesign, secure artifact routing metadata, firmware state machine, and field testing for intelligibility and leakage.  ·  risk: Receiver failure could make urgent output inaudible; recover by falling back only for explicitly public artifacts and surfacing a silent/private-unavailable state. Hardware mute must fail closed. Leakage testing is required in quiet rooms and transit noise.
- cost: Roughly $20–$80 in added BOM depending on receiver and enclosure; modest extra power, likely 10–30 mA during playback. No per-invocation API cost.  ·  latency: Negligible routing latency; private receiver wake may add 50–150 ms.
- security: Large positive: physical public/private separation. Requires signed artifact audience metadata and no downgrade from private to public without explicit owner action.
- depends on: A product pendant revision beyond the nRF9160 DK; A signed audio-artifact audience field consumed by relay, Mac, and firmware; A firmware privacy latch that controls both capture and playback

### `firmware` — Add a fail-closed audio-artifact verifier before any speaker start: the relay signs an opaque artifact manifest (artifact ID, byte length, codec/profile, audience class, expiry, session nonce); the nRF9160 verifies the signature and checksum, binds playback to the current session, and refuses unsigned, expired, replayed, or audience-mismatched artifacts. Emit a reason-coded local event and use the existing alert/inbox path for recovery rather than playing fallback text.
- **owner gets:** A stale or misrouted response cannot suddenly be spoken aloud after a reconnect, retry, or compromised bridge. The owner gets an honest “not played—verification failed” instead of hearing something that the system cannot prove came from the current conversation.
- effort: Medium-high: signing key provisioning/rotation, compact manifest framing, verifier implementation under the existing RAM budget, relay and ESP32 bridge pass-through, and negative-path hardware tests.  ·  risk: Clock ambiguity can reject valid artifacts; use monotonic session epochs and signed expiry windows rather than trusting the pendant wall clock. Key rotation outages need a bounded overlap. Recovery must never silently downgrade to unsigned playback.
- cost: No recurring inference cost; about 4–12 kB flash and under 4 kB RAM for a compact verifier/manifest, plus negligible radio bytes. A secure-element upgrade would add roughly $1–$3 if TF-M isolation is insufficient.  ·  latency: Usually under 10 ms before decode; manifest verification can happen while downloading, so no audible start penalty.
- security: Strong positive: authenticity, freshness, and audience binding at the last point before sound. Does not replace the physical privacy latch or private receiver.
- depends on: A relay signing key and rotation protocol; The existing audio_delivery_ack_queue and record_pendant_delivery_event flow; A compact signed manifest carried beside each Opus artifact; Firmware key storage/verification design validated against TF-M

### `hardware` — Make the next pendant a two-channel interaction device rather than a speaker-only prototype: add a tiny owner-facing e-ink/OLED status surface with a physical privacy shutter or proximity-to-skin sensor, plus a dedicated acknowledgement control. Private text, source names, and unresolved conflicts can be displayed locally while open-air audio carries only a neutral cue; the relay sends content-class metadata, not a guessed confidentiality decision.
- **owner gets:** The owner can receive a sensitive reminder, conflict, or failed-delivery explanation in public without broadcasting it and without needing to pull out a phone. It also gives the system a truthful place to show uncertainty when speech would be unsafe or the audio path is unavailable.
- effort: High product redesign: display, enclosure, power budget, secure rendering protocol, sunlight/readability tests, and a clear interaction model for unread/expired content.  ·  risk: A visible display can still be observed by others and could become a new data leak. Default to redacted labels, require a deliberate reveal gesture, blank on timeout/removal, and keep secrets out of display buffers when the privacy sensor is uncertain.
- cost: Approximately $8–$25 BOM and 1–10 mA while refreshing, depending on e-ink versus OLED; modest enclosure and firmware cost. No recurring API cost.  ·  latency: Cue immediately; e-ink detail may take 300–1000 ms to render. This is acceptable for status and review, not live speech.
- security: Positive if the privacy sensor/shutter and reveal gesture are hardware-enforced; otherwise it is merely another output surface and must be treated as public.
- depends on: A product pendant revision beyond the nRF9160 DK; Signed content-class metadata for every displayed/spoken artifact; A local privacy state machine shared by audio, display, and physical controls


## What it asked for

_Nothing._
## Its own summary

Round 208 produced three owner-facing capabilities and two stack changes. The strongest new capability is a retrospective interruption-policy simulator: replay yesterday’s attention decisions under alternate policies without speaking or mutating anything. I also specified temporal decision reconstruction (what the system knew at the instant of a judgement) and a read-only revocation blast-radius report (what evidence-derived copies would remain before deletion). The hardware/firmware direction is a product private-audio path and fail-closed signed audio-artifact verification, because the current prototype has no last-mile confidentiality or authenticity gate. The recorder noted the first three are connective work over existing primitives; the genuinely missing pieces are durable attention journals, timestamped decision envelopes, cross-store provenance edges, and transactional revocation—not new model features.

**Biggest unknown:** The owner still has not chosen the policy values that determine whether private content may ever be spoken on an open speaker, which destinations are trusted, or what counts as urgent. I will not invent those. Until those choices exist, ship conservative defaults and make every decision name the policy field that caused it. Accessibility/Screen Recording remain owner-side TCC decisions; I did not re-request them.

