# Harness derivation — faculty-action — round 175

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I’m walking into my next meeting—prepare me.”"
- **useful because:** The worn interface turns calendar context into a ready-to-use workspace: it finds the next event, gathers the linked notes/files and relevant browser pages on the Mac, creates a private meeting scratchpad, and reads a 20-second spoken brief back to the owner. It is genuinely cross-surface: the pendant supplies urgency and confirmation, relay coordinates, Mac and browser hold the authenticated data, and perception confirms the workspace actually opened.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-perception
- **model tier:** background for calendar/document retrieval and summarization; realtime only for the brief and follow-up conversation
- **latency:** Under 10 seconds to announce the meeting and start preparation; under 30 seconds for the complete packet. Never block the owner on a slow browser tab.
- **cost:** Roughly $0.01–$0.05 per preparation, dominated by summarization and browser/page extraction; calendar and local Mac operations are negligible.
- **security:** Meeting titles, notes, and browser content remain on the authenticated Mac/browser surfaces where possible; the relay receives only the minimum structured event and brief. External sending or editing source documents must be staged and require the existing physical transaction approval latch. If links or permissions fail, report partial preparation rather than claiming success.
- **missing:** A meeting-prep orchestrator that resolves the next event and its links; A private scratchpad creation action with an idempotency key; A compact spoken-brief response path from relay to the pendant; A verifier recipe for calendar selection, opened resources, and scratchpad file state

### "“Privacy shield.” (a deliberate pendant gesture)"
- **useful because:** One physical gesture immediately moves the owner's Mac into a known private state while they are away from the keyboard: pause browser polling, hide or lock sensitive windows, mute notification previews, and mark the session as privacy-armed. A second deliberate gesture restores the prior state. This is useful in a café, office, or when handing the laptop to someone, and unlike a software hotkey it remains available when the screen is obstructed or the owner is carrying the machine.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-perception
- **model tier:** No large model for the hot path; deterministic policy and local Mac actions. Use the realtime model only to explain status if the owner asks by voice.
- **latency:** Visible privacy state within 2 seconds of the confirmed gesture; restoration within 3 seconds. If any surface cannot be secured, the pendant must say which one remains exposed.
- **cost:** Near-zero API cost; primarily local action execution and one small relay event per arm/disarm.
- **security:** The pendant receives only an opaque state/nonce, never window titles, page contents, or secrets. The Mac agent must use an allowlisted privacy profile, record exactly what changed, and verify each postcondition independently. Do not close tabs or discard unsaved work; lock/hide/mute only, with a bounded undo record. Arming should be allowed proactively only if the owner chooses that policy; default to confirmation for disarm.
- **missing:** A first-class privacy profile with reversible, allowlisted actions across macOS and the browser bridge; A pendant gesture/event route that works while LTE is absent but the pendant is USB-attached; A fail-closed aggregate status beacon when one surface cannot be secured; An independent verifier mapping for hidden/locked windows, browser pause, and notification state

### "“I’m leaving now—save my place.”"
- **useful because:** A deliberate pendant gesture creates a durable, private continuity card for the owner's current work: active project, unsaved-document warnings, relevant files, browser session URLs/titles, and the last action state. It then lets the owner resume from the pendant or Mac later instead of reconstructing context. The Mac/browser do the observation and persistence; the relay stores the signed handoff; the pendant gives an immediate receipt even when disconnected.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-perception
- **model tier:** Deterministic capture first; a cheap background model may summarize the card. Realtime is only for a spoken confirmation or resume query.
- **latency:** Acknowledge the gesture in under 1 second, capture local state in under 5 seconds, and sync opportunistically. Never wait for cloud connectivity before writing the local handoff.
- **cost:** Near-zero for capture; about $0.005–$0.02 when a model summarizes a large work context. Storage is small JSON plus hashes, not document copies.
- **security:** Do not upload document bodies or page secrets by default; retain titles/paths/URLs only when their sensitivity policy allows. Redact password-manager and private browsing surfaces. The card must be encrypted at rest, expire by policy, and show provenance for every item. Resume must reopen or edit only after explicit owner intent, with verification that the target file/page still matches its recorded hash.
- **missing:** A cross-surface continuity-card schema and encrypted relay store; A Mac/browser snapshot operation that returns a structured, sensitivity-labelled state rather than screenshots; A pendant offline acknowledgement and later delivery tied to the existing typed OUTBOX; A resume planner that treats stale hashes as warnings instead of silently acting

