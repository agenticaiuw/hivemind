# Harness derivation — faculty-action — round 214

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Do this multi-step task, but if any step fails or becomes uncertain, put everything you changed back and tell me exactly what could not be restored.”"
- **useful because:** Real-world tasks span Mac and logged-in browser state and often fail halfway. A saga executor would capture only reversible, privacy-safe pre-state, execute one step at a time, independently verify each postcondition, and run compensations on failure instead of falsely saying done. The owner gets a truthful final state rather than a half-edited account, draft, or file.
- **path:** faculty-judgement → relay-realtime → mac-planner → browser-extension → mac-vision → faculty-perception → faculty-action → pendant
- **model tier:** Use the low-latency model only to negotiate the plan and communicate exceptions; use the Mac planner/background executor for the step graph and cheaper perception checks for each postcondition.
- **latency:** Preview in under 2 seconds; each step may take normal UI time. On failure, begin compensation immediately and report within 5 seconds of the last receipt.
- **cost:** One planning invocation plus one cheap verification per step; dominant cost is browser/Mac execution, not model tokens. Compensation adds only for failed or cancelled runs.
- **security:** Never snapshot passwords, payment values, message bodies, or private page text. Store typed pre-state hashes or narrowly scoped reversible handles. Compensation must be allowlisted and itself verified; if it cannot safely restore, stop and require confirmation rather than guessing.
- **missing:** A first-class saga/compensation job record linking step receipts, verification evidence, and compensation receipts; Per-action declarations of reversible pre-state and a safe compensator; A user-facing mixed-state summary on the pendant and relay

### "“Complete this logged-in form or checkout, but do not tell the pendant, relay, or model any secret value; ask me for one physical approval only after showing me the non-secret summary.”"
- **useful because:** The browser is the only node that can hold authenticated sessions, while the pendant is the only trustworthy physical consent surface. This lets the owner delegate tedious authenticated work without exporting passwords, one-time codes, card numbers, or private form contents into the hive, and prevents a model from silently submitting a changed total or recipient.
- **path:** browser-extension → mac-planner → mac-vision → faculty-judgement → faculty-perception → faculty-action → relay-realtime → pendant
- **model tier:** Use a cheaper planner for field discovery and summary generation; use realtime only for the owner's spoken clarification or approval. Browser execution and postcondition inspection remain deterministic/allowlisted.
- **latency:** Non-secret preview in 2–4 seconds after the page is ready; after physical approval, submit and verify within the site's normal response time, with a 30-second timeout before unknown status.
- **cost:** One planning call and one minimal verification per form; browser I/O dominates. No secret values are sent to model or relay, reducing context and privacy cost.
- **security:** The browser extension must classify fields by sensitivity, redact secret/private values at the command boundary, and return only field labels, types, and hashes/lengths. OTP/password/payment fields require explicit owner entry or OS/browser-native secure UI. The pendant receives a digest and human-readable non-secret summary only; approval must be bound to the exact summary, URL/session, expiry, and submit intent. If URL, total, recipient, or digest changes, invalidate approval.
- **missing:** Sensitivity-aware browser command/result schema that can prove a field was filled without returning its value; A browser-native secure-entry handoff for OTP/password/payment fields; Approval binding to browser session, URL, summary digest, and submit action

