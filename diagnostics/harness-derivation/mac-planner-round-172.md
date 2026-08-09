# Harness derivation — mac-planner — round 172

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-accessibility-live** — AI Pendant Agent now has Accessibility and Screen Recording trusted; synthesized events verified reaching the screen, secure input is false, and 3 browser sessions are visible. This unblocks semantic UI control/inspection proposals that were previously owner-blocked.
  - evidence: mac_readonly_inspect(operation=running_apps) resolved GET /observe at 2026-08-08T01:15:18Z: accessibility.trusted=true, screenRecording=true, eventsPost=true, inputReachability=verified.

## Capabilities it proposed

### "When my pendant is plugged into my Mac, keep the conversation and my bookmarks working even if LTE is unavailable, then reconcile anything queued when the relay comes back."
- **useful because:** The pendant is physically present today but unregistered on LTE; this would make the wearable useful in the exact state it is currently in instead of silently failing. Button bookmarks, short voice turns, and generated replies would continue over the USB-connected Mac, with no duplicate events after reconnection.
- **path:** pendant → mac-planner → relay-realtime → dashboard
- **model tier:** Realtime only for the live turn; a cheap background worker performs deduplication and replay reconciliation.
- **latency:** Under 300 ms from pendant USB frame to relay ingress for control/events; audio remains bounded by the existing 60 ms framing. Reconciliation can take seconds after reconnect.
- **cost:** Realtime token/audio cost is unchanged for an active turn; background reconciliation is <$0.01 per reconnect in typical use. Dominant cost is the missing USB serial transport and firmware framing work, not inference.
- **security:** USB frames must be authenticated and bound to the local pendant identity; never expose raw queued microphone data to arbitrary Mac apps. Persist only encrypted, content-addressed outbox records and delete them after relay acknowledgement. The owner should explicitly enable USB companion mode once.
- **missing:** A real mac_serial_exchange capability or a Mac agent route that opens /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA with framed, authenticated I/O; A relay ingress/reconciliation endpoint accepting idempotency keys for pendant events and audio chunks; A Mac background companion that reconnects the serial links and surfaces link state without stealing focus

### "Do this task on my Mac and keep going until you can prove it worked: use the right app or browser tab, make the change, verify the resulting state, and tell me exactly what changed if verification fails."
- **useful because:** Today a plan can execute actions but the owner still has to trust that the right window, tab, account, and resulting state were used. A closed loop would make the Mac node genuinely dependable: it can notice a stale tab, a failed save, a logged-out session, or a changed confirmation page instead of claiming success.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision
- **model tier:** Realtime for the owner's short command and final spoken result; a cheaper local/background model handles UI state extraction, selector matching, and deterministic postcondition checks. Escalate to realtime only when the UI is ambiguous.
- **latency:** Read/act/verify loop under 5 seconds for ordinary app or browser tasks; up to 20 seconds for a multi-page workflow. Never loop indefinitely: stop after three mismatches and report the evidence.
- **cost:** Typically <$0.01 for local semantic extraction plus one short model call; realtime cost only for ambiguity or final speech. The main engineering cost is typed postconditions and browser/app adapters.
- **security:** Verification must not send or mutate anything a plan did not name; redact passwords, tokens, and page content in receipts. The existing empty policy slot must explicitly authorize each action class, while the verifier remains read-only. If a postcondition cannot be proven, report failure rather than infer success.
- **missing:** A planner contract that carries explicit postconditions and touched-resource identities from relay to Mac; Accessibility-backed semantic UI snapshots and app-specific read adapters for the currently foreground app; Browser bridge support for stable tab/session identity plus read-only after-state inspection; A durable receipt format that stores before/after hashes and the reason for any retry

