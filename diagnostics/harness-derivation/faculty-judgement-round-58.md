# Harness derivation — faculty-judgement — round 58

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What do I actually know about this?” — reconcile the claims in my mail, calendar, notes, and logged-in pages, show what is confirmed versus assumed or contradicted, and keep the answer current until I tell you it is settled."
- **useful because:** People lose trust when assistants flatten an email, an old note, and a live account page into one fact. This gives the owner a compact answer with freshness and provenance, and surfaces contradictions before they become missed appointments, wrong payments, or embarrassing replies. It is genuinely cross-surface: the pendant is the query and alert surface, the relay coordinates durable claims, browser reads private web evidence, and Mac reads local notes/mail/calendar.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Background/cheap model extracts and normalizes claims; faculty-perception reconciles evidence and assigns confidence; realtime is used only for the owner's spoken question or a high-impact contradiction alert.
- **latency:** Spoken answer in 3–6 seconds for an existing topic; 30–90 seconds for a fresh multi-source reconciliation. Contradiction alerts are queued and interruption-arbitrated rather than speaking immediately.
- **cost:** Roughly $0.01–$0.06 per fresh reconciliation, dominated by model context and private-page extraction; cached claim updates should be cents or less. Storage is small structured records plus source hashes, not copied page contents.
- **security:** Private mail, calendar, notes, and authenticated pages are processed. Keep raw content on the Mac/browser session where possible; relay stores only normalized claims, source identifiers, hashes, sensitivity, TTL, and user-selected topic scope. Never expose secrets in spoken alerts; require confirmation before turning an inferred claim into an external action.
- **missing:** A durable claim/evidence schema with source, observedAt, freshness/TTL, confidence, sensitivity, and contradiction links; A topic-scoped reconciliation route that can fan out to Mac and authenticated browser reads and return citations; A review UI/audio format for confirmed, uncertain, and conflicting claims, with dismiss/settle/forget controls; A change-trigger bridge from page watches, calendar/mail/file events, and voice notes into claim re-evaluation; Retention and deletion policy for derived claims and source hashes

### "“Help me practice this difficult conversation.” Use the context I authorize from my notes, calendar, mail, and relevant browser pages to role-play the other person, challenge my assumptions, and leave me with a concise set of points and boundaries I can recall from the pendant."
- **useful because:** The owner can prepare while walking, without manually assembling context or exposing private material to a separate coaching service. The pendant provides private voice rehearsal, the Mac and browser gather the authorized facts, and the relay keeps the exercise coherent across interruptions. This is not merely meeting preparation: it helps the owner discover what they actually want to say, rehearse likely objections, and preserve their chosen boundaries without sending anything.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a cheaper background model to build a sourced context packet and objection candidates. Use realtime only for the live role-play and short spoken coaching turns. A final low-cost pass can compress the owner's chosen points into a durable rehearsal card.
- **latency:** Context assembly in 20–60 seconds; each spoken role-play turn under 2 seconds; final rehearsal card under 10 seconds.
- **cost:** Approximately $0.03–$0.15 per rehearsal, dominated by context extraction and the realtime turns. Reusing a prepared context packet reduces repeat cost.
- **security:** Mail, notes, calendar, and authenticated pages may contain sensitive relationship and employment information. Keep raw sources local to Mac/browser, send only selected excerpts and citations to the relay, and make the owner explicitly choose the role and source scope. Never contact the other person or infer sensitive traits; require confirmation before saving the rehearsal card or creating any follow-up.
- **missing:** A first-class rehearsal session with role, objective, authorized source scope, and expiry; A local source-packet compiler that cites excerpts without copying whole private pages; A realtime role-play mode with explicit distinction between sourced facts, simulated objections, and model speculation; Pendant controls for pause, “stay in character,” “coach me,” and “save that point”; A private rehearsal-card store with automatic expiry and deletion


## Changes it proposed to its own stack

### `memory` — Add an append-only epistemic-claim layer between perception and action. Each claim has subject/predicate/value, source surface and locator, observedAt, TTL, confidence, sensitivity, derivation, and supersedes/contradicts links. A topic compiler returns only the minimal current claim set plus unresolved conflicts; source payloads remain on Mac/browser and can be re-fetched. Every action plan that relies on a non-confirmed claim must carry that uncertainty into its receipt and pause when the uncertainty could cause an external side effect.
- **owner gets:** The owner gets answers that say “confirmed,” “probably,” or “these two sources disagree,” instead of confident but stale automation. Old calendar details or notes stop silently driving the wrong action, and the owner can settle a fact once rather than correcting it repeatedly.
- effort: Medium: schema and D1/R2 indexes, extraction/reconciliation worker, source-hash references, TTL sweeper, and adapters for existing research, jobs, page-watch, and Mac results. Add a compact spoken rendering and a review view.  ·  risk: Incorrect extraction or conflict resolution could create false doubt or hide a true contradiction. Mitigate by preserving source citations, never deleting conflicting evidence automatically, and requiring explicit owner settlement for high-impact claims. Recover by re-fetching the cited source and invalidating derived claims.
- cost: Low ongoing storage and model cost; incremental extraction can use a cheap model and hashes avoid storing duplicate pages. Fresh reconciliation is the main cost, roughly cents per topic.  ·  latency: No impact on ordinary commands if unused. Existing topics answer quickly from indexed claims; a fresh source fetch adds seconds.
- security: Derived claims can reveal sensitive relationships even without raw text. Encrypt and label sensitivity, enforce per-surface authorization, avoid secret values in spoken output, and support topic/claim deletion with source-local cleanup.
- depends on: A typed context projection with provenance and TTL (the open memory backlog items); A durable event/job trigger so page-watch, Mac, and pendant observations can enqueue claim updates; A review/settlement interaction on pendant and Mac; do not infer owner approval from silence

