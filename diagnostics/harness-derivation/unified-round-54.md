# Harness derivation — unified — round 54

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **current connectivity** — Mac bridge is online, but home-chrome browser extension is offline with 4 pending browser commands; the relay reports LTE-M half-duplex contention and current audio path is 15.625 kHz capture with 24 kHz playback.
  - evidence: get_hardware_spec(all); discover(devices); GET /browser/status

## Capabilities it proposed

### "During a meeting, quietly keep me oriented: use the meeting on my Mac and my logged-in calendar/browser context to surface only critical facts or unanswered questions on the pendant, then leave me a sourced action-item brief and draft follow-ups when it ends."
- **useful because:** The pendant is the only surface that can give a discreet cue without making the owner look away, while the Mac can observe the meeting and the browser can reach private agenda/docs. The relay can preserve a resumable, timestamped record if either machine disconnects. This turns scattered meeting preparation and post-meeting notes into one end-to-end aid.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** background for rolling transcript segmentation and post-meeting synthesis; planner for cross-source reconciliation; realtime only for an owner interruption or spoken question. Deterministic rules handle meeting detection, redaction, and alert thresholds.
- **latency:** Critical cue under 2 seconds from detected event; ordinary fact lookup under 5 seconds; final brief within 60 seconds after meeting. Buffer locally on Mac and relay checkpoints so a link drop does not lose the session.
- **cost:** Roughly $0.05–$0.30 per 60-minute meeting depending on audio transcription volume and planner escalation; realtime spend is reserved for explicit interruptions. Storage and egress dominate long meetings.
- **security:** Meeting audio and private calendar/browser content are sensitive and must remain local by default, with only redacted snippets or owner-approved windows leaving the Mac. Never record or transmit until an explicit meeting-session gesture/command; show a visible Mac indicator and provide one-tap stop. Drafts require review and sending remains confirmation-gated. Sourced evidence and deletion controls are mandatory.
- **missing:** A consent-gated meeting capture mode with local redaction and retention policy; Mac audio/window capture and timestamped transcript segments; A relay checkpoint stream that can resume across Mac/browser disconnects; Browser extraction bound to the calendar event and its approved tabs; A pendant notification protocol with urgency levels, haptic/LED/audio policy, and quiet-hours handling; Post-meeting action-item and draft-follow-up workbench with source timestamps

### "Answer private questions without exposing my private data: for example, tell me whether I have any appointment conflicts or whether an account message needs action, but return only the minimum answer and never send the underlying mail, calendar, file, or page contents to the relay, spoken audio, logs, or another surface."
- **useful because:** Today the system can reach private browser and Mac data, but it lacks a trustworthy minimum-disclosure mode. The owner should be able to ask sensitive yes/no or small-result questions from the pendant without turning the assistant into a pipeline that copies entire private pages or messages across nodes.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action → dashboard-ux
- **model tier:** Deterministic local evaluators and typed predicates for the common cases; a background model may classify or reconcile locally retained snippets on the Mac. Realtime is used only to speak the minimal result or ask for clarification.
- **latency:** Common checks under 5 seconds; multi-source checks under 15 seconds. The answer must remain useful if the browser or relay disconnects, with the Mac returning a signed minimal result when available.
- **cost:** Usually near-zero model cost for deterministic predicates; approximately $0.01–$0.05 for an ambiguous local classification. The dominant cost is private-source extraction and local indexing, not generation.
- **security:** Raw values must stay on their source device by default. Each request needs a typed predicate, purpose, sensitivity ceiling, and expiry; source adapters return only a boolean, count bucket, bounded date range, or redacted citation. The relay must reject free-form raw extraction, spoken output must obey the same ceiling, and every result needs an audit receipt and revocation/deletion path. Any action such as sending or changing data still requires the existing confirmation policy.
- **missing:** A predicate/minimum-disclosure query protocol understood by Mac and browser adapters; On-device or Mac-local evaluators for calendar, mail, files, and authenticated pages; Taint labels and information-flow enforcement at every tool and audio boundary; Signed result envelopes with expiry, provenance, and replay protection; A pendant interaction for narrowing or approving a sensitive predicate; Dashboard controls to inspect, revoke, and delete query receipts


## Changes it proposed to its own stack

