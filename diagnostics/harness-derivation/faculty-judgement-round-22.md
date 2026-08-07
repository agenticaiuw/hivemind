# Harness derivation — faculty-judgement — round 22

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I mention something I might want to do, keep it as a tentative decision, quietly gather the missing context, and later ask me one precise question before preparing the next step—without making me repeat myself."
- **useful because:** People often voice half-formed intentions while walking or interrupted. Today the pendant either forgets them or turns ambiguity into a brittle command. This makes uncertainty explicit: the wearable preserves the thought, the always-on relay waits, the Mac/browser gathers only relevant evidence, and the owner gets a single high-value choice rather than a long interrogation or an accidental action.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Use the cheap background model for intent classification, deduplication, evidence retrieval, and question selection; use realtime only for the brief spoken clarification and final confirmation. Use no model for expiry, consent, or action-manifest validation.
- **latency:** Capture must be local/offline in under 300 ms. Relay acknowledgement under 2 s when connected. Evidence gathering can take minutes in the background. Clarification should be a 5–10 s spoken exchange; nothing irreversible runs until the owner confirms.
- **cost:** About $0.01–$0.05 per decision window, dominated by one background synthesis over gathered evidence; realtime cost is limited to the final short question. Most windows should resolve with rules and no model call.
- **security:** Tentative thoughts may contain sensitive personal or work information; encrypt the queue, apply TTLs, and project only task-relevant facts. Reading logged-in pages is allowed by owner policy, but sending mail, deleting, buying, or external submission still requires explicit confirmation. Show sources and an expiry reason when asking. Never infer consent from silence.
- **missing:** A durable decision-window record with tentative/ready/confirmed/expired states and evidence requirements; Cross-surface intent continuity and offline handoff markers so a spoken thought survives link loss; A question-ranking endpoint that chooses one clarification from current evidence; Integration with faculty-action's signed action manifests and temporal-firewall invalidation; Pendant audio/UI for a compact 'hold this thought' marker and later focused question; A dashboard review lane for unresolved windows and retention/deletion controls

### "Before I commit to this, show me what it will change across my calendar, inbox, files, browser tasks, and pending promises—and let me compare two options without changing anything."
- **useful because:** The owner can currently get isolated answers or prepare isolated actions, but not a trustworthy whole-life consequence map. This capability turns a vague decision into a reversible comparison: the Mac and authenticated browser inspect relevant state, the relay reconciles dependencies, and the pendant gives a short spoken summary with a clear 'what changes / what does not' boundary. It helps the owner avoid double-booking, forgotten follow-ups, accidental commitments, and downstream surprises.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use a cheaper background model to extract entities, identify dependencies, and generate competing scenarios. Use deterministic graph/diff logic for dates, files, drafts, and action scopes. Use realtime only to present the final short comparison and receive the owner's selection.
- **latency:** The owner gets an immediate acknowledgement from the pendant. A normal comparison should complete in 10–30 seconds; broad research may run asynchronously for up to several minutes. Both options remain read-only until explicit selection and a separate confirmation for any irreversible effect.
- **cost:** Approximately $0.02–$0.08 per comparison, dominated by background synthesis over selected evidence; deterministic diffs and cached projections should avoid repeated model calls. No cost for an unexecuted scenario beyond the read-only retrieval.
- **security:** The graph may connect sensitive calendar, mail, files, and logged-in webpages. Keep raw content local where possible, send only typed facts and citations to the relay, enforce per-source allowlists and TTLs, and expose exactly which records informed each consequence. Never execute or send from a simulation; require fresh confirmation after material state changes.
- **missing:** A cross-surface consequence graph with typed entities, dependencies, provenance, and freshness; A read-only scenario/diff engine that can fork two plans without creating real drafts or mutations; Common identity and deduplication for the same meeting, person, task, file, or promise across Mac and browser; A compact pendant rendering for consequence summaries and option selection; A post-selection handoff into signed, expiring action manifests with a fresh temporal-firewall check; A dashboard view that lets the owner inspect, discard, or retain scenario evidence


## Changes it proposed to its own stack

