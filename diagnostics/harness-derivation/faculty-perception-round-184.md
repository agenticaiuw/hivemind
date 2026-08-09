# Harness derivation — faculty-perception — round 184

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-perception-permissions** — Live /ops/snapshot at 2026-08-08T22:15Z reports AI Pendant Agent Accessibility trusted=true, Screen Recording granted=true, requiredMissing=[], ready=true; Safari browser bridge online with one pending command and DoorDash tab.
  - evidence: read_continuity_snapshot(include relay,pipeline) invoked GET /ops/snapshot HTTP 200; body status.permissions and status.browser.

## Capabilities it proposed

### "“I got interrupted—show me exactly where I was in the browser and let me resume that task, without guessing what had already happened.”"
- **useful because:** Today catch-up can report jobs and browser spool but cannot prove the exact authenticated tab state or distinguish a staged form from a submitted transaction. This would let the owner resume a real web task from a browser snapshot, with a grounded diff and an explicit stop before any irreversible action.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** Background model builds a compact state summary and compares the saved browser evidence; realtime only handles the owner's spoken resume/stop command. Vision is invoked only if DOM/browser evidence is insufficient.
- **latency:** 3–8 seconds to gather browser state and render a diff; under 500 ms to answer a spoken stop. No action is taken until the owner confirms the proposed next step.
- **cost:** Roughly $0.01–$0.08 per resume, dominated by one vision call; cheap text comparison and browser polling are negligible.
- **security:** Authenticated page content stays on the Mac unless the owner explicitly asks for relay help. Persist a redacted capsule/hash and tab/session pseudonym, never passwords or full payment fields. Require confirmation for submit, purchase, send, delete, or navigation away; report evidence age and whether it came from DOM or screenshot.
- **missing:** A resumable browser checkpoint record that joins browser commandId, tab/session, evidence capsuleId/content hash, and the last safe action; A browser-side read-only snapshot/diff action for the extension, plus a resume endpoint that refuses to act when the checkpoint is stale or the page hash changed; Mounting the existing browserProvenance/evidence capsule routes so the owner can inspect and revoke the checkpoint

### "“Before you send, buy, delete, or publish anything, tell me what each surface independently says will happen, and stop if they disagree.”"
- **useful because:** A browser can show one state while the Mac ledger, relay job, or page has moved on. The owner needs a perceptual safety gate, not another action planner: a short spoken quorum report with the exact target, current page hash, intended side effect, and freshness of each observation.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** Cheap background model normalizes observations and detects disagreement; realtime speaks the concise report and collects the owner's yes/no. Vision is fallback only for visual-only controls.
- **latency:** 1–3 seconds for the quorum report, with an immediate local stop path on the pendant if any source says stale, changed, or unknown.
- **cost:** About $0.005–$0.04 per check; the cost is a small structured-model call, with vision adding $0.03–$0.15 only when needed.
- **security:** Never transmit secrets or raw page bodies by default. Use redacted evidence capsules, content hashes, action-ledger prestate/poststate, and relay receipt IDs. Confirmation must bind to the exact hash and action parameters; if the page changes, require a new confirmation. The pendant must fail closed offline rather than treating relay acceptance as consent.
- **missing:** A cross-surface observation schema with a common monotonic observationId and freshness/authority fields; A relay-to-Mac receipt join for browser command, action ledger, and any announcement/job; current completion is not proof of hearing; A pendant-local confirmation token that expires and is bound to the displayed hash/action, then is verified by the Mac before execution

