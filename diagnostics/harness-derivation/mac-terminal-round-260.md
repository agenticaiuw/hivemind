# Harness derivation — mac-terminal — round 260

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I got interrupted—continue the task I was doing.”"
- **useful because:** This would be the system's single most useful everyday capability: it turns the pendant, Mac, browser, and relay into one continuity layer instead of making the owner restate context after a crash, dropped link, or closed conversation. It should recover the last unfinished action, the active Safari tab/session, the project and the exact step that last completed, then either continue automatically for reversible work or speak one precise question for the blocked step.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the cheap background model to assemble and summarize the recovery capsule; use realtime only to hear the owner's request and speak the one missing decision. Let the Mac executor perform the actual continuation.
- **latency:** Under 2 seconds to speak what was recovered; under 5 seconds to resume a reversible action. Do not wait on a full transcript or vision pass unless the recovered step requires it.
- **cost:** Usually one small background-model call (roughly $0.01–$0.05 depending on capsule size); the dominant cost is avoidable context re-sending, so pass IDs and short receipts rather than raw logs/screenshots.
- **security:** The capsule may contain a private browser URL, project path, or page title. Keep it on the relay/Mac, redact page bodies and tokens, and require the existing owner confirmation semantics only when the recovered step is consequential. Never claim a step completed unless its receipt says so.
- **missing:** boot-time reconciliation that converts stale processing jobs into interrupted recoverable jobs; a durable join between jobId, action-ledger id, browser command/session, and pendant turn id; an idempotent resume endpoint that replays only the first incomplete action; a compact recovery-capsule schema with redacted browser provenance

### "“If something you ran fails, fix what you can and tell me only if I need to intervene.”"
- **useful because:** Today a failed shell or browser step is a dead end: the owner gets an error string, no exit code, no diagnosis, and no safe continuation. This would turn failures into useful outcomes by classifying the failure, collecting one targeted diagnostic, retrying only idempotent steps, undoing a partially completed reversible action when appropriate, and speaking a short intervention request only when recovery is impossible.
- **path:** relay → mac-bridge → browser → pendant → dashboard
- **model tier:** Use deterministic rules for exit status, timeout, known transient network/browser errors, idempotency, and undo receipts. Use a cheap background model for unfamiliar stderr grouping; realtime only for the final interruption question.
- **latency:** Add no more than 1 second before a retry and 10 seconds for a repair attempt. A failed long-running process must surface its state immediately rather than waiting for the entire recovery policy.
- **cost:** Most cases are zero model calls; unfamiliar failures cost roughly $0.01–$0.05. Mac diagnostics and retries dominate latency and machine use.
- **security:** Automatic retry must be limited by action identity and explicit replay safety, never duplicate email, purchases, deletion, or external submissions. Keep stderr local by default, redact environment variables and secrets, and show the owner the exact action and repair attempted. Pendant feedback must say retrying/failed, never completion by inference.
- **missing:** capture and retain shell exit code, signal, timeout, and process identity; wire the existing retry/idempotency engine into real /execute jobs; an action-level repair policy with explicit replaySafety and undo metadata; abortable child processes so cancellation and recovery can stop a running shell; a durable failure capsule linked to the job, ledger, browser command, and pendant turn

### "“Only interrupt me when my Mac is blocked waiting for me, and let me resolve the block from the pendant.”"
- **useful because:** Long jobs currently fail silently or sit waiting for a browser login, permission sheet, CAPTCHA, missing file chooser, or a question from the planner. This would convert those moments into a single actionable pendant notification: what is blocked, which app/site owns it, how long it has waited, and one or two safe responses. The owner could say “allow once,” “skip,” “cancel,” or “show me,” while the Mac/browser carries out the selected continuation.
- **path:** mac-bridge → browser → relay → pendant → dashboard
- **model tier:** Use deterministic detectors for job states, browser command waits, accessibility permission prompts, and planner asks; use a small model to compress the block into a sentence and map speech to the advertised options. Realtime is appropriate only for the short exchange.
- **latency:** Detect within 2 seconds of a block and speak within 5 seconds. Keep notifications suppressed while the owner is actively interacting with the blocking app, with a 30-second escalation fallback.
- **cost:** Usually zero or one small classification call (under $0.02); the main cost is the Mac/browser event stream and maintaining a small pending-block record.
- **security:** Do not expose page contents or secrets in a notification. A pendant command must be scoped to the exact job/command ID and expire quickly; “allow” must never silently broaden permissions. CAPTCHA and login completion should remain owner-driven in the browser, with the pendant only selecting resume/skip/cancel.
- **missing:** a first-class blocked/waiting state and reason enum on jobs and browser commands; Mac accessibility/browser event adapters that identify permission prompts, file choosers, authentication waits, and planner questions; a push path from Mac to relay and pendant with acknowledgement and expiry; job-scoped response actions that resume exactly the blocked step rather than rerunning the whole plan

