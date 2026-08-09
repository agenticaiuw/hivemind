# Harness derivation — faculty-action — round 180

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “handle this” while wearing the pendant, carry the request through the Mac and my authenticated browser as one transaction: prepare the exact change, show me a short spoken summary and a physical-confirmation prompt, commit only after my deliberate gesture, independently verify the resulting app/browser/file state, and if verification is unknown leave a resumable recovery card instead of claiming success."
- **useful because:** This is the core promise of a wearable agent: one spoken request becomes a safe, truthful real-world result across surfaces, rather than a plan or an unverified click. It composes the pendant, relay, Mac planner, browser session, and perception into one owner-visible operation.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-judgement → faculty-action → faculty-perception
- **model tier:** Realtime only for the short conversational summary; use the local planner for execution and a cheaper background verifier/recovery model after commit.
- **latency:** 2–5 s to stage and ask; 1–8 s to execute; verification receipt within 2 s after the action. Long browser operations may continue asynchronously with pendant progress cues.
- **cost:** Usually under $0.03 per operation; browser/Mac calls dominate latency, not tokens. Realtime is used for at most one short turn.
- **security:** Never send page secrets or form contents to the pendant. Require the existing physical transaction latch for consequential commits, scope the browser command to the named tab/session, redact evidence, and treat failed/unknown verification as unknown—not success. Ask before irreversible or external communication actions.
- **missing:** A first-class operation envelope joining action_id/attempt_id, physical approval nonce, executor receipt, and verify_operation_step provenance.; A recovery-card state machine for partially completed or unknown operations.; A compact pendant rendering of the canonical action summary and verification result.

### "Give me a privacy curtain I can trigger with one deliberate pendant gesture: immediately stop sending live audio and page/context telemetry, pause queued browser/Mac work, visibly acknowledge the private mode on the pendant, and resume only after a second deliberate gesture or an explicit spoken request once the curtain is down."
- **useful because:** A wearable agent is physically present during sensitive moments. The owner needs a fast, trustworthy way to make the entire hive go dark without finding the Mac, closing a browser tab, or trusting a cloud timeout. This combines local hardware authority with relay and Mac enforcement.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-action
- **model tier:** No model is needed for the safety path. Use deterministic firmware and relay/Mac policy; optionally use a cheap background model only to summarize work paused during the curtain.
- **latency:** Local LED/audio acknowledgement under 100 ms; relay revocation and Mac/browser pause within 500 ms when connected. Offline curtain must still work immediately and remain latched across reconnect.
- **cost:** Negligible token cost; one small authenticated control event and at most a few queued status messages per transition.
- **security:** The device must fail closed on link loss and boot into curtain if its privacy state is uncertain. Do not rely on a spoken command to enter privacy mode. Do not store microphone audio merely because the curtain was activated. Resume must not replay or submit paused commands without a fresh approval.
- **missing:** A firmware-resident privacy latch with monotonic counter and crash-safe persistence.; Relay fan-out that revokes active audio/context streams and marks queued jobs paused.; Mac/browser hooks that stop capture, redact pending inspection payloads, and expose a deterministic paused receipt.

### "Let me ask “what changed since I left?” and get a private, evidence-backed digest of only the Mac/browser changes that happened after a physical pendant bookmark: new or modified files, completed/failed jobs, changed tabs or drafts, and unresolved approvals, with each item linked to an undo or resume action."
- **useful because:** The owner can leave a task mid-flight and return without reconstructing state from dashboards. The bookmark is made on the wearable, while the Mac and browser provide the facts and the relay preserves the checkpoint, so no single surface can provide this continuity alone.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-action
- **model tier:** Use deterministic logs, job receipts, browser inspection hashes, and file metadata for collection; use a cheaper background summarizer for the spoken digest, with Realtime only if the owner asks during a live conversation.
- **latency:** Bookmark acknowledgement under 300 ms. Digest in 2–5 s for normal history; large histories can stream a first three-item summary and continue asynchronously.
- **cost:** Typically $0.005–$0.02 for summarization; collection is local and dominates neither cost nor privacy exposure.
- **security:** Persist hashes and metadata by default, not page contents or secrets. Require physical confirmation before undo/resume. Scope the comparison to the owner’s bookmark and expire it after a configurable period. Clearly label inferred versus directly observed changes.
- **missing:** A durable cross-surface bookmark ID emitted by the pendant and relay.; A normalized change ledger joining Mac jobs, browser session mutations, pipeline events, and verifier provenance.; A spoken digest renderer with per-item action affordances.

