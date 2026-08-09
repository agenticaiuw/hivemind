# Harness derivation — unified — round 249

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What changed across my browser, Mac, and pendant since I last checked, and what actually needs my attention?”"
- **useful because:** The owner currently has to ask separate surfaces and cannot distinguish a new event from a stale job or a browser result that never completed. This produces one bounded, provenance-linked delta digest: Mac jobs and receipts, authenticated browser changes in explicitly bound tabs, relay delivery state, and pendant inbox/approval state, with each item labeled observed/failed/pending and a direct next action. It is the single most useful daily capability because it turns the hive from a set of tools into a trustworthy continuity layer.
- **path:** relay → pendant → mac-bridge → browser → dashboard
- **model tier:** background for collection and deterministic diffing; realtime only to summarize on demand
- **latency:** Initial digest under 5 s from cached snapshots; fresh browser probes may take up to 20 s and must be explicitly labeled live
- **cost:** ~$0.01–$0.04 per digest; browser probes and model summarization dominate, while receipts and hashes are local/deterministic
- **security:** Only inspect browser tabs/session bindings the owner explicitly authorizes; never include page credentials or raw private DOM by default. Every item needs source, timestamp, and evidence receipt; mutation is never implied by the digest.
- **missing:** A durable cross-surface cursor/watermark per owner acknowledgement; Typed delta normalization joining relay jobs, Mac jobs, browser results, and pendant inbox records; A dashboard/pendant presentation for grouped pending/failed/changed items

### "“Before I open or download this, tell me whether it is the same file/page I trusted before, what changed, and quarantine it if it is not.”"
- **useful because:** A logged-in browser and Mac can reach private documents that the pendant cannot inspect, while the relay can retain a compact provenance record. This capability gives the owner a practical safety boundary against changed invoices, attachments, and look-alike pages: compare origin, signed/cryptographic identity where available, content fingerprint, and prior owner-approved evidence, then stage—not silently perform—a quarantine or move when the identity drifts.
- **path:** browser → mac-bridge → relay → dashboard → pendant
- **model tier:** deterministic hashing and policy checks first; background model only for explaining semantic differences
- **latency:** 2–5 s for known local files/pages; up to 15 s for an authenticated page extraction; no download or move without confirmation
- **cost:** ~$0.002–$0.02 per check; hashing and metadata are cheap, semantic diff is the main variable
- **security:** Never upload file contents by default; hash locally and send only redacted metadata/diff spans. Browser extraction must be restricted to an owner-bound tab. Quarantine is a write and requires the existing physical_transaction_approval_latch or equivalent explicit confirmation.
- **missing:** A typed file/page identity capsule with canonical URL, origin, size, hash, signer and prior-approval reference; A safe local quarantine action with receipt and undo semantics; Browser extension support for owner-visible, redacted semantic diff regions

### "“I’m about to leave—make sure nothing private is still recording, queued, exposed in the browser, or waiting for approval, and tell me exactly what remains.”"
- **useful because:** The current privacy latch can stop the pendant, but the owner has no single end-of-session assurance across relay persistence, Mac jobs, browser exposure, queued captures, and staged transactions. This capability performs a read-only convergence audit, separates stopped/contained from pending/off-machine, and offers only explicitly confirmed cleanup actions. It is the practical privacy boundary for a wearable that spans devices.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic state convergence and receipts; realtime speech only for the short owner-facing result
- **latency:** Under 3 s from cached leases; up to 10 s for live browser/Mac checks; must return partial results rather than hang
- **cost:** <$0.01 per audit; dominated by live bridge/browser checks, not model tokens
- **security:** The audit itself must not expose captured audio or page contents. Report opaque IDs, counts, timestamps, and retention state. Cleanup of off-machine copies is asynchronous and must say requested/pending. Any deletion or cancellation requires confirmation and a durable receipt.
- **missing:** A unified end-of-session state machine tying privacy latch state to relay queues, Mac capture/jobs, browser sessions, and approval records; A typed cleanup plan distinguishing stop, cancel, delete, and await-replication; Owner-facing presentation of partial convergence and stale-device warnings

