# Harness derivation — faculty-judgement — round 8

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **pendant hardware constraint** — Current prototype is nRF9160 DK, 64MHz Cortex-M33, 211,608B app RAM, 1MB flash, single button/LED; 24kHz audio work must stay bounded and product hardware is not fixed.
  - evidence: get_hardware_spec(pendant)

## Capabilities it proposed

### "“I can’t deal with this now—bring it back to me later.” Then, at the right time, remind me with the exact page, message, or file I was looking at and a one-sentence explanation of what I meant to do; let me snooze or finish it by voice."
- **useful because:** People lose commitments at the handoff between attention states. This turns an offhand spoken intention into a reliable return to the precise context, rather than a generic reminder that requires reconstructing the task.
- **path:** pendant captures the spoken intent and gives immediate audible confirmation → relay stores a durable deferred-action packet and schedules the return → Mac planner resolves the relevant local file/window and browser extension resolves the authenticated tab, each with read-only evidence → relay recontacts the pendant at the chosen time; Mac/browser re-open or stage the context without sending/submitting anything → dashboard shows the packet, source evidence, snooze history, and a clear delete control
- **model tier:** gpt-realtime-2.1 only for the short capture/confirmation and spoken return; gpt-5.6-luna on the relay/Mac for deferred interpretation and context resolution; gpt-4.1-mini only for screenshot/UI grounding when selectors fail. No expensive realtime turn while asleep.
- **latency:** Capture confirmation under 1.5s. Background context resolution under 30s. At reminder, spoken summary within 3s, with staged context allowed to follow asynchronously.
- **cost:** About $0.01–$0.08 per deferred item depending on browser/UI recovery; realtime audio dominates capture, while most scheduled work uses cheaper model and can be batched.
- **security:** The packet may contain private page text, file paths, and sensitive intent. Encrypt at rest, retain only a bounded source excerpt plus hashes, honor existing browser-read permission, and require confirmation for any send, delete, purchase, or other irreversible action. Never expose secrets in spoken notifications or dashboard previews by default.
- **missing:** durable deferred-action packet and scheduler with idempotent lifecycle; cross-surface context handoff that can bind a browser tab, Mac window/file, and source evidence; voice snooze/complete controls and a notification quiet-hours policy; owner-visible retention and deletion controls

### "“Protect my attention. While I’m working or in a meeting, decide which incoming things truly deserve an interruption; quietly queue the rest, and tell me afterward what you held back and why.”"
- **useful because:** Today notifications compete blindly with the owner’s attention. The hive should understand the owner’s current activity, urgency, relationship, and deadline, then make a transparent interruption decision rather than merely forwarding alerts or producing another periodic briefing.
- **path:** pendant detects the owner’s interruptibility mode locally from button state, spoken preference, and connection status, and provides a discreet haptic or short spoken interrupt when authorized → relay remains awake, receives candidate events, applies quiet-hours and escalation policy, and keeps an auditable held/allowed queue → Mac planner reads foreground app/window, calendar meeting state, local task deadlines, and notification metadata without exporting unnecessary content → browser extension inspects only opted-in authenticated tabs for urgent changes and supplies source evidence; it never sends or mutates anything → dashboard lets the owner set policies such as ‘never interrupt calls except family’ and review, release, or permanently dismiss held items
- **model tier:** Use a cheap background model for event classification and policy explanation; use gpt-5.6-luna only for ambiguous cross-source conflicts; reserve gpt-realtime-2.1 for the rare spoken escalation and the owner’s reply. Deterministic deadline/contact rules should run without a model.
- **latency:** Candidate events should be classified in under 2 seconds. A permitted urgent interruption should reach the pendant within 3 seconds; held events can be summarized in a later batch.
- **cost:** Roughly $0.01–$0.05 per classified burst, dominated by private-content summarization; metadata-only rules should be effectively free. Realtime cost occurs only when an interruption is actually delivered or discussed.
- **security:** This system sees highly sensitive notification, calendar, browser, and activity metadata. Process metadata locally where possible, minimize snippets sent to the relay, encrypt the queue, define short retention, expose the reason/source for every decision, and require explicit confirmation before any reply, dismissal, or external action. A fail-safe mode must hold rather than suppress when classification is uncertain.
- **missing:** an interruptibility policy language with precedence, contacts, deadlines, and escalation windows; a local Mac activity/calendar/notification broker that emits privacy-minimized candidate events; a relay-side durable held-event queue with reason codes, replay protection, and delivery acknowledgements; pendant haptic/privacy interaction hardware and firmware for discreet acknowledgement; a review UI showing what was interrupted, held, expired, or escalated and allowing policy correction


## Changes it proposed to its own stack

