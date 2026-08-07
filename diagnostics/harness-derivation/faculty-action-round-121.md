# Harness derivation — faculty-action — round 121

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I’m leaving.” Lock down my Mac and private browser session: save anything unsaved that can be safely saved, close or hide sensitive windows, pause notifications and media, and tell me exactly what was changed through the pendant; leave a receipt I can undo when I return."
- **useful because:** A single spoken phrase turns a wearable plus Mac plus authenticated browser into a reliable privacy boundary, rather than requiring a frantic checklist. It is useful precisely because the relay can finish after the owner walks away and the pendant can report completion.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background planner for the checklist; realtime only to recognize the phrase and report completion.
- **latency:** Acknowledge in under 1 s; execute safe reversible steps within 10 s; wait for per-step receipts before claiming lockdown.
- **cost:** ~$0.01–0.05 per invocation; dominated by planner context and browser inspection, not Mac actions.
- **security:** Private tab titles and window state leave the Mac only as structured metadata; never transmit page bodies. Closing/signing out can lose work, so save/close only allowlisted apps and require confirmation for destructive or sign-out steps. Store an encrypted, expiring undo receipt.
- **missing:** A privacy-lockdown action recipe with app-specific save/close policies; A reliable browser session hide/lock primitive and verified completion proof; Owner-configured allowlist of sensitive apps and reversible steps

### "“Hold my focus for the next hour.” Put the Mac in a quiet, visible focus mode, mute or defer nonessential notifications and browser distractions, keep an emergency path available from the pendant’s single button, then restore the exact prior state and report what was restored."
- **useful because:** The owner gets a dependable work boundary without manually changing several Mac and browser settings, and restoration avoids the common damage of forgetting what was muted or closed. The pendant remains a physical escape hatch even when the Mac is unattended.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Cheap scheduled/background model for setup and restoration; realtime only for the button interruption and spoken status.
- **latency:** Setup under 5 s, immediate button escape under 1 s, exact restoration at deadline within 10 s.
- **cost:** ~$0.005–0.02 per session; mostly deterministic Mac actions, with one planner call for state reconciliation.
- **security:** Snapshot only settings needed to restore (Focus, volume, notification mode, selected tabs); do not inspect page content. Emergency escape must be local and not depend on LTE. Restoration must be idempotent and show diffs if another app changed the state meanwhile.
- **missing:** A Mac Focus-mode adapter with before/after state snapshots; A pendant-local emergency-cancel event over the current USB serial gateway; A scheduled restore job that detects conflicting changes

### "“Mark this for later.” Press the pendant button once while I’m at the Mac to capture the frontmost app, selected text or clipboard, active Safari tab, and timestamp into a private action packet; later I can say “continue the thing I marked” and the system reconstructs the context without me explaining it again."
- **useful because:** This makes the worn button a physical memory affordance for moments when the owner cannot stop to dictate. The Mac supplies rich context, the browser supplies the authenticated tab identity, and the relay preserves it until the owner is ready to act.
- **path:** pendant → mac-bridge → browser → relay → dashboard
- **model tier:** No expensive model at capture; background model summarizes and deduplicates packets; realtime model only resolves the later spoken reference.
- **latency:** Capture acknowledgement under 500 ms over USB; packet visible in the dashboard within 3 s; later reconstruction under 2 s.
- **cost:** <$0.005 per packet; dominated by optional summarization, with metadata-only capture nearly free.
- **security:** Clipboard and tab metadata may contain secrets. Require an explicit capture mode, redact password-manager/payment fields, encrypt packets, and auto-expire them. Never capture microphone audio. Show a clear LED confirmation and provide one-button cancellation before persistence.
- **missing:** A button gesture distinct from conversation start/end; Mac adapter for frontmost app, selection, clipboard, and Safari tab metadata; Private expiring action-packet storage and a reference resolver

### "“I need help.” Or press the pendant’s emergency gesture. Alert my configured contact with my last known location/status and a short, owner-approved message, keep retrying over the Mac/relay path until delivery is verified, and cancel only when I explicitly cancel from the pendant or dashboard."
- **useful because:** This is the one capability that can matter more than convenience: a worn button can summon help when the owner cannot open a phone or explain the situation. The tethered Mac is usable today, while the relay can retry when the Mac disappears.
- **path:** pendant → mac-bridge → relay → dashboard → iOS
- **model tier:** Deterministic templates and background delivery; realtime model only interprets an ambiguous spoken request. Never use a generative model to invent emergency details.
- **latency:** Local LED acknowledgement under 300 ms; first send within 3 s; delivery/retry status within 10 s.
- **cost:** <$0.01 per event plus carrier/SMS or messaging fees; retries dominate operational cost.
- **security:** Require a physical gesture or explicit phrase plus a configured contact/message template. Do not expose location by default; use last-known data with timestamp and make the payload visible in the dashboard. Cancellation and escalation must be authenticated and idempotent; log every delivery attempt.
- **missing:** Pendant-local emergency gesture and offline event spool; A relay delivery adapter (SMS/iMessage/push) with delivery receipts and bounded retries; Owner-configured emergency contact, message, and location-consent policy

