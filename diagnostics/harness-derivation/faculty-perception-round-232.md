# Harness derivation — faculty-perception — round 232

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **safari-reading-list-observability** — The owner has repeatedly asked for the four latest Safari Reading List items and each attempt is recorded as failed; Safari is currently online with five tabs, but this does not establish that Reading List was inspected.
  - evidence: discover:owner said/asked_for_and_did_not_get plus discover:devices shows Safari on MacIntel online, 5 tabs

## Capabilities it proposed

### "“Did you actually check my Safari Reading List, or did it fail? If it failed, tell me exactly where and when.”"
- **useful because:** The owner has asked this repeatedly and received only failure. A trustworthy answer must distinguish empty Reading List, wrong surface (tabs/history), extension offline, permission failure, and an unattempted query. It would return an evidence matrix with attempted surface, freshness, result count, and a bounded reason—never turn missing data into “none.”
- **path:** browser-extension → mac-planner → relay-realtime → faculty-perception
- **model tier:** background for collection and normalization; realtime only to state the already-established result in one short sentence
- **latency:** Under 3 seconds when Safari heartbeat is fresh; otherwise return a staged status immediately and never wait longer than 5 seconds on a dead extension
- **cost:** Usually one cheap local route plus zero model calls; roughly <$0.01 per request, dominated by an optional short realtime explanation
- **security:** Reading List titles/URLs remain on the Mac/browser boundary; relay receives only counts, status, timestamps, and redacted failure reasons unless the owner explicitly asks for items. Any claim of “empty” requires a successful authenticated Reading List read and a freshness bound.
- **missing:** A first-class Safari Reading List read route (not just tab inspection); A typed result contract separating empty, unavailable, denied, stale, and failed; A perception reducer that records attempted surfaces and does not infer absence from a failed command

### "“Is any of your memory or context contradicting itself right now?”"
- **useful because:** The system currently injects a machine-originated America/Chicago preference at high confidence even though the Mac resolves to America/New_York. A perception pass should surface contradictions before judgement silently chooses one, showing source origin, authority scope, confidence, age, and the exact affected answers (routine times, quiet hours, file dates). This prevents a plausible but wrong answer from becoming the owner's reality.
- **path:** faculty-perception → mac-planner → relay-realtime → unified
- **model tier:** background deterministic rule engine; realtime only summarizes a detected conflict
- **latency:** Under 500 ms from the local memory projection and machine context; no external model call required
- **cost:** Near-zero API cost; bounded JSON reads and deterministic comparison dominate
- **security:** Do not expose secret fact values in relay logs or spoken output. Only emit key, provenance, authority scope, and a redacted conflict summary. Never auto-delete or rewrite owner facts; require explicit owner action to resolve.
- **missing:** A contradiction endpoint that joins memory projection provenance with authoritative machine facts; Authority rules for machine-resolved versus owner-declared preferences; A durable, dismissible conflict record with affected-answer links

### "“Give me the research brief, and show me which source text you actually read and whether it is still trustworthy.”"
- **useful because:** Scheduled research can currently turn relay-fetched page text into an announcement with no URL, hash, or durable capsule, while the Mac already has a strong evidence-capsule schema. This capability would let perception establish source identity and freshness before judgement summarizes it, and tell the owner when a cited page was unavailable or changed instead of presenting orphaned prose as research.
- **path:** relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement
- **model tier:** background model for summarization only after deterministic provenance checks; realtime only for a spoken summary
- **latency:** Research may take minutes asynchronously; provenance receipt should be available within 2 seconds after each page read
- **cost:** One cheap hash/capsule operation per page; model cost only for the requested summary, typically <$0.05 per brief
- **security:** Redact secrets and private page regions before leaving Safari. Public relay reads remain untrusted. Keep source URL, capture time, content hash, and capsule ID; do not persist raw relay page text indefinitely. Owner confirmation is required before sharing private-page excerpts.
- **missing:** Relay read response must return a stable request/capsule correlation ID and content hash; A Mac call that stores relay results in the existing evidence-capsule and browser-provenance stores; Routine/announcement records must carry source references rather than only speech text; A freshness policy that marks changed, expired, revoked, and uncapsuled sources

