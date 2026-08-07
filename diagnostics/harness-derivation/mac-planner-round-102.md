# Harness derivation — mac-planner — round 102

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Keep an eye on my important things, but only interrupt me when it’s genuinely urgent and I’m at a safe stopping point.”"
- **useful because:** This would combine the pendant’s always-available intent and haptic channel, the relay’s persistent scheduling, the Mac’s current foreground app and calendar context, and authenticated browser sessions into one interruption policy. Instead of either spamming notifications or missing changes, it queues evidence-backed items and delivers a one-sentence alert only when urgency and interruptibility both pass; otherwise it leaves a cited review queue for later.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background/scheduled triage uses a cheaper slow model; realtime is used only for the owner’s button-press follow-up or spoken delivery.
- **latency:** Source polling can be minutes to hours depending on watch cadence. A button press should acknowledge state in under 1 second; a delivered summary should begin within 2 seconds once a safe window is detected.
- **cost:** Low-to-moderate: mostly scheduled extraction and small ranking calls; roughly $0.01–$0.05 per daily source sweep, with realtime cost only for an actual spoken interaction. Storage/egress is dominated by retained browser snippets and generated audio.
- **security:** Only named authenticated browser sessions and redacted Calendar/Mail snippets enter triage. Never include secrets or full mail bodies by default. A page change can be adversarial or misleading, so alerts must include source URL/time and confidence, and actions remain draft-only. The owner’s physical quiet/urgent control should override model judgment locally.
- **missing:** A shared attention-envelope schema (urgency, interruptibility, quiet hours, source provenance, expiry, delivery channel) understood by relay, Mac, browser, and pendant; A durable scheduler/queue that deduplicates page changes and survives browser or Mac offline periods; A Mac read-only context implementation for foreground app, running apps, and calendar/mail; the granted tools are currently schemas without implementations; Browser watch execution with TTL and stale-session parking/revalidation; Safari is currently offline and has stale queued commands; Pendant firmware support for a persistent quiet/urgent mode and a small haptic/audio delivery queue

### "“If my Mac loses Wi‑Fi, keep only my essential work connected through the pendant until normal internet returns.”"
- **useful because:** Today the pendant can speak over LTE-M, but it cannot serve as a controlled backup link for the Mac. A cellular failover mode would preserve calendar/mail sync, relay control, and a narrow set of approved browser or collaboration endpoints during a router outage or travel—without pretending LTE-M is a fast general-purpose hotspot.
- **path:** pendant → mac-bridge → relay → browser → dashboard
- **model tier:** No expensive model is needed for failover. Firmware and Mac networking handle routing; a cheap background policy service maintains the allowlist and reports health. Realtime is used only if the owner asks what is happening.
- **latency:** Failover detection and route activation within 5–15 seconds; status should be visible locally within 1 second. Throughput is deliberately best-effort and bounded by LTE-M, with large downloads blocked or deferred.
- **cost:** Low model cost (health checks and policy are deterministic). Cellular data and hardware certification dominate; expect a small monthly data charge and roughly $5–$15 incremental modem/power-management hardware if the product board needs a proper USB/network interface.
- **security:** The Mac must not expose the pendant’s cellular link as unrestricted routing. Use an owner-visible allowlist, device-bound keys, DNS/IP filtering, per-app quotas, and an emergency disable gesture. Relay sees connection metadata and approved traffic, not decrypted HTTPS contents. Never silently upload private browser data merely because failover is active.
- **missing:** Pendant firmware USB networking or a secure tether protocol; the current prototype exposes no implemented network-interface mode; A Mac network-extension/helper that detects Wi‑Fi loss, installs a metered route, and removes it cleanly on recovery; Relay-side authenticated tunnel termination and traffic accounting; A policy UI for essential apps/domains, quotas, and an explicit failover indicator; A browser harness mode that pauses nonessential polling and stale commands while the link is metered


## Changes it proposed to its own stack

### `integration` — Add a durable Attention Envelope contract and queue between browser watches, Calendar/Mail briefs, relay scheduling, Mac context, and pendant delivery. Each item carries source/session provenance, normalized urgency, interruptibility requirements, quiet-window expiry, dedupe key, redaction class, and delivery state (parked, eligible, delivered, acknowledged). Re-evaluate eligibility when Mac foreground/calendar state changes; park items when browser heartbeat or Mac is offline; never replay a stale browser command without session affinity revalidation.
- **owner gets:** The owner gets fewer disruptive alerts and fewer missed urgent changes. A queued item can survive leaving the Mac or losing Safari, then arrive as one concise, sourced sentence at a sensible moment instead of repeated stale notifications.
- effort: Medium-high: shared schema and D1/R2 persistence, triage worker, Mac context adapter, browser heartbeat integration, and pendant delivery acknowledgement; add replay/dedupe tests for offline and reconnect cases.  ·  risk: A bad urgency classifier could suppress something important or interrupt at a bad time. Recover with explicit urgent override, visible review queue, expiry notices, and a manual pendant button to flush parked items. Browser session loss must fail closed to parked, not retry blindly.
- cost: Small persistent metadata cost; background model calls only when a new/changed item needs ranking. Audio generation and browser extraction dominate variable cost.  ·  latency: Eligibility decisions become near-real-time after heartbeat/context events, typically sub-second locally and a few seconds through relay; scheduled source checks remain cadence-bound.
- security: Improves privacy by storing redacted summaries and provenance instead of raw page/mail bodies, with per-item sensitivity and expiry. Do not mix unrelated authenticated sessions in one envelope.
- depends on: Implement the currently schema-only mac_readonly_inspect and mac_read_sources grants; Browser stale-queue TTL/session revalidation (browser-extension’s pending proposal); A pendant-local quiet/urgent state and acknowledgement event; Durable relay scheduler/queue rather than transient polling

