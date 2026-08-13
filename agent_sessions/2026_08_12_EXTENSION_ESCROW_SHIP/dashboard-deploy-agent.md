# Dashboard deploy — closing the committed-vs-deployed gap

Owner: orchestrator (CEO context)
Date: 2026-08-13

## The ask

> "can you make sure you deploy the changes to the dashboard?"

## What was actually wrong

The dashboard changes were **committed but never shipped**. There is no CI in this
repo — no `.github/workflows` at all — so `git push` deploys nothing. The
SvelteKit dashboard has to be deployed by hand, and it has **two** outputs:

| surface | command | where it lands |
|---|---|---|
| public Worker | `npm run deploy:cloudflare` | `ai-pendant-dashboard.evan20050827.workers.dev` |
| Mac agent copy | `npm run build:agent` | `build-agent/`, served at `127.0.0.1:8000/dashboard` |

Last Worker deploy before today: **2026-08-12T19:27:49Z**.

Dashboard commits after that timestamp, i.e. live nowhere:

- `fb0d272` 2026-08-12T15:26 CDT — *System tile row deleted* ← the owner asked for
  this and had been looking at a dashboard that still had the row.

So the owner's suspicion was correct, and it was not a UI bug — it was a
delivery gap. The commit was real; the deploy never happened.

## What went out

Worker version **`4a9f2a5a-68bc-4a36-a8cc-1e6704f966e8`**, carrying:

- `fb0d272` System tile row deleted (previously committed, never deployed)
- the composer-to-top move (`+page.svelte`) and its margin fix (`globals.css`)
- the new `/bench` route, which self-describes as Mac-only on the hosted build

## How it was verified — by bytes, not by eye

Opening the page and looking at it proves nothing: a browser can serve a cached
asset, and a login redirect hides the payload entirely. So:

1. **Live asset vs local build, byte for byte.**
   `_app/immutable/nodes/2.B56mGJ_0.js` — local 37993 bytes / sha256
   `4baf8e087515d2e4`; fetched from the live Worker: 37993 bytes / sha256
   `4baf8e087515d2e4`. Identical, so the Worker is running exactly this source.

2. **The change itself, read out of the LIVE bundle's compiled template:**

   ```
   </header> <!> <section class="ask" aria-label="Ask the hive"><!></section> <!> <!> ...
   ```

   The composer is the first thing after the header. (Raw string offsets are
   misleading here — `needs-you` and `recent` also appear in the component's JS
   logic, not only its template, so ordering must be read from the template.)

3. **Deleted panels confirmed absent from the shipped bundle:** `Memory` occurs
   0 times, `History` 0 times. The single remaining `System` is the
   `aria-label="System status"` on the status-dot cluster, not the deleted row.

4. **Mac agent surface checked the same way:** `build-agent/.../2.Dax6pJg2.js`
   on disk (sha `f70eab052424cee6`) is byte-identical to what
   `http://127.0.0.1:8000/dashboard/...` serves, and carries the same
   composer-at-top template. Both surfaces agree.

5. `wrangler deployments list` confirms `4a9f2a5a` created 2026-08-13T15:51:21Z
   as the current version at 100%.

## Gotcha for the next agent

`node --test tests/*.test.mjs` reported 30 pass / 21 fail on the first run with
module-resolution errors out of `tests/support/workerd-loader.mjs`, then 51/51
on an immediate re-run with no code change. The loader resolves modules out of
`.svelte-kit/output`, so a **concurrent build from another agent** wipes that
directory mid-test. The failures were the race, not the code. If two agents
share this package, serialize builds before believing a red test run.

## Standing rule added to AGENTS.md

> Nothing in this repo auto-deploys — there is no CI, so "commit and push" ships
> NOTHING. A change to the dashboard is not delivered until BOTH surfaces are
> rebuilt (`npm run deploy:cloudflare` and `npm run build:agent`); the relay
> likewise needs its own `wrangler deploy`. Verify a deploy by byte-comparing a
> live asset against the local build, never by opening the page.
