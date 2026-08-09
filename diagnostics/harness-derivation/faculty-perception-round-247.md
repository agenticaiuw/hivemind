# Harness derivation — faculty-perception — round 247

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-permissions-and-surfaces** — Live continuity snapshot at 2026-08-09T03:28Z reports Mac bridge reachable, browser extension online with Safari YouTube tab 85, Accessibility and Screen Recording granted, automation grants present, and no required permissions missing. Device discovery lists nrf9160-pendant offline (last seen 02:56:31Z), so pendant is registered stale but not live.
  - evidence: read_continuity_snapshot(include relay,pipeline) HTTP 200 body; discover(devices) live table

## Capabilities it proposed

### "When something fails, say which boundary failed—my speech capture, relay, Mac action, browser session, iPhone mirror, or final external effect—and give me the smallest useful recovery."
- **useful because:** The current system can report a job as complete when playback is still pending and can expose stale or truncated stores. A boundary-level diagnosis prevents repeated commands, makes failures understandable while away, and avoids claiming success from a single optimistic status.
- **path:** pendant → relay → mac → browser → iOS → dashboard
- **model tier:** Deterministic fault tree over telemetry, with a cheap background model to summarize only when multiple boundaries disagree; realtime speaks the result.
- **latency:** 1–3 seconds from a fresh snapshot; no more than 15 seconds if it must wait for a heartbeat or browser poll.
- **cost:** Low: bounded status reads and rules; occasional small summarization call, under a cent.
- **security:** Do not include raw audio, page text, or message contents in diagnostics. Treat browser and relay content as untrusted evidence; surface missing telemetry as unknown rather than failure.
- **missing:** Normalized boundary event schema with monotonic sequence and timestamps; Freshness policy distinguishing stale, absent, and negative evidence; Per-boundary health probes for iPhone mirroring and pendant link; Correlation between action receipts and resulting external state

### "Before I leave, give me a compact “handoff card” of everything still in flight, what is safe to resume, what expired, and what cannot be verified because the pendant is offline."
- **useful because:** The relay and Mac retain different bounded histories, announcements can be filtered but never deleted, and the pendant is currently stale. A handoff card would prevent lost work and false confidence after sleep, reboot, or a disconnected wearable.
- **path:** pendant → relay → mac → browser → iOS → dashboard
- **model tier:** Background reducer and scheduled job; realtime only reads the already-built card aloud.
- **latency:** Generate in under 5 seconds on demand and refresh on reconnect, sleep/wake, and before scheduled briefings.
- **cost:** Very low: metadata-only joins and cached state; model optional for a one-sentence summary.
- **security:** Cards should contain titles, IDs, timestamps, and confidence—not page bodies, message text, or secrets. Require confirmation to resume an action or resend audio.
- **missing:** Durable cross-surface handoff record independent of count-capped stores; Explicit expiry and ownership state for announcements and browser commands; Pendant reconnect import of offline reality beacon and capture verdicts; A distinction between pending, expired, delivered-to-socket, and owner-confirmed

### "Tell me whether the answer you are about to give is safe to act on right now, and if not, what single observation would make it safe."
- **useful because:** A live browser and Mac can coexist with a stale pendant, an expired relay job, or a machine-derived memory fact. The owner needs a direct trust boundary before acting, not another generic status page.
- **path:** pendant → relay → mac → browser → iOS → dashboard
- **model tier:** Deterministic evidence policy computes safe/unsafe/unknown and the missing-observation request; realtime verbalizes it, with no expensive model unless evidence conflicts.
- **latency:** Under 1 second for cached evidence and under 5 seconds when a fresh probe is allowed.
- **cost:** Very low: bounded metadata reads and policy evaluation; model usually unnecessary.
- **security:** Never treat untrusted browser text, relay socket delivery, or machine-originated preferences as proof. Require explicit confirmation before irreversible actions when the verdict is unknown.
- **missing:** Trust-policy engine with per-action evidence thresholds; Fresh probe orchestration for pendant, browser, relay, Mac, and iOS; Outcome classes distinguishing direct observation, derived state, and assertion; Owner-visible reason code for every unsafe/unknown verdict

### "Give me a physical privacy curtain: when I double-press the pendant or say “private,” stop listening everywhere, cancel unsent audio, prevent browser/Mac/iPhone actions, and prove afterward that nothing from the private interval was retained or acted on."
- **useful because:** A wearable assistant is present during conversations where the owner cannot safely inspect a screen. Today capture, relay buffering, browser sessions, and queued jobs have no single emergency privacy boundary; the owner must trust several independent components.
- **path:** pendant → relay → mac → browser → iOS → dashboard
- **model tier:** Firmware and deterministic policy only for activation, transport shutdown, cancellation, redaction, and proof. Realtime is used only to recognize the spoken trigger when the button is unavailable; no background model should inspect private audio.
- **latency:** Physical trigger must mute/cut uplink within 100 ms; relay and Mac/browser action barriers within 1 second; privacy proof available within 5 seconds of resume.
- **cost:** Low ongoing API cost; firmware state machine, relay cancellation, and local tombstone ledger dominate implementation.
- **security:** The curtain must fail closed on link loss, survive relay/Mac restarts, and prevent logs, browser spools, audio retention, transcripts, and model prompts from receiving private data. The proof should expose hashes, sequence ranges, and deletion attestations—not private content. Spoken activation is weaker than the physical trigger and must be clearly indicated.
- **missing:** A cross-surface privacy epoch and monotonic sequence protocol; Firmware-local mute latch and offline persistence; Relay and Mac APIs to cancel/erase queued audio and block new actions by privacy epoch; Browser/iOS command barrier that refuses commands during the epoch; Tamper-evident privacy receipt covering pendant, relay, Mac, browser, and iOS

