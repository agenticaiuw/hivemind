# Harness derivation — faculty-action — round 176

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/browser reachability** — At 2026-08-08T03:04Z, AI Pendant Agent has Accessibility and Screen Recording trusted, inputReachability verified, secureInput false, and uiActionsWillReachTheScreen true. Safari browser bridge is online with 9 tabs and zero pending commands, but its published capabilities array is empty; pendant/LTE device remains absent from devices table.
  - evidence: GET /ops/snapshot and GET /observe returned the above; GET /devices discovery lists only Safari, home-macbook-bridge, and an offline mobile device.

## Capabilities it proposed

### "When I say “make this safe to share,” have the pendant identify the exact file or browser draft, the Mac/browser create a redacted copy, and return a side-by-side confirmation that no recipient, hidden metadata, or private fields remain before I send it."
- **useful because:** Prevents the most dangerous everyday mistake: sending the right-looking document with private content or metadata still embedded. It requires the worn device for intent, the Mac for filesystem/metadata access, the browser for authenticated compose context, and perception for independent verification.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-perception
- **model tier:** background for metadata/content inspection; realtime only to disambiguate the owner's spoken target
- **latency:** Initial inventory 2–5 s; redaction preview under 10 s; never send automatically without the existing physical approval latch.
- **cost:** Usually $0.01–$0.08 per invocation; dominated by document extraction/inspection, with browser and Mac actions otherwise local.
- **security:** Private document content must stay on the Mac/browser where possible; send only hashes, field labels, and minimal snippets to the model. Require physical approval for any outbound send. Preserve original read-only and make a new copy.
- **missing:** A cross-surface redaction/metadata inspector that emits a machine-readable manifest; Browser action support for attaching the generated copy and exposing recipient/draft fields to verification; A policy rule defining which metadata classes count as private

### "Let me say “I’m driving” or press the pendant’s focus gesture: pause non-urgent relay notifications, set the Mac to a safe focus mode, and restore everything automatically when I say “I’m parked,” with a visible countdown and an emergency override."
- **useful because:** A wearable is uniquely positioned to change interruption policy at the moment the owner needs it, while the Mac and relay control different notification sources. Automatic restoration prevents the common failure where focus mode stays on for hours and important messages are missed.
- **path:** pendant → relay → mac-planner → unified → faculty-perception
- **model tier:** background/rules engine; realtime only for spoken state changes
- **latency:** Engage in under 1 s from button or voice intent; restore in under 2 s after explicit parked signal. No model call is needed for known phrases.
- **cost:** Near-zero API cost after setup; a small classification call only for ambiguous spoken variants.
- **security:** Do not infer driving from location or microphone continuously. Store only focus-state timestamps. Emergency contacts and emergency-call notifications must bypass suppression. Restoration must be idempotent and verified against Mac state.
- **missing:** Pendant focus gesture firmware/state event (sw1 is the candidate); Relay notification policy with durable TTL and emergency bypass; Mac DND/Focus read-write plus postcondition verification; Owner-configurable safe phrases and emergency allowlist

### "After any multi-step request, tell me one honest sentence: “done,” “partly done,” or “unknown,” naming the exact step that still needs me; if the Mac or browser disconnects, resume from the last verified step instead of repeating or guessing."
- **useful because:** This is the single most useful reliability behavior: the owner can trust that a request involving files, apps, and authenticated tabs either completed or clearly stopped. It makes the pendant a dependable hand, not a source of duplicate sends or silent failures.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement
- **model tier:** background state machine; realtime only to summarize the final status aloud
- **latency:** Immediate acknowledgement; each step receipt within 1 s of execution; recovery on reconnect within 5 s.
- **cost:** $0.001–$0.02 per workflow; mostly local bookkeeping, with model cost only for final natural-language summary.
- **security:** Persist opaque operation/step IDs, hashes, timestamps, and sensitivity labels—not page contents or secrets. Never replay a non-idempotent step without a fresh verification and policy check. Unknown must be a first-class terminal state.
- **missing:** Durable cross-surface operation ledger with idempotency keys and dependency graph; Executor receipts that include actionId/attemptId and explicit side-effect scope; Automatic resume scheduler that consults verify_operation_step before retrying; Pendant delivery of compact status summaries when LTE is unavailable

### "Let me say “read me the thing I’m looking at” and have the pendant speak only the focused browser item or Mac selection, with passwords, payment data, tokens, and hidden page text automatically omitted; tell me the source title and URL before reading it."
- **useful because:** The owner can consume the important part of a screen without handling the Mac, while the pendant remains a safe output channel rather than becoming a leak of credentials. This is a concrete wearable-plus-browser-plus-Mac capability, not merely screen reading.
- **path:** pendant → relay → mac-vision → browser-extension → faculty-perception
- **model tier:** Realtime for the spoken request and short spoken response; local extraction/redaction first, cheaper background model for long selections.
- **latency:** Focused title/selection in 1–3 seconds; long-page extraction under 8 seconds; refuse rather than guess when focus cannot be identified.
- **cost:** $0.005–$0.04 per request, dominated by summarizing long text; titles, URLs, and short selections can be local.
- **security:** Sensitive-field detection must happen before model upload and before audio synthesis. Never read password inputs, cookies, hidden DOM, or clipboard history. Require an explicit second phrase to read content classified secret.
- **missing:** A focused-selection contract from the browser extension and Mac UI observer; A redaction classifier covering secrets and financial/identity fields; Pendant playback delivery and an audible refusal/status vocabulary

