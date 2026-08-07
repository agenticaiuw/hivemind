# Harness derivation — unified — round 49

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I tap the pendant to bookmark a moment, reconstruct what I was looking at and doing across my Mac and logged-in browser at that time, then leave me a sourced note I can review later."
- **useful because:** The owner can capture an idea or confusing moment without stopping to explain it. The pendant supplies an always-available timestamped signal even offline; the Mac and browser supply private visual and page context; the relay waits through outages and turns the result into a durable, reviewable note rather than pretending the assistant understood live.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic event correlation and local extraction first; use background gpt-4.1-mini only to summarize conflicting context, escalating to realtime only if the owner asks a follow-up aloud.
- **latency:** Tap acknowledgment under 150 ms locally. After connectivity returns, context snapshot within 10 s and a concise cited note within 30 s; no blocking conversation.
- **cost:** Usually near-zero model cost for timestamp/window/page metadata; roughly $0.002–$0.01 per bookmark when summarization is needed. Storage and browser/Mac polling dominate operational cost.
- **security:** Private screen content and authenticated page excerpts leave the Mac only to the relay for the generated note; default to metadata and user-approved app/tab allowlists, redact passwords and sensitive fields, encrypt at rest, and require confirmation before any external sharing or mutation. If Screen Recording or browser consent is absent, produce an honest partial note rather than infer.
- **missing:** A pendant bookmark event with monotonic and wall-clock timestamps that survives LTE loss; A Mac snapshot endpoint capturing frontmost app/window and permitted screen regions with provenance; A browser snapshot endpoint binding open tabs/session IDs to the same timestamp and returning redacted excerpts; Relay durable correlation window and idempotent note job joining late-arriving device, Mac, and browser evidence; Dashboard review card showing evidence, confidence, missing sources, and deletion controls

### "Compare what is in my private logged-in accounts with current public information, but keep the private page contents on my Mac; give me a cited answer based only on the minimum redacted facts needed."
- **useful because:** The owner could ask questions such as whether a private travel booking is still compatible with a public disruption, or whether a logged-in order matches a current product notice, without exporting entire authenticated pages to the cloud. It combines browser-only access, local Mac redaction, relay orchestration, and public research in a way no single node can provide.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic local extraction and redaction first, then gpt-4.1-mini in the background for fact alignment; reserve the realtime tier for a spoken clarification or urgent result.
- **latency:** Spoken acknowledgment under 1 second; ordinary comparison in 20–60 seconds. Show an incremental result if public research or browser access is slow.
- **cost:** Approximately $0.003–$0.02 per comparison, dominated by background synthesis and public search; local extraction and redaction require no model call where selectors are known.
- **security:** Raw authenticated DOM, screenshots, cookies, and credentials must remain on the Mac. The Mac sends only an allowlisted typed fact set with field-level sensitivity labels and source hashes. The owner must approve new domains or sensitive fields; the dashboard must show exactly which redacted facts left the device and support deletion.
- **missing:** A local privacy-preserving extraction/redaction service that converts authenticated pages into typed facts before relay upload; A relay protocol for signed, field-scoped evidence bundles and public-source citations; A planner that can detect when a private fact is insufficient and ask for a narrower extraction rather than requesting the whole page; A dashboard view showing private evidence kept local versus derived facts shared with the synthesis model


## Changes it proposed to its own stack

### `integration` — Add a cross-surface temporal evidence ledger. Every pendant bookmark, relay receipt, Mac foreground/screen snapshot, and browser tab extraction is recorded as an append-only event envelope with device monotonic time, synchronized wall-clock estimate, source nonce, consent scope, and evidence hash. A relay joiner groups events in a configurable ±45-second window, marks late/missing sources explicitly, and emits one immutable correlation ID consumed by the dashboard note card. This is a time-alignment primitive, not another prompt-memory projection or browser job queue.
- **owner gets:** A tap made during a dropped link can later be matched to the exact private page and app context instead of producing a vague timestamp or a false confident recollection. The owner can inspect precisely which sources contributed and delete the whole episode by correlation ID.
- effort: Medium-high: firmware event schema and clock-offset calibration; Mac/browser snapshot hooks; D1 event and index tables; idempotent join worker; dashboard evidence view; fault-injection tests for clock drift, duplicates, and delayed uploads.  ·  risk: Clock drift or stale snapshots could join the wrong context. Bound windows, require source freshness, show uncertainty and unmatched sources, and never silently merge across sessions. If the joiner fails, retain raw events and retry; if consent changes, prevent later enrichment and tombstone affected evidence.
- cost: Small D1/R2 metadata increase (typically <10 KB per bookmark before optional excerpts); no model cost for ledger/join. Optional background summarization adds about $0.002–$0.01 per completed episode.  ·  latency: Local tap remains immediate; correlation is asynchronous, normally 1–10 seconds after all sources arrive, with late evidence updating the card without rewriting its original receipt.
- security: Evidence hashes and consent scopes are stored with each event; raw screen/page content remains on the Mac until explicitly uploaded. Encrypt relay storage, redact secrets before upload, and provide per-episode deletion.
- depends on: Pendant bookmark event and offline queue; Mac/browser snapshot APIs with explicit consent scopes; Durable relay job execution and dashboard review card

