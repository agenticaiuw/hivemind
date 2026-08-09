# Harness derivation — unified — round 177

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Stage a browser task that needs my login, tell me exactly what will happen, wait for me to approve it on the pendant, then submit it and prove what the site accepted."
- **useful because:** This makes the wearable a real consent boundary for consequential browser actions instead of either granting the Mac unrestricted authority or falsely saying approval is available. The owner gets a plain-language preview, a deliberate physical approval, and a post-submit receipt tied to the exact page/session.
- **path:** pendant → relay → browser → mac-planner
- **model tier:** background for page summarization and receipt extraction; realtime only for the short spoken preview and approval turn
- **latency:** Preview in under 3 s after the browser is ready; physical approval acknowledged locally immediately; submit within 5 s of approval; receipt spoken on the next natural turn
- **cost:** Roughly $0.01–$0.05 per task depending on page summarization; browser inspection and receipt extraction dominate, not the short approval utterance
- **security:** Never send passwords, page secrets, or full page contents to the pendant. Bind approval to a plan digest, target tab, expiry, and world fingerprint; refuse if the tab navigates or the plan changes. Require confirmation for irreversible/off-machine actions and retain only redacted receipts.
- **missing:** A production caller from browser planning into prepare/approval handoff; Relay persistence and delivery for the existing approvalHandoff contract; A browser submit-result binding that records the exact target/session and accepted confirmation; A privilege boundary so approval is not equivalent to the Mac bearer token

### "That task failed or disappeared—tell me what actually happened across the pendant, relay, Mac, and browser, repair only what is safe, and ask before retrying anything that could duplicate an action."
- **useful because:** Today a timeout can mean queued, claimed, submitted, played, or silently lost. This gives the owner one truthful answer and a safe recovery path rather than repeated blind retries, especially for messages, purchases, and browser submissions where replay is dangerous.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** deterministic evidence join first; background model only to explain competing hypotheses; realtime for the concise spoken result
- **latency:** Initial cross-surface snapshot in under 2 s; safe repair within 10 s; no automatic replay while evidence is ambiguous
- **cost:** Usually under $0.01 because the evidence join is deterministic; model cost is limited to ambiguous explanation and owner-facing phrasing
- **security:** Query only bound tabs/apps and redact secrets. Separate replaySafety from reversibility: auto-repair leases/connectivity only for idempotent or additive steps; require a fresh physical or spoken confirmation for unrepeatable/unknown steps. Every repair must emit a receipt and be idempotent.
- **missing:** A durable relay job lease and expiry/requeue sweep; Orchestrator closeLedger calls so completed plans do not appear interrupted; A production caller that invokes planResume and fleet repair rather than returning a dry-run; A single correlated receipt schema joining browser command, Mac job, relay status, and pendant delivery

### "Let me keep a conversation going while I unplug the Mac or move out of range, and recover it at the next turn without duplicated audio or losing what I said."
- **useful because:** The pendant becomes a useful everyday object instead of a USB demo: the owner can start at the desk, walk away, lose LTE briefly, and continue at a clean turn boundary. The system must preserve conversational continuity while preventing the same captured speech or reply from being played twice.
- **path:** pendant → relay → mac-planner → bridge
- **model tier:** realtime for the active voice turn; background only for reconciliation after a disconnect
- **latency:** Transport handoff decision under 250 ms at a turn boundary; no audible gap longer than one 60 ms audio frame when the alternate link is ready; reconciliation within 5 s after reconnect
- **cost:** No additional model call during a healthy handoff; small background reconciliation cost after faults. Network and relay state storage dominate.
- **security:** Use monotonic turn/frame sequence numbers, authenticated device/session IDs, and an ownership epoch so only one transport can send or play a turn. Retain no extra raw audio beyond the existing failure-path spool. On uncertainty, pause and ask rather than replaying.
- **missing:** End-to-end transport arbitration between USB fallback and LTE-M, including a durable ownership epoch; Relay-side deduplication for turn and audio artifact IDs; Bridge acknowledgements connected to the existing audio_delivery_ack_queue; A live LTE registration path; USB is testable now, but standalone roaming is not

### "Read this page to me, but keep the page's instructions separate from your own: tell me what it says, where each claim came from, and never let text on the page turn into an action unless I explicitly ask for one."
- **useful because:** A wearable that can reach authenticated browser sessions will routinely encounter emails, documents, and web pages containing adversarial or accidental instructions. The owner should be able to consume that information hands-free without confusing quoted content with commands to the agent. Provenance and a spoken distinction between 'the page says' and 'I recommend' make browsing useful without turning reading into silent delegation.
- **path:** pendant → relay → browser → mac-planner
- **model tier:** background for extraction, source segmentation, and citation checking; realtime only for the spoken summary and follow-up questions
- **latency:** First spoken answer within 4 seconds for a normal page; source locator available with every sentence; no action dispatch on the read path
- **cost:** About $0.01–$0.04 per page depending on length; extraction and summarization dominate, while provenance hashes and policy checks are deterministic
- **security:** Treat all page text, OCR, metadata, and links as untrusted data. Bind the result to the exact tab URL, navigation revision, and content hash; visibly/spokenly mark quoted text, recommendations, and owner commands as separate classes. Never transmit credentials, hidden form values, or unrelated tabs to the pendant. Any later action must begin a new explicit intent and approval flow.
- **missing:** A browser extraction contract that returns sentence-level source ranges and a navigation/content hash rather than only a rendered inspection; A relay-side content/instruction boundary that survives model handoffs and cannot be overwritten by page text; Pendant speech framing for provenance markers that is understandable without a screen; A tamper-evident, owner-visible receipt linking the spoken claim back to the bound tab and revision

