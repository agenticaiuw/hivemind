# Harness derivation — unified — round 257

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""I lost connection or restarted the Mac. Tell me exactly where the last task/conversation stopped, what is safe to continue, and let me choose what happens next.""
- **useful because:** Today an interrupted run is either mistaken for an unfinished one or requires the owner to know internal IDs and manually replay returned steps. This gives a truthful, non-destructive spoken handoff: completed work, uncertain work, blocked approvals, browser state, and the one explicit next choice. It turns outages into a comprehensible recovery moment rather than duplicate actions.
- **path:** relay → mac-bridge → browser → pendant
- **model tier:** background for assembling the handoff; realtime only to speak the short result when the pendant reconnects
- **latency:** Under 3 seconds after reconnect for the summary; no action is executed during summary generation
- **cost:** Low: one background synthesis over bounded receipts and handoff metadata; dominated by a small model call, typically <$0.01
- **security:** Read only by default. Redact page contents and sensitive parameters, show only bound browser targets and action outcomes. Continuing any step requires a separate owner choice and existing physical transaction approval for staged risky actions.
- **missing:** A production caller that assembles GET /workbench/jobs/:jobId/handoff with ledger/job receipts and browser command outcomes; A durable relay-side handoff index keyed by job/session so reconnect does not require an internal ID; A pendant reconnect event that requests the handoff without treating it as permission to execute

### ""When I turn privacy mode on, make every surface actually go private, and tell me if anything could not be stopped.""
- **useful because:** The pendant latch already stops local capture and playback, but a Mac/browser may still expose queued work, browser sessions, or retained relay state. This is a cross-surface emergency action: local silence first, then relay cancellation and browser redaction, followed by a signed convergence result that names any residual risk instead of implying privacy from one LED.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** Deterministic control and read-only verification; no expensive model required except optional owner-facing explanation
- **latency:** Pendant mute/capture stop is immediate; relay/browser revocation begins within 1 second; final convergence receipt within 5 seconds or explicitly reports timeout
- **cost:** Negligible API cost; bounded state mutations and one privacy_convergence_check read. Storage is a small latch event and receipt.
- **security:** The local latch must win even with no network. Relay must reject new audio persistence and browser exposure after the latch epoch; queued external actions are cancelled or held, not silently resumed. Never delete job audit history. Require authenticated latch ID and make the receipt tamper-evident.
- **missing:** A relay privacy-epoch gate consulted by audio ingest, TTS delivery, queued jobs, and browser exposure; A Mac/browser revocation hook that cancels pending capture/playback and closes or redacts bound browser sessions; An event bridge from local_privacy_latch into the relay, plus a durable residual-risk receipt

### ""Before you send or play anything important, tell me whether the pendant is ready to hear it and whether the bridge actually played the last thing.""
- **useful because:** A relay acknowledgement is not the same as the owner hearing audio. This capability gives a preflight-and-aftercare answer grounded in current link health, codec timing, bridge buffer safety, and the device's delivery/playback receipts, so the system can defer or retry instead of speaking into a dead path.
- **path:** relay → pendant → mac-bridge
- **model tier:** Deterministic diagnostics for the measurements; background model only to summarize repeated failures
- **latency:** Preflight under 500 ms from cached health; post-playback receipt within the artifact's normal delivery window, with timeout surfaced rather than guessed
- **cost:** Low: read-only health and receipt queries; occasional audio validation/fault test is offline maintenance, not per utterance
- **security:** Do not transmit synthetic or private audio merely to test readiness during a live conversation. Use cached counters and explicit fixtures only when the owner requests diagnostics. Receipts carry opaque artifact IDs and hashes, not transcript content.
- **missing:** A live typed readiness endpoint joining pendant/bridge health to the current session; A correlation key spanning relay TTS artifact, Opus packet stream, bridge acknowledgement, and playback start/finish; A policy for what to do on DEGRADED versus FAILED (defer, retry, or fall back)

### ""Erase the last two minutes of this conversation everywhere, and prove what was removed and what could not be reached.""
- **useful because:** The privacy latch stops future capture but cannot retract audio, transcripts, relay copies, Mac logs, browser snapshots, or derived facts already created during an interval. A bounded, owner-triggered redaction interval would give the owner a practical emergency erase control with an honest partial-completion receipt.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** Deterministic interval selection, deletion and verification; no model needed except optional plain-language summary
- **latency:** Latch and interval boundary locally immediate; local deletion receipt under 2 seconds; replicated/offline surfaces report pending rather than blocking
- **cost:** Low API cost; bounded deletion manifests and verification reads dominate storage, not inference
- **security:** Require a deliberate physical gesture and a bounded maximum interval. Preserve action audit history, but delete raw audio, transcripts, browser snapshots, derived fact candidates, and relay replicas in scope. Use an append-only redaction receipt that contains IDs and outcomes, never the erased content.
- **missing:** A cross-surface redaction protocol with a single interval ID and retention-object inventory; Relay/Mac/browser deletion workers that can prove absence or report unreachable replicas; A pendant command/event for selecting and confirming a recent interval

