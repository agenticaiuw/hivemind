# Harness derivation — faculty-action — round 181

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/browser execution surface** — GET /ops/snapshot reports Mac agent 0.5.0 online, fullControlMode and planner enabled, browser extension online on Safari with 9 tabs and x.com active; computer-use loop is enabled but visionUploadConsented=false. Device inventory still lists only home-macbook-bridge and an offline mobile device, not a registered pendant.
  - evidence: GET /ops/snapshot live 200; discover(devices) live result in round 181

## Capabilities it proposed

### "When I say “do this only while I’m here,” use the pendant as a hardware presence key: challenge it over the USB/relay link, require a fresh deliberate gesture, then perform the approved Mac/browser action and tell me whether the postcondition was verified before the lease expires."
- **useful because:** High-impact actions become safe to delegate without exposing passwords or relying on a cloud-only yes. It works now with the pendant physically attached to the Mac even before LTE registration, and can later use the relay when untethered.
- **path:** pendant → mac-planner → browser-extension → mac-vision → relay-realtime → faculty-judgement → faculty-perception → faculty-action
- **model tier:** Realtime only for the spoken request and concise confirmation; deterministic firmware/relay challenge handling and a cheaper background verifier for postconditions.
- **latency:** 2–4 seconds for challenge, gesture, execution start; verification may take up to 10 seconds.
- **cost:** Usually one realtime turn plus cheap verification; roughly $0.01–$0.08 depending on whether vision is needed. USB serial is negligible.
- **security:** The pendant must receive only an opaque challenge and risk summary, never page contents or secrets. Use a monotonic counter, expiry, replay protection, and fail closed on disconnect. Require confirmation for irreversible actions. USB serial currently exists, but the nRF9160 is not LTE-registered, so untethered operation needs relay registration and authenticated device keys.
- **missing:** A real resolvable verifier route/tool (the granted verify_operation_step schema is unresolved); Firmware challenge-response and serial transport integration; A policy table specifying which action classes require a fresh gesture; Device key provisioning and relay registration for untethered use

### "Before you send, publish, or edit anything, ask “may I use the private context currently open in my browser?” and let me choose: public-only, selected tabs, or this exact tab. Then execute with a machine-enforced context allowlist and say what context was actually used."
- **useful because:** The browser is where the owner's logged-in life and secrets live. This gives a practical spoken privacy boundary instead of an all-or-nothing browser permission, while still letting the Mac and browser cooperate on real tasks.
- **path:** pendant → relay-realtime → faculty-judgement → mac-planner → browser-extension → faculty-perception → faculty-action → relay-realtime
- **model tier:** Realtime handles the short consent exchange; deterministic browser extension filters tab/session context; a cheap classifier can label sensitivity. No vision model unless the task truly requires pixels.
- **latency:** Under 2 seconds to present choices and under 5 seconds to enforce the selected scope before action.
- **cost:** A few cents at most per protected action; browser filtering and serial/relay messages dominate, not inference.
- **security:** Never send page contents to the pendant or cloud merely to ask permission. Use opaque tab/session IDs and sensitivity labels. Default to public-only on ambiguity, expire the allowlist after one operation or a short deadline, and record the selected scope in the action receipt.
- **missing:** Browser extension support for sensitivity labels and context allowlists; Planner/action schema that carries an allowlisted context set end to end; A resolvable perception verifier for proving which tabs/fields were used; Owner policy for when this question is mandatory

