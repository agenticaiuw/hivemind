# Harness derivation — faculty-perception — round 134

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live cross-surface state** — At 2026-08-08T01:07Z, the Mac agent reports permissions.ready=true with Accessibility and Screen Recording granted; relay is reachable on D1; browser extension is online with 9 tabs and active Safari page https://platform.openai.com titled 'Billing overview'; browser pendingCommands=0 and spool.spooled=0. The pendant is not represented in this Mac-agent snapshot.
  - evidence: GET /ops/snapshot returned HTTP 200; status.permissions.ready=true, relay.reachable=true, browser.online=true, browser.devices[0].tabCount=9, tabTitle='Billing overview - OpenAI API', pendingCommands=0, spool.spooled=0.

## Capabilities it proposed

### "“Did that actually happen, or does one part of you only think it did?”"
- **useful because:** Today completion is contradictory: the Mac can report a job executed, the relay can report bytes written, and the browser can report a command still pending—while no device playback evidence exists. This capability gives the owner a single plain-language answer that distinguishes observed facts, inferred success, and unknowns, instead of confidently repeating a false completion.
- **path:** relay-realtime → mac-planner → browser-extension → unified → faculty-perception
- **model tier:** background for routine reconciliation; realtime only to answer the owner’s question after the compact facts are assembled
- **latency:** Under 2 seconds when asked; use one bounded snapshot read and parallel local/relay lookups, never a full transcript replay
- **cost:** ~$0.002–$0.01 per query; dominated by model wording, not reads
- **security:** Do not expose raw page text or credentials in the contradiction report. Cite job IDs, timestamps, and states; mark relay 'delivered' as socket-write only and device hearing as unknown. No action should be triggered from this report without faculty-judgement.
- **missing:** A typed cross-surface join key linking relay job, Mac receipt, browser command, and (when present) device playback event; A contradiction classifier with explicit evidence precedence and an owner-readable confidence/status vocabulary; A relay-side reader for device playback events once the pendant exists

### "“Before you say or send this, check whether the thing currently open makes that unsafe.”"
- **useful because:** The browser is live on a billing page while the pendant/voice channel is designed to speak aloud. A harmless-looking reminder, copied text, or browser action can disclose financial, health, login, or private-message content to anyone nearby or to the wrong web origin. This is a user-visible guard that understands both the destination and the ambient output path, not a generic permission prompt.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** small background classifier for page/action sensitivity; realtime model only explains a block or asks the owner
- **latency:** 150–400 ms for known tabs using title/URL/DOM metadata; under 2 s when a fresh page read is required
- **cost:** Usually <$0.001 using deterministic host/category rules; ~$0.003–$0.01 only for ambiguous visible content
- **security:** Never upload page bodies by default. Classify locally from URL/title/accessibility metadata, redact snippets, and return only sensitivity class plus reason. Require explicit confirmation before aloud playback, clipboard transfer, external send, or navigation from a high-sensitivity surface. Billing/login pages should be treated as sensitive even when text classification is uncertain.
- **missing:** A local ambient-output policy that knows whether the destination is pendant speaker, Mac speakers, screen, clipboard, or external web form; A browser inspection result with sensitivity labels and a stable tab/session join key; A preflight hook in relay speech and browser action dispatch that faculty-action must honor

### "“Is the evidence you’re relying on still true right now?”"
- **useful because:** A browser reading or Mac observation can become false between perception and action: a price, account state, appointment, or form value may change, a tab may navigate, or a capsule may expire/revoke. Before an irreversible action, this capability rechecks the exact source and reports unchanged/changed/unavailable with a diff and age, so the owner is not asked to trust stale context.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** deterministic hash/age comparison first; small model summarizes only changed regions; realtime tier only for an owner-facing explanation
- **latency:** Under 500 ms for an already-open tab and local capsule; under 3 s for a fresh authenticated read
- **cost:** <$0.001 for local hash comparison; ~$0.003–$0.02 when a browser read and summarization are needed
- **security:** Revalidate in the same tab/session and do not silently substitute a public relay read for an authenticated page. Redact secrets before diffing or speaking. A changed or unverifiable source must stop action and require owner confirmation; revocation/expiry is a hard fail, not a low confidence score.
- **missing:** A relay-to-Mac provenance transport that returns stable read ID/content hash; the relay browser read currently returns neither; A mounted browser provenance reader joined to evidence capsules and action receipts; A precondition gate in faculty-action that consumes the revalidation verdict before mutating actions

