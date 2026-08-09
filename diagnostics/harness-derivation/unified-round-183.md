# Harness derivation — unified — round 183

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live cross-surface state** — Mac agent and Safari browser bridge are online. GET /context-graph is live and contains extracted Note/EmailDraft entities with stable IDs, while the granted incident_diagnostics, privacy_convergence_check, and commitment_evidence_query schemas currently describe as unresolved rather than callable implementations.
  - evidence: GET /health 200; GET /context-graph 200 with entities; GET /browser/status 200 online=true; describe(...) reports each granted diagnostic/query tool unresolved.

## Capabilities it proposed

### "“Show me every fact you inferred about me, where each came from, and forget the ones I choose.”"
- **useful because:** The system currently extracts facts into hidden stores the owner cannot inspect. This directly implements the owner's retention rule: extracted facts are either individually listable and erasable, or should not exist. It preserves job history while removing the fact, derived copies, and evidence capsule, and reports off-machine deletion as pending rather than falsely claiming completion.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** background for indexing and deletion planning; realtime only to resolve a spoken fact reference and confirm the exact item
- **latency:** List in under 2 s from Mac/relay caches; deletion acknowledgement under 3 s locally, with replicated erase status updated asynchronously
- **cost:** Low: one deterministic graph/store query and usually no model call; occasional small background extraction/index update dominates
- **security:** Show provenance without exposing unrelated conversation or raw audio. Require exact item selection and confirmation before deletion; never delete job audit history. Redact evidence by default and surface only the minimum excerpt needed for recognition.
- **missing:** A unified facts projection over facts.json and context-graph with stable fact IDs and provenance capsules; DELETE propagation to derived copies and relay replicas, with requested-and-pending state; A dashboard/voice list view that lets the owner recognize one fact before erasing it

### "“Stage this browser action, tell me exactly what will happen, and let my pendant's physical approval release it—even if the Mac or link drops.”"
- **useful because:** This closes the most dangerous user-facing lie in the current system: blocked plans say they are waiting for approval, but no dashboard or relay loop can actually resume them. The pendant's deliberate approval becomes a real cross-surface boundary: browser contents stay on the browser, the relay holds a bound transaction, the owner approves a nonce on the pendant, and execution happens once with receipts or expires safely.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** realtime for concise spoken summary and disambiguation; deterministic code for digest, expiry, nonce, world recheck, and execution
- **latency:** Stage/preview under 2 s; after button approval, release within 5 s when Mac/browser are online; link loss leaves a durable pending decision with no execution
- **cost:** Low per action: mostly hashing, lease and receipt writes; model cost is a short preview sentence only
- **security:** Bind approval to plan digest, browser target, world fingerprint, expiry and nonce. Do not send page secrets to the pendant. Reject changed pages, replayed counters, expired approvals, and duplicate execution. Use a distinct approval credential if possible; the current shared bearer token is not privilege separation.
- **missing:** Implement the relay half of the approval handoff and durable action lease; Connect physical_transaction_approval_latch events to pending approvals and the next conversation (the pendant cannot receive an unsolicited prompt today); Add an actual dashboard pending/approve/status view and close ordinary ledgers correctly; Add relay job lease expiry/requeue before attempting recovery

### "“Tell me whether the last answer was actually heard, and if not, recover it without making me repeat myself.”"
- **useful because:** A relay accepting audio is not the same as the owner hearing it. This gives the owner one honest answer grounded in the pendant/bridge's playback start, finish, interruption, checksum and link state, then offers a bounded replay or text fallback. It is especially valuable during the currently real USB-attached, LTE-unregistered phase and during simultaneous uplink/downlink loss.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → dashboard
- **model tier:** deterministic receipt correlation first; background model only to summarize a failure; realtime only for the owner's immediate spoken question
- **latency:** Answer from cached receipts in under 500 ms; recovery begins within 2 s; never block the active conversation on a diagnostic probe
- **cost:** Very low: bounded receipt lookup and state machine; model invocation is optional and only for human-friendly explanation
- **security:** Use opaque artifact IDs and checksums, not audio content, in routine receipts. Replay requires the same conversation/owner binding and must not duplicate an action. Do not retain audio beyond existing failure-buffer policy; distinguish delivered-to-bridge from physically-started playback.
- **missing:** A consumer/orchestrator for the existing audio_delivery_ack_queue rather than raw counters only; A cross-surface receipt join keyed by artifact ID across relay, USB/LTE transport, ESP32 bridge and pendant; A bounded replay command with idempotency and an explicit owner confirmation when replay could interrupt live speech

