# Harness derivation — faculty-action — round 117

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **devices** — The reachable fleet still has Safari on MacIntel and home-macbook-bridge online, but no pendant; the only mobile device is offline and last seen 2026-07-31. Pendant-side confirmation and 24 kHz end-to-end verification cannot be validated this round.
  - evidence: discover(devices) returned Safari on MacIntel online, home-macbook-bridge online last seen 2026-08-07, and cloudflare-contract-test mobile offline last seen 2026-07-31; get_hardware_spec(audio) marks the 24 kHz path PROTOTYPE.

## Capabilities it proposed

### "“Do this across my Mac and logged-in browser, but don’t leave me half-done: check everything first, make the reversible changes, ask once before the final commit, and recover cleanly if one side fails.”"
- **useful because:** Today faculty-judgement can decide a goal, but faculty-action has no cross-surface transaction boundary. A calendar update plus browser form, or a drafted Mail message plus an authenticated submission, can partially succeed and leave the owner guessing. This gives one human-readable approval and a durable outcome instead of silent half-completion.
- **path:** faculty-judgement emits a typed action bundle with preconditions, reversible steps, irreversible commit steps, and compensation hints → relay persists the bundle and approval token, routes Mac steps to the online Mac bridge and browser steps to the authenticated Safari bridge, and survives a dropped pendant link → mac-planner/mac_run_actions performs AppleScript-backed reversible Mac steps and returns typed before/after receipts → browser-extension/browser_run_actions performs tab-affine reads and staged mutations, stopping at the declared commit gate → pendant speaks a compact 24 kHz approval summary and receives success, compensated-partial, or needs-owner-intervention status; Mac receives a local notification and a detailed receipt
- **model tier:** Use the cheap background model for precondition checking, step ordering, and receipt compression; reserve realtime only for the pendant approval exchange. No model should invent a commit step: the typed bundle is authoritative.
- **latency:** Preflight under 3 seconds when both bridges are online; approval response under 1 second after the owner presses the button; execution may run asynchronously with status pushed to the pendant and queryable later.
- **cost:** Usually <$0.01 in model/API cost, dominated by one short background planning/verification call; browser and Mac execution are local/relay work. Audio costs are dominated by the existing 24 kHz encode/decode path, not tokens.
- **security:** Private browser contents and potentially sensitive Mail/Calendar fields cross the relay only as scoped step inputs and receipts. Irreversible steps require an approval token bound to the exact normalized bundle hash, tab/session, and expiry; a changed page or stale precondition invalidates it. Compensation must never claim success when an external side effect cannot be undone.
- **missing:** A durable transaction coordinator with idempotency keys, precondition checks, compensation records, and explicit partial-failure states; A single approval-token protocol shared by Mac and browser bridges; Owner-defined compensation policies for actions such as sent messages, bookings, and payments; The already-requested verification/proof tools and physical confirmation skill, or an equivalent server-side implementation

### "“Make my contact details consistent everywhere I use them.”"
- **useful because:** The owner can discover information in one place and edit another, but cannot safely reconcile the same personal fact across native Mac apps and authenticated websites. This capability finds conflicting values, identifies which sources are authoritative, stages the necessary edits, and presents one concise conflict report before changing anything. It is not a watch or a one-off form fill: it resolves a named fact across multiple systems.
- **path:** Pendant captures the spoken target fact and reads back the proposed canonical value and conflict count for confirmation. → Relay creates a reconciliation job, keeps a source-by-source provenance record, and resumes it if the pendant link drops. → Mac agent reads and stages changes in Contacts, Calendar, Mail signatures, and other AppleScript-granted native stores. → Browser bridge inspects authenticated profile/account pages, identifies matching fields, and stages edits without submitting them. → Faculty-perception verifies each current value; faculty-judgement chooses or asks the owner to choose the canonical value; faculty-action applies only approved, field-specific mutations and returns before/after receipts.
- **model tier:** Use a cheaper background model for field matching, conflict clustering, and provenance summarization. Use realtime only for the brief pendant confirmation and ambiguity questions.
- **latency:** Collect and compare sources in 5–15 seconds; present a short conflict summary; apply staged edits asynchronously and report completion or blocked sources.
- **cost:** Typically under $0.03 per reconciliation, dominated by authenticated page extraction and one background reasoning call; native Mac reads are local.
- **security:** Contact details are sensitive and may include private account data. Never infer authority from frequency alone; require explicit canonical-source selection when values disagree. Bind approval to the exact field/value/source set, redact values in relay logs, and require a fresh confirmation if a page changes before mutation.
- **missing:** A reconciliation data model for normalized personal fields, source authority, provenance, and conflicts; Field-level staged mutation support across AppleScript and browser sessions; A shared approval payload that covers multiple heterogeneous targets without allowing extra fields to be added; A privacy-preserving receipt format that shows enough evidence to audit changes without retaining full page contents


