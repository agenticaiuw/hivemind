# Harness derivation — faculty-judgement — round 21

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If something you planned is no longer true, don’t do it—recheck the important details and ask me only when the change matters.”"
- **useful because:** Today an approved multi-step task can become unsafe or simply wrong while the Mac, browser, or relay is waiting: a price changes, a meeting moves, a file is edited, or the owner’s words are superseded. This gives the owner a temporal safety boundary rather than a one-time approval prompt, while preserving the requested one-sentence spoken interaction.
- **path:** pendant → relay → browser → mac-bridge → dashboard
- **model tier:** Use a cheap background model to normalize the goal and identify assumptions; use deterministic checks for timestamps, hashes, ownership, and permissions; reserve realtime for the brief approval or exception conversation.
- **latency:** Normal execution adds under 1 second for local precondition checks and 1–3 seconds for a cross-surface recheck. If an assumption changed materially, pause and ask on the next available pendant interaction instead of silently proceeding.
- **cost:** Roughly $0.001–$0.01 per task for background manifest/recheck summarization; most checks are deterministic and free. Realtime cost occurs only when a material change needs explanation or approval.
- **security:** The manifest should contain typed, minimized facts (hashes, IDs, timestamps, sensitivity labels), not copied private page contents. Browser and Mac evidence stays on their surfaces unless needed for the spoken explanation. Sending, deleting, purchasing, or external publication always requires a fresh explicit approval after the final recheck; stale manifests must fail closed.
- **missing:** A shared durable assumption/manifest schema with per-field source, confidence, sensitivity, and expiry; Event subscriptions from browser watches, Mac file/app state, calendar/mail changes, and relay job progress; A deterministic preflight verifier and invalidation path between faculty-perception and faculty-action; A pendant-friendly materiality classifier and concise re-approval prompt; Receipts that record which assumptions were checked immediately before each irreversible step

### "“Keep working on this, but if the facts change before you act, stop and tell me exactly what changed; never finish a stale plan.”"
- **useful because:** A one-time approval is not enough for work that waits across a browser, Mac, and relay. This gives the owner confidence that background automation remains faithful to current reality without forcing them to supervise every intermediate step.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Cheap background planning and deterministic source comparisons; realtime only for the short spoken exception and renewed approval.
- **latency:** Automatic checks should add less than a second locally and a few seconds cross-surface. A material change pauses the job and waits for owner approval rather than silently continuing.
- **cost:** About $0.001–$0.01 per long-running task for compact change summaries; hashes, IDs, timestamps, and permission checks are deterministic.
- **security:** Keep private contents on the Mac/browser; share only typed, minimized changed fields and provenance. Bind every approval to a fresh manifest and fail closed for sending, deletion, purchase, or publication. Retain an auditable before/after receipt.
- **missing:** A durable cross-surface manifest containing assumptions, expiry, provenance, and materiality rules; Event-driven invalidation from browser, Mac, and relay jobs; A pre-side-effect verifier that can pause/resume jobs without duplicate actions; Fresh approval tokens bound to the changed manifest and a concise pendant prompt


## Changes it proposed to its own stack

### `integration` — Introduce a Temporal Action Firewall between judgement and action. Judgement emits a typed manifest: goal, planned steps, assumptions, source references, validity windows, materiality thresholds, and required approval class. Before every side-effect—and after any wait, reconnection, browser navigation, or relevant event—faculty-perception re-reads only the affected sources and returns valid, changed(material), or unknown. The relay durably pauses invalid jobs, sends a one-sentence pendant prompt with before/after facts, and records a new approval bound to the refreshed manifest. No executor may accept an old approval token for a changed manifest.
- **owner gets:** The pendant will not act on yesterday’s truth. A task can keep working in the background without turning a changed appointment, edited document, or altered checkout into an accidental action; the owner is interrupted only when the change is meaningful.
- effort: Medium-high: typed schema and migration, verifier library, event hooks in browser/Mac runners, relay pause/resume state machine, and receipt/dashboard presentation. Start with file hashes, tab URL/title, calendar event IDs, and explicit destructive steps.  ·  risk: False invalidations could create annoying re-prompts; missed events could still allow stale work. Recover with conservative expiry, fail-closed for destructive actions, deterministic evidence in receipts, manual resume, and idempotency keys. A crash during pause must preserve the manifest and never duplicate the side effect.
- cost: Small storage and D1/R2 event-log increase; deterministic checks dominate. Occasional cheap background model calls to summarize changed facts, with realtime only for owner-facing exceptions.  ·  latency: Sub-second for local hashes/IDs; roughly 1–3 seconds for cross-surface refresh. Long jobs may pause rather than add latency when sources are unavailable.
- security: Improves safety by binding approval to exact, fresh evidence and preventing replay of approvals. Minimized manifests reduce private-data movement; source snippets remain on Mac/browser unless the owner asks for detail.
- depends on: Durable cross-surface job/event persistence; Faculty-perception postcondition and source-read primitives; Faculty-action typed manifests and receipts/undo; Browser session affinity and Mac action request IDs


## What it asked for

_Nothing._
## Its own summary

Proposed a genuinely new Temporal Action Firewall: every cross-surface job carries typed assumptions, source provenance, validity windows, materiality thresholds, and approval binding; perception rechecks affected facts immediately before each side effect and after waits/reconnections, while relay pauses stale jobs and asks the pendant only when a material change occurred. Also proposed the owner-facing capability: “If something you planned is no longer true, don’t do it.” This goes beyond one-time approval and existing receipts by preventing replay of approvals against changed reality.

**Biggest unknown:** The shared durable job/event persistence and current cross-surface preflight primitives are not visible yet (earlier requests remain unanswered), so I cannot tell whether the firewall can be integrated cleanly or needs a new relay state machine. I still need those primitives, plus the event inventory and audio/attention acceptance criteria, before specifying implementation details.

