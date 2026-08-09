# Harness derivation — faculty-perception — round 147

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **macOS input and screen observability** — Live /ops/status reports Accessibility trusted=true, Screen Recording granted=true, requiredMissing=[] and permissions.ready=true for com.aipendant.agent; computer-use loop enabled and vision model configured, but visionUploadConsented=false.
  - evidence: GET /ops/status returned HTTP 200 at 2026-08-08T01:56Z with those fields.
- **browser continuity** — Safari browser bridge is online with one connected device, 9 tabs, active tab https://x.com titled Home / X, pendingCommands=0 and spool.spooled=0.
  - evidence: GET /browser/status returned HTTP 200 at 2026-08-08T01:56Z.
- **relay and pendant liveness** — Mac local agent reaches the configured D1 relay; relay reports macBridgeOnline=true. The live device inventory still contains no nRF pendant, only home-macbook-bridge online and cloudflare-contract-test offline.
  - evidence: GET /ops/status relay payload and discover(devices) both observed this round.

## Capabilities it proposed

### "“Use the page I’m looking at as the source of truth, make the requested change, and tell me exactly what you relied on and what actually happened.”"
- **useful because:** This would be the first genuinely trustworthy end-to-end action: Safari supplies the authenticated page, the Mac performs the reversible change, and the relay/pendant can report the result without confusing a browser read, Mac execution, or audio delivery with owner confirmation. It is especially valuable now that Accessibility and Screen Recording are live, while preserving a hard stop when source evidence is stale or ungrounded.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → relay → pendant
- **model tier:** Use the realtime model only to interpret the spoken request and summarize; use the Mac planner/computer-use loop for page grounding and action, and a cheap background verifier for hashes, receipt joins, and freshness.
- **latency:** 3–8 seconds for a simple page-grounded action; up to 20 seconds for a multi-step browser workflow. No speech should claim success before the Mac receipt and source capsule are joined.
- **cost:** Usually one realtime turn plus local computer-use; roughly $0.02–$0.15 depending on vision steps. Browser rendering and local actions dominate latency, not the final summary.
- **security:** Page contents may contain secrets and authenticated data. Keep redacted evidence capsules local, transmit only a capsule ID/hash and minimal claim to relay, require spoken confirmation for destructive or financial actions, and show ‘source unavailable’ rather than guessing. Vision upload consent is currently false, so the loop must use local screenshots until the owner explicitly opts in.
- **missing:** A relay-to-Mac evidence capsule transport: relay reads currently mint no ID/hash, while Mac evidenceCapsules already has the schema.; A single orchestration record joining browser capsule, action ledger, Mac receipt, relay job, and (when present) device playback event.; A policy that blocks action when the captured page is stale, revoked, or only asserted.

### "“I’m away from the pendant—keep me informed anyway, and when it comes back tell me only what is definitely known versus what may have been missed.”"
- **useful because:** Today the Mac bridge and Safari are live while no nRF pendant is registered. A real fallback would prevent the system from silently pretending that relay speech was heard: it would deliver a compact Mac/browser fallback, preserve pending items, then reconcile them when a pendant reconnects, clearly separating socket delivery, Mac execution, and physical playback.
- **path:** pendant → relay → mac-planner → browser-extension → relay-realtime → unified
- **model tier:** Cheap background model maintains and ranks the bounded reconciliation queue; realtime is used only when the owner asks for the spoken away-summary or makes a decision.
- **latency:** Detect a missing pendant within 90 seconds (matching current registry semantics); produce a fallback card in under 2 seconds; reconcile on reconnect within 5 seconds.
- **cost:** Near-zero for detection and queueing; $0.01–$0.05 only when summarizing a nontrivial backlog. Storage and relay polling dominate, not model calls.
- **security:** Do not dump private page text into browser notifications. Keep only titles, provenance IDs, and redacted snippets locally; require confirmation before replaying sensitive content. Never label relay ‘delivered’ as heard. The current pendant absence is structural, so the UI must say ‘no pendant registered,’ not ‘offline.’
- **missing:** A reconnect/reconciliation protocol using the accepted bounded NVS playback ledger when firmware exists.; A Mac fallback surface (notification or browser card) that records shown/acknowledged separately from spoken delivery.; A durable cross-device queue keyed by artifact ID with explicit unknown state when no pendant is present.

### "“Before you act on anything I’m seeing, give me a live truth card: which devices are actually reachable, how fresh each observation is, whether the source is grounded, and what part of the result nobody can verify.”"
- **useful because:** The owner currently has enough live reach to act, but not a single honest perception boundary. This card would make the system’s strongest behavior legible: Accessibility and Screen Recording are now ready, Safari is online, the relay is reachable, yet there is still no pendant and no proof of hearing. It prevents high-impact actions based on stale tabs, ungrounded relay reads, or Mac-side completion masquerading as delivery.
- **path:** faculty-perception → browser-extension → mac-vision → mac-planner → relay → pendant → unified
- **model tier:** No expensive model for collection or freshness checks; use deterministic joins. Use a small background model only to compress the card into owner language, and realtime only if the owner asks a follow-up.
- **latency:** Under 500 ms from local status reads; under 2 seconds if relay and browser reads must be refreshed.
- **cost:** Effectively zero model cost for the card; a few cents only for optional spoken compression. Network freshness probes dominate.
- **security:** Expose statuses and provenance, not page bodies or credentials. Bind every claim to observedAt and source; distinguish ‘not observed’ from ‘false.’ Never infer owner location or hearing from Mac or relay timestamps.
- **missing:** A live authenticated cross-surface snapshot route; the granted read_continuity_snapshot failed resolution, so the implementation needs a real /ops/snapshot-plus route or equivalent.; A common observation envelope with observedAt, freshness bound, source, confidence, and unknown reason.; Mount local browserProvenance routes and include capsule revocation/grounded state in the card.