### "“Tell me what changed in the outside world while I was away, and separate what you observed from what you inferred.”"
- **useful because:** The owner cannot currently obtain a trustworthy change narrative across their authenticated browser sessions, Mac files/apps, relay jobs, and a future wearable. Existing histories answer isolated events, but not whether a state change was externally caused, merely displayed differently, or never verified. This would produce a causal, evidence-ranked timeline rather than another completion digest.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → unified → faculty-perception → faculty-judgement
- **model tier:** background change detector and deterministic event correlator; realtime only to explain the resulting timeline
- **latency:** Build incrementally while away; answer in under 3 seconds from a bounded event index
- **cost:** <$0.01 per away-period summary; storage/indexing dominates, not model tokens
- **security:** Keep private page bodies and file contents local; export only redacted event descriptors, hashes, source, timestamp, and confidence. Never infer that a displayed state was caused by the system. Mark third-party changes and unknown causes explicitly.
- **missing:** A durable cross-surface causal event index with immutable observation IDs and clock uncertainty; Browser and Mac watchers that emit state deltas rather than only command receipts; A reconciliation model that can represent conflicting observations without collapsing them into one status

### "“When the pendant comes back, recover exactly what I said and what you replied while it was disconnected—without guessing or replaying the wrong thing.”"
- **useful because:** Today a disconnected wearable can create an unjoinable gap: local capture quality, relay conversation state, Mac work, and later audio delivery may each have different sequence or clock domains. The owner cannot obtain a cryptographically joined offline-to-online conversation record or know which replies were never delivered. This capability would reconcile the gap and present only confirmed utterances, with explicit missing segments.
- **path:** relay-realtime → mac-planner → mac-terminal → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** deterministic sequence/boot-session reconciliation first; background model summarizes only after the ledger is joined
- **latency:** Under 5 seconds after USB/LTE reconnection; no cloud model call for the reconciliation itself
- **cost:** <$0.005 per reconnect; dominated by bounded metadata upload and optional summarization
- **security:** Use end-to-end encrypted metadata and per-session pseudonyms; never upload raw offline audio unless the owner explicitly requests recovery. Reject ambiguous sequence joins rather than stitching conversations by timestamp alone. Preserve a visible “missing” interval.
- **missing:** A pendant-originated signed session/sequence ledger that survives link loss and can be uploaded over USB or LTE; A relay/Mac join protocol accepting monotonic device time plus clock uncertainty, not assuming Mac timezone; A user-facing repair report that distinguishes recovered, duplicate, and irreconcilable segments

### "“Before you rely on this answer, tell me which parts you cannot actually observe.”"
- **useful because:** The owner cannot today ask for a complete boundary around a claim. The system may have a browser receipt, a Mac execution record, and relay delivery metadata while lacking the decisive fact—such as whether a person heard audio or whether a third party changed a page. This capability returns an explicit observability boundary and refuses to silently fill gaps with defaults or stale state.
- **path:** faculty-perception → faculty-judgement → faculty-action → unified → relay-realtime → mac-planner → browser-extension
- **model tier:** deterministic evidence-coverage computation; inexpensive model only translates the coverage graph into natural language
- **latency:** Under 1 second for an existing claim; under 3 seconds if it must gather current surface liveness
- **cost:** <$0.002 per claim; mostly local graph traversal
- **security:** Expose metadata and uncertainty, not private evidence bodies. Treat absence of an observation as unknown, never as false. Any action consuming a claim must carry its coverage boundary and expiry.
- **missing:** A first-class observation/claim graph with typed edges: observed, reported, inferred, stale, revoked, and unavailable; Every action and relay/browser result must carry an observation ID and freshness interval; A hard action-policy hook that rejects claims whose required evidence class is unavailable


## Changes it proposed to its own stack

### `relay` — Make every relay-originated browser read return a content-addressed readId and sha256 over the redacted text, plus source URL/title and capturedAt; have the Mac provenance layer mint or link its existing evidence capsule from that receipt. Preserve the current untrusted marker, but make provenance and freshness machine-readable. Do not create a second evidence schema.
- **owner gets:** When the system quotes a live page or acts on it, the owner can see exactly which page snapshot supported the claim and whether it changed before the action. This is especially important while a sensitive billing page is open and when relay and authenticated browser reads disagree.
- effort: Small relay response and Mac call-site change; moderate tests for redaction, hash stability, expiry, and same-tab/session affinity.  ·  risk: A hash without redaction discipline could become a fingerprint leak; hashing must occur after existing redaction and URLs must not include query secrets. If the bridge fails, mark evidence unavailable and block only actions requiring freshness, not unrelated conversation.
- cost: Negligible CPU/storage; bounded capsule retention already exists on Mac. One small hash and metadata record per read.  ·  latency: ~1–5 ms hashing locally; no model latency added.
- security: Improves auditability but increases durable metadata. Drop URL queries/fragments where appropriate, retain only redacted content, and honor capsule revoke/expiry.
- depends on: Mount the existing browserProvenance routes and connect the existing evidenceCapsules mintCapsule path for relay-originated reads; Define the action precondition verdict that faculty-action will enforce; Do not treat relay 'delivered' as evidence that a pendant played the resulting speech


## What it asked for

_Nothing._