### `hardware` — Replace the HUZZAH32 SBC-only A2DP source in the production audio path with a BLE Audio-capable bridge (for example an nRF5340 Audio DK-class design or equivalent) that accepts the pendant's 24 kHz mono LC3/PCM stream and negotiates a 24 kHz/32 kHz LE Audio unicast stream to the owner's earbuds. Keep the current ESP32 as a development fallback, but make the bridge expose explicit sample-rate and packet-loss telemetry to the relay.
- **owner gets:** Speech reaches the earbuds as true superwideband instead of being forced through 44.1 kHz stereo SBC and a second resampler. That should make the pendant sound clearer, reduce unnecessary radio traffic, and avoid the current fragile 44 kB Bluetooth buffer starvation.
- effort: High: select certified LE Audio chipset/earbud compatibility, redesign bridge firmware and enclosure/power, add LC3 framing and clock recovery, qualify pairing/reconnect behavior, and run end-to-end 24 kHz acceptance tests under LTE contention.  ·  risk: LE Audio earbud support and pairing UX vary by vendor; retain SBC fallback and a wired/bridge diagnostic mode. Clock mismatch or buffer underrun could cause gaps, so use bounded jitter buffering and explicit fallback telemetry. Hardware certification and RF coexistence are required before shipping.
- cost: Prototype bridge roughly $35–$80 in parts plus certification/NRE; likely 20–60 mW additional active bridge draw depending on chipset. Ongoing model/API cost unchanged; lower audio bitrate may reduce LTE data cost modestly.  ·  latency: Potentially 20–60 ms lower audio pipeline latency by removing the 31.25→44.1 kHz FIR and SBC buffering, though LE Audio connection intervals may add 10–30 ms. Reconnection may be slower than the current A2DP path.
- security: Use authenticated LE pairing, rotate bonding keys on reset, and never expose raw PCM over an unencrypted debug characteristic. Keep device identity separate from relay credentials.
- depends on: End-to-end 24 kHz superwideband acceptance criteria; Pendant link-aware duplex governor; A production pendant/bridge power and RF design

### `integration` — Create a local-first private-fact broker on the Mac. Browser extraction recipes declare an output schema and sensitivity policy; the broker resolves fields locally, removes raw DOM/URLs/cookies and disallowed values, signs a minimal fact bundle with source hashes and expiry, and sends only that bundle to the relay. The relay can combine those facts with public-search results, but cannot request raw page contents or broaden fields without a new owner-visible approval.
- **owner gets:** The owner gets answers that require both their private accounts and live public information without handing complete authenticated pages to a cloud model. They can audit exactly what crossed the privacy boundary and revoke or delete a comparison.
- effort: High: typed extraction/redaction runtime in the Mac agent, browser schema annotations, signed bundle verification in the Worker, field-level consent UI, expiry/deletion handling, and adversarial tests against prompt injection in page text.  ·  risk: A faulty extractor could omit a crucial field or leak a sensitive one; default-deny fields, local previews, schema validation, canary secret tests, and refusal on ambiguity are required. Malicious page content must be treated as data, never instructions. If signing or relay verification fails, answer locally or fail closed.
- cost: No additional hardware cost and little storage; one background synthesis call typically $0.003–$0.02. Local CPU cost is small compared with browser rendering.  ·  latency: Adds roughly 100–500 ms for local extraction/redaction and signature verification; public research remains the dominant delay.
- security: Improves privacy substantially by enforcing a cryptographic, field-scoped egress boundary. Raw authenticated content stays on the Mac; relay storage contains only minimized facts and hashes.
- depends on: Browser bridge returning structured authenticated-page data; Mac local-agent storage for consent policies and signing keys; Relay verification and public-research synthesis endpoint


## What it asked for

_Nothing._
