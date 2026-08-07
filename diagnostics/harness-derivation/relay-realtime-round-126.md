# Harness derivation — relay-realtime — round 126

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Check whether the amount and deadline in the document I’m looking at match the authenticated portal and the related local messages/files; tell me only what conflicts, with the exact sources.”"
- **useful because:** Today the browser, Mac, and pendant can each inspect a source, but the owner cannot ask for a single trustworthy reconciliation across sources they may not even be near. This catches stale PDFs, changed portal values, and conflicting messages without making the owner manually compare them.
- **path:** relay-realtime → browser-extension → mac-planner → mac-terminal → faculty-perception → faculty-judgement → faculty-action → relay-realtime
- **model tier:** Use relay-realtime only to capture the spoken request and acknowledge it; use the cheaper background planner/perception-judgement-action path to retrieve, normalize, compare, and cite sources, then return a short spoken result.
- **latency:** Acknowledge within 300 ms; return an initial result in 10–20 seconds. If a source is slow, report which source is pending rather than blocking the voice session.
- **cost:** Roughly one background multi-source task (about $0.02–$0.15 depending on document length and screenshots), plus negligible relay speech overhead. Token and screenshot extraction dominate.
- **security:** The browser session and local files/messages may contain private or work data; send only the minimum requested fields to the comparison model, retain source references and hashes rather than full copies, and never expose one source's contents in another surface's logs. Reading is default; any write, send, or portal submission must remain a separate explicit action.
- **missing:** A typed cross-source extraction/comparison job that accepts a user-specified subject and source selectors; Common normalized fields with source citations, confidence, and explicit conflict/unknown states; A result delivery path that associates the completed comparison with the originating voice session; Redaction and retention controls spanning authenticated browser captures and Mac artifacts

### "“I lost my pendant—lock it out everywhere, invalidate its sessions, and tell me what is still active; if I find it, let me re-pair without losing my history.”"
- **useful because:** A wearable is a physical bearer of the owner's voice access. Today there is no single spoken recovery operation that revokes the pendant, browser sessions, relay tokens, and Mac pairing together; losing the device could leave an unclear, long-lived access path.
- **path:** relay-realtime → browser-extension → mac-planner → mac-terminal → unified → dashboard
- **model tier:** No expensive model is needed: deterministic relay/device identity code performs revocation and inventory; use background summarization only to explain the resulting session list in plain language.
- **latency:** Revoke relay and browser credentials immediately (under 2 seconds), then inventory Mac/browser heartbeats and report partial results within 10 seconds. Re-pairing can take under a minute.
- **cost:** Negligible model cost; mostly durable identity/session storage and a few authenticated status calls. A background explanation, if requested, should be well under $0.01.
- **security:** The spoken request itself must be strongly bound to the current owner, not accepted from an arbitrary replay. Require a pre-established recovery factor (for example a dashboard-held recovery key or a second registered device), make revocation idempotent, record an append-only audit event, and never speak secrets or token values. Re-pairing must rotate all credentials, not restore old ones.
- **missing:** A durable device-identity registry with per-surface revocation fan-out; A recovery factor and explicit lost-device/re-pair state machine; Browser-session and Mac-agent token invalidation endpoints with acknowledgement; A status view showing which surfaces have confirmed revocation versus are unreachable


## Changes it proposed to its own stack

### `integration` — Add a first-class Source Reconciliation job and result schema between browser research and Mac planning. The relay submits a declarative comparison (entities, fields, source selectors, freshness limit); the browser harness and Mac agent each return field-level typed observations with stable artifact IDs, timestamps, and redacted evidence spans; a background comparator produces matches, conflicts, unknowns, and confidence. Persist only the normalized result plus encrypted short-lived evidence handles, expose GET /jobs/:jobId/reconciliation, and emit the result into the originating voice session. Do not route this through a generic free-form plan, which currently loses source identity and makes a claimed match unauditable.
- **owner gets:** They can ask one spoken question and receive an answer that distinguishes “same,” “conflict,” and “could not verify,” rather than trusting a model that silently blended a portal page, a Mac file, and a message.
- effort: Medium-high: new typed schemas and adapters in browserSessions/pageWatch and Mac artifact readers, comparator worker, encrypted evidence-handle store, and relay-session delivery; roughly 1–2 weeks for a robust first version.  ·  risk: A parser can align the wrong invoice or date, or stale browser data can look current. Every field must carry source, capture time, and confidence; ambiguous entity matches become unknown, never a match. If the worker fails, retain the source handles and allow retry without rereading or mutating anything.
- cost: One background comparison and optional OCR/vision pass per request; approximately $0.02–$0.15 depending on pages and attachments. Storage is small for normalized fields; encrypted evidence retention is the main cost.  ·  latency: Adds parallel source collection plus comparison, typically 10–20 seconds; relay can acknowledge immediately and deliver a concise completion event.
- security: Crosses the browser's authenticated boundary and local Mac data boundary, so enforce per-request source selectors, least-data extraction, encrypted short-lived evidence handles, audit receipts, and no cross-surface raw-content logging. Read-only initially.
- depends on: A durable background job runner or equivalent retryable execution for multi-source reads; A relay event/result delivery path to the originating voice session; Typed browser and Mac artifact extraction with stable IDs and timestamps; Redaction and retention primitives shared by browser and Mac adapters


## What it asked for

_Nothing._
## Its own summary

Recorded two owner-facing proposals. First, a cross-source reconciliation job that compares authenticated browser data with Mac documents/messages using field-level citations, timestamps, confidence, and explicit conflicts/unknowns; the missing work is the typed connective layer, durable background execution, redacted evidence handles, and voice-session result delivery. Second, a lost-pendant recovery capability that atomically revokes relay/browser/Mac access and supports secure re-pairing; it needs device identity, recovery-factor, fan-out revocation, and confirmation inventory. I did not perform further discovery per instruction.

**Biggest unknown:** Whether the device identity/revocation endpoints and recovery flow already exist on an unobserved relay surface; the proposal explicitly treats them as unverified rather than assuming absence.