### `firmware` — Add an explicit audio session capability handshake and quality governor: advertise capture/playback rates, frame size, Opus mode, bridge wire clock, battery, and measured encode/decode headroom; relay selects a 24 kHz playback profile when safe and instructs a bounded downgrade (frame duration/bitrate, not silent format drift) when CPU, radio loss, or battery crosses thresholds. Emit a machine-readable session receipt recording every profile transition and verify the 24 kHz path with loopback tone plus speech fixtures.
- **owner gets:** The pendant sounds consistently natural instead of occasionally stuttering or silently changing quality. When conditions worsen it degrades deliberately and recovers automatically, so a conversation or briefing does not fail halfway through—and the owner can tell whether a quality issue came from the pendant, bridge, or network.
- effort: Medium-high: firmware session state and metrics, bridge negotiation, relay profile selection, fixture-based CI, and a small diagnostics view. The current 15,625 Hz mic means true 24 kHz capture still needs a documented resampling profile; playback can remain 24 kHz end to end where negotiated.  ·  risk: A governor oscillating between profiles could create audible artifacts; use hysteresis and minimum dwell times. A bad negotiation could strand old firmware; retain a versioned 16 kHz compatibility profile and fail closed to it. Loopback passing does not guarantee speech quality, so retain recorded fixtures.
- cost: Negligible API cost; a few hundred bytes of session telemetry. Firmware CPU may rise during resampling; no hardware cost for the prototype, though a production design should reserve DSP headroom rather than running both encode/decode at the current ~87% single-core load.  ·  latency: Handshake adds under 200 ms at session start; profile transitions occur on frame boundaries. Larger safety margins may add 20–60 ms buffering during packet loss.
- security: Telemetry should contain rates, counters, and battery—not audio. Authenticate profile commands and reject unsupported rates to prevent malformed decoder/resource exhaustion.
- depends on: 24 kHz acceptance criteria and current relay/pendant audio implementation truth; A versioned audio capability schema shared by firmware, bridge, and relay; Persistent pipeline receipts for profile transitions and failures

### `interaction` — Create a private rehearsal-session protocol distinct from ordinary planning or execution. It should accept an owner-selected goal, counterpart role, source allowlist, and forbidden inferences; compile a cited context packet on the Mac/browser; maintain a turn-by-turn state machine for role-play, coaching, and owner-authored points; and emit an expiring rehearsal card plus a receipt that proves no external action occurred. Pendant button gestures must pause, switch from role-play to coaching, or discard the session locally if the link drops.
- **owner gets:** They can safely rehearse a hard conversation in the moment and retain only the points they deliberately chose, without the assistant confusing simulation with fact or accidentally sending a message. The exercise remains usable while walking and recoverable after an interruption.
- effort: Medium-high: new session schema and protocol, source-packet compiler, realtime mode prompt/state machine, pendant gesture handling, local encrypted card storage, and explicit no-side-effect receipts.  ·  risk: A simulated person may sound more certain or hostile than reality and could reinforce a mistaken assumption. Label every simulated turn, cite factual inputs, offer multiple plausible reactions, and provide a one-tap discard. Link loss must fail to local pause—not continue with stale hidden state.
- cost: Low storage and no external API calls for discarded sessions; roughly $0.03–$0.15 per completed rehearsal depending on context size and realtime turns.  ·  latency: One context-build delay of 20–60 seconds, then sub-2-second spoken turns. Local pause/discard should be immediate even offline.
- security: High sensitivity by default. Raw source text should stay on the Mac/browser where possible; relay receives a minimal authorized packet. Encrypt rehearsal cards, expire them automatically, and prohibit the protocol from invoking send, purchase, deletion, or account mutation routes.
- depends on: A durable cross-surface session/event store; A local source-packet compiler with citations and redaction; Pendant offline pause/discard handling; A model-routing rule keeping background context assembly off realtime


## What it asked for

### `t19-dltk` (tool) — reconcile_evidence_claims
- why: Implement the new epistemic-claim capability without routing raw private content through the realtime model. It should fan out to authorized Mac/browser sources, normalize claims, preserve citations and conflicts, and return a compact topic-scoped answer suitable for spoken output.

```json
{
  "type": "object",
  "required": [
    "topic"
  ],
  "properties": {
    "topic": {
      "type": "string"
    },
    "sources": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": [
          "mac_mail",
          "mac_calendar",
          "mac_notes",
          "browser_authenticated",
          "browser_public",
          "pendant_notes"
        ]
      }
    },
    "freshness": {
      "type": "string",
      "enum": [
        "cached",
        "refresh_stale",
        "refresh_all"
      ],
      "default": "refresh_stale"
    },
    "sensitivity_max": {
      "type": "string",
      "enum": [
        "normal",
        "sensitive",
        "secret"
      ],
      "default": "sensitive"
    },
    "action_context": {
      "type": "string"
    },
    "include_raw_quotes": {
      "type": "boolean",
      "default": false
    }
  }
}
```

### `c6-kwwy` (context) — derived-claim storage and privacy policy
- why: The proposed epistemic-claim layer needs an explicit owner-safe retention boundary: whether normalized claims may persist, which sensitivity classes can be spoken, and how deletion propagates to Mac/browser sources.
- would change: Until clarified, I would design claims as short-TTL derived metadata only, never persist raw quotes or secrets, and require explicit confirmation before any claim influences an external action.

