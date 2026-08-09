# Harness derivation — mac-terminal — round 186

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/browser state** — Mac agent is healthy with fullControlMode and computer-use loop enabled; Accessibility and Screen Recording are granted. Safari browser bridge is online with 9 tabs, active X tab, zero pending commands. Relay is reachable and Mac bridge online, but the physical pendant remains unregistered/offline.
  - evidence: GET /ops/status and GET /browser/status returned HTTP 200 at round 186; devices discovery shows home-macbook-bridge online and cloudflare-contract-test offline.

## Capabilities it proposed

### "“What am I looking at, and what should I do next?” (or a short button press followed by that question)"
- **useful because:** This is the highest-value daily interaction: the owner gets an answer grounded in the actual screen, authenticated browser tab, active project, and the last Mac job instead of a generic model guess. It turns the worn device into an always-available orientation layer without requiring them to describe what is in front of them.
- **path:** pendant → mac-planner → mac-vision → browser-extension → relay-realtime
- **model tier:** Realtime for the short spoken answer; a cheap vision/text model performs OCR and tab/project summarization before the realtime turn, and the expensive model sees only the compact evidence capsule.
- **latency:** 2–4 seconds after the request; capture and browser inspection in parallel, then one short realtime response.
- **cost:** Usually one small vision/text call plus a brief realtime turn; roughly $0.01–$0.05 depending on screenshot size and speech duration. Most cost is image tokens, so crop to the active window and send only changed regions.
- **security:** The screenshot and authenticated tab metadata leave the Mac for inference. Redact password fields, payment pages, and off-screen tabs by default; show the source app/tab in the spoken answer. Never infer a task completion from pixels alone.
- **missing:** A coordinator that joins /capture output, active browser inspection, /projects/active, and the latest /jobs receipt into one time-bounded evidence capsule; A redaction/cropping pass for screenshots before upload; A pendant request event that can be initiated over the currently attached USB serial link when LTE is absent

### "“That Mac task failed—explain the real cause and retry it the right way.”"
- **useful because:** Today a failed shell job collapses exit status and error details, cannot be resumed, and cancellation cannot stop a running process. This capability would turn a dead-end failure into a bounded repair: identify whether it was timeout, missing dependency, transient network, or a bad path; propose the smallest correction; then rerun with the original job linked to the repair and report the result on the pendant.
- **path:** relay-realtime → mac-planner → mac-terminal → pendant
- **model tier:** A cheap background classifier diagnoses stderr/exit metadata and chooses a repair template; realtime is used only for the owner-facing explanation and explicit spoken retry request.
- **latency:** Diagnosis under 1 second from stored receipt; retry starts immediately and streams a one-line progress state to the pendant. Long commands remain asynchronous.
- **cost:** Near-zero for deterministic classes; $0.002–$0.01 for an uncommon model diagnosis, plus normal command cost. Do not resend full stdout; send bounded excerpts and structured exit data.
- **security:** The repair model sees command, cwd, stderr, and selected environment names. Secrets must be redacted. Automatic retry is acceptable for the owner's maximum-access policy only when the repair is mechanically local (timeout/path/temporary network); destructive or externally visible commands must be reported as non-retryable, not silently replayed.
- **missing:** Capture the actual exit code, signal, timeout-vs-killed distinction, and a redacted environment fingerprint in each run_shell receipt; A repair planner that emits a new action list with parentJobId and an idempotency key, rather than blindly duplicating side effects; A relay event carrying failure/repair state to the pendant's already-accepted truthful_action_status_beacon

### "“Do the browser task, then prove exactly what changed.”"
- **useful because:** Authenticated browser work is where a mistaken click can matter most. The owner should receive a compact before/after witness—target URL and title, relevant DOM text or download hash, action sequence, and whether the page actually confirmed the change—rather than the agent merely saying it clicked a button. The pendant can announce success or uncertainty while the browser session remains private on the Mac.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision
- **model tier:** Deterministic DOM/state comparison first; a cheap text model summarizes the diff. Realtime only speaks the short result or asks for clarification when the witness is ambiguous.
- **latency:** Read-only witness under 1 second; mutation plus verification under 5 seconds for normal pages. Long downloads become asynchronous tasks.
- **cost:** Usually no model call, or $0.001–$0.01 for summarization. Hashes and structured DOM selectors are far cheaper than screenshots.
- **security:** Never export full page content by default; scope evidence to the target element and origin. Strip tokens, email bodies, and form values. Keep authenticated evidence local unless the owner explicitly asks for relay delivery. A failed verification must be reported as unknown, not success.
- **missing:** A browser action transaction that records before-state, intended locator/value, after-state, and a cryptographic artifact hash as one durable receipt; A local-only evidence filter that understands sensitive DOM fields and authenticated-origin boundaries; A relay-to-pendant result envelope supporting success, changed-but-unverified, and no-change states

