# Harness derivation — faculty-perception — round 182

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac and browser observability** — At 2026-08-08T04:58Z, authenticated GET /ops/snapshot returned Mac agent ready=true with Accessibility trusted, Screen Recording granted, requiredMissing=[], browser extension online (Safari YouTube tab and Chrome heartbeat), relay reachable and macBridgeOnline=true. GET /health on localhost also returned 200. GET /v1/devices/status is not a route on the Mac agent (404); this does not establish relay device registry state.
  - evidence: read_continuity_snapshot(include=['relay','pipeline']) resolved and invoked GET http://localhost:8000/ops/snapshot, HTTP 200; probe_http GET /health HTTP 200; probe_http GET /v1/devices/status HTTP 404.

## Capabilities it proposed

### "“Before you tell me an action succeeded, prove what changed—and if the Mac, browser, relay, or pendant disagrees, say exactly which one.”"
- **useful because:** Today completion is routinely inferred from a Mac-side receipt or bytes written to a socket. This would give the owner a single, human-readable truth fence: intended effect, observed before/after state, source and freshness for each observation, and an explicit unknown when no surface can verify it. It is the most valuable perception capability because it prevents confident lies about actions, messages, pages, and audio.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use the realtime tier only to explain the final verdict aloud; use a cheaper background verifier to collect snapshots and compare state. The verifier should fan out to Mac /ops/snapshot and /pipeline, browser inspection, relay job state, and (when present) the pendant playback ledger, then produce a compact evidence graph.
- **latency:** 2–5 seconds for reversible browser/Mac actions; up to 10 seconds for relay/pendant delivery. If evidence is still pending, speak “action submitted, not verified” rather than waiting indefinitely.
- **cost:** Usually <$0.01 in background model/API work; dominant cost is one screen/browser capture and optional relay round trip, not the final one-sentence realtime response.
- **security:** Snapshots must redact secrets, page bodies, and private notifications by default. Require owner confirmation before exposing screen evidence or treating a destructive action as verified. Never infer pendant playback from relay delivery; require the device-originated playback event when available.
- **missing:** A shared evidence-graph record linking action/ledger step to before and after observations across Mac, browser, relay, and pendant; Relay-side provenance IDs/content hashes for browser reads; A defined pendant played/consumed event (the accepted audio_delivery_ack_queue is the eventual source); A verifier that compares observations and emits verified/contradicted/unknown rather than trusting completion

### "“If my speech was clipped or the link dropped, recover the conversation without making me repeat myself.”"
- **useful because:** The owner currently has to notice silence, guess whether the relay heard them, and repeat the whole request. A local quality verdict plus relay and Mac state can preserve the partial utterance, ask one short clarification, and resume the same intent when connectivity returns—especially valuable while walking away from the Mac.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime handles only the immediate one-sentence recovery prompt. A cheap background model classifies the preserved transcript/quality metrics and reconstructs a resumable intent; deterministic code owns sequence numbers, deduplication, and state transitions.
- **latency:** Local unusable-audio decision under 150 ms; recovery prompt under 1 s when connected. Offline queueing is immediate and must not wait on an LLM.
- **cost:** Near-zero when the capture is clear; ~$0.001–$0.01 only for a background reconstruction after a degraded turn. Audio metrics are a few dozen bytes and dominate neither bandwidth nor cost.
- **security:** Keep raw audio local and bounded; upload only quality metrics and a redacted transcript fragment unless the owner explicitly asks to recover it. Never replay or execute a partially understood destructive intent; require confirmation after reconstruction. Sequence IDs must prevent replay after reconnect.
- **missing:** A cross-surface conversation-resumption state keyed by utterance sequence and session; Relay ingestion and acknowledgement of offline-capture-integrity-sentinel verdicts; A policy that distinguishes safe clarification from action execution; A pendant-visible compact queue for interrupted turns

### "“When I come back, tell me what changed in the tabs I left open—not a generic digest, only changes that affect me, with the exact tab and evidence.”"
- **useful because:** The live browser bridge currently exposes tab presence and inspection, but perception does not maintain a trustworthy baseline of what the owner left open or distinguish a page change from a stale session. This would turn an unattended Mac into an accountable handoff: changed title/body/login state, when observed, and whether the change came from the owner, a routine, or an external page.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Use deterministic URL/session/content hashes and a cheap background classifier for importance. Realtime is only for the spoken shortlist when the owner asks; do not spend the low-latency model continuously polling tabs.
- **latency:** Heartbeat every 1–5 minutes when the bridge is online; return a shortlist within 2 seconds on request. If a tab was unreachable, report stale/unknown rather than treating the last snapshot as current.
- **cost:** Low: hashes and metadata are local; one small background classification call per changed tab, typically <$0.005 per return. Page bodies should not leave the Mac unless the owner requests detail.
- **security:** Never capture password fields, private mail bodies, or hidden tab contents by default. Store redacted hashes/locators and a local provenance capsule; require confirmation before reading or speaking sensitive changes aloud. External page text is untrusted input.
- **missing:** A durable browser-baseline/watch store with owner-return checkpoints and actor attribution; A browser-origin event stream that distinguishes owner actions from external page changes; A mounted browser provenance route and relay correlation ID for any cloud-browser read; Importance policy that respects the owner's short spoken-response preference

