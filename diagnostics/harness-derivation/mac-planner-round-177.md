# Harness derivation — mac-planner — round 177

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac host and browser are currently usable for cross-node prototypes** — At 2026-08-08T01:38:24Z, AI Pendant Agent is foreground-capable with Accessibility trusted, synthesized events verified, Screen Recording true, secure input false; Safari bridge is online with 9 tabs and active OpenAI billing page. The granted mac_readonly_inspect wrapper still fails to resolve accessibility_enabled and browser_tabs due resolver ambiguity, but GET /observe returns the live state directly.
  - evidence: mac_readonly_inspect foreground_app resolved GET /observe HTTP 200; body reports accessibility trusted/eventsPost true/screenRecording true and browser tabs including platform.openai.com; other two calls returned unresolved/ambiguous nearest capabilities.

## Capabilities it proposed

### "When I say “what am I looking at?”, tell me what is on my active browser page or Mac window and the single next action that matters."
- **useful because:** This is the first genuinely hive-native answer: the pendant supplies the low-friction question, the browser supplies authenticated page context, the Mac supplies the foreground application, and the relay fuses them instead of making the owner explain which surface they mean. It turns an arbitrary work state into an actionable spoken answer in seconds.
- **path:** pendant → relay → browser → mac-planner → mac-vision
- **model tier:** Realtime for the spoken answer; a cheap structured extractor should first normalize tab title/URL/page text and foreground-window metadata, with realtime only deciding relevance and wording.
- **latency:** Target 2-4 seconds. Browser and Mac observations in parallel (<700 ms), extraction in <1 s, speech generation thereafter. If either surface is unavailable, say exactly which one and answer from the other rather than stalling.
- **cost:** About $0.01-$0.04 per invocation; browser/Mac observation dominates neither cost nor time, while realtime synthesis and 1-3k tokens of page context dominate.
- **security:** Authenticated page text leaves the browser bridge and is sent to the relay/model; redact password fields, tokens, billing identifiers, and hidden DOM by default. Never click or submit. Make the response explicitly observation-only. Owner must configure which domains may be read unattended.
- **missing:** A browser inspection result that returns bounded visible text plus semantic controls for the active tab (not just URL/title); A Mac window/document identity payload from ui_snapshot when Accessibility/Screen Recording are unavailable; A relay fusion endpoint that accepts typed browser and Mac observations and returns a spoken next-action answer

### "Save this page as a useful research note."
- **useful because:** The owner can convert an authenticated or otherwise hard-to-revisit page into a durable, readable artifact without copy-paste: the browser contributes the visible page and URL, the relay extracts claims and citations, and the Mac atomically writes a Markdown note into a chosen project folder. The pendant is the capture trigger; no single node can do the whole job while the owner is moving.
- **path:** pendant → browser → relay → mac-planner
- **model tier:** Background/cheap model for extraction, citation normalization, and concise summarization; realtime only acknowledges capture and reports completion over audio.
- **latency:** Acknowledge in under 1 second, finish in 5-15 seconds depending on page size. Write a draft if extraction exceeds the spoken latency budget, then announce the file path.
- **cost:** Roughly $0.005-$0.03 per page; page text and summarization tokens dominate. Mac file creation is negligible.
- **security:** Page content may contain private work or secrets. Send only bounded visible text, exclude password/input values and cross-origin frames, include the source URL and retrieval time, and write only under an owner-selected allowlisted folder. Never infer that a page is public from its URL.
- **missing:** A browser command/result that returns bounded visible-page text, selection, canonical URL, and citation anchors; A relay transform that emits a deterministic note plus sha256 and provenance metadata; An owner-configured research-folder policy and a pendant trigger/ack path

### "When the pendant is plugged into my Mac, let me use it as a complete local assistant even with no LTE or internet: press the button, speak, and hear the answer, with the answer able to open or write things on the Mac."
- **useful because:** The hardware is physically present now but LTE registration is not. This turns the real tethered pendant into a useful product today instead of a paperweight in dead zones: local capture and playback stay on the pendant/USB bridge, the Mac handles inference and desktop actions, and the relay is optional rather than a single point of failure.
- **path:** pendant → audio → mac-planner → mac-vision → relay
- **model tier:** A small local Mac model or cached command grammar for immediate intents; use the expensive realtime tier only when a local model cannot answer. No cloud call for private/local commands unless the owner explicitly asks for it.
- **latency:** Button-to-listening tone under 150 ms, local transcription partials under 500 ms, simple command completion under 2 s. Cloud fallback may be clearly announced as unavailable or delayed.
- **cost:** Near-zero API cost for local commands; optional cloud fallback costs normal realtime inference. Engineering cost is serial framing, local STT/TTS, and routing, not model tokens.
- **security:** USB serial is a privileged control channel: authenticate the pendant, bind it to this Mac, and show a persistent local indicator when microphone/audio/control mode is active. Keep audio in RAM unless the owner invokes an offline memo. Desktop mutations must be recorded in the existing job receipt path and use the owner's configured policy, not silently inherit FULL_CONTROL_MODE.
- **missing:** A live mac_serial_exchange capability for bidirectional framed transport to /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A local audio/STT/TTS loop that can consume pendant frames and return Opus/PCM without the relay; A pairing key and reconnect protocol for the two USB serial devices; A typed local-intent router that can hand desktop actions to mac_run_actions and preserve receipts

