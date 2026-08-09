# Harness derivation — unified — round 265

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live cross-surface readiness** — At this check the Mac agent, relay, browser extension, Accessibility, Screen Recording, and automation permissions are all healthy; Safari has one online YouTube tab with zero pending commands. The nRF9160 pendant remains offline/unregistered, so current readiness is Mac/relay/browser-only, not wearable duplex.
  - evidence: GET /ops/status returned agent.ok=true, relay.reachable=true, permissions.ready=true, browserExtension.online=true, pendingCommands=0; discover(devices) listed nrf9160-pendant offline.

## Capabilities it proposed

### "“Why did I miss that reply?” Give me one owner-readable diagnosis of a failed or delayed conversation turn, separating capture, relay, model, playback, and bridge causes, with the exact evidence and whether retrying is safe."
- **useful because:** Today each layer can report a local symptom, but the owner cannot tell whether silence came from capture loss, LTE/relay loss, model completion, or audio never reaching the speaker. A correlated answer prevents blind retries and makes a real outage actionable.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Background model for correlation and explanation; deterministic validators and counters first, with realtime only if the owner asks during a live call.
- **latency:** Under 5 seconds for a completed turn; under 15 seconds for historical diagnosis.
- **cost:** Low: mostly reads and deterministic checks; one short background-model explanation, roughly $0.01–$0.05 depending on evidence volume.
- **security:** Redact transcript/audio content by default; expose sequence IDs, counters, hashes, and timing rather than raw speech. Require explicit expansion before showing audio or text.
- **missing:** A single correlation key carried from capture through pipeline, relay job, delivery acknowledgement, and bridge playback; Automatic invocation of audio_pipeline_validate and incident_diagnostics for one turn; A dashboard/voice formatter that distinguishes evidence from hypotheses

### "“Continue the interrupted thing I asked you to do, but do not repeat anything that already happened or send anything irreversible without asking me.”"
- **useful because:** A Mac/browser outage currently leaves the owner with either a stale status or a dangerous manual replay. The existing ledger can classify replay safety and the workbench can identify committed outputs, but no owner-facing path joins those facts into a safe continuation.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic resume planner for ledger/workbench decisions; background model only explains the plan in plain language.
- **latency:** Plan in under 3 seconds; execute only after explicit confirmation for unrepeatable, unknown, irreversible, off-machine, or uncontained steps.
- **cost:** Low: filesystem/ledger reads dominate; optional explanation under $0.01.
- **security:** Never replay unrepeatable or unknown steps automatically. Bind the plan to the original job, world fingerprint, and a short lease; preserve audit history and show every skipped/rerun/blocked step.
- **missing:** A production caller that closes ordinary ledgers and invokes planResume; A relay job lease and stale-processing requeue; A resumable owner-facing route that returns completed/skipped/rerun/ask/blocked steps and executes only approved safe steps; A real approval delivery path for pending physical_transaction_approval_latch decisions

### "“Before I rely on you, run a privacy-and-reachability check and tell me exactly which parts can hear me, act for me, or expose my browser right now.”"
- **useful because:** The owner currently has to infer readiness from separate health pages. A single preflight distinguishes an offline pendant from a healthy Mac bridge, a held browser command from an actually connected tab, and an active capture path from a privacy latch. It is useful before a sensitive conversation or delegated action, not merely during an outage.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic checks and receipts; a cheap background model turns the result into a concise owner-facing answer only when requested.
- **latency:** Under 3 seconds for local surfaces and under 8 seconds if relay/browser heartbeats are needed.
- **cost:** Negligible API cost; parallel authenticated reads and one compact formatter.
- **security:** Do not expose tab URLs, page contents, microphone audio, or bearer credentials. Return capability states and freshness timestamps only. A failed check must fail closed for any subsequent sensitive delegation.
- **missing:** A typed cross-surface preflight route with a single freshness deadline and correlation ID; A relay-side liveness check that distinguishes pendant never-seen/offline from merely not registered; A browser exposure check that reports command leases and tab connectivity without page content; A policy hook that blocks sensitive actions when privacy convergence or reachability is stale

### "“For the next hour, treat this as a private session: do not retain or expose names, page content, or transcripts, and prove that the rule is active on every surface.”"
- **useful because:** A privacy latch stops microphone and playback, but it does not express a temporary data-handling boundary while the owner is still using the system. The owner needs a mode that constrains relay persistence, Mac/browser observation, extracted-memory writes, and downstream model context together.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic policy enforcement and receipts; no model should decide whether content belongs inside or outside the private boundary.
- **latency:** Activation and authenticated convergence receipt within 2 seconds; policy must apply before the next captured frame or browser command.
- **cost:** Low ongoing cost; one signed session policy and compact receipts, with no additional model call.
- **security:** Default-deny on stale or missing policy receipts. Keep the policy token opaque, prevent browser page contents from crossing the boundary, and make expiry automatic. The owner must explicitly end or extend the mode.
- **missing:** A signed privacy-policy epoch shared by pendant, relay, Mac, and browser bridge; Capture/relay/model/context-graph gates that honor the epoch before accepting data; A browser command scope that can be issued without page-content retention; An owner-visible receipt proving each surface adopted the same policy and expiry

### "“I think something unsafe is about to happen—stop every pending action everywhere, revoke their authority, and tell me what was prevented.”"
- **useful because:** Stopping audio capture is not enough during a compromised or mistaken delegation. The owner needs a physical or spoken panic action that cancels queued relay jobs, browser commands, Mac execution leases, and staged approvals, then returns one tamper-evident prevention report.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic revocation and reconciliation; a background model may summarize prevented effects after the stop is complete.
- **latency:** Local pendant stop immediately; relay/browser/Mac revocation fan-out within 2 seconds; reconciliation within 10 seconds.
- **cost:** Low: signed epoch revocation and status reads; no routine model cost.
- **security:** The revoke path must work without relay connectivity and persist an epoch across reboot. It must never claim cancellation after an irreversible side effect has already committed; report committed, prevented, and unknown separately.
- **missing:** A monotonic global revocation epoch accepted by relay, Mac executor, browser bridge, and approval store; Cancellation hooks for queued and processing jobs plus browser command leases; A pendant-resident offline revoke event and retry-safe delivery; A receipt correlating every cancelled, already-committed, and indeterminate action

### "“Never remember these categories about me again—before anything leaves the pendant or browser, strip them, and show me that the rule was applied.”"
- **useful because:** Review-and-delete is too late for information the owner never wanted stored. A preventative retention firewall lets the owner define forbidden classes—such as health, finance, or other people's names—and enforces the rule before relay persistence, model context, extracted facts, or browser evidence are created.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic pattern/entity filtering for high-confidence classes; ambiguous matches are withheld and surfaced for owner review rather than guessed.
- **latency:** Under 100 ms for metadata and text filtering on the Mac/relay path; bounded buffering for pendant frames with no added conversational delay.
- **cost:** Small ongoing compute cost for local classifiers; background model use only for owner-authored rule setup, roughly cents per rule change.
- **security:** Rules and redaction decisions must be auditable without storing the redacted content. Fail closed when the classifier or policy receipt is unavailable. Explicitly distinguish redaction from deletion and never imply that already-replicated data was erased.
- **missing:** A versioned owner policy with category rules and precedence; Local filtering before upload plus relay-side defense-in-depth filtering; Redaction markers that preserve task continuity without retaining the sensitive value; A signed per-event receipt showing policy version, fields removed, and replication status


## What it asked for

_Nothing._
