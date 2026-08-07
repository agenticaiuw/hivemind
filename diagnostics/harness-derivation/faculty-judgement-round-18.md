# Harness derivation — faculty-judgement — round 18

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "While I listen to my brief on the pendant, let me say “why?” or “open that,” and have you explain the evidence or open the exact source on my Mac without losing my place."
- **useful because:** A spoken summary is only useful if the owner can challenge one item in the moment. This turns passive audio into a trustworthy, resumable interaction: the pendant supplies low-friction control, the relay keeps the conversation alive, and the Mac/browser can reveal the private source that cannot be fetched server-side.
- **path:** relay-realtime → pendant → mac-planner → browser-extension → dashboard
- **model tier:** Use the cheap background tier to assemble and cite the brief; use realtime only for the owner's short interruption and a concise explanation; use mac-planner/browser only when the owner asks to open or inspect a private source.
- **latency:** Audio control acknowledgement under 300 ms; evidence answer under 3 s; opening a private source under 8 s. Preserve a durable playback cursor and a per-item source bundle so reconnecting does not restart the brief.
- **cost:** About $0.01–$0.08 per daily brief depending on source count and audio length; interruption cost is usually <$0.01. Dominant costs are synthesis/audio generation and any private-page extraction, not button handling.
- **security:** Private mail/calendar/browser text must remain on the Mac/browser bridge unless explicitly summarized into the relay response. Never open a sensitive source aloud in a shared space without a confirmation or a privacy mode; redact secrets from citations. “Open that” is reversible navigation, but sending, purchasing, or editing still requires the existing confirmation gate.
- **missing:** A durable audio playlist with item IDs, playback cursor, and source citations; A pendant control protocol for pause/replay/next/why/open-that with offline buffering; A cross-surface source handoff that maps an audio item to a reattachable Mac/browser tab and evidence snapshot; A privacy-aware spoken-response policy and dashboard showing what source was exposed

### "When I hear something in a brief, let me say “save that,” “remind me Friday,” or “add this to the email draft,” and have it capture the exact item and source, then resume where I was."
- **useful because:** The owner should not have to remember or stop what they are doing to act on an insight. The pendant hears the intent, the relay identifies the current brief item, the Mac creates the reminder/note/draft, and the source remains attached so the follow-up is trustworthy rather than a vague transcription.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Background model prepares the brief and structured item IDs; realtime handles the short command and confirmation wording; mac-planner/browser performs note, reminder, or draft creation. No expensive model is needed for routine capture.
- **latency:** Acknowledge and pause under 300 ms; create a reminder or note under 3 s; resume audio within 500 ms. If the Mac is asleep, persist the intent at the relay and complete it when the Mac returns, with an honest queued receipt.
- **cost:** Typically <$0.01 per capture; the main cost is occasional background brief synthesis. Durable queue and idempotency avoid repeated API calls after reconnects.
- **security:** The exact source may contain private mail or account data; keep it on the Mac and store only a source reference plus the minimum quoted text. Creating reminders/notes is permitted by the owner's preference; adding to an email draft is reversible but must never send. Ask before including sensitive text in a draft.
- **missing:** A structured audio-item manifest shared by relay and Mac; Intent capture that binds an utterance to the currently playing item and playback cursor; An idempotent deferred-action queue with completion receipts; A source-preserving notes/reminders/draft API and a pendant resume control

### "When I ask something sensitive while I’m around other people, answer privately through the safest available surface—haptic confirmation on the pendant and a discreet Mac or phone display—instead of speaking the secret aloud, and let me switch back when I’m alone."
- **useful because:** A wearable assistant that cannot distinguish private from public context forces the owner either to avoid useful requests or risk exposing mail, health, account, and relationship information. The pendant can remain useful in public without becoming a loudspeaker for secrets.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheap classifier and explicit owner rules for sensitivity and surface selection; reserve realtime for the live request and a short acknowledgement. Mac/browser fetch private content locally, while the relay returns only a redacted result or control signal.
- **latency:** Detect and acknowledge the privacy mode within 250 ms; deliver a one-sentence safe result within 2 s; switch output surfaces within 1 s. If context confidence is low, default to silence plus haptic and ask the owner to choose.
- **cost:** Under $0.01 per interaction beyond the normal request; the dominant cost remains any underlying private-page extraction or model response. Haptics and local routing are effectively free.
- **security:** Do not infer sensitive context from untrusted ambient audio beyond the owner’s command and explicit settings. Store no ambient recordings. Keep account data on the Mac/browser, use redacted previews, require confirmation before displaying highly sensitive content on a shared Mac screen, and provide a physical gesture to cancel speech immediately.
- **missing:** A cross-surface privacy policy with sensitivity labels and output-surface rules; Pendant firmware support for immediate mute/haptic-only acknowledgement and a cancel gesture; A Mac/browser discreet-output channel that does not steal focus or expose content to screen sharing; A local or paired-device presence/context signal, with a conservative unknown state; An auditable dashboard showing where each response was delivered


## Changes it proposed to its own stack

