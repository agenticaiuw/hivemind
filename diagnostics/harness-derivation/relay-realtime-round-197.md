# Harness derivation — relay-realtime — round 197

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Watch me perform this workflow once, then turn it into a voice-triggered routine I can safely rerun.”"
- **useful because:** The owner can teach the system a personal workflow by doing it once across Safari and Mac apps, instead of explaining brittle steps or rebuilding it every time. The pendant becomes the trigger; the Mac/browser preserve the real interaction sequence and the relay turns it into a reusable routine with a spoken test result.
- **path:** pendant → relay → mac-planner → browser-extension → mac-terminal
- **model tier:** Use the low-latency relay only to capture the spoken goal and confirm completion; use the cheaper Mac planner for sequence interpretation and a background model for routine normalization and parameter extraction.
- **latency:** Begin recording within 500 ms of the spoken command; capture the teaching session interactively. Normalize in under 10 seconds after the owner says “done”; a rerun should begin within 2 seconds of a later pendant command.
- **cost:** About $0.02–$0.10 per teaching session depending on screenshots and planner turns; reruns are mostly local action execution and should cost near-zero model tokens.
- **security:** The sequence may contain authenticated pages, secrets, or typed text. Keep screenshots, DOM details, and credentials on the Mac/browser; send the relay only a redacted routine schema and completion summary. The owner must explicitly say “teach” to enter capture mode, and the first rerun should be dry-run or visibly announced.
- **missing:** A first-class teach-mode recorder that correlates pendant utterance, Mac actions, browser commands, and observed results; A routine schema with variables, assertions, redaction markers, and versioned replay; A relay route that can invoke a named routine from a voice session

### "“For the next hour, treat messages from Alex as urgent, draft replies but never send them, and forget this rule afterward.”"
- **useful because:** The owner gets temporary, spoken control over how the hive behaves without changing permanent settings. The same constraint follows the task from the pendant to authenticated browser sessions and Mac apps, expires automatically, and is visible when it affects an action.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** The relay parses the short-lived policy in realtime; a cheaper background model validates scope and resolves references such as a contact or project. Downstream Mac/browser agents receive the resulting policy capsule as structured context, not repeated prose.
- **latency:** Acknowledge the policy in under 1 second and attach it to the next delegated task without an extra conversational turn.
- **cost:** Under $0.01 for policy creation and attachment; the dominant cost is whatever downstream task the policy governs.
- **security:** Policies must be scoped by subject, surfaces, action types, and expiry, with an immutable audit entry. Never silently convert “draft” into “send.” Keep contact identifiers and message contents on the Mac/browser where possible; require a fresh spoken command to extend an expired policy.
- **missing:** An expiring shared policy/context capsule store readable by relay, Mac planner, and browser harness; Policy propagation on POST /plan and POST /execute, including explicit precedence and conflict reporting; A pendant-readable confirmation and expiry notification that is distinct from ordinary job completion

### "“Answer this using my open browser session, my Mac files, and public sources—and tell me which facts disagree.”"
- **useful because:** This would make the hive a genuinely trustworthy research partner: it can combine private authenticated context that only the browser/Mac can reach with public web evidence, identify contradictions instead of blending them, and speak a short answer while leaving a traceable dossier on the Mac.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Use realtime only for clarification and the spoken synthesis. Use a cheaper background model to extract claims, normalize dates/identities, compare evidence, and produce the dossier. Browser and Mac agents remain the only components that see private content.
- **latency:** Speak an initial “I’m checking three sources” acknowledgement within 1 second; deliver a concise answer in 15–30 seconds for a normal request, with longer research continuing as a job.
- **cost:** Roughly $0.03–$0.20 per question, dominated by private-page extraction, screenshots, and claim-comparison tokens; the spoken response itself is inexpensive.
- **security:** Private page text and local files must not be sent to public search providers or mixed into model prompts unnecessarily. Every claim needs source, capture time, surface, and confidence; if sources disagree, say so. Redact secrets and allow the owner to delete the dossier.
- **missing:** A cross-surface evidence/claim graph that preserves provenance and detects contradictions; A local extraction path for authenticated browser pages and Mac files with redaction before relay synthesis; A durable dossier artifact and pendant summary protocol


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing proposals. The strongest is a private/public evidence answer: the pendant asks one question, the browser and Mac inspect sources they alone can reach, the relay synthesizes a spoken answer while preserving claim-level provenance and explicitly reporting contradictions. The other two are teach-once workflow recording and expiring spoken policy capsules. What is still needed is not another generic planner: it is the connective layer between existing routes—provenance/claim storage, teach-mode event correlation and replay schemas, and a shared expiring policy context propagated into plan/execute without leaking private page data.

**Biggest unknown:** Whether the existing session and journal routes already retain enough structured event detail to implement teach-mode correlation and claim provenance without a new durable store.