### "“What do you currently believe about me that might be wrong or machine-inferred rather than something I told you?”"
- **useful because:** The system currently injects a pinned, high-confidence machine-written timezone preference that contradicts the Mac's actual timezone. It can silently steer every future answer. This audit would expose provenance, contradictions, age, confidence, and injection frequency before a bad fact becomes an action.
- **path:** mac-planner → mac-terminal → browser-extension → relay-realtime → pendant
- **model tier:** Background model periodically compares memory facts, machine context, filesystem/runtime observations, browser locale, and relay device claims; realtime presents only the few conflicts that matter and asks whether to correct them. No action is taken by the auditor.
- **latency:** A scheduled audit can take 10–30 seconds; an on-demand spoken answer should return a ranked top five within 2 seconds from a cached report.
- **cost:** About $0.01–$0.05 per audit, dominated by one structured comparison; scheduled audits can use a cheaper background tier.
- **security:** Treat source.origin as evidence, not intent. Do not upload private fact values or browser contents to the relay; send classifications, hashes, and minimal excerpts. Never rewrite a fact automatically. Corrections require explicit owner confirmation and retain an audit tombstone showing old/new provenance.
- **missing:** A contradiction/provenance report that joins memory facts with machine-context observations and records why a value was flagged; A safe owner-facing correction workflow for pinned facts (including source origin and downstream prompt impact) with explicit confirmation; A scheduler and bounded cache for the report, plus a pendant summary that works when the Mac is temporarily unreachable

### "“When I take the pendant off, automatically stop exposing private pages, messages, and spoken announcements; when I put it back on, restore only what I explicitly unlock.”"
- **useful because:** The system currently knows whether the Mac and browser are online, but not whether the intended human is actually wearing the conversational endpoint. A stolen session, an unattended open tab, or a queued announcement can expose private information. This makes physical possession a privacy boundary across all surfaces rather than trusting network reachability.
- **path:** pendant → browser-extension → mac-planner → relay-realtime → mac-vision
- **model tier:** A small background policy evaluator handles signed presence leases and local redaction/locking; realtime is used only when the owner asks to unlock or override. No expensive model is needed for the normal path.
- **latency:** Presence loss should close or redact sensitive browser surfaces and pause speech within 1–2 seconds; restore requires an explicit spoken or button confirmation after re-wear.
- **cost:** Negligible model/API cost; storage and crypto are local. Hardware cost depends on adding a skin/contact or clasp sensor, roughly a few dollars and milliwatts.
- **security:** Presence must be device-originated and cryptographically bound to the pendant, not inferred from USB, relay connectivity, or voice biometrics. Fail closed on stale leases, replay, or clock uncertainty. Never transmit raw sensor data; relay only signed presence state. Recovery must provide a physical-button path so the owner is not locked out.
- **missing:** A wearable-presence signal and signed monotonic lease in pendant firmware; A relay policy that invalidates speech/announcement delivery and exposes presence freshness; Browser and Mac local enforcement hooks that hide/lock sensitive surfaces and pause queued actions without sending their contents to the cloud

### "“That wasn’t what I said—show me exactly how my utterance became that action, and let me correct the record without replaying the action.”"
- **useful because:** A mistaken transcription or noisy capture can currently become a real Mac/browser action, while the owner has no compact, inspectable chain from microphone quality to transcript to plan to execution. This gives the owner a reversible dispute workflow: identify the failing stage, suppress the disputed interpretation, and preserve an honest correction rather than silently rewriting history.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension
- **model tier:** Background model assembles a structured causal trace and compares transcript alternatives; realtime explains it in plain speech and accepts a correction. Use the expensive realtime tier only for the live dispute conversation.
- **latency:** Initial trace under 3 seconds from a spoken dispute; immediate local cancellation for any still-pending action. Historical forensic detail may load asynchronously.
- **cost:** About $0.01–$0.06 per dispute, dominated by alternative transcription or summarization; hashes and ledger reads are local and cheap.
- **security:** Audio and transcript are highly sensitive. Keep raw audio local and time-limited; relay receives only quality metrics, hashes, and redacted text unless the owner explicitly requests playback. A correction must never be treated as proof the original action was authorized; require a separate confirmation for compensating actions.
- **missing:** A durable causal join from capture-integrity sequence to transcript, model turn, plan, action-ledger step, browser command, and receipt; An owner-visible dispute endpoint that returns stage-by-stage evidence and alternative interpretations without exposing secrets; A quarantine state for disputed commands and a correction/tombstone record consumed by judgement and future memory