### "“Read and summarize what is on my screen, but keep everything confidential—nothing from this screen may leave my Mac.”"
- **useful because:** The owner can use the pendant around passwords, work, finance, or private messages without choosing between usefulness and privacy. Today the computer-use path can inspect the screen, but it does not offer a verifiable local-only mode; the owner cannot reliably know whether pixels or OCR context reached the relay/model.
- **path:** pendant → mac-vision → mac-planner → browser-extension → relay-realtime
- **model tier:** A local Mac OCR/layout model performs extraction and redaction; only the resulting short summary or synthesized audio leaves the Mac. Use realtime for the final spoken exchange, never for the raw screenshot.
- **latency:** Under 3 seconds for a normal screen; under 6 seconds for a dense document. If local inference is unavailable, fail closed rather than silently falling back to cloud vision.
- **cost:** No per-request cloud vision cost in the normal path; local CPU/GPU use is the dominant cost. A small realtime turn costs only the final response/audio tokens.
- **security:** The privacy promise must be technically enforceable: disable network upload for the raw capture, show a persistent local-only indicator in the Mac agent and a distinct pendant tone, keep raw pixels in memory only, and provide a receipt proving the model endpoint was local. Redaction must cover passwords, payment fields, tokens, private messages, and browser form controls. If any component cannot attest to local execution, return “cannot provide privately.”
- **missing:** A local-only vision/OCR execution path with network isolation for raw capture buffers; A signed privacy-mode receipt spanning capture, OCR, summarization, and audio delivery; A pendant-visible privacy state and fail-closed transport rule; A policy router that prevents /capture or browser inspection payloads from entering relay logging or cloud prompts while this mode is active

### "“For the next ten minutes, let you work only in this browser tab, then revoke access automatically.”"
- **useful because:** The owner gets practical delegation without permanently exposing every authenticated session. Today browser and Mac permissions are broad and durable; there is no spoken, tab-scoped lease whose expiry is independently enforced across the browser extension, Mac agent, and relay.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision
- **model tier:** Realtime handles the spoken lease request; enforcement is deterministic and does not rely on a model remembering the deadline.
- **latency:** Lease activation under 1 second; expiry and revocation must occur within 1 second of the deadline even if the model or relay is busy.
- **cost:** Negligible API cost; a small local timer and browser permission state are the main resources.
- **security:** The lease must bind to tab ID, window ID, origin, permitted action classes, issuing turn, and absolute expiry. The browser extension and Mac agent must reject commands after expiry independently, including queued commands. Revocation state must survive relay loss and Mac restart; no cloud component should be able to extend the lease silently.
- **missing:** A signed, tab-scoped capability lease understood by both browser extension and Mac agent; Local expiry enforcement in the extension and action dispatcher, including queued-command rejection; A pendant acknowledgment and unmistakable expired/revoked state; Lease audit records that omit page contents and credentials

### "“Find the exact text I was looking at earlier and bring me back to it.”"
- **useful because:** The owner often remembers a fragment, not a URL or filename. Today the system can inspect the current browser and Mac state, but it cannot search a private, time-indexed trail of the owner's previously viewed screen regions, selected text, browser pages, and project files, then restore the exact tab/scroll position with evidence.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision
- **model tier:** A local indexing process performs OCR/text hashing and retrieval; a cheap text model ranks matches. Realtime only asks a disambiguating question or speaks the selected result.
- **latency:** Under 2 seconds for the common recent-history window; under 8 seconds for a larger local index. Restoration should be explicit and deterministic after the match is selected.
- **cost:** No recurring cloud cost if the index and embeddings stay local; disk usage and periodic local embedding compute dominate.
- **security:** Index only explicitly opted-in windows/origins and encrypt it at rest. Never upload raw screen history. Support immediate purge and per-origin exclusion. Results must show timestamp and source so an old match is not mistaken for current state.
- **missing:** A local, encrypted, opt-in visual/text trail with retention and purge controls; Stable browser scroll/selection restoration primitives and Mac window-state capture; A retrieval protocol joining browser tab IDs, screen regions, project files, and pendant timestamps; A spoken disambiguation/result envelope that can restore only after the owner chooses a match


## Changes it proposed to its own stack

### `mac-harness` — Add a first-class detached task supervisor for long-running Mac work. run_shell actions that opt into task mode should launch under a small local supervisor with a stable task ID, captured pid/process group, monotonic start/finish times, exit code/signal, bounded stdout/stderr spool, heartbeats, and a boot-time reattach/reconcile pass. The relay polls task state independently of the HTTP request; a reconnecting pendant receives queued state transitions. Keep ordinary run_shell behavior unchanged, but expose task mode as a distinct action type so it cannot be confused with a completed synchronous job.
- **owner gets:** A build, export, download, test suite, or backup can keep running when the Mac agent UI, relay connection, or pendant link drops. The owner can leave, ask later “is that done?”, and receive the truthful result instead of a permanently processing job or having to rerun an uncertain side effect.
- effort: Medium-high: supervisor daemon/process-group handling, durable task state, bounded spool, boot reconciliation, and relay event integration; one to two weeks for a robust implementation plus crash tests.  ·  risk: Orphaned processes or duplicate reattachment could cause side effects. Use a stable task identity, process-group ownership, explicit adoption states (running/unknown/finished), and never rerun automatically after a crash. If reattach fails, report unknown rather than inventing completion. Cap output and reap abandoned tasks.
- cost: No model/API cost for supervision; small local disk writes and one low-rate relay poll/heartbeat per active task. CPU overhead is negligible outside active tasks.  ·  latency: Adds under 100 ms to task launch and makes status queries immediate; completion notification is event-driven rather than waiting for a request timeout.
- security: The supervisor inherits the same deliberate maximum-access policy, but should record a redacted environment fingerprint and never persist raw secrets in the spool. Process-group metadata and command strings stay in the authenticated local job store.
- depends on: A new task-mode action and stable task record schema; Repair the existing job↔ledger join and close ledgers at completion so task state is auditable; A relay task-status event consumed by truthful_action_status_beacon; Boot-time reconciliation that distinguishes an exited child from an unknown child


## What it asked for

_Nothing._