### `integration` — Define a signed Brief Item Manifest exchanged between background jobs, relay, pendant, Mac, and browser: each spoken item has a stable item ID, short text, sensitivity class, source references, allowed follow-up intents, audio offsets, and an expiring playback cursor. Relay actions use request IDs and return a receipt; Mac/browser resolves private source references locally and can reattach the exact tab or draft context.
- **owner gets:** The owner can interrupt a brief with natural language and get a precise answer or follow-up instead of losing the place, repeating themselves, or receiving an untraceable summary. It also makes queued work honest when the Mac is asleep or the link drops.
- effort: Medium-high: schema and signing, relay persistence, pendant control messages, background brief generation changes, Mac/browser source resolver, and dashboard inspection UI.  ·  risk: Stale or mismatched item IDs could attach an action to the wrong source. Use short expiry, source hash checks, explicit item text in the confirmation, and idempotency. If the manifest is unavailable, fall back to ordinary playback and say that capture is queued.
- cost: Small storage and relay/database overhead; roughly <$0.01 per interaction. No extra model call for pause/next; only follow-up explanation or extraction incurs model cost.  ·  latency: Adds negligible local lookup latency; source opening may take several seconds. Cursor persistence makes reconnect recovery faster.
- security: Manifests may reveal sensitive topics, so encrypt at rest, minimize quoted text, enforce per-item sensitivity and expiry, and keep private source bodies on the Mac/browser. Signed references prevent a stale tab or another job from being mistaken for the source.
- depends on: Durable audio playlist and cursor; Idempotent cross-surface job/event persistence; Private-source browser/Mac reattachment; Pendant control protocol and privacy-aware spoken output

### `hardware` — Replace the prototype single-button development-kit interaction with a production pendant that has a physically latched microphone mute/privacy switch, a distinct tactile privacy button, a small haptic motor, and a privacy-status LED visible to the wearer. Expose the switch state electrically to firmware so the relay cannot override it, and make the default after boot or fault muted until the owner deliberately enables listening.
- **owner gets:** The owner can trust the pendant around other people and can silence it instantly without negotiating with software. A visible, physical state prevents the worst failure mode—believing the assistant is private when it is still listening or speaking.
- effort: High: new enclosure and board, microphone/audio power gating, certified radio/audio design, firmware state machine, relay acknowledgement, accessibility testing, and a recovery path for a stuck or damaged switch.  ·  risk: A physical mute fault could make the pendant appear safe while audio remains active; use dual electrical sensing, a fail-closed audio gate, startup self-test, and a periodic haptic/LED fault indication. Accidental mute reduces availability but never compromises privacy.
- cost: Prototype redesign roughly $15–$40 in added components and enclosure work per unit, plus certification/NRE; negligible ongoing API cost and modest battery draw only while haptic/LED indicators run.  ·  latency: Local mute is immediate (milliseconds) and does not depend on cellular, relay, or Mac availability. Privacy-mode surface selection still needs the software path described above.
- security: Improves the security boundary by making microphone disablement hardware-enforced and observable. The switch state must be included in every relay session and job receipt; no server command may unmute it.
- depends on: Dedicated production pendant hardware rather than the nRF9160 development kit; Firmware audio power-gating and fail-closed boot behavior; Relay/session protocol carrying authoritative mute state; Privacy-aware output routing on Mac/browser


## What it asked for

### `t8-zr10` (tool) — audio_brief_item_action
- why: The two proposed capabilities need a durable, source-linked way to pause the pendant brief, bind the owner's utterance to the current item, and enqueue a reminder/note/draft without losing playback position. Existing tools expose generic Mac/browser actions but not the semantic audio cursor or idempotent item action.

```json
{
  "type": "object",
  "properties": {
    "operation": {
      "type": "string",
      "enum": [
        "get_state",
        "pause",
        "resume",
        "next",
        "previous",
        "defer",
        "create_note",
        "create_reminder",
        "append_to_draft",
        "get_evidence"
      ]
    },
    "item_id": {
      "type": "string"
    },
    "cursor_token": {
      "type": "string"
    },
    "text": {
      "type": "string"
    },
    "due_at": {
      "type": "string",
      "description": "ISO-8601 timestamp for reminders"
    },
    "target": {
      "type": "string",
      "description": "Note, reminder, or draft identifier"
    },
    "request_id": {
      "type": "string",
      "description": "Idempotency key"
    }
  },
  "required": [
    "operation",
    "request_id"
  ]
}
```

### `s3-l7fk` (skill) — brief_item_bookmark
- does: On a short double-press while a brief is playing, pause playback, emit a local bookmark event containing monotonic time, playback offset, button gesture, and a small rolling audio-item correlation token; on reconnect, upload it so the relay can bind it to the exact brief item and resume playback. A long press cancels the last bookmark before upload.
- must be on-device because: The gesture must work while the owner is walking, during a dropped cellular link, and without requiring a spoken interruption. Only the pendant can capture the exact physical moment and preserve it offline.
- trigger: Pendant button double-press; long-press within five seconds cancels the pending bookmark.
- storage: Ring buffer in nonvolatile settings or a small flash log: up to 32 bookmark records, each ~48–96 bytes (timestamp, offset, token, flags, CRC), under 4 KB; clear after relay acknowledgement.
- RAM budget: ~3–6 KB for event queue and serialization, plus existing audio buffers; designed to fit comfortably within 211,608 B application RAM, with no additional codec or model memory.

## Its own summary

Round 18 produced a new cross-surface capability: interrupt a spoken brief with “why?”, “open that,” “save that,” or “remind me,” while preserving the exact item, evidence, and playback position. I proposed a signed Brief Item Manifest and idempotent source-linked action protocol across background jobs, relay, pendant, Mac, and browser; requested the audio_brief_item_action tool; and requested an offline pendant double-press bookmark skill that works through link loss with a tiny flash ring buffer. The owner gets resumable, evidence-backed audio rather than passive summaries or lost follow-ups.

**Biggest unknown:** The durable audio playlist/cursor and cross-surface event primitives—and the pending audio acceptance criteria—are still not visible to me. I still need those implemented or exposed, plus the private-source reattachment path, before this can be made reliable end to end.

