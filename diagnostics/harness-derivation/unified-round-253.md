# Harness derivation — unified — round 253

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “do this,” carry it through the Mac and my logged-in browser, ask for the pendant’s physical approval only when needed, and tell me exactly what happened—even if the Mac or browser drops halfway."
- **useful because:** This is the system’s highest-value promise: a spoken intent becomes a durable, auditable result rather than a plan that can be spoken about and silently discarded. It joins the worn approval boundary, relay durability, Mac execution, and browser-only reach.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** Realtime for the short spoken confirmation and result; background/planner tier for action decomposition, evidence reconciliation, and retry decisions.
- **latency:** Acknowledge in under 1 s; stage approval in under 3 s; execute in background and speak a receipt within 10 s for ordinary actions. Outages may defer completion, but never fabricate success.
- **cost:** About $0.01–$0.08 per invocation depending on planning and browser ambiguity; model planning and browser screenshot context dominate.
- **security:** Never put credentials or page contents on the pendant. Bind approval to plan digest, world fingerprint, nonce, expiry, and replay safety. Require physical approval for off-machine, irreversible, or uncontained actions; idempotent/additive steps may resume only under a valid lease. Keep job history while allowing separate fact erasure.
- **missing:** Wire shared approvalHandoff persistence into relay D1 and the pending-next-conversation delivery path; Call closeLedger from ordinary orchestrator runs so completed plans are not misclassified as interrupted; Add relay job leases and requeue sweep for crashed Mac workers; Connect physical_transaction_approval_latch events to the approval evaluator and execute gate; Provide a real owner-facing pending/approved result surface instead of the current spoken 'waiting for approval' dead end

### "At the end of every conversation, tell me whether you heard my words, delivered your reply to the pendant, and whether it actually played—then automatically recover or give me a precise next step if any stage failed."
- **useful because:** Relay acceptance is not delivery, and delivery is not hearing. This gives the owner a truthful end-to-end conversation result instead of assuming a successful websocket or Opus packet means the reply was audible.
- **path:** pendant → relay → mac-bridge
- **model tier:** Deterministic counters and receipts for the verdict; background model only to phrase a human explanation when degraded. No expensive realtime generation is needed for diagnosis.
- **latency:** Update stage state within one audio frame; speak a compact final status within 1 s after playback stop. Recovery should begin immediately, without injecting synthetic audio into the hot path.
- **cost:** Near-zero model cost for healthy turns; $0.001–$0.01 only for explaining persistent degradation. Storage is a bounded metadata ring, not routine SD audio.
- **security:** Transmit opaque artifact IDs, sequence ranges, checksums, and counters—not raw audio. Keep receipts bounded and deduplicated. Never claim hearing from relay acknowledgement alone; expose uncertainty and preserve privacy-latch state.
- **missing:** Complete the existing audio_delivery_ack_queue across relay, bridge, and pendant firmware; Correlate uplink capture, Opus packet ranges, bridge acknowledgements, playback start/finish/interruption, and link faults under one turn ID; Add owner-facing degraded/failure phrasing and a bounded recovery policy that respects the duplex_audio_congestion_guard; Expose a read-only receipt query joining pipeline and job evidence

### "When I ask you to buy something in my logged-in browser, read back the exact item, seller, total, delivery address, and return policy; let me approve that exact checkout on the pendant; then submit once and bring me the browser’s confirmation receipt."
- **useful because:** Purchases are where browser reach and a wearable consent boundary matter most. It prevents the dangerous gap between 'I asked for this' and an accidental checkout, while still letting the Mac/browser do work the pendant cannot reach.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Planner/background tier for product comparison and checkout-field extraction; realtime only for the concise readback and approval interaction. Deterministic browser assertions must gate submission.
- **latency:** Readback within 5 s after checkout page is ready; physical approval valid for one exact digest and expires after 10 minutes; submit once and return confirmation within 5 s.
- **cost:** $0.02–$0.10 per purchase depending on comparison and page complexity; browser snapshots and planner reasoning dominate.
- **security:** Never read or transmit payment credentials to the pendant or model. Bind approval to merchant, SKU/quantity, total/currency, address hash, shipping estimate, and page/session identity. Refuse if any bound field changes, if the page is not the expected authenticated tab, or if confirmation cannot be captured. Treat purchase as off-machine/irreversible and require the physical latch.
- **missing:** A typed checkout-field extractor and immutable purchase digest across browser snapshots; A browser submit gate that accepts only the pendant’s transaction nonce and revalidates all fields immediately before click; Relay persistence for staged purchase state and expiry across Mac/browser reconnects; A receipt parser that captures order number, final total, and confirmation URL without storing payment secrets

### "Before I check out, warn me if this purchase duplicates something I already bought or a subscription I already have, and show me the matching order, renewal date, and cancellation path; let me explicitly override the warning on the pendant if I still want it."
- **useful because:** The owner cannot currently get a cross-site duplicate-purchase or subscription warning. The browser can see the current checkout and the Mac can act, but neither has a durable, owner-auditable comparison across order history, receipts, and active subscriptions. This prevents accidental recurring charges and duplicate gear without blocking legitimate replacements.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background/planner tier for normalizing merchant, SKU, quantity, and subscription terms; realtime only for the short warning and override prompt. Deterministic matching and policy checks must decide whether to block or warn.
- **latency:** Analyze the checkout in under 5 seconds after its fields are stable; show a warning before any submit action. An override is bound to the current checkout digest and expires after 10 minutes.
- **cost:** About $0.01–$0.06 per check; browser order-history reads and product normalization dominate. Store compact merchant/item/renewal metadata, not page screenshots or payment data.
- **security:** Read only explicitly bound authenticated tabs and approved receipt sources. Never expose payment credentials or full addresses to the model or pendant. Hash sensitive identifiers, retain provenance for each match, and require a deliberate physical override for a detected duplicate or recurring charge. Treat the warning as advisory unless the owner chooses a blocking policy.
- **missing:** A privacy-preserving purchase/subscription inventory with provenance and retention controls; Browser adapters for order history, subscription management, and current checkout fields across supported sites; A deterministic duplicate matcher with confidence, replacement-versus-duplicate distinction, and owner-configurable blocking policy; A relay-persisted checkout warning/override record bound to the exact checkout digest and physical approval nonce; A cancellation-path extractor that can return a safe, site-specific next action without submitting it


## What it asked for

_Nothing._
## Its own summary

Recorded three new owner-facing capabilities: durable cross-surface execution with physical approval and truthful recovery; end-to-end audio heard/delivered/playback receipts; and exact, nonce-bound browser checkout approval. The extracted-fact review/erase idea was correctly rejected as an existing backlog item, so I did not restate it. Fresh discovery shows /prepare and /approve are documented but return 404 in this live backend, while /browser/poll is live and currently returns 204.

**Biggest unknown:** The approval loop is the key blocker: whether the orchestrator will wire the existing local prepare/approve implementation into the live relay and pendant delivery path, and what the actual production request/response contract should be. I still need that implementation decision—not another capability grant—before these proposals can become runnable.

