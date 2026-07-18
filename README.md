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
| `docs.html` | The **documentation** site (served at `/docs`) — sidebar + on-page TOC, same `dc-runtime` |
| `guide.html` | The **printable getting-started guide** (served at `/guide`) — letter-format, via `doc-page.js` |
| `doc-page.js` | The paged-document component that `guide.html` imports (letter layout, print/PDF-friendly) |
| `support.js` | The `dc-runtime` that renders every `<x-dc>` page (loads React 18 from unpkg at runtime) |
| `assets/andromeda-cat.png` | The Andromeda cat mascot |
| `vercel.json` | Rewrites `/install*` → the CLI repo's raw scripts and `/docs`, `/guide`, `/guia` → the doc pages, plus headers |
| `robots.txt` | Allow indexing |

**Rendering note:** the landing is client-side rendered by `support.js`, which pulls React (and
Babel standalone) from `unpkg.com` at runtime — so first paint depends on that CDN and the page
is not server-rendered. To edit the design, re-export from the design tool and replace
`index.html` + `support.js`; the production `<head>` (title, description, OG tags, favicon) is
added on top of the export and should be preserved on re-export.

## Documentation

The docs are served from the same domain by the same `dc-runtime`:

- **`/docs`** (`docs.html`) — the full documentation: install, providers & auth, the engineering
  harness, working with agents, configuration, and the command reference. Dark theme (matches the
  landing), sidebar + on-page table of contents with scroll-spy.
- **`/guide`** (`guide.html`, alias `/guia`) — a printable, letter-format getting-started guide
  (light theme) built with `doc-page.js`; good for reading top-to-bottom or exporting to PDF.

Both are static `dc-runtime` exports like `index.html`: to edit, re-export from the design tool and
replace the file, preserving the production `<head>` (title/description/OG/favicon) and the absolute
`/support.js` (and `/doc-page.js`) script paths. The landing's nav, hero CTA, and footer link to
`/docs`.

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

The site is hosted on Vercel with `andromedacli.com` attached and SSL auto-provisioned. It is
**not** Git-connected, so pushing to `main` here does **not** auto-deploy — production is published
through the Vercel **REST API**. A read-only token 403s on file upload, so deploy needs a
**Full Account / write-scoped** token, kept in a local, untracked `.env` (never printed or
committed). To ship an update, re-run the REST deploy: upload the files to `/v2/files` by sha1,
then `POST /v13/deployments` with `target: production`.

Alternatively, connect this repo under **Project → Settings → Git** in the Vercel dashboard for
push-to-deploy (needs the Vercel GitHub app OAuth on the account).

Local preview: `npx vercel dev` (or just open `index.html` — the `/install*`, `/docs`, and
`/guide` rewrites only run on Vercel; you can still open `docs.html` / `guide.html` directly).

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