### "“Before you send anything outside my Mac, show me exactly what will leave and stop if it contains a secret.”"
- **useful because:** The owner gets a trustworthy outbound-data firewall rather than hoping an action planner noticed a credential, private URL, or personal identifier. It intercepts browser submissions, email/message sends, uploads, and clipboard-to-web actions; computes a field-level redaction/diff preview; speaks a short summary through the pendant; and requires the existing physical approval latch only for the risky fields. Safe local actions continue without friction.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Deterministic local classifiers and policy engine on the Mac for the hot path; a cheaper background model may explain ambiguous fields. No realtime model is needed unless the owner asks for a spoken explanation.
- **latency:** Intercept and classify in under 300 ms for ordinary forms; preview in under 2 seconds. Fail closed on classifier uncertainty for external transmission, but never destroy the draft.
- **cost:** <$0.01 per intercepted action when local classifiers resolve it; occasional model explanation costs roughly $0.01–$0.03.
- **security:** Raw secrets must remain on the Mac/browser; the relay and pendant receive hashes, sensitivity labels, and a human-readable summary only. The firewall itself must be unbypassable by a planner, log an immutable decision receipt, and distinguish a user-approved exception from an automatic pass. It must never claim a message was sent until the independent verifier checks the postcondition.
- **missing:** A Mac/browser interception hook for all external writes, not just planner-generated actions; A field-level outbound payload inspector with secret/PII policy labels; A safe redaction preview protocol that can be rendered as short pendant audio; A verifier postcondition for the exact approved payload digest

### "“Only interrupt me for something I must answer today; hold everything else.”"
- **useful because:** The owner gets a true cross-device interruption filter: Mac and browser notifications are classified against calendar, deadlines, sender identity, and the owner's current focus; urgent items are summarized privately on the pendant, while everything else is held in a digest with a promised delivery time. A button can promote the currently held item without opening the laptop. This is more useful than blanket Do Not Disturb because it preserves the few interruptions that actually matter.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Cheap background classification with deterministic deadline/sender rules; realtime only for an urgent spoken summary or the owner’s reclassification command.
- **latency:** Classify new notifications within 1 second; urgent pendant alert within 3 seconds. Digest generation can be deferred to the next quiet boundary.
- **cost:** Approximately $0.001–$0.01 per notification batch, dominated by classification; local rules handle most events without API calls.
- **security:** Notification bodies stay on the Mac/browser whenever possible; the relay gets only urgency, source, deadline, and a short encrypted summary. Private banking, health, and authentication notifications must never be spoken or relayed without explicit policy. Every suppression needs an expiry and an accessible audit trail so nothing silently disappears.
- **missing:** A unified notification/event feed across macOS and authenticated browser sessions; Owner-editable urgency and sensitivity policies with per-sender and per-calendar exceptions; A durable held-item queue with expiry, deduplication, and pendant promotion gestures; Independent verification that an urgent item was delivered and a suppressed item remains retrievable

### "“Give my accountant access to these three documents until Friday, and take it back automatically.”"
- **useful because:** The owner can make a bounded external commitment without manually hunting through sharing dialogs: the Mac identifies exactly the named files, the browser handles the authenticated sharing service, the relay tracks expiry, and the pendant confirms the final recipient/scope/duration. At expiry it revokes access and independently verifies revocation, turning risky ad-hoc sharing into a reversible delegation.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Background model for resolving “these documents” and recipient identity; deterministic policy for scope, expiry, and revocation. Realtime only for the concise approval prompt.
- **latency:** Prepare a scope preview within 10 seconds; execute after physical confirmation within 5 seconds; revoke at the deadline with retry and a truthful unknown state if the provider is unavailable.
- **cost:** Roughly $0.01–$0.05 per delegation, mostly document/recipient resolution; scheduled revocation and verification are low-cost.
- **security:** Never send document contents to the relay. The approval envelope contains only recipient identity, file IDs/hashes, permission level, and expiry. Default to least privilege and no resharing. If revocation cannot be verified, alert the owner and keep retrying; never report success from an API acknowledgement alone. Provider-specific permanent links and inherited folder permissions require explicit refusal or a stronger confirmation.
- **missing:** Provider-neutral share/revoke adapters for browser-authenticated services; A scope resolver that proves file identity before any share action; A scheduled revocation worker with retry and independent postcondition verification; An approval summary that is short enough for the pendant but includes recipient, files, permission, and expiry


## What it asked for

_Nothing._
## Its own summary

Recorded three new, non-duplicate cross-surface capabilities: “prepare me for my next meeting,” a physical privacy shield, and “save my place” continuity handoff. The strongest immediate candidate is Privacy Shield: a pendant-confirmed, fail-closed, reversible Mac/browser privacy state with independent verification and no secrets sent to the pendant. I still need (1) the owner’s policy for which privacy actions may arm/disarm without a second approval, (2) the actual pendant revision/button/connection status so the gesture and offline acknowledgement can be implemented honestly, and (3) a live inventory from faculty-perception of which privacy and work-state postconditions it can verify. Accessibility/Screen Recording remain owner-side blockers; I did not re-request them.

**Biggest unknown:** Whether the current physical pendant is actually reachable over the stated USB serial paths in this run, and which exact macOS/browser privacy transitions are available without Accessibility.