### "I'm about to share my screen — hide sensitive windows and tabs, leave only the presentation visible, and restore my workspace when I say I'm done."
- **useful because:** Screen sharing is a high-consequence everyday transition: the owner needs the pendant's immediate physical command, the Mac's window control, and the browser's authenticated-tab awareness together. It prevents accidental exposure of billing, mail, private notes, and active sessions without requiring the owner to hunt through windows under pressure, then returns the workspace rather than destroying it.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision
- **model tier:** Realtime interprets the short command; deterministic local policy and a cheap model classify windows/tabs by sensitivity and presentation relevance. No model should receive page bodies unless the owner opted in.
- **latency:** Prepare in 2 seconds, with a spoken 'ready' only after the visible state is verified. Restore in under 3 seconds. If verification is unavailable, leave the workspace unchanged and say so.
- **cost:** <$0.01 per transition after local classification; the dominant cost is engineering app/browser adapters and state snapshots, not inference.
- **security:** This must default to hiding or minimizing, never closing tabs or signing out. Save an encrypted before-state containing window IDs, tab IDs, bounds, and visibility—not page contents or cookies—and expire it after 24 hours. The owner must configure which apps/domains count as sensitive; an empty policy stops rather than guessing. Restoration must verify the same user session before re-opening anything.
- **missing:** A cross-app window-state snapshot and restore adapter using the now-live Accessibility/Screen Recording permissions; Browser tab classification and visibility control that preserves authenticated sessions; An explicit owner-configured sensitive-domain/app policy and a non-destructive presentation profile; A pendant-to-Mac low-latency command path that works while the pendant is USB-attached as well as over relay

### "Before you use my Mac or browser context, make a private local summary that keeps only what is needed for this task, show me what categories will leave the Mac, and let me say 'local only' to refuse cloud processing."
- **useful because:** The owner gets useful automation without having to choose between full access and sending raw mail, documents, URLs, or screen contents to a model. The pendant provides an immediate privacy command; the Mac performs redaction before relay upload; the relay can still reason over task-relevant structure.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** A local deterministic redactor/classifier does the first pass; use a cheaper background model for uncertain classification. Realtime sees only the resulting task-scoped projection and handles the spoken interaction.
- **latency:** Under 500 ms for common text and tab metadata; under 2 seconds for a document. 'Local only' must take effect immediately and never wait for relay acknowledgement.
- **cost:** Usually <$0.005 per invocation; local CPU and app-specific extraction dominate. Cloud token usage should decrease because raw context is not resent.
- **security:** Fail closed when classification is uncertain. Never upload passwords, cookies, auth headers, hidden form fields, or full page bodies by default. Keep an auditable local manifest of fields removed and expire it quickly. This requires an owner-defined policy because the current action policy is empty; do not invent defaults that silently permit exfiltration.
- **missing:** A local context compiler with field-level redaction and uncertainty handling; A relay protocol carrying a projection plus redaction manifest rather than raw context; A physical pendant command/state indicator for local-only mode; Owner-editable data-category policy and dashboard preview before the first use

### "Watch me do this workflow once, turn the meaningful steps into a reusable command, and next time run it against the current document or browser session instead of replaying stale clicks."
- **useful because:** The owner can teach the system a personal workflow without writing a script, then invoke it from the pendant. Semantic recording would survive window movement, changed tab IDs, and new documents, unlike a brittle macro; it would make repeated Mac work disappear rather than merely automate one request.
- **path:** pendant → mac-planner → mac-vision → browser-extension → relay-realtime
- **model tier:** A local model extracts semantic steps from Accessibility events and browser DOM/state; a cheaper validator checks whether each target still matches. Realtime is only needed to name the workflow or resolve ambiguity.
- **latency:** Recording adds no noticeable delay. Validation before replay under 2 seconds; ordinary replay under 10 seconds. Stop and report the first mismatch rather than guessing.
- **cost:** <$0.02 to create and validate a workflow, then <$0.01 per replay; local event capture and app/browser adapters dominate.
- **security:** Recording must omit keystrokes into secure fields, passwords, tokens, and arbitrary typed text unless explicitly marked as a parameter. Store semantic selectors and a redacted sample, not screenshots or secrets. An owner-configured policy must decide which apps/domains can be replayed unattended; unapproved workflows remain drafts.
- **missing:** A semantic event recorder spanning Accessibility and browser bridge events; A workflow intermediate representation with parameters, preconditions, postconditions, and versioning; A replay validator that can rebind targets to the current document/tab safely; An owner-facing workflow library and pendant command namespace