### "After you act for me, give me a spoken, tamper-evident receipt: what you changed, which app/tab/file it affected, what evidence confirmed it, and what remains unknown. Let me say “show the receipt” later and hear the exact short version without reopening the private content."
- **useful because:** The owner can trust delegated work without watching the screen. It turns opaque automation into an accountable history and makes failures or uncertain outcomes recoverable, especially when the pendant is away from the Mac.
- **path:** pendant → relay-realtime → faculty-action → faculty-perception → mac-planner → browser-extension → mac-vision → relay-realtime
- **model tier:** Cheap deterministic receipt construction and hashing; realtime only summarizes on request. Vision is used only when app state cannot be read structurally.
- **latency:** Receipt commitment within 1 second of action completion; spoken replay starts within 2 seconds.
- **cost:** Near-zero for hashes and structured state; $0.01–$0.05 only when a visual check is required.
- **security:** Store hashes and minimal metadata by default, not page contents or secrets. Encrypt private receipts, enforce retention/expiry, bind each receipt to operation and attempt IDs, and label unverified outcomes explicitly rather than claiming success.
- **missing:** A real read-only postcondition verifier (verify_operation_step is granted but unresolved); Receipt persistence and replay route keyed by operation/attempt IDs; Executor instrumentation that records exact target locators and before/after hashes; A pendant delivery format that can fit concise receipts offline

### "Start the task now, but if anything is ambiguous or needs my choice, pause exactly where you are, tell me the one decision, and resume from that checkpoint when I answer—even if the Mac, browser, or pendant link dropped in between."
- **useful because:** Real tasks fail today when a browser prompt, permission, or missing detail interrupts them. A durable checkpoint lets the owner delegate long workflows from a wearable without losing place or forcing a restart that may duplicate a purchase, message, or edit.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-judgement → faculty-action → faculty-perception → relay-realtime
- **model tier:** Cheap deterministic state machine for checkpoints and retries; realtime model only interprets the owner's choice and summarizes the next step. Use the planner model again only when the prior page/app state is no longer valid.
- **latency:** Checkpoint commit under 500 ms; resume acknowledgement under 3 seconds after the owner answers.
- **cost:** Low: mostly durable JSON state and existing job polling; $0.01–$0.05 for replanning only after stale state.
- **security:** Never blindly replay a side effect after reconnect. Persist step id, idempotency key, preconditions, expiry, and whether the step is reversible. Re-verify fresh app/browser state before resuming; require physical approval again if the old approval expired or the target changed.
- **missing:** A durable checkpoint schema and resume endpoint tied to operation/step IDs; Executor idempotency keys and explicit pause-safe boundaries; A resolvable read-only verifier for fresh Mac/browser preconditions; Pendant delivery of a concise pending-choice card through the existing audio path

### "Before carrying out a consequential request, tell me the strongest plausible way your interpretation could be wrong, what would happen if it were wrong, and the one fact that would disambiguate it. Let me answer that fact once from the pendant, then proceed or refuse."
- **useful because:** The owner gets an adversarial safety check rather than a confident guess. This catches wrong recipients, similarly named files, stale browser accounts, and ambiguous purchases before anything leaves the machine.
- **path:** pendant → relay-realtime → faculty-judgement → faculty-perception → faculty-action → mac-planner → browser-extension → mac-vision
- **model tier:** A separate inexpensive critique pass for ordinary actions; realtime only presents the concise risk and asks the single clarifying question. High-risk actions may use an independent model with no shared hidden context.
- **latency:** 2–5 seconds before execution; never more than one clarification round unless the owner asks for detail.
- **cost:** Approximately $0.02–$0.12 per consequential action, dominated by the independent critique model or visual inspection.
- **security:** The critic must see only the minimum task and target metadata, not secrets. It must not invent certainty or silently widen scope. If critics disagree, fail closed and stage the action. Preserve the critique and answer as an auditable preflight record.
- **missing:** An independent critique route with separate context isolation; A structured ambiguity/risk schema shared by judgement and action; Fresh target disambiguation from Mac/browser state; A compact pendant interaction for answering one fact without exposing private page content