### ""Run a monthly fire drill: test that the pendant, relay, Mac, browser, and audio bridge can recover from an outage, then tell me the first thing that would fail.""
- **useful because:** The owner cannot know whether the system will recover until a real failure destroys continuity. A scheduled, non-user-data synthetic drill would exercise link loss, queued work, browser command leases, audio delivery, and reconnection across all nodes, producing a ranked failure boundary before it matters.
- **path:** relay → pendant → mac-bridge → browser
- **model tier:** Background deterministic test orchestration; cheap model only to summarize the ranked findings
- **latency:** Runs off-hours for up to 5 minutes; owner receives a concise result after completion, never during a live conversation
- **cost:** Moderate test traffic and a few synthetic audio packets per drill; no owner content leaves the device
- **security:** Use fixed synthetic payloads and isolated test job IDs. Never invoke external irreversible actions or touch logged-in page data. Require an explicit opt-in schedule and make the drill cancellable.
- **missing:** A test namespace that isolates synthetic jobs, browser commands, and receipts from production history; A controlled fault matrix spanning modem/relay/codec/Mac/browser and a recovery oracle; A scheduler and owner-facing report that ranks failed invariants rather than merely saying pass/fail

### ""For this conversation, let me choose exactly which surfaces may see it and what may be retained; enforce that boundary on the pendant, relay, Mac, and browser before anything leaves.""
- **useful because:** The current privacy latch is an emergency all-or-nothing stop, while ordinary turns have no owner-visible data boundary. This would let the owner permit, for example, browser control but no page snapshot retention, or audio processing but no extracted memory, and receive a refusal before a surface that cannot honor the boundary is used.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** Deterministic policy compilation and enforcement; no model call required
- **latency:** Policy acknowledgement before capture or action begins, under 300 ms when local; fail closed if a surface cannot attest compliance
- **cost:** Low runtime cost; policy envelopes and short compliance receipts dominate
- **security:** Policy must be signed/bound to session and turn, immutable for that turn, and visible on the pendant. A surface that cannot enforce a requested rule must be excluded, not treated as compliant. Preserve only minimal audit metadata and never use the policy as permission to expose secrets.
- **missing:** A per-conversation data-boundary schema covering capture, transcript, page content, screenshots, memory extraction, and retention; Preflight attestations from relay, Mac, and browser that name the exact processors/storage they will use; Enforcement hooks that reject capture/action dispatch when the requested boundary cannot be met


## Changes it proposed to its own stack

### `model-routing` — Add a deterministic 'evidence sufficiency' gate before any owner-facing completion claim. It must classify a result as confirmed, partially evidenced, or unknown by joining action receipts, browser results, audio delivery/playback receipts, and commitment evidence; the model may phrase the result but may not upgrade unknown to success.
- **owner gets:** The owner should never hear 'done' when the Mac accepted a command but the browser did not submit, or when audio was delivered but never played. This turns the system's strongest trust feature into honest language at the exact point where overclaiming is most damaging.
- effort: Medium: define evidence precedence and correlation IDs, implement a deterministic reducer, add adversarial tests for missing, stale, contradictory, and redacted evidence.  ·  risk: It may sound less helpful by refusing to guess, or incorrectly mark a valid action unknown when a receipt is delayed. Show the missing evidence and offer a status recheck rather than retrying side effects.
- cost: Near-zero per request; bounded receipt reads. Background synthesis only when explanation is requested.  ·  latency: Adds tens to hundreds of milliseconds for receipt reads; no realtime model call required.
- security: Reduces leakage by summarizing evidence rather than exposing page contents or sensitive parameters; requires strict binding of evidence to job/session/artifact IDs.
- depends on: A shared correlation identifier across /execute, browser results, pipeline artifacts, and delivery receipts; Typed receipt schemas with timestamps and terminal states; Existing commitment_evidence_query and GET /jobs/:jobId/receipts


## What it asked for

_Nothing._
## Its own summary

This round I recorded three owner-facing capabilities: outage recovery handoff (truthful stopped/finished/unsafe-to-replay summary), cross-surface audio readiness/playback assurance, and a privacy-epoch integration that actually gates relay/Mac/browser state after the local latch. I also recorded an evidence-sufficiency model-routing change so completion claims cannot upgrade missing evidence into success. The staged physical-approval integration and extracted-fact erasure proposal were rejected as existing backlog items rather than new work; I will not restate them.

**Biggest unknown:** What remains genuinely unbuilt is the connective layer: typed correlation IDs across job/browser/audio receipts, a live readiness endpoint, relay privacy-epoch enforcement, and a reconnect handoff caller. I do not need another permission or tool this round; the next useful discovery is an inventory of /workbench/* and any existing approval/privacy/receipt routes so these proposals can be narrowed to exact missing code rather than overlapping existing endpoints.

