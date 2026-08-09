# Harness derivation — faculty-perception — round 228

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac accessibility and screen recording live state** — The live Mac ops snapshot reports AI Pendant Agent permissions ready=true: Accessibility trusted, Screen Recording granted, requiredMissing=[]; browser extension online on Safari USPS Tracking page with zero pending commands.
  - evidence: read_continuity_snapshot include relay/pipeline, called GET /ops/snapshot HTTP 200 at 2026-08-09T00:57Z

## Capabilities it proposed

### "Before I speak, tell me whether the whole system is genuinely ready—and if not, automatically use the best available body instead of pretending the pendant heard me."
- **useful because:** Today the relay and Mac bridge can be healthy while the pendant is absent, or the browser can be live while a requested action is impossible. This gives the owner one honest preflight (relay reachable, Mac permissions ready, browser session live, pending work, and pendant presence) and a graceful Mac-audio fallback, so a request is never silently lost merely because one body is unavailable. It is the highest-value capability because it prevents false confidence in every other capability.
- **path:** relay-realtime → relay → mac-planner → browser-extension → unified → pendant
- **model tier:** Use deterministic health evaluation and a cheap background model for explanation; reserve realtime only for the live conversation and never infer pendant playback from relay delivery.
- **latency:** Preflight under 300 ms from cached status; fallback selection under 1 s; no model call for the common healthy/unhealthy decision.
- **cost:** Near-zero API cost for status checks; occasional short explanation call under $0.01. Dominant cost is keeping a small status cache fresh, not inference.
- **security:** Do not expose browser URLs or authenticated tab contents in a spoken health report unless asked. Treat absence from the registry as 'unverified', not offline, because the pendant does not currently heartbeat. Switching to Mac audio must be explicit in the turn and visibly logged.
- **missing:** A single freshness-bounded health contract that includes the pendant-facing state; current live aggregate covers relay, Mac, browser, permissions, and pipeline but not a real pendant.; Mac audio capture/playback fallback wired to the same conversation/session state.; A policy for what actions are allowed when the pendant is unverified or absent.

### "Watch this authenticated page while I am away and tell me only when something materially changes—what changed, why it matters, and what I can do next."
- **useful because:** A logged-in page (shipping, school, billing, appointments) is often the only place a meaningful change appears, and the current public-page reader cannot see it. The owner gets a concise, actionable interruption instead of repeatedly checking Safari or receiving identical alerts.
- **path:** browser-extension → mac-planner → relay → relay-realtime → pendant
- **model tier:** Use deterministic DOM/text normalization and hashes for change detection; use a cheap background model only to classify materiality and summarize the delta. Realtime is only for the owner's follow-up conversation.
- **latency:** A scheduled check should complete in 5–15 seconds, with no owner-visible delay unless a material change is found. Alert delivery should begin within 2 seconds of a successful check.
- **cost:** Minimal when unchanged (browser inspection plus hashing); roughly $0.001–$0.02 per changed page depending on summary length. Browser rendering/session access dominates latency, not the model.
- **security:** Keep page content on the Mac unless the owner explicitly enables relay summarization; redact account numbers and secrets before any cloud call. Require confirmation before submitting forms or changing account state. Record the exact tab/session and capture time so an alert cannot be mistaken for current truth.
- **missing:** A durable watch definition with URL/session, selector or semantic region, cadence, and materiality policy.; A Mac-side authenticated capture path that emits a normalized, redacted delta rather than sending the whole page to the relay.; A relay scheduler trigger and alert deduplication keyed by content hash; pendant delivery remains unverified until a real device is registered and emits playback telemetry.

### "Start this task from my voice, let the Mac continue it in the browser, and if I disappear or the link drops, resume exactly where it stopped and tell me the one decision still needed when I return."
- **useful because:** A wearable conversation is inherently interruptible: the owner may walk away, lose LTE, close the laptop, or need to approve a sensitive step later. This turns a spoken request into a bounded, resumable handoff across relay, Mac, and browser instead of a one-shot command whose apparent completion may be false.
- **path:** pendant → relay-realtime → relay → mac-planner → browser-extension → unified
- **model tier:** Use deterministic step state, idempotency keys, receipts, and browser checkpoints; use a cheaper background model to compress the handoff summary. Realtime is only needed when the owner reconnects and asks what remains.
- **latency:** A handoff receipt within 1 s; checkpoint after every browser mutation; reconnect summary under 2 s from stored state.
- **cost:** Low: mostly local state and existing job receipts; under $0.01 for a reconnect summary. Browser interactions and model vision, when required, dominate cost.
- **security:** Never replay a mutation after uncertain completion without checking the recorded before/after state. Pause at login, payment, send, delete, or irreversible steps and require explicit owner confirmation. Bind checkpoints to the authenticated browser session and expire them when the session changes.
- **missing:** A shared task manifest joining relay job ID, Mac job ID, browser command IDs, session ID, and action-ledger step keys.; A resume protocol that distinguishes completed, uncertain, and awaiting-confirmation steps instead of treating Mac completion as owner success.; A pendant reconnect/return event; no pendant is currently registered, so this must be testable first through the Mac bridge and later upgraded to wearable delivery.