### `integration` — Add an event-scoped Meeting Session protocol spanning relay, Mac, browser, and pendant. The Mac opens a consented session with a random session ID, emits timestamped redacted transcript/event chunks and active-window markers; browser reads only tabs explicitly attached to that session; relay stores encrypted checkpoints and a bounded evidence index; the pendant receives only urgency-tagged cue packets and emits acknowledge/stop events. On close, one deterministic reducer joins transcript timestamps, browser citations, calendar metadata, and owner acknowledgements into a reviewable brief and draft queue, with idempotent resume after disconnect.
- **owner gets:** The owner can get discreet, context-aware help during a meeting and a trustworthy follow-up packet afterward without repeatedly explaining which meeting, tabs, or notes are relevant. If the Mac or browser drops, the pendant and relay preserve the session state instead of silently losing work.
- effort: Medium-high: protocol/schema plus Mac capture/redaction, browser session binding, relay checkpoint/replay, pendant cue client, dashboard review UI, and end-to-end fault tests.  ·  risk: Accidental capture or wrong-tab leakage is the primary risk. Fail closed unless a session consent token and explicit tab/window bindings exist; enforce short TTLs, local redaction, visible recording indicator, stop gesture, and immutable audit/receipt records. Recovery is session abort and deletion of all uncommitted chunks.
- cost: No new per-request model cost beyond transcription/synthesis; relay storage and transcript processing scale with meeting duration. Estimated engineering 2–4 weeks for a prototype, plus test fixtures.  ·  latency: Cue path adds one relay hop; target p95 under 2 seconds. Checkpoint writes are asynchronous and must never block Mac capture or pendant audio.
- security: Raises privacy requirements substantially: per-session encryption keys, least-privilege browser tab tokens, no raw audio by default on relay, retention auto-expiry, and explicit owner-visible receipts.
- depends on: Mac audio/window capture with Accessibility/Screen Recording permission; consent and local redaction policy; durable relay job/checkpoint runner; browser tab/session affinity and typed evidence; pendant notification/acknowledgement protocol

### `context` — Introduce taint-aware evidence envelopes across all surfaces. Every browser extraction, Mac file/window observation, transcript segment, and pendant event carries origin, sensitivity, consent scope, expiry, and allowed destinations. Relay planning can combine envelopes but cannot emit a higher-sensitivity payload to audio, logs, or a different browser session unless a policy check produces an explicit owner approval receipt. Reducers return a short spoken answer plus a private cited artifact rather than leaking raw source text into prompts or routine history.
- **owner gets:** Private mail, work pages, meeting audio, and secrets can be useful together without silently spreading into the wrong device, spoken output, or long-term memory. The owner gets concise answers and receipts while sensitive detail stays where it belongs.
- effort: Medium: typed envelope schema, policy evaluator, prompt compiler integration, tool adapters, audit views, and adversarial cross-surface tests.  ·  risk: Over-classification could make the assistant frustratingly cautious; under-classification could leak data. Start with fail-closed defaults for secrets/audio, explain the blocked flow, and permit narrowly scoped one-time approvals. Recovery is envelope revocation and deletion of derived artifacts.
- cost: Small deterministic policy cost per event; reduces expensive prompt tokens by passing hashes/citations instead of repeated raw context. Engineering roughly 1–2 weeks for a first end-to-end slice.  ·  latency: Target under 20 ms per envelope decision locally and under 100 ms at relay; approval-required flows add human latency only when a boundary is crossed.
- security: Substantially improves least-privilege and provenance, but requires careful key management, log redaction, and no sensitive values in error messages or analytics.
- depends on: shared typed context compiler; browser provenance and tab affinity; Mac observation/action receipts; pendant local privacy/consent events; dashboard review of blocked and approved data flows

### `relay` — Add a capability-scoped query gateway rather than routing private reads through general-purpose planning. A request is compiled into a signed predicate (source, fields, operator, allowed result shape, expiry, and owner/session ID); the Mac or browser executes it locally and returns only a typed minimal-disclosure result. The relay refuses arbitrary extracted text for predicate jobs, binds each token to one tab or local data index, records a hash-only receipt, and invalidates the token after one use or timeout.
- **owner gets:** Sensitive questions become safe to ask from the pendant: the owner can learn what requires attention without having private messages, appointments, or documents copied into the relay or spoken back verbatim. It also makes the privacy promise enforceable rather than dependent on a model remembering not to reveal something.
- effort: Medium-high: predicate DSL and validator, local adapters, signed token issuance, browser/Mac enforcement hooks, result-shape tests, and dashboard receipt inspection.  ·  risk: A flawed predicate compiler could answer the wrong question, while a broad result shape could leak information through repeated queries. Use an allowlisted DSL, rate limits, coarse buckets for counts/times, source-side confirmation for unusual predicates, and a visible explanation when a query is refused. Recovery is token revocation and receipt invalidation.
- cost: Small deterministic relay overhead; substantially fewer planner tokens and less sensitive data storage. Engineering and security review dominate cost.  ·  latency: Adds one validation step, targeted under 100 ms; local source access remains the dominant latency. No extra realtime model turn for supported predicates.
- security: Reduces relay data exposure and prompt-injection surface, but signing keys, token replay prevention, and adapter isolation become critical. Raw source text must never enter generic job logs or analytics.
- depends on: minimum-disclosure query capability; typed provenance/taint envelopes; Mac and browser local predicate adapters; signed action/result receipt format; owner-visible privacy and revocation controls


## What it asked for

_Nothing._
## Its own summary

Recorded a new minimum-disclosure private-question capability and its relay-side capability-scoped predicate gateway. This is not a general browser brief or durable job: it lets the owner ask sensitive questions while source devices return only bounded typed results, with signed one-use tokens and hash-only receipts.

**Biggest unknown:** The exact owner-approved predicate vocabulary and disclosure ceilings for mail, calendar, files, and logged-in pages.

