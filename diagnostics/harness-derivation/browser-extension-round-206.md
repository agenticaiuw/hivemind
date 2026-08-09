# Harness derivation — browser-extension — round 206

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“From the Discord tab, tell me which conversations need my attention, quote only the relevant snippets, and draft—not send—the shortest replies.”"
- **useful because:** This turns the authenticated browser session into an actionable wearable inbox: the owner gets triage across a session no other node can reach, while preserving the explicit stop before sending. It works across browser, relay, Mac, and pendant rather than being a generic Discord client.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a cheap background extraction/classification model for page text and urgency; use realtime only to answer the spoken follow-up and read the final digest.
- **latency:** 8–15 seconds for one active Discord tab; under 2 seconds to speak the resulting three-item digest once extracted.
- **cost:** About $0.01–$0.04 per triage run, dominated by authenticated page extraction and model context; no cost for merely listing tabs.
- **security:** Page snippets and proposed replies leave the browser only to the local Mac/relay model. Persist only short-lived host-keyed findings and provenance, never raw page text. Never click Send; show each draft and its target for explicit owner action.
- **missing:** A browser action that can identify message/thread boundaries and unread/mention metadata robustly across Discord DOM variants; A structured draft artifact routed to the pendant without treating it as a sent message; An owner-supplied per-origin rule for Discord read/extract/speak/retain policy (ship empty)

### "“Before I send this form or message, read back the exact recipient, amount, and text from the authenticated browser page, and let me approve or revise it from the pendant.”"
- **useful because:** The browser is where the real recipient, hidden fields, totals, and logged-in identity are visible; the pendant is where a final spoken check is practical. This catches wrong-account and wrong-amount errors without making the owner hunt through Safari, and it stops at the irreversible boundary.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** A local/cheap structured extractor reads visible form labels and values; realtime handles the short read-back and voice edits. Use the expensive tier only when fields are ambiguous.
- **latency:** 3–6 seconds after the owner asks for a check; revised field values should be reflected within 3 seconds.
- **cost:** Roughly $0.005–$0.02 per check; the dominant cost is model disambiguation of unusual forms, not browser actions.
- **security:** Never transmit passwords, payment CVV, or hidden tokens; redact them before extraction. Show origin, account identity when available, recipients, monetary values, and exact message body. Approval must be bound to a hash of the displayed payload and expire if the page changes. The browser may submit only after a fresh spoken approval; retain a receipt, not page contents.
- **missing:** A browser_snapshot/form-inspection action that returns labeled visible fields and a page version hash; A relay-to-browser approval token bound to that hash, with automatic invalidation on DOM or origin change; Pendant UI for concise approve/revise/cancel choices

### "“Watch the authenticated pages I explicitly configure—starting empty—and alert my pendant only when a meaningful change appears, with a one-sentence explanation and a link; never save the page.”"
- **useful because:** This is the browser-only counterpart to the failed generic work-portal brief: it can see sessions behind Safari logins, detect a changed deadline, bill, appointment, or account notice while the Mac is unattended, and deliver only the delta through the worn device. The owner supplies origins later instead of the system inventing them.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Cheap scheduled fetch/diff and DOM extraction; a small classifier ranks meaningful versus cosmetic changes. Realtime is used only when the owner asks the pendant for detail.
- **latency:** Poll on a configurable 15-minute to 6-hour cadence; alert generation under 10 seconds after a detected change.
- **cost:** $0.01–$0.05 per changed page, usually near zero when unchanged if local hashing runs first; browser/relay uptime is the dominant operational cost.
- **security:** Ship an empty per-origin configuration. For each origin, owner chooses read/extract/redact/never-store and speak permissions. Store only a <=200-character claim, host, URL, evidence capsule, and 24-hour TTL; never HTML, screenshots, credentials, or page text. Require a visible pause/delete control and suppress alerts for disallowed categories.
- **missing:** A durable browser page-watch scheduler that reuses authenticated sessions and emits DOM/content hashes; Meaningful-change extraction that compares structured regions rather than whole-page noise; A configurable empty-origin policy editor and a pendant alert payload carrying source plus expiry

