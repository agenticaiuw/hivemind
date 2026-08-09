# Harness derivation — faculty-action — round 165

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Finish that task even if my Mac disconnects, and tell me exactly whether it completed, resumed, or needs me.”"
- **useful because:** Today a multi-step action can stop after an unknown side effect when the bridge or browser disappears. A durable checkpointed executor would resume only after independently verifying the last completed step, preventing duplicate sends, purchases, or edits while letting the owner walk away from the pendant.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-action
- **model tier:** background for checkpoint planning and reconciliation; realtime only for the owner's short status question
- **latency:** Immediate acknowledgement under 1 s; resume within 10 s of bridge return; reconciliation may take up to 60 s
- **cost:** Usually < $0.01 per recovery; dominated by one or two perception/browser calls, not generation
- **security:** Persist only opaque operation IDs, step hashes, and risk metadata in relay; never persist form secrets. High-risk resumed steps require the existing pendant physical approval latch. An unknown postcondition must stop rather than guess.
- **missing:** durable operation state machine with idempotency keys; executor receipt schema correlated to verification provenance; automatic reconnect/resume worker; policy for which steps may resume without a new approval

### "“Before you change anything across my Mac and browser, show me the exact before/after diff, then make the whole bundle—or roll every reversible part back.”"
- **useful because:** The owner can ask for a goal spanning Finder, Calendar, Mail, and a logged-in browser, but existing action execution is step-oriented and leaves the owner to infer the net effect. A cross-surface transaction would expose one understandable diff, commit atomically where possible, and automatically undo reversible mutations when a later step fails.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-action
- **model tier:** background for planning and diff construction; realtime for presenting a concise spoken summary
- **latency:** Preview in 5–15 s; commit starts only after explicit approval and reports each step; rollback begins within 2 s of failure
- **cost:** $0.01–$0.05 per bundle, driven by browser/file inspection and rollback verification
- **security:** Diffs must redact secrets and private field values by default, showing labels and hashes instead. Existing physical approval latch signs the bundle digest, not individual hidden mutations. Irreversible steps are isolated and staged for a second explicit confirmation.
- **missing:** cross-surface transaction/bundle schema; dry-run adapters for AppleScript and browser commands; compensating-action registry with safety levels; diff renderer for spoken pendant summaries and detailed Mac view

### "“When I ask you to handle something private in a browser, use the session I already have, keep the contents off the relay, and leave me a verifiable receipt without exposing the secret.”"
- **useful because:** The browser bridge holds sessions the relay cannot reach, but action planning, execution, and proof currently have no uniform privacy boundary. A privacy-preserving browser action lets the Mac/browser perform the sensitive work locally while the pendant receives only a redacted intent, outcome class, and proof hash—useful for banking, health portals, and work systems.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-action
- **model tier:** realtime for intent clarification only; local Mac planner and browser harness perform execution; background relay stores minimal receipt
- **latency:** Intent acknowledgement under 1 s; ordinary operation 5–30 s; receipt available immediately after local verification
- **cost:** <$0.02 per operation; mostly local execution, with low token use for intent and summary
- **security:** Relay must receive no page text, credentials, cookies, or screenshots. Browser extension returns structured outcome and salted hash/provenance only. Sensitive actions use the existing physical approval latch; failed verification returns unknown, never success.
- **missing:** privacy-classified browser command/result protocol; local-only secret handling and redaction enforcement; hash-chain receipt format with browser tab/session provenance; capability policy mapping risk classes to approval requirements

### "“If I change my mind while you are acting, stop the old task everywhere and carry out only the newest instruction.”"
- **useful because:** Today a spoken correction can race with already queued Mac or browser commands, leaving a stale action running after the owner's intent changed. The owner needs one authoritative intent stream that cancels queued work, revokes in-flight leases where possible, and prevents late results from being mistaken for the current task.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-judgement → faculty-action → faculty-perception
- **model tier:** realtime for detecting and confirming the correction; deterministic relay/action protocol for cancellation and stale-result rejection
- **latency:** Cancellation acknowledgement under 500 ms; no new stale command after 1 s; already-running steps report cancelled or unknown within 10 s
- **cost:** <$0.01 per correction; protocol work dominates, not model tokens
- **security:** Every command carries an intent generation and revocation token. Cancellation cannot claim rollback unless perception verifies it. Private command payloads stay on the responsible local surface; the relay stores only hashes and lifecycle state.
- **missing:** monotonic intent-generation protocol across relay, Mac, and browser; revocation endpoint checked before every side effect; late-result quarantine and UI/status semantics; safe cancellation adapters for AppleScript and browser commands

### "“Notice when I or another app changed the thing you were working on, stop before overwriting it, and ask me about the conflict in one sentence.”"
- **useful because:** An action can be logically valid when planned but become destructive when the owner edits the same file, calendar event, message draft, or browser field during execution. The owner needs optimistic concurrency across every action surface, with a human-readable conflict instead of silent last-writer-wins behavior.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-action
- **model tier:** cheap deterministic hashes and local observers for detection; realtime only to explain a detected conflict
- **latency:** Conflict detection before each mutation, under 1 s; spoken question within 2 s of detection
- **cost:** <$0.01 per action; mostly local state hashes and observers
- **security:** Use metadata, hashes, and field labels rather than copying private contents to the relay. Treat a missing or stale observation as conflict/unknown, never permission to overwrite. Require explicit approval for a force-overwrite.
- **missing:** precondition snapshot protocol for files, app records, and browser fields; watchers or fresh reads immediately before mutation; standard conflict object with safe redacted summaries; force-overwrite approval path tied to the existing physical approval mechanism

### "“Give me one honest answer about everything you asked my devices to do—even if some devices are offline—and let me replay the exact unfinished parts when they return.”"
- **useful because:** Today status is fragmented across relay jobs, Mac jobs, browser commands, and pendant delivery. The owner cannot distinguish completed, delivered, heard, pending, expired, or unknown work from one spoken request. A federated action ledger would reconcile all surfaces into one lifecycle and make offline work replayable without duplicating completed effects.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-action → unified
- **model tier:** background reconciliation and deterministic state reduction; realtime only for concise owner queries
- **latency:** A status answer under 2 s from cached ledger; fresh reconciliation under 15 s when devices are online
- **cost:** <$0.01 per status query; storage and reconciliation dominate
- **security:** Ledger entries contain opaque IDs, risk class, timestamps, hashes, and outcome states—not secrets or page contents. Device-return replay requires expiry checks, idempotency, and approval revalidation for sensitive actions.
- **missing:** federated action-ledger schema spanning relay/Mac/browser/pendant; delivery and playback acknowledgements distinct from execution receipts; replay coordinator with idempotency and expiry; single owner-facing status vocabulary and query endpoint


## What it asked for

_Nothing._
