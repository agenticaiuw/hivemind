# Harness derivation — mac-terminal — round 165

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Do that Mac task, then prove to me what changed — not just that the command exited."
- **useful because:** A successful shell exit currently says almost nothing about the user's world, while failures lose the exit code. This produces a spoken, compact before/after proof: changed files or app/window state, exit status, duration, and an honest warning when the result cannot be verified. It is especially valuable when the owner is wearing the pendant and cannot inspect the screen.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension
- **model tier:** Use a cheap deterministic verifier for hashes, process status, active app, and browser tab metadata; reserve realtime model only for converting the evidence into a short spoken explanation.
- **latency:** Capture before-state under 500 ms, execute normally, capture after-state under 1 s, speak within 2 s of completion.
- **cost:** Near-zero model cost for structured diffs; modest local I/O for bounded file manifests. No cloud upload of file contents, only names, hashes, and typed state.
- **security:** Never snapshot arbitrary file contents or secrets. Redact paths outside the requested scope; hash only explicitly touched paths. The user must be told when a command had unbounded side effects and the system cannot establish a proof.
- **missing:** a typed postcondition contract on /execute (requested paths/apps/tabs and expected predicates); shell result capture of exit code, start/finish/duration, and original-vs-rewritten action; Mac-side before/after probes for files, foreground app, and browser session state; a receipt endpoint/payload carrying the diff and verification confidence

### "Take the result from the page I'm looking at, save it into the right project on my Mac, and tell me if anything was missing or changed."
- **useful because:** This is the daily seam between the browser's authenticated session and the Mac's filesystem: today each surface can act, but neither can safely attest that the page data became the intended local artifact. The wearable supplies the short instruction and receives a concise receipt while the browser keeps credentials in-browser.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-terminal
- **model tier:** A cheap structured extractor/diff handles DOM fields and file hashes; realtime is used only to clarify which visible record and destination the owner meant.
- **latency:** Visible-page inspection in 1 s, local write in 2 s, spoken receipt within 4 s; no page navigation unless explicitly requested.
- **cost:** Low: one structured browser inspection, one typed Mac write, and a small summary. Do not send full page HTML or credentials to the relay/model.
- **security:** The browser extension must return only explicitly selected fields and origin/title, never cookies or unrestricted HTML. The Mac writer must use a temporary file plus atomic rename, preserve the previous artifact, and report conflicts rather than silently overwrite. The spoken receipt should include destination and field count.
- **missing:** a browser command that exports a user-selected structured record with origin and selection fingerprint; a Mac action for atomic write plus hash/mtime comparison against the prior artifact; a relay transaction ID joining browser result, Mac receipt, and pendant speech; conflict detection when the page changes between inspection and extraction

### "Run this heavy Mac job when it won't get in my way, and let me know if the machine becomes unsafe to continue on."
- **useful because:** The system can launch work and can read bits of machine state, but it has no owner-facing execution that adapts to battery, AC, thermal/load, network, foreground app, and an explicit quiet window. This would let the owner delegate expensive jobs from the pendant without returning to a dead or overheated Mac, and would explain a pause rather than silently failing.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → unified
- **model tier:** Cheap deterministic policy evaluates battery/power/network/load and schedule; use the realtime model only for the initial natural-language constraint extraction and final spoken exception.
- **latency:** Acknowledge immediately; evaluate every 15–30 s. Pause or resume within 5 s of a threshold crossing.
- **cost:** Minimal model spend; bounded local telemetry and one durable scheduler record per job.
- **security:** Only coarse telemetry (power state, load band, foreground app) leaves the Mac. Never infer private activity from process names in spoken output. The owner chooses thresholds; default is pause, not kill, when conditions become unsafe.
- **missing:** a resource-aware job policy attached to /execute or /plan (battery, AC, network, load, quiet-hours, foreground-app predicates); Mac diagnostics routes for battery, load, thermal pressure, and active app with stable typed responses; scheduler wakeups and durable pause/resume state surviving agent restart; pendant/relay status events that distinguish waiting-for-capacity from failed

