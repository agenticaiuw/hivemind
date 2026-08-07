# Harness derivation — faculty-perception — round 34

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-input-reachability** — At 2026-08-07T10:43:01Z, Mac agent's /observe says Accessibility trusted=false, Screen Recording=false, inputReachability status=failed, eventsPost=false, uiActionsWillReachTheScreen=false. It explicitly says synthesized events are accepted by a different binary than running com.aipendant.agent; UI action receipts cannot be trusted.
  - evidence: GET /observe HTTP 200 response observedAt 2026-08-07T10:43:01.583Z
- **mac-agent-readiness** — At 2026-08-07T10:43:01Z, Mac agent is online v0.5.0 with fullControlMode=true and requiredMissing=[], but permissions.ready=false because Accessibility and Screen Recording remain ungranted for the running AI Pendant Agent binary. Computer-use loop is disabled and vision upload consent is false.
  - evidence: GET /ops/status HTTP 200 payload timestamped 2026-08-07T10:43:01Z
- **browser-connectivity** — At 2026-08-07T10:43:01Z, home-chrome browser extension is offline with no active tab/window metadata and 3 pending commands; /observe still lists 3 durable browser sessions pointing to time.is/UTC, Selenium web form, and httpbin form, but those are not proof of live browser control.
  - evidence: GET /browser/status and GET /observe HTTP 200 responses
- **timezone** — Mac machine-context reports authoritative host timezone America/New_York.
  - evidence: GET /machine-context HTTP 200 machine.timezone
- **computer-use-vision-readiness** — At 2026-08-07T10:43:01Z, computer-use loop is disabled despite visionModelConfigured=true because visionUploadConsented=false; this prevents screenshot-based perception and is separate from Accessibility/Screen Recording permission state.
  - evidence: GET /ops/status HTTP 200 agent.computerUse payload

## Capabilities it proposed

### "“Before you try, tell me whether you can actually do this right now—and if not, what I need to fix.”"
- **useful because:** Today the system reports optimistic full-control mode while live probes show UI input cannot reach the screen, and it retains three queued browser commands while Chrome is offline. A wearer needs a truthful feasibility answer before trusting a spoken command, not a receipt after a no-op. This makes perception a first-class cross-device service: the pendant hears the request, relay asks the Mac observer and browser bridge for fresh probes, judgement maps the requested operation to prerequisites, and the pendant speaks either a viable route with an expiry or a precise blocker and safe alternative.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime for the short spoken feasibility question and prerequisite classification; use a cheap background model only to summarize repeated diagnostics or suggest setup steps.
- **latency:** 2–4 seconds for a fresh probe-backed answer; cache only within a short lease (for example 30 seconds) and visibly say when a result is cached. Re-probe immediately before any consequential action.
- **cost:** Roughly one small realtime turn per check; model cost is dominated by voice input/output, while Mac/browser probes are local and effectively free. Background summaries should use a cheaper tier.
- **security:** Do not transmit page contents, credentials, screenshots, or audio beyond the existing relay path just to answer feasibility. Return capability names, permission state, device online state, timestamps, and blockers. Never claim success from an action receipt when observe says uiActionsWillReachTheScreen=false. Any proposed permission fix or irreversible action still requires owner confirmation.
- **missing:** A shared typed feasibility endpoint/contract that joins /observe, /ops/status, /browser/status, relay reachability, and pendant pipeline state with source timestamps and expiry.; A request-to-prerequisite matrix (read page vs click UI vs send message vs speak) owned by judgement, with fail-closed semantics.; A pendant/relay spoken response type for blocker, alternative route, and freshness/expiry.; A dashboard view showing the exact probe evidence behind “can/cannot.”

### "“When you tell me something, let me ask ‘why?’ and hear the exact evidence, timestamp, and uncertainty behind it—without exposing my private page contents.”"
- **useful because:** The owner cannot currently audit a spoken conclusion across the pendant, relay, Mac observer, and browser: a result may combine stale device state, a private-tab reading, and a model inference, with no single explanation that distinguishes those layers. This capability would let them trust or correct the system in the moment, especially when a device was offline or an action was not reachable. It is not an action-history view; it is a cross-surface provenance replay for perceptions and conclusions, with redacted evidence and explicit uncertainty.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime only to answer the owner's short spoken “why?” follow-up; use a cheaper background model to normalize evidence and produce redacted summaries when the original result is old.
- **latency:** Under 2 seconds when the provenance capsule is retained locally; under 5 seconds if the relay must retrieve and redact multiple source records. Provenance should expire with the conclusion, and the spoken answer must say when only a summary remains.
- **cost:** Small incremental relay/D1 metadata storage and one short realtime response. Do not resend raw screenshots or full page text unless the owner explicitly asks and confirms; normal use is dominated by a compact text turn.
- **security:** Store hashes, source labels, timestamps, confidence, and redacted snippets by default—not credentials, session cookies, or unrestricted page contents. Private browser evidence must be permission-scoped and revocable; revocation should leave an audit tombstone saying evidence was withdrawn without retaining the secret. Require confirmation before revealing sensitive source text or replaying audio.
- **missing:** A cross-surface provenance capsule schema linking each spoken claim to observation IDs, source device, observedAt, expiry, confidence, and redaction policy.; Relay storage and retrieval for capsules with per-owner authorization, revocation, and tombstones.; Mac and browser observers that emit stable observation IDs and field-level sensitivity labels.; A claim composer that preserves which parts were observed versus inferred, and a pendant response format for concise uncertainty explanations.; Dashboard UI to inspect the same capsule without silently expanding redaction.


## Changes it proposed to its own stack

### `context` — Add a fail-closed, signed “capability lease” snapshot produced by the perception service. Each lease contains operation class (read-only web, browser click, Mac UI input, filesystem, audio), device/surface, boolean reachability, blocker code, evidence source, observedAt, expiresAt, and a monotonically increasing generation. Judgement may plan only against an unexpired lease; action must revalidate the generation immediately before execution and attach the lease plus final observation to the receipt. Permission changes, browser heartbeat loss, foreground/secure-input changes, or probe failure revoke the relevant lease and increment its generation.
- **owner gets:** The owner stops hearing confident confirmations for actions that could not reach the screen. If Chrome disconnects or macOS permissions silently change, the pendant can explain the blocker before acting and automatically fall back to a server/public read where safe.
- effort: Medium: define schema and revocation rules in relay/shared context, implement Mac observer projection and browser heartbeat integration, add preflight in judgement/action, and expose dashboard diagnostics. Requires tests for stale snapshots, concurrent actions, and clock skew.  ·  risk: A false negative delays a useful action; recover by offering an alternate route or a one-tap recheck. A false positive is more dangerous, so leases must default to denied when evidence is missing or stale. Never treat a historical receipt as current reachability.
- cost: Negligible storage and local CPU; one compact snapshot per probe and small D1 history. No additional model call for execution; the feasibility voice answer may add a small realtime turn.  ·  latency: Adds a local preflight of tens to hundreds of milliseconds, plus a fresh browser/Mac probe when the lease is expired. Prevents much longer failed computer-use loops.
- security: Improves least privilege by binding permissions to operation class and expiry; avoid storing page content in leases. Lease signatures prevent one surface from asserting another surface is ready without evidence.
- depends on: A shared typed context projection (existing backlog work should be extended rather than duplicated); A Mac /observe probe that reports the actual running binary’s permissions; Browser heartbeat with online/offline generation changes; Judgement/action integration that refuses expired or revoked leases


## What it asked for

_Nothing._