### "Remember the commitments I make in conversation and messages, ask me before recording them, and later tell me what is still outstanding—with the exact source and whether I actually followed through."
- **useful because:** People lose promises between a spoken conversation, a text, an email, and a calendar entry. The owner should have one trustworthy commitment ledger that distinguishes an explicit promise from an inferred intention, links it to its source, detects completion across their apps, and asks before creating a reminder or nudging someone. No single Mac app, browser session, relay, or pendant can establish that continuity alone.
- **path:** pendant → relay-realtime → relay → mac-planner → browser-extension → unified
- **model tier:** Use a cheap background model to extract candidate commitments and match completion evidence; use realtime only to ask the owner for confirmation during the live conversation. Deterministic rules should enforce source links, confidence, and status transitions.
- **latency:** Candidate extraction within 30 seconds of a message or completed voice turn; confirmation prompt under 2 seconds; daily outstanding digest under 5 seconds.
- **cost:** Approximately $0.01–$0.05 per day for normal personal volume; scanning and redacting Mail/Messages/browser content dominates token cost. No cloud model should receive raw private content unless the owner opts in.
- **security:** Treat inferred commitments as untrusted until the owner confirms. Keep sensitive message bodies local, store only a redacted quote/hash and source locator in the relay ledger, encrypt the local ledger, and require confirmation before sending reminders, contacting another person, or changing calendars. Completion must never be inferred merely from a Mac job marked completed.
- **missing:** A durable commitment schema with provenance links spanning pendant utterance IDs, Mail/Messages/Calendar records, browser evidence, and action receipts.; Local connectors that can read outgoing Mail/Messages and calendar changes as events rather than one-off app actions, with redaction before relay sync.; A relay reconciliation worker that re-checks open commitments and an owner-facing review/confirm surface; the current continuity stores are not a commitment ledger.

### "When I open or receive something suspicious, tell me whether it is a scam, show me the exact evidence, and stop me from sending money, credentials, or a reply until I explicitly approve it."
- **useful because:** The owner encounters threats in authenticated browser pages, Mail, Messages, and spoken requests, while each surface alone lacks context. A cross-surface shield can correlate sender, domain, requested action, prior conversation, and account state, then turn a vague warning into a concrete, reversible decision before harm occurs.
- **path:** browser-extension → mac-planner → relay → relay-realtime → pendant → unified
- **model tier:** Use deterministic domain/recipient/permission checks first, then a background classifier for scam likelihood and explanation; realtime is only for a short spoken warning and confirmation.
- **latency:** Inspection and blocking decision under 500 ms for known patterns; under 3 seconds for model analysis. Never delay harmless reading, only risky mutation or submission.
- **cost:** Under $0.01 for common local checks; $0.01–$0.05 for a difficult page/message classification. Screenshot/OCR and redaction dominate cost.
- **security:** Private messages and financial context must stay local by default. The shield must fail closed for send/payment/credential actions but fail open for viewing. It must show uncertainty and evidence, never claim certainty from a heuristic, and provide a bypass requiring deliberate confirmation.
- **missing:** A pre-mutation policy hook shared by browser commands, Mac actions, and relay-issued work; current action routes do not provide a universal veto.; Local connectors for Mail and Messages content plus a redacted threat-evidence record.; A device/UI confirmation protocol that binds the approval to the exact recipient, URL, amount, and payload, rather than a generic 'yes'.

### "Find everywhere this service has my personal data, show me what can be deleted, and carry out only the exact deletions I approve—with a receipt proving what was and was not removed."
- **useful because:** Privacy requests are fragmented across authenticated web accounts, email, local files, and browser sessions. The owner cannot currently ask one mind to discover the spread, distinguish reversible from irreversible cleanup, and verify the result across the browser, Mac, relay, and wearable conversation.
- **path:** browser-extension → mac-planner → relay → relay-realtime → pendant → unified
- **model tier:** Use deterministic inventory and deletion receipts; use a background model to cluster duplicate records and explain consequences. Realtime is only for interactive scope decisions and final confirmation.
- **latency:** Inventory in 1–5 minutes depending on services; every deletion preview within 2 seconds; execution should be staged and resumable rather than one long blocking turn.
- **cost:** Usually $0.05–$0.50 per service sweep, dominated by authenticated page inspection and screenshots; no model call is needed for known structured records.
- **security:** Never infer authorization to delete from a vague request. Present exact account, record type, scope, retention consequence, and undo availability; require per-service confirmation for irreversible operations. Keep credentials in the browser, transmit only redacted identifiers, and retain deletion receipts without retaining the deleted content.
- **missing:** A service-specific discovery/deletion adapter model with dry-run and verification contracts; browser_run_actions alone cannot establish complete coverage.; A cross-surface deletion plan and receipt ledger joining browser command IDs, Mac action ledger steps, and relay job records.; A policy for relay retention and announcement cleanup so the system does not preserve the very data the owner asked it to remove.


## What it asked for

_Nothing._
## Its own summary

Live discovery changed an important constraint: the Mac agent is now fully ready (Accessibility and Screen Recording granted, requiredMissing empty), relay and browser are reachable, and Safari’s authenticated USPS tab is online with zero pending commands. I recorded that verified state. I proposed three capabilities: a whole-system readiness gate with Mac-audio fallback (highest value), authenticated-page material-change watches, and interruption-safe voice-to-Mac/browser task handoff with resumable checkpoints. The system already has the individual status, job, browser, and receipt routes; the missing value is the contracts joining them.

**Biggest unknown:** The pendant remains unregistered and has no live heartbeat/playback confirmation. I still need a real device registration/heartbeat plus a device-originated playback event to claim that anything was heard; until then, Mac fallback is the only honest body.

