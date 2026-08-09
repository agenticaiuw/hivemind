# Harness derivation — faculty-perception — round 167

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac accessibility and screen recording reachability** — As of 2026-08-08T03:02Z, GET /observe reports inputReachability.status=verified, Accessibility trusted, Screen Recording true, secureInput false, and uiActionsWillReachTheScreen=true for com.aipendant.agent; GET /ops/snapshot independently reports permissions.ready=true and no requiredMissing permissions.
  - evidence: Authenticated GET /observe and GET /ops/snapshot both returned HTTP 200 with these fields.

## Capabilities it proposed

### ""Only act when you can tell I’m not actively using the Mac; otherwise ask me first.""
- **useful because:** Prevents the Mac agent from typing, speaking, or changing a browser session while the owner is in the middle of something, without reducing unattended automation. It combines independent presence signals instead of trusting a single foreground-app guess.
- **path:** mac-planner reads /observe and /ops/snapshot → browser-extension reports heartbeat, tab/window identity, and pending commands → relay records the policy decision and expiry for an unattended job → pendant speaks a short confirmation or interruption request when connected
- **model tier:** Cheaper background rules model for signal fusion; realtime only for the spoken interruption. No expensive model is needed for the normal allow/deny decision.
- **latency:** Under 300 ms for a local preflight; if signals disagree, pause and ask rather than guessing.
- **cost:** Negligible API cost for the normal path; one short realtime turn only when owner confirmation is required. Dominant cost is none, not tokens.
- **security:** Foreground app and browser tab titles can reveal sensitive context, so relay receives only a signed presence verdict and coarse reason, not URLs or screenshots. Any action affecting external communication still requires explicit confirmation.
- **missing:** A signed, bounded presence-attestation record joining /observe, browser heartbeat, and relay job ID; A policy evaluator that turns disagreement or stale signals into pause/confirm; A Mac preflight hook before every delegated action

### ""Before I depend on this pendant, run a one-minute bench test and tell me exactly which link or speaker stage failed.""
- **useful because:** The hardware is physically testable over USB even though no pendant is relay-registered. This would turn the current misleading binary state into a useful end-to-end verdict: serial discovery, firmware beacon, audio capture quality, relay reachability, browser/Mac path, and (when registered) actual delivery.
- **path:** mac-terminal discovers /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA and runs the bounded probe → pendant emits the accepted offline-reality-beacon and offline-capture-integrity-sentinel verdicts → relay checks registration, heartbeat freshness, and a nonce-scoped echo without treating socket write as playback → mac-planner renders a stage-by-stage report and stores the test receipt → browser-extension is used only to confirm the owner's browser bridge remains reachable, not as a substitute for audio
- **model tier:** No model for measurements; a cheap summarizer turns numeric results into one spoken sentence. Realtime is unnecessary unless the owner asks follow-up questions.
- **latency:** 60 seconds maximum, with each stage individually time-bounded and abortable. USB tests must never write to the SD fallback store.
- **cost:** Near-zero API cost; dominated by one-minute hardware probe and optional TTS. No screenshot or page content leaves the Mac.
- **security:** Serial output may contain firmware identifiers but no page content. Use a nonce and redact credentials. Never claim playback from relay acceptance; report unregistered/no-device as a precise stage result.
- **missing:** Read-only serial probe action for the two live USB ports; A test-only firmware command/response for beacon and capture verdict; Relay nonce echo plus a registration-aware result endpoint; A single receipt schema joining USB, relay, and playback stages

### ""When I come back, give me a confidence-ranked account of what happened—not just a list of completed jobs—and let me inspect the evidence for each claim.""
- **useful because:** Current completed statuses can mean only that the Mac or relay accepted work, while playback and owner hearing remain unknown. This produces a causal timeline that explicitly separates observed facts, inferred links, and unknown delivery, with drill-down evidence instead of false certainty.
- **path:** relay supplies job and announcement state plus device registry freshness → mac-planner supplies pipeline events, action receipts, browser spool, and permission state → browser-extension supplies command/result and tab provenance when a browser action was involved → pendant contributes beacon/playback telemetry when connected → unified presents a short spoken digest and links each claim to its source receipt
- **model tier:** Cheaper background model clusters and ranks events; realtime is used only to answer the owner's follow-up about one claim. Deterministic rules must label 'socket bytes', 'Mac executed', and 'owner heard' separately.
- **latency:** Digest in under 2 seconds from cached snapshot; evidence drill-down under 1 second for local records and bounded at 4 seconds for relay reads.
- **cost:** Low: one small summarization call per digest, with event metadata rather than raw audio or page text. Storage and network reads dominate, not model tokens.
- **security:** Never expose raw browser URLs, audio, or secrets by default. Redact claims and require confirmation before revealing sensitive evidence. Preserve source timestamps and freshness so stale records cannot masquerade as live facts.
- **missing:** Fix the unresolved read_continuity_snapshot grant to resolve to GET /ops/snapshot and GET /pipeline (current call returns unresolved at score 0.447); A provenance-preserving join key across relay jobs, Mac pipeline IDs, browser command IDs, and pendant playback events; A UI/voice renderer that shows confidence and the exact reason a claim is only inferred