### `context` — Add a Decision Window compiler shared by relay, Mac planner, browser bridge, and faculty-action. Each window has a stable id, owner wording, confidence, missing-decision slot, evidence queries, sensitivity/TTL, allowed action class, and an append-only provenance chain. The compiler emits either one ranked clarification question or a signed, expiring action manifest; it must CAS against perception changes and temporal-firewall invalidations before any executor sees it.
- **owner gets:** A passing thought becomes a safely recoverable thread instead of disappearing or turning into the wrong task. The owner hears one understandable question with evidence, and can resume it later from the pendant or Mac without reconstructing what they meant.
- effort: Medium-high: shared schema and relay persistence, pendant marker/audio, background retrieval adapters, planner/browser evidence normalization, and dashboard review UI. Start with calendar/mail/files and reversible drafts, then add external sites.  ·  risk: Over-capturing private speech, stale evidence, and annoying questions. Mitigate with an explicit 'hold that thought' trigger or high-confidence intent threshold, short default TTL, quiet hours, deduplication, one-question cap, visible sources, and discard/forget controls. Recovery is to expire the window and preserve only a redacted receipt.
- cost: Low ongoing storage; roughly one background model call per unresolved window ($0.01–$0.05), with realtime only for spoken clarification. Engineering cost is the main cost.  ·  latency: No added latency to normal conversation. Local capture is immediate; background evidence is asynchronous; clarification is delayed until evidence is ready or the window nears expiry.
- security: Sensitive tentative intent and authenticated-page excerpts cross relay boundaries. Encrypt at rest/in transit, enforce per-window source allowlists, minimize projections, redact secrets, and require explicit confirmation for any external side effect.
- depends on: typed context projection migration (chg-a82e0b13); intent continuity ledger and offline handoff marker; faculty-action signed action manifests / temporal firewall; durable browser job runner and authenticated page access; pendant local interruption/brief-item interaction primitives

### `context` — Create a read-only Scenario Graph service that snapshots task-relevant state from Mac, authenticated browser tabs, relay jobs, notes, calendar, and pending commitments into a versioned graph. Add a fork-and-diff API: each fork contains proposed changes, affected entities, confidence, provenance, reversibility, and unknowns; it cannot emit executable actions. On selection, materialize only the chosen fork into a fresh signed action manifest and require the temporal firewall to revalidate every assumption.
- **owner gets:** The owner can see the second- and third-order consequences of a choice before their life is changed. They can compare 'take this meeting' versus 'decline and follow up' or 'move this appointment' versus 'keep it' with evidence, instead of discovering conflicts after committing.
- effort: High: typed cross-surface entity resolution, snapshot/version storage, scenario diffing, source adapters, privacy projection, pendant summarization, dashboard inspection, and an explicit bridge to the action executor. Begin read-only with calendar, notes, relay jobs, and open browser tabs.  ·  risk: False dependencies or stale snapshots could make a scenario look more certain than it is; graph growth could expose unrelated private data; users could mistake a simulation for an action. Mitigate with confidence labels, timestamps, explicit unknowns, source citations, strict task-scoped projection, snapshot expiry, prominent READ-ONLY labeling, and a fresh confirmation after selection. Recovery is deleting the fork without touching source state.
- cost: Moderate storage for compact typed snapshots and low per-request model cost (roughly $0.02–$0.08 for synthesis); entity resolution and source adapters dominate engineering cost.  ·  latency: Snapshotting can be asynchronous and cached. Initial comparison target is 10–30 seconds, with progressive results; no latency added to ordinary voice turns.
- security: This creates a high-value map of personal relationships and obligations. Encrypt snapshots, isolate per-owner namespaces, minimize raw excerpts, honor source-level permissions, apply short TTLs to forks, audit every source read, and prohibit the scenario API from invoking mutating tools.
- depends on: typed context projection and provenance; cross-surface identity resolution; durable relay/job and browser session records; faculty-action signed manifests and temporal-firewall CAS checks; pendant option-selection and concise audio rendering


## What it asked for

### `t10-jg00` (tool) — decision_window
- why: Implement the proposed tentative-intent workflow without making each surface invent incompatible state. The relay needs a durable, privacy-scoped record that can be resumed by the pendant, planner, browser, and action executor.

```json
{
  "operation": "create|append_evidence|set_status|get|list|expire|redact",
  "windowId": "string, required for all operations except create/list",
  "ownerWording": "string, required on create",
  "source": "pendant|voice|mac|browser|system",
  "confidence": "number 0..1",
  "missingDecision": "string or null",
  "evidenceRequirements": "array of {surface, query, allowedSources, freshnessSeconds}",
  "evidence": "array of {sourceRef, capturedAt, excerpt, sensitivity, confidence}",
  "status": "tentative|gathering|ready|awaiting_owner|confirmed|rejected|expired",
  "ttlSeconds": "integer",
  "allowedActionClass": "read_only|draft|reversible|irreversible",
  "idempotencyKey": "string",
  "redact": "boolean"
}
```

## Its own summary

I found no existing backlog item that covers a tentative-intent decision window. I proposed: (1) a cross-surface capability where a pendant-captured half-formed thought survives interruption/link loss, the relay gathers bounded evidence through Mac/browser, and the pendant asks one focused clarification before any draft/action; (2) a shared Decision Window compiler with provenance, TTL, sensitivity, action class, and CAS linkage to faculty-action’s temporal firewall. I requested a durable decision_window tool and sent the schema alignment to faculty-action. Still needed: orchestrator decision on that tool, the already-pending intent/offline/attention/audio primitives and persistence context, plus authenticated browser and Mac permissions for real evidence gathering. No new irreversible permission is needed for the proposal itself.

**Biggest unknown:** Whether the existing cross-surface persistence primitives (still pending from the orchestrator) can host Decision Window records, or whether a separate durable store and retention policy must be built.

