# andromedacli-web

Landing page and install-script front for **[Andromeda](https://github.com/datamaia/andromeda)**,
served at **[andromedacli.com](https://andromedacli.com)**.

This is a static site (no build step) plus a `vercel.json` that proxies the canonical install
scripts from the CLI repo, so the scripts have a single source of truth and this repo never
duplicates them.

## What's here

| Path | Purpose |
| --- | --- |
| `index.html` | The landing page — a design-tool export driven by the `dc-runtime` in `support.js` |
| `support.js` | The `dc-runtime` that renders the `<x-dc>` template (loads React 18 from unpkg at runtime) |
| `assets/andromeda-cat.png` | The Andromeda cat mascot |
| `vercel.json` | Rewrites `/install`, `/install.sh`, `/install.ps1` → the CLI repo's raw scripts, plus headers |
| `robots.txt` | Allow indexing |

**Rendering note:** the landing is client-side rendered by `support.js`, which pulls React (and
Babel standalone) from `unpkg.com` at runtime — so first paint depends on that CDN and the page
is not server-rendered. To edit the design, re-export from the design tool and replace
`index.html` + `support.js`; the production `<head>` (title, description, OG tags, favicon) is
added on top of the export and should be preserved on re-export.

## The install one-liners

`vercel.json` proxies (not redirects) the scripts, so these serve the exact bytes of the
canonical scripts in [`datamaia/andromeda`](https://github.com/datamaia/andromeda/tree/main/scripts):

```sh
# macOS / Linux
curl -fsSL https://andromedacli.com/install | bash

# Windows (PowerShell)
irm https://andromedacli.com/install.ps1 | iex
```

Source of truth:
- `/install` and `/install.sh` → `scripts/install.sh` on `main`
- `/install.ps1` → `scripts/install.ps1` on `main`

Because they proxy `main`, the served installer always tracks the latest committed script; the
script itself resolves the latest published release.

## Deploy (Vercel)

1. Create a Vercel project from this repo (Framework preset: **Other** — it's static).
2. Add the domain `andromedacli.com` in **Project → Settings → Domains** and point the
   registrar's nameservers/records as Vercel instructs.
3. Every push to `main` redeploys. No environment variables or secrets are required.

Local preview: `npx vercel dev` (or just open `index.html` — the `/install*` rewrites only run
on Vercel).

## Optional: vanity `go install` path

To enable `go install andromedacli.com/cli@latest`, Go needs a `go-import` meta tag **and** the
CLI module's path must match. That means renaming the module in `datamaia/andromeda` from
`github.com/datamaia/andromeda` to `andromedacli.com/...`, which rewrites every internal import —
a deliberate, one-way commitment. Until that's done, do **not** add a `go-import` route here, or
`go install` against the vanity path will fail. Keep advertising
`go install github.com/datamaia/andromeda/cmd/andromeda@latest`.

## Brand assets

`assets/andromeda-cat.png` is the Andromeda cat mascot used in the hero. Brand palette: violet
`#7C5CFF`, taupe `#8C7B6E`, off-white `#F5F2ED`, on a near-black `#0e1013` cosmic background.
