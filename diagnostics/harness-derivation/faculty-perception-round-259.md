# Harness derivation — faculty-perception — round 259

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **device-registry** — Current device discovery lists nrf9160-pendant as registered but offline, last seen 2026-08-09T02:56:31.366Z; home-macbook-bridge and ios-brain-prod-probe are online. This is stale registration, not proof of a physically connected/live pendant.
  - evidence: discover(category=devices) live response in round 259; Mac GET /v1/devices/status separately returned 404 because the registry route is relay-side.

## Capabilities it proposed

### "“Did anything private from my browser, phone, or voice get copied into the relay or spoken aloud—and what exactly crossed the boundary?”"
- **useful because:** Today a relay browser read can be inserted into an announcement and retained indefinitely without a URL, hash, or provenance, while a Mac capsule may exist separately. This gives the owner a concrete outbound-data report: content class, destination surface, timestamp, retention state, and whether the record is traceable or an uninstrumented blind spot.
- **path:** browser → mac → relay → iOS → pendant
- **model tier:** Use deterministic redaction/classification and joins first; a cheaper background model summarizes only the already-redacted event graph. Realtime is unnecessary except for a short spoken alert when sensitive content is detected.
- **latency:** A post-hoc report in under 3 seconds from local ledgers; a live pre-speech warning in under 500 ms from the relay announcement path. If provenance is absent, warn immediately rather than waiting for classification.
- **cost:** $0.001–$0.01 per report; most work is local hashing, provenance joins, and bounded classification, with model cost only for ambiguous content.
- **security:** Never copy the suspected secret into the report or send it to a model unnecessarily. Hash/redact locally, expose only domain/field class and a short safe label, and require owner confirmation before any sensitive relay announcement or pendant playback. Existing announcements can already be permanent despite a nominal 6-hour TTL, so the report must say retention is unknown/indefinite unless deletion is verified.
- **missing:** A relay-side provenance record containing a stable read ID, content hash, source URL, and destination announcement/job ID; A Mac call site that imports that relay provenance into the existing evidence capsule and browserProvenance stores; A read-only announcement/audit route exposing actual stored speech metadata and retention/deletion state; A pre-send sensitivity gate on relay announcements and pendant speech; Mounting the existing browserProvenance routes, which are currently uncalled

### "“Is every surface still acting as me, or did a browser tab, iPhone mirror, Mac bridge, or relay switch accounts or lose its trusted session?”"
- **useful because:** A task can be technically successful while targeting the wrong account. The system currently has browser sessions, iOS probes, a Mac bridge, and relay device credentials but no owner-facing identity continuity check. This would catch silent account drift, login-wall substitutions, revoked sessions, and a newly registered device before an action or announcement reaches the wrong place.
- **path:** browser → iOS → mac → relay → pendant
- **model tier:** Deterministic extraction and comparison of non-secret identity labels (domain, account display label, session pseudonym, device credential fingerprint) should do the work. A cheap background model can explain changes; realtime only speaks a high-severity warning.
- **latency:** Cached baseline check under 300 ms; refresh browser/iOS/Mac checks within 3 seconds. A changed identity must fail closed for consequential actions, not wait for a model.
- **cost:** Under $0.005 per check when labels are cached; browser and iOS refreshes dominate latency, not token cost.
- **security:** Never expose cookies, tokens, email addresses, or full account identifiers; compare salted local pseudonyms and return only a safe label such as “same Google workspace” or “account changed.” Baselines require explicit owner approval, and a relay credential/device change must be treated as suspicious rather than auto-accepted.
- **missing:** A privacy-preserving identity-label contract for browser extension, iOS mirror, Mac bridge, relay, and pendant; Read-only iOS visible-account/session reporting through the Mac harness; Relay credential/device-change events and a durable trusted-device baseline; Owner approval and recovery flow for establishing or replacing a baseline; Freshness and login-wall markers from browser reads, not just page text

### "“Are the timestamps across my Mac, relay, browser, phone mirror, and pendant actually comparable, or could this ‘latest’ event be stale or from the wrong clock?”"
- **useful because:** Perception currently mixes Mac wall time, relay timestamps, browser event times, and a pendant clock with no timezone/NITZ. That makes ‘this morning,’ freshness, and causal ordering unreliable exactly when the owner asks what happened. This capability reports clock offset/uncertainty and refuses to order events when the evidence cannot support it, instead of silently borrowing America/New_York for a device timestamp.
- **path:** pendant → relay → mac → browser → iOS
- **model tier:** No model is needed for offset estimation, monotonic sequence checks, and interval arithmetic. Use a cheap model only to explain a disputed timeline in owner language; realtime is optional for the spoken explanation.
- **latency:** Under 500 ms from cached heartbeats; under 3 seconds when collecting fresh relay, Mac, browser, and iOS samples. A stale/unsynchronized result should be immediate and useful.
- **cost:** Near-zero API cost; local arithmetic and bounded route reads dominate. Explanation adds roughly $0.001–$0.005.
- **security:** Do not infer the owner's physical timezone from the Mac zone. Preserve each source's clock provenance, monotonic sequence, and uncertainty interval. A future pendant beacon must be authenticated and replay-resistant; otherwise an old frame could look current.
- **missing:** Authenticated relay time samples and a server-issued monotonic/UTC reference; Pendant beacon frames carrying boot/session ID, monotonic time, and last relay acknowledgment (the accepted offline-reality-beacon is the hardware basis); Browser and iOS event timestamps normalized with source timezone/monotonic capture time; A shared interval-based event schema and a rule that blocks causal claims when intervals overlap or clocks are stale