### "“Someone else is nearby—switch to private mode now, stop sending room audio to the cloud, and tell me what was retained.”"
- **useful because:** The pendant's microphone is worn in shared spaces, but today there is no perceptual boundary between a private utterance and a conversation involving another person. A local bystander-risk detector would pause uplink before sensitive speech leaves the device, give a distinct haptic/audio cue, and provide a truthful retention summary when privacy resumes.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal
- **model tier:** A tiny on-device classifier handles voice activity, speaker-count change, and wake-phrase confidence; background text logic summarizes retention. Realtime is used only after privacy mode is safely engaged.
- **latency:** Local mute within 100–300 ms of detecting a second speaker or loss of wake-phrase confidence; owner can override with a physical button. Retention summary under 2 seconds after reconnect.
- **cost:** No per-event API cost while local; occasional summary costs under $0.01. Firmware flash/RAM work is the dominant cost.
- **security:** Raw audio used for detection must remain in volatile buffers and be discarded on mute; do not upload speaker embeddings or bystander identities. Fail closed on classifier uncertainty and link loss. Clearly distinguish 'uplink blocked' from 'already transmitted' and expose any buffered/offline audio count.
- **missing:** An on-device shared-space/privacy classifier and hard audio-uplink gate in the nRF9160/bridge path; A relay protocol carrying privacy state and a retention receipt, including whether any frames left the device before the gate; A Mac/relay mode that suppresses queued announcements and browser/action narration while private mode is active, with a physical recovery path


## Changes it proposed to its own stack

### `context` — Make every live perception result carry an explicit authority tuple: source surface, observedAt, freshness deadline, provenance kind (owner-stated/machine-observed/inferred), content hash or state hash, and contradiction set. Add a bounded, redacted 'perception ledger' that records only these tuples and tombstones, not raw page/audio content, and expose a single read route for judgement/action.
- **owner gets:** The owner would hear “the browser says the order is still in the cart, but the relay receipt is stale and the Mac saw a changed page” instead of a confident action based on mixed-age guesses. It also makes the known machine-authored timezone error visible and correctable.
- effort: Medium: adapter writers around existing memory, browser provenance, pipeline, relay receipt, and device status sources; one bounded store and one authenticated read route. No new model is required.  ·  risk: A bad authority ranking could hide a real conflict; preserve every conflict as unknown and fail closed for irreversible actions. If the ledger is unavailable, fall back to current behavior but label results unverified. Test clock skew and relay restarts.
- cost: Negligible storage and API cost; one small structured comparison call when requested, not on every voice turn.  ·  latency: Under 100 ms for cached reads; 1–2 seconds for a fresh multi-source comparison.
- security: Improves security by storing hashes, provenance, and redacted summaries rather than content. Requires strict redaction and owner-only access because even fact keys can be sensitive.
- depends on: Mount the existing local browserProvenance/evidence capsule routes; A relay response ID/content hash for cloud browser reads; A device-originated playback/health event once a pendant exists


## What it asked for

_Nothing._
## Its own summary

Established fresh live truth: Mac Accessibility and Screen Recording are now granted and ready; Safari bridge is online with an authenticated DoorDash tab and one pending command; relay/Mac bridge are reachable; pendant remains absent. Proposed three owner capabilities: evidence-grounded exact browser resume, fail-closed cross-surface action quorum, and a provenance/contradiction audit for machine-inferred beliefs. Proposed a bounded authority/freshness perception ledger, while noting it is close to existing envelope work.

**Biggest unknown:** No live pendant exists to verify device-originated health, confirmation, or playback; all pendant claims remain hypothetical until it registers. Still needed: cross-surface joins and relay browser IDs/hashes, mounting existing provenance routes, and an owner-approved correction path for pinned machine facts.

