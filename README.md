# andromedacli-web

Landing page and install-script front for **[Andromeda](https://github.com/datamaia/andromeda)**,
served at **[andromedacli.com](https://andromedacli.com)**.

This is a static site (no build step) plus a `vercel.json` that proxies the canonical install
scripts from the CLI repo, so the scripts have a single source of truth and this repo never
duplicates them.

## What's here

| Path | Purpose |
| --- | --- |
| `index.html` | The landing page (self-contained; inline CSS/JS, theme-aware, responsive) |
| `vercel.json` | Rewrites `/install`, `/install.sh`, `/install.ps1` → the CLI repo's raw scripts, plus headers |
| `robots.txt` | Allow indexing |

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

The 🐱 in the nav/hero is a placeholder for the real Andromeda cat mascot — drop the mascot
asset in and swap the emoji when available. Brand palette: violet `#7C5CFF`, taupe `#8C7B6E`,
off-white `#F5F2ED`.