### ""Make this a private conversation, and later prove that no transcript, browser content, recording, or action residue was retained anywhere.""
- **useful because:** Today 'private' is a preference, not an end-to-end fact: relay jobs, announcements, audio, Mac traces, browser spool, and model context have different retention behavior. The owner should be able to invoke a mode whose boundary is enforced across every body and whose completion is auditable, rather than trusting a single delete button.
- **path:** pendant receives a local privacy-mode indication and buffers no routine content to its failure store → relay issues a privacy-session nonce, rejects persistence for that nonce, and returns signed expiry/deletion receipts → mac-planner tags pipeline, job, action-ledger, and TTS artifacts with the nonce and prevents them entering durable stores → browser-extension uses the nonce to suppress capsule/provenance capture and reports whether any command or result escaped the boundary → unified presents a compact deletion/non-retention certificate and flags any surface that could not attest
- **model tier:** Deterministic policy and cryptographic receipts; no model needed for enforcement. Use the cheaper text tier only to explain a certificate. Realtime handles the spoken mode toggle and status.
- **latency:** Privacy mode must become active before the next audio frame or browser command (under 150 ms locally); certificate generation under 2 seconds after the session closes.
- **cost:** Low API cost; dominated by bounded receipt storage and key management. No raw content should leave the device in this mode.
- **security:** A dishonest or crashed node must not be able to claim deletion. Use per-session keys, authenticated append-only receipts, and an explicit 'unverifiable' result when a node was offline. Never promise cryptographic erasure from media that cannot support it; expose the exact residual metadata and its retention policy.
- **missing:** A cross-node privacy-session protocol with a nonce, expiry, and per-surface retention contract; Enforcement hooks before relay job creation, Mac pipeline/action/audio writes, and browser evidence capture; A tamper-evident receipt chain and a verifier the owner can inspect offline; Firmware-visible privacy state that survives a dropped link without writing ordinary conversation data

### ""While I’m away, prepare this but do not execute it unless two independent sources agree it is exactly the condition I named; otherwise wake me with the disagreement.""
- **useful because:** This turns unattended automation from a brittle trigger into a bounded commitment. A calendar, browser state, or incoming message can be stale or ambiguous; requiring corroboration protects the owner while still allowing useful work overnight.
- **path:** relay holds the expiring commitment and wakes the pendant if it cannot be resolved → browser-extension supplies authenticated page/session evidence → mac-planner checks local Calendar, Reminders, Mail, or filesystem evidence through granted automation → faculty-judgement compares independent timestamps/content hashes and decides ready, blocked, or disagreement → faculty-action executes only a signed ready commitment and returns a receipt to the relay and pendant
- **model tier:** Deterministic predicates and hashes for the safety gate; cheap background model only extracts candidate facts. Realtime is reserved for the owner's disagreement summary.
- **latency:** Checks on schedule or event arrival; decision under 1 second after both sources are available. A disagreement alert should reach the pendant within 5 seconds.
- **cost:** Low: mostly local reads and small relay metadata. Model cost only when natural-language conditions need extraction.
- **security:** Commitments must expire, be scoped to exact accounts/tabs/files, and never infer consent for side effects. Store hashes and source identities rather than message bodies by default; require explicit approval for external sends, purchases, or deletion.
- **missing:** A commitment schema with expiry, source quorum, exact predicate, and side-effect scope; Authenticated event subscriptions from Mac and browser rather than polling snapshots; A judgement-to-action lease that cannot execute unless quorum and freshness checks pass; A pendant alert path that distinguishes disagreement from ordinary failure


## Changes it proposed to its own stack

### `context` — Build a cross-surface recovery capsule that snapshots the owner's active task as an encrypted, resumable bundle: intent, exact browser session/tab, Mac app/document locations, pending jobs, last confirmed side effect, and unresolved questions. Replicate only the encrypted bundle to the relay; rehydrate it on the Mac or pendant after a crash or overnight gap, with each field carrying its source and freshness.
- **owner gets:** If the Mac crashes, the browser session expires, or the owner changes surfaces, they can say “continue where I left off” and get the real task—not a generic summary or a false completed status.
- effort: High: define a versioned encrypted bundle, capture hooks in planner/browser/action ledger, relay replication, and a rehydration flow that refuses stale or secret fields.  ·  risk: A stale task capsule could cause duplicate or wrong actions. Every side effect needs an idempotency key and a visible resume preview; if any required source is stale or unavailable, resume becomes read-only.
- cost: Small storage and bandwidth cost for encrypted metadata; no raw audio or full page bodies by default. Occasional cheap summarization cost when compressing the bundle.  ·  latency: Capture incrementally during work; resume preview under 2 seconds from local cache, with relay fallback bounded by network latency.
- security: High-value state must be encrypted per owner/session, with browser secrets and tokens omitted. Relay stores ciphertext and expiry metadata only; local key loss intentionally makes recovery impossible.
- depends on: A stable join key spanning pipeline runs, action receipts, browser commands, and relay jobs; A resumable action protocol with idempotency and explicit stale-state refusal; A user-visible resume preview and revocation path


## What it asked for

_Nothing._
## Its own summary

Round 167 established a major change: the Mac agent is now genuinely observation- and action-capable. GET /observe and GET /ops/snapshot report Accessibility and Screen Recording granted, inputReachability=verified, secureInput=false, uiActionsWillReachTheScreen=true, permissions.ready=true, browser bridge online with 9 Safari tabs and zero pending commands, and relay/mac bridge online. I recorded that as a verified finding and informed faculty-action. I proposed three owner-facing capabilities: presence-aware action gating across Mac/browser/relay; a USB bench test that distinguishes serial, firmware, relay, speech, and playback failures without pretending LTE registration; and a confidence-ranked return-from-absence account that separates Mac execution, relay socket acceptance, and owner hearing. The continuity snapshot grant itself is unusable: its call resolved to nothing (nearest GET /ops/snapshot, score 0.447), so the third capability needs that resolver fixed or a direct authenticated snapshot route.

**Biggest unknown:** There is still no trustworthy live pendant playback fact. The registry has no nRF9160, and completed pipeline/relay states do not prove receipt or hearing. I still need a working cross-surface snapshot resolver, a read-only USB serial probe for the physically connected chips, and—when firmware is connected—a device-originated playback event joined to the relay job.