### "“Run presentation mode.” While I present, let the pendant’s button advance or go back through Keynote/PowerPoint/browser slides, let me ask the mind to jump to a named slide or display speaker notes on the Mac, and give a clear LED/audio acknowledgement for every transition."
- **useful because:** The owner gets a discreet, wearable presentation remote that can also recover from a wrong slide without touching the laptop. It combines a physical control, Mac application state, browser content, and optional audio feedback in a way no single node can provide.
- **path:** pendant → mac-bridge → browser → relay
- **model tier:** Deterministic button commands for next/previous; a cheaper planner for slide-name lookup; realtime only for ambiguous spoken corrections.
- **latency:** Button-to-slide transition under 250 ms; spoken slide lookup under 2 s.
- **cost:** <$0.01 per session; mostly local AppleScript/browser actions.
- **security:** Bind control to the explicitly selected presentation window and session; do not capture microphone audio or slide contents unless requested. Require a clear start/stop gesture and show the active presentation target.
- **missing:** Presentation-session binding for Keynote, PowerPoint, and browser slides; A pendant button gesture/state distinct from conversation control; Low-latency Mac event channel with ordered acknowledgements and recovery when the presentation app changes

### "“Fill this out without exposing my private data.” Have the Mac and authenticated browser inspect the form, fetch only the minimum matching values from local sources, fill reversible fields locally, and show me a field-by-field provenance and redaction report before anything leaves the Mac or is submitted."
- **useful because:** The owner can use logged-in services without handing the relay a copy of their identity, financial, or health data. The browser can reach the private form while the Mac remains the privacy boundary and the pendant can announce that review is waiting.
- **path:** pendant → mac-bridge → browser → relay → dashboard
- **model tier:** Background extraction/classification model on the Mac; realtime only for owner questions about a field.
- **latency:** Form inspection under 5 s; review report under 10 s; zero network transmission of protected values.
- **cost:** ~$0.01–0.05 per form; dominated by local structured extraction and optional semantic matching.
- **security:** Treat all field values as sensitive by default. Keep raw values on the Mac, send only field labels, redacted previews, and hashes to the relay/dashboard, and require explicit approval for each sensitive field or a narrowly scoped batch.
- **missing:** A local-only form-field matching and redaction engine; Browser bridge support for field metadata and before/after values without exporting values; A dashboard review that proves where each value came from and what will be submitted

### "“Protect me if the pendant disappears.” If the worn device is unexpectedly disconnected or its heartbeat stops, lock the Mac, pause private browser work, revoke only the sessions I have configured as high-risk, and notify me through another channel; distinguish a planned USB unplug from a loss and let me recover safely when the pendant returns."
- **useful because:** A wearable that carries access to private accounts should provide a real loss response, not merely report that it went offline. This turns physical presence into a practical privacy boundary across the pendant, Mac, browser, and relay.
- **path:** pendant → mac-bridge → browser → relay → dashboard → iOS
- **model tier:** Fully deterministic heartbeat and policy engine; no expensive model required.
- **latency:** Detect unexpected loss within 5 s; lock/pause within 2 s after detection; recovery status when the pendant reconnects.
- **cost:** Negligible per event; persistent heartbeat telemetry and occasional notification fees dominate.
- **security:** False positives could interrupt work or revoke sessions, so support a grace period, charging/USB-maintenance mode, and an authenticated recovery gesture. Never use absence alone to delete data. Keep location and device identifiers out of notifications unless explicitly configured.
- **missing:** Signed pendant heartbeat and planned-disconnect protocol; Mac lock and browser-session containment primitives with verified completion; A loss/recovery policy editor and alternate notification channel


## Changes it proposed to its own stack

### `integration` — Add an action saga coordinator that joins relay jobs, Mac action receipts, browser request IDs, and pendant serial event sequence numbers into one transaction graph. Each step publishes prepared/committed/failed/compensated state; the coordinator can pause at a missing proof, retry only idempotent steps, and expose one owner-readable timeline rather than claiming success from a 200 response.
- **owner gets:** When the system acts across a private browser and Mac, the owner will know whether the real-world outcome happened, what partially happened, and how to recover. This prevents silent half-completed tasks—the most dangerous failure mode of an agent that makes things happen.
- effort: Medium-high: shared schema, coordinator worker, Mac/browser adapters, and dashboard timeline.  ·  risk: A bad compensation could undo an owner change; default to no automatic compensation for irreversible steps, retain current receipts, and offer explicit per-step retry/undo.
- cost: Low storage/compute overhead; one small D1 record per step and occasional background reconciliation.  ·  latency: Adds tens to hundreds of milliseconds for receipt commits; no extra model call.
- security: More detailed action metadata is retained; redact page content and clipboard values, encrypt sensitive receipts, and enforce per-job access controls.
- depends on: Signed USB gateway from mac-planner; Existing actionReceipt and browser request-id work; A durable job runner (chg-16bc5dee remains open)

### `mac-harness` — Add a local privacy kernel between the Mac agent and browser bridge: classify every outgoing field, clipboard value, screenshot region, and page extraction as public, personal, or secret; enforce a deny-by-default export policy; perform matching, redaction, and hashing locally; and return verifiable proofs that the relay saw only the permitted projection.
- **owner gets:** The owner can ask the system to act on private websites and documents without trusting that the cloud model received their passwords, identity numbers, or financial details. Privacy becomes an enforced behavior rather than a promise in a prompt.
- effort: High: local classifier, browser protocol changes, policy UI, test corpus, and fail-closed integration across every Mac/browser route.  ·  risk: Over-redaction can make tasks fail; recover by showing the blocked field category and allowing a narrowly scoped, time-limited local approval. Misclassification must never export a secret by default.
- cost: Moderate local CPU/RAM; small relay storage for policy decisions and hashes, with no raw sensitive payloads.  ·  latency: Adds roughly 100–500 ms for structured fields and more for screenshots; no added latency when an action contains only allowlisted metadata.
- security: Substantially reduces cloud data exposure, but the local classifier and policy store become high-value components; sign policies, audit changes, and protect them with the Mac keychain.
- depends on: Browser bridge field-level metadata protocol; Local action receipts and typed results; Dashboard support for redaction/provenance review


## What it asked for

_Nothing._