### "“Replay what the system knew when it answered me yesterday—not what it knows now—and show me which facts were observations, which were assumptions, and which were unavailable.”"
- **useful because:** Today a later inspection cannot distinguish a true historical observation from a value inferred after the fact. An epistemic replay would let the owner audit a consequential answer without trusting the system’s current memory: reconstruct the exact time-bounded perception frontier across Mac, browser, relay, and (when present) pendant, then label every premise observed, stale, inferred, contradicted, or missing.
- **path:** faculty-perception → relay-realtime → mac-planner → browser-extension → unified → faculty-judgement
- **model tier:** Deterministic event reconstruction first; use the background model only to render a concise explanation. Realtime is optional for spoken delivery.
- **latency:** A bounded replay should return in under 5 seconds for a single turn and under 20 seconds for a day; partial results must explicitly identify missing event sources.
- **cost:** Low API cost for indexed event reads; storage/indexing is the dominant cost. Model cost is only a short explanation, typically under $0.02.
- **security:** Historical snapshots can contain private browser content, messages, and secrets. Keep raw evidence local, redact sensitive values in cross-surface indexes, enforce per-owner authorization, and make the replay immutable so a later correction cannot rewrite history. Require confirmation before exposing secret-bearing evidence.
- **missing:** An append-only, clock-synchronized observation journal shared by relay, Mac, browser, and pendant, with monotonic sequence plus wall-clock uncertainty; Per-turn links from perception inputs to judgement outputs and action/job IDs; A replay API that returns evidence availability and uncertainty rather than silently filling gaps; Retention and redaction rules for historical observations

### "“When two parts of you disagree, run the smallest safe check that could tell which one is true, then report the result and what remains unknown.”"
- **useful because:** A contradiction report alone leaves the owner to arbitrate. This capability turns uncertainty into a bounded experiment: for example, compare the Mac’s authoritative timezone against the stale memory preference, verify Safari’s actual Reading List surface rather than infer from tabs, or test relay reachability before claiming a pendant delivery. It prevents confident answers based on whichever source happened to win sorting.
- **path:** faculty-perception → mac-planner → browser-extension → relay-realtime → faculty-judgement → faculty-action
- **model tier:** Deterministic policy selects a read-only discriminator; a cheap background model may explain competing hypotheses. Realtime is used only if the owner must approve a check that touches private data or causes a side effect.
- **latency:** Read-only checks under 3 seconds; if no safe discriminator exists, return the competing hypotheses and explicit unknown rather than guessing.
- **cost:** Near-zero model/API cost for local checks; occasional browser or relay read is the dominant cost.
- **security:** The experiment planner must be read-only by default and scope-limited to the disputed fact. Never send test messages, mutate browser state, or reveal private content merely to resolve uncertainty. Keep the chosen test and its scope in the receipt so the owner can see what was not tested.
- **missing:** A typed hypothesis/discriminator contract linking a disputed claim to permissible observations; A policy engine that chooses the least-privilege read and stops after a bounded attempt; Cross-surface result comparison with freshness and authority metadata; An owner-facing receipt containing hypotheses, selected check, result, and residual uncertainty

### "“Which parts of you have been wrong lately, and how should that change how much I trust the next answer?”"
- **useful because:** The system exposes confidence and provenance but not calibration. The owner cannot currently see that a browser bridge was stale, a relay ‘delivered’ state only meant socket bytes, or a machine-derived preference contradicted the authoritative clock. A source-calibration view would measure claims against later verified outcomes, report false-positive/false-negative rates by surface and claim type, and lower trust in a source without silently rewriting facts.
- **path:** faculty-perception → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Background deterministic aggregation over resolved observations; use a cheap model only to explain trends, never to assign the scores.
- **latency:** Under 2 seconds for a 30-day source report; each new verified outcome updates metrics asynchronously.
- **cost:** Minimal API cost; bounded local aggregation and compact counters dominate. No model call needed for the core result.
- **security:** Do not turn private content into a global reputation score. Store claim-type and surface identifiers, timestamps, and outcome classes—not raw page text or message contents. Make the calibration explainable, reversible, and visible before it affects trust.
- **missing:** A claim ledger with predicted state, confidence, source, freshness, and later verification outcome; Outcome joins from browser receipts, Mac action receipts, relay delivery boundaries, and device playback acknowledgements; A calibration algorithm that handles censored outcomes (unknown is not failure); An owner-facing report and policy hook that can lower confidence without deleting evidence


## What it asked for

_Nothing._
## Its own summary

Established a fresh fact: Safari is online with five tabs, but the owner’s repeated “four latest Safari Reading List items” requests are recorded as failed; that does not prove the Reading List was empty or even inspected. I recorded this distinction. I proposed three non-duplicate capabilities: (1) a typed negative-result verifier that says empty vs unavailable vs denied vs stale, (2) a contradiction detector that catches machine-originated preferences overriding authoritative machine facts, and (3) provenance/freshness-aware research that exposes which source was actually read. I also tested a relay-capsule integration change; the recorder correctly rejected it as an existing backlog item, so I did not rephrase it.

**Biggest unknown:** The live inventory still lacks a first-class authenticated Safari Reading List reader and typed failure contract. Until that exists, perception cannot honestly answer the owner’s repeated Reading List question. I also still need the existing relay provenance bridge to be wired end-to-end, but that is already known backlog rather than a new proposal.