### "When I say “put this in the right place,” have the pendant identify the current file or browser record, show me a short destination preview, and then move or file it only after I make the deliberate physical confirmation; if the destination changes while I’m deciding, cancel instead of acting."
- **useful because:** Filing downloads, notes, and browser exports is repetitive but risky. The owner gets a reliable handoff from an ephemeral spoken reference (“this”) to a concrete filesystem or account destination, with a physical boundary against filing the wrong object.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension → faculty-perception → faculty-action
- **model tier:** Background planner for destination resolution; realtime only for clarifying ambiguous “this” or destination names.
- **latency:** Preview in under 4 seconds; action starts only after physical confirmation; re-check object and destination immediately before mutation.
- **cost:** $0.01–$0.06 per invocation for semantic destination resolution; filesystem operations and browser commands are local.
- **security:** Preview must expose names/types and destination, never file contents or secrets. Use hashes/inode identity to detect replacement, enforce allowed-path and account boundaries, and treat a changed browser tab or file as cancellation.
- **missing:** A cross-surface object identity envelope (file hash/inode or browser tab+record locator); A durable preflight snapshot that invalidates approval on drift; A destination resolver spanning Finder, Notes, Downloads, and authenticated browser records

### "Let me say “I’m handing this to you” while a Mac window or browser tab is open: create a durable handoff card containing the exact app/tab, selection, URL, and my spoken instruction, then let me resume it later from the pendant or Mac without reopening the wrong account or tab."
- **useful because:** People lose work at the boundary between a fleeting thought and a later computer task. This creates a trustworthy continuation point that uses the wearable for capture, the Mac/browser for exact context, and the relay for durable delivery—even if the original tab or link disappears.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-perception
- **model tier:** Background for compacting the handoff and deduplicating cards; realtime only for capture acknowledgement.
- **latency:** Capture acknowledgement under 1 second; card persisted within 3 seconds; resume must verify app/tab identity before presenting or acting.
- **cost:** $0.002–$0.02 per handoff; mostly local metadata storage, with model cost only for normalization.
- **security:** Persist opaque account/session identifiers, hashes, titles, and URL origin—not page bodies, cookies, or credentials. Mark private cards, expire them, and require reauthentication if the session changed. Never auto-submit on resume.
- **missing:** A durable handoff-card data model with expiry and sensitivity; Browser and Mac context snapshots that can be revalidated later; A pendant command to list/select cards when the LTE link is available


## Changes it proposed to its own stack

### `browser-harness` — Add a signed browser-bridge capability attestation and per-session action contract. On heartbeat, Safari reports concrete supported operations (inspect DOM, fill field, click, navigate, upload, read URL/title) with extension version, tab/session ID, and expiry; the relay refuses to enqueue an operation not covered by the current contract. Each result includes the contract hash and the browser tab identity so faculty-perception can verify the same tab rather than merely trusting “browser online.”
- **owner gets:** Authenticated browser sessions are the one place the system can reach accounts the Mac model cannot safely recreate. This makes “send the form / update the account” actually dependable: the owner gets a clear unsupported-action answer instead of a silently queued command, and actions cannot drift onto the wrong tab.
- effort: Medium: extension heartbeat schema, relay contract cache, command admission check, and result metadata; then exercise against the existing Safari session.  ·  risk: An extension update or stale heartbeat could temporarily make actions unavailable; recover by refreshing heartbeat and requiring a new contract. Never infer permissions from a claimed capability—verify result and URL/tab identity afterward.
- cost: Negligible API/storage cost; no hardware cost.  ·  latency: Adds under 50 ms admission check; heartbeat refresh may add up to one round trip before first action.
- security: Improves security by binding commands to a tab/session and expiring capability claims; capability metadata must not contain page contents or cookies.
- depends on: Existing Safari browser bridge heartbeat/poll/result routes; verify_operation_step for postcondition and tab identity; Owner policy for which browser operations may be staged versus require physical approval


## What it asked for

_Nothing._
## Its own summary

Round 176 produced three new owner-facing capabilities: privacy-safe share redaction, a driving/focus mode coordinated across pendant/relay/Mac, and resumable cross-surface workflows with honest done/partial/unknown status. Also proposed a browser-harness change: signed, expiring per-tab capability contracts because Safari is online but currently advertises capabilities=[]. Live probes confirm Accessibility and Screen Recording are now trusted, input reachability is verified, browser has 9 tabs and no pending commands, while no pendant is registered. The granted audio_path_probe still has no live implementation (resolver returned unresolved), so I did not claim an audio measurement.

**Biggest unknown:** Whether the browser extension can expose concrete operation capabilities and tab-bound postcondition evidence today, and whether a physical pendant can be registered/deliver receipts; both are required before claiming end-to-end wearable action completion.