### "“Keep track of this multi-step web process across my authenticated tabs—where I stopped, what is still missing, and what I need to do next—and remind me on the pendant when the next step becomes possible.”"
- **useful because:** Web applications routinely split one real-world task across several pages, tabs, and delayed states: an application, enrollment, return, claim, or appointment. Today the owner must remember the checkpoint and repeatedly reopen the site. A cross-tab process memory would turn the browser session into an ongoing assistant while exposing only the next action over the wearable.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a background model to infer a compact typed state machine from page labels and visible statuses; use realtime only for the owner's spoken question or reminder. Escalate to the expensive model only when page states conflict.
- **latency:** Initial checkpoint capture in 10 seconds; subsequent tab transitions recognized within one poll cycle; pendant reminder delivery within 15 seconds of a qualifying state change.
- **cost:** Approximately $0.02–$0.08 per meaningful transition, dominated by state inference; unchanged polls should use local hashes and cost nearly nothing.
- **security:** Persist only a typed process record (origin, step name, status, missing item, next action, expiry, and provenance), never page bodies or uploaded documents. Each process must have an explicit owner label and expiration. Never infer that an application was submitted or a payment completed from a merely displayed form; report uncertainty and link the source tab.
- **missing:** A process-state store and transition engine that can correlate multiple authenticated tabs without retaining page text; Browser instrumentation for stable page/region identifiers and navigation events across tabs and Safari restarts; A pendant reminder payload that carries process ID, next step, source origin, and expiry; A user command to pause, inspect, amend, or delete one process record

### "“Before I act, tell me whether the tabs involved are signed into the same account and organization, and warn me if any tab is using a different identity.”"
- **useful because:** Wrong-account errors are invisible in many web workflows: one tab may be personal, another work, and a third may be an old shared session. The browser can see the authenticated identity indicators that the pendant and relay cannot, while the pendant can warn before the owner posts, edits, or submits.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a low-cost local extractor for visible identity/org indicators and a deterministic comparison engine; use realtime only to phrase a short warning or answer a follow-up.
- **latency:** Under 3 seconds for a check across up to 10 tabs; warning must precede any queued mutation.
- **cost:** Less than $0.01 per check; most work is browser extraction and deterministic comparison.
- **security:** Do not speak full email addresses, account IDs, or organization names by default; speak a redacted label and offer detail on request. Never infer identity from URL alone. Identity evidence is ephemeral and must not be persisted as page content. A mismatch warning is advisory and must not silently block owner-authorized actions.
- **missing:** Stable extraction of account and organization indicators from each tab, including an explicit confidence score; A cross-tab identity comparison record tied to the exact tabs and navigation versions; A pre-action hook that delivers the warning to the pendant before browser mutations

### "“Turn this authenticated web app into a voice-navigable outline: tell me the sections, let me jump to one, and read only the controls or errors in that section.”"
- **useful because:** Dense authenticated dashboards are often unusable from a small screen or while away from the Mac. This would make the browser a structured voice surface rather than a page-summary dump: the owner can inspect the relevant region from the pendant and then decide what to do.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** A cheap DOM accessibility-tree parser builds the outline; realtime performs low-latency section navigation and concise reading. No large model is needed unless labels are ambiguous.
- **latency:** Outline in under 5 seconds; moving to and reading a section in under 2 seconds per request.
- **cost:** About $0.002–$0.01 per section request; extraction and audio generation dominate.
- **security:** Return visible text and control labels only, excluding password fields, hidden inputs, and sensitive values by default. Keep the outline in memory for the session and expire it on navigation or timeout. Voice navigation may select a target but must not activate irreversible controls without a separate explicit command.
- **missing:** An accessibility-tree/semantic-region browser action with stable section IDs; A session-scoped voice cursor that survives several pendant turns and invalidates on navigation; A browser action that focuses or scrolls to a semantic region without clicking it


## What it asked for

_Nothing._
