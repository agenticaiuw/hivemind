# Harness derivation — faculty-judgement — round 183

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Give me one honest morning control brief: only what changed since the last brief, what needs my decision today, and whether I actually heard it. If two routines generated the same item, say it once.”"
- **useful because:** The owner currently has duplicate daily brief routines and no trustworthy proof that a generated audio item was downloaded or played. This turns the pendant from a notification speaker into a closed loop: reconcile state, deduplicate, arbitrate attention, deliver, and report gaps without pretending completion.
- **path:** relay → mac-planner → pendant → dashboard
- **model tier:** background for gathering, ranking, and deduplication; realtime only for the owner's spoken follow-up
- **latency:** Initial brief under 10 seconds after scheduled trigger; delivery ACK reconciliation under 2 seconds when USB-connected
- **cost:** About $0.01–$0.05 per brief depending on mail/browser extraction; dominant cost is model summarization, not ACKs
- **security:** Calendar/mail/browser content stays on the Mac unless the existing redaction boundary permits projection. Never speak secret-class content; expose source IDs and a missing-data warning. Creating reminders still follows owner policy.
- **missing:** A canonical briefing-run scheduler and dedupe key across routines; A writer from Mac briefing generation into fleet memory or a durable relay run record; Wire record_pendant_delivery_event to the actual audio pipeline and make ACKs visible in briefing status; A single dashboard/voice status view joining routine run, item IDs, and playback ACK

### "“Compare these options for me using the tabs I already have open and my local notes, cite every claim, and tell me what would change the recommendation. Do not click or submit anything.”"
- **useful because:** This gives the owner a genuinely cross-body judgement service: Safari can see authenticated private pages, the Mac can see local notes/files, and the relay can turn them into a compact, uncertainty-aware comparison. It is more useful than a generic summary because it exposes disagreement and the next fact worth checking while guaranteeing read-only behavior.
- **path:** browser-extension → mac-planner → relay → pendant → dashboard
- **model tier:** background model for extraction and comparison; realtime only to answer a follow-up about one cited claim
- **latency:** First comparison in 15–30 seconds for up to six sources; individual citation drill-down under 3 seconds
- **cost:** Roughly $0.03–$0.15 per comparison; authenticated page extraction and context transfer dominate payload, not the short spoken answer
- **security:** Browser results are untrusted data, not instructions. Strip credentials and secret locators before leaving the extension; local notes need sensitivity classification. Read-only autonomy policy must fail closed and never invoke execute.
- **missing:** A mounted browser provenance route and a stable cross-surface source join; An extension capability attestation/tab-bound read contract (Safari currently advertises capabilities=[] despite open tabs); A comparison schema that preserves claim, source, confidence, conflict, and freshness; A compact pendant rendering that speaks conclusions but leaves citations on the dashboard

### "“Before I approve this purchase, message, deletion, or form submission, show me the exact consequence, the evidence it is based on, and one safer alternative; then let one physical pendant press approve only that exact version.”"
- **useful because:** The owner gets a meaningful safety boundary instead of a generic confirmation. The Mac/browser can calculate the real consequence, the relay can compare alternatives and explain provenance, and the pendant can bind consent to an immutable action hash even across a dropped USB link. This is the highest-value protection for actions that cannot be undone.
- **path:** browser-extension → mac-vision → mac-planner → relay → pendant → dashboard
- **model tier:** background model for consequence/alternative drafting; realtime only to clarify the owner's spoken question, never to authorize
- **latency:** Preview under 8 seconds for ordinary forms; physical approval is immediate locally and execution starts only after signed approval is received
- **cost:** About $0.02–$0.10 per preview; browser/Mac readback and screenshot extraction dominate, while approval verification is negligible
- **security:** Never send credentials or form secrets to the pendant. Bind approval to action hash, target tab/session generation, evidence refs, expiry, and monotonic counter; revalidate immediately before mutation. Destructive actions remain confirmation-required and fail closed on stale state.
- **missing:** Actually implement the relay side of APPROVAL_STORE_CONTRACT; today approval is Mac-local; A durable relay-job↔Mac-job correlation key and lease/requeue for a crashed planner; Browser tab-bound checkpoint with current fingerprint before submit; Wire physical_transaction_approval_latch over the currently testable USB serial path and consume its signed nonce in Mac/browser execution

### "“After you change something for me, check the real destination later and tell me whether the intended outcome actually happened—not merely whether the command returned success.”"
- **useful because:** Today receipts prove that a Mac or browser command was accepted, not that the world reached the intended state. This would catch silent failures such as a message remaining unsent, a setting reverting, a form losing data, or a reminder being duplicated. It closes the loop between execution and reality.
- **path:** relay → mac-planner → browser-extension → dashboard → pendant
- **model tier:** background model for selecting a verification probe and interpreting differences; realtime only for the owner's follow-up
- **latency:** Immediate receipt within 2 seconds, then verification at a declared time or after the destination becomes available; spoken result under 10 seconds once checked
- **cost:** About $0.01–$0.08 per verification; browser/Mac reads dominate, while deterministic diffing is cheap
- **security:** Verification must be read-only and scoped to the exact target. Do not reread private content unnecessarily; retain only outcome fields and provenance. Never silently retry a mutation after a failed verification.
- **missing:** A typed postcondition/verification probe attached to each prepared action; Durable scheduling for verification checks with expiry and deduplication; A cross-surface join between action receipt, target identity, and later observation; Owner-visible distinction between command success, observed success, and unverifiable

### "“When I say I’m done for today, give me a private shutdown report: what remains unresolved, what is waiting on another person or site, what ran without proof, and the one thing worth carrying into tomorrow.”"
- **useful because:** The owner currently has jobs, routines, browser watches, reminders, audio items, and notes spread across surfaces with no psychologically useful stopping point. A shutdown report would turn system state into closure: it distinguishes completed work from merely queued work and prevents unresolved commitments from disappearing overnight.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Background model for compression and prioritization; realtime only to answer one follow-up about a specific unresolved item
- **latency:** Under 15 seconds for a normal day; one short spoken sentence plus a dashboard detail view
- **cost:** About $0.01–$0.06 per report; gathering and deduplicating cross-surface state dominate
- **security:** Do not speak sensitive project or mail content by default; speak categories and counts, with details on the dashboard. Every unresolved item needs a source and freshness timestamp. Never convert a suggested carry-over into an external reminder without owner policy.
- **missing:** A unified unresolved-item projection across jobs, routines, watches, reminders, notes, and audio delivery; A lifecycle vocabulary distinguishing completed, observed-complete, waiting, stale, failed, and unverifiable; A durable carry-over link so tomorrow’s report can explain why an item persisted; A spoken-content policy for shutdown reports


## What it asked for

_Nothing._