### "“Find every place this fact is duplicated, show me which copy is authoritative, and—only after I approve—correct or retire the stale copies everywhere.”"
- **useful because:** The system already demonstrated a dangerous failure mode: a machine-originated America/Chicago preference is pinned at high confidence and injected into every context projection despite the Mac actually being America/New_York. The owner needs correction propagation, not merely another warning. This would locate contradictory facts across memory, relay state, browser provenance, routine configuration, and device snapshots, preserve the original provenance, and apply one owner-approved correction without silently rewriting history.
- **path:** mac → relay → browser → iOS → pendant
- **model tier:** Deterministic key/provenance/entity matching should find candidate duplicates and contradictions. A cheap model may group aliases and explain impact; realtime is only for asking the owner to approve a consequential correction.
- **latency:** Produce an impact report in under 3 seconds for cached stores; apply an approved correction atomically within 5 seconds. Never auto-correct a fact whose source is owner-authored or whose authority is ambiguous.
- **cost:** Roughly $0.005–$0.02 per investigation, mostly a bounded model call for entity matching; writes and provenance joins are local or relay calls.
- **security:** Correction must be append-only or tombstone-based, with before/after values, source, approver, and affected projections. Do not propagate a correction into a device or external account without explicit confirmation. Machine-derived facts must never outrank owner-authored facts merely because they have higher confidence or use count.
- **missing:** A cross-surface fact identity and authority contract; Read/write APIs for memory, relay state, routines, browser provenance, and device snapshots with per-field provenance; An owner approval transaction and append-only correction ledger; A projection invalidation/rebuild mechanism after correction; A safe preview showing every affected prompt, routine, and pending announcement

### "“When something goes wrong or contradicts itself, freeze the smallest useful forensic record so you can later tell me what happened—even if the normal logs or queues have already rolled over.”"
- **useful because:** Today the important evidence is fragmented across count-capped Mac traces, short-lived relay jobs, browser spool records, and device telemetry that may not exist. A near-miss can therefore disappear before anyone investigates. An automatic, redacted incident bundle would preserve the causal edges—source observations, timestamps, session/device IDs, action receipt, browser capsule links, and the exact unknowns—without recording ordinary private conversation.
- **path:** pendant → relay → mac → browser → iOS
- **model tier:** Use deterministic triggers for contradictions, stale acknowledgements, permission changes, packet-quality failures, and unexpected device/session changes. A cheaper background model summarizes only the redacted bundle; realtime should not be spent unless the owner asks for an explanation.
- **latency:** Capture the bundle synchronously in under 200 ms at the triggering surface; make it queryable within 1 second. Summarization can take seconds in the background and must not delay the owner's action.
- **cost:** Under $0.01 per incident, dominated by optional summarization. Storage should be bounded by a small encrypted ring with explicit owner retention controls.
- **security:** Default to metadata, hashes, redacted snippets, and provenance links—not raw audio, page text, tokens, or screenshots. Encrypt at rest, bind records to a boot/session and relay correlation ID, and make export/deletion visible. Incidents involving a potentially compromised session should be isolated from the compromised surface.
- **missing:** A cross-surface incident schema and correlation ID; A durable encrypted ring independent of the count-capped pipeline/job stores; Trigger hooks for contradiction, stale delivery, capture degradation, permission drift, and device registration changes; A redaction/classification policy that runs before persistence; An owner-facing incident browser with evidence confidence and retention controls

### "“Put the whole hive into a verifiable private mode for the next conversation: prove what stays on the pendant/Mac, block relay/browser/iOS transmission, and tell me exactly what will be discarded or queued.”"
- **useful because:** The owner cannot currently obtain a trustworthy local-only conversation boundary. A browser read can be unproven and relay announcements can persist indefinitely; disabling one route does not prove that another surface did not transmit. A coordinated private mode would make sensitive conversations usable in practice, with a preflight attestation and a post-session transmission audit rather than a vague privacy promise.
- **path:** pendant → relay → mac → browser → iOS
- **model tier:** No model is needed for enforcement or attestation. Use realtime only for the owner's voice interaction after the mode is proven active; a cheap background process can produce the post-session audit.
- **latency:** Preflight under 1 second when all surfaces are online; under 3 seconds if a device must be checked. If any surface cannot attest, private mode must fail closed or clearly downgrade to “best effort,” never silently proceed.
- **cost:** Near-zero inference cost; implementation cost is protocol and policy work. Optional audit summarization is under $0.005 per session.
- **security:** A claim of privacy is itself sensitive and must be backed by signed enforcement state: relay routes disabled, browser commands blocked, iOS actions blocked, audio retention disabled, and local stores bounded. Handle offline reconnection explicitly so queued data cannot leak later without consent. The owner must be able to inspect and revoke the mode.
- **missing:** A signed privacy-mode contract understood by pendant firmware, Mac agent, relay, browser extension, and iOS harness; Fail-closed transmission gates at every outbound route, including queued announcements and retry queues; A local-only speech/model path or an explicit statement that local-only speech is unavailable; Post-session network and storage audit with deletion verification; Owner-visible mode state and an explicit confirmation before leaving private mode


## What it asked for

_Nothing._