### `integration` — Add a typed Resume Packet protocol for deferred intentions. A packet contains intent, capture timestamp, owner-selected return time/condition, sensitivity, source references (browser tab/session or Mac window/file), a minimal redacted excerpt and content hash, resolution status, and lifecycle events (captured, staged, reminded, snoozed, completed, deleted). At reminder time, each surface independently revalidates its source; if it changed or disappeared, report that explicitly and offer a safe fallback instead of silently opening the wrong context.
- **owner gets:** A reminder will bring back the thing they actually meant to do, with honest evidence when the original page or file has changed, and without accidentally acting on stale information.
- effort: Medium-high: shared schema and persistence, relay scheduler, Mac/browser adapters, voice commands, dashboard review/deletion UI, and end-to-end crash/idempotency tests.  ·  risk: A stale or misbound tab could reveal the wrong private context. Mitigate with source hashes, tab/session affinity, visible source title/domain, revalidation, redacted notifications, and confirmation before mutation. If a surface is offline, retain the packet and retry rather than losing it.
- cost: Small per-packet storage and one background model call; no realtime cost except capture and reminder. Engineering cost is mostly adapter and recovery tests.  ·  latency: Negligible capture overhead; staging can happen in background. Reminder may take 1–3s to verify sources, with a concise fallback spoken immediately if unavailable.
- security: Improves security by making provenance and retention explicit, but requires encrypted packet storage and strict sensitivity-aware logging; source excerpts should be minimized and deletable.
- depends on: durable job/event persistence primitives; browser command queue with tab/session affinity; Mac window/file identity adapter; voice reminder/snooze intent handling

### `hardware` — Design the product pendant (not the provisional nRF9160 DK) with a low-power haptic actuator and a two-stage tactile control: short press acknowledges/snoozes the current reminder, long press cancels or marks complete; add a hardware privacy LED state that is unambiguous but does not expose notification content. Keep the nRF9160-class audio path separate from haptic/UI state so a dropped link can still acknowledge locally and queue the event for relay reconciliation.
- **owner gets:** They can handle a reminder discreetly in a meeting, on a bike, or when speech is inappropriate, and a lost connection will not make a reminder impossible to dismiss or cause repeated interruptions.
- effort: Medium hardware revision plus firmware event queue and relay reconciliation tests; prototype with an ERM/LRA haptic motor, driver, sealed button, and revised enclosure.  ·  risk: Accidental presses or vibration fatigue could dismiss an important item. Use distinct press durations, a reversible local snooze rather than destructive completion, confirmation vibration patterns, and replay-safe event IDs. Validate comfort, water resistance, and pocket activation.
- cost: Roughly $3–$10 BOM increase in volume (motor/driver, tactile control, enclosure changes), plus a few mA only while vibrating; negligible API cost.  ·  latency: Local acknowledgement under 100ms; relay synchronization waits for connectivity and must be eventually consistent.
- security: Improves privacy by reducing forced spoken interaction. The privacy LED must avoid encoding sensitive categories; only generic busy/listening states should be shown.
- depends on: resume packet lifecycle semantics; pendant firmware event queue and reconnect reconciliation; industrial-design and battery validation


## What it asked for

### `t4-b4ht` (tool) — resume_packet
- why: The proposed deferred-intention capability needs one durable, provenance-aware object spanning pendant capture, relay scheduling, Mac/browser context restoration, snooze/complete, and deletion. Existing generic action tools cannot guarantee source binding or idempotent lifecycle.

```json
{
  "operation": "string enum: create|get|list|transition|delete",
  "packet_id": "string optional",
  "intent": "string optional",
  "return_at": "ISO-8601 timestamp or condition optional",
  "source": {
    "kind": "browser|mac_file|mac_window|voice_only",
    "stable_id": "string",
    "title": "string optional",
    "url_or_path": "string optional",
    "excerpt_hash": "string optional"
  },
  "sensitivity": "string enum: normal|sensitive|secret optional",
  "transition": "string enum: staged|reminded|snoozed|completed|cancelled optional",
  "snooze_until": "ISO-8601 timestamp optional",
  "idempotency_key": "string optional"
}
```

## Its own summary

Round 8 produced a new cross-surface capability: deferred intentions that return the owner to the exact browser page, Mac file/window, or source context, with revalidation, voice snooze/complete, provenance, and deletion. I proposed the Resume Packet protocol, requested the missing durable tool, and proposed product hardware with discreet haptic/tactile reminder controls that work offline. I also recorded the concrete nRF9160 prototype constraints so 24 kHz audio and local event handling are budgeted honestly. Still needed from the orchestrator: the harness-ledger priorities and audio acceptance criteria, cross-surface job/event persistence details, the pending commitment-ledger and situational-note tools, pendant diagnostics/bug-draft tooling, and the requested Mac/browser authorizations if they have not actually landed; these are prerequisites for implementation, not reasons to weaken the design.

**Biggest unknown:** Whether the newly granted Mac Accessibility/Screen Recording and browser-bridge authorization are truly active, and what durable job/event primitives already exist; without that, Resume Packets cannot safely bind and later revalidate private context.