### "“For this request, confine the agent to this one browser tab and these exact fields; prove afterward that nothing else was touched.”"
- **useful because:** The owner can currently bind evidence queries to targets, but action execution is not a true capability sandbox. This would make least privilege tangible: a browser task receives a short-lived, target-scoped capability token, rejects navigation or typing outside the declared tab/field set, and returns a tamper-evident scope receipt. It prevents a helpful-looking automation from wandering into another logged-in account or tab.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** deterministic policy and receipt enforcement; realtime model only translates the spoken scope into a preview
- **latency:** Scope preview under 1 s; each browser command adds under 50 ms for token/scope validation; final receipt immediately after completion
- **cost:** Low: signed token checks and bounded receipts dominate; no model call for enforcement
- **security:** Tokens must include tab/session identity, allowed URL pattern, DOM/field selectors, verbs, expiry, nonce and plan digest. Fail closed on navigation, frame changes, stale snapshots or selector ambiguity. Never put page secrets in the pendant receipt. Physical approval can authorize the scoped token but must not widen it.
- **missing:** Browser extension enforcement of scope on every command, not only planner intent; Relay-issued short-lived capability tokens and a verifiable scope receipt; Dashboard rendering of touched targets and rejected out-of-scope attempts

### "“Why did you do that? Show me the short, redacted chain from what I said to the action, what changed, and what evidence proves the result.”"
- **useful because:** Today the owner can inspect separate jobs, journals, browser results and pipeline records, but cannot get one causal explanation. A cross-surface explanation would make the system accountable without exposing an entire transcript: utterance reference → interpreted intent → selected plan → approvals → concrete Mac/browser effects → verification and audio delivery. It would also say when evidence is missing instead of inventing success.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** deterministic event correlation and redaction first; a cheaper background model compresses the already-redacted chain into speech
- **latency:** Cached explanation under 1 s; cold correlation under 3 s; never delay an action to generate prose
- **cost:** Low-to-moderate: event joins are cheap, with a small summarization call only when the owner asks for spoken detail
- **security:** Use opaque IDs and minimum necessary excerpts. Keep action audit history even if a remembered fact is erased. Distinguish intent, attempted action, completed action and independently verified outcome; never treat relay acceptance as proof of browser or playback success.
- **missing:** A stable correlation ID propagated from utterance/session through plan, execution, browser commands and audio receipts; Read-only join endpoint with redaction and explicit missing-evidence states; Owner-facing timeline view and spoken summarizer

### "“For the next conversation, keep this topic on the Mac and pendant; do not send its text, audio, or page contents to the relay or browser, and prove the boundary held.”"
- **useful because:** The existing privacy latch stops capture and playback, but it cannot express a deliberate, temporary data-routing boundary while the owner still wants to talk. This capability lets the owner choose local-only, relay-allowed, or browser-allowed handling per conversation, enforces it before capture/planning, and produces a receipt listing what stayed local and what was blocked. It is useful for confidential work without requiring the owner to stop using the pendant.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** deterministic routing gate; realtime model handles the owner's short spoken policy request, never the protected content when local-only is active
- **latency:** Policy takes effect before the next capture frame; routing decision under 100 ms; boundary receipt under 2 s after the turn
- **cost:** Very low during use: policy checks and metadata receipts; local-only may require a local model or a clearly announced degraded mode
- **security:** Fail closed if the local path is unavailable. Do not claim local-only if telemetry, retries, crash logs or browser commands can carry content. Encrypt and minimize the boundary receipt; make expiry explicit; require a deliberate reset to broaden scope. This is separate from the physical privacy latch: it protects data destinations, not microphone state.
- **missing:** A pre-capture/pre-plan routing gate that all audio, text, browser and retry paths consult; A local-only execution/model path or an honest refusal when it is unavailable; Signed cross-surface boundary receipts and a dashboard audit view


## What it asked for

_Nothing._
## Its own summary

I discovered the live state and recorded three distinct capabilities. (1) An owner-facing extracted-fact cabinet: list inferred facts with provenance and individually erase the fact, derived copies, and evidence while preserving job audit history. (2) A real staged browser approval flow using the pendant's physical transaction latch; this was recorded as connective work, with the warning that the existing plan/execute/browser routes are only pieces and the relay/dashboard loop is absent. (3) An honest “did I hear that?” recovery flow based on playback receipts, with bounded replay or text fallback. Live checks show the Mac agent, context graph, and Safari bridge are online. The context graph already contains extracted Note and EmailDraft entities with stable IDs, making the first capability immediately concrete.

**Biggest unknown:** The most important remaining gap is not another proposal: several granted schemas are not actually callable. incident_diagnostics, privacy_convergence_check, and commitment_evidence_query all describe as unresolved, despite being intended as live tools. The implementation work still needed is: a facts projection plus deletion cascade; relay persistence/delivery for approvals and a dashboard pending state; and a receipt consumer/join for physical playback. The owner does not need to decide more for these proposals, but the system needs those missing implementations before it can honestly promise them.