### "“Forget everything you have about this topic everywhere—your relay, Mac notes/files, browser drafts, and pendant caches—and prove what was deleted and what you could not reach.”"
- **useful because:** Today the owner cannot reliably revoke one piece of personal information across the hive: a fact may exist in context-graph memory, a captured voice note, a Mac artifact, a browser draft, relay logs, or a queued pendant item. A single privacy erasure command would make the system trustworthy enough for intimate daily use, while reporting unreachable or immutable copies instead of claiming deletion.
- **path:** unified → faculty-judgement → faculty-perception → faculty-action → relay-realtime → mac-planner → mac-terminal → browser-extension → pendant
- **model tier:** Use a cheap background discovery/indexing model to locate candidate records; use the realtime tier only to clarify an ambiguous topic or confirm a destructive scope. Deterministic deletion and verification should run in the relay/Mac action layers.
- **latency:** Return a deletion scope preview within 5 seconds; execute asynchronously with progress and a final receipt. Never block the voice channel while scanning large Mac storage or relay history.
- **cost:** One low-cost classification pass plus read-only scans; storage traversal and deletion receipts dominate. No model should receive the private contents it is merely locating.
- **security:** Deletion must be scoped by opaque record IDs and content hashes, not broad keyword wipes. Require the existing physical approval latch for destructive deletion. Do not expose secrets in the preview. Use tombstones and idempotent receipts so retries cannot resurrect data; distinguish deleted, already absent, inaccessible, immutable-retention, and unknown. Browser deletion must cover drafts and local extension queues without touching unrelated logged-in data.
- **missing:** A cross-surface privacy index mapping topic-linked records to relay, context graph, Mac paths, browser artifacts, and pendant outbox/inbox IDs; Read-only deletion preview plus an idempotent delete operation with per-record provenance; Retention/backup semantics and a verifiable purge receipt for relay and Mac stores; A pendant-safe compact deletion summary bound to physical approval


## Changes it proposed to its own stack

### `hardware` — Add a low-profile rotary encoder with push switch to the jewellery pendant enclosure and integrate it as a signed action-inbox selector. The relay sends compact, non-secret pending-action cards (short label, risk class, expiry, digest); the pendant scrolls cards locally, gives distinct haptic/audio ticks at card boundaries, and sends only the selected opaque ID. Push/second button confirms selection through the existing physical transaction approval latch; scrolling never approves or executes. Keep at most 16 cards and expire them locally.
- **owner gets:** The owner can safely choose among several waiting actions without pulling out a phone or remembering which long-press gesture means what. This solves the real pendant crowding problem: multiple reminders, approvals, and retries become selectable while secrets and page contents stay off the jewellery.
- effort: Medium hardware/firmware integration: source a jewellery-scale encoder, add one GPIO plus debounce/interrupt handling, enable the existing I2C haptic/IMU bus only if used for feedback, define the compact signed card envelope, and add relay routing. Bench-test over the currently connected USB setup; USB remains a test transport, not a product mode.  ·  risk: False rotation or accidental push could select the wrong card, so rotation is strictly non-mutating and approval remains a deliberate separate gesture. Lost links may leave stale cards; every card needs expiry, monotonic sequence, digest, and explicit unknown state. Recover by dropping expired cards and replaying signed inbox state; never execute locally.
- cost: Prototype encoder roughly $2–8 and negligible incremental power; enclosure/mechanical work dominates. Firmware and relay work have no per-action API cost.  ·  latency: Local scrolling and feedback under 50 ms; relay round trip only when fetching cards or confirming a selected opaque ID.
- security: The pendant sees labels and risk classes only, never secrets or page contents. Signed cards bind action ID, summary digest, expiry, session, and approval nonce; stale or digest-mismatched cards are refused.
- depends on: Owner's planned rotary encoder/second-button product revision; physical_transaction_approval_latch (s10-j9l4); tactile_action_outcome_beacon; A compact signed action-inbox envelope shared by relay and pendant; A firmware GPIO and enclosure pinout decision


## What it asked for

_Nothing._
## Its own summary

Recorded three non-duplicate proposals: (1) cross-Mac/browser saga execution with independently verified compensations and truthful mixed-state reporting, (2) secret-preserving authenticated browser/form completion whose physical approval is bound to a non-secret digest and session, and (3) a jewellery-scale rotary encoder action inbox so the pendant can select among up to 16 pending actions without approving by scrolling. The first is the highest-value capability: it turns partial computer actions into recoverable, honest outcomes.

**Biggest unknown:** The owner still needs to choose the encoder’s physical form factor/pin budget and, separately, define which action classes may ever run without approval. The software gaps are concrete: compensation declarations, sensitivity-aware browser result schemas, and a signed compact action-card envelope. Existing approval, job, browser, execute, receipt, journal, and verification surfaces are the foundation; no new USB product transport is assumed.

