# Harness derivation — unified — round 213

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “show me the truth about that action,” give me one owner-readable timeline of what I asked, what the Mac/browser actually did, what the relay accepted, and whether the pendant delivered it—marking unknown instead of filling gaps."
- **useful because:** Today evidence is split across jobs, receipts, browser results, and audio delivery. This would stop the system from confidently claiming completion when only planning or relay acceptance occurred, especially after outages.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for assembly and mismatch analysis; realtime only for the short spoken summary
- **latency:** Under 3 seconds for a normal job; up to 10 seconds when browser and audio receipts must be joined.
- **cost:** Roughly $0.01–$0.05 per invocation; most cost is structured evidence retrieval, with a small background-model synthesis.
- **security:** Only expose evidence bound to the requested job/commitment and redact page contents, tokens, and sensitive parameters. Never infer success from absence of errors; require explicit receipts or say unknown. Browser evidence must remain target-bound.
- **missing:** A production cross-surface receipt join keyed by job/commitment ID across relay jobs, Mac receipts, browser command results, and audio delivery acknowledgements; A dashboard and spoken formatter for explicit unknown/mismatch states; A stable correlation field propagated into browser and pendant delivery events

### "When I say “handle this privately,” let the browser complete the task inside the bound logged-in tab while the relay and dashboard receive only a redacted outcome and a cryptographic receipt—not page text, screenshots, form values, or credentials."
- **useful because:** The system can currently act in authenticated browser sessions, but privacy depends on every downstream component behaving. This gives the owner a usable mode for banking, health, and private messages without making the AI blind to whether the action succeeded.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for policy validation and receipt summarization; deterministic local rules for redaction and routing
- **latency:** Normal browser action latency plus under 500 ms to issue the redacted receipt; no extra model round trip for each click.
- **cost:** Near-zero incremental model cost for deterministic redaction; $0.005–$0.02 when a background model summarizes the outcome.
- **security:** The browser extension must enforce an allowlisted tab/session binding and perform redaction before data leaves the Mac. No raw DOM, screenshots, typed values, or URL query secrets cross the relay. Irreversible actions still require the existing physical transaction approval latch. A fail-closed mode must abort if redaction cannot be proven.
- **missing:** Browser-side redaction and a signed local-only execution envelope; A relay schema for opaque private-action receipts and replay-safe correlation; A dashboard indicator proving private mode is active and what was intentionally withheld

### "Before you rely on anything you inferred about me, say “I found a possible memory,” show me the exact fact in plain language and where it came from, and let me keep, correct, or forget it from the pendant or dashboard."
- **useful because:** The owner explicitly cannot currently see extracted facts, although those facts can influence future behavior. This makes memory an opt-in, inspectable relationship rather than invisible profiling, while preserving the action audit trail.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** background model for candidate extraction and plain-language rendering; deterministic policy for consent, deletion, and provenance
- **latency:** Candidate notice within one conversation turn; review page under 2 seconds; deletion receipt within 5 seconds locally, with off-machine deletion reported as requested-and-pending.
- **cost:** About $0.01–$0.04 per candidate for extraction/rendering; negligible deterministic cost for review and erase.
- **security:** Show only the fact and minimum evidence needed for recognition, redact unrelated transcript/audio, and require an explicit keep/correct/forget decision. Forget must erase the fact, derived copies, and its evidence capsule, but not job history; relay replicas must return pending until confirmed.
- **missing:** Owner-facing list/detail/edit/delete routes for extracted facts with provenance; A consent state machine that prevents unreviewed candidates from entering active context; Cascading erase across facts.json, context graph, evidence capsules, and relay replicas; Pendant-friendly short rendering and a durable review queue

### "If my pendant disappears from the relay for longer than my chosen grace period, freeze queued browser/Mac actions, stop new audio delivery, and require a fresh physical presence signal before anything sensitive resumes; tell me exactly what was held."
- **useful because:** A lost pendant, dead battery, or stolen session should not leave an authenticated browser or queued action free to continue. This turns the wearable into a presence boundary rather than merely an audio endpoint.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic state machine; no model needed except an optional background explanation of held work
- **latency:** Freeze within one heartbeat timeout (configurable, default 60 seconds); resume acknowledgement under 2 seconds after the pendant reconnects and the owner confirms.
- **cost:** Negligible model cost; small relay heartbeat/storage overhead and one extra state check before dispatch.
- **security:** Fail closed for sensitive and irreversible work, but do not revoke unrelated Apple/browser sessions without explicit policy. Distinguish radio outage from deliberate privacy latch, record the reason, prevent stale reconnect replay with monotonic device counters, and never use presence as a substitute for the physical transaction approval latch.
- **missing:** Authenticated pendant presence heartbeats with monotonic counter and last-seen time; Relay/Mac/browser dispatch gate that holds and later revalidates queued work; A per-action sensitivity policy and owner-configurable grace period; A reconnect receipt proving held work was not executed while absent