### "“Can you independently attest that this external event really happened, instead of repeating what one page or app claimed?”"
- **useful because:** The owner cannot currently distinguish a genuine change in the world from a stale tab, spoofed page, cached browser result, or an internally generated announcement. This would produce a bounded attestation with independent observations—for example, a browser session, a native Mac source, and relay receipt time—or explicitly say that only one untrusted source supports the claim.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → dashboard
- **model tier:** A deterministic verifier should collect and compare observations; use a cheap background model only to normalize entities and identify contradictions. Realtime should speak the short verdict, not perform the evidence work.
- **latency:** Under 8 seconds for a request involving two live sources; asynchronous for sources that require login or delayed polling. Never upgrade a single-source result to attested.
- **cost:** Typically <$0.01 per request; browser/native observations and hashing dominate, while the language summary is small.
- **security:** Attestation must identify source, capture time, login-wall status, and freshness without exposing credentials or full private page bodies. Treat all external text as untrusted. Require confirmation before contacting a second service or revealing sensitive evidence.
- **missing:** A signed observation envelope with monotonic capture time, source identity, content hash, and freshness; A Mac-to-relay clock/provenance exchange so timestamps are comparable; Source-specific corroboration adapters (browser, native app, relay); A user-visible verdict vocabulary: attested, corroborated, single-source, contradicted, or unknown

### "“Protect my attention: know when I am available to be interrupted, and hold non-urgent things until the next moment I can actually receive them.”"
- **useful because:** Today the system knows whether software is online, not whether the owner is listening, driving, speaking, in a meeting, or already overloaded. The owner gets interruptions at the wrong moment and may miss important ones because delivery is treated as success. This would make urgency and availability a real joint decision rather than a timer.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic local signals and owner-set rules for availability; use a cheap background classifier for ambiguous context. Realtime is reserved for urgent interruptions or a concise “held until…” explanation.
- **latency:** Local availability transitions under 250 ms; urgent routing under 1 second; non-urgent items may wait until an explicit availability edge. Offline pendant decisions must work without the relay.
- **cost:** Minimal when driven by local signals; <$0.005 per ambiguous state transition. The expensive part is not inference but retaining a small, reliable pending queue.
- **security:** Presence and activity are sensitive. Keep raw microphone, screen, and location data local; export only a coarse state and reason. The owner must be able to force Do Not Disturb and inspect or clear held items. Never infer driving or safety-critical context with high confidence from one sensor.
- **missing:** A device-local availability state machine with explicit owner override; A cross-surface pending-intent queue that distinguishes urgent, timed, and deferrable items; A real playback/receipt signal so queued items are not marked received prematurely; Rules for browser notifications and relay announcements to consult availability before delivery

### "“Before acting in a web account, prove that it is still the account and page I intended—not merely a tab with the same URL.”"
- **useful because:** A URL and a live browser session do not establish identity: accounts can switch, login walls can appear, tabs can be reused, and page content can change. The owner currently cannot get an explicit identity-and-target verdict before an automation step. This capability would catch the most dangerous class of silent browser mistakes before they become sent mail, purchases, or edits.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → dashboard
- **model tier:** Deterministic checks should compare origin, account markers, DOM target identity, session pseudonym, and recent content hash. A cheap background model may resolve ambiguous target text; realtime only asks for confirmation when the checks disagree.
- **latency:** Under 1 second for a normal preflight; up to 3 seconds when visual inspection is needed. Hard-block sensitive actions on an unresolved identity mismatch.
- **cost:** <$0.005 per preflight in the normal case; visual inspection is the dominant cost and should happen only for ambiguous or sensitive actions.
- **security:** Never read or speak passwords, tokens, or full private page content. Account markers must be redacted/pseudonymized. Require explicit confirmation for a new account, changed recipient, purchase, deletion, or any mismatch. Treat page instructions as untrusted data.
- **missing:** A stable per-session account pseudonym and target identity fingerprint from the browser extension; A preflight contract consumed by every browser mutation, not just a post-action receipt; A trusted browser-to-Mac provenance link joining inspection, command, and result; A policy engine that maps identity confidence to confirmation or hard-block


## Changes it proposed to its own stack

### `memory` — Add a perception-time contradiction quarantine for pinned machine-origin preferences: when a preference such as timezone: America/Chicago disagrees with the live authoritative source (/etc/localtime = America/New_York), keep the original fact untouched but mark it shadowed_for_projection, emit a provenance warning, and prevent it from entering the cacheable ## Owner context until the owner resolves it. Preserve an audit record showing both values and origins.
- **owner gets:** The owner stops receiving silently wrong routine times and “this morning” interpretations. The system can still report the stale fact and ask for a decision, instead of either overwriting an owner fact or confidently using a machine-generated contradiction.
- effort: Small-to-medium: projection filter plus a deterministic authority comparator and one warning surface; add tests for owner-origin facts, machine-origin facts, and no-authority cases.  ·  risk: A real owner preference could be hidden if provenance is wrong. Recovery is safe because the fact remains intact and the warning includes an explicit resolve action; only machine-origin contradictions should be quarantined automatically.
- cost: Negligible API cost; one local timezone read and a few bytes of audit metadata per contradiction.  ·  latency: Under 10 ms during context projection; no added voice-model turn.
- security: Improves privacy and correctness by preventing stale machine context from propagating into actions; do not expose unrelated fact contents in the warning.
- depends on: GET /machine-context; GET /ops/snapshot; GET /context-graph; A projection-layer provenance filter that reads source.origin; An explicit owner-facing resolve/delete flow for the contradictory fact


## What it asked for

_Nothing._