### "“I was away—what changed on my Mac and in my browser since I last used the pendant?”"
- **useful because:** Instead of replaying every notification, the owner gets a bounded change digest tied to their last active session: files created or modified in the active project, jobs that completed or failed, browser tabs/navigation/downloads that changed, and anything that is still waiting. It answers the practical return-from-lunch question while preserving the owner's attention and avoiding raw transcript or page dumps.
- **path:** pendant → mac-bridge → browser → relay → dashboard
- **model tier:** Use deterministic filesystem mtimes, job receipts, browser command/provenance records, and session timestamps to assemble the candidate set. Use a cheap background model to rank and phrase the digest; realtime only reads it aloud on request.
- **latency:** Return a spoken five-item maximum digest within 3 seconds; generate deeper details only after the owner asks for one item.
- **cost:** Usually one small summarization call, about $0.01–$0.03; local file/job/browser queries dominate. No screenshots or page bodies should be sent to the model.
- **security:** Scope changes to the active project and browser sessions owned by this pendant, redact filenames/URLs that match secrets, and retain only hashes, timestamps, and short titles in the digest cache. Never imply that a file was changed by the agent unless a matching receipt exists.
- **missing:** a durable last-seen watermark shared by pendant turn, Mac session, project, and browser session; a change-feed endpoint that returns only deltas since that watermark; browser download/navigation events with timestamps and provenance rather than only current tab state; a compact digest cache with acknowledgement so repeated button presses do not repeat the same changes

### "“Don’t just tell me you clicked it—prove that the thing actually happened.”"
- **useful because:** The owner currently receives execution receipts, not outcome evidence. A click can succeed while a form rejects, a download is partial, or a browser session navigates away before the server commits. This capability would attach a declared postcondition to each consequential task, independently verify it through the browser/Mac state after execution, and speak either verified, disproven, or unknown with the evidence used. It prevents the most damaging failure mode of a personal agent: confident claims that are only action logs.
- **path:** browser → mac-bridge → relay → pendant → dashboard
- **model tier:** Use deterministic postcondition checks first: URL/state changes, DOM confirmation text, file stability plus hash, job exit status, and API-visible result where available. Use a cheaper model only to interpret unfamiliar confirmation pages; realtime only reads the concise verdict.
- **latency:** Return an initial action result immediately, then a verified verdict within 2–5 seconds. If verification needs polling, speak 'checking' and expire to unknown rather than claiming success.
- **cost:** Usually zero model calls for structured checks; unfamiliar pages cost roughly $0.01–$0.04. Browser polling and local hashing are the dominant costs.
- **security:** Evidence may contain private URLs, filenames, or confirmation text. Keep raw evidence local, expose only a redacted excerpt and source type, bind it to the exact action/job, and never treat a screenshot or model interpretation alone as proof for money movement, deletion, or messaging.
- **missing:** a typed postcondition contract on actions (for example file_hash, page_state, download_complete, or server_confirmation); post-execution verifier hooks for Mac and browser actions, including stable-download detection and DOM/state assertions; a durable evidence record linked to the action receipt and pendant turn, with verified/disproven/unknown semantics; a spoken pendant response that distinguishes accepted, completed, and independently verified


## What it asked for

_Nothing._
## Its own summary

Round 260 produced three non-duplicate owner-facing capabilities: resume an interrupted task across pendant/Mac/browser/relay; automatic failure repair with truthful retry/undo reporting; and pendant-routed blocked-job intervention. A fourth return-from-away change digest was also recorded. The live inventory confirms Safari and the Mac bridge are online, full-control/computer-use are enabled, and the two-chip USB diagnostic schema still does not resolve to a real tool. The bench-health proposal was correctly rejected as an existing backlog item rather than rephrased.

**Biggest unknown:** I still need an implemented, bounded USB serial reader/framing parser (or an equivalent typed Mac action) to establish live nRF9160/ESP32 health. The granted schema is only a specification; it cannot be called. I also still need the missing cross-record wiring: job↔ledger↔browser command↔pendant turn IDs, boot reconciliation, and a resumable blocked-step protocol.