### "Use my pendant as a physical presence key: when I explicitly ask, let it authorize one sensitive action in the authenticated browser session, show me exactly what will happen, and record the result."
- **useful because:** Today the browser session and Mac agent can act, but neither can prove that the person requesting a consequential action is physically holding the pendant. This would combine possession of the worn device, the authenticated browser session, and a deterministic action preview into a narrowly scoped authorization event. It is not a general automation gate: it is a new owner-visible way to safely perform actions that cannot responsibly be inferred from voice alone.
- **path:** pendant → relay → browser → mac-planner
- **model tier:** A cheap deterministic planner creates the exact action preview and resource list. Realtime only handles the owner's spoken request and reads the preview; no model should decide whether a physical confirmation is valid.
- **latency:** Preview in under 2 seconds; pendant confirmation acknowledgment under 500 ms; browser execution and receipt within 5 seconds. Expire an unconsumed authorization after 30 seconds or a browser-session change.
- **cost:** Less than $0.01 per invocation; browser inspection and deterministic signing dominate engineering complexity, not API usage.
- **security:** The pendant must never authorize an arbitrary server-supplied action. Bind a one-time nonce to the exact normalized URL, tab ID, action list, account/session identity, and expiry; display a short human-readable summary on the pendant; require a deliberate button edge; reject replay, tab changes, navigation changes, and stale previews. Store only a redacted receipt. This must not silently authorize purchases, messages, or deletion without an owner-configured action class.
- **missing:** A cryptographic pendant-to-Mac/relay pairing and one-time nonce protocol; A firmware confirmation primitive that can display or encode a short action digest using the existing LED/button constraints; A browser harness action-preview and commit endpoint that revalidates tab identity and page state between preview and execution; A policy configuration owned by the user defining which sensitive action classes may use pendant presence

### "Before you act, tell me which account, workspace, browser tab, and local project you are actually using, and stop if they do not match the context I named."
- **useful because:** Authenticated browser sessions, Mac files, Calendar/Mail accounts, and relay jobs can each be valid while referring to different identities or workspaces. The owner cannot reliably see that mismatch from a pendant. A provenance check would prevent the most expensive class of silent mistake: sending or editing the right thing in the wrong account.
- **path:** pendant → relay → browser → mac-planner
- **model tier:** Deterministic account/session/resource resolver first; a cheap model may turn the structured result into plain language. Realtime is unnecessary except for the spoken response.
- **latency:** Under 1 second for already-known session metadata; under 3 seconds if a browser inspection is required. No action should begin until the provenance record is complete.
- **cost:** Under $0.01 per check; metadata reads dominate, with negligible model cost.
- **security:** Do not expose full email addresses, tokens, or document contents in speech. Return redacted account labels and stable fingerprints. Treat missing identity metadata as unknown, not as a match. Persist a provenance hash with the action receipt so later review can identify exactly which session and local root were used.
- **missing:** Typed identity metadata from browser sessions, Calendar/Mail account scope, local project roots, and relay jobs; A cross-surface provenance resolver that compares requested context with observed identities; A spoken and machine-readable mismatch result that can be consumed before POST /execute

### "Undo the last thing you did, wherever it happened, and tell me exactly what was reversed and what cannot be reversed."
- **useful because:** The system already records Mac jobs, browser commands, and relay activity in separate places, but the owner has no single spoken recovery command. A unified undo would resolve “that” across surfaces, apply reversible compensations in reverse dependency order, and honestly distinguish completed reversals from irreversible side effects.
- **path:** pendant → relay → browser → mac-planner
- **model tier:** Deterministic receipt graph and compensation executor; use realtime only to resolve ambiguous natural-language references such as “the email one” and to report the result.
- **latency:** Resolve the target in under 1 second and present a preview under 2 seconds. Reversible local/browser changes should complete within 5 seconds; external side effects must return an explicit non-reversible report.
- **cost:** Under $0.01 for deterministic receipt lookup; model cost is only incurred for ambiguous references.
- **security:** Never claim an external message, purchase, deletion, or remote mutation was undone unless the target service confirms it. Bind compensation to the original receipt, tab/session identity, and resource version. Preserve an append-only audit trail and refuse guessed targets when multiple recent actions match.
- **missing:** A single cross-surface receipt graph with causal ordering and compensation descriptors; Browser-side inverse operations or service-specific confirmation for actions that are currently only logged; A pendant/relay intent that can address the latest action by stable receipt ID and speak a bounded result; Version checks for local files and browser state before applying compensation


## What it asked for

_Nothing._