## Changes it proposed to its own stack

### `relay` — Add a transaction coordinator between the existing /plan → /execute pipeline, Mac/browser action tools, and job receipts. It should persist a normalized bundle hash, per-step idempotency key, precondition snapshot, approval token, compensation plan, and state machine (prepared, approved, running, committed, compensated, partial-needs-owner). Dispatch each step to its owning surface, refuse stale or changed preconditions, and emit one aggregate receipt with exact before/after evidence. Never run a second attempt unless the step key is known-safe; expose an explicit owner-intervention state when an external side effect cannot be undone.
- **owner gets:** A request spanning Safari and the Mac either completes coherently or tells the owner exactly which side happened and what remains. They no longer have to inspect several job IDs or wonder whether retrying sent a duplicate message or submitted a form twice.
- effort: Medium-high: relay state machine and D1 schema, typed bridge responses, compensation adapters for reversible AppleScript/browser mutations, and integration tests for disconnects and duplicate delivery.  ·  risk: A coordinator bug could block valid work or misreport compensation. Recover by making the state machine append-only, requiring explicit evidence for every transition, retaining the existing per-job receipts, and routing ambiguous external effects to needs-owner rather than guessing.
- cost: Negligible storage/API overhead per step; one additional cheap verification call for bundles with multiple surfaces. No new realtime model call.  ·  latency: Adds roughly 100–300 ms for persistence/precondition validation; execution remains asynchronous and can continue after the pendant disconnects.
- security: Improves safety by binding approval to exact bundle hash, session/tab affinity, and short expiry; reduces replay and confused-deputy risk. Relay must avoid storing raw private page content in coordinator rows.
- depends on: A typed action-bundle schema shared by faculty-judgement, Mac, and browser; A server-side approval/proof mechanism (the requested verification tools or equivalent); Explicit compensation policy for each irreversible action class; Reliable bridge heartbeat and idempotent dispatch

### `integration` — Add a field-reconciliation layer that sits above Mac and browser action primitives. It should normalize a requested fact into typed fields, collect current values with source and timestamp, detect conflicts and semantic duplicates, require an explicit canonical value for disagreements, and emit a signed field-level mutation set. Each mutation must be staged before execution and bound to the exact source/value snapshot; if any source changes, invalidate only affected fields rather than replaying the whole set.
- **owner gets:** The owner can correct an address, phone number, name, or preference once and know exactly which native apps and logged-in sites were updated, while seeing unresolved conflicts instead of silently propagating a bad value.
- effort: Medium: schema and matching logic in the relay, AppleScript adapters for native stores, browser field adapters, and a field-level receipt/approval UI.  ·  risk: Incorrect field matching could alter the wrong account field. Recover by defaulting to staged-only mode, requiring source-specific evidence and exact-value approval, and allowing per-field rejection; unchanged sources remain untouched.
- cost: Low storage and model cost; one background extraction/matching pass per source set. No new realtime inference required.  ·  latency: Adds seconds for cross-source reads and conflict analysis, but avoids repeated manual edits and retries.
- security: High sensitivity because it handles identity data. Encrypt or minimize stored values, redact relay logs, scope browser sessions explicitly, and expire staged mutation sets quickly.
- depends on: Typed source/provenance schema; Per-field approval and mutation receipts; Mac and browser adapters that expose stable field identifiers; Owner-granted browser access for each target account


## What it asked for

_Nothing._
## Its own summary

Recorded a new owner-facing capability: reconcile one personal fact across native Mac apps and authenticated websites, detect conflicts, stage exact field-level edits, and apply only after approval. Also recorded the required integration layer for typed provenance, conflict resolution, staged mutations, and field-specific invalidation. This is distinct from page watching, morning briefings, generic form drafting, or transaction execution.

**Biggest unknown:** Which personal-data sources the owner considers authoritative for each field (for example Contacts versus a specific account profile), and which authenticated browser accounts they would permit this reconciliation to touch.