### "“Before I send or say this, tell me whether it reveals something private about me, who could receive it, and what safer wording keeps the useful part.”"
- **useful because:** The system can already see owner-authored context on the Mac, authenticated browser sessions, and extracted personal facts, but it cannot act as a disclosure boundary. This would catch accidental oversharing in email, messages, forms, and spoken replies while preserving the owner's intent. It would report the exact evidence behind a warning and never rewrite or send without confirmation.
- **path:** pendant → browser → mac-bridge → relay → dashboard
- **model tier:** background classification and deterministic policy checks; realtime only for the short spoken warning
- **latency:** Under 2 seconds for text already in the conversation; up to 8 seconds when inspecting a bound browser form or recipient context
- **cost:** $0.01–$0.05 per assessment; semantic classification dominates
- **security:** The analyzer itself must not broaden access: inspect only owner-selected drafts or explicitly bound form fields, redact secrets before model use, and retain only a hash plus decision receipt. Sending, typing, or changing text requires explicit confirmation.
- **missing:** A privacy taxonomy for facts, recipients, and disclosure purposes; Recipient/context extraction from bound Mail, Messages, and browser sessions; A redacted explanation format that cites the relevant fact without repeating the secret

### "“Find contradictions in what my calendar, reminders, browser pages, and recent conversations say, and ask me only about conflicts that change what I should do.”"
- **useful because:** The hive currently stores observations in separate systems and can act on stale or mutually inconsistent information. A contradiction service would compare dates, commitments, names, and status claims across explicitly authorized sources, rank conflicts by consequence, and present one concise clarification question instead of silently choosing a source.
- **path:** relay → mac-bridge → browser → pendant → dashboard
- **model tier:** deterministic normalization and temporal comparison first; background model for entity resolution and concise questions
- **latency:** 15 seconds for an on-demand sweep; under 3 seconds for cached recent sources
- **cost:** $0.02–$0.08 per sweep; source reads and entity-resolution inference dominate
- **security:** Only compare sources the owner binds for that request. Store conflict fingerprints and source pointers, not full calendar, page, or conversation contents. Never edit a source while resolving a contradiction.
- **missing:** A common fact representation with source authority, observed time, effective time, and confidence; Connectors that expose bounded Calendar, Reminders, browser, and conversation evidence; A conflict lifecycle: open, owner-resolved, superseded, and intentionally ignored

### "“I replaced or reset my pendant. Restore my privacy settings, pending inbox, and safe operating policy without restoring old audio or granting the new device authority by accident.”"
- **useful because:** A wearable can be lost, reset, or replaced. Today the owner cannot safely migrate the state that matters—privacy latch policy, transport preferences, pending non-audio inbox items, approval trust, and delivery cursors—without either starting over or risking stale authority. This would make replacement survivable while explicitly excluding recordings and requiring a fresh physical binding ceremony.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** deterministic manifest migration and cryptographic verification; background model only to explain differences
- **latency:** 5–15 minutes for a deliberate replacement ceremony, with every stage resumable
- **cost:** <$0.02 per migration; cryptographic operations and small relay metadata dominate
- **security:** The old device must be revoked before the new one receives authority. Never migrate audio, raw transcripts, browser secrets, or approval tokens. Require possession of the old device where possible plus a physical approval on the new one; provide a signed recovery receipt.
- **missing:** Device identity and revocation records in the relay; A versioned, allowlisted pendant-state manifest with per-field sensitivity; A two-device or recovery-key binding ceremony and replay-resistant migration receipt


## Changes it proposed to its own stack

### `relay` — Add a cross-surface causal timeline protocol. Each relay, Mac, browser-extension, and pendant event carries its local monotonic counter plus wall-clock observation, boot/session epoch, source, and predecessor receipt. The relay stores only compact event headers and computes a bounded partial order with explicit uncertainty intervals instead of pretending the clocks agree. Expose causal links such as staged→approved→dispatched→browser-applied→audio-delivered and mark gaps or impossible reversals.
- **owner gets:** When something goes wrong, the owner can hear the truth about what happened and in what order—rather than a misleading list of timestamps. It makes “it said it sent it, but I never heard it” and “the page changed before/after I approved” answerable across devices.
- effort: Medium-high: event schema, boot/session handling on pendant and bridge, relay partial-order reducer, and adapters for existing job/browser/audio receipts.  ·  risk: Clock mistakes or duplicate events could create false causal links. Preserve raw source events, never delete them during reduction, and label uncertain ordering. Roll out read-only first and compare against known audio/job traces.
- cost: Low storage and API cost: roughly 100–300 bytes per event header; no model cost for ordering.  ·  latency: Negligible on hot paths if reduction is asynchronous; a fresh explanation may wait 1–3 seconds for late receipts.
- security: Event headers can contain sensitive URL/job labels, so encrypt or redact payload labels and bind access to the owner token. Never include page contents or audio in the timeline.
- depends on: A typed shared receipt/event envelope across existing Mac, browser, relay, and pendant producers; A durable owner acknowledgement cursor for reading the timeline; Existing audio_delivery_ack_queue and action/job receipts must expose stable predecessor IDs


## What it asked for

_Nothing._