### "“Challenge this claim before I act: compare the authenticated page I’m viewing with an independent source and my local records, show me every contradiction and what timestamped evidence supports each side.”"
- **useful because:** This gives the owner something today’s assistants cannot: a perception-level adversarial check rather than a fluent answer. It is designed for deadlines, prices, account notices, travel changes, and suspicious messages where one source can be stale or manipulated. The system should refuse to collapse disagreement into a single guess.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → relay → pendant
- **model tier:** Deterministic collectors and hash/diff code first; a cheap text model clusters claims and contradictions; realtime only speaks the final short dispute report.
- **latency:** 5–15 seconds for two web sources plus local records; up to 30 seconds when authenticated browser interaction is needed. The owner gets a partial report immediately if one source is blocked.
- **cost:** About $0.01–$0.08 per challenge; browser reads and local file/calendar access dominate. No vision upload is needed when the local computer-use loop reads the screen.
- **security:** Never send authenticated page bodies or local records to the relay by default. Keep raw captures on the Mac, send only redacted claims, hashes, and source metadata. Treat every source as untrusted, preserve exact observedAt times, and require confirmation before acting on a disputed claim.
- **missing:** A contradiction-oriented observation ledger that stores each claim, source, observedAt, content hash, and comparison result without retaining raw secrets.; A second-source acquisition policy that can choose public web, local Calendar/Mail/Notes, or another authenticated tab without silently broadening access.; A spoken report format that names unknowns and disagreement instead of selecting a winner.

### "“At 9:15, what did each surface know, what changed afterward, and which change caused the action you took?”"
- **useful because:** The owner needs a forensic rewind, not a generic history list. It would reconstruct a bounded, timestamped perception timeline across Safari, Mac apps, relay jobs, and wearable delivery, highlighting deltas and causal links. That makes silent stale-state errors visible—for example, a browser page changing after a draft was prepared—without claiming that an audio response was heard.
- **path:** faculty-perception → browser-extension → mac-planner → relay → pendant → unified
- **model tier:** Use deterministic event and hash joins for the timeline and a low-cost model only to summarize deltas. Realtime is unnecessary unless the owner asks for a spoken rewind.
- **latency:** Under 3 seconds for a recent 15-minute window; under 15 seconds for a day-scale query with local search.
- **cost:** Usually negligible; $0.01–$0.05 only for compressing many deltas. Storage/index reads dominate.
- **security:** Raw browser and local-app content remains on the Mac; the relay receives opaque references and redacted summaries. Tombstone revoked evidence and clearly label gaps caused by retention caps, relay restart, or missing pendant telemetry. Never infer causality merely from event order.
- **missing:** An append-only, local observation timeline with monotonic sequence numbers and wall-clock uncertainty, separate from the existing action/job ledgers.; Cross-surface causal edges linking a browser capture, a Mac action, a relay job, and any later device event.; A durable export/import format so a relay restart or offline pendant can be reconciled without rewriting history.

### "“Tell me when two parts of my digital life disagree—like Safari showing one deadline while Calendar or Mail says another—and ask me one focused question before anything acts.”"
- **useful because:** This is an active perception safeguard: instead of waiting for the owner to notice stale or conflicting state, the collective detects semantic disagreement across browser, Mac apps, and relay context, explains the smallest conflicting facts, and pauses action. It is more useful than a status dashboard because it interrupts only when disagreement can change the outcome.
- **path:** browser-extension → mac-vision → mac-planner → relay → pendant → faculty-judgement
- **model tier:** Deterministic freshness and field extraction where possible; a small background model normalizes dates, amounts, names, and statuses; realtime only asks the one clarification question through the pendant or Mac fallback.
- **latency:** Run on demand in 2–10 seconds, or as a low-rate watch that raises an alert within one minute of a relevant page/app change.
- **cost:** On-demand checks generally under $0.05; watch mode is mostly local computation with occasional cheap extraction. Cloud cost is bounded by changed-field events, not continuous screenshots.
- **security:** Watch only explicitly approved apps/sites and fields. Keep sensitive values local and send relay only a redacted disagreement label. No action may proceed while a high-impact conflict is unresolved; low-risk conflicts can be logged without interrupting.
- **missing:** A semantic field normalizer with per-field sensitivity and authority rules (date, price, status, recipient, location).; A watch subscription that can observe Safari plus Calendar/Mail/Notes through existing permissions without polling full page contents.; A judgement/action gate that converts a detected conflict into one owner question and blocks downstream execution until answered.


## What it asked for

_Nothing._
## Its own summary

Fresh discovery completed. The Mac agent is now genuinely perception-capable: /ops/status reports Accessibility and Screen Recording granted, permissions.ready=true, full-control and computer-use enabled. Safari’s bridge is online with 9 tabs and no pending commands; relay/D1 is reachable and the Mac bridge is online. The nRF pendant is still absent from the live device inventory, so no claim about wearable receipt or hearing is justified. I recorded these facts and proposed three owner-facing capabilities: evidence-gated page-grounded action, honest Mac/browser fallback and reconnect reconciliation when the pendant is absent, and a deterministic live truth card that distinguishes reachable, fresh, grounded, and unverifiable. The cross-surface continuity tool remains unusable despite its grant: resolution failed, with /ops/snapshot the nearest live route, so implementation still needs a real unified snapshot route. Vision upload consent is also false; local vision can run, but screenshots must not leave the Mac without explicit owner consent.

**Biggest unknown:** Whether the physical pendant is connected over USB but simply not registered remains unknown to the HTTP surfaces; the authoritative relay view says no pendant is registered. Also unknown is owner consent for uploading vision frames, which is unnecessary for local-only computer use but blocks cloud vision.

