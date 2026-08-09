# Harness derivation — unified — round 234

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Before you tell me a result, prove which parts actually happened: the Mac action, the browser change, and what the pendant physically played.”"
- **useful because:** A successful relay receipt is not proof that a browser command ran, and a delivered audio artifact is not proof that it was heard. This owner-facing proof chain joins action receipts, browser result receipts, pipeline timing, and device playback acknowledgements into one honest answer with explicit unknowns.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background deterministic joiner for receipts; realtime model only summarizes the already-correlated evidence in natural language
- **latency:** Join available evidence in under 1 s; wait up to 10 s for late browser/device receipts, then answer with a timeout and missing leg
- **cost:** <$0.003 per query; retention/indexing of compact receipts dominates
- **security:** Correlate by opaque job/artifact IDs, not page contents or audio text. Bind browser evidence to explicit tab/session targets. Never upgrade relay acceptance to completion when a physical acknowledgement is absent; preserve an audit trail and redact sensitive parameters.
- **missing:** A typed cross-surface receipt join keyed by jobId/artifactId; A durable late-receipt correlator for browser and pendant events; Owner-facing status vocabulary separating accepted, executed, delivered, started, finished, interrupted, and unknown

### "“Show me exactly what you would change in my logged-in browser and Mac, let me inspect it, then let me approve only that frozen plan with the pendant.”"
- **useful because:** The live blocked-plan path says it is waiting for approval, but no dashboard control or connected approval loop can complete it. This gives the owner a real preview-before-action boundary for browser and Mac side effects, with a frozen world/plan digest and a physical confirmation that cannot silently approve a changed plan.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic planner/approval verifier for diff, digest, expiry, and risk; background model may draft the explanation but never grant execution
- **latency:** Preview in under 3 s; owner can inspect asynchronously; after physical approval begin only the frozen plan within 2 s
- **cost:** <$0.01 per preview; browser snapshots and world fingerprints dominate
- **security:** Redact secrets and page contents in previews; bind browser actions to explicit tab/session targets; include riskTier, replaySafety, touched paths, and irreversible reason. Approval expires, is one-shot, and refuses on plan/world drift. Pendant receives only opaque nonce and status.
- **missing:** A dashboard preview renderer for blocked plans; A relay-backed implementation of APPROVAL_STORE_CONTRACT and delivery/readback state; A route that binds browser/Mac plan digests to the staged transaction and physical nonce; Separate approval and execution credentials or an explicit owner decision that the current bearer token is sufficient

### "“Before you send anything outside this Mac, tell me what personal facts or files it would expose, remove anything unnecessary, and make me approve the final payload on the pendant.”"
- **useful because:** The system can act through logged-in browser sessions and Mac apps, but current planning treats an action as safe/unsafe without a concrete data-egress inventory. This creates a user-visible privacy boundary at the moment information leaves the machine, rather than relying on broad app trust or a retrospective receipt.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic taint/provenance scanner for files, extracted facts, clipboard, form fields, and recipients; background model only classifies ambiguous text and must defer to the owner
- **latency:** Inventory in under 2 s for ordinary forms/messages; approval remains valid for 10 min only if recipient, payload digest, and page world fingerprint stay unchanged
- **cost:** <$0.02 per outbound action; local content hashing and browser snapshots dominate, with model calls only for ambiguous classification
- **security:** Scanning stays local where possible; relay sees hashes and redacted labels, not payload contents. Never auto-redact legal/financial content without showing the exact diff. Physical approval is nonce-bound, one-shot, and refuses on any payload or recipient change.
- **missing:** A taint/provenance index linking extracted facts and local files to outgoing fields; Browser and Mac action adapters that expose a canonical payload before submission; A redaction editor and digest-bound approval record; Policy values for categories the owner always blocks versus always allows

### "“Before you let a logged-in site act as me, prove that this is my browser session, my Mac, and my pendant—not just somebody holding the bearer token.”"
- **useful because:** Today the relay, Mac agent, and browser actions share bearer-token authority, while the pendant is not cryptographically part of the authorization decision. The owner cannot distinguish a genuine action through their live browser session from token replay or a stale extension. A hardware-bound session attestation would make the wearable a real identity witness rather than only an audio endpoint.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic cryptographic verifier and policy engine; no language model should decide whether attestation is valid
- **latency:** Establish or refresh a session in under 1 s; re-attest only on browser-session change, relay reconnect, or high-risk action
- **cost:** Under $0.001 per verification; key provisioning, nonce exchange, and storage dominate rather than model inference
- **security:** Use per-device asymmetric keys in protected pendant storage, Mac bridge key binding, browser-extension challenge responses, short-lived relay session certificates, nonce replay protection, and explicit revocation. Never expose private keys or page contents to the relay. If the pendant is offline, degrade to read-only rather than silently treating the bearer token as equivalent.
- **missing:** A browser_identity_attestation capability that returns a signed session/device statement; Hardware-backed pendant key provisioning and rotation; A relay session-certificate verifier that binds pendant, Mac bridge, browser tab/session, and owner-approved scope; Authorization middleware that rejects or downgrades un-attested browser/Mac mutations; A recovery ceremony for replacing a lost pendant without weakening the security boundary


## What it asked for

_Nothing._
## Its own summary

This round recorded three new owner-facing capabilities: (1) a cross-surface proof chain that distinguishes relay acceptance, Mac/browser execution, and physical playback; (2) a frozen preview→pendant approval flow for browser/Mac side effects; and (3) a data-egress guard that inventories facts/files before anything leaves the Mac and requires nonce-bound physical approval. The memory-review and generic resume versions collided with existing backlog and were not restated. Live discovery also exposed an important implementation uncertainty: describing POST /browser/inspect, POST /prepare, and POST /approve produced GET 404 responses, so those routes must be verified as actually mounted before being named dependencies.

**Biggest unknown:** Whether the approval/inspection routes are truly mounted POST handlers (the route inventory says yes, but live describe probes issued GET and returned 404), and which external-data categories the owner wants always blocked, always allowed, or individually approved. The pendant remains absent from live device discovery; the Mac bridge and browser are online.