### "Before you send a sensitive message, purchase, delete, or change an account, require a consent receipt bound to my physical pendant press, the exact final payload, the destination, and the browser/Mac session—and let me inspect or revoke that receipt later."
- **useful because:** A spoken confirmation today can be detached from the exact payload that eventually leaves a browser or iPhone, especially after a delayed job, page mutation, or reconnect. This gives the owner a durable, understandable proof of what they authorized.
- **path:** pendant → relay → mac → browser → iOS → dashboard
- **model tier:** Deterministic cryptographic receipt and policy engine; realtime or a cheap model may summarize the payload, but never decides whether consent is valid.
- **latency:** Show a concise confirmation in under 2 seconds; bind the receipt before transmission; revocation should propagate within 1 second while the action is still queued.
- **cost:** Low API cost; local hashing/signing and bounded receipt storage dominate.
- **security:** Sensitive payloads must be hashed or locally encrypted, not copied into relay logs. A receipt must expire, be single-use, identify the destination/session, and fail closed if the page or payload changes. Physical press should be required for high-risk classes.
- **missing:** Pendant secure monotonic consent counter and signing key; Canonical payload serialization shared by Mac, browser, and iOS paths; Relay-side single-use nonce and revocation endpoint; Pre-send interception hooks for browser and iPhone mirrored actions; Owner-facing receipt/revocation UI

### "In a room with other people, understand which words are mine, ignore bystanders by default, and ask me before any bystander speech is transcribed, remembered, or used to control my Mac, browser, or phone."
- **useful because:** A worn microphone hears everyone nearby. Today there is no durable speaker-boundary decision, so an innocent command or private remark from someone else can become a transcript, memory, or action. This makes the pendant socially safe to wear in shared spaces.
- **path:** pendant → relay → mac → browser → iOS → dashboard
- **model tier:** On-device voice activity and speaker-change detection for immediate gating; a small background model can classify uncertain turns, but uncertain speech must remain untranscribed. Realtime is only for an explicit owner confirmation.
- **latency:** Gate likely bystander audio within 150 ms; resolve an uncertain speaker turn within 2 seconds; never delay a clearly owner-directed command more than 300 ms.
- **cost:** Moderate engineering and model cost for speaker enrollment/classification; ongoing inference can remain local, with cloud use only after consent.
- **security:** Keep speaker embeddings local and encrypted; never upload bystander audio by default. False acceptance is worse than false rejection for actions and memory. Provide a visible/physical listening indicator and an audit record containing only decision metadata.
- **missing:** Firmware or bridge microphone channel for local speaker-boundary features; Owner enrollment and rotating local speaker embedding; Relay protocol carrying speaker decision and confidence with each utterance; Mac/browser/iOS policy that refuses action or memory writes when speaker is unknown; Dashboard control for shared-space mode, exceptions, and audit review


## Changes it proposed to its own stack

### `memory` — Add a provenance-aware quarantine rule for machine-originated facts of kind preference that conflict with authoritative live machine state. Keep the original immutable, but exclude it from the prompt head and mark it needs-review until the owner confirms or a fresh owner-originated value supersedes it. Apply first to preference.timezone=America/Chicago versus /etc/localtime America/New_York.
- **owner gets:** The owner stops receiving a confidently wrong timezone in every prompt, so “this morning,” routine times, and quiet hours resolve correctly without silently deleting their memory.
- effort: Small-to-medium: add conflict detector, projection filter, and review item; test against existing memory provenance.  ·  risk: A machine-derived preference could be quarantined when it was intentional. Recovery is one owner confirmation; original row remains intact and visible in review.
- cost: Negligible API cost; local memory read/write only.  ·  latency: A few milliseconds on projection, with cached conflict checks.
- security: Improves provenance safety; never exposes secret fact values in diagnostics beyond existing owner projection.
- depends on: Authoritative timezone resolver for the Mac; source.origin retained in memory projection; Owner review/confirmation route

### `context` — Introduce a trust ledger that records, per answer, the freshest supporting observation, its source surface, age, and whether it is direct evidence, derived state, or an unverified claim; expire trust independently from the underlying event stores.
- **owner gets:** The system can say “browser is online but the pendant has been offline for 32 minutes” instead of blending stale and live facts into one confident answer.
- effort: Medium: deterministic trust records and projection fields, then wire dashboard and voice summary.  ·  risk: False precision if clocks or source timestamps are wrong. Recovery is to label clock-skew and downgrade confidence rather than infer.
- cost: Low storage and compute; no model call required for the ledger.  ·  latency: Near-zero for cached summaries; small join cost on refresh.
- security: Metadata-only by default, with redaction of URLs, message text, and secrets.
- depends on: read_continuity_snapshot; source freshness metadata; clock-skew handling; dashboard trust rendering


## What it asked for

_Nothing._