### "Before I let the agent do something consequential, let me ask “what would happen if you did this?” and receive a non-mutating rehearsal: the Mac and browser run against an isolated snapshot or generated fixture, the pendant speaks the expected changes and risks, and I can approve the real operation only if the rehearsal matches my intent."
- **useful because:** Today the owner must approve an action without seeing its likely concrete effect. A dry-run makes dangerous automation understandable before it touches a real account, file, or message. It requires the wearable for the decision, the relay for orchestration, and Mac/browser isolation for a credible rehearsal.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-judgement → faculty-action → faculty-perception
- **model tier:** Use deterministic cloning/fixture execution where possible; use a cheaper reasoning model to summarize differences. Reserve Realtime for the owner’s short spoken question and answer.
- **latency:** A simple rehearsal in 2–5 seconds; complex browser workflows may return a staged preview within 10 seconds and continue in the background.
- **cost:** Approximately $0.01–$0.05 per rehearsal, dominated by isolated browser/VM or fixture setup and diff generation.
- **security:** The rehearsal must not contact external services, send messages, or mutate the owner’s real files. Secrets must be replaced with fixtures. Clearly label effects that cannot be simulated faithfully. Real execution still requires the existing physical confirmation and independent verification.
- **missing:** A no-side-effects rehearsal executor for Mac and browser actions.; Snapshot/fixture adapters for common apps and authenticated web workflows.; A structured predicted-diff format that can be compared with post-execution evidence. 

### "Let me say “when I return to my desk, remind me where I left off” and have the system recognize a local return using the Mac becoming active plus the pendant reconnecting, then give me a private, short spoken handoff of the unfinished task—without GPS, continuous location tracking, or recording ambient audio."
- **useful because:** The owner loses context between leaving and returning. A local presence transition is more private and more reliable than location tracking, while combining the pendant’s physical proximity with Mac state and the relay’s durable task memory.
- **path:** pendant → relay-realtime → mac-planner → faculty-perception → faculty-action
- **model tier:** Use deterministic presence signals and job state collection; use a cheap background model to compress the handoff. Realtime is unnecessary unless the owner starts a conversation.
- **latency:** Detect return within 1–3 seconds of both signals being present; speak a three-item handoff within 5 seconds, with a quiet-hours suppression option.
- **cost:** Usually below $0.01 per return; local event handling dominates and no continuous model inference is needed.
- **security:** Store only coarse transition timestamps and task identifiers, never raw proximity traces or ambient audio. Require an explicit opt-in and a physical gesture to enable the routine. Do not reveal private browser or message content aloud unless the owner asks.
- **missing:** A signed local-presence event from pendant↔Mac attachment/reconnect.; A task checkpoint index spanning jobs, browser sessions, drafts, and approvals.; A privacy policy for spoken handoff content and quiet-hour behavior.

### "When I dictate a message containing sensitive details, let me say “protect the private parts”: identify names, account numbers, addresses, and secrets in the draft, replace them with explicit placeholders before anything leaves the Mac, read back only the redacted version, and let me approve each protected span from the pendant."
- **useful because:** The owner can use the wearable to compose quickly without accidentally disclosing private data. The Mac/browser retain access to the draft, while the pendant provides a physical, content-minimal approval channel and the relay coordinates policy without receiving the secrets.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-action → faculty-perception
- **model tier:** Use deterministic pattern detectors first; a local small model may classify ambiguous spans. Realtime should handle only the spoken command and redacted readback, never the original sensitive text.
- **latency:** Redaction preview within 1–2 seconds for ordinary messages; per-span approval feedback under 500 ms.
- **cost:** Near-zero for pattern matching; under $0.01 for ambiguous local classification. No cloud token cost if the original draft stays on the Mac.
- **security:** Original text and detected spans must remain local. Placeholders must be unambiguous and collision-resistant. Never auto-submit after redaction; require the existing physical approval for external sends. If classification confidence is low, over-redact and ask rather than expose.
- **missing:** A local redaction engine with deterministic detectors and confidence/provenance fields.; Browser/Mac draft transformation that preserves formatting while preventing secret leakage.; A compact per-span approval protocol that sends only span IDs and hashes to the pendant/relay.


## Changes it proposed to its own stack

### `integration` — Add a capability-negotiation and privacy-mode contract between the Mac agent, Safari extension, relay, and pendant. On heartbeat, the extension must report concrete operations it supports (inspect tab, locate field, draft, submit, observe URL) plus a per-operation sensitivity class; the Mac agent must refuse to enqueue an operation whose required capability is absent, and the pendant/relay must receive a human-readable blocker rather than a generic timeout. Keep page content local when visionUploadConsented is false, and attach the negotiated capability snapshot to every operation receipt.
- **owner gets:** Today Safari is online but reports capabilities:[], so a request can look executable while silently lacking the browser primitive it needs. The owner should hear “I can inspect this tab but cannot submit here” immediately, with no accidental upload of sensitive screenshots.
- effort: Moderate: define a small heartbeat schema, implement extension responses for existing actions, enforce preflight in the Mac planner, and include the snapshot in receipts. No new model required.  ·  risk: Older extensions may report no capabilities and make work appear blocked; recover by treating unknown as unsupported and offering the owner an explicit update/retry. A stale heartbeat could misdescribe a tab, so revalidate before commit.
- cost: Near-zero API cost; a few hundred bytes per heartbeat and receipt.  ·  latency: Adds one local preflight round trip, normally under 100 ms; avoids much longer failed computer-use loops.
- security: Improves security by preventing cloud vision upload when consent is false and by making sensitive browser operations explicit. Capability declarations are not authority; physical approval and postcondition verification remain required.
- depends on: Safari extension heartbeat schema and command capability implementation; Operation envelope joining planner intent, browser command, approval nonce, and verifier receipt; A deterministic local-only computer-use path when vision upload consent is false


## What it asked for

_Nothing._
