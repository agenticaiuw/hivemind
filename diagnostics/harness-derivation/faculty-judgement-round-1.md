# Harness derivation — faculty-judgement — round 1

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **owner and product** — Owner uses a voice-first pendant with one-short-sentence spoken replies; allows browser reading/clicking and reminders/notes without asking, but requires confirmation before sending mail, deleting files, or buying. Active goals are reliable voice and shipping 24 kHz superwideband audio end-to-end.
  - evidence: owner discovery returned remembered facts and goals.
- **available surfaces** — Mac local agent v0.5.0 is reachable on localhost:8000 with 120 routes, including briefings, research, routines, browser sessions/watches, mail triage (compose/store only), meeting prep/follow-up, memory, jobs with undo, and execution journal. Relay is configured and reachable; browser extension is offline; Mac is not ready because Accessibility and Screen Recording are missing despite cached automation grants.
  - evidence: GET /capabilities and GET /ops/status returned these live states.
- **unmet capability pattern** — Owner repeatedly asked for authenticated account/calendar/mail/GitHub access, browser page access, and status checks; recorded attempts failed. Existing backlog repeatedly proposes durable browser work queues/page watches, morning private-account briefings, background work with completion notice, and audio digests, but these remain proposed rather than implemented.
  - evidence: owner discovery asked_for_and_did_not_get plus backlog entries cap-26c609fc and cap-e21eb7f4 (status proposed), and browser extension offline in /ops/status.
- **reliability risks affecting judgement** — Current system has a live timezone mismatch (owner memory America/Chicago vs machine context America/New_York), cached Automation grants that conflict with briefing reports saying Calendar/Mail unavailable, and duplicate unplayed identical scheduled research briefings. These are trust failures that should trigger reconciliation before personalized actions or claims.
  - evidence: faculty-perception live findings.

## What it asked for

### `t1-3r6y` (tool) — reconcile_personal_state
- why: The owner’s system currently has conflicting timezone/permission reports and duplicate scheduled audio. Judgement needs a read-only, provenance-backed reconciliation before promising calendar/mail access or issuing briefings; existing status endpoints expose raw surfaces but no unified conflict detector.

```json
{
  "type": "object",
  "properties": {
    "domains": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": [
          "timezone",
          "permissions",
          "scheduled_briefings",
          "browser_connectivity",
          "audio_queue",
          "goals"
        ]
      }
    },
    "as_of": {
      "type": "string",
      "format": "date-time"
    },
    "include_recommendations": {
      "type": "boolean"
    }
  },
  "required": [
    "domains"
  ]
}
```

## Its own summary

Environment reconnaissance complete. The owner has a voice-first AI Pendant Simulator on a Mac local agent v0.5.0 plus Cloudflare relay. Live Mac/relay are reachable, but Accessibility and Screen Recording are missing and Safari/browser extension is offline; cached automation grants conflict with reported availability. The owner wants reliable voice, 24 kHz audio, private account/calendar/mail/GitHub help, browser access, status checks, and background work with concise spoken results. Several high-value capabilities remain proposed only (durable browser work queue, authenticated page watches, morning private-account brief, completion-after-leaving, audio digest). The most important unfilled capability is a read-only personal-state reconciliation and recovery lane: detect permission/timezone/connectivity/duplicate-audio conflicts, state exactly what is blocked, queue/retry safely when a surface returns, and never claim access or completion from stale cache. I queued request_tool reconcile_personal_state with a provenance/conflict schema.

**Biggest unknown:** Peer agents may identify additional owner needs, but the central trust/recovery gap is already evidenced by failed owner requests, offline browser, permission contradictions, timezone mismatch, and duplicate briefings.

