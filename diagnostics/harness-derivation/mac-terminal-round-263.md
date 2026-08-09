# Harness derivation — mac-terminal — round 263

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What changed while I was away, and what should I look at first?”"
- **useful because:** On returning to the Mac, the owner currently has to reconstruct state manually. A background checkpoint would compare the last known foreground app and Safari tab against current tabs, local project branches/diffs, newly downloaded files, and relay jobs, then produce a short prioritized delta with direct resume links. It uses the browser's authenticated reach and the Mac's filesystem without copying page contents into cloud memory.
- **path:** mac-planner → browser-extension → relay → dashboard
- **model tier:** background cheap model for periodic diffing and ranking; realtime only when the owner asks for the briefing
- **latency:** Checkpoint silently in under 3 s after a focus change; answer in under 2 s from cached deltas
- **cost:** <$0.003 per checkpoint if structured metadata is cached; one small model call for a multi-source summary
- **security:** Keep page text and local file contents on the Mac; relay receives hashes, titles, paths, timestamps and redacted findings unless the owner explicitly asks for detail. Never infer completion from tab focus. Git diffs and download names can contain secrets, so apply existing sensitivity labels and expiration.
- **missing:** Mac focus/tab/file checkpoint event source; a durable per-project baseline and comparison store; browser tab metadata diff with authenticated-session identity but no page-body upload; a cross-surface delta-ranking route; resume links that tie a delta back to the exact tab, job or file

### "“Take the result from the private site I’m viewing and put it into the local project, with a link back to exactly where it came from.”"
- **useful because:** This is the missing bridge between browser-only authenticated knowledge and Mac-local work. The browser can reach sessions the relay cannot, while the Mac can edit files and run tests. The system should extract only the owner-selected fields, preserve source URL/title/locator and a content hash, write a reviewable local artifact, and optionally run a project-specific import/test—without sending the private page or credentials to the cloud.
- **path:** browser-extension → mac-planner → relay → dashboard
- **model tier:** background model for schema mapping and import planning; realtime only for a terse success/failure answer
- **latency:** Preview in <3 s; write/import in <10 s; tests may continue as a tracked job
- **cost:** <$0.01 per transfer, dominated by one extraction/mapping call; zero model cost for already structured fields
- **security:** Require an owner-selected DOM region or explicit fields, not whole-page scraping. Keep raw bytes local; relay receives a provenance capsule and hashes. Treat downloads, scripts and imported content as untrusted. The local project path and command remain maximum-access per owner policy, but record exact mutations and make the generated artifact easy to undo.
- **missing:** browser-to-Mac structured selection/export protocol; local artifact writer with provenance sidecar and sha256; schema-mapping preview before mutation; project import adapters and test receipt; a browser command that returns selected-field provenance rather than only a screenshot/page snapshot

### "“When the local tests fail, find the matching issue in the authenticated tracker and prepare the update with the exact failure evidence.”"
- **useful because:** The Mac can run the test and the browser can reach the owner's private tracker, but today those are separate actions. This would correlate the local failure to an existing issue, attach a bounded log excerpt and commit/branch identity, and prepare—not silently post—the update. It saves the owner the tedious context switch while keeping the private tracker session in the browser.
- **path:** mac-planner → browser-extension → relay → dashboard
- **model tier:** background model for stack-trace/issue matching; realtime only to report the proposed update
- **latency:** Start correlation within 2 s of a failed test; proposal in <15 s; posting remains an explicit separate owner action
- **cost:** <$0.02 per failure, with most cost in one embedding or cheap text-match call; no cost when exact issue keys occur in output
- **security:** Send only bounded, redacted test evidence to the browser command. Never expose tracker cookies to Mac or relay. Treat issue comments as external content and do not execute commands copied from them. Drafts must be visibly separate from posted updates, with source commit and test command recorded.
- **missing:** test-failure event and bounded log redaction on the Mac; tracker search through the authenticated browser session; cross-surface issue matcher with confidence and citations; draft-comment artifact and explicit browser post action; a receipt joining local test, issue result and final post

### "“Reconstruct exactly what the computer and browser looked like at the moment that task went wrong, without recording me continuously.”"
- **useful because:** When an automation fails, today's job record has text and partial receipts but no synchronized visual/browser state, so the owner cannot explain or reproduce the failure. An event-triggered incident capsule would keep a short rolling local ring of window metadata, browser tab identity, command receipts, and—only when a failure occurs—the surrounding screenshots and relevant DOM snapshot. It gives the owner a precise replay point without an always-on microphone or continuous screen recording.
- **path:** mac-planner → browser-extension → relay → dashboard
- **model tier:** Background model for post-failure summarization; realtime is unnecessary unless the owner asks what failed
- **latency:** Capture the failure capsule within 1 s; render a replay in under 3 s
- **cost:** <$0.005 per incident for local metadata and one optional vision summary; storage is bounded by a rolling ring and short retention
- **security:** Keep the pre-failure ring on the Mac and encrypt it; redact password fields and sensitive browser origins. Upload only a selected capsule after the owner requests sharing. Never capture microphone audio. Make the trigger explicit and expire unpromoted capsules automatically.
- **missing:** A bounded rolling local ring for window/tab metadata and recent action receipts; Failure-triggered screenshot and DOM capture coordinated across Mac and browser; A synchronized monotonic timeline joining shell, browser and UI events; A local replay viewer with redaction controls; Retention/expiry and explicit export of an incident capsule