### "Watch the health of the browser sessions I rely on, and tell me on the pendant before a login expires, a required extension disconnects, or a saved session becomes unusable—without reading the site's private content."
- **useful because:** The owner currently discovers broken authenticated sessions only when a deadline task fails. A relay-side monitor can check safe session metadata and the browser bridge heartbeat, then give an actionable warning while there is still time to fix it. This is different from reading a work portal: it protects reachability, not content surveillance.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** No realtime model for polling; deterministic checks and a cheap background classifier identify session-health changes. Realtime is only used if the owner asks why a session is unhealthy.
- **latency:** Heartbeat every 1–5 minutes with no visible browser disruption; surface a warning within one interval. A repair attempt should complete within 10 seconds or produce a precise failure.
- **cost:** A few cents per month for normal polling, dominated by relay invocations; local browser work is negligible. No page-content tokens are needed.
- **security:** Inspect only tab/session identity, bridge connectivity, HTTP/auth status, and explicit expiry signals; never collect page text, cookies, or credentials. Do not auto-login or alter account settings without an owner policy. Encrypt health history and expire it quickly.
- **missing:** A browser bridge health contract exposing non-content session and authentication status; Relay scheduling and deduplicated alerting into the existing pendant inbox; A repair flow that can reopen the affected session without capturing secrets; Dashboard controls for monitored sessions, severity, quiet hours, and retention


## Changes it proposed to its own stack

### `mac-harness` — Add a read-only semantic context endpoint to the Mac agent that returns the foreground window's app/document identity, selected text, focused control label/value, and browser tab/session identity through Accessibility and the existing browser bridge, with field-level redaction and a timestamped snapshot ID. Use the now-verified AI Pendant Agent TCC grants rather than screen pixels wherever possible.
- **owner gets:** The owner can say 'use what I have selected' or 'continue in this document' and get the correct context without dictating or exposing an entire screen. It also lets the agent distinguish a stale browser tab or wrong document before acting.
- effort: Medium: AX traversal and app adapters for common apps, browser bridge correlation, redaction tests, and a new read-only route. Start with Safari, Chrome, Mail, Notes, VS Code, and Preview.  ·  risk: Accessibility element trees differ by app and may contain secrets. On timeout or ambiguous identity, return partial data with confidence and do nothing; never substitute a guessed document. Recover by falling back to the existing foreground-app observation.
- cost: Negligible API cost; local CPU and engineering effort dominate. No page body or screenshot leaves the Mac unless explicitly requested.  ·  latency: 200–800 ms for a foreground snapshot; browser correlation may add ~500 ms.
- security: Read-only but privacy-sensitive. Redact password/secure fields, URLs containing credentials, and mail bodies by default; make selected-text capture explicit in the owner policy. Log only snapshot hashes and field provenance.
- depends on: Accessibility and Screen Recording trust for AI Pendant Agent (now verified live); A concrete JSON-schema operation replacing the current ambiguous ui_snapshot/browser_tabs resolver; Existing GET /observe and browser session inventory


## What it asked for

_Nothing._
## Its own summary

Discovered live Mac state: AI Pendant Agent now has Accessibility and Screen Recording trust, synthesized input is verified reaching the screen, secure input is off, and three browser sessions are present (including an authenticated OpenAI billing tab). Recorded this as a fresh finding. Proposed four non-duplicate capabilities/changes: USB-attached pendant continuity while LTE is unregistered; closed-loop Mac/browser actions with explicit postcondition verification; a pendant-triggered screen-sharing privacy presentation profile with reversible restoration; and a read-only Accessibility/browser semantic-context endpoint for selected text, document identity, and stable tab identity. Asked faculty-perception whether that semantic path already exists.

**Biggest unknown:** The missing physical bridge remains unresolved: there is no callable mac_serial_exchange capability, so I cannot test or implement the USB serial pendant path from this harness. Also browser_tabs resolution is currently ambiguous between browser_inspect and browser_list_tabs; the existing /observe response still exposes the three tabs.