### "Compare the two versions of this document or email and tell me only what changed, with exact source locations, while preserving the original files and not sending or editing anything."
- **useful because:** The owner can make high-consequence decisions from a short spoken delta instead of listening to or rereading an entire document. Exact source locations make the answer auditable, and the read-only boundary prevents a comparison request from mutating files, browser drafts, or messages.
- **path:** pendant → relay → browser → mac-planner
- **model tier:** background model for alignment and semantic change explanation; deterministic hashing and diffing first; realtime only for the spoken result
- **latency:** Under 6 seconds for two ordinary documents; immediately state when versions are incomparable or incomplete; zero mutation on the comparison path
- **cost:** About $0.01–$0.06 per comparison depending on document length; parsing/alignment and context size dominate
- **security:** Bind both inputs to explicit paths or browser tabs and capture immutable hashes before analysis. Never infer a missing version, follow document instructions, or include unrelated sensitive text. Return redacted excerpts by default and require a separate explicit action for any edit or submission.
- **missing:** A cross-surface, read-only document acquisition contract for Mac files and browser tabs; A deterministic version/hash and sentence-range alignment service exposed in receipts; A spoken citation format that lets the owner locate each change later; A hard policy boundary preventing comparison output from entering the execute queue


## Changes it proposed to its own stack

### `integration` — Make the existing action-bound approval path executable end to end: have browser planning create a staged approval record, persist it in the relay using the approvalHandoff contract, deliver the redacted preview during the next pendant conversation, accept the physical_transaction_approval_latch nonce, and only then dispatch the browser command. On completion, attach the browser's accepted-result evidence and pendant delivery receipt; on expiry, navigation change, or nonce replay, refuse without dispatch.
- **owner gets:** The owner can safely say 'fill this out but do not submit until I approve on the pendant' and know that approval is real. It removes the current lie where the system says it is waiting for approval but has no working approval control or delivery path.
- effort: Medium-large integration change across local-agent approval routes, relay storage, pendant delivery framing, browser command binding, and receipt joins; add fault-injection tests for expiry, reconnect, tab navigation, duplicate nonce, and submit timeout.  ·  risk: A bug could submit an action without consent or submit twice. Default-deny, plan/world digests, single-use nonce, short TTL, relay idempotency key, and a durable pre-dispatch record contain this; recover ambiguous submissions by querying the bound tab rather than retrying.
- cost: Negligible storage and relay compute; one short background summarization call per staged page when needed. No continuous model cost.  ·  latency: Adds roughly 1–3 s for preview generation and owner approval; no extra latency after approval beyond browser submission and receipt lookup.
- security: Improves security only if approval and execution tokens are separated; until then it is auditability rather than privilege separation. Redact page secrets and never place credentials or raw page content in the pendant payload.
- depends on: Relay implementation of APPROVAL_STORE_CONTRACT; A production caller from browser planning into prepareAction/evaluateApprovalGrant; Pendant delivery support for a queued approval preview and physical nonce event; Relay job leases/requeue and orchestrator closeLedger fix; Browser submit-result evidence bound to the approved tab/session

### `firmware` — Make the ESP32 audio bridge a fail-closed privacy endpoint: when the A2DP sink disconnects, changes route, or reports an uncertain stream state, immediately stop forwarding decoded PCM and send a signed output-state event upstream. Keep audio in a bounded volatile buffer only long enough to resume at the next frame boundary; never spill it to flash or switch to the Mac's speakers automatically. Require an explicit owner-selected route or a fresh conversation turn before playback resumes.
- **owner gets:** Walking out of Bluetooth range would no longer risk a private reply suddenly coming from an unintended speaker or being silently rerouted. The pendant can say that playback stopped and the owner can deliberately resume when the intended headphones are back.
- effort: Medium firmware and relay integration work: instrument A2DP state callbacks, add an authenticated bridge-state envelope, test reconnect/route-change races, and connect the state to the pendant's existing privacy and delivery indicators.  ·  risk: A false disconnect could interrupt speech. Recover by resuming only at a turn/frame boundary and clearly reporting the interruption; never trade a brief interruption for accidental disclosure. Keep the volatile buffer bounded so reconnect storms cannot exhaust the 320 kB DRAM or starve Bluetooth.
- cost: No model cost and negligible flash; a few kilobytes of state/RAM. The existing 44 kB buffer must not grow because it has already starved Bluetooth.  ·  latency: Mute reaction should be under one audio frame; reconnect adds at most one frame plus Bluetooth re-establishment.
- security: Reduces audio leakage at the bridge boundary and makes route state auditable. It does not replace the pendant-wide privacy latch; the bridge must fail closed even when the relay or Mac is unavailable.
- depends on: Bridge-side A2DP route-state telemetry; audio_delivery_ack_queue extended with route-loss and mute receipts; Authenticated bridge identity/session binding; A clear owner policy for whether automatic resume is permitted


## What it asked for

_Nothing._