### "Rewrite this outgoing message to reveal the least personal information needed to accomplish its purpose, show me the private details you removed as categories rather than quoting them, and let me approve the redacted version from the pendant before sending."
- **useful because:** The owner can ask the system to communicate without accidentally disclosing home addresses, health details, private names, or unrelated conversation context. It is more useful than merely warning that a draft is sensitive: it produces a safer usable draft.
- **path:** pendant → relay-realtime → faculty-judgement → faculty-perception → faculty-action → mac-planner → browser-extension
- **model tier:** A cheaper structured redaction model produces the candidate and classified removals; realtime reads a short summary; deterministic diffing ensures the sent bytes equal the approved draft.
- **latency:** 3–8 seconds to produce a candidate; under 2 seconds to approve and send.
- **cost:** About $0.02–$0.10 per draft, depending on classification and whether browser form state must be inspected.
- **security:** Raw private content must remain on the Mac/browser whenever possible. The pendant receives categories and a redacted preview, never the removed secrets. No automatic send after rewriting; require explicit approval for external communication. Keep the original and candidate in separate encrypted stores with short retention.
- **missing:** A local redaction/classification service with stable entity categories; Byte-exact draft diff and approval binding so the sent text cannot change after approval; Browser and Mail/Message adapters that expose draft state without leaking content to the relay; A policy defining categories that are never allowed to leave the Mac

### "When you tell me a personal fact or recommendation, let me ask “why do you believe that?” and hear a short provenance chain: which Mac file, calendar event, browser page, or conversation supplied it, when it was observed, what may be stale, and what you inferred rather than directly saw."
- **useful because:** The owner can detect stale or misattributed personal information before it drives an action. This makes the hive trustworthy without reading private documents aloud and distinguishes observed facts from model guesses.
- **path:** pendant → relay-realtime → faculty-perception → faculty-judgement → faculty-action → mac-planner → browser-extension → mac-vision
- **model tier:** Deterministic provenance graph and freshness calculation; a low-cost model compresses the chain into speech. Realtime is only needed for the conversational explanation.
- **latency:** Under 2 seconds for an existing fact; under 10 seconds if fresh Mac/browser inspection is required.
- **cost:** Near-zero for indexed provenance; $0.01–$0.05 for summarization or a fresh inspection.
- **security:** Speak source types and minimal titles by default, not document contents. Require a deliberate request before revealing sensitive source names. Hash source snapshots, enforce retention, and mark inferred links as uncertain rather than presenting them as evidence.
- **missing:** A provenance graph that records source locator, observation time, transformation, and confidence for every claim; Instrumented Mac/browser reads that emit provenance events rather than only final text; Freshness and contradiction rules across calendar, files, browser, and conversation state; A privacy-preserving spoken provenance formatter


## Changes it proposed to its own stack

### `integration` — Add a policy-enforced context firewall between faculty-judgement and every executor. Each operation receives an immutable ContextGrant containing opaque browser session/tab IDs, allowed sensitivity class, purpose, expiry, and one-use scope. browser-extension rejects commands outside the grant; mac-planner strips ungranted context from prompts; faculty-action records grant use and sends the grant ID to postcondition verification. Default grant is empty/public-only.
- **owner gets:** The system will stop accidentally using an open private tab, message, or document while still being able to act across the Mac and browser. The owner gets a simple spoken privacy choice rather than needing to understand internal routing.
- effort: Medium-high: schema and enforcement in planner, browser bridge, Mac executor, and relay; integration tests for expiry, replay, and disconnect.  ·  risk: A false sensitivity label could block a useful action or, worse, allow too much. Fail closed, provide a visible reason, and allow the owner to explicitly widen scope for one operation. Recover by cancelling the operation and requiring a new grant.
- cost: Negligible runtime/API cost; engineering effort across four surfaces.  ·  latency: Under 100 ms for grant checks; no model latency unless classification is unavailable.
- security: Material improvement: least-privilege context, reduced prompt leakage, replay-resistant one-use grants. Does not replace physical approval for irreversible actions.
- depends on: Browser extension must expose stable opaque session/tab identifiers and sensitivity labels; The existing actionRisk/approvalHandoff/policyRouter seam must carry ContextGrant; A real verifier route must consume grant ID and confirm actual context use


## What it asked for

_Nothing._
