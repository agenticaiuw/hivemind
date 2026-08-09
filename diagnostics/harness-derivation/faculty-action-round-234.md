# Harness derivation — faculty-action — round 234

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“The Mac was locked when you tried that. Resume it automatically when I unlock, but re-check that the same page, file, and account are still in place before doing anything.”"
- **useful because:** A dropped or locked Mac should not turn a safe delegated task into either a silent failure or an unsafe blind retry. The relay can hold the intent, the Mac can wait for unlock, browser can reattach, and faculty-perception can independently revalidate every precondition before faculty-action continues.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-action
- **model tier:** background for queue supervision and revalidation; realtime only for the owner's short resume/cancel exchange
- **latency:** Immediate pendant acknowledgement; resume within 5 seconds of a fresh Mac heartbeat, otherwise remain staged
- **cost:** Low: mostly event/state checks and one cheap planner turn only when revalidation differs; dominant cost is browser/Mac evidence capture
- **security:** Never infer unlock from heartbeat. Keep the intent encrypted and secret-free on relay; require a fresh app/file/browser fingerprint and the existing physical approval latch after any material state change. If any check is unknown, stop and report unknown.
- **missing:** A real Mac lock/unlock event source (the current observe surface reports no lock state); A durable resume policy with explicit precondition hashes and invalidation reasons; A relay-to-Mac wake/unlock handoff (resume begins on the next agent heartbeat, never by bypassing login)

### "“There are several things waiting for my approval. Let me turn the pendant wheel to choose exactly one, tell me its short summary, and approve or cancel only that one.”"
- **useful because:** The current approval latch can safely queue decisions, but a single button/LED cannot let the owner distinguish multiple pending actions. A rotary selector makes the wearable a real control surface: the owner can disambiguate a browser submission from a file move without exposing page secrets or reaching for the Mac.
- **path:** pendant → relay → faculty-judgement → faculty-action → mac-planner → browser-extension
- **model tier:** Realtime for the terse spoken summary and haptic interaction; background for queue maintenance
- **latency:** Wheel-to-summary under 300 ms; approval result delivered within 2 seconds when connected; queue remains usable offline
- **cost:** Low per interaction; realtime tokens dominate, with compact signed queue records under 1 KB each
- **security:** Pendant receives only opaque action IDs, risk class, and redacted human summary—not credentials, page contents, or form values. Selection and approval must bind to nonce plus monotonic counter; stale or changed summaries cancel rather than approve.
- **missing:** Rotary encoder and one additional button in the jewellery enclosure (owner's stated product direction); Firmware input/state machine and haptic/audio vocabulary for browse, selected, approved, cancelled; Relay API for querying a bounded pending-action index and atomically reserving one item

### "“When I say ‘send this to the team’, use the note I just spoke, the file or page I am looking at, and the right logged-in destination to prepare one reviewable draft everywhere—but do not send anything.”"
- **useful because:** This turns the pendant into a bridge between fleeting speech and the owner's actual working context. The Mac can identify the foreground document, the browser can supply the authenticated destination, and the relay can preserve one provenance-linked draft; the owner gets a coherent draft instead of manually copying between surfaces, with sending still impossible until separately approved.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-action
- **model tier:** Background planner for extracting and formatting; realtime only to capture the spoken note and confirm the target audience
- **latency:** Capture immediately; draft package in under 15 seconds; no mutation beyond draft creation without explicit confirmation
- **cost:** Moderate: one planning turn plus Mac/browser reads; avoid realtime for composition and reuse extracted context across destinations
- **security:** Default to draft-only. Never transmit passwords, hidden fields, or unrelated page text. Require explicit target resolution when multiple team destinations exist; show source provenance and redact sensitive snippets before the draft leaves the Mac. Sending is a separate high-risk transaction with physical approval.
- **missing:** A typed cross-surface context capsule joining pendant audio, foreground Mac document, and browser session without copying whole pages; A draft-only multi-destination action primitive with per-destination previews and independent cancellation; A policy resolver for ambiguous audience names and private/public destinations

### "“If I change the page or file myself while you are working, stop before overwriting me, tell me exactly what conflicted, and let me choose whether to keep mine or yours.”"
- **useful because:** Today an agent can have a stale plan while the owner edits the same document or browser tab. Cross-surface conflict detection would make delegation safe in the way a human assistant is safe: owner work wins by default, and the system explains the precise divergence instead of silently applying an old action.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-action
- **model tier:** Cheap deterministic fingerprints and event comparison first; background model only to explain the conflict in plain language
- **latency:** Detect before each mutating step, under 500 ms for normal file/browser state; spoken/haptic warning immediately
- **cost:** Low to moderate; hashes and typed state dominate, with model cost only for ambiguous human-readable summaries
- **security:** Compare hashes, field identities, and structural metadata rather than exporting private content. Never merge secrets or submit after a conflict. Require explicit owner choice, with cancel as the default and physical approval for resuming a mutation.
- **missing:** A shared version vector spanning Mac files, browser tabs/fields, and relay action steps; Pre-mutation snapshots and typed conflict records consumable by faculty-perception; A pendant conflict interaction that distinguishes cancel, keep-owner-state, and retry-against-new-state


## Changes it proposed to its own stack

### `integration` — Add a signed Mac session-state provider to the local agent. It should publish login-session transitions (locked, unlocked, logged-out, asleep, awake), session generation, and observation age through a read-only route and event stream. The provider must use the host's native session APIs, not Accessibility or Screen Recording, and must never expose usernames, window contents, or credentials. On every unlock, emit a new generation so deferred faculty-action work cannot reuse pre-lock browser/file evidence.
- **owner gets:** The owner can ask the pendant to finish work after stepping away without risking execution against a changed or unattended Mac. Actions can wait for a real unlock event and then re-check their targets instead of guessing from a stale heartbeat.
- effort: Medium: native macOS session-state helper, signed event plumbing, route schema, and integration with the existing job/resume and verification records.  ·  risk: A missed or spoofed transition could resume the wrong work; recover by treating stale, contradictory, or unknown state as locked and requiring fresh verification plus the existing physical approval. No automatic unlock or credential handling.
- cost: Negligible runtime/API cost; small always-on helper and event storage.  ·  latency: Unlock-to-resume decision under one second when the agent is online; no polling burden.
- security: Improves safety by making lock state explicit. Events must be authenticated, minimal, retained briefly, and never include account secrets or page content.
- depends on: A durable deferred-action record containing precondition fingerprints and invalidation reasons; A resume coordinator that consumes session-generation changes and calls independent postcondition verification before execution


## What it asked for

_Nothing._
