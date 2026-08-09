# Harness derivation — mac-planner — round 264

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Run a real hardware-in-the-loop pendant audio check every night: exercise both directions over USB, compare measured counters with the acceptance limits, save a dated report, and tell me in the morning only if it regressed."
- **useful because:** The owner gets an early warning that the wearable's voice path degraded, instead of discovering distortion during a conversation. It is specifically actionable today because both chips are physically attached over USB even though LTE registration is absent.
- **path:** pendant → mac-planner → relay → dashboard
- **model tier:** No realtime model for collection; a cheap background model only classifies the numeric report and writes a one-sentence exception summary.
- **latency:** Run unattended in under 2 minutes overnight; morning alert under 5 seconds from cached result.
- **cost:** Near-zero API cost for fixture execution and threshold checks; $0.002–$0.01 only when a report needs a generated explanation.
- **security:** The fixture must synthesize audio only and never read microphone content. Store counters and firmware/build identifiers, not raw PCM. USB commands should be restricted to the allowlisted diagnostic procedure, and reports should be append-only with a receipt so retries cannot fabricate a pass.
- **missing:** A Mac-terminal bounded USB diagnostic procedure that can arm the existing audio_path_diagnostic_fixture and parse UART counters without arbitrary shell semantics; A scheduled relay job that knows the acceptance thresholds (alias rejection >=60 dB, mic drops ~1%, tx_starved near zero, codec under one core); A durable report route and morning exception notifier to the existing pendant inbox; A firmware diagnostic completion marker containing fixture version and monotonic sequence

### "Before you send mail, delete a file, or buy something on my Mac, read me a one-sentence summary on the pendant and let the physical button approve or cancel it; if I do nothing, expire it."
- **useful because:** The owner's stated rule is confirmation for destructive actions, but a Mac prompt is easy to miss while away from the screen. A physical, local-to-the-owner decision channel makes the rule real across the Mac, relay, browser session, and wearable.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime only for concise summary and button-window interaction; deterministic policy and action execution should remain on the relay/Mac without an expensive model call.
- **latency:** Summary in under 2 seconds; 30-second approval window; execute immediately after approval and report a receipt back to the pendant.
- **cost:** Usually under $0.01 per action; model cost is limited to summarizing the proposed action, with deterministic templates for common mail/delete/purchase operations.
- **security:** Never approve based on a stale or replayed event: bind a nonce, exact resource digest, and expiry to the pending action. The pendant should display only a redacted summary; do not speak message bodies or payment details by default. Cancellation and timeout must be fail-closed, and the Mac receipt must record the physical decision.
- **missing:** A relay pending-action channel that can push a nonce-bound summary to the shipped alert inbox and accept the button decision; Firmware mapping for approve/cancel/timeout while preserving existing recording, bookmark, inbox, and privacy-latch semantics; A policyRouter integration that pauses execution before the existing FULL_CONTROL_MODE path, without pretending FULL_CONTROL_MODE currently gates anything; Browser purchase/send routes that expose a canonical action digest; A receipt join between approval event, POST /execute, and final result

### "When you tell me something about my work, let me ask “prove it” on the pendant and hear a short, source-backed answer that says exactly which current calendar, mail, browser page, or Mac file supports it and when that source was read."
- **useful because:** The owner can distinguish a live observation from an old memory or model guess without opening a laptop. This is a new cross-surface trust primitive: the pendant supplies the physical challenge, the relay coordinates it, and the Mac/browser surfaces expose evidence that the voice model cannot reach by itself.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime model only compresses already-collected evidence into one short spoken sentence; deterministic source retrieval, timestamps, hashes, and contradiction checks happen in background services.
- **latency:** Return a source list and freshness in under 4 seconds for cached context; under 12 seconds if Calendar/Mail/browser/Mac reads are needed.
- **cost:** Typically $0.005–$0.03 per challenge, dominated by one compact synthesis call; source reads and hashing are local or relay-side.
- **security:** Never read an entire sensitive document aloud by default. Return source type, title/subject, timestamp, and a redacted supporting excerpt; honor the owner's existing mail/file/browser permissions; keep evidence hashes and short-lived encrypted excerpts, with a dashboard deletion control. If sources conflict, say so rather than selecting a winner silently.
- **missing:** A relay evidence ledger that stores source snapshots, read timestamps, content hashes, and claim-to-source links; A claim provenance contract emitted with every spoken factual answer, including confidence and freshness; A pendant command/event for challenging the last answer and receiving its evidence response; A Mac/browser adapter that returns redacted, hashable evidence rather than only an undifferentiated action result