### `hardware` — Revise the wearable prototype with a low-power haptic actuator and a fuel-gauge/charger monitor on I2C, while retaining the single button and LED as fallback. Expose battery percentage/health and a distinct short/long haptic vocabulary for parked-item, urgent-item, and acknowledgement events.
- **owner gets:** The pendant could notify discreetly without opening a microphone or interrupting audio, and the system could avoid starting a delivery that will die during an LTE-M burst. The owner would get dependable quiet alerts and an honest battery warning instead of guessing from the LED.
- effort: Prototype-level board spin and enclosure iteration; add I2C drivers, power budgeting, haptic patterns, and relay capability fields. Validate coexistence with the single full-duplex I2S peripheral and LTE-M transmit peaks.  ·  risk: Haptic draw may shorten runtime and vibration may be missed or annoying. Keep patterns brief, add a firmware disable/quiet mode, and retain LED/button fallback. Fuel-gauge readings can drift; calibrate and report confidence rather than false precision.
- cost: Roughly $2–$8 BOM increase for a coin vibration motor/LRA, driver, and gauge IC plus PCB/enclosure work; tens of milliamps only during short haptic pulses, negligible average draw if rate-limited.  ·  latency: Local haptic acknowledgement can be under 100 ms; battery telemetry adds no conversational latency.
- security: Battery and haptic state are non-sensitive. Do not transmit microphone or user content for these events.
- depends on: Attention Envelope integration and pendant-local quiet/urgent state; A firmware delivery queue that can operate through dropped LTE/WebSocket links

### `integration` — Create a cellular-failover coordinator spanning the pendant modem, relay, and Mac network stack: authenticated USB/tether handshake, health-based Wi‑Fi loss detection, an explicit metered allowlist, browser polling suspension, relay tunnel quotas, and automatic teardown/recovery receipts. Treat the pendant as an emergency narrowband link, not a hotspot.
- **owner gets:** A Wi‑Fi outage would no longer strand essential work or force the owner to hunt for a hotspot, while nonessential browser traffic is prevented from consuming the pendant’s limited radio budget.
- effort: High: firmware networking and power work, a signed Mac Network Extension/helper, relay tunnel and quota enforcement, and an end-to-end recovery test across sleep, reconnect, and modem loss.  ·  risk: A routing bug could leak traffic, drain the battery, or create an unexpectedly expensive cellular bill. Fail closed when authentication or policy is unavailable, show a prominent metered-mode indicator, cap bytes/time, and record a receipt for every activation and teardown.
- cost: No per-request model spend; ongoing cost is cellular data and modest relay egress. Firmware may need a better USB/network-capable board and additional power-management components.  ·  latency: Adds a few seconds only during failover; once active, LTE-M latency and throughput are materially worse than Wi‑Fi, so the coordinator must defer large transfers.
- security: Adds a new network boundary and therefore requires device-bound keys, signed policy, encrypted tunnel, least-privilege routing, and no unrestricted LAN access. The owner must be able to disable it physically.
- depends on: USB/network-capable pendant hardware or firmware transport; Mac Network Extension/helper implementation; Relay tunnel and quota service; Browser metered-mode cooperation


## What it asked for

_Nothing._
## Its own summary

Round 102 produced a new cross-node capability: an attention-aware interruption system. It combines authenticated browser changes, Calendar/Mail briefs, Mac foreground/calendar context, relay persistence, and pendant delivery so urgent items interrupt only at safe stopping points; stale/offline work is parked and deduplicated. I also proposed the missing Attention Envelope integration contract and a hardware revision adding haptics plus a fuel gauge for discreet, battery-aware local delivery. I messaged relay-realtime about the design.

**Biggest unknown:** The newly granted mac_readonly_inspect and mac_read_sources tools are schemas only and returned no implementation, so I could not verify live foreground apps, browser tabs, Calendar, or Mail. Safari is reported offline with seven pending commands and stale sessions. I still need working read-only Mac adapters, browser TTL/session revalidation, and pendant firmware support for local quiet/urgent state and acknowledgement; Accessibility remains owner-blocked.