### "For the next hour, let me put the whole system under a temporary operating contract—such as “draft only,” “never send messages,” or “never touch personal files”—and show me a receipt proving that the pendant, relay, Mac planner, and browser all enforced it until expiry."
- **useful because:** The owner currently has to trust that separate surfaces interpret safety preferences consistently. A temporary, owner-authored contract would make boundaries explicit during travel, meetings, sensitive work, or shared-screen situations, without permanently changing configuration.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic policy evaluation and enforcement; background model only parses natural-language policy into a reviewable typed contract.
- **latency:** Contract activation and propagation under 2 seconds; every action gate adds under 20 ms; expiry must be enforced locally even if the relay is unreachable.
- **cost:** Under $0.01 per contract for parsing and rendering; negligible recurring cost for deterministic checks.
- **security:** The contract must be signed or otherwise authenticated, versioned, scoped, and fail closed when a surface cannot verify it. Natural-language parsing must never silently broaden permissions. A physical pendant confirmation should be required for contracts that relax restrictions; expiry and revocation must work offline. Receipts must reveal enforcement state without exposing private page contents.
- **missing:** A shared typed policy-contract schema with deny-first semantics, scope, expiry, and version; A signed propagation and acknowledgement protocol across pendant, relay, Mac, and browser; Action-gate integration that evaluates the contract before planning and execution, not merely after; A convergence receipt and dashboard editor for active contracts

### "What information is leaving this Mac or pendant right now? Show me a live, plain-language egress ledger by destination and purpose, and let me block a category immediately without killing unrelated local work."
- **useful because:** The owner has privacy controls for capture and individual actions, but no way to see the aggregate boundary: audio, browser results, inferred facts, diagnostics, and credentials can cross different paths. A live egress view makes the system auditable while it is operating.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic event classification and byte/accounting; background model only translates technical destinations into plain language.
- **latency:** Visible updates within 1 second of an egress event; emergency category block applied within one heartbeat and locally enforced if disconnected.
- **cost:** Negligible model cost; bounded event journal and dashboard streaming are the main resource costs.
- **security:** The ledger must avoid copying the sensitive payload it describes, use destination allowlists and content-type labels, and fail closed for unclassified egress. Blocking must not corrupt in-flight transactions; report whether bytes were already sent. The ledger itself is sensitive and needs local redaction and bounded retention.
- **missing:** Instrumented egress accounting at pendant, relay, Mac, and browser boundaries; A shared taxonomy for audio, page data, credentials, memory, diagnostics, and action receipts; Per-category local kill switches with safe drain semantics; A tamper-evident but payload-free dashboard ledger

### "If the Mac, browser, relay, and pendant disagree about whether something happened, stop acting and ask me one concise conflict question with the competing evidence and the safest choices; do not silently pick a side."
- **useful because:** Distributed state can diverge after sleep, browser disconnects, or partial audio delivery. The owner currently gets either a confident answer or a low-level failure, not a bounded decision that prevents the wrong duplicate or omission.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic conflict detection and safe-choice generation; background model only compresses evidence into spoken language.
- **latency:** Detect on receipt reconciliation or reconnect within 3 seconds; speak the conflict in one turn; keep all affected actions paused until resolved or expired.
- **cost:** Under $0.01 per conflict for summarization; most cost is bounded evidence retrieval and durable state.
- **security:** Present provenance and timestamps, never fabricate a winner, and redact unrelated browser contents. Resolution must be scoped to the one disputed action, expire, and require physical confirmation for any irreversible choice. Preserve both evidence trails for audit.
- **missing:** A common event identity and causal ordering scheme across all four surfaces; Conflict classes and deterministic safe defaults; A durable owner decision record that unblocks only the affected action; Pendant-compatible short evidence cards and dashboard detail view


## What it asked for

_Nothing._