### "Let me give you a time-limited delegation such as “until 5 PM, triage this project’s incoming items and prepare drafts, but do not send or delete anything,” then have the pendant tell me only about exceptions and automatically revoke the delegation at the deadline."
- **useful because:** Today the owner can ask for individual actions or recurring routines, but cannot safely hand the hive a bounded period of responsibility spanning Mail, Calendar, authenticated browser sessions, and Mac files. An expiring delegation turns the system into an assistant without making an indefinite standing permission.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Background model performs triage and draft preparation; realtime is reserved for the owner’s spoken grant/revoke and urgent exception notices. Deterministic policy evaluates every proposed mutation.
- **latency:** Grant acknowledgement under 2 seconds; routine triage can run asynchronously; urgent exception delivered within 30 seconds; revocation takes effect within one polling cycle.
- **cost:** $0.02–$0.15 per delegation window depending on item volume, dominated by classification and draft generation; read-only polling is cheap.
- **security:** A delegation must be an explicit signed capability with scope, resources, allowed operations, deadline, and revocation nonce. Drafting must be separated from sending/deleting, browser credentials must never leave the browser bridge, and every attempted action needs an audit receipt. Silence, link loss, model uncertainty, or clock disagreement must suspend work rather than extend authority.
- **missing:** A cross-surface delegation token and revocation service understood by relay, Mac, and browser; A policy evaluator that can enforce operation-level scope instead of the current undifferentiated FULL_CONTROL_MODE execution path; An exception queue with deduplication and pendant delivery semantics; A dashboard showing active grants, scope, expiry, and receipts

### "At any time ask “what did you learn about me today?” and hear a compact inventory of new memories, captured bookmarks, browser/calendar/mail evidence, and pending audio, with a physical pendant action to delete one category before it is retained."
- **useful because:** The owner currently has to trust many surfaces that can observe or retain context. A daily, spoken data-inventory and deletion control makes the hive accountable at the moment of use, including observations made while the Mac was unattended or the pendant was offline.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic aggregation and redaction first; a cheap model groups items into a short spoken inventory. Realtime is used only for the owner’s query and deletion confirmation.
- **latency:** Cached inventory under 3 seconds; full same-day reconciliation under 20 seconds; deletion receipt under 5 seconds.
- **cost:** Usually under $0.02 per inventory, mostly aggregation; deletion is a local/relay operation with no model requirement.
- **security:** Inventory must describe sensitive items without repeating their contents. Deletion must propagate to relay queues, Mac workbench, browser snapshots, and pendant SD outbox where technically possible, returning an honest list of replicas that remain. Require a nonce-bound physical confirmation for irreversible deletion and retain only a minimal deletion receipt.
- **missing:** A unified retention ledger spanning relay memory, Mac/browser evidence, pendant queues, and workbench artifacts; A deletion fan-out protocol with per-surface receipts and an explicit 'could not delete' state; A pendant browse/delete interaction that does not conflict with recording, inbox, bookmark, and privacy-latch controls; A user-facing daily privacy inventory route and redaction-aware summarizer


## Changes it proposed to its own stack

### `hardware` — Add a small, owner-visible USB test dock between the Mac and the pendant/ESP32 bridge: keyed connectors, independent power switching, and a hardware-present GPIO that the Mac can detect. On insertion it exposes stable identities for both serial devices and lets the scheduled HIL test power-cycle the bridge without touching the worn pendant's buttons.
- **owner gets:** Nightly audio checks and recovery would work reliably while the pendant is charging on the desk; a loose cable or wedged bridge would become a clear dock fault instead of silently producing a false pass. The owner would no longer need to remember which of the two changing USB serial paths is which.
- effort: Moderate hardware/firmware work: a small powered USB/serial dock, udev-style identity handling in the Mac harness, and a pendant/bridge presence handshake. Prototype can use an off-the-shelf powered hub plus a simple dock PCB.  ·  risk: Power cycling the wrong USB target could interrupt a live call or corrupt an SD write; only allow the scheduled bench profile to cycle devices when no call is active, and require a stable presence handshake before declaring failure. Recovery is unplug/replug and fall back to direct serial paths.
- cost: Roughly $20–$60 prototype hardware, under 1 W idle and a few watts during charging/test; negligible API cost.  ·  latency: Adds 1–3 seconds to device discovery, but removes repeated manual retries and makes overnight tests deterministic.
- security: The dock is a physical trust boundary: accept only known USB VID/PID/serial identities and never treat arbitrary newly attached serial devices as the pendant. Keep firmware flashing disabled in the unattended test profile.
- depends on: The proposed hardware-in-the-loop audio regression job; A Mac USB diagnostic procedure with stable device identity mapping; A firmware presence/diagnostic handshake that distinguishes bench mode from normal wearable use


## What it asked for

_Nothing._
## Its own summary

This round produced three non-duplicate additions. (1) A scheduled hardware-in-the-loop audio regression service that uses the already-shipped diagnostic fixture over the physically live USB links, checks measured acceptance thresholds, stores a dated receipt, and alerts only on regression. (2) A physical pendant approval channel for destructive Mac/browser actions, binding a redacted spoken summary to a nonce, exact resource digest, expiry, and final execution receipt. (3) A keyed, power-switchable USB test dock so overnight pendant/bridge tests can identify and recover devices deterministically instead of trusting changing serial paths. I also discovered Safari is online with five tabs and the Mac bridge is online; the owner’s current rules are short spoken replies, browser read/click allowed, and destructive actions require confirmation.

**Biggest unknown:** The critical missing live surfaces are still the bounded USB/UART diagnostic executor, a relay pending-action push/decision channel tied to the existing approval seam, and a reliable Mac semantic context read. I did not re-request the already-pending semantic-context tool. The granted mac_workbench_transaction name still resolves in the live resolver to a read-only handoff route, so its claimed atomic-write behavior cannot yet be assumed.