### "“Use my pendant as a physical presence key: when it is with me, unlock the Mac's private work context and let the browser fill approved credentials; when it leaves, revoke that access.”"
- **useful because:** The current pendant is a voice endpoint, not a trustworthy presence factor. The owner still has to unlock and context-switch manually, while browser sessions and Mac secrets remain disconnected. A cryptographically attested, revocable presence channel would make the system feel wearable: proximity can unlock a narrowly scoped workspace or approve a pre-declared fill, and loss of the pendant can immediately close that access.
- **path:** pendant → mac-planner → browser-extension → relay → dashboard
- **model tier:** No model should decide authentication; use firmware/OS cryptography and deterministic policy. Models may explain state but never mint or handle secrets
- **latency:** Presence verification under 500 ms; revoke on link loss within 5 s; no cloud round trip for ordinary unlock
- **cost:** <$0.01 per verification; requires a secure-element-capable pendant revision or protected key storage, plus Mac Keychain and browser-extension integration
- **security:** This is security-sensitive and must be opt-in per context, not a universal unlock. Use challenge-response, device-bound keys, short-lived leases, explicit loss/revoke flow, anti-relay timing checks, and OS-native credential APIs. No passwords or private keys leave the Mac/browser; the relay stores only public keys and revocation metadata.
- **missing:** Hardware-backed key storage and attestation on the pendant; BLE or another authenticated low-power presence transport; USB alone is not a product transport; Mac login/Keychain presence integration; Browser extension support for WebAuthn/passkey or narrowly scoped fill approval; Relay revocation registry and dashboard recovery flow

### "“Before this runs, show me exactly what information will leave my Mac or browser, and afterward prove what actually left.”"
- **useful because:** Maximum access is the owner's policy, but today there is no usable data-flow account: shell inherits the full environment, browser work can cross into relay planning, and receipts do not show the actual outbound payload. A preflight/postflight egress report would let the owner keep unrestricted power while understanding whether source text, credentials, screenshots, or only metadata crossed a boundary.
- **path:** mac-planner → browser-extension → relay → dashboard
- **model tier:** Deterministic taint/provenance engine first; a cheap model may turn the report into plain language, never decide whether a transfer is allowed
- **latency:** Preflight under 300 ms for structured actions; postflight under 2 s; deep filesystem/network accounting can be asynchronous
- **cost:** <$0.002 per action for hashing and receipt generation; engineering cost is in instrumentation, not inference
- **security:** The auditor itself must not copy secrets into its report. Hash or classify sensitive values, retain exact payloads only locally and briefly, and distinguish intended from observed egress. This is observability, not a confirmation gate; the owner’s no-restriction policy remains intact.
- **missing:** Outbound boundary instrumentation for Mac shell, browser extension and relay; Secret-aware taint labels for environment, files, DOM fields and screenshots; A signed preflight intent and postflight network/payload receipt; A dashboard diff showing intended versus observed data movement; Retention and redaction rules for audit evidence


## Changes it proposed to its own stack

### `mac-harness` — Add a failure-correlation hook to the Mac job lifecycle: whenever an action or test command exits nonzero, emit a bounded, redacted failure event containing exit code, signal, cwd, git revision, command fingerprint, and a short log window to the relay; expose it to browser-session planners as an ephemeral query context and expire it after 24 hours.
- **owner gets:** A failed local test can immediately become a correctly sourced tracker draft instead of requiring the owner to copy logs, branch names and issue context by hand. It also makes failures explainable when the owner returns later.
- effort: Medium: add exit-status capture around run_shell, redaction/fingerprinting, one event route, and a browser-planner context adapter.  ·  risk: Logs may contain secrets or proprietary code; redact tokens and cap bytes, and keep raw output local. A false issue match must remain a draft, never an automatic post. If event delivery fails, the local job still completes normally.
- cost: Negligible storage; <$0.01 for optional matching. No new hardware cost.  ·  latency: <100 ms to emit locally; matching remains asynchronous.
- security: Improves least-data transfer by sending evidence capsules rather than raw logs, but requires careful redaction and per-job expiry.
- depends on: A real run_shell exit code/signal in receipts; A relay event ingestion route; Browser planner support for ephemeral failure context


## What it asked for

_Nothing._
## Its own summary

This round produced three non-duplicate owner-facing capabilities and one concrete Mac change: (1) a “what changed while I was away” delta briefing across Mac, Safari, files and relay jobs; (2) browser-selected private data transferred into a local project with provenance and hashes; (3) failed local tests correlated to an authenticated tracker issue as a sourced draft; and (4) a failure-correlation event hook carrying bounded redacted evidence. I also verified that the granted mac_usb_serial_diagnostics schema still has no live implementation: the attached chips remain testable in principle only through existing shell capture scripts.

**Biggest unknown:** The browser provenance/trace routes surfaced by proposal feedback need a live inventory check before implementation, and the system still lacks a real bounded serial reader. The latter is the immediate bench blocker: USB hardware is physically present, but the only practical path today is run_shell invoking the existing dual-chip capture scripts, with weak receipts.