### "Put the terminal session I’m working in on my pendant so I can keep driving it by voice while I walk away from the Mac."
- **useful because:** The current Mac surface submits discrete jobs; it cannot hand an interactive PTY, prompts, curses UI, or streaming stdin/stdout to the wearable. This would make the pendant a true continuation of the owner's active terminal rather than a separate command launcher.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → audio bridge
- **model tier:** Realtime handles low-latency voice-to-keystroke and prompt interpretation; deterministic Mac code owns PTY bytes, resize, and session identity.
- **latency:** PTY output to audio/text acknowledgement under 250 ms; reconnect without losing the session after a short USB/LTE interruption.
- **cost:** Low ongoing model cost for short voice turns, plus bounded audio relay bandwidth. PTY output should be summarized locally unless the owner asks for verbatim text.
- **security:** The owner must explicitly select which terminal session is exported. Never expose arbitrary terminal output to cloud inference by default; redact secrets and require a local-only mode for sensitive sessions. Keep a complete input/output audit tied to the session.
- **missing:** a Mac PTY broker that allocates a session, captures process-group identity, supports stdin, resize, and reconnect; relay session routes for bidirectional framed PTY data and voice turn correlation; pendant UX for speaking a command, hearing prompts, and recovering from a dropped link; session expiry and explicit close semantics so an abandoned shell does not remain reachable

### "Find the first change that broke this project, prove the regression, and leave me a reviewable fix."
- **useful because:** Today the agent can run commands, but it cannot conduct a bounded, resumable bisect: choose good/bad revisions, execute the project's test or reproduction, classify flaky results, preserve evidence, and return a patch for review. This turns the Mac into an engineering instrument while the owner only has to answer ambiguous test questions from the pendant.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → unified
- **model tier:** A cheaper background model runs the deterministic bisect and test repetitions; realtime is only for clarifying the reproduction and reporting the final culprit.
- **latency:** Acknowledge in seconds; run asynchronously for minutes or hours with progress checkpoints and interruption-safe resume.
- **cost:** Model cost is limited to test-result classification and final explanation; local CPU/time and project test execution dominate.
- **security:** Operate only in a disposable worktree by default, never rewrite the owner's current branch, and capture commands, revisions, test output hashes, and patch diff. Network access and publishing a branch require explicit owner instruction; source stays on the Mac unless requested.
- **missing:** a project-aware bisect orchestrator with disposable worktree/branch management; typed test-run predicates and flaky-test repetition policy; durable checkpoints and evidence bundles that survive agent restart; a review artifact route exposing the candidate patch and proof without auto-committing

### "Watch for only the notifications I care about, read them to me on the pendant, and let me answer without opening the Mac."
- **useful because:** The owner currently has scheduled briefings and on-demand actions, but no low-noise interrupt layer that watches native Mac notifications, correlates them with the active app/browser session, and offers a voice reply. This would make the wearable useful while the owner's hands and eyes are elsewhere instead of requiring repeated polling.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → audio bridge → browser-extension
- **model tier:** A local deterministic filter handles app/sender/keyword rules; realtime is used only to summarize an accepted notification and transcribe an optional reply.
- **latency:** Detect within 2 s, speak a short alert within 5 s, and deliver a reply within 2 s after the owner confirms verbally.
- **cost:** Low if filtering and redaction happen locally; model spend occurs only for notifications that pass the owner's rules.
- **security:** Notifications can contain private messages, codes, and financial data. Keep capture local, redact configured classes, never read notification bodies aloud in public mode without a wake-word confirmation, and require per-app reply permissions. Store only a short-lived receipt.
- **missing:** a Mac notification observer with app/sender/body metadata and dismissal/reply handles; a persistent owner-configured priority/filter policy and quiet-location mode; relay push events and a pendant acknowledgement/reply protocol with deduplication; app-specific reply adapters, including a browser-session adapter where native reply is unavailable


## What it asked for

_Nothing._
